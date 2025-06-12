import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Google API scopes (gộp cả Tasks và Calendar) ---
SCOPES = [
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_credentials():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except Exception:
        pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def get_tasks_service(creds):
    return build('tasks', 'v1', credentials=creds)

def get_calendar_service(creds):
    return build('calendar', 'v3', credentials=creds)

def list_tasks(service, tasklist_id='@default'):
    result = service.tasks().list(tasklist=tasklist_id).execute()
    return result.get('items', [])

def is_task_added(service, title, tasklist_id='@default'):
    tasks = list_tasks(service, tasklist_id)
    for task in tasks:
        if task.get('title') == title:
            return True
    return False

def add_task(service, title, due_date, note=None, tasklist_id='@default'):
    task_body = {
        'title': title,
        'due': due_date + 'T23:59:59.000Z',
    }
    if note:
        task_body['notes'] = note
    try:
        service.tasks().insert(tasklist=tasklist_id, body=task_body).execute()
        print(f"[OK] Đã thêm task: {title} | {due_date}")
    except Exception as e:
        print(f"[ERR] Lỗi khi thêm task {title}: {e}")

def is_event_added(service, title, date):
    start_datetime = f"{date}T00:00:00+07:00"
    end_datetime = f"{date}T23:59:59+07:00"

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_datetime,
        timeMax=end_datetime,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    for event in events:
        if event.get('summary', '') == title:
            return True
    return False

def add_event(service, title, date, url):
    event_body = {
        'summary': title,
        'description': f'Sự kiện lấy từ UTH: {url}',
        'start': {
            'date': date,
            'timeZone': 'Asia/Ho_Chi_Minh',
        },
        'end': {
            'date': date,
            'timeZone': 'Asia/Ho_Chi_Minh',
        }
    }
    try:
        result = service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"[OK] Đã thêm sự kiện: {title} | {date} | Link: {result.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"[ERR] Lỗi khi thêm sự kiện {title}: {e}")
        return False

def load_uth_login(filename="uth_login.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            mssv = data.get("mssv", "")
            password = data.get("password", "")
            if not mssv or not password:
                raise ValueError("File uth_login.json thiếu thông tin mssv hoặc password")
            return mssv, password
    except Exception as e:
        print(f"[ERR] Lỗi đọc file đăng nhập UTH: {e}")
        exit(1)

# --- Đọc thông tin đăng nhập từ file ---
mssv, password = load_uth_login()

# --- Khởi động Selenium ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # Chạy ẩn
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

# Danh sách các site và đường dẫn login
sites = [
    ("https://courses.ut.edu.vn", "/login/index.php"),
    ("https://thnn.ut.edu.vn", "/login/index.php"),
]

events = []

for base_url, login_path in sites:
    driver.get(base_url + login_path)
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(mssv)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    time.sleep(3)

    driver.get(base_url + "/calendar/view.php?view=month")
    time.sleep(5)

    days_with_events = driver.find_elements(By.CSS_SELECTOR, "td.hasevent")
    for day_cell in days_with_events:
        try:
            timestamp = int(day_cell.get_attribute("data-day-timestamp"))
            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            event_items = day_cell.find_elements(By.CSS_SELECTOR, "li[data-region='event-item']")
            for item in event_items:
                title = item.find_element(By.CLASS_NAME, "eventname").text.strip()
                url = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                events.append({"title": title, "date": date_str, "url": url})
        except Exception as e:
            print("[ERR] Lỗi:", e)

driver.quit()

print(f"[OK] Tổng số sự kiện lấy được: {len(events)}")

# --- Lấy credentials chung ---
creds = get_credentials()

# --- Tạo Google Tasks và Calendar service ---
tasks_service = get_tasks_service(creds)
calendar_service = get_calendar_service(creds)

# --- Xử lý thêm Task và Event ---
for event in events:
    # Thêm task nếu chưa có
    if not is_task_added(tasks_service, event['title']):
        add_task(tasks_service, event['title'], event['date'], note=f"Sự kiện từ UTH: {event['url']}")
    else:
        print(f"[WAR] Task đã tồn tại, bỏ qua: {event['title']} | {event['date']}")

    # Thêm event nếu chưa có
    if not is_event_added(calendar_service, event['title'], event['date']):
        add_event(calendar_service, event['title'], event['date'], event['url'])
    else:
        print(f"[WAR] Sự kiện đã tồn tại trên Calendar, bỏ qua: {event['title']} | {event['date']}")

print("\n[OK] Hoàn tất xử lý.")
input("Nhấn Enter để thoát...")

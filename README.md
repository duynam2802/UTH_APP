
# Tự Động Thêm Deadline Vào Google Calendar & Tasks từ UTH

Chương trình Python này sẽ:
- Đăng nhập vào các trang học trực tuyến của **Đại học Giao thông Vận tải TP.HCM (UTH)**.
- Lấy thông tin **sự kiện lịch học / deadline** trên calendar của từng môn.
- Tự động thêm vào **Google Calendar** và **Google Tasks** nếu chưa có.

---

## Tính Năng Chính

-  Đăng nhập vào nhiều trang học UTH bằng Selenium.
-  Lấy toàn bộ deadline hiển thị trong calendar của từng môn học.
-  Kiểm tra tránh trùng lặp trước khi thêm.
-  Thêm Task vào Google Tasks.
-  Thêm Event vào Google Calendar.
-  Lưu thông tin đăng nhập từ file `uth_login.json`.

---

##  Yêu Cầu Cài Đặt

- Python 3.10+  
- Trình duyệt **Google Chrome**  
- Các thư viện:

```bash
pip install selenium google-auth google-auth-oauthlib google-api-python-client
```

- Tải và đặt driver Chrome tương thích tại thư mục đã cấu hình.

---

##  Cấu Hình Tài Khoản UTH

Tạo file `uth_login.json` trong cùng thư mục với nội dung:

```json
{
  "mssv": "12345678",
  "password": "matkhaucuaban"
}
```

---

##  Kết Nối Google API

1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project, bật **Google Calendar API** và **Google Tasks API**
3. Tạo thông tin đăng nhập kiểu **OAuth client ID (Desktop)**.
4. Tải file `credentials.json` về và đặt trong thư mục chứa chương trình.

---

##  Chạy chương trình

```bash
python calendar_and_task_add_deadline.py
```

Lần đầu sẽ mở trình duyệt để xác thực Google. Sau đó token được lưu vào `token.json`.

---

##  Tự động chạy cùng Windows

1. Tạo file `run_script.bat`:

```bat
@echo off
cd /d D:\DuongDanCuaBan
python calendar_and_task_add_deadline.py
```

2. Nhấn `Win + R` → gõ `shell:startup`
3. Dán file `.bat` vào thư mục Startup.

---

##  Ghi chú

- Chạy script định kỳ để cập nhật deadline mới.
- Dùng `pause` trong file .bat để dễ kiểm tra lỗi nếu cần.

---

##  Tác giả
**duy**

---


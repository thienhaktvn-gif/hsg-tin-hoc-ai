# HSG Tin học AI — Nâng cấp chuyên đề, bài tập và liên kết (20-10-2026)

## Những gì đã sửa
- Sửa logic đăng nhập JS, bỏ việc gắn event listener popstate lặp trong mỗi lần đăng nhập.
- Các thẻ chuyên đề trong tài khoản giáo viên/học sinh có thể nhấp vào và mở danh sách bài tập đúng chủ đề.
- 7 chuyên đề có bài học tóm tắt và 28 bài thực hành (6 bài cũ + 22 bài mới), mỗi bài đều có ví dụ và bộ test ẩn.
- Không đổi giao diện gốc (CSS/HTML giữ nguyên). Chấm điểm thật qua Judge0, không có điểm mô phỏng.
- Khi chưa cấu hình JUDGE0_URL, nút chạy/chấm trong phòng lập trình bị khóa để tránh hiểu nhầm.

## Kiểm tra cục bộ
- `python TEST_ONLINE_LOCAL.py` — kiểm tra máy chủ, đăng nhập, phân quyền, đường dẫn.
- `python -m py_compile HSG_Tin_Hoc_AI/app.py`
- `node --check HSG_Tin_Hoc_AI/static/app.js`
- Kiểm thử dữ liệu mới: 7 chuyên đề, 28 bài, tất cả chuyên đề đều có bài.

## Cập nhật đúng repository đã liên kết Render
Trong Render screenshot, Blueprint trỏ tới `thienhaktvn-gif/hsg-tin-hoc-ai` nhánh main, khác với repo `hsg-tin-hoc-ai-pro`.
Cách tốt nhất: tại repo `hsg-tin-hoc-ai` giải nén ZIP và tải lên thư mục `HSG_Tin_Hoc_AI` đúng như ZIP này, không tạo thêm thư mục bọc ngoài như `HSG_Tin_Hoc_AI_SUA_LOI_RENDER_THIEU_THU_MUC`.
Trong `render.yaml` ở gốc, cấu hình `rootDir: HSG_Tin_Hoc_AI` (4 dấu cách ở đầu dòng). Sau khi commit, trở lại Blueprint chọn Manual sync; kiểm tra Logs đến khi Live.

**LƯU Ý:** Không đổi `rootDir` trong `render.yaml` nếu bạn vẫn dùng đường dẫn thư mục lồng cũ, trừ khi bạn chuyển mã nguồn vào đúng vị trí. Chỉ nên giữ MỘT đường dẫn mã nguồn hợp lệ.

## Chấm tự động Judge0
Nút chấm có backend và bộ test. Nhưng cần dịch vụ Judge0 thực tế do chủ hệ thống cung cấp: `JUDGE0_URL`, `JUDGE0_API_KEY`/`JUDGE0_AUTH_HEADER` nếu endpoint yêu cầu. Không được đưa API key vào mã nguồn hoặc GitHub. `GET /api/judge/status` dùng để kiểm tra trạng thái thật. Nếu chưa có endpoint, không thể chạy hoặc chấm code tự động, đây không phải lỗi giao diện.

## An toàn và giới hạn
Đây vẫn là bản preview được bảo vệ bằng `HSG_PREVIEW_PASSWORD` và `HSG_SECRET`, không nên dùng thông tin học sinh thật. Tài khoản demo chưa phù hợp dùng công khai. Cơ sở dữ liệu SQLite trên Render Free không bền vững giữa các lần khởi động/tái triển khai. Muốn sử dụng chính thức, cần thay lớp tài khoản demo, dùng DB bền vững và kết nối Judge0 thật.

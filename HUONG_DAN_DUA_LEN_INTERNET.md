# HSG Tin học AI — giữ nguyên giao diện cũ, đưa lên Internet (bản xem thử)

## Thiết kế
Giao diện được giữ từ bản `HSG_Tin_Hoc_AI_Routing_Dashboard_Giong_Web_That.zip` (HTML/CSS/JavaScript). Không chuyển sang Lovable, không cần Lovable credits.

## Đưa lên Render Free
1. Giải nén file ZIP này. Tạo kho GitHub **Private** và tải lên `render.yaml`, thư mục `HSG_Tin_Hoc_AI` cùng tài liệu. **Không tải** `hsg.sqlite3`, `.env` hoặc mật khẩu lên GitHub.
2. Trên Render: New > Blueprint, kết nối GitHub, chọn repo vừa tạo. Cấu hình Free nếu Render đang hỗ trợ ở tài khoản của bạn.
3. Render yêu cầu biến môi trường `HSG_PREVIEW_PASSWORD`. Nhập một mật khẩu dài ít nhất 16 ký tự do bạn tự chọn. `HSG_SECRET` được Render tạo ngẫu nhiên. Không đăng mật khẩu này công khai.
4. Chờ build/deploy thành công, mở địa chỉ do Render **thực sự** cấp. Trình duyệt hỏi mật khẩu xem trước: tên người dùng là `preview`, mật khẩu là `HSG_PREVIEW_PASSWORD` đã tự đặt.
5. Sau khi qua lớp bảo vệ, tài khoản demo nội bộ `giaovien` / `Demo@12345` hoặc `hocsinh` / `Demo@12345` chỉ để trình diễn **không dùng dữ liệu thật**.
6. Thử nhấn trang chủ, Đăng nhập, Đăng ký, Cổng học sinh, Dashboard, Thư viện bài, Tham khảo; thử mở trực tiếp URL rồi F5.

## Giới hạn không được bỏ qua
- Free web instance có thể ngủ và khởi động chậm. SQLite trên bộ lưu trữ không bền của Render có thể mất dữ liệu khi redeploy/restart. **Không dùng để tổ chức thi hay quản lý học sinh thật**.
- Đăng ký trong bản public preview bị tắt vì cơ chế tự nhận vai trò giáo viên của bản local không an toàn để mở Internet. Muốn dùng thật phải thiết kế lại đăng ký với xác thực email, RLS, quyền giáo viên được duyệt, dữ liệu PostgreSQL bền vững.
- Judge0 chưa được cấp máy chấm. Chỉ hoạt động nếu có `JUDGE0_URL` và (nếu cần) API key riêng; cần đánh giá cách ly và tính phí trước khi công khai nộp code. Không chạy code học sinh trên máy chủ web.
- Trợ lý AI chưa kết nối API. Các khung demo không phải AI hoạt động thật.
- Không chia sẻ link public không mật khẩu hoặc đưa dữ liệu riêng tư lên bản thử nghiệm.

## File nguồn
- `HSG_Tin_Hoc_AI/static/style.css` — giao diện cũ
- `HSG_Tin_Hoc_AI/static/app.js` — điều hướng đúng URL
- `HSG_Tin_Hoc_AI/app.py` — server và API demo
- `render.yaml` — cấu hình deploy Render

## Lưu ý bảo mật
Mật khẩu và API key nhập trong phần Environment của Render, không nhập vào HTML/JavaScript hoặc commit GitHub.

## Bản đóng gói đã kiểm tra bổ sung
- Chạy trước bằng `python TEST_ONLINE_LOCAL.py` ở thư mục gốc gói mã nguồn (có Python 3.10+).
- Nếu thấy dòng `PASS` thì xác nhận các luồng HTTP cốt lõi đạt trên máy thử. Nó **không** thay thế việc kiểm tra thủ công trên Render.
- File `.gitignore` ngăn đẩy database SQLite, log, cache và `.env` lên GitHub. Chỉ nhập secrets trong dashboard Render.
- Khi thử ở Render, đường dẫn `/auth/login`, `/auth/register`, `/dashboard` cần mở trực tiếp và reload được. `/auth/register` chỉ hiện giao diện: API đăng ký bị vô hiệu hóa trong bản public preview.
- Không nhập thông tin học sinh thật; không dùng bản preview để tổ chức kỳ thi chính thức. Judge0 chưa được kết nối.
- Nếu Render không cho dùng gói Free hoặc yêu cầu phương thức thanh toán, dừng và kiểm tra gói hiện hành trước khi xác nhận khoản phí. Không cần mua dịch vụ để tiếp tục phát triển giao diện local.

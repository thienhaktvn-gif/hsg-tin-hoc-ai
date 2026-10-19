# HSG Tin học AI — Checklist triển khai an toàn

Đây là **bản xem thử** online được bảo vệ, giữ nguyên HTML/CSS/JS, không phải hệ thống sản xuất cho học sinh.

1. Giải nén gói. Trong GitHub repo https://github.com/thienhaktvn-gif/hsg-tin-hoc-ai-pro, chọn Add file > Upload files và **tải NỘI DUNG của thư mục gói**, giữ `render.yaml` tại gốc, thư mục `HSG_Tin_Hoc_AI/` bên trong. Không tải file ZIP duy nhất.
2. Vào https://dashboard.render.com/select-repo?type=blueprint hoặc Dashboard > New > Blueprint. Kết nối GitHub, chọn repo đã tải mã nguồn, chọn Blueprint miễn phí `render.yaml`. Không đồng ý gói trả phí.
3. Khi Render yêu cầu biến `HSG_PREVIEW_PASSWORD`, tạo mật khẩu NGẪU NHIÊN riêng ít nhất 16 ký tự; giữ kín. `HSG_SECRET` được tự động tạo qua `generateValue`. Không đưa 2 biến này vào git.
4. Render báo Live, mở URL thực do Render cấp; nếu HTTP 401 chưa điền Basic Auth password xem thử là hành vi dự kiến. Đăng nhập bằng **tên người dùng `preview` và mật khẩu xem thử trong biến môi trường** (Basic Auth).
5. Kiểm tra trang chủ, /auth/login, /auth/register, /student/portal, /dashboard và vào DevTools > Console để xem lỗi tải assets.
6. Nếu Render lỗi: xem Events / Logs và so sánh với `python TEST_ONLINE_LOCAL.py` trên máy cục bộ.

**Giới hạn:** Bản demo tạo tài khoản giáo viên/học sinh mẫu với mật khẩu cố định. Do đó **bắt buộc bảo vệ bằng HSG_PREVIEW_PASSWORD** và không sử dụng để quản lý dữ liệu học sinh thật. SQLite trên Render Free có thể mất dữ liệu khi triển khai lại, không có database bền vững. Judge0 và AI chưa được cấp dịch vụ, không tự động chấm thật. Không công bố rộng rãi.

Bảo mật tài khoản: nếu từng chia sẻ mật khẩu tài khoản trên chat, đổi mật khẩu đó trên trang chính thức và bật 2FA. Không gửi mật khẩu cho trợ lý.

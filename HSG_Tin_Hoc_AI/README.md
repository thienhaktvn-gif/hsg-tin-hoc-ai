# HSG Tin học AI — bản nâng cấp phục vụ trình diễn / thử nghiệm

## Cách chạy

Yêu cầu: Python 3.10 hoặc mới hơn. **Không cần pip install**.

- Windows: Giải nén thư mục, nhấp đúp `CHAY_UNG_DUNG.bat` (cần Python trong PATH).
- macOS / Linux: Chạy `python3 app.py` ở thư mục ứng dụng.
- Mở trình duyệt: **http://127.0.0.1:8765**.
- Dừng ứng dụng: `Ctrl+C` trên cửa sổ lệnh.

Tài khoản mẫu (chỉ để chạy trên máy của bạn):
- Giáo viên: `giaovien` / `Demo@12345`
- Học sinh: `hocsinh` / `Demo@12345`

Dữ liệu lưu trong `hsg.sqlite3` (tạo tự động). **Sao lưu tệp này** để giữ nội dung đã nhập. Khi cần đặt lại dữ liệu mẫu, tắt app và đổi tên/xóa tệp đó.

## Chức năng đã hoạt động

- Trang chủ responsive theo cảm hứng giao diện TrợLý GV, có thương hiệu riêng.
- Đăng nhập, phân quyền giáo viên / học sinh, phiên đăng nhập ký số.
- Các nhóm chuyên đề theo định hướng phụ lục HSG THCS.
- Danh sách bài, tạo bài mới dành cho giáo viên; bài mẫu có test ẩn ở SQLite.
- Soạn mã C++, Python, Pascal và lưu nháp trong trình duyệt.
- Thiết lập đề luyện tập gồm tối đa 4 bài; lịch sử nộp sau khi chấm.
- **Mới:** Tạo lớp, phát mã tham gia lớp, học sinh gia nhập lớp.
- **Mới:** Giáo viên giao bài theo lớp, học sinh xem các bài được giao.
- **Mới:** Giáo viên thêm test ẩn cho bài do mình tạo và chấm theo trọng số test.
- **Mới:** Thống kê số lượt nộp và điểm cao nhất từ dữ liệu chấm thật.
- **Mới:** Thêm các bài mẫu hình học, xâu, tìm kiếm và Fibonacci.
- Có tích hợp Judge0 **nếu cấu hình máy chấm bên ngoài**.

## Kích hoạt chấm thật với Judge0 (tùy chọn)

Cần có Judge0 chạy và hỗ trợ `C++17`, `Python 3`, `Free Pascal`.

Linux / macOS:

```bash
export JUDGE0_URL='https://YOUR-PRIVATE-JUDGE0-ENDPOINT'
export JUDGE0_API_KEY='YOUR-KEY-IF-NEEDED'
python3 app.py
```

Windows (Command Prompt):

```cmd
set JUDGE0_URL=https://YOUR-PRIVATE-JUDGE0-ENDPOINT
set JUDGE0_API_KEY=YOUR-KEY-IF-NEEDED
python app.py
```

Mã nguồn chỉ được chuyển đến Judge0, **không chạy bằng Python subprocess trên máy local**. Khi chưa cấu hình, app hiển thị lỗi minh bạch thay vì điểm giả.

**Quan trọng:** Bản này là nguyên mẫu dùng trên máy tính cá nhân, chỉ lắng nghe 127.0.0.1. Không mở port ra mạng hoặc đưa lên hosting công khai. Việc chạy mã nguồn người dùng đòi hỏi hệ thống cách ly chuyên dụng, auth/rate limit, hàng đợi, mã hóa HTTPS, phân quyền mạnh, nhật ký và kiểm thử bảo mật; bản demo chưa có đủ các bảo vệ đó. Không dùng tài khoản demo cho dữ liệu học sinh thật. Bộ chấm hiện dùng so sánh đầu ra sau `strip()` và chấm theo tổng điểm test; cần hỗ trợ các quy tắc chấm khác trước khi sử dụng chính thức.

## Còn cần hoàn thiện cho sản phẩm thật

Supabase/PostgreSQL đa người dùng; quản lý test ẩn bằng UI; lớp học và giao bài; thi có thời gian và quy tắc lấy bài nộp; AI trợ giảng qua backend; nhập/xuất đề và Excel; đăng ký/phê duyệt giáo viên, quên mật khẩu; HTTPS, log, sao lưu tự động; CI kiểm thử và sandbox của máy chấm.

## Phạm vi bản nâng cấp

Bản này là **web app cục bộ có chức năng thực**, không phải website thương mại đã hoàn thiện hoặc công cụ tổ chức thi HSG chính thức. Chưa có AI API, chưa có máy chấm được cung cấp kèm, chưa có phòng thi khóa thời gian, giám sát gian lận, biểu đồ nâng cao hay máy chủ triển khai Internet. Mục tiêu là trình diễn sản phẩm và tiếp tục phát triển một cách an toàn.

### Cách bảo vệ dữ liệu

- Ứng dụng chỉ lắng nghe `127.0.0.1`; không đưa lên Internet.
- **Không dùng dữ liệu cá nhân thật của học sinh trên tài khoản demo**.
- Thay đổi mật khẩu demo và bổ sung đăng ký/quản trị người dùng trước khi sử dụng thực tế.
- Cần trang bị rate limiting, CSRF protection toàn diện, HTTPS, quản lý phiên và sandbox riêng trước khi mở rộng nhiều người dùng.


## BẢN SỬA LỖI 19/10/2026 – ĐĂNG NHẬP VÀ MENU

Đã sửa xung đột tên hàm `login()` (trang đăng nhập/biểu mẫu đăng nhập) và chính sách CSP chặn sự kiện nhấn nút của giao diện offline. Đã sửa thông báo tạo bài tập, tạo đề. Tệp ZIP phát hành không đính kèm cơ sở dữ liệu đã qua thao tác thử; cơ sở dữ liệu được khởi tạo khi chạy đầu tiên.

### Đã kiểm thử
- `node --check static/app.js` và `python -m py_compile app.py`: đạt.
- Kiểm thử API HTTP tự động: đăng nhập, đăng xuất, tài khoản giáo viên/học sinh, chuyên đề, bài tập, lớp học, tham gia lớp, giao bài, test ẩn, thi thử, thống kê, quyền hạn: đạt.
- Không kiểm thử trực tiếp thao tác giao diện bằng trình duyệt trong môi trường đóng gói vì môi trường kiểm thử chặn truy cập trang cục bộ; cần xác nhận trên Windows của người dùng.

### Chưa cung cấp thực sự
- Chấm code tự động C++/Python/Pascal phải cấu hình dịch vụ Judge0 riêng. Nút chấm sẽ báo chưa cấu hình thay vì cho điểm giả.
- Chưa có trợ lý AI được kết nối.
- Thi thử hiện là danh sách đề luyện tập, chưa có phòng thi đếm ngược/khóa giờ.
- Không triển khai bản offline này trực tiếp lên Internet; có tài khoản demo và chính sách CSP chỉ phục vụ bản local.

Bản quyền thuộc HSG Tin học AI 2026. Xây dựng bởi: Nguyễn Việt Hà & Võ Thị Vân Huyền.


## Tính năng trang chủ (bản cải tiến điều hướng)
Cả sáu thẻ Chuyên đề HSG, Phòng viết code, Chấm code tự động, Thi thử HSG, Bảng kết quả, Trợ lý AI đều là nút có thể nhấp và mở màn hình phù hợp. Khách xem được nội dung giới thiệu trước khi đăng nhập. Trợ lý ôn tập gồm gợi ý kiến thức định sẵn và được ghi nhãn rõ là không phải AI trực tuyến. Chấm code thật vẫn yêu cầu Judge0.


## Tài liệu tham khảo và kết nối Judge0 (bản nâng cấp)
- Mở mục **Tài liệu tham khảo** ở trang chủ hoặc menu. Có liên kết Python, cppreference, Free Pascal, VNOI, Codeforces, CSES, W3Schools, Judge0. Một số trang cấm iframe: dùng **Mở web gốc** để truy cập.
- Để chấm code thật, bạn **phải tự vận hành hoặc đăng ký một dịch vụ Judge0 có quyền sử dụng**. Mở CMD tại thư mục dự án rồi chạy:

  `set JUDGE0_URL=https://TEN-MAY-CHAM-CUA-BAN`

  `set JUDGE0_API_KEY=KHOA-CUA-BAN` (chỉ khi nhà cung cấp yêu cầu)

  `CHAY_UNG_DUNG.bat`

- Có thể thay `JUDGE0_AUTH_HEADER` khi dịch vụ cung cấp dùng tên header khác; một số gateway đòi hỏi `JUDGE0_HOST`. **Không** nhập khóa bí mật vào giao diện web, không đưa khóa vào file nén chia sẻ.
- Tại mục **Kiểm tra Judge0**, bấm **Kiểm tra kết nối Judge0**: thấy danh sách ngôn ngữ từ máy chấm mới có thể thử nộp. Hãy chạy chương trình đơn giản bằng C++ / Python / Pascal để xác minh cả worker.
- Hệ thống chạy bài theo token và kiểm tra trạng thái đến khi xong. Có kiểm tra kết quả từng test, không dùng AI để đoán điểm. Không công bố test ẩn cho học sinh.
- **Hạn chế:** Đây vẫn là hệ thống offline demo; việc gọi máy chấm trong HTTP request phù hợp nhóm nhỏ, chưa có hàng đợi bền vững; không dùng cho kỳ thi chính thức hoặc Internet công khai trước khi nâng cấp hạ tầng, bảo mật, tải và phân quyền.

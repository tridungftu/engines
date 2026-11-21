# TS-PL — kiểm màn và ảnh DEMO

Đã kiểm bằng Core giả (CoreGia); các callback màn bước thuộc cửa D2 dự kiến,
chưa kiểm tích hợp Core thật. TS-PL không có máy/dịch vụ hoặc bí mật để nhập.
Nút kiểm kiểm cấu trúc tại máy; không gọi dịch vụ. KttCore giả từ chối mọi lời
gọi cấu hình/ngăn/thao tác/két bí mật không thuộc phạm vi tham số bước.

```powershell
node --test e_phan_luong/tests/ui/tham_so.test.mjs
.venv/Scripts/python.exe -X utf8 -B -m pytest e_phan_luong/tests/test_ts_pl_ui.py -q
node e_phan_luong/tests/ui/dung_anh.mjs .venv/ui-ts-pl-DEMO.html
node e_phan_luong/tests/ui/chup_anh.mjs
```

Trang HTML tự chứa mã màn, CSS và Core giả, CSP chặn mạng. Mở tệp cục bộ
hoặc dùng Chromium headless với profile tạm trong `.venv/` để chụp.
Không cần máy chủ, thư viện Node hoặc cài dependency UI.
`chup_anh.mjs` dùng Chrome/Edge đã cài trên Windows hoặc nhận đường dẫn Chromium
ở đối số thứ nhất; không đổi ExecutionPolicy. `chup_anh.ps1` là cách tương đương
cho máy cho phép chạy script PowerShell.

Tham số trang chụp: `?the=nguong_json,chinh_sach_json` để chỉ hiện các thẻ
được chọn (mã thẻ theo `du_lieu_tham_so.js`); `che_do=loi` để đánh dấu
SAD không hợp lệ, `che_do=cas` để tạo tranh chấp lưu, `che_do=tam_khoa` để
hiện trạng thái Core chưa có bộ lưu. Các chế độ chỉ dùng trong công cụ test.

Ảnh chụp tại `anh/` dùng đúng thành phần, dữ liệu DEMO và KttCore giả:

- [Danh mục loại](anh/ts-pl-danh-muc.png): bố cục thẻ theo ảnh Máy AI.
- [Bộ phân loại](anh/ts-pl-phan-loai.png): thứ tự quy tắc, nhóm VÀ/HOẶC, loại trừ.
- [Ngưỡng và chính sách](anh/ts-pl-nguong-chinh-sach.png): tiền hiển thị theo VND, chính sách cơ bản.
- [Khuôn cột](anh/ts-pl-khuon-cot.png): khuôn cột và danh sách tiêu đề.
- [Màn hẹp có lỗi nhập](anh/ts-pl-di-dong-loi.png): một cột ở 500 px, lỗi cạnh ô. Chromium
  cục bộ giới hạn viewport cửa sổ tối thiểu 500 px; công cụ kiểm viewport
  thực không rộng hơn ảnh và kiểm tràn ngang để không nhận ảnh bị cắt cạnh.
- [Tranh chấp CAS](anh/ts-pl-cas.png): giữ nháp, khóa lưu khi người khác sửa.

Không dùng `imagegen`; đây là ảnh render thật của biểu mẫu. Không có ô API key,
nên đường "bí mật chỉ hiện 4 ký tự cuối" không áp dụng cho lát này; bộ kiểm
xác nhận không đọc két và không hiện giá trị bí mật ngoài năm ô được giao.

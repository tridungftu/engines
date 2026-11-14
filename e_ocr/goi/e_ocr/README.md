# Engine nhận dạng văn bản — OCR-0

Gói độc lập theo SDK 2.0.0, phiên bản engine 1.0.0. Lát OCR-0 chỉ có khung:
`ocr.doc_tai_lieu@1`, `ocr.doc_van_ban@1`, `ocr.xuat_word@1` đều trả lỗi
`CHUA_LAM`. Chưa xử lý OCR, chưa nối ABBYY hoặc Tesseract. Các kiểm tra cổng
**đã kiểm bằng Core giả (CoreGia)**; chưa kiểm trên Core thật.

Mỗi năng lực nhận PDF/PNG/JPEG tối đa 20 MiB, thời hạn 900 giây, có lựa chọn
nguồn `tu_dong` / `chi_abbyy` / `chi_tesseract`. Trần 60 trang được triển khai
ở OCR-1, trước bước giữ hạn mức. Loại `van_ban_tai_lieu` dùng schema sao chép
nguyên tệp từ `_chung/contract/van_ban_tai_lieu.schema.json`.

## Cài và kiểm

Python >= 3.11. Runtime chỉ dùng thư viện chuẩn và SDK 2.0.0 đã ghim trong
`requirements.lock`; cài SDK từ wheel phát hành, không cần mạng. Nguồn và
băm các tệp xem `NGUON.md`.

Trong thư mục gốc repo, sau khi cài SDK vào `.venv`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
.venv\Scripts\python -m kho_tri_thuc_sdk.thu e_ocr/goi/e_ocr
.venv\Scripts\python -m pytest e_ocr/tests -q
.venv\Scripts\python e_ocr/tests/kiem_doc_lap.py
```

Trên Linux dùng `.venv/bin/python`, đặt `PYTHONDONTWRITEBYTECODE=1` trước khi
nạp gói. Không đóng gói bytecode, test, môi trường ảo hoặc dữ liệu máy.

`chay_thu_demo` hiện rỗng, vì bộ DEMO xử lý OCR thuộc OCR-5. Lệnh SDK trên
trả mã **1**, câu `Phiếu chưa có ví dụ chay_thu_demo.`; chưa đạt điều kiện
DEMO chung của AGENTS.md §5. Pytest kiểm riêng cả ba hàm tạm qua CoreGia,
yêu cầu kết thúc `LOI/CHUA_LAM` và không nộp kết quả. Không báo DEMO đã đạt.

## Cấu hình máy ngoài gói

`e_ocr.cau_hinh_may.doc_cau_hinh()` đọc tệp JSON do `KTT_ENGINE_CAU_HINH`
chỉ định; mặc định là
`%PROGRAMDATA%\KhoTriThuc\engines\e_ocr\cau_hinh.json`. Trên Linux, khi không
có `PROGRAMDATA`, gốc thay thế là `/var/lib`. Cấu hình nằm trong gói bị từ chối.

Schema: `contract/cau_hinh_may.schema.json`. Mẫu **DEMO**:
`demo/cau_hinh.demo.json`; chép ra ngoài gói rồi cấu hình bằng biến môi trường.
Thiếu tệp trả `None`, engine vẫn khởi động; việc cần nguồn đọc phải gọi
`doc_cau_hinh(bat_buoc=True)` để nhận `CHUA_CAU_HINH` khi thiếu tệp.

Trường bỏ trống trong JSON được điền mặc định theo schema: ABBYY tắt,
thời hạn 900 giây, hạn mức 5.000 trang/30 ngày, ngôn ngữ `vie+eng`.
Loader kiểm đúng các kiểu và ràng buộc của schema này bằng thư viện chuẩn;
không phải bộ kiểm JSON Schema tổng quát. Tệp tối đa 64 KiB; từ chối khóa
lặp, kiểu sai, trường ngoài schema và số không hữu hạn. Không có trường bí mật.
Loader không mở Hot Folder và không kiểm tra/chạy tệp thực thi.

## Kho tạm

`e_ocr.kho_tam.KhoTam` có `doc(khoa, mac_dinh=None)` và `ghi(khoa, gia_tri)`.
Nguồn thư mục: `KTT_ENGINE_DU_LIEU`; mặc định
`%PROGRAMDATA%\KhoTriThuc\engines\e_ocr\du-lieu`. Trên Linux dùng cùng gốc
thay thế như cấu hình máy. Khởi tạo đối tượng chưa tạo thư mục.

Kho chỉ lưu mã, băm, số đếm, cờ và cấu trúc JSON gồm những giá trị đó. Chuỗi
mã tối đa 200 ký tự ASCII thuộc `[A-Za-z0-9_.:@+-]`, không có khoảng trắng
hay đường dẫn. Không truyền bytes, nội dung tài liệu hoặc nội dung mã hóa.
Các tên trường nội dung như `van_ban`, `noi_dung`, `tai_lieu`, `prompt` bị từ chối.
Mỗi giá trị tối đa 64 KiB, độ sâu tối đa 16; toàn kho tối đa 8 MiB, vượt trần
thì báo lỗi, không cắt. Không cần lưu tên hoặc đường dẫn tài liệu.

Đọc và ghi dùng một tệp khóa cố định `kho.khoa`: `msvcrt.locking` trên Windows,
`fcntl.flock` trên Linux. Ghi khóa cả đọc–sửa–ghi, ghi tệp tạm trong cùng thư
mục, `flush` + `fsync`, đóng tệp rồi `os.replace` sang `kho.json`; Linux còn
`fsync` thư mục. Lỗi thay tệp giữ nguyên bản cũ và dọn tệp tạm của lượt ghi.
Kho hỏng bị từ chối, không tự đặt lại thành kho rỗng. Hết hạn chờ khóa trả
`KHO_TAM_DANG_BAN`, cho phép thử lại.

Tính nguyên tử áp dụng cho **từng** lệnh `doc` hoặc `ghi`. Chuỗi `doc` rồi
`ghi` không phải giao dịch/CAS; không dùng nó để cộng hạn mức hoặc giữ lượt
có điều kiện giữa nhiều tiến trình. Các thao tác đó thuộc lát nghiệp vụ sau
và ngăn dữ liệu engine của Core. Kho là lớp bọc tạm theo phiếu giao, sẽ thay
bằng ngăn engine và lượt bền #10 khi Core cung cấp.

`demo/van_ban_tai_lieu.demo.json` chỉ minh họa hợp đồng bằng dữ liệu giả có
nhãn DEMO, gồm vị trí, ô trống và ô gộp; băm toàn số 0 là băm minh họa.

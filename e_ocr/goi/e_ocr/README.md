# Engine nhận dạng văn bản — OCR-3

Gói độc lập theo SDK 2.0.0, phiên bản engine 1.0.2. Hai năng lực
`ocr.doc_tai_lieu@1` và `ocr.doc_van_ban@1` dùng chung lõi đọc lớp chữ PDF
hoặc nhận PDF lớp chữ từ ABBYY Hot Folder cục bộ. `ocr.xuat_word@1` dùng
cùng lõi, dựng DOCX và gửi qua `viec.tai_tep_ra`. **Đã kiểm bằng Core giả (CoreGia)** và ABBYY giả;
chưa kiểm ABBYY hoặc Core thật.

Mỗi năng lực nhận PDF/PNG/JPEG tối đa 20 MiB, thời hạn 900 giây, có lựa chọn
nguồn `tu_dong` / `chi_abbyy` / `chi_tesseract`. Tệp được đọc bằng `viec.mo_tep`,
kiểm định dạng thực và đếm trang trước khi gửi nguồn ngoài. Vượt 60 trang
trả `QUA_SO_TRANG`, tệp hỏng/mật khẩu trả `TEP_HONG`, không gửi ABBYY.
Loại `van_ban_tai_lieu` dùng schema sao chép
nguyên tệp từ `_chung/contract/van_ban_tai_lieu.schema.json`.

## Cài và kiểm

Python >= 3.11. Dùng SDK 2.0.0, pdfplumber, Pillow và dependency đã ghim
trong `requirements.lock`; tất cả phiên bản thư viện ngoài SDK giữ như
lock cũ. Không dùng PyMuPDF, numpy hay vendor/mask_ocr trong OCR-1. Môi
trường kiểm dùng `.venv --system-site-packages` và thư viện có sẵn, SDK cài
offline từ wheel repo với `--no-index --no-deps`. Đây chưa là kiểm máy sạch
của OCR-6; lock hiện chưa có hash wheel đa nền tảng. Nguồn/băm xem `NGUON.md`.

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

`chay_thu_demo` có ba ví dụ đọc/xuất Word từ PDF DEMO lớp chữ 3 trang, chạy
được không cần cấu hình máy hoặc ABBYY. Bộ PDF được sinh bằng thư viện
chuẩn ở `tests/demo/tao_pdf.py`; có nhãn ảnh DEMO và chữ ẩn ToUnicode,
không cần font máy. Bộ kiểm Hot Folder dùng luồng nền nhận tệp DEMO rồi
ghi PDF cùng mã tương quan. Test dùng filesystem Python trên Windows/Linux;
lượt kiểm OCR-1 chạy thực tế trên Windows, chưa có Linux/WSL trong máy này.

## Đọc lớp chữ và giao thức Hot Folder

- PDF có lớp chữ đọc được ở **mọi trang** được đọc trực tiếp, nguồn
  `lop_chu_san`; không đọc cấu hình, gửi ABBYY hoặc OCR lại ảnh nền.
  Trang thiếu lớp chữ/hướng chữ chưa hỗ trợ khiến cả tệp gửi ABBYY, không
  trả kết quả thiếu trang. `chi_tesseract` vẫn cho phép đọc lớp chữ sẵn;
  khi cần OCR ảnh thì trả `CHUA_LAM` tới OCR-2, không gửi ABBYY.
- Cấu hình ABBYY bật, hai thư mục vào/ra phải là đường dẫn tuyệt đối tới
  hai thư mục đã có, tách biệt. Engine chỉ dùng đúng tên ngẫu nhiên
  `<ma_tuong_quan>.pdf|png|jpg`, không dùng tên người dùng hoặc quét thư mục.
- Tác vụ Hot Folder phải **rời/xóa tệp vào khi nhận** và xuất một PDF có
  lớp chữ đầy đủ tên `<ma_tuong_quan>.pdf` vào thư mục ra, giữ số trang.
  Đây là quy ước cần kiểm trên ABBYY thật ở OCR-7; quan sát tệp biến mất
  được dùng làm tín hiệu đã nhận, chưa có ACK riêng từ ABBYY.
- Tệp đệm được ghi/`fsync` trong thư mục tạm riêng của lượt, nằm **cạnh**
  thư mục vào, rồi đổi tên nguyên tử trên cùng filesystem. Tài khoản engine
  cần quyền tạo/dọn thư mục đệm tại đó. Thư mục đệm được dọn ở `finally`.
  Khi hủy, engine gọi `kiem_huy()` trong vòng chờ và rút đúng tệp còn chờ;
  không ép dừng ABBYY khi tệp đã được nhận.
- Chỉ đọc kết quả đúng mã sau khi kích thước/mtime ổn định qua hai lượt,
  có EOF và không thay đổi trong lúc đọc. Trần kết quả 20 MiB, 60 trang,
  500.000 ký tự; vượt thì từ chối, không cắt. Tệp kết quả đã đọc và tệp vào
  còn chờ được dọn sau lượt; không đụng kết quả thuộc mã khác.
- Hết hạn mà còn rút được tệp chờ: `ABBYY_QUA_THOI_HAN`. Tệp đã biến mất
  hoặc không rút được: `ChuaRo(ma_tuong_quan)`, không trả thành công hoặc
  chuyển nguồn. Chống trùng/lưu lượt bền và chốt kết quả trả muộn thuộc OCR-4.
- Kết quả có băm SHA-256 **tệp đầu vào**, phiên bản engine và cảnh báo.
  Toàn văn nối trang bằng `\f`; khối/dòng/từ có tọa độ point theo trang.
  Giữ nguyên tiền/ngày trong văn bản, không tự hiệu đính hay suy giá trị.
  Bảng có đường kẻ PDF giữ ô trống/ô gộp; bảng chỉ có trong ảnh nền chưa
  được tái tạo và có cảnh báo. Fallback và sổ hạn mức thuộc OCR-2.

## Xuất Word giữ bảng

`ocr.xuat_word@1` nhận tệp PDF/PNG/JPEG như hai action đọc. Kết quả là
phong bì `tep` chứa DOCX, MIME chuẩn Word và tên
`<tên gốc không phần mở rộng>-OCR.docx`; giữ dấu tiếng Việt và dấu chấm
trong tên gốc. Không ghi nội dung DOCX ra đĩa, không nhận dạng lại để xuất.

`xuat_word.dung_docx` dùng cấu trúc `van_ban_tai_lieu`: mỗi trang theo số
thứ tự thành một section, giữ khổ ngang/dọc; đoạn và bảng neo theo tọa độ
`pt` trên trang. Bảng dựng từ ô gốc, gộp ngang bằng `gridSpan`, gộp dọc
bằng `vMerge` và giữ cả ô trống. Có tọa độ từng ô thì giữ độ rộng cột;
nếu nguồn chỉ có khung bảng, chia đều khoảng chưa có mốc. Hai bảng liên
tiếp có đoạn ngăn để Word không nhập chúng thành một bảng.

Từ chối lưới thiếu/chồng ô, vị trí không hợp lệ hoặc đơn vị khác `pt`,
bảng trên 100 hàng/40 cột, hơn 60 trang hoặc hơn 500.000 ký tự; không
cắt ngầm hay tự thêm ô. Hủy/chưa rõ của nguồn đọc được giữ nguyên, không
tạo kết quả thành công giả. Word có thể dàn lại dòng/chiều cao theo font
trên máy; tọa độ bảng được ghi trong XML, chưa kiểm hiển thị trên Word thật.

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

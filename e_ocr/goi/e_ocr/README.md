# Engine nhận dạng văn bản — OCR-4

Gói độc lập theo SDK 2.0.0, phiên bản engine 1.0.4. Ba năng lực
`ocr.doc_tai_lieu@1`, `ocr.doc_van_ban@1` và `ocr.xuat_word@1` dùng chung
lõi đọc lớp chữ PDF hoặc ABBYY Hot Folder cục bộ, dự phòng Tesseract.
Xuất Word dựng DOCX và gửi qua `viec.tai_tep_ra`. **Đã kiểm bằng Core giả
(CoreGia)**, ABBYY/Tesseract mock và một ca Tesseract thật bằng DEMO trên
Windows; chưa kiểm Linux, ABBYY hoặc Core thật.

Mỗi năng lực nhận PDF/PNG/JPEG tối đa 20 MiB, thời hạn 900 giây, có lựa chọn
nguồn `tu_dong` / `chi_abbyy` / `chi_tesseract`. Tệp được đọc bằng `viec.mo_tep`,
kiểm định dạng thực và đếm trang trước khi gửi nguồn ngoài. Vượt 60 trang
trả `QUA_SO_TRANG`, tệp hỏng/mật khẩu trả `TEP_HONG`, không gửi ABBYY.
Loại `van_ban_tai_lieu` dùng schema sao chép
nguyên tệp từ `_chung/contract/van_ban_tai_lieu.schema.json`.

## Cài và kiểm

Python >= 3.11. Dùng SDK 2.0.0, pdfplumber, Pillow và dependency đã ghim
trong `requirements.lock`; tất cả phiên bản thư viện ngoài SDK giữ như
lock cũ. Bộ render là pypdfium2 đã ghim; vendor mask_ocr chỉ giữ phần cần
dùng, không thêm PyMuPDF, defusedxml, numpy hoặc model. Môi
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
  khi cần OCR ảnh thì bỏ ABBYY nếu không còn lượt ABBYY dở. PDF trộn chữ/ảnh qua Tesseract giữ nguyên
  trang có chữ, chỉ render/nhận dạng trang thiếu chữ.
- Cấu hình ABBYY bật, hai thư mục vào/ra phải là đường dẫn tuyệt đối tới
  hai thư mục đã có, tách biệt. Engine chỉ dùng tên tất định theo pháp nhân, băm và lần gửi
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
  500.000 ký tự; vượt thì từ chối, không cắt. Tệp kết quả sau thành công,
  hủy hoặc lỗi được dọn kể cả chưa đọc bytes; chỉ `ChuaRo` giữ kết quả
  để đối chiếu. Tệp vào còn chờ được rút nếu chưa nhận; không đụng kết quả
  thuộc mã khác.
- Hết hạn mà còn rút được tệp chờ: `ABBYY_QUA_THOI_HAN` trong chế độ chỉ
  ABBYY, hoặc chuyển Tesseract trong chế độ tự động. Tệp đã biến mất
  hoặc không rút được: `ChuaRo(ma_tuong_quan)`, không trả thành công hoặc
  chuyển nguồn. OCR-4 đã có chống trùng/lượt bền và chốt kết quả trả muộn.
- Kết quả có băm SHA-256 **tệp đầu vào**, phiên bản engine và cảnh báo.
  Toàn văn nối trang bằng `\f`; khối/dòng/từ có tọa độ point theo trang.
  Giữ nguyên tiền/ngày trong văn bản, không tự hiệu đính hay suy giá trị.
  Bảng có đường kẻ PDF giữ ô trống/ô gộp; bảng chỉ có trong ảnh nền chưa
  được tái tạo và có cảnh báo. Tesseract giữ bảng có đường kẻ vector và
  điền chữ vào đúng ô; chưa suy cấu trúc bảng chỉ có trong ảnh.

## Chọn nguồn và Tesseract

- `tu_dong`: ưu tiên ABBYY. Chuyển khi không đủ hạn mức, ABBYY tắt/không
  truy cập được, hoặc lỗi/quá hạn mà **chắc chắn chưa nhận** (chưa công bố
  hoặc đã rút được tệp vào), hoặc có biên nhận nguồn từ chối không tiêu
  trang. Đã nhận nhưng chưa có căn cứ hoàn, lỗi dọn kết quả hoặc chưa rõ
  việc nhận → không chuyển. `ChuaRo` không nộp kết quả giả.
- `chi_abbyy`: trả lỗi ABBYY/hạn mức rõ ràng, không dùng Tesseract.
  `chi_tesseract`: nếu không có lượt ABBYY dở thì bỏ backend/sổ, lý do
  chuyển là `null` vì Anh chọn nguồn; còn lượt dở thì đối chiếu lượt đó trước.
  Đọc lớp chữ sẵn vẫn áp dụng cho cả ba chế độ.
- `nguon_doc` là `abbyy`, `tesseract` hoặc `lop_chu_san`;
  `ly_do_chuyen_nguon` có câu tiếng Việt khi tự chuyển. Năng lực văn bản
  thuần vẫn chỉ trả chuỗi theo hợp đồng đã khóa.
- Tesseract tìm `tesseract.duong_dan`, rồi PATH/vị trí cài mặc định Windows;
  kiểm đủ `tesseract.ngon_ngu` (mặc định `vie+eng`). Thiếu executable hoặc
  model ngôn ngữ khi cần dùng → `NGUON_DU_PHONG_CHUA_CAI`. Khởi động engine,
  PDF có chữ và việc ABBYY đọc được không cần cài Tesseract.
- CLI chạy từng trang, có hủy/quá hạn và không in stderr chương trình
  ngoài. PNG/TSV ở thư mục tạm riêng, dọn khi xong/lỗi/hủy. PDF render
  150 dpi, tối đa 20 triệu pixel/trang; giữ tọa độ từ TSV, không tạo điểm
  tin cậy giả. Cần đối chiếu tiền/ngày và bảng với bản gốc.
- Vendor có parser DOCX giữ thứ tự, ô trống, `gridSpan` và `vMerge`; ảnh
  nhúng nhận bộ đọc qua `image_reader`. DOCX chưa thêm vào MIME của ba
  năng lực; phần này dành cho lõi nội bộ/OCR-3, không đổi hợp đồng API.
  OOXML dùng parser chuẩn, chặn DTD/entity trước parse; chỉ nhận XML UTF-8.

Máy đích cần Tesseract Windows x64 và ngôn ngữ `vie`, `eng`. Anh tự chạy
`e_ocr/cong-cu/KIEM-TESSERACT.cmd` từ repo (hoặc truyền đường dẫn executable
làm đối số thứ nhất). Công cụ ASCII chỉ kiểm/hiện hướng dẫn cài offline,
không tải hoặc cài phần mềm. Chi tiết ở `e_ocr/docs/VIEC.md`, mục **Cần cài**.

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
Thiếu tệp trả `None`, engine vẫn khởi động; `chi_abbyy` nhận `CHUA_CAU_HINH`.
Chế độ tự động khi chưa cấu hình ABBYY thử Tesseract theo PATH/vị trí mặc
định; `chi_tesseract` cũng có thể chạy không cần tệp cấu hình.

Trường bỏ trống trong JSON được điền mặc định theo schema: ABBYY tắt,
thời hạn 900 giây, hạn mức 5.000 trang/30 ngày, ngôn ngữ `vie+eng`.
Loader kiểm đúng các kiểu và ràng buộc của schema này bằng thư viện chuẩn;
không phải bộ kiểm JSON Schema tổng quát. Tệp tối đa 64 KiB; từ chối khóa
lặp, kiểu sai, trường ngoài schema và số không hữu hạn. Không có trường bí mật.
Loader không mở Hot Folder và không kiểm tra/chạy tệp thực thi.

## Kho tạm

`e_ocr.kho_tam.KhoTam` có `doc(khoa, mac_dinh=None)`, `ghi(khoa, gia_tri)`
và `cap_nhat(khoa, sua)` / `cap_nhat_nhieu(cac_khoa, sua)` để đọc–sửa–ghi một hoặc nhiều khóa trong cùng khóa tệp và một lần thay tệp.
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

Chuỗi `doc` rồi `ghi` không phải giao dịch/CAS. Sổ và nhật ký dùng
`cap_nhat_nhieu`: kiểm lượt dở, giữ trang và ghi dấu `dang_gui` **trong cùng
lần thay tệp trước khi công bố**. Khóa `han_muc_abbyy` giữ sổ theo ngày UTC
và giây trong ngày, cửa sổ **30 × 86.400 giây** trượt. Mỗi pháp nhân + băm
có khóa `luot_abbyy.<sha256>` riêng, nên không dồn nhật ký vào một giá trị
64 KiB. Kho chỉ lưu mã pháp nhân, băm, số trang, lần gửi, thời điểm và trạng thái.

`ma_tuong_quan` là UUID5 từ pháp nhân + băm nội dung + `lan_gui` bền; Core
đổi `viec_id`, `lan_thu` hoặc năng lực đọc/xuất Word vẫn tra cùng lượt dở.
Khóa tệp riêng theo mã lượt ngăn hai tiến trình cùng đọc/dọn kết quả; tiến
trình không lấy được khóa trả `ChuaRo` ngay. Hệ điều hành tự nhả khóa khi
chết; **dấu chống trùng vẫn nằm trong kho**. Không dùng lease/timeout để xóa dấu.

Lượt `dang_gui`/`chua_ro` luôn tìm PDF đúng mã trong thư mục ra trước; không
có kết quả hợp lệ thì tiếp tục `ChuaRo`, không gửi lần hai, không chạy
Tesseract và không tự hoàn trang. Áp dụng cả khi chọn nguồn mới là
`chi_tesseract`, ABBYY vừa tắt hoặc thiếu cấu hình. Có PDF thì đối chiếu,
chuyển chỗ giữ sang trang đã dùng đúng một lần, kiểm đủ lớp chữ/số trang,
chốt `xong` bền rồi mới dọn PDF. Nếu chốt bền lỗi, giữ PDF bằng `ChuaRo`.
`xong` không là cache nội dung: việc mới sau lượt đã chốt tạo lần gửi tiếp.

Trước nhận, rút được tệp hoặc gửi chưa thành công là căn cứ bỏ chỗ giữ.
Sau crash, chỉ không thấy tệp vào **không đủ** để kết luận đã công bố hay
đã nhận: giữ chỗ tới khi có kết quả hoặc bằng chứng từ chối. Vì vậy khi
khởi động lại, nhật ký được dùng để chốt/nhả `dang_giu`; không tự hết hạn.
PDF hỏng, thiếu chữ, sai số trang hoặc sự im lặng không là căn cứ hoàn trang.

Quy ước tạm cho bằng chứng từ chối rõ là `<ma_tuong_quan>.loi.json`, UTF-8,
tối đa 2 KiB, đúng ba trường dưới đây; nguồn chỉ tạo khi xác nhận **không
tiêu trang**. Không diễn giải tệp log/thông báo lỗi tùy ý thành bằng chứng:

```json
{"ma_tuong_quan":"<đúng mã lượt>","trang_thai":"tu_choi","da_tieu_trang":false}
```

Biên nhận hợp lệ cho phép nhả chỗ giữ hoặc hoàn đúng lượt đã tính, một lần,
sau khi rút/dọn được tệp vào còn chờ. Không rút được thì giữ biên nhận,
hạn mức và `ChuaRo` để tránh nguồn nhận tệp sau khi đã hoàn;
`chi_abbyy` báo `ABBYY_TU_CHOI`, chế độ tự động có thể dùng Tesseract. Biên
nhận khác mã, thiếu trường, báo đã tiêu trang hoặc xung đột với PDF vẫn
`ChuaRo`. Nếu ghi chốt lỗi thì giữ biên nhận để lần sau đối chiếu. Quy ước
này **chưa kiểm ABBYY thật**, cần xác nhận khi nối nguồn ở OCR-7; không có
biên nhận xác nhận thì tiếp tục giữ hạn mức.

Khi Core có thao tác #10 `luot-ben` giữ/chốt/đọc, thay phần nhật ký lượt
trong `kho_tam` bằng cửa đó. Ngăn engine có CAS sẽ thay sổ tạm. Không dùng
hàm `ocr_*_luot` hoặc cổng riêng cũ.

`demo/van_ban_tai_lieu.demo.json` chỉ minh họa hợp đồng bằng dữ liệu giả có
nhãn DEMO, gồm vị trí, ô trống và ô gộp; băm toàn số 0 là băm minh họa.

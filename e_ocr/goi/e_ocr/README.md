# Engine nhận dạng văn bản — OCR-8

Gói độc lập theo SDK 2.0.0, phiên bản engine 1.0.8. Ba năng lực
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
của OCR-6; lock đã có hash wheel đa nền tảng. Nguồn/băm xem `NGUON.md`.

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

`chay_thu_demo` có **6 ví dụ**: PDF quét 3 trang và PNG 1 trang cho cả ba
năng lực, đều `nguon=chi_tesseract`; không cần ABBYY. CLI SDK dùng Tesseract
thật với `vie+eng`. Máy thiếu bộ đọc chạy công cụ test từ repo:
`.venv\Scripts\python e_ocr/tests/chay_demo.py`; công cụ tự dùng Tesseract
giả và ghi rõ khi thiếu executable/ngôn ngữ. `--gia` ép dùng giả cho CI.
Nguồn giả chỉ ở ngoài gói, không tự thay nguồn trong engine. Công cụ cách
ly cấu hình và dữ liệu DEMO bằng ngăn RAM riêng.

Bộ sinh `tests/demo/tao_bo_demo.py` chuyển từ mã cũ, dùng Pillow đã ghim,
font Arial/DejaVu Sans sẵn trên máy, PDF thuần Python và bộ ghi Word của
gói; không thêm dependency. `tao_bo_demo(thu_muc, ca_loi=False)` sinh tệp
nhỏ để đưa vào `demo/`; mặc định còn sinh PDF 61 trang, >20 MiB và tệp
hỏng **chỉ trong thư mục tạm của test**, không đưa vào gói/git. Chỉ tạo
tệp mới, không ghi đè. Word đáp án có nhãn riêng, không là kết quả OCR.
PDF quét chỉ có ảnh, không có chữ/vector đáp án ẩn; bản ABBYY giả riêng
có lớp chữ và đường kẻ bảng. Hai PDF lớp chữ cũ vẫn giữ làm tham chiếu.

OCR-MAY ca 2/3/4/5/7/9 đã kiểm bằng Core giả (CoreGia), ABBYY giả ở thư
mục DEMO tạm. Ca 3 quan sát hàng chờ 3→2→1→0 bằng trạng thái CoreGia,
chống gửi lại lượt dở, không là kiểm màn hình thật. OCR-8 có màn cấu hình/hạn mức
đã kiểm bằng KttCore và DOM giả của Node, chờ Core nạp màn thật; ca 6 chờ thiết kế trích vùng với Đối chiếu, ca 8 chờ bí mật và
cầu nối có khóa. Chưa chạy Linux hoặc ABBYY/Core thật.

Nhật ký JSON stderr ghi năng lực, trạng thái, nguồn đọc và
`cho_nguon_giay`/`chay_giay`/`tong_giay`. Chờ là thời gian đợi ABBYY,
kết thúc trước đọc lớp chữ trả về; chạy gồm phần nội bộ/Tesseract và
xuất Word. SDK chưa cấp mốc vào hàng chờ Core nên chưa đo được thời gian
chờ ở Core. Chỉ log action đã được gọi; tệp >20 MiB bị SDK chặn trước
action. Lỗi bất ngờ trong action đổi thành câu cố định, tránh traceback
SDK lộ nội dung/đường dẫn. Không ghi tên tệp, đường dẫn, nội dung hoặc khóa.
Thời gian chạy xong action chưa bao gồm nộp kết quả/kết thúc phía SDK.

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

## Cấu hình và ngăn dữ liệu (OCR-8)

Admin dùng màn `ui/cau_hinh.js` trong Quản lý engine › OCR › Cấu hình.
Schema: `cau_hinh.schema.json`. Cấu hình là bản ghi bảng `cau_hinh`, khóa
`{"ma": "cau_hinh"}`; giá trị có `abbyy` và `tesseract`. Engine đọc bằng
`doc_cau_hinh(ngan, schema)`, kiểm kiểu/giới hạn và điền mặc định.
Không đọc cấu hình máy hoặc thư mục dữ liệu từ biến môi trường.

Thiếu cấu hình: `chi_abbyy` trả `CHUA_CAU_HINH` và hướng dẫn Admin.
Giữ hành vi chọn nguồn trước đây: chế độ tự động và `chi_tesseract` có
thể dùng Tesseract mặc định (tự tìm executable, `vie+eng`) khi không có
cấu hình; lượt ABBYY dở vẫn phải đối chiếu trước. PDF có lớp chữ không
cần cấu hình. Cấu hình sai trả câu lỗi cố định, không lộ giá trị.

Mọi trạng thái đi qua `viec.ngan` khi SDK cấp; nếu không có thì dùng
`chon_ngan(app)`. Có `app.ngan` thì dùng ngăn Core; SDK 2.0 tạm dùng
`NganBoNho`. RAM chỉ sống trong tiến trình, **khởi động lại sẽ mất hạn mức
và dấu chống trùng**, theo quyết định Anh 15/11. Cảnh báo này in đúng một
lần trên stderr khi chọn RAM. Không tự nhập dữ liệu từ sổ đĩa cũ.

| Bảng | Khóa/phạm vi | Nội dung |
|---|---|---|
| `cau_hinh` | `ma`, engine | Cấu hình ABBYY/Tesseract |
| `han_muc_ngay` | `ngay`, engine | Trang nhận theo giây UTC trong ngày; trang đang giữ theo mã lượt |
| `luot_abbyy` | `ma_tuong_quan`, phap_nhan | Duy nhất `[phap_nhan_id, bam_noi_dung]`; chỉ metadata |
| `trang_thai_engine` | `ma`, engine | Bản `abbyy` cập nhật 30 giây/lần; bản `han_muc` là mốc CAS của sổ |

Giữ trang và `lay_hoac_tao` lượt nằm trong **một lô nguyên tử** trước khi
gửi. Tất cả thay đổi sổ cùng tăng mốc CAS `han_muc`, kể cả qua nửa đêm;
xung đột thì đọc lại và thử tối đa 12 lần, không cộng trang từ lần thất bại.
Đọc ban đầu đã cũ thì nhập lượt vừa có, không tạo thế hệ gửi tiếp.
Trang đã dùng tính đúng cửa sổ trượt 30 × 86.400 giây; trang đang giữ vẫn
chặn hạn mức cho tới khi có căn cứ chốt/nhả, kể cả quá 30 ngày.

Quyền xử lý một lượt dùng CAS trên `chu_xu_ly`/`han_xu_ly`, không dùng
khóa tệp. Quyền kéo dài 30 giây, kiểm trong vòng chờ, gia hạn khi còn
10 giây; worker mất quyền phải dừng. Quyền hết hạn chỉ cho worker sau
**đọc lại cùng mã**, không cho gửi lại hoặc tự hoàn trang. Quyền được nhả
trong `finally`; ngăn Core thật mới có thể giữ dấu qua lần khởi động lại.

Màn chỉ gọi `KttCore.engine("e_ocr")`, lưu cấu hình bằng CAS; có xung đột
thì yêu cầu tải lại trước khi lưu. Hạn mức còn lại đã trừ cả trang đang giữ.
Trạng thái ABBYY lấy từ ngăn (bật cấu hình và truy cập được hai thư mục),
không khẳng định tiến trình FineReader đang chạy. Bản trạng thái quá 90
giây thì hiển thị chưa có cập nhật; không suy trạng thái từ công tắc.
Danh sách chờ đọc cả `chua_ro` và `dang_gui`, đọc hết phân trang, ẩn băm/mã.
Ngày dd/mm/yyyy, số có dấu chấm hàng nghìn; mọi nội dung qua `textContent`.
`mount(goc, {KttCore})` trả `{refresh, destroy}`; Core cần gọi `destroy`
khi đóng màn để dừng chu kỳ đọc 30 giây.

`engine.json` giữ schema 2.0, chỉ tăng phiên bản engine lên 1.0.8.
Khai báo dự kiến SDK 2.1 nằm riêng trong `KHAI-SDK-2.1.json`.
`ngan.py`/`cau_hinh.py` dùng nguyên bản chung NGAN-0 (PR #34).
Hai test so băm luôn chạy, chuẩn hóa CRLF thành LF trước khi tính SHA-256.
Ngăn RAM nhận khai báo bảng từ `KHAI-SDK-2.1.json/ngan_du_lieu`;
bảng cấu hình có khóa `{}`, giá trị chính là dict cấu hình.
`kho_tam.py`, `cau_hinh_may.py` và schema máy cũ giữ nguyên để chuyển
`LUU-TRU/` sau; chúng không thuộc đường chạy engine hiện tại.

Lượt `dang_gui`/`chua_ro` luôn tìm PDF đúng mã trong thư mục ra trước; không
có kết quả hợp lệ thì tiếp tục `ChuaRo`, không gửi lần hai, không chạy
Tesseract và không tự hoàn trang. Áp dụng cả khi chọn nguồn mới là
`chi_tesseract`, ABBYY vừa tắt hoặc thiếu cấu hình. Có PDF thì đối chiếu,
chuyển chỗ giữ sang trang đã dùng đúng một lần, kiểm đủ lớp chữ/số trang,
chốt `xong` trong ngăn rồi mới dọn PDF. Nếu chốt ngăn lỗi, giữ PDF bằng `ChuaRo`.
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

Khi SDK 2.1 cấp ngăn thật, dữ liệu sẽ được Core lưu bền qua cùng API.
Không dùng hàm `ocr_*_luot` hoặc cổng riêng cũ.

`demo/van_ban_tai_lieu.demo.json` chỉ minh họa hợp đồng bằng dữ liệu giả có
nhãn DEMO, gồm vị trí, ô trống và ô gộp; băm toàn số 0 là băm minh họa.

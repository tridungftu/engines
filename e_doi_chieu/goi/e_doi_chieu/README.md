# Đối chiếu bản ký — DC-3, phiên bản 0.3.0

`doi_chieu.doc_docx@1` nhận DOCX qua `viec.mo_tep`, kiểm bản đã chốt và
trả `van_ban_tai_lieu`. Đọc trong RAM bằng SDK và thư viện chuẩn, không
OCR/AI/Cloud, không chương trình ngoài. `doi_chieu.nhan_cap@1` nhận JSON cặp,
kiểm nguồn và chuẩn hóa có dấu vết; chưa triển khai so/đánh giá bản ký.

Đọc thân, đầu/chân trang, footnote/endnote, đoạn và bảng lồng; giữ ô trống,
gộp ngang/dọc. Quét sửa đổi/comment trong mọi phần XML Word, kể cả phần
phụ và thuộc tính: có thì `DC_WORD_CHUA_CHOT`, không Accept All. Vùng không
hỗ trợ hoặc hỏng trả `DC_WORD_KHONG_DOC_DUOC`, không trả văn bản thiếu.

Phạm vi hỗ trợ: WordprocessingML transitional, danh sách đánh số thông dụng
(decimal, decimalZero, letter, Roman, bullet). Chưa hỗ trợ Strict OOXML,
field động/kết quả field, hình/textbox, công thức, OLE/altChunk, danh sách
liên kết style/picture bullet và markup khác chưa hiểu; các vùng này bị
từ chối. Mọi quan hệ ngoài đều bị từ chối, kể cả hyperlink và template.

Trần cứng: DOCX 20 MiB; ZIP 2.000 mục/100 MiB giải nén, tỷ lệ nén ≤200;
XML mỗi phần 16 MiB, sâu ≤128, tổng ≤200.000 node; văn bản ≤500.000 ký tự;
JSON kết quả ≤20 MiB; bảng ≤256 cột/50.000 ô gốc, cây khối sâu ≤16.
Kiểm danh mục trước giải nén, kiểm bytes/EOF/CRC thật khi đọc XML.
Vượt trần trả `DC_QUA_GIOI_HAN`, không cắt nội dung.

Quy ước nguyên văn và vị trí (không chuẩn hóa NFC/strip ở bước đọc):

- Giữ nguyên chuỗi XML `w:t` đã giải mã, tab/ngắt dòng/gạch nối và nhãn
  đánh số nguồn. Các đoạn nối `\n`; bảng nối cột bằng ` | `, dòng bằng
  `\n`; ô phủ bởi ô gộp giữ chỗ trống, gốc ghi `gop_hang`/`gop_cot`.
- `khoi_docx` giữ thứ tự đoạn/bảng trong từng phần, gồm khối/ô lồng và
  offset `[bat_dau, ket_thuc)` theo Unicode code point trong đúng `van_ban`.
  Mỗi lát chuỗi bằng chính `van_ban` của khối/ô; offset không phải UTF-16/byte.
  Chỉ số `so_doan` chạy xuyên các phần; ngữ cảnh Điều/danh sách tách story.
- Thân trước, phần phụ theo tên OPC, từng chú thích theo thứ tự XML.
  `vung_docx` ghi phần/loại/ID chú thích, chỉ số khối bắt đầu và số khối;
  khối gốc ghi `phan`/`ma_chu_thich`, đoạn có tham chiếu ghi `chu_thich`.
  Đây là thứ tự tuần tự hóa ổn định, không phải vị trí trang vật lý.
- Chưa render Word: `so_trang=0`, `trang=[]`, cảnh báo chưa phân trang;
  không có trang/hộp giả. `bam_dau_vao` băm SHA-256 bytes DOCX thật.

SDK 2.0 dùng ngăn RAM, mất khi dừng; ngăn bền và màn quản trị chờ Core/SDK
2.1. Các màn trong bản khai là dự kiến, chưa có tệp UI. Cấu hình và dữ liệu
cần giữ chỉ qua Ngan; snapshot/ảnh do kho Core giữ, không lưu bền trên engine.

DEMO `demo/DEMO-ban-chot.docx` có nhãn DEMO, bảng gộp/ô trống, 1.000.000 VND
và 2026-10-30; không chứa hồ sơ thật. Chạy bằng venv và
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
python -m pytest e_doi_chieu/tests -q
python e_doi_chieu/tests/kiem_doc_lap.py
```

Đã kiểm bằng Core giả (CoreGia), chưa kiểm Core thật/Linux. Kết quả thật
và các cửa Core còn thiếu tại `e_doi_chieu/docs/VIEC.md`; nguồn/băm tại
`NGUON.md`. DC-2 có DEMO sạch chạy trực tiếp bằng lệnh `thu`.

## Nhận cặp — DC-3

Đầu vào theo `docs/DC-1-KHAO-SAT.md` §2: một tệp JSON UTF-8, kèm
`tham_so.bam_yeu_cau` băm **nguyên bytes**, kiểm trước parse. JSON từ chối
khóa trùng, NaN/Infinity, surrogate lẻ, đuôi thừa và cây sâu hơn 64 mức.
Không nhận khóa quyền/pháp nhân/module tự khai, đường máy, URL hoặc base64.
Mọi tham chiếu đều mở bằng `viec.mo_tep`; kiểm kích thước/băm thật,
phiên bản nguồn, quan hệ `bam_dau_vao` của từng kết quả đọc, trang/hộp/ảnh.
Word được đọc lại bằng DC-2 và so nguyên kết quả đã ghim (trừ phiên bản
engine tạo kết quả); không lấy `word_da_chot=true` làm chứng nhận đã chốt.
OCR lỗi, thiếu trang hoặc nguyên văn rỗng đều từ chối, không ra `khop`.

Core phải cấp quyền tệp con và bảo đảm provenance/phiên bản gắn nguồn,
bao gồm kết quả OCR và ảnh đúng bản ký. Băm chỉ kiểm bytes. SDK 2.0 mặc
định thiếu cửa tệp con sẽ trả `DC_THIEU_NGUON`; adapter DEMO chỉ ở tests,
không có nhánh giả lập/fallback trong runtime. PDF được kiểm dấu định dạng
vận chuyển, không tự đọc PDF hoặc gọi OCR để chứng thực lại nội dung.

Cấu hình đọc từ ngăn, thiếu trả `CHUA_CAU_HINH`. Bộ JSON do Core cấp được
ghim nguyên bytes, SHA-256 phải khớp `cau_hinh.bam_bo_chuan_hoa` và mã bộ
khớp `ma_bo_chuan_hoa`. Quy ước nội bộ của bộ tại DC-3 (không đổi schema
loại chung): `phien_ban=1`, `phien_ban_bo` khớp tham chiếu, mã bộ và
`chuan_hoa` bắt buộc; các phần quy tắc khác giữ nguyên cho lát tiếp theo.
Ví dụ **DEMO**, không phải bộ nghiệp vụ đã cấp để chạy thật:

```json
{
  "phien_ban": 1,
  "phien_ban_bo": "DEMO-1",
  "ma_bo_chuan_hoa": "DEMO-NFC-1",
  "chuan_hoa": {
    "unicode": "NFC",
    "khoang_trang": "gop",
    "dau_nhay": "thang",
    "gach_noi": "thong_nhat",
    "ngat_dong": "noi_trong_doan",
    "ngat_tu_cuoi_dong": "chi_gach_noi_mem",
    "dau_chan_trang": [],
    "bo_so_trang": false
  }
}
```

Không có bộ nới lỏng mặc định. Ngoài `unicode`, các lựa chọn dạng chuỗi
còn nhận `giu_nguyen`; danh sách đầu/chân trang và cờ số trang luôn phải
khai rõ. NFC giữ dấu tiếng Việt, emoji và hỗ trợ cả Hangul Jamo. Nháy cong
đổi sang nháy thẳng; gạch U+2010…U+2014 đổi `-`, giữ dấu trừ U+2212.
Khoảng trắng được gộp; chỉ nối ngắt dòng bên trong đoạn, giữ biên cấu trúc
và `\f` giữa trang. Chỉ bỏ **soft hyphen + ngắt dòng giữa chữ** trong một
đoạn; không xóa gạch nối cứng hoặc nối số/mã hợp đồng. Không tự chuẩn kiểu
đánh số, từ vựng hay bỏ dấu trên bản so chính.

Đầu/chân trang chỉ bỏ chuỗi đúng whitelist đã ghim và có story DOCX thật;
OCR còn cần vị trí lề và lặp ở ít nhất hai trang. Số trang chỉ bỏ nguyên
dòng `Trang n` hoặc `Trang n/tổng` ở lề, khớp số trang thật. Tiền, chữ số,
mã và nội dung thân giống header vẫn giữ. Mỗi vùng bỏ có offset/lý do;
không suy trang Word từ XML hoặc dựng hộp tọa độ mới.

Snapshot có hai nguyên phong bì văn bản, tham chiếu/băm nguồn, bộ/cấu hình,
ảnh/bằng chứng và bản chuẩn hóa. Mỗi bên `chuan_hoa` chứa `nguyen_van`,
`van_ban`, `anh_xa`, `vi_tri`, `da_bo`, `chua_neo_cau_truc`. Run ánh xạ là
`[đầu_chuẩn, cuối_chuẩn, đầu_gốc, cuối_gốc]`, Unicode nửa mở. Độ dài bằng
nhau là tịnh tiến; vùng co/giãn trỏ cả cụm gốc, ví dụ `Á` → `A\u0301`.
`vi_tri.ve_nguon(ban_chuan_hoa, a, b)` trả **các lát nguồn** và nút cấu trúc
giao nhau; lát có thể rời nhau khi bỏ soft hyphen/header. Đường dẫn nút
tính trong payload `van_ban_tai_lieu`, không phải đường tệp. Ô rỗng/gộp
vẫn có nút/offset; khối OCR lặp hoặc không neo được duy nhất chỉ có vị trí
trang và cảnh báo, không gán hộp đoán cho chữ. Giữ nguyên cây OCR gốc.

Snapshot đầy đủ tải bằng `tai_tep_ra`; phong bì schema đã duyệt chỉ giữ
tham chiếu/băm, trạng thái và số đếm. `da_nhan`: mới kiểm hai bản, các số
chưa đo là `null`, các bước sau `chua_kiem`, `ket_luan=null`,
`da_kiem_du=false`, `de_nghi_chan=true`. Không coi đây là kết luận máy.

Ngăn `luot_doi_chieu` dùng `lay_hoac_tao` theo pháp nhân, băm cặp, băm bộ
và phiên bản engine. Băm cặp gồm băm/phiên bản hai bản và băm các đầu ra
dẫn xuất/ảnh/bằng chứng, không phụ thuộc ID/tên tệp hay `ma_cap` người gọi.
Chỉ chủ lượt tải snapshot và cập nhật bằng CAS; lượt đồng thời đợi tối đa
khoảng một giây rồi báo thử lại nếu còn bận. CAS chốt thử lại tối đa ba
lần, không tải lại tệp để thử CAS. Tái dùng phải mở lại snapshot và **mọi
tham chiếu cũ** bằng quyền việc hiện tại. Hủy/lỗi để `can_thu_lai` bằng CAS,
không xóa sổ hoặc đè chủ khác. Ngăn chỉ giữ phong bì nhỏ, không toàn văn.

Các trần §2.3 được kiểm cả metadata và bytes thật: yêu cầu 1 MiB; từng tệp
gốc/ảnh/JSON nguồn ≤20 MiB, toàn việc ≤128 MiB bytes đọc (kể cả yêu cầu và
snapshot tái dùng); ≤60 trang, ≤20 triệu pixel/ảnh; ≤500.000 ký tự/bản và
tổng ≤1.000.000; snapshot ≤20 MiB, phong bì ≤64 KiB. Cấu hình chỉ được hạ
trần cứng, không cắt nội dung. ZIP vẫn chịu trần DC-2 và trần cấu hình.
Manifest khai trần đọc 20 MiB để SDK cho mở tệp con, engine tự giữ JSON
yêu cầu 1 MiB. SDK có thể từ chối đầu vào quá trần manifest trước handler.

PNG kiểm IHDR/pixel, CRC, EOF DEFLATE và đủ dòng/filter trong RAM; PNG
interlace chưa hỗ trợ sẽ từ chối. JPEG kiểm marker/khung/kích thước, **chưa
giải mã DCT** (`da_giai_ma=false`): DC-8 phải giải mã thực bằng thư viện đã
ghim trước quét. Không suy phép đổi `pt`↔`px`, DPI hoặc xoay từ metadata tự
khai; giữ tọa độ nguồn và kích thước ảnh riêng. DC-3 không đánh dấu đã quét.

`thu` tiếp tục kiểm DEMO Word 1/1; nhận cặp được kiểm end-to-end trong
pytest với CoreGia/NganBoNho/adapter tệp con, không thêm DEMO thành công
giả vào runtime thiếu quyền/cấu hình. Lớp bọc handler đổi lỗi bất ngờ thành
câu cố định để SDK 2.0 không in nội dung ngoại lệ; không sửa SDK và chưa
khép nợ log lỗi ngoài handler của SDK.

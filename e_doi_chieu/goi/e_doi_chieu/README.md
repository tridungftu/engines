# Đối chiếu bản ký — DC-2, phiên bản 0.2.0

`doi_chieu.doc_docx@1` nhận DOCX qua `viec.mo_tep`, kiểm bản đã chốt và
trả `van_ban_tai_lieu`. Đọc trong RAM bằng SDK và thư viện chuẩn, không
OCR/AI/Cloud, không chương trình ngoài. Chưa có handler nhận cặp/so bản ký.

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

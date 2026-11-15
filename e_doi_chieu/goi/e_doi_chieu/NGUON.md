# Nguồn của gói Đối chiếu

- SDK runtime: `kho_tri_thuc_sdk` 2.0.0, wheel nội bộ tại
  `docs/goi-gui-engine/sdk-2.0.0/`; API v1 giữ nguyên.
- `e_doi_chieu/ngan.py`, `cau_hinh.py`: chép nguyên mẫu NGAN-0 tại
  `_chung/mau-ma/`, test so SHA-256 sau chuẩn hóa CRLF→LF. Không sửa bản chép.
- Bốn schema dữ liệu: nguồn `_chung/contract/`, bản chép cùng thư mục phiếu,
  test so SHA-256 LF. Ba schema chung đã khóa giữ nguyên; schema
  `ho_so_doi_chieu` theo DC-P và DC-Q17 duyệt chiều 15/11/2026.
- DC-1 không chép thuật toán từ OCR/Trích xuất; chỉ khảo sát mã có sẵn trong
  workspace, dẫn nguồn tại `docs/DC-1-KHAO-SAT.md` của project engine.
- Chưa đưa từ điển, detector, model, font hoặc dependency ngoài SDK/thư viện
  chuẩn vào runtime. Nguồn/phiên bản/giấy phép/băm cần lead cấp ở lát sau.
- Công cụ kiểm: pytest 9.1.1 có sẵn qua venv system-site-packages; bộ kiểm
  tập con schema dùng thư viện chuẩn (từ DC-3 có ở runtime cho hai schema
  đã ghim, không phải triển khai đầy đủ JSON Schema). Không tải gói/mạng.

## DC-2 — 15/11/2026

Chuyển có sửa từ nguồn nội bộ đã được phép tái dùng theo phiếu DC-2:

| Nguồn tương đối từ repo | Đích tương đối trong gói | Phần chuyển và sửa |
|---|---|---|
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `e_doi_chieu/doc_docx.py` | Kiểm ZIP/XML và adapter bytes SDK; thay toàn bộ Accept All bằng từ chối sửa đổi/comment, quét mọi XML, kiểm quan hệ/kiểu phần; thêm kiểm EOF/CRC thật, đọc cả story phụ, không cảnh báo rồi bỏ nội dung |
| Cùng nguồn trên | `e_doi_chieu/cau_truc.py` | Numbering, đoạn/bảng lồng, ô trống/gộp, offset; kiểm nghiêm node/thuộc tính, không bỏ qua vùng lạ; không chuyển hàm Accept All |

Nguồn gốc của thuật toán TX-1 là `e_trich_xuat/ma-nguon/docx.py` và
`e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py`, theo NGUON.md của
Trích xuất. Không sửa các nguồn hoặc import engine khác. Không thêm
dependency/giấy phép bên thứ ba; SDK 2.0.0 và thư viện chuẩn Python.

SHA-256 dưới đây tính trên bytes UTF-8 đổi CRLF→LF cho mã nguồn, không đổi
nội dung khác. DOCX/wheel băm nguyên bytes:

| Nguồn | SHA-256 |
|---|---|
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ma-nguon/docx.py` | `84b5662856ecf2742360077012377f913698a917e1fd4a4a08f87568e1af6a5b` |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f` |
| SDK `kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `demo/DEMO-ban-chot.docx` | `e086e49c1dfad0cdfc702ab141a9de6123cbd123e4c7110df975b673e194bcaa` |

DEMO tạo xác định bằng `tao_goi`/`table_demo` trong `e_doi_chieu/tests/test_dc2.py`;
nội dung hoàn toàn giả, không có nguồn tài liệu khách hàng. Test đối chiếu
bytes fixture với DEMO đóng gói, so nguyên văn/offset, không chỉ kiểm status.

## SHA-256 bản chuyển DC-2

Băm mã nguồn sau CRLF→LF; không gồm NGUON.md.

| Tệp trong gói | SHA-256 |
|---|---|
| `e_doi_chieu/doc_docx.py` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |
| `e_doi_chieu/cau_truc.py` | `ddde14383f97bf5c1fa1a2161aed7db8f3ea1e36004c16350a2db52018c2d333` |
| `e_doi_chieu/chay.py` | `0544a6a7dae1cca5a0331383349d7d5c781500f6b1fd4bf8c63820b1aeaf4246` |

## DC-3 — 15/11/2026

- `ho_so.py`, `chuan_hoa.py`, `vi_tri.py`: viết trong lát này bằng thư viện
  chuẩn Python và SDK 2.0.0; tái dùng trực tiếp bộ đọc/kiểm ZIP của DC-2
  trong cùng gói. Không import/gọi engine khác, không thêm dependency.
- Test cặp dùng DOCX từ generator DEMO DC-2, PDF một trang có xref do test
  tạo và PNG grayscale thực do test dựng; OCR/phân quyền là adapter giả
  ghi rõ trong `tests/test_dc3.py`, không phân phối trong gói runtime.
- Test parser ảnh còn đọc hai tệp DEMO đã có của OCR:
  `e_ocr/goi/e_ocr/demo/DEMO-1-trang.jpg` và `DEMO-1-trang.png`.
  Chỉ dùng bytes fixture để kiểm PNG/JPEG; không chạy hoặc import OCR.
- Không cấp bộ quy tắc/từ điển/detector thật trong lát này. Bộ JSON DEMO
  chỉ kiểm hợp đồng ghim băm/cấu hình và phép chuẩn hóa, không thay phê duyệt
  nguồn nghiệp vụ. Chi tiết quy ước tại README; Cần Core tại VIEC.md.
- Băm `chay.py` ở bảng DC-2 là ảnh lịch sử của DC-2; tệp đã được mở rộng
  handler nhận cặp/lớp bọc lỗi an toàn trong DC-3. Hai bản chép NGAN-0 và
  bốn schema dữ liệu tiếp tục giữ nguyên, test so băm LF.

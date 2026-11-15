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
  tập con schema chỉ ở tests, dùng thư viện chuẩn. Không tải gói/mạng.

# CHANGELOG — e_trich_xuat

## 0.1.0-demo.1 (G3-GOI-31, 05/11/2026)
- Chuyển nguyên trạng `ai_chung.py`, `chay.py`, `docx.py`, `do_chinh_xac.py`, `quy_trinh.py`, `tham_so.py`, `tich_hop.py`, `engine.json` từ `src/kho_tri_thuc/engines/e_trich_xuat/` sang `engines/e_trich_xuat/` (git mv).
- Sửa nội dung: `engine.json` khoảng tương thích Core `>=1.0.0,<2.0.0` -> `>=1.0.0 <2.0.0` (dấu phẩy làm discovery báo SemVer không hợp lệ khi gói được quét); khóa đường dẫn trong `NGUON_CHEP` của `tich_hop.py` (3 khóa) trỏ đường mới; SHA-256 không đổi.
- Thêm shim namespace tại đường cũ, `__init__.py` marker, `contract/schemas.json`, `contract/vi_du.json`, tài liệu và test độc lập.

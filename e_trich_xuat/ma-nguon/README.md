# e_trich_xuat — Trích tham số hợp đồng từ DOCX

Capability thực có: `trich.tham_so_hop_dong@1` (vào `tham_chieu_tep.v1`, ra `tham_so.v1`), chạy headless qua SDK engine, bí mật từ stdin/handle.

- Vị trí: gói nằm tại `engines/e_trich_xuat/`; tên Python vẫn `kho_tri_thuc.engines.e_trich_xuat` nhờ shim `src/kho_tri_thuc/engines/e_trich_xuat/__init__.py` (chỉ đặt `__path__`). Import tương đối `...m4`, `...sdk_core` vẫn chạy nhờ tên gói giữ nguyên.
- Core khởi động qua `ho_so_chay_mau.diem_vao` (`tich_hop.chay_noi`) trong `engine.json`; discovery (`core/nap_engine.py`) đọc `engine.json` + `contract/schemas.json`, không import mã.
- Contract: `contract/schemas.json` là bản phân phối đúng bản Core đã công bố (`chung.v1`, `tham_chieu_tep.v1`, `tham_so.v1`); không tạo contract mới.
- Phụ thuộc hiện còn: `kho_tri_thuc.sdk_core`, `kho_tri_thuc.m4.review_goc.trich_xuat` (nguồn Review, cả đường tới `ai_local`), `tri_thuc.cong_ai`. Chưa tự đủ độc lập; các lát GOI-TRICH-NGUON/THUAN/AI-SDK/RUNTIME xử lý tiếp.
- Tên manifest ghi chờ phép đo TRICH-4b; trạng thái: CHUA_KIEM (mốc chuyển vị trí).

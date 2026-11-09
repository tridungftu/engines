# e_hoi_ai — Cổng AI dùng chung

Capability thực có: `ai.hoi@1` (vào `hoi_ai.v1`, ra `tra_loi_ai.v1`), chạy headless qua SDK engine, bí mật từ stdin/handle.

- Vị trí: gói nằm tại `engines/e_hoi_ai/`; tên Python vẫn `kho_tri_thuc.engines.e_hoi_ai` nhờ shim `src/kho_tri_thuc/engines/e_hoi_ai/__init__.py` (chỉ đặt `__path__`).
- Core khởi động qua `ho_so_chay_mau.diem_vao` trong `engine.json`; discovery (`core/nap_engine.py`) đọc `engine.json` + `contract/schemas.json`, không import mã.
- Contract: `contract/schemas.json` là bản phân phối đúng bản Core đã công bố (cùng `$id`, nội dung); không tạo contract mới.
- Phụ thuộc hiện còn: `kho_tri_thuc.sdk_core`, `kho_tri_thuc.tri_thuc.cong_ai` (sẽ tháo ở GOI-AI-LOI/ADAPTER). Chưa tự đủ độc lập.
- Tài khoản Windows theo mã hồ sơ do Core cấp; không ghi thông tin thật ở đây.
- Trạng thái: CHUA_KIEM (mốc chuyển vị trí; chưa gọi AI thật).

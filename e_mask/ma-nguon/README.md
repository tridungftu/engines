# e_mask — Che dữ liệu (Chờ)

Trạng thái: Chờ. Chưa công bố capability; chưa có `engine.json`, `contract/schemas.json`, `contract/vi_du.json`.

- Vị trí: gói nằm tại `engines/e_mask/`; tên Python vẫn `kho_tri_thuc.engines.e_mask` nhờ shim `src/kho_tri_thuc/engines/e_mask/__init__.py` (chỉ đặt `__path__`).
- `chay.py`: bọc tiến trình nguồn Mask (Core cấp cổng, launcher tài khoản; mặc định cấm chạy khi chưa có bằng chứng nhận khóa qua stdin/handle). `vong_doi.py`: vòng đời nội bộ.
- `contract/du_thao.json`: bốn schema HTTP dự thảo, `dang_ky=false`, `kich_hoat=false`, namespace `urn:ktt:du-thao`; không phải contract Core đã duyệt.
- Phụ thuộc hiện còn: `kho_tri_thuc.sdk_core`, helper `kho_tri_thuc.nguon.trich6_host.env_con` và nguồn Mask ngoài (`run_privacy.py`). Interface launcher đã qua `sdk_core.ho_so_engine` ở lát 29, không còn import trực tiếp `core.khoi_chay_tai_khoan` trong khung. Chưa tự đủ độc lập.
- Không tạo capability rỗng hay giả; manifest chỉ thêm khi adapter nguồn đạt (lát GOI-MASK-CAP).

Nguồn chính thức là **Mask file v2** tại `D:\GPT\Phan mem Mask file\Mask file v2`; chưa chốt revision/SHA nguồn và chưa có giấy phép phân phối ghi nhận trong căn cứ repo. Xem [NGUON.md](NGUON.md) và [nguon/PHU-THUOC.md](nguon/PHU-THUOC.md) để phân biệt phụ thuộc khung engine với thư viện của tiến trình nguồn.

Lock nguồn được khảo sát dùng `cryptography==50.0.1`, còn Core khai `cryptography==49.0.0`. Đề xuất môi trường Python riêng cho Mask, tiến trình riêng qua adapter đã duyệt; không nâng Core đồng loạt. Khung hiện gọi `sys.executable`, nên tách môi trường vẫn cần lead chốt cách chọn Python nguồn trong lát triển khai riêng, chưa được thực hiện ở đây.

Hai phương án **bundle nguồn sạch** và **cài riêng được ghim** đều **chờ Anh chọn**. Chưa có nguồn sạch thực dùng, seam cấp khóa stdin/handle, adapter/capability và contract đã duyệt thì Mask tiếp tục **Chờ**. Test thuần/mock đạt không chứng minh package độc lập hoặc nguồn Mask thật đã chạy đạt.

Lát G3-GOI-30 chỉ cập nhật tài liệu theo CD-086, không tạo `requirements.lock`, manifest hoặc capability. Theo kế hoạch §6.3, wheel SDK 1.4.1 dựng sau lát 04 chỉ là candidate; không ghim engine vào wheel này, không đổi version SDK. Lead chốt SDK cuối sau lát 34 và kiểm tương thích.

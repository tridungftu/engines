# Nguồn mã — AI-1 và AI-3, 14/11/2026

Gói chạy dùng thư viện chuẩn Python ≥ 3.11 và SDK `kho_tri_thuc_sdk` 2.0.0 từ wheel trong repo. Không thêm thư viện bên ngoài. Ghim đầy đủ và cài máy sạch thuộc AI-5.

## Nguồn khung AI-0 đã dùng lại

- Mẫu khung: `docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_dem_tu/` trong repo; chép `engine.json`, `README.md`, `demo/mau.txt`, `e_demo_dem_tu/__init__.py`, `e_demo_dem_tu/chay.py` vào vị trí tương ứng của gói `e_hoi_ai`, rồi sửa tên và nội dung. Đã bỏ nhánh import Core của mẫu; gói chỉ dùng SDK.
- SDK đã kiểm: `kho_tri_thuc_sdk-2.0.0-py3-none-any.whl`, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` (trùng `SHA256SUMS.txt` của bản phát hành).
- Contract: `_chung/docs/LOAI-DU-LIEU-RIENG.md` (14/11/2026); bản chuẩn máy kiểm tại `_chung/contract/`, sao nguyên byte vào `contract/`. Test đối chiếu SHA-256, không cần thư viện ngoài SDK để chạy gói.
- `e_hoi_ai/cau_hinh_may.py` và `contract/cau_hinh_may.schema.json`: viết mới ở AI-0 theo quyết định tạm ở `_chung/docs/GIAO-CODEX-THU-TU.md` §2 và phiếu giao engine §2.
- Tại mốc AI-0 chưa chuyển lõi từ `ma-nguon/`; AI-1 bổ sung các phần dưới đây. Mã nguồn cũ giữ nguyên.

## Lõi chuyển sang ở AI-1

Các đường dẫn dưới đây tính từ thư mục `e_hoi_ai/` trong repo nguồn. Tệp cũ giữ nguyên, chỉ chuyển phần lõi cần dùng sang hợp đồng SDK 2.0.

| Nguồn cũ | Đích trong gói | Phần chuyển và điều chỉnh |
|---|---|---|
| `ma-nguon/lib/ai_cuc_bo.py` | `e_hoi_ai/ai_cuc_bo.py` | Kiểm IP và nguồn Tailscale, socket trực tiếp, tắt proxy/redirect, trần JSON và metadata model. Đổi tên mã sang tiếng Việt không dấu; nhận URL gốc hoặc endpoint; dùng timeout từ cấu hình máy; bỏ discovery, cooldown và chức năng chọn đối tác không thuộc AI-1. |
| `ma-nguon/lib/cong_ai.py` | `e_hoi_ai/cong_ai.py` | Khung trích dẫn, đọc JSON, kiểm giá trị thuộc trích dẫn và cổng Local. Trích dẫn kiểm đúng từng ký tự, bổ sung kiểm token số; bỏ toàn bộ Mask, bí mật, thống kê bền và định tuyến Cloud. |
| `ma-nguon/dto.py` và các lớp DTO gốc trong `ma-nguon/lib/cong_ai.py` | `e_hoi_ai/dto.py` | Thay tái xuất lớp cũ bằng DTO độc lập đúng đầu vào/đầu ra phiếu 2.0; giữ kiểm prompt không rỗng. |
| `ma-nguon/hoi.py` | `e_hoi_ai/hoi.py` | Adapter mỗi request một cấu hình/kết quả; thay metadata và schema Core cũ bằng `viec` của SDK, cấu hình máy ngoài gói, kiểm hủy và nhật ký stderr chỉ metadata. |

SHA-256 nguồn trước khi chuyển:

```text
06bc8c6e4037766a674f1da93f0bacfa1397eb0d8c5f8d53d8cdb298767a5e49  ma-nguon/lib/ai_cuc_bo.py
1d35ee32bcc70621b8aababaf77508296c8cc94a93977f04a99d1aa8ab17f571  ma-nguon/lib/cong_ai.py
998528300abbf72492bfbc606c6514fec7fa0e2a75a5a5cbef631ab57bb09bc6  ma-nguon/dto.py
12e24522145a243a5e007bb7a468bcbb82a75f1c21ac179f68f8124bd82cbbba  ma-nguon/hoi.py
```

SHA-256 bốn tệp lõi tại mốc AI-1 (đường dẫn tương đối từ gói; AI-3 cập nhật bên dưới):

```text
4d0ddb9a1ccc9de23ff4af0333988feddc5a5c8e705765a5be142923aa76e029  e_hoi_ai/ai_cuc_bo.py
561d6b3d261c69c24bcfaaf090c87a5094a0cbb3b3bc984a631ad919aa25c97f  e_hoi_ai/cong_ai.py
fbd0fa58655b36e7a2d45667bbdef34abee3ad5eb0a6caa31cfa7b1d66543261  e_hoi_ai/dto.py
fb67c391ff2c617299329d249ed712d913dad6fcd3a3088a11703ec6c0aabf4a  e_hoi_ai/hoi.py
```

## AI-3 — phát hiện và chọn model

- `e_hoi_ai/chon_model.py`: viết mới theo `docs/KS-AI-MODEL.md` §2, phiếu AI-3 và lệnh giao của Anh. Chỉ thư viện chuẩn, dùng lại bộ HTTP an toàn của `ai_cuc_bo.py`; không thêm client AI/dependency.
- `e_hoi_ai/ai_cuc_bo.py`: thay phép kiểm cố định `/v1/models` bằng catalog API đã nhận diện và kiểm khả dụng hiện tại trước POST.
- `e_hoi_ai/cong_ai.py`: ủy quyền chọn model cho mô-đun riêng; giữ nguyên seam provider và hậu kiểm trích dẫn.
- `e_hoi_ai/hoi.py`: báo tiến độ trước discovery, truyền hàm kiểm hủy tới bộ chọn.
- `e_hoi_ai/dto.py`, `engine.json`: xuất `ly_do_chon_model` trong kết quả hỏi tài liệu; phiên bản gói `0.3.0`.
- Giữ nguyên mọi tệp `ma-nguon/`, không chuyển/xóa tệp cũ. SHA-256 hiện tại của 5 tệp Python thay đổi ở AI-3:

```text
af90f5ce6c9de8e61617894281254bc42c2d8c9ccf7d1700767adcb0f043bb64  e_hoi_ai/ai_cuc_bo.py
e09755393f91d0a33ff0c28b7e9b17f5c24321a09100d7d4e55f19b77e90e808  e_hoi_ai/chon_model.py
f03328adf7e28f058f233eb99e42160ab85a1762dc60aa988161c47d6a0f0ecb  e_hoi_ai/cong_ai.py
f621510b5dc8ea277d05e2449db72b8e9ed0b7ea78efc9c41fbb4b3a0e72a1bc  e_hoi_ai/dto.py
9c7d2578864b670caf030bf50b8bf1972680fc7e7bbe873bec2345a7e9cad140  e_hoi_ai/hoi.py
```

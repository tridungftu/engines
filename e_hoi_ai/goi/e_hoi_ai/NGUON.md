# Nguồn mã — AI-1, AI-2 và AI-3, 14/11/2026

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

SHA-256 bốn tệp lõi tại mốc AI-1 (đường dẫn tương đối từ gói; AI-2 và AI-3 cập nhật bên dưới):

```text
4d0ddb9a1ccc9de23ff4af0333988feddc5a5c8e705765a5be142923aa76e029  e_hoi_ai/ai_cuc_bo.py
561d6b3d261c69c24bcfaaf090c87a5094a0cbb3b3bc984a631ad919aa25c97f  e_hoi_ai/cong_ai.py
fbd0fa58655b36e7a2d45667bbdef34abee3ad5eb0a6caa31cfa7b1d66543261  e_hoi_ai/dto.py
fb67c391ff2c617299329d249ed712d913dad6fcd3a3088a11703ec6c0aabf4a  e_hoi_ai/hoi.py
```

## Phần AI-2

- `e_hoi_ai/hoi_yeu_cau.py`: viết mới theo `GIAO-CODEX-e_hoi_ai.md` AI-2 và `_chung/docs/LOAI-DU-LIEU-RIENG.md`; dùng lại DTO, khung prompt, chọn provider/model và hậu kiểm trích dẫn của AI-1. Không chuyển thêm mã nguồn cũ.
- `e_hoi_ai/khuon_json.py`: viết mới, tập con JSON Schema 2020-12 kiểm offline bằng thư viện chuẩn. Tập từ khóa hỗ trợ và giới hạn ghi trong README. Không tải schema/reference từ mạng; không thêm thư viện chạy hoặc `requirements.lock` mới.
- `e_hoi_ai/ai_cuc_bo.py`: bổ sung truyền khuôn qua Ollama native hoặc OpenAI-compatible; giữ lớp mạng đã chuyển ở AI-1. `e_hoi_ai/cong_ai.py` chỉ thêm tham số tùy chọn `khuon` ở provider Local. `e_hoi_ai/chay.py` chỉ nối hàm AI-2 vào cổng đã khai.
- QA bổ sung trên máy phát triển dùng `Draft202012Validator` có sẵn để đối chiếu 656 cặp schema/dữ liệu và hai kết quả thực từ Local giả + CoreGia với contract chung. Công cụ QA này không phải phụ thuộc của gói hay pytest lưu trong repo. `multipleOf` của bộ kiểm tự viết dùng phân số chính xác; có test riêng `0.3` chia hết cho `0.1` để tránh sai số float.

SHA-256 năm tệp Python thêm/sửa tại mốc AI-2 (byte tại mốc AI-2 trước khi gộp):

```text
363f5dbacb7d595a9c6f00d4914198fafbc0d35d2ca658493ad89c9d4faa74a0  e_hoi_ai/ai_cuc_bo.py
8988b503ab2651567c19845af1e386ada217dcd8509f3d41a20634c14eb5bb9d  e_hoi_ai/chay.py
6f5bb361dbb2c64dd1448f6dd2072d6d33d47660cb7d613fac8e289211197a4c  e_hoi_ai/cong_ai.py
9fe647d57ff269b310e5769c84faad63426d04cf122cf048d6fa95bed039ab6f  e_hoi_ai/hoi_yeu_cau.py
ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df  e_hoi_ai/khuon_json.py
```

## AI-3 — phát hiện và chọn model

- `e_hoi_ai/chon_model.py`: viết mới theo `docs/KS-AI-MODEL.md` §2, phiếu AI-3 và lệnh giao của Anh. Chỉ thư viện chuẩn, dùng lại bộ HTTP an toàn của `ai_cuc_bo.py`; không thêm client AI/dependency.
- `e_hoi_ai/ai_cuc_bo.py`: thay phép kiểm cố định `/v1/models` bằng catalog API đã nhận diện và kiểm khả dụng hiện tại trước POST.
- `e_hoi_ai/cong_ai.py`: ủy quyền chọn model cho mô-đun riêng; giữ nguyên seam provider và hậu kiểm trích dẫn.
- `e_hoi_ai/hoi.py`: báo tiến độ trước discovery, truyền hàm kiểm hủy tới bộ chọn.
- `e_hoi_ai/dto.py`, `engine.json`: xuất `ly_do_chon_model` trong kết quả hỏi tài liệu; phiên bản gói `0.3.0`.
- Giữ nguyên mọi tệp `ma-nguon/`, không chuyển/xóa tệp cũ. SHA-256 tại mốc AI-3 của 5 tệp Python thay đổi:

```text
af90f5ce6c9de8e61617894281254bc42c2d8c9ccf7d1700767adcb0f043bb64  e_hoi_ai/ai_cuc_bo.py
e09755393f91d0a33ff0c28b7e9b17f5c24321a09100d7d4e55f19b77e90e808  e_hoi_ai/chon_model.py
f03328adf7e28f058f233eb99e42160ab85a1762dc60aa988161c47d6a0f0ecb  e_hoi_ai/cong_ai.py
f621510b5dc8ea277d05e2449db72b8e9ed0b7ea78efc9c41fbb4b3a0e72a1bc  e_hoi_ai/dto.py
9c7d2578864b670caf030bf50b8bf1972680fc7e7bbe873bec2345a7e9cad140  e_hoi_ai/hoi.py
```

## Việc gộp AI-2/AI-3 — 0.4.0, 14/11/2026

- `_kiem_model` dùng lại catalog AI-3 đã xác minh để trả loại API cho khuôn AI-2, không dò API thêm; `hoi_yeu_cau.py` truyền kiểm hủy tới bộ chọn model.
- Giữ nguyên nguồn và nội dung hai lát ở trên; các SHA-256 tại mốc AI-1/AI-2/AI-3 là lịch sử. Danh sách dưới đây là SHA-256 toàn bộ tệp hiện tại trong gói sau gộp, tính theo byte worktree; không tự băm `NGUON.md` để tránh băm tự tham chiếu.
- Không thêm thư viện; phiên bản manifest 0.4.0. Đã kiểm bằng Core giả (CoreGia); xem kết quả việc gộp trong README và `e_hoi_ai/docs/VIEC.md`.

```text
247d0ffbab081fd0db0a0c168a9b80d6c635d3847312559023e755b05ad3b1f9  CHANGELOG.md
d8c7fb9858e79a722ca30059df90534024ba672e6981486a44da7688c356356a  contract/cau_hinh_may.schema.json
4c7491e5798f2774965acd49e6834634d26b3b032db8c6f0847fe06e2a0f33ee  contract/tra_loi_ai.schema.json
d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902  contract/van_ban_tai_lieu.schema.json
97c909c439defaff1d653d1448c8931495a2f81f14df3e05cf4d915111d11a75  contract/yeu_cau_ai.schema.json
78ff41b4f92eb3f850507402706b6fdcae9beff86d8dd8897670cde0e71eff12  demo/mau.txt
58401cc810f7658d796f76ce53ed2671f71f57635e6b93fd9d598cd55115ffab  e_hoi_ai/__init__.py
c6dce3bcdb427473ae3cc2b8ed4173a05a7b8a3c6a6280b4b1b2889426e4e21c  e_hoi_ai/ai_cuc_bo.py
8079dfe377ea47552b0b558da0955b5a34834c670395f68aa77a09699203b6f7  e_hoi_ai/cau_hinh_may.py
8988b503ab2651567c19845af1e386ada217dcd8509f3d41a20634c14eb5bb9d  e_hoi_ai/chay.py
81380fc3f7335f14cf85c0cd4a2e890d822a16081edbd6e57764596fab88d427  e_hoi_ai/chon_model.py
428e1bcfc06b2f232d75bd64111cdd7a4e96b1ca9e8df96d848d7c4a3a135b02  e_hoi_ai/cong_ai.py
f621510b5dc8ea277d05e2449db72b8e9ed0b7ea78efc9c41fbb4b3a0e72a1bc  e_hoi_ai/dto.py
9c7d2578864b670caf030bf50b8bf1972680fc7e7bbe873bec2345a7e9cad140  e_hoi_ai/hoi.py
69a7c0a9498ea8073574dbb3f482576042132e3faf040cb52342b294c9d0f84d  e_hoi_ai/hoi_yeu_cau.py
ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df  e_hoi_ai/khuon_json.py
6fc057b9f2ce418b49a13bb0987c5ccf4f4c9aadf4e9e3eeb0619d8453f64202  engine.json
a188fb508caf41e7ae77263205cd5edeb69a7073e9abaa02771ecd21833bee61  README.md
```

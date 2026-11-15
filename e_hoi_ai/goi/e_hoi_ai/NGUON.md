# Nguồn mã — AI-1, AI-2 và AI-3, 14/11/2026

Quy ước SHA-256: chuẩn hóa CRLF và CR thành LF trước khi băm; đường dẫn tương đối từ thư mục gói. `NGUON.md` không tự băm vì tự tham chiếu.

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

## Phần AI-2

- `e_hoi_ai/hoi_yeu_cau.py`: viết mới theo `GIAO-CODEX-e_hoi_ai.md` AI-2 và `_chung/docs/LOAI-DU-LIEU-RIENG.md`; dùng lại DTO, khung prompt, chọn provider/model và hậu kiểm trích dẫn của AI-1. Không chuyển thêm mã nguồn cũ.
- `e_hoi_ai/khuon_json.py`: viết mới, tập con JSON Schema 2020-12 kiểm offline bằng thư viện chuẩn. Tập từ khóa hỗ trợ và giới hạn ghi trong README. Không tải schema/reference từ mạng; không thêm thư viện chạy hoặc `requirements.lock` mới.
- `e_hoi_ai/ai_cuc_bo.py`: bổ sung truyền khuôn qua Ollama native hoặc OpenAI-compatible; giữ lớp mạng đã chuyển ở AI-1. `e_hoi_ai/cong_ai.py` chỉ thêm tham số tùy chọn `khuon` ở provider Local. `e_hoi_ai/chay.py` chỉ nối hàm AI-2 vào cổng đã khai.
- QA bổ sung trên máy phát triển dùng `Draft202012Validator` có sẵn để đối chiếu 656 cặp schema/dữ liệu và hai kết quả thực từ Local giả + CoreGia với contract chung. Công cụ QA này không phải phụ thuộc của gói hay pytest lưu trong repo. `multipleOf` của bộ kiểm tự viết dùng phân số chính xác; có test riêng `0.3` chia hết cho `0.1` để tránh sai số float.

## AI-3 — phát hiện và chọn model

- `e_hoi_ai/chon_model.py`: viết mới theo `docs/KS-AI-MODEL.md` §2, phiếu AI-3 và lệnh giao của Anh. Chỉ thư viện chuẩn, dùng lại bộ HTTP an toàn của `ai_cuc_bo.py`; không thêm client AI/dependency.
- `e_hoi_ai/ai_cuc_bo.py`: thay phép kiểm cố định `/v1/models` bằng catalog API đã nhận diện và kiểm khả dụng hiện tại trước POST.
- `e_hoi_ai/cong_ai.py`: ủy quyền chọn model cho mô-đun riêng; giữ nguyên seam provider và hậu kiểm trích dẫn.
- `e_hoi_ai/hoi.py`: báo tiến độ trước discovery, truyền hàm kiểm hủy tới bộ chọn.
- `e_hoi_ai/dto.py`, `engine.json`: xuất `ly_do_chon_model` trong kết quả hỏi tài liệu; phiên bản gói `0.3.0`.
- Giữ nguyên mọi tệp `ma-nguon/`, không chuyển/xóa tệp cũ.


## Việc gộp AI-2/AI-3 — 0.4.0, 14/11/2026

- `_kiem_model` dùng lại catalog AI-3 đã xác minh để trả loại API cho khuôn AI-2, không dò API thêm; `hoi_yeu_cau.py` truyền kiểm hủy tới bộ chọn model.
- Giữ nguyên nguồn và nội dung hai lát ở trên; danh mục SHA-256 hiện hành ở cuối tệp.
- Không thêm thư viện; phiên bản manifest 0.4.0. Đã kiểm bằng Core giả (CoreGia); xem kết quả việc gộp trong README và `e_hoi_ai/docs/VIEC.md`.


## AI-6 — Khung Cloud, 14/11/2026

- `e_hoi_ai/nha_cung_cap.py`: chuyển `NhaCungCapLocal` từ `e_hoi_ai/cong_ai.py`; chuyển cấu trúc payload, xác thực và đọc phản hồi của `NhaCungCapAnthropic`/`NhaCungCapOpenAI` tại `ma-nguon/lib/cong_ai.py` §7. Giữ mốc API Anthropic từ nguồn cũ, chưa kiểm Cloud thật. Thay khóa theo lượt/env bằng tham số constructor, host HTTPS cố định, không proxy/redirect/retry; bỏ Mask HTTP, cấu hình bí mật, CSDL, danh sách model và fallback/beta cũ. Thêm kiểm phong bì, cờ tắt cứng, giới hạn và lỗi SDK an toàn.
- `e_hoi_ai/cloud.py`: lớp bọc mới theo `LOAI-DU-LIEU-RIENG.md` §2.4; tái dùng hậu kiểm từ `cong_ai.py`, DTO và JSON chuẩn hóa có sẵn. Chỉ chuyển văn bản đã che ra nhà cung cấp; kết quả giữ mã mở che nội bộ.
- `e_hoi_ai/cong_ai.py`: chỉ chuyển lớp Local sang import từ mô-đun provider; không sửa đường gọi Local/chọn model/hậu kiểm.
- Chỉ thư viện chuẩn Python + SDK 2.0.0; không thêm dependency. Không sửa `ma-nguon/`, manifest hoặc bộ DEMO. Danh mục SHA-256 hiện hành ở cuối tệp.

## AI-8 — 15/11/2026

- `e_hoi_ai/ngan.py`, `e_hoi_ai/cau_hinh.py`: bản tạm viết mới theo `DE-NGHI-SDK-2.1.md` §3 và `GIAO-CODEX-DOT-2.md` §2. NGAN-0 đang làm song song; chưa có mẫu chung để chép/so băm. Chỉ thư viện chuẩn. Lead thay nguyên hai tệp khi gộp NGAN-0 và bật lại hai test so SHA-256.
- `cau_hinh.schema.json`: từ schema cấu hình máy AI-0; giữ loại dữ liệu, thêm mặc định quy tắc rỗng và trần timeout 600 giây theo trần bước hiện hành. `KHAI-SDK-2.1.json`, `ui/cau_hinh.js`: viết mới theo phiếu AI-8; DOM an toàn, không thêm thư viện trình duyệt.
- `hoi.py`, `hoi_yeu_cau.py`, `cong_ai.py`, `chon_model.py`: sửa phần nối cấu hình/model qua cổng ngăn, không chuyển thêm mã cũ. `cau_hinh_may.py` và schema cũ giữ nguyên, không thuộc đường chạy; chờ lead chuyển LUU-TRU.
- Giữ manifest SDK 2.0, không sửa wheel/hợp đồng Core, không thêm dependency chạy. Node chỉ dùng để kiểm UI với KttCore/DOM giả.

## SHA-256 hiện hành

```text
c2809e0ff68b11d6c4627c2fa58a5e2abf8b421be8002af4dc5a5479c6a381a5  cau_hinh.schema.json
6df64e3190f45aec4e5a6951e08bcb8f220c34c96e6f0bbce82f9fa5cb7cb71a  CHANGELOG.md
e42b1dee5af2da90583ee94eeac4df0404935de27da7b14a88f79f3f3a27e69c  contract/cau_hinh_may.schema.json
5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f  contract/tra_loi_ai.schema.json
81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977  contract/van_ban_tai_lieu.schema.json
36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d  contract/yeu_cau_ai.schema.json
3464bd7a36b7019edc741ffaa4aea0da193b0ffa0229ac6d03237ee0d6f0024e  demo/mau.txt
514cf09ba8f776418f50b892a22f72c27d02d87c78acc4a196aa2350ecd3649c  e_hoi_ai/__init__.py
8a9a88a6ed158af3a5704a740afe9855c5161c5785e3f3d9bae7c292d90d2f0e  e_hoi_ai/ai_cuc_bo.py
c6ba5533b0de5d1394f8bb123432da8566940f668a7f35997f1ff1217e0cee0f  e_hoi_ai/cau_hinh.py
111ebeafcf253df6e012078d12fefd27250292d3fe03953933f01bbfd98bfd73  e_hoi_ai/cau_hinh_may.py
8a42559e00454fe0aafa2dd07bf4e9d9477454f19e1a1f599ac16aabeb5c35cf  e_hoi_ai/chay.py
7f046849dfc829ef5bce280bdd6fa2612b8324f10846bf6425c651cb3c4e2ec1  e_hoi_ai/chon_model.py
9f55354b7641ce4a6d6c48fb7b8ed2fb6b7409ac0e0797af79b70f33a3ee8074  e_hoi_ai/cloud.py
99bef752985200e2a40760a55ecd33422e844b40fb7361fd63bba070bce16ae8  e_hoi_ai/cong_ai.py
912c22d54099fd4a2ddca9e0d6971ad514bfa104c067ebb249285a6237ec1985  e_hoi_ai/dto.py
1d98cf9d4974d0357138f271ad5e6b74401ee3f966c3a479c3a730a441eb9c8f  e_hoi_ai/hoi.py
4130ccafd39b070db959a0b6b3832f740d0cc694ff1e7747ff72089c2c705962  e_hoi_ai/hoi_yeu_cau.py
ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df  e_hoi_ai/khuon_json.py
268b38f739ae2761336205d142d4ffd7a51f76c7c5e499b88cbc9acd0a471a5e  e_hoi_ai/ngan.py
00fd471634ba19b8d9a3183273a5c411685a037abf9985ef346b197f6d086164  e_hoi_ai/nha_cung_cap.py
0b7a1e80f8ec22480eced0009eb1f44a50dfbb7b4a6e91058dc34d6db4e4caf9  engine.json
f06d1630ba133d73f3994c557c5521be9061e9e739602246b04979ce33c5cec8  KHAI-SDK-2.1.json
509c2fd24d3874bde62cb98e814528f8f3688a0a90a5f2424e4166b9bfc5b03d  README.md
f25f6409128d583a2cc5cf1c8022651fff2db00f72c94783c49738234a01584a  requirements.lock
2cd65eb7647c5fa9a1d904cd6972e2e135bf6f3e81682819de110113cc011e00  ui/cau_hinh.js
```

# Nguồn mã — AI-1, AI-2 và AI-3, 14/11/2026

Quy ước SHA-256: chuẩn hóa CRLF và CR thành LF trước khi băm; đường dẫn tương đối từ thư mục gói. `NGUON.md` và `sql/kiem_ke.json` không nằm trong bảng băm LF này để tránh vòng tự tham chiếu. Kiểm kê SQL sinh sau cùng bao gồm `NGUON.md` và mọi tệp còn lại trừ chính nó; bytes/SHA tại đó tính trên byte thật. Gói giữ LF qua .gitattributes.

Gói chạy dùng thư viện chuẩn Python ≥ 3.11 và SDK `kho_tri_thuc_sdk` 2.2.0 từ wheel trong repo. Không thêm thư viện bên ngoài. Ghim đầy đủ và cài máy sạch thuộc AI-5.

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

- `e_hoi_ai/ngan.py`, `e_hoi_ai/cau_hinh.py`: lead đã chép nguyên từ `_chung/mau-ma/` NGAN-0 (PR #34). Lát nối giữ nguyên hai tệp; test so SHA-256 sau CRLF → LF, không skip. Chỉ thư viện chuẩn, không sửa `_chung/**`.
- `e_hoi_ai/ngan_engine.py`: viết mới để đọc `ngan_du_lieu` từ `KHAI-SDK-2.1.json` trong gói và cấp RAM đúng khai báo cho engine/công cụ độc lập. `chay.py`, `hoi.py`, `chon_model.py`: nối API chung, phân trang bằng thuộc tính và chuyển ngoại lệ sang lỗi SDK an toàn. Không thêm dependency.
- `cau_hinh.schema.json`: từ schema cấu hình máy AI-0; giữ loại dữ liệu, thêm mặc định quy tắc rỗng và trần timeout 600 giây theo trần bước hiện hành. `KHAI-SDK-2.1.json`, `ui/cau_hinh.js`: viết mới theo phiếu AI-8; DOM an toàn, không thêm thư viện trình duyệt.
- `hoi.py`, `hoi_yeu_cau.py`, `cong_ai.py`, `chon_model.py`: sửa phần nối cấu hình/model qua cổng ngăn, không chuyển thêm mã cũ. `cau_hinh_may.py` và schema cũ giữ nguyên, không thuộc đường chạy; chờ lead chuyển LUU-TRU.
- Giữ manifest SDK 2.0, không sửa wheel/hợp đồng Core, không thêm dependency chạy. Node chỉ dùng để kiểm UI với KttCore/DOM giả.

## AI-9 — 15/11/2026

- `e_hoi_ai/hoi_mask.py`: viết mới theo phiếu AI-9 và profile đã được lead duyệt ở sổ loại chung §6. Tái dùng `_doc_yeu_cau`, `khuon_json`, cổng ngăn/chọn model/provider trong cùng gói; không dùng mã Mask/engine khác, không thay hậu kiểm hỏi–đáp cũ.
- `e_hoi_ai/ai_cuc_bo.py`: giữ socket IP/bind nguồn, kiểm URL/model và trần cũ; thêm POST theo trạng thái gửi, hoàn tất API và budget AI-9. `nha_cung_cap.py` truyền tùy chọn budget và giữ nguyên ChuaRo; `chay.py` đăng ký năng lực. Manifest 0.5.0 thêm năng lực, giữ ba DEMO cũ tương thích AI-7.
- Năm tệp mã đúng phạm vi được giao; không sửa SDK, schema chung, mẫu ngăn/cấu hình, Core hoặc nguồn cũ; không thêm dependency. Snapshot/profile DEMO chỉ fixture ngoài gói, CoreGia giữ bytes trong RAM. Chưa kiểm model/Core thật.

## AI-10 — 15/11/2026

- `e_hoi_ai/ai_cuc_bo.py`: điều chỉnh phân loại lỗi sau khi bắt đầu POST; giữ kết nối IP, các kiểm nguồn và giới hạn hiện có. Không thêm dependency.

## AI-11 — SDK 2.2.0, 15/11/2026

- Wheel `docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl`, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`: khớp `SHA256SUMS.txt`; cài venv mới với `--no-index --no-deps`, ghim `kho_tri_thuc_sdk==2.2.0`. Không thêm dependency runtime.
- Tham chiếu migration/ngăn/cấu hình: mẫu `sdk-2.2.0/engine-demo/e_demo_ngan/`; không chép nhánh import Core trong mẫu. SQL mới chỉ CREATE TABLE trong schema riêng, đầy đủ cột hệ thống; trường api đổi json → van_ban vì SDK 2.2.0 chỉ nhận kiểu vô hướng.
- Cổng tạm và bản khai SDK 2.1 chuyển nguyên byte vào `e_hoi_ai/LUU-TRU/AI-11/` ngoài gói; test so băm mẫu chung bỏ theo phiếu. Runtime chỉ đọc cấu hình snapshot/ngăn SDK; test dùng CoreGia, dat_cau_hinh/gay_xung_dot_ngan/xem_ngan.
- Gỡ khai báo bảng cấu hình; local_ai chỉ bắt buộc khi xử lý việc để giữ CHUA_CAU_HINH, không chặn khởi động engine khi Admin chưa cấu hình.
- Phụ thuộc kiểm thử ghim riêng tại `e_hoi_ai/tests/requirements.lock`; sao offline các tệp distribution đã cài trên máy vào venv mới, không tải mạng và không đưa vào gói chạy. Pytest 9.1.1, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0, iniconfig 2.3.0, colorama 0.4.6.
- CLI SDK chưa có cửa cấp cấu hình DEMO/Local giả, không còn cổng thay thế nghiệm thu. Màn UI giữ API .cau_hinh của KttCore, khai báo nạp màn engine vẫn cần Core xác nhận. Bằng chứng giả lập không chứng nhận Core/model thật.

## SHA-256 hiện hành

```text
0298691f5437c83d749781c4bf9c08d2d5fe925192c71fbc1b442e97ae94d452  cau_hinh.schema.json
9ae2efc7910795d25ffb9cd9a4182e94fdb35ddb7ca56dc423b4f8b445f65152  CHANGELOG.md
e42b1dee5af2da90583ee94eeac4df0404935de27da7b14a88f79f3f3a27e69c  contract/cau_hinh_may.schema.json
5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f  contract/tra_loi_ai.schema.json
81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977  contract/van_ban_tai_lieu.schema.json
36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d  contract/yeu_cau_ai.schema.json
3464bd7a36b7019edc741ffaa4aea0da193b0ffa0229ac6d03237ee0d6f0024e  demo/mau.txt
514cf09ba8f776418f50b892a22f72c27d02d87c78acc4a196aa2350ecd3649c  e_hoi_ai/__init__.py
8051a15ec015acd7bfec9c34bfc35a903746ff990bb15f2f27e172b2ed580ae1  e_hoi_ai/ai_cuc_bo.py
111ebeafcf253df6e012078d12fefd27250292d3fe03953933f01bbfd98bfd73  e_hoi_ai/cau_hinh_may.py
92972cc564d5a33457dea57e40d445c3fe70ce58068380692f89adfbc0d8dda2  e_hoi_ai/chay.py
ace9854285187c6dfd6543cd297f306ef45ddd29b9168dabe917749bdd5a3f66  e_hoi_ai/chon_model.py
9f55354b7641ce4a6d6c48fb7b8ed2fb6b7409ac0e0797af79b70f33a3ee8074  e_hoi_ai/cloud.py
99bef752985200e2a40760a55ecd33422e844b40fb7361fd63bba070bce16ae8  e_hoi_ai/cong_ai.py
912c22d54099fd4a2ddca9e0d6971ad514bfa104c067ebb249285a6237ec1985  e_hoi_ai/dto.py
d92e9ba99655eca098525b4f71255f4f17e9314cbe4e2623304bd997f03c7f1c  e_hoi_ai/hoi.py
10628ba65864e06b03b5250aaba277abc5c3921d9dae4144dc270688d55cc597  e_hoi_ai/hoi_mask.py
4130ccafd39b070db959a0b6b3832f740d0cc694ff1e7747ff72089c2c705962  e_hoi_ai/hoi_yeu_cau.py
ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df  e_hoi_ai/khuon_json.py
a9b105e6da5680cbdacda179d17357d0b91a8579cdefc7f862db17565803ef14  e_hoi_ai/nha_cung_cap.py
e2e2c816ab401e0ae996aa1a79ed384e05a55365daa3a8e616d1a8d545406a60  engine.json
89a04590a772e27f698a0d5eed5c02b4775a5de12039cee97b8b545eaf65cc9c  README.md
2042fa331b34afc8df48dcfa2d46909276abd557f828865360618b07b64de5a9  requirements.lock
2a803c6521dd0a2c50b41e644d7977aaf9318617c8a85afccba214708167cdae  sql/001_tao_model_phat_hien.sql
2cd65eb7647c5fa9a1d904cd6972e2e135bf6f3e81682819de110113cc011e00  ui/cau_hinh.js
```

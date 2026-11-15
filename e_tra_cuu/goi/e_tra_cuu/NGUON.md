# Nguồn và phụ thuộc hiện hành — TC-10, 15/11/2026

TC-10 chỉ sửa DEMO/manifest, tests/công cụ kiểm và tài liệu; **0 tệp Python/JS
runtime thay đổi**. Không sửa Core, SDK, schema chung hoặc nguồn cũ. Các bảng
TC-S22 và những lát trước bên dưới là lịch sử tại thời điểm tương ứng.

- `requirements.lock` giữ nguyên: duy nhất SDK 2.2.0 wheel repo, SHA nguyên
  bytes `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`,
  đã khớp `SHA256SUMS.txt`. Runtime còn lại chỉ thư viện chuẩn Python. Không
  thêm dependency, nguồn ngoài, model, giấy phép mới hoặc tải mạng.
- Dependency test giữ đúng `tests/requirements.lock` đã có ở TC-S22; phiên này
  chép offline distribution đã cài trên máy vào venv sau khi đối chiếu từng
  version, không `--system-site-packages`, không cài thư viện mới. Venv máy
  sạch riêng chỉ SDK/pip và thư viện chuẩn, không giả có pytest/jsonschema.
- Bộ `demo/tc-10/` do công cụ `tests/tao_bo_demo_tc_10.py` tạo từ giá trị DEMO
  đặt trước; generator không import engine/model hoặc đọc đáp án runtime.
  Đáp án riêng `dap-an-DEMO.json` **chưa được nghiệp vụ duyệt**. Băm raw bytes
  của nguồn/ca/đáp án ở `bam-DEMO.json`; không đổi CRLF khi kiểm dữ liệu.
- `demo/tc-10/cong-chuan/` do `tests/dong_goi_vi_du_tc_10.py` đóng băng từ
  CoreGia + Local giả, qua handler Hỏi AI AI-12 trong repo; không sửa consumer
  hoặc ép lại phong bì sau kiểm. `bam-DEMO.json` ở đó ghim bytes thật mọi
  tệp fixture/snapshot/nguồn. Cấu hình và quyền giả được loader trong tests
  cấp ngoài payload, không thành default runtime. Giữ năm ví dụ nhận; thêm
  bảy ví dụ tệp con, đủ tám năng lực. CLI chuẩn vẫn lỗi 0/12 như biên bản.
- Hai mẫu NGAN-0 **tiếp tục nguyên trạng trong LUU-TRU/TC-S22** theo chuyển
  SDK 2.2.0; không đưa cổng tạm vào gói. CoreGia dùng ngăn SDK thật trong RAM
  và `dat_cau_hinh`; bài đo chỉ ghi metadata/bốn cặp tử mẫu/tham chiếu báo cáo
  vào `dot_kiem`. Không đặt thời hạn/xóa khi TC-Q06 chưa chốt.
- Bộ chấm độc lập kiểm giá trị, thực thể, tiền tệ, ngày, câu trích/offset,
  nguồn/phiên bản/băm và hàng chờ. 12/12 trả lời, 12/12 trích dẫn, 6/6 từ chối,
  20/20 phân loại là số đo **cơ chế DEMO giả**, không accuracy model thật,
  không trung bình hoặc ngưỡng kích hoạt. `accuracy_model_that=null`.
- Kiểm cuối TC-10: **1330 passed, 0 skipped**; kiểm độc lập mã **0**, kiểm kê
  **141/141** tệp khớp bytes nguyên trạng; Node/KttCore giả **30/30**. Đã kiểm
  bằng Core giả (CoreGia); không lấy số test này làm độ chính xác nghiệp vụ.
- Công cụ máy sạch `.cmd/.sh` ASCII dùng cùng Python thư viện chuẩn, venv và
  staging tạm được kiểm nằm trong workspace, dọn trong `finally`. Windows
  cài offline/import gói riêng/không bytecode đạt; CLI 0/12/mã 1. Git Bash
  chỉ kiểm cú pháp `.sh`; Linux/WSL không có, **chưa kiểm Linux**. Pytest,
  harness và Node/KttCore giả chạy riêng; chưa Core/RLS/model/trình duyệt thật.

Bảng so băm hiện hành TC-10 dưới đây **chỉ thay CRLF→LF**, không strip,
không đổi Unicode/khoảng trắng. Test kiểm cả sáu cặp; hai bản ngăn ở lưu trữ,
bốn schema ở gói. `sql/kiem_ke.json` có bytes + SHA-256 **nguyên trạng** mọi
tệp gói trừ chính kiểm kê, cập nhật sau khi tài liệu/DEMO thay đổi.

| Nguồn repo | Bản chép | SHA-256 sau CRLF→LF |
|---|---|---|
| `_chung/mau-ma/ngan.py` | `e_tra_cuu/LUU-TRU/TC-S22/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `e_tra_cuu/LUU-TRU/TC-S22/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `_chung/contract/van_ban_tai_lieu.schema.json` | `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `_chung/contract/yeu_cau_ai.schema.json` | `contract/yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `_chung/contract/tra_loi_ai.schema.json` | `contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `_chung/contract/ho_so_tra_cuu.schema.json` | `contract/ho_so_tra_cuu.schema.json` | `2364deaf44c8fe4923640f77523e5b82c91daca27d90d7c7a6c018921df28ea9` |

## Nguồn và phụ thuộc TC-S22 (lịch sử trước TC-10)

Phần này thay thông tin cổng tạm/SDK 2.0 trong lịch sử bên dưới. Gói 0.2.0
chỉ dùng thư viện chuẩn Python ≥3.11 và `kho_tri_thuc_sdk==2.2.0`.

- **SDK nội bộ:** docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl,
  SHA-256 nguyên bytes `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`,
  đã khớp SHA256SUMS.txt. Cài vào venv sạch bằng --no-index --no-deps,
  in đúng 2.2.0; không sửa wheel/SDK/tài liệu nguồn.
- **Căn cứ:** AGENTS.md cập nhật 2.2; CHUYEN-SDK-2.2 §2/§4;
  THAY-DOI-2.2.0; mẫu e_demo_ngan (phiếu/cấu hình/migration/kiểm kê);
  LOAI-DU-LIEU-RIENG §8 và TC-9. Hướng dẫn/phiếu cũ nằm trong bộ 2.2 còn
  nhiều chữ 2.0; dùng ghi chú 2.2 và mã wheel/mẫu làm đối chiếu kỹ thuật.
- **Mã mới/chuyển:** năm tệp thay ngữ nghĩa là chay.py, trang_thai.py,
  ngu_canh_ai.py, ui/trang_thai.js, sql/001_tao_dot_kiem.sql. Chỉ SDK/thư viện
  chuẩn; không nguồn ngoài, model hoặc dữ liệu thật. Kiểm cấu hình snapshot
  riêng theo schema cố định; Core vẫn kiểm schema lúc lưu. Không sửa thuật
  toán kiểm thực thể/giá trị/đơn vị hoặc sàn nhãn TC-7.
- **Ngăn:** viec.ngan thật, pháp nhân Core gắn; JSON đã kiểm trong text cho
  chi_so/bao_cao vì SDK chưa có json/tep. Không xóa hoặc đặt hạn giữ khi
  TC-Q06 chưa chốt. Cấu hình chỉ viec.cau_hinh; row_version nội bộ chưa có
  phiên bản SDK công khai để null, không bịa số. Chi tiết Cần Core ở VIEC.
- **Lưu trữ:** KHAI-SDK-2.1.json, ngan.py, cau_hinh.py và README trước chuyển
  nằm ngoài gói ở LUU-TRU/TC-S22. Đã đối chiếu 4/4 nội dung LF với f2d73fc,
  không xóa. Bốn schema chung giữ SHA LF; những tệp mã khác trong gói chỉ
  chuẩn hóa LF để kiểm kê bytes ổn định, không thay thuật toán.
- **Test:** CoreGia 2.2.0, dat_cau_hinh/gay_xung_dot_ngan/xem_ngan thật; adapter
  quyền/tệp con và Local giả chỉ trong tests. Consumer Hỏi AI 0.12.0 chỉ
  nạp trong tests, lấy phiên bản từ manifest. Không sửa engine Hỏi AI hoặc
  ép phản hồi để vượt kiểm chứng. Giữ 1249 ca nền (bỏ đúng 2 ca so băm cổng
  tạm theo yêu cầu), thêm 19 ca TC-S22: **1268 passed, 0 skipped**; UI 29/29;
  hồi quy DEMO 43/43. **Đã kiểm bằng Core giả (CoreGia)**, không Core thật/
  RLS/Linux/model thật. CLI chuẩn **0/5 CHUA_CAU_HINH, mã 1**, chưa nghiệm thu.
- **Công cụ test riêng:** tests/requirements.lock ghim pytest 9.1.1, packaging
  26.3, pluggy 1.6.0, pygments 2.21.0, iniconfig 2.3.0, colorama 0.4.6,
  jsonschema 4.26.0, attrs 26.1.0, jsonschema-specifications 2025.9.1,
  referencing 0.37.0, rpds-py 2026.6.3, typing_extensions 4.15.0. Cài offline
  từ distribution đã cài trên máy sau khi đối chiếu version; không dùng
  system-site-packages, không tải mạng và không chép chúng vào gói chạy.
  JSON Schema đầy đủ giúp CoreGia không rơi về bộ kiểm tối giản của SDK.

Bảng hiện hành dưới đây băm SHA-256 **chỉ thay CRLF→LF**, không strip, không
đổi Unicode/khoảng trắng. Không băm NGUON.md (tự tham chiếu) hoặc kiểm kê
(kiểm kê đã chứa băm NGUON). `sql/kiem_ke.json` kiểm **bytes nguyên trạng**
toàn gói, trừ chính kiểm kê; đây là kiểm kê riêng theo mẫu SDK, không dùng
chuẩn hóa lúc xác minh. Toàn gói và quy tắc checkout giữ LF.

| Tệp (từ gốc repo) | SHA-256 LF hiện hành TC-S22 |
|---|---|
| `e_tra_cuu/.gitattributes` | `26ff5c027f6bb82b6ee1637f05478ceeeb407914752632c54ace16691e059c32` |
| `e_tra_cuu/LUU-TRU/TC-S22/KHAI-SDK-2.1.json` | `81a39d0224b4c3e1514016cb126dffc8925571c2f27a549e48bdad3c242c3537` |
| `e_tra_cuu/LUU-TRU/TC-S22/README-truoc-TC-S22.md` | `7b1c6a5fd1bcb4b0839ceaa775f3f3ad6a11d9242c884ca9ffc5a9d30e9b99b5` |
| `e_tra_cuu/LUU-TRU/TC-S22/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_tra_cuu/LUU-TRU/TC-S22/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_tra_cuu/docs/VIEC.md` | `de7b84159cacca6087b8dd2eae8acf3c121a2f2dc1d924b21e2095473adefccb` |
| `e_tra_cuu/goi/e_tra_cuu/CHANGELOG.md` | `461e05265c906f493d06c6ac227dc9a3cbb15ed8d55eaf14d9657c9a8879bf6f` |
| `e_tra_cuu/goi/e_tra_cuu/README.md` | `6bfbebb45a739471ba5b4a5a2ad1473c49903b439402bd91c66d373cf4823b15` |
| `e_tra_cuu/goi/e_tra_cuu/cau_hinh.schema.json` | `d5f29134e9abc7a5641eab5ea61d4b16f8a3ab85fc639d362fbc6b7367f2f6b3` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/chay.py` | `f4309327930d2c172e943535484d498e7d924332b0f500943179164d2822d7d8` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/ngu_canh_ai.py` | `b5bbd9ee4dadd9933c6189056ac277d308d2d5384ff6dbafb7f841ea7fc84600` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/trang_thai.py` | `91b3d8017927ba322b904b0c5bee54cd1332c169574a2dc9f78ca5eecc096434` |
| `e_tra_cuu/goi/e_tra_cuu/engine.json` | `9508e0772836fdd411d00412d66fec2712de7d9472653fd198c86d767b11c801` |
| `e_tra_cuu/goi/e_tra_cuu/requirements.lock` | `8fa45c1a5222efe4d18008b137604cb5be7c68bc1d4a54c7c130dcc839fba03f` |
| `e_tra_cuu/goi/e_tra_cuu/sql/001_tao_dot_kiem.sql` | `5865916533d70048eccd18c2d09b5ebb8ec96bf68aa1e6c42c843ec9373ed82b` |
| `e_tra_cuu/goi/e_tra_cuu/ui/trang_thai.js` | `07e42802468bd9f47ef985f88245500057a0c14d6bfdeca462da774cff1b0678` |
| `e_tra_cuu/tests/chay_demo_voi_core_gia.py` | `bb8984a1ca0b5adfd52e36dfc3ffa3a6af95e25ef7a3cec20c06e2fc5462023f` |
| `e_tra_cuu/tests/ho_tro_sdk_22.py` | `6709b84f3bf5b307a19139a7afddaca49076c2f7b4259b3af410b6117672bfa2` |
| `e_tra_cuu/tests/ho_tro_tc_2.py` | `6ad57bd5b4b2670dac39ed4afc8cfeff1b15a2f092354508c47b08f279d77116` |
| `e_tra_cuu/tests/ho_tro_tc_3.py` | `4e9fc3b406bc015e5b2ec89cde94beae8f58c11d5d23ad5d4aafc27d7555112b` |
| `e_tra_cuu/tests/ho_tro_tc_4.py` | `cb1ecc64a9d3bc619094e37337a6fc72a328a3e859325bf4e0e3ac8b0bd8e319` |
| `e_tra_cuu/tests/ho_tro_tc_5.py` | `7e2b1ee55e3ea30e583093ec564c9d099e6ff51755085bb52cb4e587af72e081` |
| `e_tra_cuu/tests/ho_tro_tc_6.py` | `b4f1113d93c4ee666cda0ba0cc93bc2818960a71e3f739b402c65d204e7dfd66` |
| `e_tra_cuu/tests/requirements.lock` | `161e9367b1524b60c0e12f9a9d39d9cdc7741bf9be29623cfde89f3e495098d8` |
| `e_tra_cuu/tests/test_sdk_22.py` | `3b856d3f1a03ca0bd28368461fd4f9f0e958db80569b6eb0214869cf7ff36dd5` |
| `e_tra_cuu/tests/test_tc_0.py` | `50121f34c0bde57b2ea162761f64a97e80fc836b841c4cb11e4ee55588c4c6ec` |
| `e_tra_cuu/tests/test_tc_1.py` | `06682d23d51f467d27763824ab623861fe5f39c0263673c3e61170ecdf59602b` |
| `e_tra_cuu/tests/test_tc_2.py` | `f0b10991bad368bd53cb3ecbd9bec1e76c19099335f63263248acb783c6a04a6` |
| `e_tra_cuu/tests/test_tc_3.py` | `f724b5a5616ec5506e9d12e5706556e2443b910833232baf30b634e4e9ef4e23` |
| `e_tra_cuu/tests/test_tc_4.py` | `8de18f58d5308c4c7b294689266ffccf803683f0c7788a979abf9ca78bff47cf` |
| `e_tra_cuu/tests/test_tc_5.py` | `bccb510cad61d02a0ef866644b123656b5a5ba7f47ff5ac4addbcfe0e1640669` |
| `e_tra_cuu/tests/test_tc_7.py` | `b10b84784a6336a0334bfdb9c3d16db01b30e0c2605be842dc983089a73c77de` |
| `e_tra_cuu/tests/test_tc_9.py` | `e479044501e694b7f146b11c6f79ae919f5b12a01351b97ee80f9120e2d8fa94` |
| `e_tra_cuu/tests/ui/ho_tro.js` | `9a9f0442edccd35b0491c6167a872ff9dd4387ba10931face982aafaf0e01fc8` |
| `e_tra_cuu/tests/ui/trang_thai.test.js` | `edec35e4a91199d437b21f7488dca70be75622d6b6d2ea2880a31aec067a3c3d` |

## Lịch sử nguồn trước TC-S22

# Nguồn và phụ thuộc — TC-0, 15/11/2026

## TC-7 — Sửa sau kiểm độc lập KHÔNG ĐẠT, 15/11/2026

Căn cứ bốn lỗi lead giao lúc 15:52, phiếu TC-7, TC-7-KIEM-CHUNG và quyết
định TC-Q14 đã duyệt. Vòng sửa chỉ thay `kiem_chung.py`, `tra_loi.py`; đọc
và giữ nguyên `bang_chung.py`, `chay.py`. Chỉ dùng thư viện chuẩn/SDK và
mô-đun cùng gói, không mã/thuật toán/dependency bên ngoài hoặc mạng.

Ngữ pháp giới hạn mới dùng thực thể/nhãn gần nhất trước giá trị trong
đoạn/ô đã kiểm. Các nhãn cạnh tranh và hậu tố đơn vị là quy tắc Python tự
viết cho lát này, không là schema/registry hoặc chính sách mới của Core.
Không rõ thì không căn cứ; trạng thái cần duyệt ở tầng 2/3 chỉ Vàng với
lý do/cảnh báo, không làm nhẹ lỗi giá trị/quan hệ/nguồn. Chi tiết ranh giới
và việc quote số/tiền phải đủ ngữ cảnh ở `docs/TC-7-KIEM-CHUNG.md`.

258 ca test mới là dữ liệu DEMO tự tạo, có bytes/metadata/băm thật nạp
CoreGia, không hồ sơ hoặc provider thật. Tổng 1210 passed, 0 skipped;
harness 36/36, độc lập mã 0; CLI chuẩn 0/5 CHUA_CAU_HINH/mã 1. Đã kiểm
bằng Core giả (CoreGia), NganBoNho/Local giả; 0 Cloud/model thật. Giữ
nguyên `_chung/**`, hai mẫu NGAN-0, bốn schema, DEMO đã ghim và
requirements.lock. Không sửa Core/SDK/engine khác; PR: **chờ lead mở**.

Bảng mới nhất dưới đây tính SHA-256 **chỉ thay CRLF→LF**, giữ nguyên
Unicode/khoảng trắng; gồm cả sáu tệp sửa/thêm ngoài NGUON.md. Không tự băm
NGUON.md vì tệp chứa chính bảng băm. Bảng của các lần gộp bên dưới giữ làm
lịch sử, không thay bảng mới nhất này.

| Tệp (từ gốc repo) | SHA-256 LF sau sửa TC-7 |
|---|---|
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/kiem_chung.py` | `2dc177ae26f99bcd2180f724164c236bbfd99db183ca1d640d12c942d09dffff` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/tra_loi.py` | `9925a6ac867fd09c25a3a096baba78f125a3440a6d43c170e96d0cfc41de8752` |
| `e_tra_cuu/tests/test_kiem_chung_tc_7.py` | `bd265c9b968c3a7b6f048b8d692fb759f4be3ab3ec0a087a6ac4b3cd6215793b` |
| `e_tra_cuu/docs/TC-7-KIEM-CHUNG.md` | `33f161e2540361614deca2d670480ec3f4d3489056aaa2f5bbe520504f7a5dd3` |
| `e_tra_cuu/docs/VIEC.md` | `0bf42c434172447398cbfa741faa47668f8aea1e10065eba596b50f87d58f3c6` |
| `e_tra_cuu/goi/e_tra_cuu/CHANGELOG.md` | `9f2c630b31951c326aba02804f69bc76c5b7746b88661537bca53cb7fb62076b` |

## TC-5 — 15/11/2026

Viết mới `phan_loai.py`, `quy_tac_nhom.py` và thêm đăng ký trong `chay.py`:
đúng 3 tệp runtime, chỉ thư viện chuẩn/SDK và mô-đun cùng gói. Căn cứ phiếu
TC-5, DAC-TA §3.2–3.7, TC-1-CONTRACT và quyết định 15/11 chiều; không sửa
API/manifest/schema/mẫu NGAN-0/requirements hoặc mã Hỏi AI/Core/nguồn cũ.

Bộ quy tắc/ngưỡng/dấu hiệu/quan hệ trong `tests/ho_tro_tc_5.py` tự tạo và chỉ
DEMO. Không đặt chính sách hoặc bộ nghiệp vụ mặc định vào runtime. Runtime
mở tài nguyên Core theo ref+băm đã ghim trong cấu hình ngăn. So khớp dấu hiệu
Python có giới hạn, không tuyên bố đã đo độ chính xác/pháp nhân hoặc model.

Tests dùng CoreGia có thật, NganBoNho và adapter quyền/tệp con riêng tests;
consumer AI-2 0.5.0 dùng Local giả trong một ca kiểm nối, giữ nguyên phản hồi
không căn cứ/hàng chờ. Không engine TC import/gọi Hỏi AI. Harness thêm 11 ca
phân loại/hàng chờ, tổng 24/24. Đã kiểm bằng Core giả (CoreGia), 0 Cloud/AI
thật; chưa kiểm Linux/Core/RLS/model thật. Kết quả thật ở VIEC.md.

## TC-4 — 15/11/2026

Viết mới `chuan_bi_ai.py`, `ngu_canh_ai.py` bằng thư viện chuẩn theo TC-4,
TC-1-CONTRACT, hợp đồng loại chung và mẫu chuyển tiếp AI-2/TX-0/DC-P; sửa
`chay.py` đăng ký handler. Đúng 3 tệp mã. Không dependency hoặc nguồn bên ngoài.
Tái dùng bộ đọc/kiểm miền TC-2 và API SDK; không sửa Core/SDK/mẫu chung/nguồn cũ.
Hai mẫu NGAN-0, bốn schema và requirements.lock giữ nguyên, test băm LF.

Test/harness dùng fixture DEMO tự tạo, bytes thực nạp CoreGia và cấu hình
NganBoNho; mở rộng bốn ca chuẩn bị. Consumer `hoi_yeu_cau.py`/`khuon_json.py`
của Hỏi AI có thật chỉ được import trong tests ngoài gói; provider Local giả
không mạng, không thay consumer/runtime engine khác. Đã kiểm bằng Core giả
(CoreGia); chưa kiểm model/Cloud/Core/RLS thật hoặc Linux. Kết quả ở VIEC.md.

Gói mới theo phiếu `e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md` §1–5,
API-ENGINE-v1 và hai hướng dẫn SDK 2.0.0. Không có lõi cũ tại chỗ để chuyển;
không tạo `ma-nguon/`. Mã khung/schema/test mới viết trong lát TC-0.

| Thành phần | Nguồn nội bộ repo | Phiên bản / SHA-256 |
|---|---|---|
| SDK | `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | 2.0.0 · `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `e_tra_cuu/ngan.py` | `_chung/mau-ma/ngan.py`, NGAN-0, PR #34 theo lead | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_tra_cuu/cau_hinh.py` | `_chung/mau-ma/cau_hinh.py`, NGAN-0, PR #34 theo lead | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

Hai mẫu chép nguyên bytes bằng Copy-Item, không sửa hoặc import `_chung` ở runtime.
Test so SHA-256 **chỉ đổi CRLF thành LF**, không strip/biên tập.
Băm SDK tính trên wheel nguyên bytes, đã khớp `SHA256SUMS.txt`.

Runtime chỉ thư viện chuẩn Python >=3.11 và SDK 2.0.0; ghim SDK trong
`requirements.lock`. Không thêm thư viện ngoài. Pytest 9.1.1 là công cụ test có
sẵn qua venv `--system-site-packages`, không đóng gói và không phải dependency
runtime. Kiểm thực tế trên Windows/Python 3.13.14; chưa chạy Linux.

SDK và hai mẫu lấy từ bộ nguồn nội bộ được giao. Metadata wheel không khai trường
License; không tự suy diễn giấy phép nguồn ngoài. Lát này không tải/nhúng mã,
mô hình hoặc dữ liệu bên ngoài. Không chép schema của loại chưa duyệt TC-Q13.
Chỉ dữ liệu DEMO trong test, không tài liệu thật; không mạng/Cloud khi kiểm.

## TC-1 — 15/11/2026

TC-Q13 đã duyệt tại `_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` câu 5.
Schema mới theo phần TC-P cuối `_chung/docs/LOAI-DU-LIEU-RIENG.md` và phiếu
Tra cứu §2; chi tiết thực thi ở `e_tra_cuu/docs/TC-1-CONTRACT.md`.
Không sửa tài liệu loại chung. Câu “chưa duyệt” phía trên mô tả lịch sử TC-0.

| Bản chép trong `contract/` | Nguồn `_chung/contract/` | SHA-256 sau chỉ đổi CRLF→LF |
|---|---|---|
| `ho_so_tra_cuu.schema.json` | Cùng tên, mới viết TC-1 | `2364deaf44c8fe4923640f77523e5b82c91daca27d90d7c7a6c018921df28ea9` |
| `van_ban_tai_lieu.schema.json` | Cùng tên, giữ nguyên | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `yeu_cau_ai.schema.json` | Cùng tên, giữ nguyên | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `tra_loi_ai.schema.json` | Cùng tên, giữ nguyên | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |

Chép nguyên bytes; pytest kiểm cả bytes và SHA-256 LF. Hai mẫu NGAN-0 giữ nguyên.
Chỉ 5 tệp schema nguồn/bản chép trong TC-1, không thay manifest/chay.py hoặc
schema đã khóa. Không thêm dependency, không dùng bộ đọc cấu hình làm validator
chung; bộ đánh giá schema mới và adapter CoreGia chỉ ở tests. Mọi fixture chỉ
DEMO với bytes được nạp vào CoreGia, metadata/băm tính thật, không tải mạng/AI.

## TC-2 — 15/11/2026

Runtime mới/sửa đúng `ho_so.py`, `kiem_dau_vao.py`, `chay.py`; không thêm
dependency. Giữ nguyên bytes hai mẫu NGAN-0 và cả bốn schema đã chép ở TC-1;
test SHA-256 sau CRLF→LF tiếp tục áp dụng. Không sửa nguồn/schema chung/Core/SDK.

Tám tệp trong `demo/` là dữ liệu giả mới tạo cho TC-2: nguồn văn bản Công ty
DEMO Ánh Dương, phong bì OCR DEMO, danh mục DEMO và năm JSON yêu cầu. Không phải
đáp án hoặc số đo chất lượng đã được nghiệp vụ nghiệm thu. Tên/metadata/băm
của tệp con nằm trong JSON yêu cầu, băm bytes chính xác từng yêu cầu ở
`engine.json.chay_thu_demo`. Không đổi Unicode hoặc canonical hóa để chữa băm.

Harness test nạp ba tệp con theo thứ tự gốc → OCR → danh mục bằng API
`CoreGia.them_tep`; vì vậy ba ID `tep-1/tep-2/tep-3` trong DEMO thực sự trỏ
bytes đã tải vào kho RAM đó. Có kiểm lại bytes/metadata/băm trước chạy; runtime
không hardcode các ID hoặc nạp dữ liệu này. SDK CLI gốc thiếu ngăn/cấu hình/
quyền tệp con; không diễn giải các ID như nguồn có sẵn ở Core thật.

Adapter `CoreGiaTepCon`/`CuaNguonGia` và dữ liệu cấu hình chỉ trong tests ngoài
gói; không đưa vào runtime. Đã kiểm bằng Core giả (CoreGia), mạng ngoài/Cloud=0;
chưa chứng nhận RLS thật hoặc Linux. Quyền/ghép nguồn/vòng đời/ACK chờ C-TC-02/03,
ngăn/cấu hình CLI chờ C-TC-01, log/lỗi trần/lease SDK chờ C-TC-05.

## TC-3 — 15/11/2026

`cat_doan.py`, `vi_tri.py` viết mới bằng thư viện chuẩn Python, theo phiếu
TC-3, `TC-1-CONTRACT.md` §3–5 và DAC-TA §3.4/8/9; không lấy thuật toán/mã hoặc
dependency bên ngoài. Sửa `chay.py` đăng ký handler cắt và `kiem_dau_vao.py`
đóng ba nợ TC-2 do lead giao. Tổng **4 tệp mã**, dưới trần khoảng 5 tệp/lát.
Không có nguồn cũ tại chỗ, không sửa Core/SDK/engine khác hoặc contract chung.

Các map bảng/ô và `hang_tieu_de` là quy ước snapshot trong phần mở sẵn có của
`van_ban_tai_lieu` v1; không sửa schema. Phép chiếu TAB + LF/CRLF được kiểm đúng
chuỗi nguồn trước khi tạo offset, không đoán hộp/ô/tiêu đề. Kiểu nguồn khác
chưa có map cần adapter Core cấp, ghi C-TC-02/03 và L-TC-01 trong VIEC.

Giữ nguyên hai mẫu NGAN-0 và bốn schema, tiếp tục so băm CRLF→LF với các giá trị
ở bảng trên. SDK 2.0.0 từ wheel offline, băm vẫn khớp SHA256SUMS.txt. Không
thêm dependency; `requirements.lock` giữ nguyên. Phiên bản 0.1.0 còn nội bộ.

Test/harness mới dùng dữ liệu tự tạo DEMO: Điều/Khoản xuyên trang/trang rỗng,
bảng ô gộp/ô rỗng và tiêu đề lặp, NFC/NFD/emoji, 1.000.000 VND, 2026-10-30.
Không dùng tài liệu thật hoặc model. Bản adapter quyền Core chỉ trong tests;
seam ghim phong bì/metadata và quyền xuyên bước chưa là API Core thật.

Kiểm hồi quy đầu trên checkout Windows phát hiện Git auto-CRLF làm lệch bytes
DEMO nguồn so với SHA đã ghim. `e_tra_cuu/.gitattributes` cố định LF cho demo/*;
bytes LF hiện tại khớp nguyên bytes HEAD và băm đã đăng ký, không sửa băm hay
canonical hóa trong runtime để bỏ qua sai nguồn. Đã kiểm bằng Core giả (CoreGia),
AI/Cloud=0; chưa kiểm Linux/RLS/Core thật/UI/chất lượng model.

## TC-6 và việc gộp TC-5 — 15/11/2026

TC-6 viết mới `cau_hoi.py`, `xep_hang.py`, đăng ký trong `chay.py`, theo phiếu
TC-6 và TC-1-CONTRACT. Chỉ thư viện chuẩn/SDK, không nguồn hoặc dependency mới.
Các seam phân giải câu hỏi/allowlist/binding là quy ước adapter CoreGia, cần
Core/lead review; không là API SDK mới hoặc số đo chất lượng model thật.

Việc gộp giữ nguyên bốn mô-đun nghiệp vụ và hai bộ test TC-5/TC-6; chỉ hợp nhất
đăng ký/handler, danh sách stub, harness và tài liệu. Hai biên bản cũ và hai
mục CHANGELOG giữ nguyên số liệu lịch sử (17/17 TC-6, 24/24 TC-5); kết quả
sau gộp là 814 passed, 0 skipped, harness 28/28 và độc lập mã 0. Đã kiểm bằng
Core giả (CoreGia), 0 Cloud/model/provider thật; CLI chuẩn vẫn 0/5 lỗi
CHUA_CAU_HINH/mã 1, C-TC-01 đã ghi trong VIEC; chưa kiểm Core/RLS/Linux thật.

Bảng kiểm sau gộp dưới đây tính SHA-256 **chỉ thay CRLF→LF**, giữ nguyên
Unicode/khoảng trắng. Gồm sáu tệp giải xung đột và bốn mô-đun nghiệp vụ được
giữ lại; không tự băm NGUON.md vì tệp này chứa chính bảng băm. Hai mẫu NGAN-0,
bốn schema, DEMO và dependency giữ nguyên các băm/nguồn đã ghi phía trên.

| Tệp (từ gốc repo) | SHA-256 LF sau gộp |
|---|---|
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/chay.py` | `13e3033d7e8d3232c36d30229bb28f7eb958ee6b880a5773c59aa9f5bf03d411` |
| `e_tra_cuu/tests/chay_demo_voi_core_gia.py` | `d16feb580d37ac7fbf8ed72280588c905e2790e62f322c2ceeb0c84fd7676012` |
| `e_tra_cuu/tests/test_tc_2.py` | `93a5723fc29927e7d3684d0913693defe37b701f40c41f41ace6906cbab5a084` |
| `e_tra_cuu/goi/e_tra_cuu/README.md` | `69e301a02aeed82aa1918d429682dc45846865333043794175a4fca6298b64ec` |
| `e_tra_cuu/goi/e_tra_cuu/CHANGELOG.md` | `9c8d962bf1a5525c9670f7063f75d80a325ad6efc5aacf1ce1935101ba97c1de` |
| `e_tra_cuu/docs/VIEC.md` | `af235c956873d24782bb68ddccea6e66c4b3d95737bdb3265d41593982c84cda` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/phan_loai.py` | `9e36a2a06d3b97613ec7d07237c6d9abb76039526adcd16758579e502d561632` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/quy_tac_nhom.py` | `aa787e8fef6cca744c777a3bf820350f5947a40cadfc3b15db2f9cc9a271c793` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/cau_hoi.py` | `c58c2aa90d1784933960d39d5797a7e575642475d45e12f3372ee8784e08c50f` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/xep_hang.py` | `6d062ebd1bbd67cd554d7d7f1404caa6ddc05d1860692446d1f20358e9018c02` |

## TC-9 — 15/11/2026

Viết mới `ui/cau_hinh.js`, `ui/trang_thai.js`, `trang_thai.py`, bổ sung seam
thuần trong `chay.py` theo phiếu TC-9; đúng 4 tệp mã, không nguồn/dependency
bên ngoài. Hai mẫu NGAN-0 và bốn schema tiếp tục giữ nguyên, test SHA-256 LF.
Các băm TC-6 ở bảng trên là lịch sử tại thời điểm gộp, không là băm hiện tại
của chay/README/CHANGELOG/VIEC đã cập nhật qua TC-7…9.

UI dùng ES module/DOM/Intl có sẵn, chỉ KttCore của chính engine. Node
24.18.0 chạy test không mạng/không npm. Tên quyền xem theo pháp nhân và hình
dạng phản hồi KttCore là đề nghị chờ Core đối chiếu; chưa phải SDK thật.
Fixture báo cáo/cấu hình/bài đo đều DEMO trong RAM, CoreGia tạo tệp+băm thật;
không dùng nguyên văn/câu hỏi trong bản ghi dot_kiem. Không sửa Core/SDK,
nguồn cũ hoặc requirements.lock. Chưa kiểm trình duyệt thật/Linux/lưu bền.

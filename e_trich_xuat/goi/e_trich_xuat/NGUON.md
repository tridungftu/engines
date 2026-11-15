# Nguồn gói TX-1 / TX-2 / TX-3 / TX-3b

## TX-6 — 15/11/2026, công cụ ngoài runtime

Quyền nguồn: mã Trích xuất/Hỏi AI/mẫu ngăn và dữ liệu DEMO là nguồn nội
bộ đã được giao trong repo để chuyển/tái dùng cho dự án. Không có giấy
phép mở riêng cho các nguồn này trong repo; không tự gắn MIT hoặc quyền
công bố lại. SDK dùng đúng wheel đã cấp và băm phát hành. Không thêm mã
bên thứ ba, thư viện runtime hoặc tài nguyên mạng trong TX-6.

| Nguồn → nơi dùng | Cách giữ/chuyển và quyền |
|---|---|
| `ma-nguon/do_chinh_xac.py`, `ma-nguon/vendor/review/kiem_tra.py` → `../../cong-cu/ho_tro_do.py` | Giữ nguyên thuật toán `compare`, `norm`, `_ngay` và mẫu số `da_do`; bỏ path/nội dung hồ sơ khỏi báo cáo. Đối chiếu AST với nguồn, không sửa nguồn; chỉ nguồn nội bộ |
| `../../docs/TX-0-THIET-KE.md`, `ma-nguon/vendor/review/danh_muc.py` → `corpus_t3` | Đúng 37 mã và toàn văn/khối tải DEMO-1/20/60 Phụ lục A; băm prompt/khuôn thực TX-2 tách băm tham khảo lịch sử; không nhập/chạy pipeline cũ |
| `e_hoi_ai/cong-cu/thu_local_ai_that.py`, gói AI-8 hiện hành → công cụ T3/N1 | Tái dùng mẫu chạy khô và seam discovery/transport/khung AI-2, không chép provider vào runtime Trích xuất, không sửa Hỏi AI; cấu hình máy thật chỉ qua dòng lệnh |
| SDK `CoreGia`/`MayChuGia`, mẫu ngăn NGAN-0 và test đã có → test TX-6 | Core điều phối; cấu hình DEMO nạp vào ngăn ngoài runtime. HTTP chỉ loopback, stdin, hủy/mất xác nhận giả; không chứng nhận quyền/TTL/ACK Core thật |
| Tự viết trong TX-6 → ba Python, hai `.cmd`, scripts/test/tài liệu | Chỉ stdlib + SDK; 5 tệp mã ngoài tests/tài liệu; không đổi runtime/manifest/schema chung |

`requirements.lock` giữ nguyên `kho_tri_thuc_sdk==2.0.0`; thư viện chuẩn
theo Python ≥3.11. `tests/requirements.lock` ghim pytest 9.1.1/jsonschema
4.26.0 cho bộ kiểm; venv runtime mới không cần hai thư viện này. Node
test dùng thư viện chuẩn. **đã kiểm bằng Core giả (CoreGia)**; T3/N1 máy
thật chưa đo/chưa kiểm. Nguồn E6 được kiểm băm bytes riêng, không lấy quy
ước LF của bảng nguồn mã dưới đây để chuẩn hóa E6 cho đạt.

> TX-3b, 15/11/2026: chi tiết TX-3 đã được Anh duyệt chiều 15/11;
> bản 0.4.0 đã đăng ký schema/năng lực/DEMO. Các nhãn “đề xuất / chưa
> đăng ký” của biên bản TX-3 bên dưới là lịch sử trước duyệt.

Nguồn nội bộ đã có trong repo; không thêm mã/thư viện bên ngoài.

| Nguồn tương đối từ gốc repo | Đích trong gói | Chuyển đổi |
|---|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `e_trich_xuat/docx.py` | Giữ đếm sửa đổi theo namespace; thay adapter đường dẫn bằng bytes SDK |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `e_trich_xuat/docx.py` | Chuyển có sửa Accept All, Numbering; giữ ô rỗng/gộp, thêm giới hạn ZIP/XML; bỏ đọc/ghi tệp và chuyển định dạng |
| `_chung/contract/van_ban_tai_lieu.schema.json` | `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte; test so SHA |
| `_chung/mau-ma/ngan.py`, `_chung/mau-ma/cau_hinh.py` (NGAN-0, PR #34) | `e_trich_xuat/ngan.py`, `e_trich_xuat/cau_hinh.py` | Lead đã chép bản chung; giữ nguyên, so SHA-256 sau chuẩn hóa CRLF→LF |
| SDK 2.0.0, engine DEMO và hợp đồng API v1 trong repo | `engine.json`, `e_trich_xuat/chay.py` | Khung khai năng lực thực; bọc hẹp lỗi SDK trước handler |
| `e_trich_xuat/ma-nguon/tich_hop.py` | `e_trich_xuat/tich_hop.py` | Chuyển có sửa kiểm bộ/build_prompt; bỏ điều phối, adapter AI, cắt/top-k; tạo hồ sơ qua SDK |
| `e_trich_xuat/ma-nguon/tham_so.py` | `e_trich_xuat/tham_so.py` | Chuyển có sửa kiểm hash/chọn bộ, dùng bộ kiểm dòng E1 của SDK; không tạo bản E1 mới, không mặc định XD |
| `e_trich_xuat/ma-nguon/vendor/review/cau_truc.py` | `e_trich_xuat/cau_truc.py` | Chuyển có sửa build_structure/vi_tri; chỉ mục Unicode nguyên toàn văn, bỏ save/strip/top-k |
| `_chung/contract/yeu_cau_ai.schema.json` | `contract/yeu_cau_ai.schema.json` | Chép nguyên byte, test SHA; không đổi loại v1 thành batch |
| Viết mới cho TX-1 | `ui/cau_hinh.js`, schema cấu hình và khai SDK 2.1 | Một ô cấu hình qua cổng Core, chưa nối Core thật |
| `e_trich_xuat/tests/mau_docx.py` (ngoài gói) | `demo/DEMO-*.docx` | Fixture giả xác định; nhãn DEMO trong nội dung |

TX-2 thêm khai năng lực/DEMO trong phiếu, kiểm cấu hình/giới hạn và hook log;
không thêm dependency runtime, không dùng adapter ai_chung.py.
Không đổi/xóa nguồn cũ hoặc schema chung. Các đường điều phối/adapter cũ
không được đưa vào gói; đề xuất lưu trữ vẫn ghi trong `docs/VIEC.md`.

SHA-256 wheel SDK đã kiểm:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Test dùng pytest 9.1.1 và jsonschema 4.26.0 có sẵn trên máy qua đường import
của tiến trình kiểm, ghim tại `../../tests/requirements.lock`; jsonschema là
dependency đã khai của SDK 2.0.0, dùng kiểm schema DOCX có `$defs`/`$ref`/union.
Không cài thêm hoặc tải mạng, không thêm dependency runtime engine.
Test UI chỉ dùng Node chuẩn.

**Quy ước SHA-256:** tất cả tệp văn bản trong các bảng bên dưới được đổi
CRLF (`\r\n`) thành LF (`\n`) trên bytes UTF-8 trước khi băm; không đổi BOM,
khoảng trắng hoặc nội dung khác. Tệp nhị phân DOCX/wheel băm nguyên bytes.
Hai tệp mẫu ngăn trong gói không được sửa, kể cả để đổi xuống dòng.

## SHA-256 nguồn đã chuyển

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `84b5662856ecf2742360077012377f913698a917e1fd4a4a08f87568e1af6a5b` |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f` |
| `e_trich_xuat/ma-nguon/tich_hop.py` | `ec2fc1fd7433f5842e7b983d66a06c8f493f8751810c110915456c403ff57d5b` |
| `e_trich_xuat/ma-nguon/tham_so.py` | `d45db071209b50d360cd6140b11b0bfd7f52d33584c93597429f1b8910579d59` |
| `e_trich_xuat/ma-nguon/vendor/review/cau_truc.py` | `2817a46ec2fc967d1e64eae1dd68e35047e687a7b654a9c8ce03f106b9aad5c6` |

## SHA-256 tệp trong gói (không gồm NGUON.md)

| Tệp | SHA-256 |
|---|---|
| `cau_hinh.schema.json` | `291d3ff81ffe0c12e31b1dd6e982b6339c3fa0992f6ec4797f33727ff06f1567` |
| `CHANGELOG.md` | `e2a4a37f8ef9df060aba8d325b32354b36bab0aa5d06ca28dd34edb6731159ee` |
| `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `contract/yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `1832b57855397f8618590ccc8100c4232ea515da65405a4d35109dcd885b37d2` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/cau_truc.py` | `1a44e428a8dc2e1e5a5d52524baaafa12e6dddc6e1dc026b17cc519470760459` |
| `e_trich_xuat/chay.py` | `47513844092347d256eb342e7759fc863048ec679b84c4f8aa1724d5f61f1d3d` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_trich_xuat/tham_so.py` | `2106cece109ca86272e94717abd6b6e6e0489e95c0ac49f33c0f71fa617cbc12` |
| `e_trich_xuat/tich_hop.py` | `26fa7299a3a2d992bfdeb44536031a367b06f1ad20b6575818332edbb2463d1a` |
| `engine.json` | `ee4f0cb36f18c775ba2dd1584adff0fa636f63bef68b142d42ef6d200e2bddda` |
| `KHAI-SDK-2.1.json` | `9dc34efb03293ab8f314d4b7610c60bff5dc231835cb733c4add06bbc4741619` |
| `README.md` | `98c6a5ffa4bff413cb0aa1c20fa3ee1f202d4f1b58e486f736b5cde530667766` |
| `requirements.lock` | `f1c814f4fcea2aef4d55342db50054ea97943552ba0f5bdf72a19c892410b3b5` |
| `ui/cau_hinh.js` | `c605cb20b135c646583da0628b8af801b768e8bde600e4eb29d048888f8615ba` |

## SHA-256 tích hợp và kiểm ngoài gói

| Tệp | SHA-256 |
|---|---|
| `_chung/mau-ma/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/tests/test_goi.py` | `69e88d09e2c23924bec5fc9ca45893d4715f71687003b72eae926e0287759b5e` |
| `e_trich_xuat/tests/test_ngan_cau_hinh.py` | `914ee271e2a811056be100236bbb0f45388b7d1d44c5803516c8d46969a520d4` |
| `e_trich_xuat/tests/test_docx.py` | `839961cb7239c412418b2986261948a7bbe5cb004a40cb2fa5fd18bab8eb0cd2` |
| `e_trich_xuat/tests/test_chuan_bi.py` | `e8911fa87335ca08923cf519a21ed422e13c1812f3c04c80d5420f179eac16d6` |
| `e_trich_xuat/tests/test_cong_sdk.py` | `18cbc6fa2bbb43a3c317b89a3d455a7df487347e5146fb44cf5630a86909fdda` |
| `e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | `01158473b3a466637814088c58b08b10c02ea22531b45c4239831cce2a2c5bc2` |
| `e_trich_xuat/tests/requirements.lock` | `736ea02ef855c421afcaa53a43f2005d5c59212f62cf0eea241de4090f40eaf3` |
| `e_trich_xuat/docs/TX-1-PHAM-VI.md` | `ddf797115058e114d79cddb17547740416c27003c28b5b7396c7c15149e97850` |
| `e_trich_xuat/docs/VIEC.md` | `185187b8a576ab2b01db25711a084162031f92aa06111c63c4185a880ae5af95` |


## Nguồn và phạm vi TX-3 — chưa đăng ký runtime

- `ma-nguon/vendor/review/kiem_tra.py` → `e_trich_xuat/kiem_tra.py`:
  giữ các hàm chuẩn hóa/số/dấu kiểm legacy để E6 đối chiếu; bỏ đọc đáp án/
  glob/I/O. Thêm kiểm nghiêm nguyên văn/offset độc lập, không dùng nhánh
  legacy fallback để xác nhận; giữ tọa độ OCR theo offset thật.
- `ma-nguon/vendor/review/logic.py` → `e_trich_xuat/logic.py`:
  giữ L1–L5, giới hạn mã XD ở loại XD; loại khác L1/L4 và ba quy tắc E1
  đã ghim. Không eval, không truy xuất bộ hiện hành hoặc sửa giá trị.
- `ma-nguon/vendor/review/xlsx_mini.py` → `e_trich_xuat/xlsx_mini.py`:
  writer OOXML chuẩn Python sang BytesIO, bỏ cắt 32.000, kiểm UTF-16 trước
  escape; bảo toàn ký tự bằng escape OOXML, text không thành công thức.
  Không mang reader/tự tìm tệp vào lõi mới.
- Viết mới `hau_kiem.py`/`xuat.py`: đọc hồ sơ qua SDK, kiểm từng ô và
  phong bì, xuất đủ hai tệp trong RAM. Không chuyển `xuat.py` cũ với
  `DANH_MUC_HD`, suy tiền/lưu dài hạn hoặc openpyxl vào gói.
- `_chung/contract/tra_loi_ai.schema.json` chép nguyên bytes vào gói,
  test SHA. Chưa tạo/chép schema bảng, chưa đổi bốn loại chung.
- Fixture/phần đăng ký đề xuất chỉ ở `tests/mau_tx3.py` bên ngoài gói,
  cổng `tests/chay_demo_voi_ngan_gia.py` có hai DEMO TX-3 chưa đăng ký.
  Manifest/runtime 0.3.0 không đổi. Không thêm dependency.

**đã kiểm bằng Core giả (CoreGia)**, NganBoNho + AI giả, 0 Cloud.
Chi tiết review tại `../../docs/TX-3-REVIEW.md`; bằng chứng/lệnh/giờ tại
`../../docs/VIEC.md`. Không nhận E6/N1/Linux/Core thật.

## Sửa theo kiểm độc lập TX-3 — 15/11/2026

- Sửa `kiem_tra.py` để khớp trọn token/cụm và strip đối xứng; số có dấu
  phân cách/khoảng trắng phân nhóm không bị tách. Dấu tạm E6 đổi tên
  `dau_kiem_tam_e6`, không đổi cách chấm cũ.
- `hau_kiem.py` chỉ nhận tiền int/chuỗi thập phân chính xác, thêm đơn vị
  offset Unicode và cờ chưa chuyển kiểu; `xuat.py` giữ các trường này khi
  xuất. Phản hồi AI chỉ kiểm toán, có thể lộ nội dung; module không hiển thị mặc định.
- Nợ TX-2: `cau_truc.py` kiểm trần phần tử/byte trước sao chép;
  `tich_hop.py` chặn hồ sơ quá 20 MiB và bỏ bản chép toàn văn trong request.
  Hậu kiểm vẫn đọc hồ sơ TX-2 cũ và kiểm băm request đầy đủ.
- Regression test token, tiền round trip, byte Unicode/trần RAM, hồ sơ cũ/gọn
  và prompt injection; không thêm dependency hoặc sửa mẫu NGAN-0/Core/SDK.
- `TX-3-REVIEW.md` giữ bổ sung **ĐỀ XUẤT TX-0, chờ Anh**, chưa sửa `_chung/**`
  hoặc đăng ký năng lực/schema/runtime. Kết quả và thời gian ở `VIEC.md`.

## SHA-256 bổ sung TX-3

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/vendor/review/kiem_tra.py` | `47ee35567cb7b864a6b3d6825bc90f93a7a26c0c6872a326e99ead9160467f12` |
| `e_trich_xuat/ma-nguon/vendor/review/logic.py` | `f7cfcf37ff2293d8f8ea994f1ae0a69f57d1d1d9a844f0620f018a3d285a4452` |
| `e_trich_xuat/ma-nguon/vendor/review/xlsx_mini.py` | `a29ed16811637daa756fcb2640557ec817734d3d2ee617c30deca51d3799857b` |
| `_chung/contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `e_trich_xuat/hau_kiem.py` | `4badcb8c769bf84bbda8a334f77b8faf1ee0c508f1de36f1ff49574776eb6be9` |
| `e_trich_xuat/kiem_tra.py` | `17a988f374d591b7d1b9b6ef31c8b86faf6352c3a53025c6701ee4d4c767fcf9` |
| `e_trich_xuat/logic.py` | `66f6befde686bc3d86cb234889a61af0655d4c92b7b1be09e86d177fcb152950` |
| `e_trich_xuat/xlsx_mini.py` | `b139d90d6adb186d658ad00f7970f7647f351178a035459b0913cf4298edc5e3` |
| `e_trich_xuat/xuat.py` | `a4cc1ff456b1235ff01ecd010f588eb89e04ce2dd6eefa7b6fc856e8dc0f431c` |
| `e_trich_xuat/tests/mau_tx3.py` | `6e3f5069692bfe0e2601bfe86219b5ca09b6b69dd73df6db119708356215124f` |
| `e_trich_xuat/tests/test_hau_kiem.py` | `da124c55b4727d7a938ee70509a26e180c404fc0e7da965dacd8dc0e0b7c8cdb` |
| `e_trich_xuat/tests/test_xuat.py` | `880c050fac738727260507ba2ac7055d6d72eefec6bd88efc96284bb0e6d4077` |
| `e_trich_xuat/docs/TX-3-REVIEW.md` | `a1e35601bdd9e7dfe7aa2a6232430d808929666ce7b4bd25b3156cb8a5832b38` |


## Nguồn TX-3b — 15/11/2026, bản 0.4.0

- `_chung/docs/LOAI-DU-LIEU-RIENG.md` §4 + bổ sung tại
  `e_trich_xuat/docs/TX-3-REVIEW.md`, đã duyệt bởi
  `_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` câu 3:
  tạo `_chung/contract/bang_trich_xuat.schema.json`, chép nguyên nội dung
  vào `contract/`; test so SHA-256 sau CRLF→LF. Không sửa văn bản loại
  chung hoặc bốn schema chung đã có.
- `tests/mau_tx3.py` → hai `chay_thu_demo` trong manifest và
  `demo/DEMO-ho-so-hau-kiem.json`: lấy từ chuẩn bị/hậu kiểm thật bằng
  CoreGia, chỉ dữ liệu giả, metadata và bytes/băm/kích thước thực.
  Tệp hồ sơ JSON canonical là tài nguyên DEMO được đóng gói, không phải
  dữ liệu engine tự ghi/lưu bền hoặc cấu hình thật.
- Viết helper `e_trich_xuat/demo.py` chỉ phục vụ cổng kiểm: API công khai
  `CoreGia.them_tep`, kiểm băm/kích thước, thay ID tệp và băm toàn request
  AI trong bản chép mẫu. Không sửa SDK hay handlers, không nạp từ runtime.
- `chay.py` nối lõi `hau_kiem.py`/`xuat.py` đã có; không đổi nghiệp vụ hoặc
  sao chép đăng ký giả từ test. Bỏ phiếu RAM đề xuất trong `tests/mau_tx3.py`.
- Không thêm dependency. **đã kiểm bằng Core giả (CoreGia)**:
  408 passed, 0 skipped; cổng có ngăn/hồ sơ 5/5; độc lập đạt; CLI chuẩn
  3/5, exit 1 (C-TX-04 `CHUA_CAU_HINH`, C-TX-06 hậu kiểm `DANG_CHAY`
  do thiếu hồ sơ tham chiếu). Linux/Core thật/E6/N1 chưa chứng nhận.

### SHA-256 bổ sung TX-3b (UTF-8, CRLF→LF)

| Tệp | SHA-256 |
|---|---|
| `_chung/contract/bang_trich_xuat.schema.json` | `f36314d7e3958281966a5c4c24ca3cd9a01df507d7a07d0b96a0aebafe4ea82f` |
| `contract/bang_trich_xuat.schema.json` | `f36314d7e3958281966a5c4c24ca3cd9a01df507d7a07d0b96a0aebafe4ea82f` |
| `demo/DEMO-ho-so-hau-kiem.json` | `4879e0e1d270631a50bcbc27707511f464bbca369816ab35f4e0fec82ab4e02b` |
| `e_trich_xuat/demo.py` | `117ea143d6d286516ee39408b11229279da522bb8cbfbe030750eaf875d155e0` |
| `e_trich_xuat/tests/test_dang_ky_tx3b.py` | `9bc74afd51c249f354e2bacb56bb534d5076632e26e7a9541cd79d5553410555` |


## SHA-256 TX-6 (văn bản CRLF→LF; wheel nguyên bytes)

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/do_chinh_xac.py` | `bb37f8c8313706f7ed9c65bfc2afffe4f7946b4986f028f93da5230ce442c3e3` |
| `e_trich_xuat/docs/TX-0-THIET-KE.md` | `95826b1cfa0cd0fa17dcef4245b7f444f642d0ddcdaf301ddec7c34690d921e9` |
| `e_hoi_ai/cong-cu/thu_local_ai_that.py` | `41bf0d57c1dc77d36b8a31e4f845b0464686fc2fafe7fc6a58d798374e47439e` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/ai_cuc_bo.py` | `3af0752bcc3ac5e641cb669ca02d7721186131257ea1c51031a70d0f53239652` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/chon_model.py` | `cd9775d479966873f9529e419c0c296c2bec02ae57a1b90773572d3131ea3481` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/cong_ai.py` | `99bef752985200e2a40760a55ecd33422e844b40fb7361fd63bba070bce16ae8` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/hoi_yeu_cau.py` | `4130ccafd39b070db959a0b6b3832f740d0cc694ff1e7747ff72089c2c705962` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/khuon_json.py` | `ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df` |
| `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `e_trich_xuat/cong-cu/CHAY-N1-MOT-LAN.cmd` | `5f883322e450299371d07a84ce5486a2c249aa0a16175bb2995232993ace4353` |
| `e_trich_xuat/cong-cu/DO-SUC-CHUA-MODEL.cmd` | `75dff0400d02dea4a8267bf457d3e53b19f48fae2be3ed37f27c624a86ca3703` |
| `e_trich_xuat/cong-cu/do_n1_mot_lan.py` | `b8fee85ed2295ae057dd23137c36df217a9603b5f7fdf9de91722090f958c5b3` |
| `e_trich_xuat/cong-cu/do_suc_chua_model.py` | `22e51a11d7c855cf178ad353d835e84f13ca9d0f63725ba9fe32af2a58ff1987` |
| `e_trich_xuat/cong-cu/ho_tro_do.py` | `a8d3501d4a95423ffcd114ac6314e433e18e9e1436977ab01ff449dcabde097d` |
| `e_trich_xuat/cong-cu/MAU-NEN-N1.json` | `910d19445e7b139eef0428e23dd40bf3a11eae7140dd8131dc8101c99159246d` |
| `e_trich_xuat/cong-cu/README.md` | `5e0a0d1fe8f4d88e23f4db2170f473c896e0d204a82a95d390609b61da8d0539` |
| `e_trich_xuat/tests/kiem_may_sach.cmd` | `78f53306d4d879ad9a5f18d70efa9f078db11a5845af3f476ae7f2bc5298efc7` |
| `e_trich_xuat/tests/kiem_may_sach.sh` | `7dfd06a38cfd955792734a0996dba76e6174a9f072488ec18868aa7c195994aa` |
| `e_trich_xuat/tests/kiem_may_sach.py` | `3004fb910b8da41890f3fbbc0263d2418d5ec61d59f7f119133b4463ae7d23fd` |
| `e_trich_xuat/tests/test_tx6_chuoi.py` | `db24627c3d2a0fcdcdb01610424e120bef3337fe0db9651bb423fa3360532135` |
| `e_trich_xuat/tests/test_tx6_http.py` | `829d30197b8533e64ad1ef482d3d28d3b41eee0730a621d5ad013dc2912d18f7` |
| `e_trich_xuat/tests/test_cong_cu_tx6.py` | `5819b64a087c4ed64629ac6dad1906b19d1598f6219096e0ec3d9068d90c57f4` |
| `e_trich_xuat/tests/test_nguon_tx6.py` | `cc7d3d1448e45e9415929d2a95cfe75f827e23fd8772634c04d1ba8307edc57b` |
| `e_trich_xuat/docs/TX-6-BIEN-BAN-MAU.md` | `719f5582df2bb32e46bb1db9aff5ee297c1a1d680b232779e2431ad947d36b65` |
| `e_trich_xuat/docs/TX-6-CHECKLIST-1700.md` | `22f1395d568f667f06fce2049e720a30c25791c98dea713afda7a2be95958e97` |
| `e_trich_xuat/docs/TX-6-KET-QUA.md` | `4fd2ddd48807429c878125fdf1c413eae03a2b92c66a366836839d048ecb7839` |
| `e_trich_xuat/docs/TX-6-N1-CHAY-KHO.json` | `13795f4cf40565e6927e76ce07ad72f424929bc19699ed1de9531816adeb8d84` |
| `e_trich_xuat/docs/TX-6-T3-CHAY-KHO.json` | `0387cf32f2589ff15a430a54dfe915cd65a39a6beea3f1215f2641aa442821f9` |

# Nguồn gói TX-1 / TX-2 / lõi TX-3 đề xuất

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
| `CHANGELOG.md` | `472bde9bdcab3b6ed581eb37562d4855d6187a7a7d2cec2a4d3ccfc4db296c06` |
| `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `contract/yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `449c8c5fb6569800087c01ef38203c91054bd97d8ba7b66e96f90bd261c9151e` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/cau_truc.py` | `6c284258181c6316cc0185b406a4da8d3f6a3670d714f35fa6b53ec27db482af` |
| `e_trich_xuat/chay.py` | `504616b003305f5e723d95eca6ec14f312feb78b617605b8d0f80ab1889df91f` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_trich_xuat/tham_so.py` | `2106cece109ca86272e94717abd6b6e6e0489e95c0ac49f33c0f71fa617cbc12` |
| `e_trich_xuat/tich_hop.py` | `3ed084a6bdca69e75c91ae4cfae88cc4c69dd01fbb111498998d90e164a93570` |
| `engine.json` | `c731456c391025ea23e6ab89641558b1f057de6033371fb174c03be618d7ba70` |
| `KHAI-SDK-2.1.json` | `9dc34efb03293ab8f314d4b7610c60bff5dc231835cb733c4add06bbc4741619` |
| `README.md` | `06cac28851c509fce61b0250518a6545edee1e6c61c565c758324dc05c3f4d3c` |
| `requirements.lock` | `f1c814f4fcea2aef4d55342db50054ea97943552ba0f5bdf72a19c892410b3b5` |
| `ui/cau_hinh.js` | `c605cb20b135c646583da0628b8af801b768e8bde600e4eb29d048888f8615ba` |

## SHA-256 tích hợp và kiểm ngoài gói

| Tệp | SHA-256 |
|---|---|
| `_chung/mau-ma/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/tests/test_goi.py` | `bafadb4e86ccab437f461b30586c8d3ffecf87cd2ea29830385175e7020d6ebc` |
| `e_trich_xuat/tests/test_ngan_cau_hinh.py` | `914ee271e2a811056be100236bbb0f45388b7d1d44c5803516c8d46969a520d4` |
| `e_trich_xuat/tests/test_docx.py` | `66480e3a5d4db58ec568943ada632f918140bc5e1cc198d647e4a62e30d74f9c` |
| `e_trich_xuat/tests/test_chuan_bi.py` | `a9109dc76957576e4ee9b1e45f0d0f3e300f41bee563ba4cf7d730ce506058f0` |
| `e_trich_xuat/tests/test_cong_sdk.py` | `18cbc6fa2bbb43a3c317b89a3d455a7df487347e5146fb44cf5630a86909fdda` |
| `e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | `aac71fd49f8eb4050b1643cdc57b26e4cc4d43cc536667f64190c8507b09f503` |
| `e_trich_xuat/tests/requirements.lock` | `736ea02ef855c421afcaa53a43f2005d5c59212f62cf0eea241de4090f40eaf3` |
| `e_trich_xuat/docs/TX-1-PHAM-VI.md` | `ddf797115058e114d79cddb17547740416c27003c28b5b7396c7c15149e97850` |
| `e_trich_xuat/docs/VIEC.md` | `db45e498f78ea6479f704fbcec48da5a2956f1210173a0c5850729a3dad2c63d` |


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

## SHA-256 bổ sung TX-3

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/vendor/review/kiem_tra.py` | `47ee35567cb7b864a6b3d6825bc90f93a7a26c0c6872a326e99ead9160467f12` |
| `e_trich_xuat/ma-nguon/vendor/review/logic.py` | `f7cfcf37ff2293d8f8ea994f1ae0a69f57d1d1d9a844f0620f018a3d285a4452` |
| `e_trich_xuat/ma-nguon/vendor/review/xlsx_mini.py` | `a29ed16811637daa756fcb2640557ec817734d3d2ee617c30deca51d3799857b` |
| `_chung/contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `e_trich_xuat/hau_kiem.py` | `0266b6baf67139e6017777882c0acf5a13ac0a691fe246494a871b909308604a` |
| `e_trich_xuat/kiem_tra.py` | `2aaece45e377e184640f6648de2ca800f4f25a4bc7d951b868c71f918a316daa` |
| `e_trich_xuat/logic.py` | `66f6befde686bc3d86cb234889a61af0655d4c92b7b1be09e86d177fcb152950` |
| `e_trich_xuat/xlsx_mini.py` | `b139d90d6adb186d658ad00f7970f7647f351178a035459b0913cf4298edc5e3` |
| `e_trich_xuat/xuat.py` | `88be1def75d909838e0431f9705d758d29f78c33d543116ef66bda5bbff6fe8a` |
| `e_trich_xuat/tests/mau_tx3.py` | `374a64d3e3de97b2ce1300fbc4e04f93731f861479eb86a7990037e3b6616410` |
| `e_trich_xuat/tests/test_hau_kiem.py` | `52dcd98922ddb58be9306f06e4061791b434ccd4a9751d3e28f93be83f69a754` |
| `e_trich_xuat/tests/test_xuat.py` | `15eb462802f5bc2b2224f397093f226beafb274943ca83d721ffa2917178f547` |
| `e_trich_xuat/docs/TX-3-REVIEW.md` | `d8d090900a9be33a447e46d40bc0aea67600f43fad2f1807e8ae731b8d74a0b8` |

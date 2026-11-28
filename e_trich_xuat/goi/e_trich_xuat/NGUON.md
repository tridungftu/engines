# Nguồn gói TX-1 / TX-2 / TX-3 / TX-3b

## SDK25 — nguồn hiện hành, 22/11/2026

Gói **0.5.3** dùng SDK **2.5.x do Core cấp**, đã kiểm với wheel 2.5.0 trong
`docs/goi-gui-engine/sdk-2.5.0/` và SHA256SUMS đi kèm. Khoảng manifest giữ
`>=2.4.0 <3.0.0`. Bộ wheel Windows do lead chuẩn bị (mục “Wheel kèm gói”)
giữ nguyên bytes/phiên bản. LX-TX thêm hash và wheel Linux ở mục cuối;
không tải mạng, không dựng lại wheel.
SDK không nằm trong lock hay wheels. Thư viện cài offline bằng hash vào khu
riêng cạnh gói, không sửa cây gói khi cài. Công cụ test dùng lock riêng.

Mã runtime chỉ dùng cửa công khai `Engine.tu_khai_bao`; bỏ chặn phiên bản
và ghi đè nội bộ. Câu lỗi MIME/kích thước và lọc log thuộc SDK (C-TX-05).
Test dùng `DuongTruyen` công khai; không chạm cấu trúc nội bộ của SDK.
Quyền/nguồn giữ nguyên; không đổi nghiệp vụ. **đã kiểm bằng Core giả (CoreGia)**.
Kết quả và phần Cần Core hiện hành nằm tại `../../docs/VIEC.md`.
Những mô tả TX-7/TX-6 và bản SDK cũ bên dưới là lịch sử; bảng băm phản ánh
nội dung tệp hiện tại theo quy ước CRLF→LF, wheel băm nguyên bytes.

### Tệp kiểm bổ sung SDK25

| Tệp | SHA-256 |
|---|---|
| `docs/goi-gui-engine/sdk-2.5.0/kho_tri_thuc_sdk-2.5.0-py3-none-any.whl` | `b235b513deb557f65f5a90c81e1d81e9b51799093fdaefb3bb5c5e1e954d2b55` |
| `e_trich_xuat/tests/phu_thuoc_python.py` | `905e351bf0929423aae8923ebbf86896e8ba5cdff9b14f0bdf619d980d8eb7fb` |
| `e_trich_xuat/tests/test_phu_thuoc_python.py` | `66820d1355dc3e13d2d66a5cf02fa15344b01e8bcd92460b349f56dc388d938c` |
| `e_trich_xuat/tests/cong_sdk_cong_khai.py` | `d6c25b5c899e8684f33c989eab59e8c4471eef768a295333e87dad98c5f87a05` |


## Lịch sử TX-7 — 15/11/2026

Gói 0.5.0 dùng SDK **2.2.0**. Mô tả TX-1…TX-6 bên dưới là lịch sử;
đường dẫn và SHA trong bảng được cập nhật theo vị trí/nội dung hiện tại.
Mã cổng tạm và CLI thay thế đã chuyển nguyên bytes sang `LUU-TRU/TX-7`,
không còn trong runtime. Không thêm thư viện nghiệp vụ. SDK 2.2.0 yêu cầu
cryptography và jsonschema; ghim toàn bộ phụ thuộc bắc cầu trong
`requirements.lock`, công cụ test ghim riêng ở `../../tests/requirements.lock`.

- Wheel SDK nội bộ: `docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl`;
  SHA-256 nguyên bytes `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`,
  khớp `SHA256SUMS.txt`; cài offline `--no-index --no-deps` vào venv mới.
- Phụ thuộc: cryptography 49.0.0, cffi 2.0.0, pycparser 3.0, jsonschema
  4.26.0, attrs 26.1.0, jsonschema-specifications 2025.9.1, referencing
  0.37.0, rpds-py 2026.6.3, typing_extensions 4.15.0. Đây là dependency
  SDK đã phát hành, không đổi nghiệp vụ engine. Test: pytest 9.1.1,
  iniconfig 2.3.0, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0,
  colorama 0.4.6 (chỉ Windows).
- Phiên này không tải mạng: đóng lại wheel từ các distribution đúng phiên bản
  đã cài trên máy, chỉ package/metadata; cài offline vào `.venv` độc lập,
  không system-site-packages/PYTHONPATH. Kho tạm ở `.venv/offline-wheels`,
  không nằm trong gói/git, không phải wheel phát hành thượng nguồn.
  `pip check` đạt. Kho wheel giao máy khác phải có binaries đúng nền tảng;
  kiểm phiên này là Windows x64, chưa chứng nhận Linux.
- Quyền/nguồn dự án giữ nguyên. Metadata/giấy phép thư viện nằm trong
  distribution đã cài; SDK/wheel là nguồn nội bộ được giao. Không chép thư viện
  ngoài vào mã gói. Các công cụ TX-6 chỉ thay môi trường/cổng cấu hình.
- Bổ sung `bam_cau_hinh` hồ sơ nội bộ để bù `Viec` chưa công bố phiên bản;
  hậu kiểm kiểm băm và giữ tương thích hồ sơ cũ. Không đổi schema loại chung.
- Không có bảng ngăn sau bỏ bảng cấu hình; không SQL/migration/kiểm kê SQL.
  SHA văn bản dưới đây chuẩn hóa CRLF→LF; nhị phân băm nguyên bytes.
  **đã kiểm bằng Core giả (CoreGia)**; CLI chuẩn 4/5, còn C-TX-06,
  không sử dụng cổng DEMO thay thế để nghiệm thu.


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
| `CHANGELOG.md` | `77a4756a0273b1468cfc9ba8296a0d53808d90b9c22b8229d9cc035d98e75f56` |

| `cau_hinh.schema.json` | `d169a619f7968469ddc25422e793b9e4b5ec83caa420b4a8f8fdc4eb1e6ba9de` |
| `CHANGELOG.md` | `77a4756a0273b1468cfc9ba8296a0d53808d90b9c22b8229d9cc035d98e75f56` |
| `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `contract/yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `1832b57855397f8618590ccc8100c4232ea515da65405a4d35109dcd885b37d2` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/LUU-TRU/TX-7/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/cau_truc.py` | `1a44e428a8dc2e1e5a5d52524baaafa12e6dddc6e1dc026b17cc519470760459` |
| `e_trich_xuat/chay.py` | `90dc40d972486b24a037963b62f2668b52f02bb7127c5c028afb1557673e910e` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/LUU-TRU/TX-7/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_trich_xuat/tham_so.py` | `2106cece109ca86272e94717abd6b6e6e0489e95c0ac49f33c0f71fa617cbc12` |
| `e_trich_xuat/tich_hop.py` | `26fa7299a3a2d992bfdeb44536031a367b06f1ad20b6575818332edbb2463d1a` |
| `engine.json` | `e7203ced4fe3abbc8a3a40a491a3b2064fd51202dee4b8a1365ab13cbde24ea0` |
| `e_trich_xuat/LUU-TRU/TX-7/KHAI-SDK-2.1.json` | `9dc34efb03293ab8f314d4b7610c60bff5dc231835cb733c4add06bbc4741619` |
| `README.md` | `84a2bc2068dc225bfd684b2ac00b81fdbedbd8a769e48005cec5bd7d32a87910` |
| `requirements.lock` | `026bf692635d589fcbb230e13d89ac9613a5950575cc3292a8f9e8f8499671be` |
| `ui/cau_hinh.js` | `dc89c9368b82cadf5753474689a8084004b584cee49cc9e61e9ecb60614d0ca5` |

## SHA-256 tích hợp và kiểm ngoài gói

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/LUU-TRU/TX-7/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_trich_xuat/LUU-TRU/TX-7/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/tests/test_goi.py` | `8fc309807c3b5e3862fbf577eef8d5b8b9d442d8d3f182192f056d4e3f60fe92` |

| `e_trich_xuat/tests/test_goi.py` | `8fc309807c3b5e3862fbf577eef8d5b8b9d442d8d3f182192f056d4e3f60fe92` |
| `e_trich_xuat/tests/test_ngan_cau_hinh.py` | `d95b96a7932f6cb5c6e534b21e1400937b29608705c95f3894b623c9e2ba3d13` |
| `e_trich_xuat/tests/test_docx.py` | `da9f46457b135d1085be447dc953bb5b86f22e91e39d8b0b94c4d50ec0babf28` |
| `e_trich_xuat/tests/test_chuan_bi.py` | `e1c721d80c0ac54513fab3b58d64305f3a906447f83a9fe059572a255bb7bd6f` |
| `e_trich_xuat/tests/test_cong_sdk.py` | `065c8fd3003da0d0ee486e20ebb3f72b48539e991822c7a899af5836634748c8` |
| `e_trich_xuat/LUU-TRU/TX-7/chay_demo_voi_ngan_gia.py` | `01158473b3a466637814088c58b08b10c02ea22531b45c4239831cce2a2c5bc2` |
| `e_trich_xuat/tests/requirements.lock` | `c3e1a435ede212a2b290d6f423ee32d48e2667dc52d1336e91f11deca6466da8` |
| `e_trich_xuat/docs/TX-1-PHAM-VI.md` | `ddf797115058e114d79cddb17547740416c27003c28b5b7396c7c15149e97850` |
| `e_trich_xuat/docs/VIEC.md` | `47738563b7f9f8f1d2209dfaece53dc0853804674d8fb0923186be0f1f1de231` |

| `e_trich_xuat/docs/VIEC.md` | `47738563b7f9f8f1d2209dfaece53dc0853804674d8fb0923186be0f1f1de231` |


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
| `e_trich_xuat/hau_kiem.py` | `d2212553a215ca1fa047c4d81f99b806c08c9b0ff03ae4150b6ed7174efde6f3` |
| `e_trich_xuat/kiem_tra.py` | `17a988f374d591b7d1b9b6ef31c8b86faf6352c3a53025c6701ee4d4c767fcf9` |
| `e_trich_xuat/logic.py` | `66f6befde686bc3d86cb234889a61af0655d4c92b7b1be09e86d177fcb152950` |
| `e_trich_xuat/xlsx_mini.py` | `b139d90d6adb186d658ad00f7970f7647f351178a035459b0913cf4298edc5e3` |
| `e_trich_xuat/xuat.py` | `a4cc1ff456b1235ff01ecd010f588eb89e04ce2dd6eefa7b6fc856e8dc0f431c` |
| `e_trich_xuat/tests/mau_tx3.py` | `bf877e267ea9ce83a7fec22e5be619aa93d75129d437d5d5982293fb7a6792e5` |
| `e_trich_xuat/tests/test_hau_kiem.py` | `ac5568e78e7669bdafb02c99bcf284a0f47caec60c4b32325b458ee4000d7ac1` |
| `e_trich_xuat/tests/test_xuat.py` | `cb8f926ec94213dbb3d0a8a13dc4f86956422e05bccc4d409919de41f8907c35` |
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
| `e_trich_xuat/tests/test_dang_ky_tx3b.py` | `f49f8592496e1898977e1d834cc511fbbc9dcd6c4fd342deb73fca74c7756701` |


## SHA-256 TX-6 (văn bản CRLF→LF; wheel nguyên bytes)

| Tệp | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/do_chinh_xac.py` | `bb37f8c8313706f7ed9c65bfc2afffe4f7946b4986f028f93da5230ce442c3e3` |
| `e_trich_xuat/docs/TX-0-THIET-KE.md` | `95826b1cfa0cd0fa17dcef4245b7f444f642d0ddcdaf301ddec7c34690d921e9` |
| `e_hoi_ai/cong-cu/thu_local_ai_that.py` | `6bd46ff6fffe39110122f082d14618c05906804936ff84014a427502c8f41e87` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/ai_cuc_bo.py` | `b8c0155ff46b2ec6bfe472483c5015c4a90e8c743499f44bce14857fc007852a` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/chon_model.py` | `ace9854285187c6dfd6543cd297f306ef45ddd29b9168dabe917749bdd5a3f66` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/cong_ai.py` | `99bef752985200e2a40760a55ecd33422e844b40fb7361fd63bba070bce16ae8` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/hoi_yeu_cau.py` | `3162ba602025607ec8b6ca7de3321a76af78b43fccaf8af837d9dce524cd565c` |
| `e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/khuon_json.py` | `ab4dc18a48df5f6f7c8e8f08ae10ea87e5a0a43ced3ca0870909e44eece069df` |
| `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `e_trich_xuat/cong-cu/CHAY-N1-MOT-LAN.cmd` | `f287b2411ca6c483a98cd3e75f1e806b1f4351fd7092c5bc98542dac1ff07911` |
| `e_trich_xuat/cong-cu/DO-SUC-CHUA-MODEL.cmd` | `d62ac92f2df51bb6f06efbb0c29fc035bb25b5ce9a088ebeacc1d0e8ef6c5365` |
| `e_trich_xuat/cong-cu/do_n1_mot_lan.py` | `b8fee85ed2295ae057dd23137c36df217a9603b5f7fdf9de91722090f958c5b3` |
| `e_trich_xuat/cong-cu/do_suc_chua_model.py` | `22e51a11d7c855cf178ad353d835e84f13ca9d0f63725ba9fe32af2a58ff1987` |
| `e_trich_xuat/cong-cu/ho_tro_do.py` | `40511c48987ecc825f5054e45e45b0556f40694a934b74574437864a07015159` |
| `e_trich_xuat/cong-cu/MAU-NEN-N1.json` | `910d19445e7b139eef0428e23dd40bf3a11eae7140dd8131dc8101c99159246d` |
| `e_trich_xuat/cong-cu/README.md` | `afec30ba63ba93b05e9b2528c6227f7c52a14a84f24d46250de6a2f803bbe79f` |
| `e_trich_xuat/tests/kiem_may_sach.cmd` | `275581a55e32d0435ee52fd19c949eeb4387550b1d1db05df662c61bbc5b5162` |
| `e_trich_xuat/tests/kiem_may_sach.sh` | `600a87981a00f93b5ae1b2512d3f233937890adb737cf205008d94865178708a` |
| `e_trich_xuat/tests/kiem_may_sach.py` | `d433142e3f9f9efcad4929b43aa73c6453df1c26ef94809a455124b34dd744a8` |
| `e_trich_xuat/tests/test_tx6_chuoi.py` | `de16d255cafece5288c28758728e4ecf66b9833c94ff59ec61812cda0e6b8b54` |
| `e_trich_xuat/tests/test_tx6_http.py` | `09b242397de9721aa92036817ec84ddb0845aadf7ae1ed107e392282f2cf8d50` |
| `e_trich_xuat/tests/test_cong_cu_tx6.py` | `e627564bd44cd1555fff63af66b41d92cbf8fb9f5b6556c85e525f54cfa4f3fb` |
| `e_trich_xuat/tests/test_nguon_tx6.py` | `cc7d3d1448e45e9415929d2a95cfe75f827e23fd8772634c04d1ba8307edc57b` |
| `e_trich_xuat/docs/TX-6-BIEN-BAN-MAU.md` | `719f5582df2bb32e46bb1db9aff5ee297c1a1d680b232779e2431ad947d36b65` |
| `e_trich_xuat/docs/TX-6-CHECKLIST-1700.md` | `22f1395d568f667f06fce2049e720a30c25791c98dea713afda7a2be95958e97` |
| `e_trich_xuat/docs/TX-6-KET-QUA.md` | `4fd2ddd48807429c878125fdf1c413eae03a2b92c66a366836839d048ecb7839` |
| `e_trich_xuat/docs/TX-6-N1-CHAY-KHO.json` | `13795f4cf40565e6927e76ce07ad72f424929bc19699ed1de9531816adeb8d84` |
| `e_trich_xuat/docs/TX-6-T3-CHAY-KHO.json` | `0387cf32f2589ff15a430a54dfe915cd65a39a6beea3f1215f2641aa442821f9` |


## SHA-256 bổ sung TX-7 (văn bản LF; nhị phân nguyên bytes)

| Tệp | SHA-256 |
|---|---|
| `docs/goi-gui-engine/sdk-2.2.0/kho_tri_thuc_sdk-2.2.0-py3-none-any.whl` | `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` |
| `e_trich_xuat/cong-cu/README.md` | `afec30ba63ba93b05e9b2528c6227f7c52a14a84f24d46250de6a2f803bbe79f` |
| `e_trich_xuat/docs/CHANGELOG.md` | `f17e2a48a37976ed57674b01de516ca37c93e34d43fcf072a86b407881451c60` |
| `CHANGELOG.md` | `77a4756a0273b1468cfc9ba8296a0d53808d90b9c22b8229d9cc035d98e75f56` |

| `cau_hinh.schema.json` | `d169a619f7968469ddc25422e793b9e4b5ec83caa420b4a8f8fdc4eb1e6ba9de` |
| `CHANGELOG.md` | `77a4756a0273b1468cfc9ba8296a0d53808d90b9c22b8229d9cc035d98e75f56` |
| `contract/bang_trich_xuat.schema.json` | `f36314d7e3958281966a5c4c24ca3cd9a01df507d7a07d0b96a0aebafe4ea82f` |
| `contract/tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `contract/yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `demo/DEMO-ho-so-hau-kiem.json` | `4879e0e1d270631a50bcbc27707511f464bbca369816ab35f4e0fec82ab4e02b` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `1832b57855397f8618590ccc8100c4232ea515da65405a4d35109dcd885b37d2` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/cau_truc.py` | `1a44e428a8dc2e1e5a5d52524baaafa12e6dddc6e1dc026b17cc519470760459` |
| `e_trich_xuat/chay.py` | `90dc40d972486b24a037963b62f2668b52f02bb7127c5c028afb1557673e910e` |
| `e_trich_xuat/demo.py` | `117ea143d6d286516ee39408b11229279da522bb8cbfbe030750eaf875d155e0` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/hau_kiem.py` | `d2212553a215ca1fa047c4d81f99b806c08c9b0ff03ae4150b6ed7174efde6f3` |
| `e_trich_xuat/kiem_tra.py` | `17a988f374d591b7d1b9b6ef31c8b86faf6352c3a53025c6701ee4d4c767fcf9` |
| `e_trich_xuat/logic.py` | `66f6befde686bc3d86cb234889a61af0655d4c92b7b1be09e86d177fcb152950` |
| `e_trich_xuat/tham_so.py` | `2106cece109ca86272e94717abd6b6e6e0489e95c0ac49f33c0f71fa617cbc12` |
| `e_trich_xuat/tich_hop.py` | `26fa7299a3a2d992bfdeb44536031a367b06f1ad20b6575818332edbb2463d1a` |
| `e_trich_xuat/xlsx_mini.py` | `b139d90d6adb186d658ad00f7970f7647f351178a035459b0913cf4298edc5e3` |
| `e_trich_xuat/xuat.py` | `a4cc1ff456b1235ff01ecd010f588eb89e04ce2dd6eefa7b6fc856e8dc0f431c` |
| `engine.json` | `e7203ced4fe3abbc8a3a40a491a3b2064fd51202dee4b8a1365ab13cbde24ea0` |
| `README.md` | `84a2bc2068dc225bfd684b2ac00b81fdbedbd8a769e48005cec5bd7d32a87910` |
| `requirements.lock` | `026bf692635d589fcbb230e13d89ac9613a5950575cc3292a8f9e8f8499671be` |
| `ui/cau_hinh.js` | `dc89c9368b82cadf5753474689a8084004b584cee49cc9e61e9ecb60614d0ca5` |
| `e_trich_xuat/LUU-TRU/TX-7/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/LUU-TRU/TX-7/chay_demo_voi_ngan_gia.py` | `01158473b3a466637814088c58b08b10c02ea22531b45c4239831cce2a2c5bc2` |
| `e_trich_xuat/LUU-TRU/TX-7/KHAI-SDK-2.1.json` | `9dc34efb03293ab8f314d4b7610c60bff5dc231835cb733c4add06bbc4741619` |
| `e_trich_xuat/LUU-TRU/TX-7/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_trich_xuat/LUU-TRU/TX-7/README.md` | `08723b4adb6bf3c7d7c1af88996579b47735ad42dbcff7a2caf3f00ef3f577be` |
| `e_trich_xuat/tests/conftest.py` | `edf0f08b74fe2fc5f52a62663352afc82a8f8a490d087b30c03d83dda02d4eb1` |
| `e_trich_xuat/tests/doi_chieu_cu_e6.py` | `608fd3b2e227a1b368cd465dcce26fa8a031de82e46b167457762e58922e0515` |
| `e_trich_xuat/tests/kiem_doc_lap.py` | `6f175792f9b0e04c20e7879bbbb24dd92d9f0d18d7407e3ae1383fb2d012d572` |
| `e_trich_xuat/tests/kiem_e6.py` | `a8986f410a07e9e5f60c92ca32694baa7032fff6d6f47600498d7620daa02990` |
| `e_trich_xuat/tests/kiem_may_sach.py` | `d433142e3f9f9efcad4929b43aa73c6453df1c26ef94809a455124b34dd744a8` |
| `e_trich_xuat/tests/kiem_may_sach.sh` | `600a87981a00f93b5ae1b2512d3f233937890adb737cf205008d94865178708a` |
| `e_trich_xuat/tests/mau_docx.py` | `28c34a8f9b5d3d728f6b8306273cee1b2862f6a7e7e5261a0dad505578443afc` |
| `e_trich_xuat/tests/mau_tx3.py` | `bf877e267ea9ce83a7fec22e5be619aa93d75129d437d5d5982293fb7a6792e5` |
| `e_trich_xuat/tests/requirements.lock` | `c3e1a435ede212a2b290d6f423ee32d48e2667dc52d1336e91f11deca6466da8` |
| `e_trich_xuat/tests/tao_demo_e6.py` | `5908b0e7b22101601cfbaece37bb2c7a3b242062f6fbb0efd68e41d86d5c9760` |
| `e_trich_xuat/tests/test_chuan_bi.py` | `e1c721d80c0ac54513fab3b58d64305f3a906447f83a9fe059572a255bb7bd6f` |
| `e_trich_xuat/tests/test_cong_cu_tx6.py` | `e627564bd44cd1555fff63af66b41d92cbf8fb9f5b6556c85e525f54cfa4f3fb` |
| `e_trich_xuat/tests/test_cong_sdk.py` | `065c8fd3003da0d0ee486e20ebb3f72b48539e991822c7a899af5836634748c8` |
| `e_trich_xuat/tests/test_dang_ky_tx3b.py` | `f49f8592496e1898977e1d834cc511fbbc9dcd6c4fd342deb73fca74c7756701` |
| `e_trich_xuat/tests/test_docx.py` | `da9f46457b135d1085be447dc953bb5b86f22e91e39d8b0b94c4d50ec0babf28` |
| `e_trich_xuat/tests/test_e6.py` | `d2a8e5783a69de379de72a0868452b1c681dd85ef526210744713ee76756df85` |
| `e_trich_xuat/tests/test_goi.py` | `8fc309807c3b5e3862fbf577eef8d5b8b9d442d8d3f182192f056d4e3f60fe92` |

| `e_trich_xuat/tests/test_goi.py` | `8fc309807c3b5e3862fbf577eef8d5b8b9d442d8d3f182192f056d4e3f60fe92` |
| `e_trich_xuat/tests/test_hau_kiem.py` | `ac5568e78e7669bdafb02c99bcf284a0f47caec60c4b32325b458ee4000d7ac1` |
| `e_trich_xuat/tests/test_ngan_cau_hinh.py` | `d95b96a7932f6cb5c6e534b21e1400937b29608705c95f3894b623c9e2ba3d13` |
| `e_trich_xuat/tests/test_nguon_tx6.py` | `cc7d3d1448e45e9415929d2a95cfe75f827e23fd8772634c04d1ba8307edc57b` |
| `e_trich_xuat/tests/test_tx5_ban_giao.py` | `48a09d3976df29942ba6ca0a03effe117cbd12a46f8954a4d67bf94ba5b1cfc7` |
| `e_trich_xuat/tests/test_tx6_chuoi.py` | `de16d255cafece5288c28758728e4ecf66b9833c94ff59ec61812cda0e6b8b54` |
| `e_trich_xuat/tests/test_tx6_http.py` | `09b242397de9721aa92036817ec84ddb0845aadf7ae1ed107e392282f2cf8d50` |
| `e_trich_xuat/tests/test_xuat.py` | `cb8f926ec94213dbb3d0a8a13dc4f86956422e05bccc4d409919de41f8907c35` |


## TS-TX — nguồn bổ sung 21/11/2026

Màn mới và thao tác kiểm thuần dùng E1 của SDK 2.2.0; không thêm dependency runtime.
SDK cài offline từ wheel đã đối chiếu SHA; .venv dùng system-site-packages với toàn bộ phiên bản khớp hai requirements.lock hiện hành.
Node kiểm offline. Playwright có sẵn trong môi trường công cụ chỉ dùng chụp ảnh DEMO, không đóng vào gói và không cần để chạy unit test Node.
Không thay hành vi việc, engine.json, ui/cau_hinh.js hoặc cau_hinh.schema.json của lát UI-TX.

| Tệp | SHA-256 (văn bản CRLF → LF) |
|---|---|
| `KHAI-SDK-2.1.json` | `d8146e46e61f3cf78551c58504fd8c97501d480acf791a52f175067af39d8661` |
| `e_trich_xuat/soan_bo.py` | `960cbc3db51fb2db2870f5c9833b78c7942dbf1dc40b7c594d24a07a5ba6bc03` |
| `ui/soan_bo_tham_so.js` | `a1cf74fa22eb4e2ea002c5720ef87ac2293bfa36d97581989c1345ac9927d11d` |
| `e_trich_xuat/tests/test_soan_bo_ts_tx.py` | `87a7e2a018f8b24178d3480bca5313216e20725f8b2022fe708e3f1a95d1176e` |
| `e_trich_xuat/tests/ui/cong_soan_bo.py` | `46423b080c66418b463c0ff2b5a00a41c6881dccd203288bc2adcde02050ddac` |
| `e_trich_xuat/tests/ui/soan_bo_ts_tx.test.mjs` | `dbaf751982d753802e8d92b3976bcc59e55a70349159c8068a922800212dd568` |
| `e_trich_xuat/tests/ui/dung_anh_ts_tx.py` | `1f0b5f080dbf5ba4af03a8c03409834553bc55867738afb9621565aba91a895e` |
| `e_trich_xuat/tests/ui/chup_anh_ts_tx.cjs` | `c6694a368055cab6d96564246638ebd0395b619537fdc9fdfe17d6e3986b56ae` |

## Wheel kèm gói (22/11/2026)

Thư mục `wheels/` chứa wheel tải từ PyPI (pypi.org) đúng phiên bản và SHA-256 ghi ở `requirements.lock`; đã đối chiếu với băm PyPI ghim từ trước nếu có. Nền CPython 3.13 win_amd64 hoặc thuần Python; `cryptography` chỉ phát hành dạng `cp311-abi3`, đã thử cài và chạy trên Python 3.13.14 sạch. Giấy phép của từng thư viện nằm trong `*.dist-info` của wheel. Không sửa wheel.

## LX-TX — wheel Linux, 28/11/2026

Lead cấp ba wheel PyPI tải bằng Python 3.13 trên WSL Ubuntu 24.04,
kèm SHA256SUMS. Đã kiểm SHA-256 nguyên bytes của nguồn và bản chép tại
`e_trich_xuat/wheels-linux/`, ngoài gói Windows. Không tải mạng, không đổi
wheel hoặc phiên bản thư viện. Giấy phép giữ trong `.dist-info` của wheel.
Lock chung giữ hash Windows trước, hash manylinux x86_64 thứ hai; sáu
wheel thuần Python dùng chung một hash từ `wheels/`. Bộ kiểm SDK25 và
venv mới dùng cùng bộ đọc nhiều hash, chọn wheel theo nền; Linux glibc
không quá 2.39, CPython 3.13 hoặc abi3 tương thích, không musllinux.
Việc cài/chạy Linux sạch do lead kiểm tiếp trên WSL, chưa chứng nhận tại đây.
Hai băm tham chiếu Hỏi AI trong bảng TX-6 đã cũ so với HEAD trước LX-TX;
đã đối chiếu HEAD/worktree trùng bytes chuẩn hóa LF rồi cập nhật băm hiện
hành cho `thu_local_ai_that.py` và `ai_cuc_bo.py`. Không sửa các nguồn này
hoặc nguồn E6; chi tiết kiểm ở `../../docs/VIEC.md`.

| Tệp | SHA-256 (nguyên bytes) |
|---|---|
| `e_trich_xuat/wheels-linux/cffi-2.0.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl` | `c8d3b5532fc71b7a77c09192b4a5a200ea992702734a2e9279a37f2478236f26` |
| `e_trich_xuat/wheels-linux/cryptography-49.0.0-cp311-abi3-manylinux_2_34_x86_64.whl` | `cbc77da8c523d5abd028635ba850a6966fcee2c82e2bf65a41d1d8afe0f98be9` |
| `e_trich_xuat/wheels-linux/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `acac386b453c2516111b50985d60ce46e7fadb5ea71ae7b25f4c946935bf27cf` |

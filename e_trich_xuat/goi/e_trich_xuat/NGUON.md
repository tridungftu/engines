# Nguồn gói TX-1

Nguồn nội bộ đã có trong repo; không thêm mã/thư viện bên ngoài.

| Nguồn tương đối từ gốc repo | Đích trong gói | Chuyển đổi |
|---|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `e_trich_xuat/docx.py` | Giữ đếm sửa đổi theo namespace; thay adapter đường dẫn bằng bytes SDK |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `e_trich_xuat/docx.py` | Chuyển có sửa Accept All, Numbering; giữ ô rỗng/gộp, thêm giới hạn ZIP/XML; bỏ đọc/ghi tệp và chuyển định dạng |
| `_chung/contract/van_ban_tai_lieu.schema.json` | `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte; test so SHA |
| `_chung/mau-ma/ngan.py`, `_chung/mau-ma/cau_hinh.py` (NGAN-0, PR #34) | `e_trich_xuat/ngan.py`, `e_trich_xuat/cau_hinh.py` | Lead đã chép bản chung; giữ nguyên, so SHA-256 sau chuẩn hóa CRLF→LF |
| SDK 2.0.0, engine DEMO và hợp đồng API v1 trong repo | `engine.json`, `e_trich_xuat/chay.py` | Khung khai năng lực thực; bọc hẹp lỗi SDK trước handler |
| Viết mới cho TX-1 | `ui/cau_hinh.js`, schema cấu hình và khai SDK 2.1 | Một ô cấu hình qua cổng Core, chưa nối Core thật |
| `e_trich_xuat/tests/mau_docx.py` (ngoài gói) | `demo/DEMO-*.docx` | Fixture giả xác định; nhãn DEMO trong nội dung |

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

| Tệp nguồn từ gốc repo | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `84b5662856ecf2742360077012377f913698a917e1fd4a4a08f87568e1af6a5b` |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f` |

## SHA-256 tệp trong gói

Không gồm chính tệp NGUON.md.

| Tệp tương đối trong gói | SHA-256 |
|---|---|
| `cau_hinh.schema.json` | `291d3ff81ffe0c12e31b1dd6e982b6339c3fa0992f6ec4797f33727ff06f1567` |
| `CHANGELOG.md` | `ba626b30b29aa394822e4c2f0d8e96ced224e4625a202d2e5785bd6988048699` |
| `contract/van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `b81a1a2d3efc663362f5c236e5d724a6c4bc19a676b647acc093f2047e91f742` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/chay.py` | `6b6373fe4dc5bbcdb983b924501d3c16db873294789aa49ba86e46806582c1fb` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `engine.json` | `f76a64b31aca1aa30d25a73880d9d294e4a6a7ad146bdbc494628d1b255a5712` |
| `KHAI-SDK-2.1.json` | `9dc34efb03293ab8f314d4b7610c60bff5dc231835cb733c4add06bbc4741619` |
| `README.md` | `cb5ff47a945b94794c748cf141de04c547aeed3aa745bd7af08e0811c82bc487` |
| `requirements.lock` | `f1c814f4fcea2aef4d55342db50054ea97943552ba0f5bdf72a19c892410b3b5` |
| `ui/cau_hinh.js` | `c605cb20b135c646583da0628b8af801b768e8bde600e4eb29d048888f8615ba` |

## SHA-256 tích hợp NGAN-0 ngoài gói

Đường dẫn tính từ gốc repo; cùng quy ước LF ở trên.

| Tệp | SHA-256 |
|---|---|
| `_chung/mau-ma/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `e_trich_xuat/tests/test_goi.py` | `80f26a43016efc664c4cbdd548ac1e6edb261cec44fe02d784bc88f45bc1d536` |
| `e_trich_xuat/tests/test_ngan_cau_hinh.py` | `914ee271e2a811056be100236bbb0f45388b7d1d44c5803516c8d46969a520d4` |
| `e_trich_xuat/tests/test_docx.py` | `78f0f36f3bbca308f37294d8e653b172712fe13b676d305b48ba69619d84ea64` |
| `e_trich_xuat/tests/requirements.lock` | `736ea02ef855c421afcaa53a43f2005d5c59212f62cf0eea241de4090f40eaf3` |
| `e_trich_xuat/docs/TX-1-PHAM-VI.md` | `ddf797115058e114d79cddb17547740416c27003c28b5b7396c7c15149e97850` |
| `e_trich_xuat/docs/VIEC.md` | `143bfb6f1253bba66e0f467d969371ceb462bb43146f264784e3fabb91033c71` |

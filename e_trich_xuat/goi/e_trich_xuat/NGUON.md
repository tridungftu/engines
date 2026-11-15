# Nguồn gói TX-1

Nguồn nội bộ đã có trong repo; không thêm mã/thư viện bên ngoài.

| Nguồn tương đối từ gốc repo | Đích trong gói | Chuyển đổi |
|---|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `e_trich_xuat/docx.py` | Giữ đếm sửa đổi theo namespace; thay adapter đường dẫn bằng bytes SDK |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `e_trich_xuat/docx.py` | Chuyển có sửa Accept All, Numbering; giữ ô rỗng/gộp, thêm giới hạn ZIP/XML; bỏ đọc/ghi tệp và chuyển định dạng |
| `_chung/contract/van_ban_tai_lieu.schema.json` | `contract/van_ban_tai_lieu.schema.json` | Chép nguyên byte; test so SHA |
| `_chung/docs/DE-NGHI-SDK-2.1.md` §3, đợt 2 §2 và ghi chú lead TX-1 | `e_trich_xuat/ngan.py`, `e_trich_xuat/cau_hinh.py` | Viết tạm theo API, thư viện chuẩn; chờ mẫu NGAN-0, chưa chứng nhận trùng mẫu |
| SDK 2.0.0, engine DEMO và hợp đồng API v1 trong repo | `engine.json`, `e_trich_xuat/chay.py` | Khung khai năng lực thực; bọc hẹp lỗi SDK trước handler |
| Viết mới cho TX-1 | `ui/cau_hinh.js`, schema cấu hình và khai SDK 2.1 | Một ô cấu hình qua cổng Core, chưa nối Core thật |
| `e_trich_xuat/tests/mau_docx.py` (ngoài gói) | `demo/DEMO-*.docx` | Fixture giả xác định; nhãn DEMO trong nội dung |

Không đổi/xóa nguồn cũ hoặc schema chung. Các đường điều phối/adapter cũ
không được đưa vào gói; đề xuất lưu trữ vẫn ghi trong `docs/VIEC.md`.

SHA-256 wheel SDK đã kiểm:
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Test dùng pytest có sẵn trên máy qua đường import của tiến trình kiểm;
không thêm dependency runtime. Test UI chỉ dùng Node chuẩn.

## SHA-256 nguồn đã chuyển

| Tệp nguồn từ gốc repo | SHA-256 |
|---|---|
| `e_trich_xuat/ma-nguon/docx.py` | `819b22d1e209d842a1d833d9d52273ccf0580bea572f6814f963b8b484264d31` |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `02022a9c05cb9fa71ef16465a59d3ac49265503dab8a85c98cb867c5933eeabc` |

## SHA-256 tệp trong gói

Không gồm chính tệp NGUON.md.

| Tệp tương đối trong gói | SHA-256 |
|---|---|
| `cau_hinh.schema.json` | `291d3ff81ffe0c12e31b1dd6e982b6339c3fa0992f6ec4797f33727ff06f1567` |
| `CHANGELOG.md` | `2d7f59250d0b53f6c32c95d05b7ad900bcf7519445eaf595ffa415e43fd7dd82` |
| `contract/van_ban_tai_lieu.schema.json` | `d73a80f276eef43536ee14810ef46a1df73d476a9b4f02cc4f3bd163f4d73902` |
| `demo/DEMO-hop-dong.docx` | `22030fe7fa1a65384e696b3fdfdd9506cca22fac7f268000d579d208cb8ec471` |
| `demo/DEMO-track-changes.docx` | `a665fac5cf0cc68fb0e1faec45984b5348185f4f34f6125fc3b2c7469edd40e7` |
| `demo/README.md` | `b81a1a2d3efc663362f5c236e5d724a6c4bc19a676b647acc093f2047e91f742` |
| `e_trich_xuat/__init__.py` | `132fde790e8e65934171f4d441cfd174ede92d8944e80c8ccdb23d8c5093f126` |
| `e_trich_xuat/cau_hinh.py` | `ac5ab84b72c60bad8725aa2bb08719e8005130c3ebc35ef96a14b79a8fee47c4` |
| `e_trich_xuat/chay.py` | `c5d17ec513083c3df38bce7466f67f231bbd2c72befb021878abc91d830a8798` |
| `e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ngan.py` | `ce962dd468f6d8f04e1807ce4ba4b4be1cc3c9517af275fda56e7c1484be5bcb` |
| `engine.json` | `f76a64b31aca1aa30d25a73880d9d294e4a6a7ad146bdbc494628d1b255a5712` |
| `KHAI-SDK-2.1.json` | `499d719ded152cfcff6cff75ad05b4e8e6c92c65a8326927f89578cf105f38ac` |
| `README.md` | `89589d45f51592be9f26f64ce7d6c0765ba02554031b91b3dc14171cbe91efc6` |
| `requirements.lock` | `f1c814f4fcea2aef4d55342db50054ea97943552ba0f5bdf72a19c892410b3b5` |
| `ui/cau_hinh.js` | `c605cb20b135c646583da0628b8af801b768e8bde600e4eb29d048888f8615ba` |

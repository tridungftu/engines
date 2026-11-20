# Nguồn và giấy phép — PL-0, 20/11/2026

Mã mới nội bộ theo PHIEU-ENGINE-e_phan_luong.md và GIAO-CODEX-e_phan_luong.md.
Không chuyển thuật toán nghiệp vụ ở PL-0; kieu.py và loi.py do lead giữ nguyên.

| Nguồn | Phần dùng |
|---|---|
| API-ENGINE-v1.md, SDK 2.2.0 MAU-PHIEU-ENGINE.md, THAY-DOI-2.2.0.md | Hợp đồng phiếu/cổng engine |
| SDK 2.2.0 engine-demo/e_demo_ngan | Cột hệ thống, migration và định dạng kiểm kê |
| e_kiem_excel/goi/e_kiem_excel/e_kiem_excel/chay.py | Ý tưởng bọc nhật ký SDK bằng mã cố định |
| e_kiem_excel/tests/conftest.py, kiem_doc_lap.py, kiem_bam_goi.py | Ý tưởng cách ly mạng, AST/import cô lập, bytes/SHA-256 |
| _chung/docs/LOAI-DU-LIEU-RIENG.md và _chung/contract/ | Hai schema AI chép nguyên byte, test đối chiếu băm |
| e_trich_xuat/goi/e_trich_xuat/engine.json | Khai báo tên loại AI chung |

Thư viện runtime ghim nguyên phiên bản/hash từ requirements.lock của e_kiem_excel:

| Thư viện | Phiên bản / giấy phép | SHA-256 wheel |
|---|---|---|
| openpyxl | 3.1.5 / MIT | 5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2 |
| et_xmlfile | 2.0.0 / MIT | 7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa |
| defusedxml | 0.7.1 / PSF License | a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61 |
| kho_tri_thuc_sdk (nội bộ, cài riêng --no-deps) | 2.2.0 | 0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984 |

PL-0 chưa dùng ba thư viện Excel lúc chạy. Các lát sau chỉ được dùng đúng
bản đã ghim. pytest là công cụ test ngoài gói. Không tải mạng ở PL-0.
Mọi bytes và SHA-256 nguyên trạng của toàn gói (kể cả tài liệu, schema,
requirements.lock, kieu.py, loi.py) nằm trong sql/kiem_ke.json; trừ chính
kiểm kê để tránh băm tự tham chiếu. Tính lại bằng tests/kiem_bam_goi.py.

Hai schema được chép nguyên byte nguồn tại worktree Windows (CRLF), khóa
`-text` trong .gitattributes để Git không đổi bytes khi checkout. Nguồn
`_chung/contract/` chưa khóa xuống dòng nên test so SHA nguồn sau khi chỉ
chuẩn hóa CRLF→LF trong RAM, đúng cả Windows/Linux; không sửa nguồn.
Kiểm kê sql/kiem_ke.json luôn so SHA-256 bytes nguyên trạng, không chuẩn hóa.

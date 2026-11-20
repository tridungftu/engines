# Nguồn và giấy phép — 0.1.0, PL-0…PL-9, 21/11/2026

Trạng thái hiện hành: PL-0…PL-8 đã có đủ năm năng lực chạy thật; PL-9 bổ sung
kiểm phát hành, mô phỏng và đo. PL-9A/PL-9B chạy riêng; kết quả của hai việc
đó cần lead ghép và chạy lại kiểm chung trước phát hành. Không dùng dữ liệu thật.
Mã mới nội bộ theo PHIEU-ENGINE-e_phan_luong.md và GIAO-CODEX-e_phan_luong.md;
kieu.py và loi.py do lead quản lý. Các ghi chú PL-0 là lịch sử dựng khung.

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
| [openpyxl](https://pypi.org/project/openpyxl/3.1.5/) | 3.1.5 / MIT | 5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2 |
| [et_xmlfile](https://pypi.org/project/et-xmlfile/2.0.0/) | 2.0.0 / MIT | 7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa |
| [defusedxml](https://pypi.org/project/defusedxml/0.7.1/) | 0.7.1 / PSF License | a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61 |
| kho_tri_thuc_sdk (nội bộ, cài riêng --no-deps) | 2.2.0 | 0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984 |

PL-6 đọc Excel bằng openpyxl/defusedxml; PL-8 ghi Excel trong RAM bằng openpyxl/
et_xmlfile. Chỉ dùng đúng bản/hash đã ghim; requirements.lock giữ nguyên.
Tên wheel: openpyxl-3.1.5-py2.py3-none-any.whl,
et_xmlfile-2.0.0-py3-none-any.whl, defusedxml-0.7.1-py2.py3-none-any.whl.
Hash wheel kế thừa bảng đã đối chiếu metadata PyPI của e_kiem_excel;
PL-9C không tải mạng hay thêm dependency. SDK cài riêng --no-deps từ wheel
nội bộ; cryptography/jsonschema thuộc phần module SDK, không phải runtime
engine. pytest và jsonschema chỉ là công cụ test ngoài gói.

Môi trường PL-9C: tạo .venv riêng, cài SDK offline; chép ba thư viện runtime
từ site-packages của venv PL-8 do không có kho wheel runtime tại worktree.
Đã kiểm SHA-256/số bytes mọi mục có hash trong RECORD của ba thư viện trước
khi chép (196/11/17 tệp). Đây là kiểm tệp đã cài, không thay cho kiểm wheel
bằng --require-hashes của quy trình máy sạch. Công cụ pytest chép riêng,
đối chiếu RECORD các tệp thư viện; không chép console script.
Mọi bytes và SHA-256 nguyên trạng của toàn gói (kể cả tài liệu, schema,
requirements.lock, kieu.py, loi.py) nằm trong sql/kiem_ke.json; trừ chính
kiểm kê để tránh băm tự tham chiếu. Tính lại bằng tests/kiem_bam_goi.py.

Hai schema được chép nguyên byte nguồn tại worktree Windows (CRLF), khóa
`-text` trong .gitattributes để Git không đổi bytes khi checkout. Nguồn
`_chung/contract/` chưa khóa xuống dòng nên test so SHA nguồn sau khi chỉ
chuẩn hóa CRLF→LF trong RAM, đúng cả Windows/Linux; không sửa nguồn.
Kiểm kê sql/kiem_ke.json luôn so SHA-256 bytes nguyên trạng, không chuẩn hóa.

## Nguồn hiện hành theo lát

| Lát | Nguồn / giấy phép | Phần dùng trong gói |
|---|---|---|
| PL-0 | API v1, SDK 2.2.0, mẫu e_demo_ngan / nội bộ | Phiếu, cổng SDK, SQL sáu bảng, ngăn và thử lại CAS |
| PL-0B | Script sinh DEMO nội bộ | Dữ liệu giả, ví dụ chạy thử và đầu vào AI giả |
| PL-1 | Phiếu §4–§5 / nội bộ; bo_nhom.py, chuan_hoa.py của e_kiem_excel / nội bộ | Decimal, JSON, ngưỡng, chia nhỏ; chép-sửa matcher từ khóa, không import engine khác |
| PL-2 | Phiếu §4.3–§4.4 / nội bộ; thư viện chuẩn Python | Clopper-Pearson, bậc thang, cờ, SHA-256 chọn mẫu, ngăn lượt |
| PL-3 | Phiếu §5.3 và Q1–Q7 / nội bộ | Kết quả kiểm, sửa loại, CAS, cập nhật bậc |
| PL-4 | Phiếu §4.5, Q8–Q11 / nội bộ | Hồ sơ gộp, băm đối tác, chốt tháng, chống cộng lại cùng việc |
| PL-5 | Schema _chung/contract, hợp đồng AI và phiếu §4.2 / nội bộ | Chuẩn bị/hậu kiểm Local AI, tham chiếu tệp và băm |
| PL-6 | e_kiem_excel/nhan_dien.py / nội bộ; openpyxl MIT, defusedxml PSF | Chép-sửa trần ZIP/XML, đọc Excel/CSV theo khuôn cột |
| PL-7 | Hợp đồng hoa_don.doc_xml@2, doc_zip@1 / nội bộ | Ánh xạ hóa đơn thành lô; không gọi engine Hóa đơn |
| PL-8 | Phiếu §5.5 / nội bộ; openpyxl MIT, et_xmlfile MIT | JSON/Excel trong RAM, màn Admin chỉ đọc (chờ CC-5) |
| PL-9 | Mẫu e_kiem_excel/tests/kiem_may_sach.sh, KIEM-MAY-SACH.cmd; _chung/cong-cu/dong_goi.py / nội bộ | Kiểm sạch offline, ZIP tất định và kiểm kê; mô phỏng/hiệu năng do PL-9A/PL-9B bàn giao |

Không chuyển mã nguồn cũ ngoài các phần tham khảo nêu trên. Mã mới/schema/
tài liệu DEMO do dự án tạo theo giấy phép nội bộ; thư viện bên ngoài giữ
giấy phép đã ghi trong bảng, không đưa site-packages hay wheel vào gói.
Mọi kiểm trước nối Core thật đều ghi: đã kiểm bằng Core giả (CoreGia).

ZIP thử dùng bytes worktree và chính hàm kiểm/tạo ZIP của dong_goi.py,
ghi ở thư mục tạm ngoài repo. CLI dong_goi.py chỉ đọc bytes đã commit;
lead phải đóng lại từ commit sau khi ghép PL-9, không dùng HEAD cũ để
đại diện tài liệu chưa commit. Không commit ZIP. SHA-256 mọi tệp gói nằm
ở sql/kiem_ke.json, tính bằng tests/kiem_bam_goi.py --cap-nhat, trừ chính
kiểm kê để tránh tự tham chiếu; không tạo bảng băm cạnh tranh trong tài liệu.

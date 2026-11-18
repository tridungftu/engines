# Nguồn và giấy phép — EX-0, 18/11/2026

Chỉ dùng dữ liệu DEMO giả. Không chuyển thuật toán từ `ma-nguon/` ở EX-0.

| Nguồn | Phiên bản / giấy phép | Phần dùng / SHA-256 wheel |
|---|---|---|
| [openpyxl trên PyPI](https://pypi.org/project/openpyxl/3.1.5/) | 3.1.5 / MIT | Nạp hai workbook trong phép đo; `5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2` |
| [et_xmlfile trên PyPI](https://pypi.org/project/et-xmlfile/2.0.0/) | 2.0.0 / MIT | Dependency openpyxl; `7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa` |
| [defusedxml trên PyPI](https://pypi.org/project/defusedxml/0.7.1/) | 0.7.1 / PSF License | openpyxl tự chọn bộ phân tích chống thực thể; `a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61` |
| SDK trong `docs/goi-gui-engine/sdk-2.2.0/` | 2.2.0 / nội bộ | `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` |

Tên wheel: `openpyxl-3.1.5-py2.py3-none-any.whl`,
`et_xmlfile-2.0.0-py3-none-any.whl`, `defusedxml-0.7.1-py2.py3-none-any.whl`.
Metadata nguồn lấy từ API JSON PyPI theo đúng phiên bản; wheel tải qua mirror
`https://mirrors.aliyun.com/pypi/` vì máy không tải được từ files.pythonhosted.org.
Mỗi wheel đã đối chiếu SHA-256 với metadata PyPI trước khi cài offline.
Wheel dùng cho test nằm ngoài gói, trong `.venv/banh/`, không đưa vào git.

Khung tham khảo trong repo engines, commit `0e759eff098979891720c8a057c6a5fd03b25ddb`
được phiếu engine ghim (nội bộ):

- `docs/goi-gui-engine/sdk-2.2.0/engine-demo/e_demo_doc_tep/`: bố cục, cổng nhận `tep`;
  bỏ hoàn toàn nhánh import Core trong mẫu.
- `e_hoa_don/goi/e_hoa_don/e_hoa_don/chay.py`: mẫu `_ghi()` chỉ ghi mã cố định,
  bọc lỗi giới hạn và đọc tệp có trần.
- `kho_tri_thuc_sdk/engine.py` trong wheel đã ghim: đối chiếu `_lam()` để bọc
  chuẩn hóa MIME tại cổng; không chép lại vòng xử lý và không sửa SDK.
- `e_hoa_don/tests/`: ý tưởng AST/import độc lập, CoreGia, cách ly test, cài sạch.
- `e_ocr/goi/e_ocr/requirements.lock`: cú pháp ghim wheel có hash.

Mã tham chiếu nghiệp vụ chỉ đọc, repo `tridungftu/review_xaydung`, commit
`1bed645ed56a36a59995afe1617af9dec83b8d82` (giấy phép nội bộ theo `ma-nguon/NGUON.md`):
`toan_ven.py` SHA-256 `a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023`;
`master_hd.py` SHA-256 `7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124`.
EX-1…EX-4 mới chuyển các phần được phiếu cho phép; EX-0 chỉ đọc điều kiện K1–K8
để cài dấu hiệu DEMO. Script XML và bộ chặn là mã mới nội bộ.

SHA-256 fixture ở `tests/demo/bam-fixture.json` ngoài gói; sinh lại bằng
`python -B e_kiem_excel/tests/demo/sinh_demo.py`. Kiểm kê SHA mọi tệp gói thực hiện EX-6.

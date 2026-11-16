# Nguồn tham chiếu — `e_kiem_excel/ma-nguon/` (CHỈ ĐỌC)

Hai tệp dưới đây chép **nguyên trạng** từ repo công khai [`tridungftu/review_xaydung`](https://github.com/tridungftu/review_xaydung), commit `1bed645ed56a36a59995afe1617af9dec83b8d82` (05/10/2026), ngày chép 16/11/2026 (Claude, lead).

| Tệp | Dòng | SHA-256 |
|---|---:|---|
| `toan_ven.py` | 887 | `a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023` |
| `master_hd.py` | 1234 | `7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124` |

**Quy tắc dùng:**
- **Không sửa, không xóa** hai tệp này. Mã engine chép phần cần dùng vào `goi/e_kiem_excel/e_kiem_excel/` theo bảng chuyển ở `docs/PHIEU-ENGINE-e_kiem_excel.md` §3.1–3.2, rồi sửa ở bản chép.
- Hai tệp chỉ dùng trong `tests/` để so kết quả engine với mã gốc (`python toan_ven.py <file DEMO>`). `master_hd.py` có import `urllib.request`, `subprocess` cho phần trích hợp đồng, nhưng chỉ import, không gọi; **tuyệt đối không đưa vào `goi/`**.
- Chạy được chỉ với `openpyxl` (không cần `python-docx`, `pdfplumber`).
- Test phải kiểm SHA-256 hai tệp đúng như bảng trên trước khi so.
- Giấy phép: phần mềm nội bộ của tập đoàn, dùng nội bộ.

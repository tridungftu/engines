# D:\Claude\Engines — các project engine

*Tách khỏi Core ngày 08/11/2026.* Mỗi engine nằm trong một thư mục riêng và là **một project riêng**. Mọi engine dùng chung **một cổng gắn vào Core: API, SDK và webhook thống nhất**.

**Đọc theo thứ tự:**
1. `_chung\docs\YEU-CAU-CHUNG-ENGINE.md`: yêu cầu bắt buộc cho mọi engine, và lý do engine từng nằm trong Core.
2. `<engine>\CLAUDE.md`
3. `<engine>\docs\YEU-CAU-VA-HIEN-TRANG.md`
4. `<engine>\docs\VIEC.md`

| Thư mục | Engine | Hiện trạng tóm tắt (08/11) | Quyết định của Anh |
|---|---|---|---|
| `e_hoi_ai\` | Hỏi AI | Lõi bản 1 (chỉ Local) đã gộp, kiểm bằng mock; chưa thử model thật; màn chạy thử và màn Cổng Local còn nằm trong Core | Đã có quyết định cuối 06/11 |
| `e_ocr\` | Nhận dạng văn bản | Đọc lớp chữ ABBYY, trích vùng, chọn nguồn, cầu nối HTTPS, "chưa rõ" bền: đã kiểm bằng mock; chưa nối ABBYY thật | Đã có quyết định cuối 06/11 |
| `e_mask\` | Che định danh | Che và mở che văn bản, kho bí danh, vòng nhận việc: đã kiểm bằng mock; chưa có che tệp Word/Excel và màn duyệt | Đã có quyết định cuối 06/11 |
| `e_trich_xuat\` | Trích thông tin hợp đồng | Mới đóng gói; phiếu lập lại (16 lát, 53 giờ công ước tính) chờ duyệt | Đã có quyết định cuối 07/11 |
| `e_hoa_don\` | Hóa đơn điện tử | Đọc XML ✅; ZIP, bảng kê, tải chưa công bố; còn 9 lát, 29 giờ công ước tính | **Chưa có quyết định cuối** |
| `e_tra_cuu\` | Tra cứu tài liệu (hỏi đáp 3 tầng) | Chưa có mã; đặc tả TL 56 | Đã chốt QĐ-1 đến QĐ-4 |
| `e_doi_chieu\` | Đối chiếu bản ký | Chưa có mã; đặc tả TL 57 | Đã chốt 5 câu |
| `_chung\` | Tài liệu và mã tham chiếu chung | `docs\`: yêu cầu chung, phiếu nối engine thật, khảo sát kênh, phiếu chuỗi, kế hoạch đóng gói. `tham-chieu-cong-hien-tai\`: bản sao mã cổng engine hiện có trong Core (kênh, SDK, khởi động, nạp, chuỗi). `du_kien.json`: danh sách 5 engine dự kiến (trước đây nằm trong Core) | — |

**Thư mục con của mỗi engine có mã:**
- `ma-nguon\`: mã engine.
- `shim-kho_tri_thuc\`: shim đường cũ.
- `tests-tu-core\`: test của engine từng nằm trong Core.
- `tu-core-cu\`: mã, test, công cụ thế hệ cũ, và `phia-core\` (bản sao mã phía Core riêng cho engine).
- `docs\`

**Lưu ý:**
- Repo gốc vẫn còn nguyên tại `D:\Claude\Phan mem ho tro ke toan\Phần mềm kho tri thức` (nhánh `hop-nhat-20261023`).
- Mã Core lưu tại `D:\Claude\Core\ma-nguon-core` (commit `755edd10`).
- SDK để đóng gói engine: `D:\Claude\Core\goi-san-sang\sdk-phat-hanh\` (1.5.0, 1.5.1).

**MASK-3J chưa thể bật chỉ bằng cách truyền `dich_vu_mask`**. Nguồn còn thiếu provider tài liệu, hồ sơ/khởi chạy engine và cơ chế retention đầy đủ. Đây là kết luận từ mã nguồn; chưa xác minh runtime DEMO.

1. **`DichVuEngine` đã có tại composition root.** Biến `engine` được dựng khi đủ pins, loại việc, runtime và KT tại [chay_core.py:625](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/chay_core.py:625>), rồi truyền cho dịch vụ engine tại `:646`; chưa truyền `DichVuChayThuMask` tại `:641–649`. Nên dùng chung instance này.

2. **Văn bản nhập hiện chưa được lưu bởi route H.** Route chỉ gọi provider `chuan_bi`, trong cùng transaction, không cho provider commit ([routes_mask.py:4](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/routes_mask.py:4>), `:286`).

   Có thể tái sử dụng `tai_lieu.tao` và kho tệp Core; kho nằm cạnh tệp kết nối, dưới `kho-tep` (`chay_core.py:623`). Adapter E yêu cầu **tệp JSON UTF-8**, chứa văn bản và mã yêu cầu/lượt; `doc_dau_vao` chỉ nhận envelope/tham chiếu rồi `mo_doc(tep_id)` ([chay.py:186](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/engines/e_mask/chay.py:186>)). Provider phải dựng thêm `DauVaoEngine` và `DauVaoMask` từ nguồn tin cậy.

   **Đề xuất:** module nguồn riêng được đăng ký đầy đủ, tên tạm `mask_thu`; hành động `MASK_THU:CHAY_THU:LAP/SUA/XEM`. Capability, loại việc, phiên bản lấy từ pins; Core sinh ID tài liệu/tham chiếu và giữ nguyên tài liệu khi mở che. Không dùng chuỗi module giả: route cấm `module='core'` ([routes_mask.py:175](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/routes_mask.py:175>)); quyền Admin không thay quyền nguồn. Login cũng phải được provision scope module tương ứng (`ung_dung.py:671–694`).

   **Migration 123 đề xuất** cho tham chiếu chạy thử, owner/phiên/pháp nhân/hạn, resolver và cửa kiểm quyền. Cửa tạo tài liệu/tệp chung đã có, nhưng chưa có đối tượng nguồn chạy thử. Chú ý: upload “tệp chờ gắn” đòi kết nối rảnh ([tep.py:357](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/tep.py:357>)); không gọi nguyên trạng trong transaction H.

3. **`doc_ket_qua` có thể ghép từ cửa hiện có.** Theo luồng [cong_sdk.py:70](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/cong_sdk.py:70>): `loi.doc_viec` → `ket_qua_ids` → `loi.doc_ket_qua_sdk` → `KhoTep.mo_doc`. Kiểm lại owner/phiên, module, pháp nhân, tài liệu, quyền hiện hành và contract; đọc JSON hữu hạn trước khi trả DTO. `ban_giao_engine` là biên nhận, không chứa payload (`068_ket_qua_engine.sql:113`). ACK sau commit chưa tự kết thúc việc (`ket_qua.py:443–447`). Cần ánh xạ rõ trạng thái `interrupted`, vì route H chưa nhận trạng thái này.

4. **Đường Core DEMO mặc định chưa đủ khởi chạy/ghim `e_mask`.** `main()` không cấp pins/runtime (`chay_core.py:694`); provider hồ sơ engine thật luôn trả `None` tại [kenh_bi_mat.py:298](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/kenh_bi_mat.py:298>). Gói chưa có manifest/contract công bố; draft vẫn `dang_ky=false`, `kich_hoat=false`. Adapter E xử lý một việc đã có; còn thiếu bootstrap/vòng nhận việc và kết thúc lease. Seam G chỉ tiêm kho Mask (`kenh_module.py:950–959`). Giữ nguyên SDK; wheel 1.4.1 vẫn là candidate theo §6.3.

5. **Retention chưa hoàn chỉnh.** Hạn 8 giờ của route chỉ dọn sổ RAM. `don_bi_danh_tam` chỉ dọn một phần alias (`117_mask_duyet_cho.sql:242`); [120_mask_chot_luot.sql:122](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/.claude/worktrees/lat-mask-3i/src/kho_tri_thuc/core/sql/120_mask_chot_luot.sql:122>) còn lưu JSON mở che không có hạn. Cần migration/cửa retention riêng bao phủ input, staging, output và lượt chốt; giữ audit/biên nhận bất biến. Không dọn theo riêng phiên: alias DEMO có thể đang được yêu cầu khác dùng; tệp theo hash cũng cần đối soát tham chiếu.

**Đề xuất chia lát, mỗi lát tối đa 3 tệp:**

| Lát | Tệp/phạm vi |
|---|---|
| J1 | Migration 123 + test thuần + test PG |
| J2–J3 | Gói module nguồn: manifest/contract; migration/resolver và test tách riêng |
| J4 | Provider `chuan_bi`/đầu vào + test |
| J5 | Provider đọc kết quả + test |
| J6–J7 | Contract engine + ví dụ + test; manifest tách riêng |
| J8 | Entrypoint/vòng xử lý trong `chay.py` + test |
| J9 | Resolver hồ sơ engine + `kenh_bi_mat.py` + test |
| J10 | Bootstrap DEMO + `chay_core.py` + test |
| J11 | Migration retention + tác vụ dọn + test |
| J12 | UI/F5 và test tương ứng |

**Lead cần chốt:** module nguồn hay mở rộng toàn chuỗi hỗ trợ Admin/Core; số migration 123; hạn lưu và cơ chế dọn payload. Không nên bật trước khi các phụ thuộc này đạt.

**Bài E2E cho lead:** đăng nhập Admin → Quản lý engine → Che định danh → Chạy thử DEMO → chọn pháp nhân DEMO → che mẫu giả có tiền/ngày → mở che → F5 → mở lại màn và chạy tiếp. Theo UI hiện tại, F5 mất nội dung/mã yêu cầu trong bộ nhớ; khôi phục phiên thử cũ sẽ là phạm vi bổ sung. Thử thêm phiên khác, thu hồi quyền, giả pháp nhân thật, retry và hết hạn; xác nhận không lộ toàn văn trong log/queue/audit.

**Tệp đổi: 0; không tạo tệp, không commit.** Test trước/sau giống nhau:

| Bộ test | OK trước/sau | FAIL / ERROR / SKIP |
|---|---:|---:|
| Python HTTP/kênh/nối Mask | 68 / 68 | 0 / 0 / 0 |
| Node UI | 44 / 44 | 0 / 0 / 0 |
| Node UI nối HTTP | 21 / 21 | 0 / 0 / 0 |

Không phát sinh lỗi trong các bộ đã chạy. Chưa chạy PostgreSQL hoặc E2E trình duyệt.
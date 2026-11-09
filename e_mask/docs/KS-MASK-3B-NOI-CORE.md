**Đề xuất: Mask đi qua hàng việc chuẩn của Core; hàm che/mở là bộ xử lý nội bộ. Kho PostgreSQL nằm phía Core, chỉ truy cập qua SECURITY DEFINER. Hiện còn thiếu cơ chế bảo đảm giao dịch trọn lượt qua kênh engine.**

Quy ước đường dẫn: `C = src/kho_tri_thuc/core`, `E = engines/e_mask`, `T = tests`. Các tên mới dưới đây là **đề xuất**, chưa tạo tệp.

**1. Đường gọi hiện có**

- Module → `engine.gui_viec` → Core trả `queued` → E1 cấp `SDKEngine` → `doc_dau_vao` → xử lý → `ghi_ket_qua`/ACK. Đầu vào hàng việc là **tham chiếu**, không phải toàn văn. Căn cứ: `C/cong_sdk.py:894`, `src/kho_tri_thuc/sdk_core/engine_module.py:22`.
- `xu_ly_function` OCR là hàm nội bộ được `xu_ly_viec` gọi, **chưa phải API engine đồng bộ**: `engines/e_ocr/chay.py:59`, `:89`.
- Mask nên thêm bộ xử lý tương tự, dùng lại `che`/`mo_che`; launcher nguồn ngoài và vòng đời khóa/danh mục hiện đã lệch quyết định mới: `E/chay.py:61`, `E/vong_doi.py:5`, `docs/47-core/g3/QUYET-DINH-CUOI-e_mask.md:135`.

Không nên coi “import hàm vào Core rồi gọi đồng bộ” là đường chuẩn đã có: chuẩn yêu cầu engine chạy tiến trình riêng (`CHUAN-CORE-SDK-v1.0.md:44`).

**2. Kho PostgreSQL và giao diện SQL**

Engine **không có kết nối CSDL riêng**; Core login cũng không được đọc trực tiếp bảng Mask. Căn cứ: `CHUAN-CORE-SDK-v1.0.md:69`, `C/sql/113_mask_dinh_danh.sql:62`, `:235`.

Đề xuất các hàm dưới đây nhận thêm `ctx` gồm mã phiên/ủy nhiệm, module, pháp nhân, hành động, việc/thế hệ lease; **SQL xác minh lại**, suy người gửi và `la_demo`, kiểm tài liệu.

| Hàm đề xuất | Vào nghiệp vụ → Ra |
|---|---|
| `mask.cap_ma_yeu_cau` | tài liệu → UUID yêu cầu |
| `mask.liet_ke_dinh_danh` | → danh mục chính thức/tạm đúng vùng |
| `mask.tra_bi_danh` | giá trị chuẩn → bản ghi hoặc rỗng |
| `mask.ghi_cho_duyet` | yêu cầu, cụm, nhóm, bí danh dự kiến → bản ghi có thẩm quyền, cờ vừa thêm |
| `mask.doc_yeu_cau` | mã yêu cầu → trạng thái; sai chủ/vùng/đã đóng thì từ chối |
| `mask.ghi_bi_danh_da_dung` | yêu cầu, danh sách bí danh → xác nhận giữ tham chiếu |
| `mask.tra_dinh_danh` | yêu cầu, bí danh chuẩn → giá trị gốc hoặc rỗng |
| `mask.dong_yeu_cau` | yêu cầu → xác nhận đóng |

Chỉ Core được gọi; danh mục/giá trị gốc chỉ đi trong kênh xử lý nội bộ. GUC phải đặt **trong từng DEFINER sau xác minh**, rồi khôi phục. Mẫu đã có ở `C/sql/117_mask_duyet_cho.sql:106`, `:142`. Cửa cấp mã cũ vẫn tin `p_la_demo`; cần thu hồi quyền gọi chữ ký cũ và thay bằng cửa có phiên (`113_mask_dinh_danh.sql:195`).

Hai điểm bắt buộc:

- **Đếm gặp lại:** chỉ UPSERT chưa đủ. Lõi hiện chỉ gọi `ghi_cho_duyet` khi tra không thấy; phải ghi nhận cả cụm tạm đã tồn tại, tăng nguyên tử và chống đếm lại khi retry. Căn cứ: `E/che_van_ban.py:490`, `117_mask_duyet_cho.sql:74`.
- **Giao dịch:** E1 chưa có thao tác kho; mỗi call mở transaction riêng (`C/kenh_engine.py:653`). Đề xuất **snapshot có phiên bản + nhật ký thay đổi tạm + `mask.chot_luot` nguyên tử** phía Core; xung đột thì không công bố kết quả. Không biến từng phương thức `Kho` thành các RPC commit độc lập.

**3. Chia lát đề xuất — tối đa 3 tệp/lát**

| Lát | Tệp dự kiến |
|---|---|
| A — xác minh phiên, khép cửa cấp mã cũ | `C/sql/118_mask_phien.sql`; `T/test_mask_phien.py` |
| B — các cửa kho DEFINER | `C/sql/119_mask_kho.sql`; `C/kho_mask.py`; `T/test_mask_kho.py` |
| C — ghi nhận gặp lại, đồng bộ RAM | `E/che_van_ban.py`; `E/kho_bo_nho.py`; `E/tests/test_che_van_ban.py` |
| D — snapshot/chốt nguyên tử, chống phát lại | `C/sql/120_mask_chot_luot.sql`; `C/mask.py`; `T/test_mask_chot_luot.py` |
| E — adapter function/việc | `E/chay.py`; `E/kho_qua_core.py`; `E/tests/test_noi_core.py` |
| F — bàn giao riêng, kiểm envelope nội bộ | `C/kenh_engine.py`; `C/contract/ky_thuat.json`; `T/test_mask_kenh.py` |
| G — ghép provider/binding | `C/chay_core.py`; `C/kenh_module.py`; `T/test_mask_noi.py` |
| H — route Admin | `C/routes_mask.py`; `C/ung_dung.py`; `T/test_mask_http.py` |
| I — nối DEMO | `C/ui/chay_thu_mask.js`; `C/ui/quan_tri.js`; `T/ui_chay_thu_mask.cjs` |

Schema kỹ thuật cần có: snapshot, thay đổi/chốt lượt, phản hồi bị chặn với văn bản `null`, vị trí dạng object và trạng thái mở che. **Không ép vào `noi_dung_da_che.v1` cũ**, vốn còn bắt buộc lượt/hạn/danh mục (`C/contract/ky_thuat.json:560`). Tám contract công bố vẫn thuộc **lát 6**, tên chờ duyệt; không đổi version SDK.

**4. Nối màn DEMO**

Đề xuất route mới:

- `POST /api/v1/quan-tri/engine/e_mask/chay-thu/che-van-ban`
- `POST /api/v1/quan-tri/engine/e_mask/chay-thu/mo-che-van-ban`
- `GET /api/v1/quan-tri/engine/e_mask/chay-thu/{viec_id}`

POST trả 202; adapter `api_mask` đợi kết quả rồi trả object cho màn. Mỗi route kiểm lại Admin, phiên, vùng DEMO và quyền sở hữu việc; Core tự gắn danh tính/tài liệu/nguồn.

Ở `lat/mask-5`, màn mới có seam tiêm (`chay_thu_mask.js:2`). Cần đồng bộ:

- Chấp nhận `van_ban_da_che=null` khi bị chặn.
- Vị trí là object, không phải mảng.
- Dùng `van_ban_da_mo_che`, `trang_thai_ma_yeu_cau`, `mo_day_du`.
- Chỉ hiển thị bản che khi cả ba điều kiện kiểm đều đạt.

Đối chiếu: nhánh `lat/mask-5`, `chay_thu_mask.js:163`, `:183`; lõi `E/che_van_ban.py:521`, `:631`.

**5. Rủi ro và kiểm chứng**

- Không đưa toàn văn, cụm gốc, mã yêu cầu hoặc snapshot vào metadata hàng việc, audit, khóa dedupe, lỗi driver hay Cloud. `from None` không thay thế việc kiểm soát nơi ghi traceback.
- Kết quả mở che chứa định danh: phải kiểm lại quyền khi đọc kết quả; không dựa riêng vào quyền gửi việc.
- Không dọn bí danh khi yêu cầu còn xử lý; phối hợp khóa với cửa dọn 117 (`117_mask_duyet_cho.sql:214`).
- Trần JSON kênh là **1 MiB**, có thể nhỏ hơn 500.000 ký tự UTF-8; cần dùng luồng có kiểm quyền, không tự nâng trần (`sdk_core/kenh_khung.py:33`).

**Test trước/sau:** bộ thuần/mock phù hợp sandbox đều **89/0/0/0** — ok/fail/error/skip. Lượt thăm dò ban đầu **84/0/1/0**: một fixture cần thư mục tạm, bị sandbox chỉ đọc chặn; không chạy lại ca đó. PostgreSQL và UI đầu-cuối chưa kiểm.

Tôi không sửa/tạo tệp hay commit. Hai tệp 117/test tương ứng thay đổi ngoài phiên khảo sát. **Lead cần chốt cơ chế snapshot/chốt nguyên tử, cách đếm lần gặp và route Admin trước khi giao code; số migration 118–120 cần giữ chỗ khi triển khai.**
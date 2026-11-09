# Phiếu nối Core với engine chạy thật

Ngày 08/11/2026 · **Trình Anh chốt trước khi code phần CSDL (CD-091).** Đề xuất bổ sung hồ sơ cài engine và cửa SQL tin cậy, sau đó nối các khâu đã có; lấy Hỏi AI làm ca nghiệm thu đầu, OCR/Mask dùng cùng đường.

Căn cứ: [khảo sát K1–K5](KS-KENH-ENGINE-THAT.md) (30–48 giờ công ước tính) và `var/lead-codex/k1-dung-0841.md` (đã đọc tại thư mục dự án chính; tệp không có trong worktree này). Đối chiếu mã tại HEAD `31ee0522`. Đây là kế hoạch, chưa phải bằng chứng chạy thật hoặc lệnh mở rộng whitelist của worker.

## 1. Anh thấy gì khi xong

Trên **Core thử**, đăng nhập quản trị → mở **Hỏi AI → Chạy thử** → chọn chức năng DEMO, nhập tài liệu giả và câu hỏi → bấm chạy. Core tự khởi động engine đã cài, engine nhận việc từ hàng việc chung và gọi **máy AI Local qua cổng AI của phần mềm**; màn hình hiện trả lời, trích dẫn và lịch sử. F5 hoặc khởi động lại Core vẫn xem được kết quả; gửi lại cùng lượt không sinh kết quả trùng. Khi máy AI mất kết nối, hiện lý do và thao tác thử lại; bản 1 giữ **0 lượt Cloud**.

OCR và Mask dùng cùng cơ chế hồ sơ, khởi động, xác thực, nhận việc và bàn giao kết quả; kiểm bằng một việc DEMO của từng engine. Giao diện giữ tiếng Việt nghiệp vụ, ngày dd/mm/yyyy, không xưng hô; mã kỹ thuật chỉ trong thông tin quản trị/chi tiết hỗ trợ thu gọn theo CD-102.

## 2. Đường chạy đang đứt ở đâu

Quy ước đường dẫn: **C** = `src/kho_tri_thuc/core`, **A** = `engines/e_hoi_ai`, **T** = `tests`. Các vị trí sau là căn cứ đọc mã; lỗi binding/proof chưa được tái hiện bằng phiên chạy thật trong lượt khảo sát này.

| Điểm đứt | Căn cứ tệp:dòng và ý nghĩa |
|---|---|
| CLI chưa cấp composition engine | `C/chay_core.py:626`, `:646`, `:711`: cần pins, binding, runtime và kiểm gói; đường CLI mặc định chưa cấp đủ. `C/kenh_bi_mat.py:298` trả `None` cho hồ sơ engine. |
| K1 thiếu nguồn lưu tin cậy | `C/sql/005_dang_ky.sql:62`, `C/sql/016_so_cong.sql:39`: registry/hồ sơ vận hành chưa lưu đủ snapshot pins, binding và ngữ cảnh quyền nhận việc tương đương hồ sơ module. `C/ho_so_chay.py:390`, `C/sql/038_ho_so_chay_engine.sql:480`: bootstrap đòi biết trước `row_version`, chưa phải cửa đọc composition active. |
| Không thể chữa bằng SELECT trực tiếp | `C/sql/016_so_cong.sql:142`: FORCE RLS và thu quyền bảng, gồm `engine_ho_so_chay`. Cửa tạo hồ sơ được SQL `025_ap_goi.sql:78` đổi thành login Core + phiên Admin, nhưng danh sách trường tại `:97` vẫn chỉ là vận hành, chưa có composition. |
| Đã xếp việc chưa có nghĩa đã chạy | `C/routes_quan_tri.py:1630`, `C/sql/129_ai_chay_thu.sql:286`, `:341`: POST chọn engine/hồ sơ rồi xếp việc. `C/kenh_module.py:906` đòi caller giữ context và gọi `worker.phuc_vu()`; chưa có consumer của ứng dụng nối đủ đường này. |
| Danh tính tiến trình lệch module của việc | `C/dich_vu_engine.py:280` đòi owner là engine; `C/kenh_module.py:961` đưa owner vào ngữ cảnh, trong khi `C/kenh_engine.py:589` đối chiếu với module nghiệp vụ (`core` cho chạy thử). `C/kenh_module.py:971` còn thiếu `loai_con='engine'`; mặc định tại `src/kho_tri_thuc/sdk_core/kenh_khung.py:578` là `module`. |
| Launcher, Local và nhật ký chưa ghép đủ | `A/chay.py:302` còn cần callbacks/settings/schema/writer; `A/engine.json:47` và `C/routes_quan_tri.py:625` chưa thống nhất với runtime `enabled/url/model`. `A/nhat_ky.py:170` cần snapshot nhật ký nhưng đầu vào v2 tại `A/chay.py:95` khóa đúng bốn trường. |

Đã có phần dùng lại: `TienTrinhCore` spawn/bootstrap/socket/readiness (`C/tien_trinh.py:351`); dịch vụ và kênh nhận việc (`C/dich_vu_engine.py:376`, `C/kenh_engine.py:488`); commit trước ACK và phát lại ACK (`C/kenh_engine.py:969`, `:1032`). Test `T/test_ai_chay_thu_noi.py:59`, `:109`, `:136` dùng Local/runtime/hàng việc giả, chưa chứng minh CLI tự nối engine thật.

## 3. Thiết kế đề xuất để chốt

**Bộ cài lưu một snapshot đầy đủ, có phiên bản.** Sau khi kiểm gói, ghim danh tính/băm gói, adapter, capability, contract đầu vào/đầu ra + phiên bản/băm schema, hồ sơ tiến trình, bản cấu hình `row_version`, binding loại việc và mẫu ngữ cảnh quyền được Core cho phép. Lưu, đối chiếu registry và kích hoạt nguyên tử; có CAS/chống ghi trùng, nhật ký và thế hệ active. Hồ sơ cũ thiếu thông tin phải được bộ cài kiểm và ghim lại; không tự chọn contract mới nhất hoặc tự cấp quyền.

Mẫu dùng lại là `C/ho_so_module.py:393` (`ghim_launch`, pins tại `:407`), SQL `102_cd060_launch.sql:47` (đọc active), `:62` (ghim có CAS), `109_dai_cong_module.sql:48` (cấp cổng), `116_crm_nguon_launch.sql:13` và `125_crm_kiem_gan_launch.sql:12` (quyền con theo hành động). **Dùng lại nguyên tắc, không sao chép quyền CRM sang engine.** Binding phải phân biệt owner tiến trình với module/chức năng của việc; quyền nhận việc bị giới hạn theo loại việc, hành động và pháp nhân. Snapshot chỉ lưu chính sách/tham chiếu; Core xác minh người khởi tạo, cấp phiên/ủy nhiệm hợp lệ cho từng lượt, không lưu token hay giá trị bí mật trong snapshot. Không suy quyền từ chuỗi `quyen` trong manifest/request (`C/ho_so_module.py:362`).

**Migration thêm cửa SQL đọc composition active chỉ cho login Core.** Hàm `SECURITY DEFINER`, `search_path` khóa, tên bảng đầy đủ; kiểm `session_user`, thu quyền PUBLIC và chỉ cấp EXECUTE cho login Core. Hàm tự tìm đúng thế hệ active, trả snapshot cùng bản cấu hình đã ghim và tham chiếu cần thiết; giữ RLS/quyền bảng hiện tại. Cửa ghi snapshot mới chỉ cho login cài đặt tin cậy, kiểm bằng chứng gói/quyền và audit; quyền Core + Admin tạo hồ sơ vận hành hiện có không tự thành quyền ghim pins. Bước áp gói engine trong `kich_hoat.py` gọi `cai_engine.py` sau kiểm snapshot, trước commit/kích hoạt; không mở provisioning trong HTTP. Lead kiểm owner, ACL và các ca giả mạo login bằng PostgreSQL.

**Resolver `ho_so_engine.py`** đọc cửa trên trong transaction ngắn, kiểm lại gói/registry/contract/kiểm gói, dựng `GhimEngine`, `GhimLoaiViec`, `HoSoEngine`, hàng việc/kho/thu hồi và provider runtime; nối vào provider hiện có và CLI. Bộ cài/đổi cấu hình phải làm mới composition có CAS; nhận việc kiểm lại thế hệ/bản hồ sơ, drain lượt cũ trước chuyển bản, không giữ transaction khi gọi engine/Local AI.

**Các khâu tiếp theo:** K2 dùng launcher con đang làm, thực thi entrypoint đã ghim, cấp bootstrap/credential/callbacks và readiness thật. K3 ánh xạ một cấu hình Local từ schema gói → màn quản trị → runtime; đổi cấu hình dùng cửa Core có kiểm quyền/CAS để lập bản composition mới từ pins bất biến, không được sửa pins/quyền của bộ cài. K4 ghép writer bền theo lượt, giữ đầu vào v2 hợp lệ, commit trước ACK, retry không ghi trùng và lịch sử sau restart. K5 chạy consumer từ ứng dụng, quản lý lease/drain/restart, sửa binding và proof `loai_con='engine'`. OCR/Mask lắp adapter vào cùng launcher/resolver/consumer sau khi gói và contract của từng engine đủ điều kiện.

Giữ phiên bản SDK engine đang ghim; **wheel 1.4.1 chỉ candidate, không phát hành/ghim mới**, theo [kế hoạch G3-GOI §6.3](KE-HOACH-G3-GOI.md#63-điều-kiện-từ-lát-04-opus-review-05112026). Không thêm thư viện; mọi AI đi qua cổng chung của phần mềm.

## 4. Toàn bộ lát, phụ thuộc và ước giờ

Danh sách dưới đây là **phạm vi tệp dự kiến để lead khóa khi giao**, không cho phép sửa trong lát tài liệu này. **N** = tệp mới; không có N là sửa tệp hiện có. Mỗi lát tối đa 3–5 tệp, đã tính test. Migration lấy **số kế tiếp lúc giao** (worktree hiện dùng tới **130**), không giữ chỗ số 131 hay sửa migration lịch sử.

| Lát / kết quả bàn giao | Tệp dự kiến | Phụ thuộc | Giờ công **ước tính** |
|---|---|---|---:|
| **K1a — CSDL composition:** snapshot, active/CAS, cửa ghi/đọc và đổi bản cấu hình có quyền hẹp | **N** `C/sql/<số kế tiếp lúc giao>_engine_composition.sql`; **N** `T/test_engine_composition_sql.py`; **N** `T/test_engine_composition_pg.py` — **3** | Anh chốt thiết kế | 4–6 |
| **K1b — Bộ cài engine:** kiểm gói, lưu pins/binding/quyền, kích hoạt; có điểm gọi bộ cài thực, không chỉ helper trong test | **N** `C/cai_engine.py`; `C/kich_hoat.py`; `C/nap_engine.py`; **N** `T/test_cai_engine.py`; `T/test_g2_25.py` — **5** | K1a; dùng lại bộ kiểm/áp gói hiện có | 6–10 |
| **K1c — Resolver và CLI:** đọc active, dựng hồ sơ/hàng việc/provider, không tiêm pins thủ công | **N** `C/ho_so_engine.py`; `C/kenh_bi_mat.py`; `C/chay_core.py`; **N** `T/test_ho_so_engine.py` — **4** | K1a → K1b để kiểm tích hợp | 6–10 |
| **K2 — Launcher con:** bootstrap, entrypoint, callbacks/schema, readiness đúng gói | **N** `C/khoi_chay_engine.py`; `A/chay.py`; `A/NGUON.md`; `T/test_g3_ai_4a.py` — **4** | **Đang làm theo handoff K2**; chốt giao diện với K1c, không giao trùng | 4–6 |
| **K3 — Local thống nhất:** cấu hình quản trị vào runtime; đổi cấu hình tái lập composition qua CAS | `A/engine.json`; `C/routes_quan_tri.py`; `A/NGUON.md`; `T/test_ai_model_quan_tri.py`; `T/test_g3_ai_4a.py` — **5** | Làm schema/test song song K1/K2; kiểm ghép sau K1a–K1c/K2 | 4–6 |
| **K4 — Nhật ký bền:** writer v2, retry/ACK/lịch sử sau restart | `A/nhat_ky.py`; `A/chay.py`; `C/kenh_engine.py`; `A/NGUON.md`; `T/test_g3_ai_4a.py` — **5** | Giao diện K2 và K1c; tránh giữ chung tệp khi K2/K3 đang sửa | 6–10 |
| **K5 — Consumer/binding/proof:** ứng dụng tự phục vụ việc, lease/drain đúng | `C/kenh_module.py`; `C/kenh_engine.py`; `C/chay_core.py`; `T/test_g2_32_p1.py`; `T/test_ai_chay_thu_noi.py` — **5** | K1c + K2; ghép K3/K4 trước nghiệm thu | 6–10 |
| **K6-OCR — Lắp cùng đường:** entrypoint/readiness/adapter nhận việc OCR DEMO | `engines/e_ocr/chay.py`; `C/khoi_chay_engine.py`; `engines/e_ocr/NGUON.md`; `T/test_g3_ocr_4a.py` — **4** | K1–K5; gói OCR hợp lệ và gate backend/quyền theo phiếu OCR | 4–6 |
| **K6-Mask — Lắp cùng đường:** entrypoint/readiness/adapter nhận việc Mask DEMO | `engines/e_mask/chay.py`; `C/khoi_chay_engine.py`; `engines/e_mask/NGUON.md`; **N** `T/test_g3_mask_runtime.py` — **4** | K1–K5; gói/manifest/contract Mask hợp lệ theo phiếu Mask; thiếu thì chưa công bố sẵn sàng | 4–6 |
| **Lát 8 — Local thật:** thử model đã kê khai, mất kết nối, 0 Cloud | **N** bằng chứng JSON DEMO tại đường lead chốt; `PHIEU-ENGINE-e_hoi_ai.md`; `docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md` — **3** | K3 + máy AI được phép; dùng `tools/thu_local_ai_that.py` hiện có | 2–3 |
| **Lát 14 — Core thử Hỏi AI:** bài cuối §6, ảnh/log/thời gian thực tế | **N** báo cáo nghiệm thu Hỏi AI; **N** ảnh tổng hợp từng bước; `PHIEU-ENGINE-e_hoi_ai.md`; `docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md` — **4**; đường bằng chứng do lead chốt | K1–K5 + lát 8 | 2–3 |
| **NT-OCR — Kiểm nối OCR trên Core thử:** bài §6 áp dụng OCR | **N** báo cáo nối OCR; **N** ảnh tổng hợp từng bước; `PHIEU-ENGINE-e_ocr.md`; `docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md` — **4**; đường bằng chứng do lead chốt | K6-OCR + gate gói/backend/quyền OCR | 2–3 |
| **NT-Mask — Kiểm nối Mask trên Core thử:** bài §6 áp dụng Mask | **N** báo cáo nối Mask; **N** ảnh tổng hợp từng bước; `PHIEU-ENGINE-e_mask.md`; `docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md` — **4**; đường bằng chứng do lead chốt | K6-Mask + gate gói/contract/quyền Mask | 2–3 |

**Tổng phạm vi 52–82 giờ công, là ước tính chưa đo**, gồm nền KS 30–48 + CSDL/bộ cài 10–16 + adapter OCR/Mask 8–12 + kiểm nối OCR/Mask 4–6. Phần tới nghiệm thu Hỏi AI là **40–64 giờ**. Không cộng lại vào giờ các phiếu engine/G3-GOI; lead ghi cùng mã việc và trừ phần K2 đã làm để ra giờ còn lại. Chưa tính thời gian chờ máy/model/quyền vận hành và gate gói OCR/Mask thuộc phiếu riêng. Không hứa tổng thời gian hoàn tất cả ba engine bằng con số này.

Thứ tự: **Anh duyệt → K1a → K1b/K1c → ghép K2/K3 → K4/K5 → lát 8 + 14 Hỏi AI → K6 và kiểm OCR/Mask**. Có thể chốt giao diện/test mock song song; lead cấp lượt sửa các tệp chung, nhất là `chay_core.py`, `kenh_engine.py`, `A/chay.py`, `A/NGUON.md`. Số lát song song quyết định lúc triển khai. CSDL/quyền: test thuần/mock + review chéo; lead chạy PostgreSQL/quyền và review sâu trước gộp. Lát khác kiểm nhẹ rồi dồn kiểm đầu–cuối ở §6.

## 5. Bốn câu trình Anh chốt

1. **Ưu tiên nghiệm thu Hỏi AI trước, sau đó OCR/Mask cùng đường?** Đề xuất đồng ý; không đợi đủ ba engine mới cho xem kết quả Hỏi AI.
2. **Bổ sung migration và bộ cài lưu snapshot/binding/ngữ cảnh quyền?** Đề xuất duyệt K1a/K1b trước K1c; hồ sơ cũ được kiểm và ghim lại, không suy pins/quyền tự động.
3. **Core chỉ đọc active qua cửa SQL tin cậy, quyền theo từng việc/pháp nhân/người khởi tạo?** Đề xuất đồng ý; giữ khóa bảng/RLS, tách owner engine khỏi module nghiệp vụ, không cấp quyền đọc bảng rộng hoặc token cố định.
4. **Chấp thuận quỹ ước tính 52–82 giờ và cổng nghiệm thu §6?** Đề xuất ưu tiên phần Hỏi AI 40–64 giờ; lead cập nhật giờ còn lại sau K1a/K1b và phần K2 đã làm; giữ Local-only, SDK hiện tại, OCR/Mask theo gate riêng.

## 6. Bài test tổng thể cuối trên Core thử — CD-099

**Lead thực hiện sau khi ghép, bằng dữ liệu DEMO và phiên thật trên trình duyệt**, không thay thao tác bấm bằng gọi API. Worker không chạy PostgreSQL/server hoặc máy AI thật trong lát tài liệu này.

1. Dùng bộ cài tin cậy cài/ghim gói; khởi động Core thử theo đường mặc định, không tiêm hồ sơ/runtime giả. Đăng nhập → trang chủ → bấm Hỏi AI → Chạy thử; lưu ảnh màn và giờ bắt đầu.
2. Chọn function DEMO, nhập tài liệu giả/câu hỏi, bấm chạy; thấy đang xử lý rồi trả lời có trích dẫn. Log hỗ trợ chứng minh đúng gói/instance nhận lease → cổng AI Local trên máy AI → commit kết quả → ACK → kết thúc lease. Lưu ảnh kết quả và số lượt Cloud = 0.
3. Gửi lại cùng lượt; F5 → mở lịch sử → về trang chủ. Lead khởi động lại Core rồi vào lại bằng trình duyệt: kết quả/nhật ký còn, không ghi trùng. Kiểm lease cũ/instance cũ không nhận hoặc ghi hộ; ngắt ở sau commit/trước ACK vẫn chỉ một kết quả khi retry.
4. Tài khoản thiếu quyền/pháp nhân khác bị từ chối; phiên/ủy nhiệm hết hạn không nhận việc. Lead kiểm PG: login sai không đọc composition/ghi snapshot, không SELECT trực tiếp được bảng, đổi gói/config giữa lượt bị CAS hoặc drain an toàn.
5. Mất kết nối Local/model chưa sẵn sàng: màn báo tiếng Việt dễ hiểu, có thử lại; không rơi sang Cloud. Sau phục hồi chạy thành công. Soát tên hiển thị/ngày và việc ẩn mã kỹ thuật; lưu ảnh lỗi và phục hồi.
6. Sau K6 và gate gói/quyền của từng engine, bấm một việc OCR DEMO và một việc Mask DEMO trên màn tương ứng, nhận kết quả qua cùng hồ sơ/launcher/consumer; F5, xem lại và về trang chủ, chụp ảnh. Đây là kiểm nối dùng chung; bài đo chất lượng OCR/Mask giữ theo phiếu engine tương ứng.

Chỉ báo **SẴN SÀNG** cho engine đã chạy trọn bài áp dụng, có ảnh từng bước, log đã loại bí mật, số test đạt/fail/error/skip, phút thực tế và điểm chưa đạt. Test mock xanh hoặc POST 202 không thay bằng chứng này. Lượt lập phiếu chỉ khảo sát, viết tài liệu và chạy test thuần/mock; chưa nghiệm thu chạy thật.

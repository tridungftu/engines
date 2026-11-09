**Anh, nhận xét Opus đúng: lệnh `python -m kho_tri_thuc.core.chay_core …` hiện chưa tự nối được engine đã cài thành luồng chạy thật.** Có mã điều phối, tiến trình, kênh và ACK, nhưng thiếu phần ghép chúng; đồng thời có hai điểm không tương thích về binding và proof.

Khảo sát trên nhánh `hop-nhat-20261023`, HEAD đọc được `9bd2ad48`. Quy ước: **C** = `src/kho_tri_thuc/core`, **A** = `engines/e_hoi_ai`, **T** = `tests`.

**1. Luồng hiện có và điểm đứt**

```text
chay_core → dựng ứng dụng HTTP + bộ quản lý kênh
                 ⇢ pins / hồ sơ engine / caller nhận việc còn thiếu
DichVuEngine ← provider runtime → TienTrinhCore → tiến trình engine
                                      → bootstrap + socket + readiness
Core WorkerEngine ↔ kênh xác thực ↔ engine kéo việc
       → lease → đầu vào → Local AI trong e_hoi_ai
       → ghi kết quả → commit → ACK → kết thúc lease → GET kết quả
```

Dấu `⇢` biểu thị đoạn chưa được nối trong đường CLI mặc định.

| Bước | Implementation và giới hạn |
|---|---|
| **CLI → ứng dụng** | [`C/chay_core.py:711`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/chay_core.py:711>) gọi `dung_ung_dung`; `:723` chỉ bật scanner của manager rồi phục vụ HTTP. `main()` không cấp `ghim_engine`, `ho_so_runtime`, `loai_viec`. |
| **Dựng dịch vụ engine** | [`C/chay_core.py:626`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/chay_core.py:626>) lấy pins từ caller; `:639` thêm binding `CHAY_THU_HOI_AI` **nếu đã có pin đúng**; `:646` chỉ dựng `DichVuEngine` khi đủ pins, binding, runtime và KT. |
| **Dịch vụ → runtime** | [`C/dich_vu_engine.py:313`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/dich_vu_engine.py:313>) gọi provider để lấy controller đã sẵn sàng, rồi kiểm registry/hồ sơ/lease. **Dịch vụ này không spawn engine.** |
| **Hồ sơ → tiến trình** | [`C/kenh_module.py:913`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_module.py:913>) xin `HoSoEngine`; `:923` lấy controller, `:927` giữ lượt sử dụng. `_controller` tại `:743` dựng `TienTrinhCore`. Provider mặc định hiện trả `None`, nên đoạn này dừng ở 503. |
| **Spawn → bootstrap** | [`C/tien_trinh.py:351`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/tien_trinh.py:351>) dùng `Popen`, pipe và Windows Job; `:358` claim sổ cổng; `:375` truyền instance/generation/nonce/socket qua bootstrap; `:389` truyền bí mật; `:397` kiểm readiness, `:401` giao quyền accept cho con. Đây là cơ chế dùng lại được khi có hồ sơ/launcher đúng. |
| **Tiến trình → kênh** | [`C/kenh_module.py:970`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_module.py:970>) nối loopback và dựng `WorkerEngine`, nhận hàng việc/kho/thu hồi từ hồ sơ tại `:975`. [`C/kenh_engine.py:672`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_engine.py:672>) thực hiện xác thực rồi phục vụ kênh. |
| **Kéo việc → xử lý** | [`C/kenh_engine.py:488`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_engine.py:488>) chuyển nhận việc sang `DichVuEngine.nhan_viec`; [`C/dich_vu_engine.py:376`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/dich_vu_engine.py:376>) gọi hàng việc với instance đúng. Phía engine, [`A/chay.py:230`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/chay.py:230>) kéo lease, `:243` tạo SDK, `:260` xử lý. |
| **Kết quả → ACK** | [`A/chay.py:156`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/chay.py:156>) gửi kết quả qua SDK. [`C/kenh_engine.py:1019`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_engine.py:1019>) kiểm contract; `:1032` ra khỏi transaction trước công bố ACK; `:969` hỗ trợ phát lại ACK cùng nội dung, `:980` nhận kết thúc lease. |

Riêng **Chạy thử Hỏi AI**, POST hiện đi trực tiếp từ [`routes_quan_tri.py:1630`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/routes_quan_tri.py:1630>) vào SQL. [`129_ai_chay_thu.sql:286`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/sql/129_ai_chay_thu.sql:286>) chọn engine/hồ sơ active đúng capability v2; `:341` tạo việc `CHAY_THU_HOI_AI`. **POST 202 mới chứng minh đã xếp việc, chưa chứng minh engine được khởi chạy.**

Khi có worker đúng, [`dich_vu_engine.py:214`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/dich_vu_engine.py:214>) đọc đầu vào bằng lease, đối chiếu prompt của module đã cài và tạo yêu cầu `chi_cuc_bo=True` tại `:231`. Engine gọi `AdapterHoiAI → CongAI → Local`; [`A/hoi.py:119`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/hoi.py:119>) khóa Cloud. SQL [`129_ai_chay_thu.sql:382`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/sql/129_ai_chay_thu.sql:382>) ghi kết quả và `:390` kết thúc việc trong cùng transaction; GET tại `routes_quan_tri.py:1636` đọc lại.

Bước Hỏi AI trong **chuỗi thường** còn cần provider đầu vào riêng tại [`kenh_engine.py:530`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_engine.py:530>), rồi mới đối chiếu nguồn/prompt. Không thể suy nhánh DEMO đã đủ thì nhánh chuỗi cũng tự đủ.

**2. Những chỗ còn thiếu hoặc chỉ được ghép trong test**

| Khoảng trống | Bằng chứng cụ thể |
|---|---|
| **Chưa có resolver engine thật** | [`C/kenh_bi_mat.py:298`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_bi_mat.py:298>) luôn báo `KENH_HO_SO_ENGINE_CHUA_GHEP` và trả `None`. Tìm trong `src` không có lời gọi constructor `HoSoEngine(...)`, `HangViecCore(...)`. |
| **Chưa có consumer nối vào ứng dụng** | `su_dung_engine` yêu cầu caller giữ context và gọi `worker.phuc_vu()` tại [`kenh_module.py:909`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_module.py:909>). Trong `src` chưa có caller đó. Scanner hiện hữu không thay consumer engine. |
| **Binding tiến trình và nghiệp vụ không khớp** | [`dich_vu_engine.py:280`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/dich_vu_engine.py:280>) yêu cầu controller mang `module=e_hoi_ai`; manager tại `kenh_module.py:961` dùng chính danh tính ấy cho kênh. Nhưng [`kenh_engine.py:589`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/kenh_engine.py:589>) yêu cầu module kênh bằng module của việc — `core` với chạy thử. **Chỉ điền hồ sơ chưa giải quyết được.** |
| **Proof đang chọn sai loại con** | `kenh_module.py:971` thiếu `loai_con='engine'`; mặc định [`sdk_core/kenh_khung.py:578`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/sdk_core/kenh_khung.py:578>) là `module`, dẫn tới allowlist khác tại `:587`. Test nối tay truyền đúng loại. |
| **Thiếu adapter thực thi entrypoint con** | [`A/chay.py:302`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/chay.py:302>) cần callbacks, settings, schema và writer; chưa có `main/__main__` gọi chúng. Manifest chỉ khai module entry tại `engine.json:22`. Launcher module hiện có dùng signature khác (`C/khoi_chay_module.py:219`). |
| **Cấu hình UI ↔ manifest ↔ runtime chưa thống nhất** | [`A/engine.json:47`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/engine.json:47>) cấm khóa ngoài hai danh sách model/rule; UI dùng `local_ai.models/quy_tac/dia_chi` tại [`routes_quan_tri.py:625`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/src/kho_tri_thuc/core/routes_quan_tri.py:625>), runtime dùng `enabled/url/model`. Chưa tìm thấy mapping tương ứng. |
| **Writer bền chưa được ghép vào runtime v2** | [`A/chay.py:314`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/chay.py:314>) bắt writer có cơ chế bàn giao/retry. `BoGhiQuaCore` cần snapshot `nhat_ky_ai` tại [`A/nhat_ky.py:170`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_hoi_ai/nhat_ky.py:170>), trong khi payload v2 bắt đúng bốn khóa tại `A/chay.py:95`. Chưa có composition tương thích được chứng minh. |

Hai điểm binding/proof là kết luận từ đối chiếu mã; **chưa phải lỗi đã tái hiện bằng chạy thật** trong khảo sát này.

Test tiêu biểu [`T/test_ai_chay_thu_noi.py:59`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/tests/test_ai_chay_thu_noi.py:59>) chặn socket/Popen thật; `:77` giả Local, `:109` tiêm runtime, `:136` tự dựng hàng việc và `:145` gọi thẳng `xu_ly_viec`. [`T/test_g2_32_p1.py:59`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/tests/test_g2_32_p1.py:59>) tự cấp `HoSoEngine` giả. Những test này chưa kiểm đường CLI mặc định.

**3. Engine nào đã có bằng chứng đầu–cuối trên Core thử?**

**Chưa tìm thấy engine nào trong ba engine được hỏi có bằng chứng đạt đầy đủ.**

| Engine | Bằng chứng hiện có |
|---|---|
| **e_hoi_ai** | Lượt **07:35 ngày 08/11**, [`TRANG-THAI.md:77`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md:77>) ghi đã gộp 10a/10b nhưng còn nối kênh engine chung và thử máy AI thật. [`PHIEU-ENGINE-e_hoi_ai.md:55`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/docs/47-core/g3/PHIEU-ENGINE-e_hoi_ai.md:55>) ghi lát 8 chưa thử thật; `:56` ghi lát 14 chưa làm. |
| **e_ocr** | [`TRANG-THAI.md:83`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md:83>) ghi lượt bền đủ phía mã, còn thử ABBYY thật. [`engines/e_ocr/chay.py:176`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_ocr/chay.py:176>) vẫn là entrypoint tiêm callbacks, mặc định backend giả, readiness chưa công bố contracts. |
| **e_mask** | [`KS-MASK-3J-BAT-CHAY-THU.md:46`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/docs/47-core/g3/KS-MASK-3J-BAT-CHAY-THU.md:46>) chưa kiểm PG/E2E trình duyệt. Mã hiện tại [`engines/e_mask/chay.py:332`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/engines/e_mask/chay.py:332>) vẫn cần callbacks; `:373` readiness có `contracts=[]`. |

Các ca Core thử thành công tại [`TRANG-THAI.md:183`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/docs/46-chuyen-doi-dieu-phoi/TRANG-THAI.md:183>) và `:240` là **module CRM**, chứng minh kênh module, chưa chứng minh kênh engine.

**4. Các lát tối thiểu đề xuất**

Phạm vi dưới đây nhằm hoàn tất **Chạy thử DEMO trên Core thử**, giữ việc gọi model trong `e_hoi_ai`. Tên tệp mới là đề xuất; chưa tạo handoff hay tệp nào.

| Lát | Kết quả cần đạt | Phạm vi tệp dự kiến | Giờ công **ước tính** |
|---|---|---|---:|
| **K1 — Hồ sơ và composition** | Cấp pins, hồ sơ process, ngữ cảnh quyền nhận việc và hàng việc từ nguồn tin cậy; nối vào CLI. | `C/ho_so_engine.py` mới; `C/kenh_bi_mat.py`; `C/chay_core.py`; `T/test_ho_so_engine.py` mới — **4 tệp** | 6–10 |
| **K2 — Launcher con** | Thực thi entrypoint đã ghim; cấp bootstrap, callbacks xác thực/kênh/schema; readiness thật. | `C/khoi_chay_engine.py` mới; `A/chay.py`; `A/NGUON.md`; `T/test_g3_ai_4a.py` — **4 tệp** | 4–6 |
| **K3 — Cấu hình Local** | Thống nhất schema gói, DTO Admin và settings runtime; kiểm bằng manifest thật. | `A/engine.json`; `C/routes_quan_tri.py`; `A/NGUON.md`; `T/test_ai_model_quan_tri.py`; `T/test_g3_ai_4a.py` — **5 tệp** | 4–6 |
| **K4 — Nhật ký bền** | Ghép writer theo lượt, tương thích v2, giữ retry/ACK và lịch sử sau restart. | `A/nhat_ky.py`; `A/chay.py`; `C/kenh_engine.py`; `A/NGUON.md`; `T/test_g3_ai_4a.py` — **5 tệp** | 6–10 |
| **K5 — Consumer và binding** | Tách owner tiến trình khỏi module nghiệp vụ; sửa proof; chạy worker và quản lý drain/lease từ ứng dụng. | `C/kenh_module.py`; `C/kenh_engine.py`; `C/chay_core.py`; `T/test_g2_32_p1.py`; `T/test_ai_chay_thu_noi.py` — **5 tệp** | 6–10 |
| **Lát 8 — Local thật** | Dùng công cụ hiện có thử model, mất kết nối và không fallback Cloud. Có thể làm song song các lát nối. | JSON bằng chứng DEMO; phiếu Hỏi AI; TRANG-THAI — **3 tệp** | 2–3 |
| **Lát 14 — Core thật** | Trình duyệt → process → queue/lease → Local → commit/ACK → GET; F5/restart, lịch sử và chống ghi trùng. | Báo cáo nghiệm thu kèm liên kết ảnh/log; phiếu Hỏi AI; TRANG-THAI — **3 tệp** | 2–3 |

**Tổng sơ bộ: 30–48 giờ công**, chưa tính chờ máy/model hoặc PG toàn bộ. Dự toán một giờ của lát 14 trong phiếu là thời gian nghiệm thu sau khi đủ đường chạy; không bao gồm các khoảng trống tích hợp trên. Công cụ [`tools/thu_local_ai_that.py:8`](<D:/Claude/Phan mem ho tro ke toan/Phần mềm kho tri thức/tools/thu_local_ai_that.py:8>) cũng ghi rõ thử cổng Local chưa thay nghiệm thu Core/SDK/UI.

Đã khảo sát chỉ đọc; không sửa tệp, commit, chạy test, server, PostgreSQL hay mạng.
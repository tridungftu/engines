**nên mở rộng cổng hiện có, lưu cấu hình model trong Core và giữ Cloud khóa ở bản 1**. Không cần thêm client AI hay thư viện.

Worktree sạch, không tạo/sửa tệp, không commit. **CD-106 chưa có trong worktree**: `docs/46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md:1041` kết thúc ở CD-105; khảo sát dùng nội dung CD-106 trong handoff.

Quy ước: `A = engines/e_hoi_ai`, `C = src/kho_tri_thuc/core`, `T = tests`.

1. **Đường nối Local hiện tại**

   `CongAI._local()` → `ai_cuc_bo.ask_local()` → HTTP JSON `POST /v1/chat/completions`; hỗ trợ OpenAI-compatible, gồm Ollama/LM Studio. Địa chỉ chỉ nhận loopback, LAN hoặc Tailscale; chặn DNS, proxy và redirect (`A/lib/ai_cuc_bo.py:35,118,213`; `A/lib/cong_ai.py:1086`).

   **Model đang cố định theo một cấu hình chung** `settings.local_ai.model`, dùng cho mọi loại việc (`A/lib/cong_ai.py:952,1077`). Không ghim tên GPT-OSS/Qwen/Gemma trong engine; mặc định model rỗng, khi gọi rơi về chuỗi `"local"` (`A/lib/ai_cuc_bo.py:26,174,221`). Chưa chọn theo function.

   Core hiện có bridge nhật ký, không có API quản trị model. Runtime mặc định provider giả, readiness `contracts=[]`; chưa thể coi là nối vận hành đầy đủ (`A/chay.py:149,206`). Cloud đã bị ép tắt ở adapter và runtime (`A/hoi.py:93`; `A/chay.py:204`).

2. **Phát hiện model và loại phần mềm**

   | API | Mã hiện có | Cần bổ sung |
   |---|---|---|
   | Ollama `GET /api/tags` → `models[]` | Đọc metadata để kiểm model đã chọn | Trả toàn bộ danh sách chuẩn hóa |
   | OpenAI-compatible `GET /v1/models` → `data[].id` | Đã đọc, tìm đúng model cấu hình | Công bố danh sách cho màn quản trị |
   | LM Studio | Dùng được `/v1/models`; chưa nhận diện riêng | Probe API native để lấy loại model/trạng thái tải |

   Bằng chứng: `A/lib/ai_cuc_bo.py:171–210`. Hiện `/v1/models` phải thành công trước; `/api/tags` chỉ là kiểm bổ sung, chưa phải discovery API.

   Đề xuất probe **cùng IP/cổng đã cấu hình**, kiểm cấu trúc phản hồi: Ollama qua `/api/tags`; LM Studio qua `/api/v1/models`, tương thích bản cũ bằng `/api/v0/models`; còn lại ghi “Tương thích OpenAI”. Không suy loại phần mềm từ tên model/cổng. Danh sách tải về cũng không đồng nghĩa model đang chạy. [Ollama](https://docs.ollama.com/api/tags), [LM Studio compatible](https://lmstudio.ai/docs/developer/openai-compat/models), [native](https://lmstudio.ai/docs/developer/rest/list), [v0](https://lmstudio.ai/docs/developer/rest/endpoints).

3. **Nơi lưu và cách chọn**

   **Khuyến nghị dùng `loi.ho_so_chay_engine.cau_hinh` JSONB**: đã có schema, lịch sử, CAS và audit (`C/sql/038_ho_so_chay_engine.sql:55,71,81`; `C/ho_so_chay.py:366`). Lưu hai mảng có schema đóng:

   - Danh sách phát hiện: endpoint, loại phần mềm, ID model nguyên gốc, khả năng/trạng thái biết được, thời điểm phát hiện.
   - Quy tắc `(module, function)` → model ưu tiên và danh sách dự phòng có thứ tự.

   Chọn model còn khả dụng theo quy tắc; dùng bản cấu hình riêng từng request, tránh đổi instance chung (`A/hoi.py:88–90`). Không tự xếp chất lượng GPT-OSS/Qwen/Gemma khi chưa đo DEMO.

   **Chưa cần DDL migration** nếu dùng JSONB hiện có; cần bổ sung `cau_hinh_schema` vào manifest và phát hành phiên bản engine phù hợp. Manifest hiện chưa có schema; cùng phiên bản không được đổi schema (`A/engine.json:1`; `C/ho_so_chay.py:318`). SDK giữ nguyên.

   Metadata function hiện thiếu trong DTO (`A/lib/cong_ai.py:288`), phải nối với AI-1b; `loi.dang_ky_ham_module` là đăng ký hàm SQL, không phải danh mục function AI (`C/sql/005_dang_ky.sql:106`). Nếu chọn bảng riêng để quản lý catalog độc lập thì cần migration: **lead cấp số sau phần Mask 126/127**, không tự lấy số trống.

4. **Hai màn và route**

   Thêm hai mục **Cổng Local AI**, **Cổng Cloud AI** tại chi tiết Hỏi AI, cạnh Chạy thử DEMO (`C/ui/quan_tri.js:484,500`). Luôn hiện cả hai; Cloud chỉ đọc, thông báo “Chưa áp dụng trong bản 1”, không có thao tác bật.

   Với tiền tố `/api/v1/quan-tri/engine/e_hoi_ai`:

   - Dùng lại `GET /cau-hinh-schema`, `GET/PUT /ho-so-chay?phien_ban_du_lieu=1.2` (`C/ung_dung.py:784,809`).
   - Đề xuất `GET /local`: trạng thái/danh sách đã lưu; `POST /local/phat-hien`: phát hiện qua provider được Core cấp.
   - Cloud bản 1 không cần API bật hay gọi nhà cung cấp.

   Kiểm Admin phía server; mã kỹ thuật ẩn, ngày dd/mm/yyyy. Màn DEMO hiện chỉ mô phỏng, đã tự ghi rõ chưa nối engine (`C/ui/chay_thu_hoi_ai.js:80`).

5. **Đề xuất 4 lát — mỗi lát tối đa 3 tệp, gồm test**

   | Lát | Tệp đề xuất | Kết quả |
   |---|---|---|
   | **AI-MODEL-DO** | `A/lib/ai_cuc_bo.py`; `A/engine.json`; `T/test_ai1_local_ai_lan.py` | Discovery, chuẩn hóa catalog, schema cấu hình; test metadata hoàn toàn mock |
   | **AI-MODEL-CHON** | `A/lib/cong_ai.py`; `A/hoi.py`; `T/test_g3_ai_2.py` | Chọn theo function/context Core xác minh, dự phòng Local, không đổi cấu hình chung |
   | **AI-MAN-LOCAL** | `C/routes_quan_tri.py`; `C/ui/quan_tri.js`; `T/test_ai_model_quan_tri.py` *(đề xuất mới)* | API, phát hiện, lưu/xem cấu hình và bảng ưu tiên |
   | **AI-MAN-CLOUD** | `C/ui/quan_tri.js`; `T/ui_chay_thu_hoi_ai.cjs`; `T/g3_goi_quan_tri.cjs` | Màn Cloud khóa, kiểm điều hướng/quyền và hai màn luôn hiện |

   Theo CD-058 (`CHI-DAO-TU-ANH.md:631`), DO/CHON đi cùng MAN-LOCAL từng mốc; khung hai màn xuất hiện ngay bằng dữ liệu giả. `quan_tri.js` chỉ một worker giữ. Việc cấp provider discovery và metadata function phải ghép với chuỗi AI-1b, không tự thêm SDK/IPC.

   DEMO mock cần kiểm: ba model, danh sách rỗng/model mất, dự phòng, model remote bị chặn, cách ly hai function đồng thời, CAS/quyền/hết phiên, đọc lại cấu hình và **0 lượt Cloud**.

**Test trước/sau khảo sát:**

| Bộ test | Trước: ok/fail/error/skip | Sau |
|---|---:|---:|
| Python: `test_g3_ai_2`, `test_g3_ai_5b`, `engines.e_hoi_ai.tests.test_doc_lap` | 78/0/0/0 | 78/0/0/0 |
| Node: hai tệp UI nêu trên | 72/0/0/0 | 72/0/0/0 |
| **Tổng** | **150/0/0/0** | **150/0/0/0** |

Không lỗi mới trong phạm vi chạy; chưa kiểm máy AI thật/PG. **Lead cần chốt:** dùng JSONB hay bảng riêng, thứ tự model theo function, và phạm vi tích hợp AI-1b/phiên bản engine; đồng bộ CD-106 vào worktree trước giao code.
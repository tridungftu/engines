# Giao Codex — `e_hoi_ai` (Hỏi AI) theo SDK 2.0

*Lập 14/11/2026 (Claude, lead). Ưu tiên 1. Căn cứ: `QUYET-DINH-CUOI-e_hoi_ai.md` (06/11), chỉ đạo của Anh (khung có cả Local và Cloud; tự phát hiện, tự chọn model; máy AI có gpt-oss 20B, Qwen3 8B, Gemma qua Tailscale), `API-ENGINE-v1.md`, `_chung/docs/GIAO-CODEX-THU-TU.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`.*

## 1. Kết luận

- **8 lát, khoảng 24 giờ công (ước tính, chưa đo).** Lát AI-0 → AI-1 bắt buộc trước; AI-2, AI-3 song song sau AI-1; AI-6 làm cuối.
- Đích: gói `e_hoi_ai/goi/e_hoi_ai/` chạy bằng SDK 2.0, **chỉ Local** khi chạy thật, **0 lượt Cloud**. Cloud có khung mã và test nhưng **chưa khai trong phiếu** (bản 2: cần bí mật + Mask).
- Lõi tái dùng: `ma-nguon/lib/cong_ai.py`, `ma-nguon/lib/ai_cuc_bo.py`, `ma-nguon/dto.py`, `ma-nguon/hoi.py`, `ma-nguon/nhat_ky.py`. **Bỏ** vỏ socket cũ (`ma-nguon/chay.py`, `bi_mat.py`).

## 2. Thiết kế phiếu `engine.json` 2.0 (Codex được chỉnh chi tiết, ghi lý do trong PR)

| Năng lực | Nhận | Trả | Dùng khi |
|---|---|---|---|
| `ai.hoi_tai_lieu@1` | `van_ban`, `van_ban_tai_lieu` | `truong`: `tra_loi` (van_ban), `co_can_cu` (co_khong), `trich_dan` (van_ban, mỗi câu một dòng), `model` (van_ban) | Module hỏi AI về một tài liệu, ghép thẳng vào cột ngăn |
| `ai.hoi_theo_yeu_cau@1` | `yeu_cau_ai` | `tra_loi_ai` | Bước giữa chuỗi (ví dụ Trích xuất: chuẩn bị → **hỏi AI** → hậu kiểm); hỗ trợ `khuon_tra_loi` |

**Cài đặt bước (`tham_so`) của `ai.hoi_tai_lieu@1`** — đây là nơi **prompt thuộc module** (Admin module đặt khi tạo quy trình):
- `ma_prompt` (van_ban, bắt buộc; dạng `<module>.<function>`, ví dụ `m4.hoi_dieu_khoan`), `phien_ban_prompt` (van_ban, bắt buộc), `prompt` (van_ban, bắt buộc), `model_uu_tien` (van_ban, không bắt buộc).
- **Không có prompt mặc định chung.** Prompt rỗng/khoảng trắng → `LoiNghiepVu("THIEU_PROMPT", …)` (AI-7).

**Giới hạn đề xuất:** `ky_tu_toi_da` 500.000 (theo trần Mask), `thoi_han_giay` 600, `so_viec_dong_thoi` 1, `huy_duoc: true`.
**`loai_du_lieu_rieng`:** `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai` — chép đúng `LOAI-DU-LIEU-RIENG.md`.
**Cấu hình máy** (tệp ngoài gói, xem GIAO-CODEX-THU-TU §2): `local_ai.url`, `local_ai.timeout_giay`, `quy_tac_model[]` (`mau_ma_prompt` như `m4.*` hoặc `*`, `uu_tien`, `du_phong[]`). Engine **không biết module/function qua ngữ cảnh** (ngữ cảnh chỉ có `viec_id`, `buoc`, `phap_nhan_id`), nên chọn model theo `ma_prompt`.

## 3. Các lát

| Lát | Nội dung | Yêu cầu | Phụ thuộc | Giờ (ước tính) |
|---|---|---|---|---:|
| AI-0 | Khung gói SDK 2.0 + kiểm độc lập | AI-13 | — | 2 |
| AI-1 | `ai.hoi_tai_lieu@1`: khung trích dẫn, Local, kiểm trích dẫn | AI-1…5, 7, 8 | AI-0 | 5 |
| AI-2 | `ai.hoi_theo_yeu_cau@1` + khuôn trả lời | AI-3, 5; phục vụ TX-3 | AI-1 | 4 |
| AI-3 | Tự phát hiện model + chọn theo quy tắc | AI-10 | AI-1 | 3 |
| AI-4 | Chạy thử DEMO + bộ test Core giả đầy đủ | AI-12, 18 (phần engine) | AI-1, 2, 3 | 3 |
| AI-5 | Ghim thư viện, `NGUON.md`, cài máy sạch | AI-13 | AI-4 | 2 |
| AI-6 | Khung Cloud (chưa khai phiếu) | AI-21…24 (khung) | AI-2 | 3 |
| AI-7 | Công cụ thử Local thật 3 model (Anh chạy) | AI-14, AI-8 | AI-3 | 2 |
| | **Tổng** | | | **24** |

Ngoài phạm vi Codex: bài test cuối 40 phút (sau khi Core thật nối engine), AI-15/16/17 (hàng việc, quyền pháp nhân, lịch sử: việc của Core), màn Cổng Local/Cloud (chờ thẻ "Trạng thái" của Core).

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

### AI-0 — Khung gói SDK 2.0
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_hoi_ai/docs/GIAO-CODEX-e_hoi_ai.md.
Làm lát AI-0 cho e_hoi_ai:
1. Tạo e_hoi_ai/goi/e_hoi_ai/ theo bố cục AGENTS.md §3, chép mẫu từ docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_dem_tu.
2. engine.json 2.0 theo GIAO-CODEX-e_hoi_ai.md §2 (2 năng lực, tham_so, loai_du_lieu_rieng). Hàm năng lực tạm raise LoiNghiepVu("CHUA_LAM", ...).
3. Tạo _chung/contract/{van_ban_tai_lieu,yeu_cau_ai,tra_loi_ai}.schema.json theo LOAI-DU-LIEU-RIENG.md; chép vào gói; test so băm hai bản.
4. Tạo e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/cau_hinh_may.py (đọc JSON ngoài gói theo KTT_ENGINE_CAU_HINH, có schema, thiếu tệp không làm engine chết) + test.
5. e_hoi_ai/tests/kiem_doc_lap.py: quét goi/ không có "kho_tri_thuc." ngoài "kho_tri_thuc_sdk", không __pycache__/.pyc/symlink; mã thoát 0/1.
Đạt: Engine.tu_khai_bao đọc phiếu không lỗi; pytest e_hoi_ai/tests xanh; kiem_doc_lap mã 0. Không sửa ma-nguon/.
```

### AI-1 — Hỏi tài liệu, chỉ Local
```
Làm lát AI-1 cho e_hoi_ai (đọc lại AGENTS.md và GIAO-CODEX-e_hoi_ai.md).
Chép lõi cần dùng từ e_hoi_ai/ma-nguon/lib/cong_ai.py, lib/ai_cuc_bo.py, dto.py, hoi.py vào goi/e_hoi_ai/e_hoi_ai/ (bỏ mọi import kho_tri_thuc.*, bỏ socket/Bootstrap/SDKEngine).
Viết ai.hoi_tai_lieu@1:
- Nhận van_ban hoặc van_ban_tai_lieu (lấy trường van_ban). tham_so: ma_prompt, phien_ban_prompt, prompt, model_uu_tien.
- Ghép khung chung: bắt buộc trích dẫn nguyên văn; không có căn cứ thì trả "không thấy căn cứ", không bịa.
- Gọi Local AI qua ai_cuc_bo (chỉ loopback/LAN/Tailscale, chặn DNS/proxy/redirect như mã cũ). Cấu hình lấy từ cau_hinh_may.
- Python kiểm trích dẫn: câu trích phải có nguyên văn trong tài liệu; số trong câu trả lời phải có trong nguồn; không đạt thì co_can_cu=false + cảnh báo.
- Prompt rỗng → LoiNghiepVu THIEU_PROMPT. Local lỗi/mất kết nối/model chưa sẵn sàng → LoiNghiepVu LOCAL_AI_KHONG_SAN_SANG, thu_lai_duoc=True. Tuyệt đối không gọi Cloud.
- viec.tien_do trước/sau gọi AI; viec.kiem_huy() trước khi gọi AI.
- Nhật ký kỹ thuật ra stderr: ma_prompt, phien_ban_prompt, model, ly_do_chon, thời gian ms, kết quả kiểm. KHÔNG ghi prompt, tài liệu, câu trả lời.
Test (Linux, không mạng): máy chủ Local giả HTTP trên 127.0.0.1 kiểu OpenAI-compatible; CoreGia().chay_thu cho các ca: trả lời đúng 1.000.000 VND / 30/10/2026 có trích dẫn; câu không có trong tài liệu → co_can_cu=false; trích dẫn bịa → bị hạ; thiếu prompt → LOI THIEU_PROMPT; Local tắt → LOI thu_lai_duoc; hủy giữa chừng → HUY; gay_mat_xac_nhan("ket_qua") → không nộp trùng. Khẳng định 0 lượt Cloud (đếm số lời gọi tới provider Cloud = 0).
```

### AI-2 — Hỏi theo yêu cầu, có khuôn trả lời
```
Làm lát AI-2 cho e_hoi_ai.
Viết ai.hoi_theo_yeu_cau@1: nhận yeu_cau_ai, trả tra_loi_ai đúng _chung/docs/LOAI-DU-LIEU-RIENG.md.
- khuon_tra_loi != null: gửi Local kèm khuôn (Ollama: "format": <schema> qua /api/chat; OpenAI-compatible: response_format json_schema). Kiểm kết quả đúng khuôn bằng bộ kiểm JSON Schema tối thiểu tự viết hoặc thư viện đã ghim (nếu thêm thư viện: ghi NGUON.md). Sai khuôn sau 1 lần hỏi lại → LoiNghiepVu AI_TRA_SAI_KHUON.
- chuyen_tiep trả lại nguyên vẹn (so sánh byte JSON chuẩn hóa trong test). Trần chuyen_tiep 64 KiB, khuon 32 KiB → vượt thì từ chối.
- Cùng quy tắc trích dẫn, thiếu prompt, Local lỗi, 0 Cloud như AI-1.
Test bằng Local giả + CoreGia: có khuôn (trả du_lieu đúng schema), sai khuôn, không khuôn, chuyen_tiep nguyên vẹn, vượt trần.
```

### AI-3 — Tự phát hiện và chọn model
```
Làm lát AI-3 cho e_hoi_ai.
- Phát hiện model trên máy Local theo e_hoi_ai/docs/KS-AI-MODEL.md mục 2: Ollama GET /api/tags; LM Studio /api/v1/models (dự phòng /api/v0/models); còn lại GET /v1/models → "openai_compatible". Không suy loại từ tên model/cổng. Lưu đệm trong bộ nhớ 5 phút; lỗi phát hiện không làm engine chết.
- Chọn model cho mỗi lượt: model_uu_tien (tham_so) nếu có và khả dụng → quy_tac_model khớp ma_prompt (mẫu "m4.*", "*") theo thứ tự uu_tien rồi du_phong → model đầu tiên khả dụng. Ghi ly_do_chon_model vào kết quả. Không model nào khả dụng → LOCAL_AI_KHONG_SAN_SANG.
- Không tự xếp chất lượng gpt-oss/Qwen/Gemma; không ghim tên model trong mã.
Test: Local giả trả danh sách theo từng kiểu API; ca ưu tiên, dự phòng, không khớp, model biến mất giữa hai lượt.
```

### AI-4 — Chạy thử DEMO và bộ test đầy đủ
```
Làm lát AI-4 cho e_hoi_ai.
- engine.json: chay_thu_demo với dữ liệu DEMO của QUYET-DINH-CUOI-e_hoi_ai.md §5 ("Công ty DEMO Ánh Dương", "DEMO-001", 1.000.000 VND, 30/10/2026; một câu không có đáp án). Không ví dụ nào cần dữ liệu thật.
- e_hoi_ai/tests/chay_demo_voi_local_gia.py: bật Local giả, đặt KTT_ENGINE_CAU_HINH trỏ tệp cấu hình DEMO trong tests/, chạy CoreGia().chay_thu_demo(app); mã thoát 0 khi mọi ví dụ đạt. Đây là cổng đạt thay cho "python -m kho_tri_thuc_sdk.thu" của engine này (lệnh đó không có máy AI); ghi rõ trong README gói.
- Thêm 1 test chạy qua MayChuGia (HTTP thật trên loopback) để kiểm đường app.chay() đọc dòng khởi động stdin.
- Cập nhật e_hoi_ai/docs/VIEC.md và YEU-CAU-VA-HIEN-TRANG.md (trạng thái "đã kiểm bằng Core giả").
```

### AI-5 — Ghim và cài máy sạch
```
Làm lát AI-5 cho e_hoi_ai.
- goi/e_hoi_ai/requirements.lock (chỉ thư viện thật sự dùng; nếu chỉ thư viện chuẩn thì ghi rõ), NGUON.md: nguồn từng tệp chép từ ma-nguon (đường dẫn cũ → mới) + SHA-256 tệp trong gói.
- Kịch bản tests/kiem_may_sach.sh và .cmd ASCII: tạo venv mới, cài SDK wheel --no-index --no-deps, cài requirements.lock, chạy chay_demo_voi_local_gia.py. Chạy bản .sh trong CI của lát.
- Đảm bảo goi/ sạch __pycache__.
```

### AI-6 — Khung Cloud (chưa khai phiếu)
```
Làm lát AI-6 cho e_hoi_ai. KHÔNG thêm năng lực Cloud vào engine.json ở lát này.
- Tách seam nhà cung cấp: NhaCungCapLocal (đang dùng) và NhaCungCapCloud (chuyển từ ma-nguon/lib/cong_ai.py: Anthropic/OpenAI) — Cloud nhận khóa qua tham số khởi tạo, KHÔNG đọc env/tệp/đĩa.
- Hàm hoi_cloud(van_ban_da_che, ...) chỉ nhận phong bì van_ban_da_che (LOAI-DU-LIEU-RIENG §2.4): từ chối nếu con_sot khác rỗng hoặc kiem_tien_ngay != true; không gửi ma_yeu_cau ra ngoài; chép ma_yeu_cau vào chuyen_tiep.
- Cờ BAT_CLOUD = False cứng trong mã; test khẳng định mọi đường của ai.hoi_tai_lieu@1 và ai.hoi_theo_yeu_cau@1 không bao giờ chạm NhaCungCapCloud.
- Ghi vào VIEC.md: bản 2 cần Core có bi_mat[], công tắc Cloud theo module (M9 và nhóm 07 luôn chỉ Local), đo độ chính xác + kiểm xác suất 20%→10%→5% (cần ngăn dữ liệu).
Test chỉ bằng Cloud giả trong bộ nhớ.
```

### AI-7 — Công cụ thử Local thật
```
Làm lát AI-7 cho e_hoi_ai.
- Chuyển e_hoi_ai/tu-core-cu/tools/thu_local_ai_that.py thành e_hoi_ai/cong-cu/thu_local_ai_that.py dùng gói mới: mặc định CHẠY KHÔ (không gọi mạng); chỉ gọi thật khi có --that và --url.
- Chạy ca DEMO của AI-4 trên từng model phát hiện được; ghi bảng: model, đúng/sai so đáp án, có trích dẫn, thời gian ms; ca tắt Local → báo không sẵn sàng; đếm Cloud = 0. Kết quả ghi tệp JSON trong thư mục chạy, không ghi nội dung tài liệu ngoài DEMO.
- Tệp e_hoi_ai/cong-cu/THU-LOCAL-AI-THAT.cmd (ASCII) để Anh tự chạy trên máy Windows có Tailscale; hướng dẫn 5 dòng trong README.
Codex không chạy bản thật.
```

## 5. Cần Core / Chờ Anh của engine này
- Cần Core: mục 3 của `GIAO-CODEX-THU-TU.md` (điểm 1, 2, 6, 7).
- Chờ Anh: Q1, Q3, Q4 ở `GIAO-CODEX-THU-TU.md` §4. Bản 2: cách giữ khóa Cloud và tài khoản Windows.

## 6. AI-9 — Nhận diện thực thể chỉ Local cho MASK-2c

*Thiết kế MASK-2c-P, 15/11/2026; chưa code/chưa bật Cloud. Các mô tả tệp cấu hình lịch sử đã được AI-8 và GIAO-CODEX-DOT-2.md §2 thay thế: cấu hình/model qua Ngan, tạm RAM, không lưu trên máy engine.*

**Quyết định của Anh 15/11/2026 (nguyên văn): "Thêm AI cục bộ"** — trước khi bật Cloud, thêm lớp AI cục bộ (Local AI) nhận diện tên người như lớp an toàn thứ hai cho Mask.

Căn cứ mã đã đọc: `hoi_yeu_cau.py` có `ai.hoi_theo_yeu_cau@1`, trả nguyên `chuyen_tiep`, khuôn đúng mới trả `du_lieu`; `_kiem_tra_loi/_duoc_dan` hiện kiểm mọi lá JSON trong câu trích nên nhãn `nguoi`, `chac`, offset và danh sách rỗng không phù hợp để tái dùng nguyên handler. Trích dẫn dùng `.index()` cũng không phân biệt lần tên lặp. `ai_cuc_bo.py` đã chặn DNS/proxy/redirect, chỉ IP nội bộ/Tailscale, chọn model Local; nhưng hiện gom lỗi POST thành `LocalAIKhongSanSang` và chưa kiểm đủ dấu hiệu phản hồi bị cắt. Không coi đây là năng lực nhận diện đã hoàn tất.

Chọn năng lực riêng **`ai.hoi_mask_cuc_bo@1`: `yeu_cau_ai` → `tra_loi_ai`**, vẫn dùng hai loại sẵn có và transport/model/schema checker đã có. Không đổi nghĩa/cách kiểm hỏi–đáp cũ. Profile `chuyen_tiep.mask_2c` là **ĐỀ XUẤT MASK-2c-P, chờ Anh**, chi tiết ở `_chung/docs/LOAI-DU-LIEU-RIENG.md` §6 và phiếu Mask §6; không sửa schema chung. Core gọi AI-9, không phải e_mask. Prompt thuộc module/quy trình, có mã/phiên bản/băm, không thêm màn quản lý prompt của engine.

| Lát | Nội dung | Phụ thuộc | Giờ ƯỚC TÍNH | Độ khó | Tối đa tệp mã |
|---|---|---|---:|---|---|
| AI-9 | JSON thực thể+offset, Local bắt buộc, kiểm span và lỗi đóng | AI-8; duyệt profile MASK-2c; MASK-2c-2 cho tích hợp | 6 | kho | 5: `hoi_mask.py`, `chay.py`, `ai_cuc_bo.py`, `nha_cung_cap.py`, `../engine.json` (Python tương đối `goi/e_hoi_ai/e_hoi_ai/`) |

### AI-9 — Nhận diện theo span chỉ bằng Local AI
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, SDK 2.0.0 HUONG-DAN-VIET-ENGINE.md/MAU-PHIEU-ENGINE.md; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md §6; e_hoi_ai/CLAUDE.md, docs/QUYET-DINH-CUOI-e_hoi_ai.md, YEU-CAU-VA-HIEN-TRANG.md, GIAO-CODEX-e_hoi_ai.md §6, VIEC.md và mã goi/e_hoi_ai/e_hoi_ai/{hoi_yeu_cau,khuon_json,ai_cuc_bo,nha_cung_cap,chon_model}.py; e_mask/docs/BAO-CAO-MASK-2b.md và GIAO-CODEX-e_mask.md §6. Làm AI-9 sau AI-8, 6 giờ ƯỚC TÍNH, kho. Quyết định Anh 15/11: "Thêm AI cục bộ". Profile dữ liệu chưa duyệt thì chỉ test fixture, không kích hoạt runtime.
Tối đa 5 tệp mã: e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/{hoi_mask.py,chay.py,ai_cuc_bo.py,nha_cung_cap.py}, e_hoi_ai/goi/e_hoi_ai/engine.json. Thêm ai.hoi_mask_cuc_bo@1 nhận yeu_cau_ai, trả tra_loi_ai. Tái dùng bộ kiểm schema/chọn model/transport qua import trong cùng gói, không import/gọi e_mask. Không sửa schema chung/SDK/nguồn cũ, không dependency. Không đổi _kiem_tra_loi của hỏi–đáp cũ để làm xanh nhận diện.
Trong hoi_mask.py kiểm profile chuyen_tiep.mask_2c đúng §6 sổ loại chung: nha_cung_cap_bat_buoc=local bắt buộc, mã/phiên bản/băm prompt+khuôn, kiểu offset unicode_code_point, đoạn/băm đúng yêu cầu; thiếu hoặc khác local từ chối trước gửi. Chỉ dùng provider local, không tự tạo metadata tin cậy từ phản hồi model; chuyen_tiep trả nguyên byte JSON chuẩn hóa, không đưa nó/snapshot/mã yêu cầu ra model. tai_lieu là đoạn GỐC chưa che (Cf/NFD giữ nguyên), chỉ Local; prompt do module/quy trình cấp, ghim profile, không lưu prompt trong cấu hình engine.
Khuôn du_lieu bắt buộc {da_quet_het:true,thuc_the:[{loai:nguoi|to_chuc|dia_chi,nguyen_van:string,bat_dau:integer,ket_thuc:integer,muc:chac|nghi_ngo}]}, additionalProperties:false, đủ required tại mọi object, mảng rỗng hợp lệ. Khuôn <=32 KiB/chuyen_tiep<=64 KiB; kiểm schema tối thiểu hiện có, không nhận khóa trùng/NaN/Infinity/sai kiểu/JSON thiếu. Python kiểm 0<=a<b<=len(tai_lieu) và tai_lieu[a:b]==nguyen_van; không dùng .index() để chữa sai offset hoặc gộp các lần tên lặp. Nhãn/mức/offset là metadata, không yêu cầu chúng xuất hiện trong câu trích. Trích dẫn từng thực thể giữ nguyên văn+offset; kiểm_trich_dan.dat chỉ true khi thực sự đúng. Danh sách rỗng hợp lệ trả khong_thay_can_cu,kiem_trich_dan.dat=true,du_lieu đúng khuôn, tuyệt đối không tạo thực thể giả; rỗng không tự là chứng cứ an toàn. nha_cung_cap của kết quả do engine đặt local, bam_dau_vao tính SHA JSON chuẩn của TOÀN phong bì yeu_cau_ai như handler cũ, không phải SHA tai_lieu.
Giữ kiểm URL IP loopback/LAN/Tailscale, bind nguồn, cấm DNS/proxy/redirect, từ chối metadata remote/cloud; chỉ dự phòng sang model Local theo cấu hình Ngan, không Cloud. Kiểm budget đầu vào/đầu ra, hoàn tất API (Ollama done/done_reason; OpenAI-compatible finish_reason), response bị cắt/thiếu dấu hoàn tất/sai khuôn thì fail-closed. Không cắt âm thầm theo max tokens/bytes. Có thể hỏi lại tối đa 1 lần khi phản hồi HOÀN TẤT nhưng sai khuôn, không áp retry đó cho lượt chưa rõ.
Phân biệt lỗi trước gửi -> LoiNghiepVu LOCAL_AI_KHONG_SAN_SANG thu_lai_duoc; POST có thể đã nhận nhưng mất phản hồi/timeout hoặc 202 chưa kết quả -> raise ChuaRo(ma_tuong_quan), không fallback/retry mù/đổi thành mảng rỗng. Cần sửa transport theo trạng thái gửi, giữ kiểm an toàn cũ và cập nhật test các handler chịu ảnh hưởng; provider local truyền nguyên ChuaRo. Không biết chắc nguồn chưa nhận thì chọn ChuaRo bảo thủ. Hủy/mất lease dừng trước trả. BAT_CLOUD vẫn False, không khai năng lực Cloud, không gửi original tới bất kỳ Cloud provider nào kể cả khi module bật Cloud sau này.
Cấu hình/model qua Ngan và NganBoNho như AI-8; không sửa mẫu ngan.py/cau_hinh.py, không tệp cấu hình/sổ/cache bền. Log chỉ mã/phiên bản/số đếm/thời gian, không prompt/gốc/trích dẫn/response/URL thật/mã yêu cầu. Lead xác nhận server dùng model tại chỗ, chặn egress Cloud trước dùng thật; IP private và nhãn local riêng lẻ không chứng minh điều đó. Core chứng thực nguồn bước AI-9 để Mask hậu kiểm, payload không tự cấp quyền.
Test Local HTTP giả+CoreGia: danh sách đúng, rỗng đúng, nhiều lần tên trùng, JSON sai/thiếu/ngoài khuôn/offset sai/kiểu bool giả integer, NFD/Cf, cắt response/context overflow, timeout trước và sau POST/ChuaRo/202, hủy, thiếu local/giả cloud, cấu hình remote/proxy/redirect/DNS, prompt injection, chuyen_tiep nguyên vẹn và không lên wire; đếm Cloud=0. Hồi quy toàn bộ hỏi–đáp cũ, không hạ chuẩn trích dẫn cũ.
Chạy .venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai; -B -m pytest e_hoi_ai/tests -q; -B e_hoi_ai/tests/kiem_doc_lap.py; -B e_hoi_ai/tests/chay_demo_voi_local_gia.py. Dán kết quả thật và giới hạn CLI thiếu cấu hình/model, git diff --check; cập nhật e_hoi_ai/docs/VIEC.md/CHANGELOG nếu có, ghi đã kiểm bằng Core giả (CoreGia), chưa đo model/Core thật. PR chờ lead mở, không commit/push; báo cáo AGENTS.md §6 với giờ thực tế và lệch phiếu. Cần Core nguồn tin cậy/lặp đoạn/deadline/quyền snapshot ghi VIEC.md, không viết route Core riêng.
```

**Điều kiện hoàn tất lát:** bộ giả/hồi quy đạt, nguyên bản chỉ ra Local và 0 Cloud; không suy ra đạt mục tiêu 0 lọt. Đo held-out và `.cmd` do MASK-2c-4 thực hiện, Anh chạy model thật. Cần Core chứng thực nguồn/kế hoạch đoạn/quyền tệp và SDK 2.1; thiếu thì fail-closed, không coi payload có `nha_cung_cap=local` là đã xác thực.

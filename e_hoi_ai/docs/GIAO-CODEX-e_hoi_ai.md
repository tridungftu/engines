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

# e_hoi_ai — Hỏi AI: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `QUYET-DINH-CUOI-e_hoi_ai.md` (06/11) và `PHIEU-ENGINE-e_hoi_ai.md`.
- Chỉ đạo của Anh ngày 07–08/11:
  - máy AI có gpt-oss 20B, Qwen3 8B, Gemma;
  - tự phát hiện và tự chọn model;
  - luôn có màn Cổng Local AI và Cổng Cloud AI;
  - máy AI đã bật, nối qua Tailscale.
- TL 48 (cổng AI).
- **Yêu cầu chung** của mọi engine nằm ở `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Hiện trạng** đối chiếu `ma-nguon\CHANGELOG.md` (tới 08/11) và mã. Ký hiệu:
- ✅ có, đã kiểm bằng mock/thuần
- 🟡 một phần, hoặc đang nằm trong Core
- ❌ chưa có

**Chưa có gì chạy thật với model thật.**

## 0. Kết luận
- **Bản 1 = chỉ Local AI.** Module gửi prompt của function cùng tài liệu → engine ghép khung "trả lời có trích dẫn / không thấy căn cứ" → gọi Local → Python kiểm trích dẫn → trả kết quả và ghi nhật ký.
- **Mã lõi bản 1 đã gộp (08/11)** và kiểm bằng mock. Gồm: contract v2, ghim function và prompt, chọn model theo module/function có dự phòng, nhật ký nguồn gốc.
- **Còn thiếu để Anh dùng được:**
  1. đường chạy engine thật trên Core (cổng chung K1–K5);
  2. thử 3 model thật (lát 8);
  3. màn Cổng Cloud AI;
  4. bài test cuối 40 phút.
- Màn Chạy thử và màn Cổng Local **hiện nằm trong mã Core** (vi phạm G14). Phải chuyển thành giao diện của engine, nạp qua Quản lý engine.

## 1. Yêu cầu

### 1.1 Bản 1 (Local)

| Mã | Yêu cầu | Căn cứ |
|---|---|---|
| AI-1 | Bản 1 **chỉ Local**. Cloud để sang bản 2. Mọi lượt bản 1 phải có **0 lượt Cloud** | QĐ §1, câu P |
| AI-2 | Nhận từ module: prompt của function, tài liệu, mã module, mã function | QĐ §1 |
| AI-3 | Ghép khung chung: bắt buộc trích dẫn; tài liệu không có thông tin thì trả "không thấy căn cứ", không bịa | QĐ §1 |
| AI-4 | Gửi Local qua cổng chung. Máy Local riêng, có GPU. Kết nối theo TL 48 §1.2 (Tailscale) | QĐ §1, LM; Anh 08/11 |
| AI-5 | Python kiểm trích dẫn: câu trích phải có nguyên văn trong tài liệu; số trong câu trả lời phải có trong nguồn | QĐ §1 |
| AI-6 | Nhật ký mỗi lượt: module, function, phiên bản prompt, model, lý do chọn model, thời gian, kết quả kiểm. **Không ghi nội dung nhạy cảm** | QĐ §1; chuỗi bản 1 |
| AI-7 | Lượt **thiếu prompt** → từ chối, báo rõ lý do. Không có prompt mặc định chung | QĐ §1 |
| AI-8 | Local lỗi (mất kết nối, model chưa sẵn sàng) → báo rõ "không sẵn sàng / thử lại", cho thử lại, không chuyển Cloud | QĐ §1, lát 8 |
| AI-9 | **Prompt thuộc module:** mỗi function một prompt, có mã và phiên bản, khai báo trong gói module. Engine dùng đúng prompt của function gửi tới. Sửa prompt làm **trong module**: Admin module sửa của mình, Admin Core sửa tất cả | QĐ PR, PR2 |
| AI-10 | **Tự phát hiện model** trên máy Local khi kết nối và **tự chọn** theo module/function, có ưu tiên và dự phòng. Máy hiện có: gpt-oss 20B, Qwen3 8B, Gemma | Anh 07/11 |
| AI-11 | **Luôn có hai màn:** Cổng Local AI (địa chỉ máy, trạng thái, model tìm thấy, model chọn cho từng function) và Cổng Cloud AI (bản 1 hiện "tắt", để sẵn cấu hình bản 2) | Anh 07/11 |
| AI-12 | Màn **Chạy thử DEMO**, chỉ Admin. Làm cùng lúc với back end; làm đầu tiên | QĐ lát 10, DM |
| AI-13 | Khóa phiên bản thư viện, cài được trên máy sạch | QĐ lát 3 (G3-GOI-09) |
| AI-14 | Thử Local thật trên 3 model đã kê khai | QĐ lát 8 |
| AI-15 | Hàng chờ: người dùng thấy vị trí trong hàng và thời gian ước trong "Việc của tôi"; mỗi việc ghi một lượt | QĐ §5 bước 2 |
| AI-16 | Phân quyền theo pháp nhân: vai khác pháp nhân không xem được nội dung không thuộc quyền | QĐ §5 bước 4 |
| AI-17 | Lịch sử và thống kê còn nguyên sau khi khởi động lại | QĐ lát 7 (gộp vào bài cuối) |
| AI-18 | Bài test cuối khoảng 40 phút, 5 bước, chỉ dữ liệu DEMO | QĐ §5 |

### 1.2 Bản 2 (Cloud) — chưa làm

| Mã | Yêu cầu | Căn cứ |
|---|---|---|
| AI-21 | Công tắc Cloud **theo từng module**, mặc định tắt. **M9 luôn chỉ Local**; nhóm tài liệu 07-Nhân sự chỉ Local (TL 56) | QĐ A1 |
| AI-22 | Module đã bật Cloud thì tự chuyển sang Cloud khi Local không chạy, Local không chắc, hoặc ở lượt kiểm xác suất | QĐ §1 |
| AI-23 | Đo độ chính xác Local theo function. Tỷ lệ kiểm xác suất 20% → 10% → 5%, không về 0; dưới 90% thì quay lại 20% | QĐ A2 |
| AI-24 | **Mọi lượt Cloud đi qua Mask.** Chỉ nội dung đã che được ra ngoài | QĐ §1; QĐ Mask §3 |
| AI-25 | Tài khoản Windows riêng và cách giữ khóa API Cloud (quyết khi làm bản 2) | QĐ lát 6 |
| AI-26 | Gộp lát 5 và 9: kiểm các ca Mask lỗi bằng Cloud giả | QĐ lát 5+9 |

### 1.3 Ngoài phạm vi engine này
- **Tạo vector `ai.nhung_vector@1`:** năng lực của `e_hoi_ai`, chỉ chạy Local, nhưng làm theo phiếu `e_tra_cuu` (QĐ A3; TL 56 §9.2).
- **Quản lý prompt** thuộc module (lát AI-PROMPT đã bỏ).
- **Hàng chờ và chuỗi** thuộc bộ điều phối của Core.

## 2. Hiện trạng

| Mã | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| AI-1 | ✅ mock | Chuỗi bản 1 (08/11): "Bản 1 chỉ Local" |
| AI-2, AI-3, AI-5, AI-7 | ✅ mock | Contract `hoi_ai.v2` / `tra_loi_ai.v2`; `hoi.py`, `dto.py`. Chưa chạy model thật |
| AI-4 | 🟡 | Có cấu hình địa chỉ Local; máy AI đã bật qua Tailscale; **chưa gọi thật** |
| AI-6 | ✅ mock | Nhật ký nguồn gốc (provenance) có module/function/prompt/model/lý do chọn. Nhật ký bền sau khởi động lại phụ thuộc K4 của Core |
| AI-8 | 🟡 | Có mã lỗi; chưa thử tắt Local thật |
| AI-9 | 🟡 | Engine ghim function và prompt. Phía Core đọc prompt từ manifest module (`ham_hoi_ai`) bằng **mã riêng cho Hỏi AI trong Core** (`ho_so_module.doc_hoi_ai`, `dich_vu_engine.nguon_hoi_ai`) → cần cửa chung. Màn sửa prompt trong module: ❌ |
| AI-10 | 🟡 | Chọn model theo module/function có ưu tiên và dự phòng (✅ mock). **Tự phát hiện model khi kết nối: chưa xác nhận chạy thật** (`KS-AI-MODEL.md`) |
| AI-11 | 🟡 / ❌ | Màn Local: route `/api/v1/quan-tri/engine/e_hoi_ai/local` và JS **nằm trong Core**. Màn Cloud: ❌ |
| AI-12 | 🟡 | `chay_thu_hoi_ai.js` và route chạy thử **nằm trong Core** (bản sao ở `tu-core-cu\phia-core\`). Chưa nghiệm thu trên trình duyệt |
| AI-13 | 🟡 | AI-LAT3: `requirements.lock`, `NGUON.md` có SHA-256 của 14 tệp. **Chưa build và cài wheel độc lập** |
| AI-14 | 🟡 | AI-LAT8: công cụ thử 3 model, mặc định chạy khô (`tu-core-cu\tools\thu_local_ai_that.py`, `MO-THU-LOCAL-AI.cmd`). **Chưa chạy thật** |
| AI-15, AI-16, AI-17 | ❌ | Phụ thuộc hàng việc, quyền và nhật ký bền của Core (K4, K5) |
| AI-18 | ❌ | Chưa chạy |
| AI-21 … AI-26 | ❌ | Bản 2 |

**Phụ thuộc vào Core** (xem `_chung`): đường chạy engine thật K1 → K5, cổng HTTP để engine ở máy khác, màn chạy thử chung, màn cấu hình dựng từ schema.

## 3. Thư mục

| Thư mục | Nội dung |
|---|---|
| `ma-nguon\` | Mã engine: `hoi.py`, `chay.py`, `dto.py`, `bi_mat.py`, `nhat_ky.py`, `lib\`, `contract\`, `engine.json`, `tests\` |
| `shim-kho_tri_thuc\` | Shim đường cũ (chỉ để tham chiếu; gói mới không dùng) |
| `tests-tu-core\` | 23 test cũ chạy trong Core: cổng AI, chạy thử, model quản trị |
| `tu-core-cu\src\` | Mã thế hệ cũ: `tri_thuc\cong_ai.py`, `ai_cuc_bo.py` |
| `tu-core-cu\tools\` | `thu_local_ai_that.py`, `MO-THU-LOCAL-AI.cmd` |
| `tu-core-cu\phia-core\` | Bản sao mã phía Core riêng Hỏi AI: `chay_thu_hoi_ai.js`, SQL 129, `nhat_ky_ai_legacy.py` (đã chuyển hẳn khỏi Core: không ai dùng, import hỏng) |
| `docs\` | Quyết định cuối, phiếu, khảo sát model, xác minh kênh 1a, quyết định 1b |

## 4. Thứ tự đề xuất
1. Đóng gói theo cổng chung (`_chung`): gói độc lập, bỏ shim, chỉ dùng SDK.
2. Màn Chạy thử, màn Cổng Local, màn Cổng Cloud (tắt) dưới dạng **giao diện của engine**, nạp qua Quản lý engine.
3. Lát 8: thử 3 model thật qua Tailscale; ghi phút thực tế.
4. Ghép với Core khi có K1–K5 → bài test cuối 40 phút.
5. Bản 2: AI-21 → AI-26 (sau khi Mask xong).

## 5. Chờ Anh
- Không có câu chặn bản 1. Model đã kê khai (07/11).
- Bản 2: cách giữ khóa API Cloud và tài khoản Windows (quyết khi làm bản 2).

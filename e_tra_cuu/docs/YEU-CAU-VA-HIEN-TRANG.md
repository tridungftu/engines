# e_tra_cuu — Tra cứu tài liệu (hỏi đáp 3 tầng): yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- Đặc tả `DAC-TA-e_tra_cuu.md`, là bản chép TL 56 (31/10/2026). Anh đã chốt QĐ-1 đến QĐ-4.
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

## 0. Kết luận
- **Chưa có dòng mã nào.** Mới có đặc tả, Anh đã chốt 4 quyết định.
- Engine thứ 6. Thay cho E-RAG (TL 53) và phần hỏi đáp M9-2. **Mọi module dùng chung một engine.**
- **Hỏi đáp 3 tầng**, dừng ở tầng đủ căn cứ. Câu trả lời luôn có trích dẫn và nhãn **Xanh** (dữ liệu đã duyệt) hoặc **Vàng** (trích từ tệp, chưa duyệt).
  1. Dữ liệu có cấu trúc đã duyệt.
  2. Chỉ mục đoạn văn.
  3. Trích lại trên đúng tệp.
- **Phần lớn khối lượng nằm ở Core**: Kho tài liệu, `loi_tra_cuu`, hai quy trình. **Engine chỉ tính toán**: phân loại, cắt đoạn, phân tích câu hỏi, xếp hạng lại, soạn câu trả lời. Engine không giữ dữ liệu.

## 1. Yêu cầu

### 1.1 Anh đã chốt (31/10)
| # | Quyết định |
|---|---|
| 1 | RAG làm thành **engine trong Core**, không gắn riêng một module |
| 2 | Khi hỏi, Local AI **ưu tiên dữ liệu từ engine trích xuất**; không thấy mới trích từ tệp |
| 3 | **Mỗi lượt hỏi đáp lưu dạng cache** để dùng lại |
| 4 | Cấu trúc thư mục kho **do hệ thống tạo, người không sắp xếp** |
| 5 | Kho chia **trước hết theo pháp nhân, sau đó theo 8 nhóm**: 01 Pháp lý dự án · 02 Vay · 03 Mua hàng (không gồm xây dựng) · 04 Hợp đồng xây dựng · 05 Bán hàng · 06 Pháp lý công ty · 07 Nhân sự · 08 Quy chế khác |
| 6 | Nhóm 05 gồm bán nhựa và bán điện ở trạng thái **chờ kích hoạt** |
| 7–8 | Ranh giới 03/04 nằm ở **BOQ**. Thiết bị kèm lắp đặt, sửa chữa bảo trì, vật tư chủ đầu tư tự mua → 04. Thuê máy móc → 03 |
| 9 | Hợp đồng đổi bản chất giữa chừng → chuyển cả bộ sang nhóm mới, ghi nhật ký |
| 10 | Quy chế về người lao động → 07; còn lại → 08 |
| 11–12 | Nhóm 06 có nhánh cho công ty TNHH. Nhóm 08 không định sẵn thư mục con |
| 13 | Dùng SDK, API, CSDL chuẩn của Core |
| QĐ-1 | Chỉ mục và cache do **Core lưu** (`loi_tra_cuu`); engine không giữ dữ liệu |
| QĐ-2 | Dữ liệu mới tìm ở tầng 2–3 → **hàng chờ duyệt K5** |
| QĐ-3 | Hộp nhận: **web + thư mục trên máy chủ** |
| QĐ-4 | **Không** đối chiếu ngược tầng 1 với tệp ở từng câu hỏi. Bù bằng cờ "có văn bản mới chờ duyệt" khi nạp văn bản thay thế |

### 1.2 Năng lực của engine (đặc tả §9)

| Capability | Vào → ra |
|---|---|
| `tra_cuu.phan_loai_tai_lieu@1` | `van_ban_tai_lieu.v1` + danh mục đang hoạt động → `phan_loai_tai_lieu.v1` (pháp nhân, nhóm, loại, đối tượng, hiệu lực, độ tin cậy, căn cứ) |
| `tra_cuu.cat_doan@1` | văn bản (+ bảng) → `doan_van.v1`, cắt theo điều/khoản/bảng/trang |
| `tra_cuu.phan_tich_cau_hoi@1` | `cau_hoi_tra_cuu.v1` + hàm tra cứu được phép → ý định, thực thể, hàm và tham số, cờ phụ thuộc thời điểm |
| `tra_cuu.xep_hang_lai@1` | câu hỏi + đoạn ứng viên → điểm |
| `tra_cuu.soan_tra_loi@1` | câu hỏi + bằng chứng → `tra_loi_tra_cuu.v1` |

**Bổ sung cho engine khác:**
- `e_hoi_ai` thêm `ai.nhung_vector@1`, chỉ Local; phải đo trên bộ câu hỏi mẫu trước khi chốt model.
- `e_trich_xuat` nhận "danh sách trường cần trích".

### 1.3 Quy tắc chính
- Mọi lượt gọi model **chỉ qua `e_hoi_ai`**. Tạo vector luôn chạy Local. Cloud chỉ qua `e_mask`. M9 và nhóm 07 chỉ dùng Local.
- **"Không thấy ở tầng 1"** gồm các trường hợp: không có giá trị, có nhưng chưa duyệt, độ tin cậy dưới ngưỡng, thuộc phiên bản hết hiệu lực, hoặc câu hỏi ngoài các trường đã trích.
- Python kiểm: trích dẫn phải đúng nguyên văn, số phải có trong bằng chứng. Không đạt thì hạ nhãn hoặc trả "không thấy căn cứ".
- **Mâu thuẫn** giữa tầng 1 và tệp → trả cả hai kèm cờ, tạo việc trong K5, không tự chọn bên nào.
- **Cache:** chỉ trùng khi **thực thể trùng khớp**; quyền của người hỏi phải bao trùm mọi nguồn; hết hạn theo sự kiện nguồn; chỉ lưu tham chiếu, không chép nội dung.
- **Quyền lọc ngay trong truy vấn PostgreSQL (RLS)**, nên đoạn văn ngoài quyền không bao giờ tới AI.

### 1.4 Phần thuộc Core, không thuộc engine
Kho tài liệu (cây kho, hộp nhận, đặt tên, phiên bản, hàng chờ phân loại), schema `loi_tra_cuu`, hai quy trình `nap_tai_lieu` và `hoi_dap`, các route `/api/v1/tra-cuu/*` và `/api/v1/tai-lieu/*`, SDK JS `KhungHoiDap`, `CayKhoTaiLieu`, `HangChoPhanLoai`, bus sự kiện.

**Lưu ý G14:** các route và màn mang tên "tra cứu" là **dịch vụ Kho tài liệu chung của Core**, không phải mã riêng của engine. Lead Core cần xếp chúng vào Phụ lục A, hoặc đưa vào dạng module hệ thống "Kho tài liệu".

## 2. Hiện trạng
| Phần | Trạng thái |
|---|---|
| Engine `e_tra_cuu` | ❌ chưa có mã |
| Kho tài liệu của Core (TC-1) | 🟡 Core có `tai_lieu.py`, `routes_tai_lieu.py`, `tep.py`; chưa có cây 8 nhóm và hộp nhận |
| pgvector / unaccent / pg_trgm trên PostgreSQL hiện có (TC-0) | ❌ chưa khảo sát |
| `ai.nhung_vector@1` | ❌ |

## 3. Lát (đặc tả §14; chưa có giờ vì chưa đo)
TC-0 khảo sát → TC-1 kho (Core) → TC-2 phân loại + cắt đoạn + vector → TC-3 hỏi đáp tầng 1–2 → TC-4 tầng 3 + hàng chờ + cờ mâu thuẫn → TC-5 cache → TC-6 SDK JS, nhúng M9, bộ câu hỏi mẫu nhóm 02 → TC-7 nạp hàng loạt.

**Project engine làm:** phần engine của TC-2, TC-3, TC-4, và bộ đo chất lượng. Phần còn lại là của Core.

## 4. Chờ Anh (trả lời sau, đặc tả §15)
1. Tên tệp có thêm mã pháp nhân không.
2. Ai được sửa danh mục; ngưỡng gợi ý loại mới ở nhóm 08.
3. Chính sách Cloud mặc định cho các module ngoài M9.
4. Thời hạn cache ngắn hạn; thời hạn giữ nhật ký; tần suất sao lưu `loi_tra_cuu`.
5. Cấu hình máy Local AI (đã biết: có GPU; model gpt-oss 20B, Qwen3 8B, Gemma).
6. Danh sách loại chi tiết của nhóm 01–07.
7. "Bán điện" có khác "điện năng" KCN không.
8. Sửa chữa, bảo trì không gắn dự án xếp vào đâu.
9. Có nạp hàng loạt tệp hiện có không.

# Giao Codex — `e_mask` (Che định danh) theo SDK 2.0

> Bổ sung 15/11/2026: [§6 MASK-2c](#6-mask-2c--lớp-ai-cục-bộ) là thiết kế mới cho lớp an toàn Local AI trước Cloud; các mô tả kho tệp/cấu hình tệp lịch sử bên dưới đã bị quyết định 15/11 và `GIAO-CODEX-DOT-2.md` §2 thay thế.

*Lập 14/11/2026, lát MASK-P, chỉ tài liệu. Căn cứ: `AGENTS.md`; `API-ENGINE-v1.md`; SDK 2.0.0 (`HUONG-DAN-VIET-ENGINE.md`, `MAU-PHIEU-ENGINE.md`); `_chung/docs/GIAO-CODEX-THU-TU.md`; `_chung/docs/LOAI-DU-LIEU-RIENG.md`; toàn bộ `e_mask/CLAUDE.md`, `e_mask/docs/` và mã trong `ma-nguon/`. Cấu trúc theo phiếu Hỏi AI/OCR. Quyết định cuối 06/11/2026 thắng về nghiệp vụ; API v1 + SDK 2.0.0 thắng về cổng kỹ thuật.*

## 1. Kết luận

- **14 lát, MASK-0 → MASK-13, tổng 52–62 giờ công ƯỚC TÍNH, chưa đo.** Khoảng giờ gồm chuyển lõi, lớp vỏ SDK, test DEMO, đóng gói và soạn công cụ; không gồm thời gian chờ Core/Anh, code phía Core hoặc chạy bài trình duyệt thật. Riêng MASK-P lập phiếu: **1 giờ ước tính**, không cộng vào tổng triển khai.
- Đích: `e_mask/goi/e_mask/`, tiến trình cục bộ SDK 2.0, HTTP do SDK quản; che/mở che văn bản và các phần tệp đã được kiểm. **Mask tạo `van_ban_da_che` cho Hỏi AI bản 2; mốc này 0 lượt Cloud, 0 lượt gọi engine khác.** Scan/ảnh do Core xếp OCR → Mask; Mask không OCR.
- **Phần tệp có điều kiện:** MASK-7 trình mức hỗ trợ và phần thiếu; MASK-8…11 chỉ triển khai phần được lead cung cấp mã sạch hoặc Anh đồng ý phương án bổ sung. Không tự viết thay phần thiếu rồi nhận là đã được duyệt. Tổng 52–62 giờ là dự toán có điều kiện, phải ước lại sau MASK-7; chưa phải cam kết hoàn thành toàn bộ Word/Excel.
- Tái dùng: `che_van_ban.py` (trần, hậu kiểm, tiền/ngày, nhận diện bí danh mềm, chống đếm lặp); các phần cần dùng của `nguon/privacy/{core,types,company_names,person_names,detectors,leftovers}.py`; nguyên tắc snapshot/chốt của `kho_qua_core.py`; test/vector hiện có. `kho_bo_nho.py` chuyển thành **fixture DEMO ngoài gói**, không là kho vận hành. `excel.py`, `excel_values.py`, `docx_revisions.py` là nguồn khảo sát cho các lát tệp, không mặc nhiên đủ tiêu chí.
- Không mang sang gói: `chay.py`/`vong_doi.py` cũ, socket/Bootstrap/SDKEngine, `env_con`, launcher nguồn ngoài, shim, SQL/route/màn riêng trong Core, contract bốn mẫu cũ, mã khóa/mở danh mục và helper mã hóa bảng đối chiếu. `variants.py` chỉ gợi ý gom tên, chưa cần trong luồng tự động. **Giữ nguyên hiện vật cũ**, ghi việc chuyển lưu trữ sau vào `VIEC.md`.
- Kho bí danh là dữ liệu lâu dài, đích là **ngăn engine do Core quản**. Đợt 1 dùng lớp `kho_tam.py` đúng giới hạn §2 dưới đây; không coi nó là quyền ghi tên gốc xuống JSON. Thiếu kho hoặc danh tính tin cậy thì từ chối xử lý thật, vẫn phát triển/test bằng **Core giả (CoreGia)**.

## 2. Thiết kế phiếu `engine.json` 2.0

Thiết kế dưới đây để các lát sau hiện thực, **MASK-P không tạo gói hoặc schema**. Chỉ điều chỉnh chi tiết triển khai tương thích và ghi lý do trong PR; thay nghiệp vụ/loại dữ liệu phải trình lead/Anh. Không đưa các khóa đề xuất của tài liệu 08/11 vào manifest đã khóa.

**Khung:** `phien_ban_manifest: 2`, `loai: "engine"`, `ma: "e_mask"`, `ten: "Che định danh"`, `phien_ban: "1.0.0"`; `tuong_thich: {core: ">=2.0.0 <3.0.0", api: "v1", sdk: ">=2.0.0 <3.0.0"}`; `che_do_chay: "cuc_bo"`; `diem_vao: {lenh: ["{python}", "-m", "e_mask.chay"], thu_muc: "."}`; `tai_nguyen.so_viec_dong_thoi: 1`; `readiness.thoi_han_giay: 30`; `bi_mat: []`; `webhook: null`. Cấu hình/schema cấu hình đặt trong gói để lớp bọc đọc, **không thêm `cau_hinh_schema`, `ngan_du_lieu`, `giao_dien_quan_tri` vào phiếu 2.0**.

### 2.1 Năng lực và tám mẫu nghiệp vụ

| Năng lực dự kiến | `nhan` | `tra` | Mẫu nghiệp vụ / thời điểm |
|---|---|---|---|
| `mask.che_van_ban@1` | `van_ban`, `van_ban_tai_lieu`, `tep` (JSON UTF-8 mẫu 1) | `van_ban_da_che` | Mẫu 1–2; MASK-5 |
| `mask.mo_che_van_ban@1` | `tra_loi_ai`, `tep` (JSON UTF-8 mẫu 3) | `truong` — bộ M dưới đây | Mẫu 3–4; MASK-5 |
| `mask.che_tep_van_ban@1` | `tep` (DOCX/XLSX/PDF có chữ hoặc JSON mẫu 5) | `van_ban_da_che` | Mẫu 5–6, mặc định văn bản; MASK-8/9 |
| `mask.che_tep_giu_dinh_dang@1` | `tep` (DOCX/XLSX hoặc JSON mẫu 5) | `truong` — bộ C | Mẫu 5–6, chọn nhận tệp; MASK-9/10 |
| `mask.mo_che_tep@1` | `tep` (JSON UTF-8 mẫu 7, tham chiếu DOCX/XLSX) | `truong` — bộ T | Mẫu 7–8; MASK-11 |

Một năng lực luôn có **một loại trả cố định**. Lựa chọn văn bản/tệp được biểu diễn bằng hai năng lực che tệp, không đổi `tra` theo tham số. Tám mẫu là bốn cặp vào/ra nghiệp vụ, **không phải tám năng lực hay tám route**. Chỉ thêm năng lực tệp vào phiếu sau khi ca tương ứng đạt; chưa đủ cả tám mẫu thì báo rõ phần chưa kiểm. Khung MASK-0 chưa được cài/kích hoạt vận hành.

**Ba loại gốc giữ đúng API:** `van_ban` chỉ mang chuỗi; `tep` là tham chiếu kho tệp Core, không đường dẫn máy; `truong` chỉ chứa các trường có kiểu đã khai. Không thêm metadata tùy ý ngang hàng `loai`/khóa payload. Bộ `truong_ra` tĩnh:

- **M:** `van_ban_da_mo_che` (`van_ban`), `so_cho_mo` (`so`), `bi_danh_khong_ro_json` (`van_ban`, mảng JSON gồm bí danh/vị trí), `mo_day_du` (`co_khong`), `trang_thai_ma_yeu_cau` (`van_ban`: `DANG_XU_LY`/`DA_DONG`), `tra_loi_ai_da_mo_json` (`van_ban`, đối tượng JSON hoặc `null` khi đầu vào mẫu 3).
- **C:** `tep_da_che` (`tep`), `ma_yeu_cau` (`van_ban`), `con_sot_json` (`van_ban`, luôn `"[]"` khi thành công), `kiem_tien_ngay` (`co_khong`), `so_cho_thay` (`so`), `bi_danh_json` (`van_ban`), `so_cum_vua_them` (`so`), `vung_da_quet_json` (`van_ban`), `canh_bao_json` (`van_ban`).
- **T:** `tep_da_mo_che` (`tep`), `so_cho_mo` (`so`), `bi_danh_khong_ro_json` (`van_ban`), `mo_day_du` (`co_khong`), `trang_thai_ma_yeu_cau` (`van_ban`).

Các trường tên `*_json` là **chuỗi JSON có kiểm cấu trúc**, không khai kiểu cột `object`/`array` ngoài API. Trường không có giá trị là `null`, không bỏ khóa. Bộ C/T là kết quả nội bộ cho module, **không phải đầu vào hợp lệ của Cloud**. Bộ M ghép được vào cột; không tự nối nó vào bước Trích xuất đang đòi `tra_loi_ai`. Nếu cần chuỗi đó, lead phải thiết kế năng lực bảo toàn loại riêng trước, không âm thầm đổi `tra`.

**Loại riêng** chép đúng tên từ sổ chung:

- `{"ma":"van_ban_tai_lieu","ten":"Văn bản tài liệu có vị trí"}`;
- `{"ma":"tra_loi_ai","ten":"Trả lời AI có trích dẫn"}`;
- `{"ma":"van_ban_da_che","ten":"Văn bản đã che định danh"}`.

Không cần mã loại mới. Đề xuất **bổ sung trường tùy chọn và chốt ngữ nghĩa** cho khung `van_ban_da_che` ở cuối `LOAI-DU-LIEU-RIENG.md`, nhãn **“ĐỀ XUẤT MASK-P, chờ Anh”**. MASK-4 chỉ tạo schema khi phần đề xuất được chốt; không sửa định nghĩa cũ hoặc schema dùng chung khác để vượt kiểm.

### 2.2 Phong bì, tham số và kiểm nội dung

- `van_ban_tai_lieu`: đọc toàn văn `van_ban`, kiểm trần trước khi dò; không chuyển nguyên trang/khối/chữ gốc vào kết quả đã che. Vị trí OCR gốc không mặc nhiên còn đúng sau thay tên bằng bí danh.
- Mẫu 1 khi cần định danh theo từng lượt: Core lưu **tệp JSON đầu vào riêng của việc**, engine đọc qua `viec.mo_tep`. Payload `{van_ban, dinh_danh_da_biet?}`; danh sách gồm `{gia_tri, nhom}`. Nhận `van_ban`/`van_ban_tai_lieu` trực tiếp thì danh sách mặc định rỗng. Không đặt tên gốc vào Cài đặt bước hoặc cấu hình máy.
- Mẫu 3: tệp JSON `{ma_yeu_cau, van_ban, dong_viec?}`. Không nhận riêng `van_ban` để mở che vì phong bì đó thiếu mã yêu cầu. `tra_loi_ai` lấy mã từ `chuyen_tiep.ma_yeu_cau`; mã thiếu/sai → lỗi, không suy từ `viec_id`, pháp nhân hoặc nội dung AI.
- Mẫu 5: tệp tài liệu trực tiếp, mặc định không có danh sách đã biết; hoặc tệp JSON `{tep: {tep_id, ten, mime, kich_thuoc}, dinh_danh_da_biet?}`. Mẫu 7: tệp JSON `{ma_yeu_cau, tep: {...}, dong_viec?}`. Tham chiếu con chỉ được mở nếu **Core xác minh thuộc cùng việc**; không chấp nhận URL/path, không tự đọc đĩa theo tên trong JSON. Cần Core xác nhận cơ chế này trước nối thật.
- `tham_so` của các năng lực che: `[]`. Hai năng lực mở che có `dong_viec` (`co_khong`, `mac_dinh: false`). Nếu payload có `dong_viec` hợp lệ thì dùng giá trị đó; nếu thiếu mới dùng Cài đặt bước. Không có `ma_yeu_cau`, danh tính, bảng đối chiếu, công tắc bỏ hậu kiểm hoặc công tắc Cloud trong Cài đặt bước.
- Che thành công: trả `{"loai":"van_ban_da_che","van_ban_da_che":{phien_ban:1, van_ban:..., ma_yeu_cau:..., con_sot:[], kiem_tien_ngay:true, chuyen_tiep:{}, ...}}`. Chỉ tạo sau hậu kiểm thực tế và sau chốt kho. Không gán hai cờ an toàn bằng hằng để vượt kiểm. Còn sót/thiếu tài nguyên/đổi tiền-ngày → `LoiNghiepVu`, **không trả loại `van_ban_da_che` hoặc tệp chưa đạt**. Kết quả nội bộ cũ `van_ban_da_che=None` không biến thành thành công ở cổng mới.
- Mở che `tra_loi_ai`: mở trong `tra_loi`, các giá trị chuỗi của `du_lieu`, câu trong `trich_dan`; giữ khóa, số, ngày, boolean, `null` và metadata nguồn/model. Trả toàn bộ đối tượng đã xử lý trong `tra_loi_ai_da_mo_json`, kèm văn bản/bộ M. Còn bí danh phải có vị trí đường trường/offset; không bỏ `du_lieu` hoặc trích dẫn. Trích dẫn đã thay chữ **không còn được giữ kết luận kiểm nguyên văn cũ**: đánh dấu cần kiểm lại, không tự tính offset mới từ tài liệu gốc chưa có. `chuyen_tiep` giữ nội bộ, không dùng làm nguồn danh tính.
- Mã yêu cầu do Core cấp/quản, coi là mã opaque; không kế thừa giới hạn UUID/64 ký tự của vỏ cũ khi cổng mới chưa chốt. Core xác minh module, người gửi, tài liệu và vùng DEMO/thật. `ngu_canh` SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`: **không đủ cho MK-12**. Thiếu nguồn tin cậy → `MASK_NGU_CANH_CHUA_XAC_MINH`; không nhận danh tính tự khai từ payload, tham số hoặc cấu hình máy.
- Mở che tra bảng chung chính thức + tạm, không giới hạn vào bí danh của một mã yêu cầu. Mã yêu cầu dùng kiểm quyền và giữ tham chiếu. Nhận diện mềm không đồng nghĩa đoán tên; bí danh hỏng/lạ giữ nguyên, báo vị trí, `mo_day_du=false`, giữ `DANG_XU_LY` dù yêu cầu đóng. Chỉ đóng khi được yêu cầu và mở đủ.

### 2.3 Giới hạn và chặn lỗi

- Mọi năng lực văn bản khai `ky_tu_toi_da: 500000`; engine tự kiểm chuỗi lồng trong loại riêng/JSON và tổng nội dung cần mở của `tra_loi_ai` vì SDK 2.0 chỉ tự đếm loại gốc `van_ban`. **500.000 được nhận, 500.001 bị từ chối**, không cắt. Danh sách đã biết ≤500 mục, giá trị ≤300 ký tự, nhóm ≤20 ký tự; giữ bộ kiểm nhóm/giá trị của lõi. Trần 500 mục không áp cho số cụm detector tìm được.
- `thoi_han_giay` đề xuất 60 cho văn bản, 300 cho tệp; `huy_duoc: true`. Đây là dự toán kỹ thuật cần đo lại, không thay trần nghiệp vụ. Gọi `viec.kiem_huy()` giữa các bước/trang/phần XML và trước chốt, tải tệp ra; SDK lo lease/retry/hủy chung, không chép vòng heartbeat cũ.
- MIME văn bản đóng gói JSON: `application/json`; DOCX: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`; XLSX: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; PDF: `application/pdf`. Kiểm cả byte/đuôi/cấu trúc, không chỉ tin MIME. JSON phải UTF-8, từ chối khóa trùng, NaN/Infinity, payload sai cấu trúc.
- **Trần tệp và đầu ra chưa được Anh chốt.** MASK-7 đo DEMO rồi trình; không lấy 20 MiB/80 MiB của parser Excel cũ hoặc 4 MiB JSON của adapter cũ làm quyết định nghiệp vụ. Có thể dùng các mức này làm trần kỹ thuật chặt hơn trong bộ thử, ghi rõ. Chưa chốt thì đường tệp vận hành báo `MASK_TEP_CHUA_CHOT_GIOI_HAN`; chưa công bố năng lực tương ứng. Không coi 500.000 đầu vào là trần đầu ra: bí danh có thể làm văn bản dài hơn; bước Hỏi AI phải kiểm lại trần của nó.
- Tệp ZIP: kiểm số phần, kích thước nén/giải nén, đường thành viên, symlink, XML entity và phần không hỗ trợ; vượt trần hoặc không quét đủ thì từ chối. Không tự bỏ sheet/ảnh/chart/lịch sử sửa hoặc chuyển sang workbook “chỉ giá trị” để báo đạt giữ định dạng. PDF yêu cầu trả tệp → `MASK_PDF_CHI_VAN_BAN`; scan/trang không có lớp chữ → `MASK_PDF_CAN_OCR`, để Core chọn chuỗi khác.
- Cụm gốc chỉ đi vào kho được phép, không vào phản hồi che, cảnh báo, stderr hoặc contract công bố. Các `changes`, `disclosures`, tên sheet, đường XML và lỗi parser cũ có thể chứa định danh: lọc về mã vùng/chỉ số/vị trí an toàn trước xuất. Tệp và nội dung mở che chỉ về đúng người/module đã xác minh.
- `LoiNghiepVu("MASK_DAU_VAO", "Nội dung yêu cầu chưa hợp lệ.")`; `MASK_QUA_GIOI_HAN` → “Nội dung vượt giới hạn cho phép. Cần chia nhỏ yêu cầu.”; `MASK_MA_YEU_CAU` → “Không xác minh được quyền mở che cho yêu cầu này.”; `MASK_THIEU_TAI_NGUYEN`/`MASK_DINH_DANH_CHUA_DAT`/`MASK_TIEN_NGAY_THAY_DOI` → câu cố định tiếng Việt, không đính kèm đầu vào/ngoại lệ gốc. Xung đột kho → `MASK_XUNG_DOT`, `thu_lai_duoc=True`.

### 2.4 Cấu hình máy và dữ liệu tạm

Theo `GIAO-CODEX-THU-TU.md` §2:

| Thành phần | Cách làm tạm | Khi có Core |
|---|---|---|
| `cau_hinh_may.py` | JSON ngoài gói: `KTT_ENGINE_CAU_HINH`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_mask\cau_hinh.json`; schema trong gói. Khai vị trí tài nguyên detector sạch và giới hạn kỹ thuật đã được chốt; không khóa, danh mục, tên người/module hoặc cờ tự cấp quyền. Thiếu tệp vẫn khởi động; việc cần cấu hình báo `MASK_CHUA_CAU_HINH`. Linux dùng đường DEMO tường minh, không tự ghi vào đường Windows. | Đổi nguồn đọc sang cấu hình Core, giữ schema |
| `kho_tam.py` | JSON tại `KTT_ENGINE_DU_LIEU`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\e_mask\du-lieu\`; ghi nguyên tử qua tệp tạm + `os.replace`, khóa tệp đa tiến trình trên Windows/Linux. Chỉ băm, mã, số đếm/trạng thái mã hóa bằng mã; giữ dấu chống đếm lặp, tham chiếu mã yêu cầu/bí danh, phiên bản, mã tương quan. | Ngăn engine, CAS/duy nhất/ghi lô nguyên tử |
| Bảng tên gốc–bí danh, cụm chờ, chủ yêu cầu | Là dữ liệu lâu dài, **không thể thay bằng băm để mở che**. Giới hạn kho tạm không cho ghi nội dung này. Đợt 1: port kho + bên cấp quyền được tiêm trong test, kho DEMO ở fixture RAM ngoài gói. Bản chạy thường không có port thật thì `MASK_KHO_CHUA_NOI`, không tự dựng kho tệp chứa tên gốc hay fallback RAM. | Ngăn riêng engine có quyền hạn chế; không SQL/route riêng Mask |
| Nội dung tài liệu | Xử lý RAM; nếu thư viện buộc cần tệp, chỉ thư mục tạm riêng của việc, dọn `finally` cả thành công/lỗi/hủy; không cache input/output trong kho tạm hoặc gói. | Kho tệp/kết quả của Core, kiểm quyền cả lúc đọc lại |
| “Chưa rõ” | Mask thuần thường không có nguồn ngoài. Chỉ khi bên lưu trữ **đã nhận chốt mà chưa xác nhận**: lưu mã/băm trong kho tạm, `raise ChuaRo(ma_tuong_quan)`; lần giao lại hỏi trạng thái qua port trước, không cấp mã/đếm/chốt lần nữa. Không ghi kết quả mở che xuống JSON để phục hồi. | Lượt bền #10 và đối soát ghi ngăn/kết quả |

Đây là giới hạn thực tế của phương án tạm, **không phải nghiệm thu kho bí danh lâu dài**. Nếu Anh muốn giữ cả tên gốc ở kho tệp tạm, đó là ngoại lệ mới phải được chốt rõ; phiếu này không tự cấp ngoại lệ. Nhật ký kỹ thuật chỉ stderr: mã lỗi, phiên bản, băm, số đếm, thời gian; không mã yêu cầu nguyên văn, văn bản, bảng đối chiếu hoặc đường máy. Không cần bí mật Cloud/khóa mã hóa danh mục.

## 3. Các lát

Tệp trong cột cuối là tập mã dự kiến **tối đa 5 tệp/lát**, chưa tính test/tài liệu; schema/manifest cũng được tính bảo thủ. Tên Python dưới đây tương đối với `goi/e_mask/e_mask/`, trừ nơi ghi khác. Nếu phát sinh thêm tệp vượt tập này, tách lát và ước lại trước làm; không sửa `ma-nguon/`, tham chiếu hoặc Core.

| Lát | Nội dung / yêu cầu | Phụ thuộc | Giờ ước tính | Tập mã dự kiến |
|---|---|---|---:|---|
| MASK-0 | Khung SDK 2.0, cấu hình máy, kiểm độc lập — MK-1, cổng chung | — | 2 | `__init__.py`, `chay.py`, `cau_hinh_may.py`, `schemas/cau_hinh_may.schema.json`, manifest ngoài gói Python |
| MASK-1 | Lõi so khớp thuần, tách crypto/xuất Word không dùng — MK-1, 11, 21 | MASK-0 | 3 | `nguon/privacy/{__init__,types,core,company_names,person_names}.py` |
| MASK-2 | Detector, hậu kiểm, tiền/ngày — MK-2, 18, 20, 21 | MASK-1 | 3 | `nguon/privacy/{detectors,leftovers,core}.py`, `che_van_ban.py`, `tai_nguyen.py` |
| MASK-3 | Port kho/quyền, `kho_tam`, chống trùng — MK-10…13, 16…19 | MASK-2 | 5 | `kho_tam.py`, `kho_dinh_danh.py`, `kho_qua_core.py`, `quyen_yeu_cau.py` |
| MASK-4 | Phong bì và schema loại riêng — mẫu 1–4, MK-20 | MASK-3; Anh chốt đề xuất dữ liệu | 2 | `phong_bi.py`, schema `van_ban_da_che` chung + bản gói, bản gói `van_ban_tai_lieu` và `tra_loi_ai` |
| MASK-5 | Hai năng lực văn bản SDK, mở che AI — MK-12…14, 18, 20, 21 | MASK-4 | 5 | `chay.py`, `che_van_ban.py`, `phong_bi.py`, `kho_dinh_danh.py`, `engine.json` |
| MASK-6 | Duyệt/từ chối, đóng/dọn và chuyển danh mục DEMO qua port — MK-11, 15…19, 22 | MASK-5 | 3 | `duyet_dinh_danh.py`, `kho_dinh_danh.py`, `kho_qua_core.py`, `e_mask/cong-cu/chuyen_danh_muc_demo.py` |
| MASK-7 | Báo cáo mức hỗ trợ tệp, DEMO đo trần, phương án phần thiếu — MK-1, 4, 21 | MASK-6 | 2 | Chỉ test/tài liệu; chưa bổ sung thuật toán |
| MASK-8 | DOCX/PDF có chữ → văn bản đã che — mẫu 5–6, MK-4, 5 | MASK-7; phần thiếu/trần được chốt | 4 | `doc_tep.py`, `doc_word.py`, `doc_pdf.py`, `chay.py`, `engine.json` |
| MASK-9 | XLSX → văn bản hoặc tệp, quét phần ẩn — mẫu 5–6 | MASK-8; phương án Excel được chốt | 5–7 | `nguon/privacy/{excel,excel_values}.py`, `tep_excel.py`, `chay.py`, `engine.json` |
| MASK-10 | Che DOCX giữ định dạng và quét vùng ẩn — mẫu 5–6 | MASK-9; nguồn/phương án Word được chốt | 6–10 | `tep_word.py`, `doc_word.py`, `nguon/privacy/docx_revisions.py`, `chay.py`, `engine.json` |
| MASK-11 | Mở che DOCX/XLSX sau AI sửa, đúng quyền — mẫu 7–8, MK-3, 13, 14, 16 | MASK-9, 10; phần mở che được chốt | 6–10 | `mo_tep_word.py`, `mo_tep_excel.py`, `phong_bi.py`, `chay.py`, `engine.json` |
| MASK-12 | DEMO đầy đủ, HTTP Core giả, provenance/lock/máy sạch — MK-1, 6, 20…22 | MASK-5, 6 và các lát tệp được duyệt | 4 | `requirements.lock`, `tests/kiem_may_sach.sh`, `tests/KIEM-MAY-SACH.cmd`; còn lại test/tài liệu |
| MASK-13 | Công cụ thử máy Windows/Core DEMO, Anh chạy | MASK-12; Core thật đủ cửa thì mới thử tích hợp | 2 | `e_mask/cong-cu/thu_mask_that.py`, `e_mask/cong-cu/THU-MASK-THAT.cmd` |
| | **Tổng 14 lát, có điều kiện** | | **52–62** | |

MASK-7 là mốc trình phần thiếu, không phải quyền tự xây Word/Excel mới. Nguồn hiện có: Word chỉ `make_docx` dựng mới, chưa che DOCX gốc/mở mềm; Excel giữ XML một phần, không che được mọi tên sheet/chart/công thức và chưa mở che tệp. `excel_values` có cắt ô 32.767 ký tự/đổi tên sheet, **không thay cho giữ định dạng**. Tài nguyên detector sạch chưa có. Các khoảng thiếu này vẫn phải ghi vào `VIEC.md`, kể cả khi test DEMO của phần đã hỗ trợ đạt.

Ngoài phạm vi engine: UI duyệt Admin/lọc kiểu Excel, UI Chạy thử chung, quyền đọc kết quả/tệp, cấp danh tính/mã yêu cầu, ngăn dữ liệu và đối soát J8b phía Core. Không dựng màn/cổng HTTP/SQL riêng để bù. Bài trình duyệt 11 bước (1, 2, 3, 4, 4b, 5, 6, 7, 8, 9, 10), **135 phút ước tính**, do Anh/lead chạy sau nối Core; ca scan chưa nối OCR ghi riêng “chưa kiểm”.

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

Mỗi khối tự đủ để giao một lát. Mọi PR cập nhật `VIEC.md`/CHANGELOG của gói nếu có, ghi giờ thực tế và “đã kiểm bằng Core giả (CoreGia)”. Các lát khung còn `CHUA_LAM` phải báo đúng phần chưa đạt DEMO nghiệp vụ; không tạo kết quả giả để làm xanh. Từ MASK-5 dùng bộ chạy DEMO có fixture CoreGia nêu trong khối; đó là cổng thay thế lệnh CLI SDK mặc định khi chưa có kho/quyền/tài nguyên Core. `pytest` và `kiem_doc_lap.py` vẫn bắt buộc cho các lát code.

### MASK-0 — Khung gói SDK 2.0
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, docs/goi-gui-engine/sdk-2.0.0/HUONG-DAN-VIET-ENGINE.md và MAU-PHIEU-ENGINE.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md và QUYET-DINH-CUOI-e_mask.md.
Làm MASK-0 cho e_mask, chỉ dữ liệu DEMO:
1. Tạo e_mask/goi/e_mask/ theo AGENTS.md §3; dùng SDK wheel 2.0.0 trong repo, Python >=3.11, Windows dùng .venv/Scripts/python. Khung engine.json theo phiếu §2, ban đầu chỉ hai năng lực văn bản; handler nhận/trả đúng loại thiết kế nhưng tạm raise LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất."). Không kích hoạt gói vận hành.
2. Tối đa 5 tệp mã: __init__.py, chay.py, cau_hinh_may.py, schema cấu hình, engine.json. Không chép vỏ socket/Bootstrap/SDKEngine, không import kho_tri_thuc.*.
3. cau_hinh_may đọc JSON ngoài gói từ KTT_ENGINE_CAU_HINH, mặc định %PROGRAMDATA%/KhoTriThuc/engines/e_mask/cau_hinh.json; schema riêng trong gói, không thêm khóa manifest ngoài API. Thiếu tệp không làm tiến trình chết; khi cần thì LoiNghiepVu MASK_CHUA_CAU_HINH. Không danh mục/tên gốc/bí mật/danh tính trong cấu hình. Linux dùng đường DEMO tường minh.
4. Tạo e_mask/tests/kiem_doc_lap.py: quét AST/import và tệp trong goi/, cấm kho_tri_thuc.*, socket cũ, shim, __pycache__/.pyc/symlink; mã thoát 0/1. Chặn SQL/driver CSDL và tham chiếu nguồn ngoài.
Test: Engine.tu_khai_bao đọc phiếu; CoreGia().chay_thu nhận lỗi CHUA_LAM đúng, không XONG giả; cấu hình thiếu/hỏng/khóa lạ không lộ đường dẫn. Chạy pytest e_mask/tests -q và kiem_doc_lap; báo rõ cổng DEMO nghiệp vụ còn chưa đạt do stub. Không sửa ma-nguon/, Core hay bộ SDK.
```

### MASK-1 — Chuyển lõi so khớp thuần
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md §1–3 và QUYET-DINH-CUOI-e_mask.md. Làm MASK-1 sau MASK-0, chỉ DEMO.
Chép tối đa 5 tệp nguon/privacy/{__init__,types,core,company_names,person_names}.py từ e_mask/ma-nguon/ sang goi/e_mask/e_mask/; ghi đường nguồn, SHA trước/sau và điều chỉnh trong NGUON.md của gói. Không sửa nguồn cũ.
- Giữ matcher KnownText, chuẩn hóa, vị trí, bảo vệ số và numeric_review; chuyển định dạng bí danh sang [[...]] phù hợp mã Junsky/mã tự sinh, không cấp lại mã Junsky hoặc cắt số thứ tự lớn.
- Tách phần không dùng trong bản chép: encrypt/decrypt bảng, xuất Word mới, import cryptography/python-docx tương ứng. Không khởi chạy nguồn ngoài, OCR, server hoặc AI. Trì hoãn import detector tới MASK-2 để lõi cần dùng vẫn import/test được ở lát này.
- Không gọi suggest làm bộ che tự động vì nó cắt 500 dòng. Không dùng ví dụ [CONG_TY_001] làm bí danh phát hành.
Test thuần DEMO: NFC/NFD, khoảng trắng, tên dài ưu tiên, mã số không bị coi nhầm là tiền/ngày; giữ 1.000.000 VND và 30/10/2026. CoreGia vẫn kiểm stub CHUA_LAM; không tuyên bố che đã hoàn tất. Lỗi ra cổng dùng LoiNghiepVu tiếng Việt theo phiếu, không in cụm gốc từ PrivacyError. Chạy pytest/kiem_doc_lap; cập nhật VIEC.md và nguồn gói, không thêm thư viện ngoài SDK ở lát này.
```

### MASK-2 — Detector và hậu kiểm an toàn
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md và QUYET-DINH-CUOI-e_mask.md. Làm MASK-2 sau MASK-1.
Tối đa 5 tệp mã: chép/sửa nguon/privacy/detectors.py, leftovers.py, core.py, che_van_ban.py; thêm tai_nguyen.py trong gói mới. Tận dụng test_che_van_ban.py, tự đủ fixture DEMO ngoài gói, bỏ import tests/Core cũ.
- Đầu vào lõi: văn bản và danh sách đã biết; đầu ra nội bộ giữ kết quả che/mở cùng kiểm. Không đổi mẫu 1–4 hoặc tự cấp quyền. 500.000/500/300/20 giữ đúng phiếu; 501 cụm detector tìm được không bị cắt theo trần danh sách đã biết.
- Giữ hậu kiểm độc lập detector, Counter tiền/ngày từ bản gốc đầy đủ, số bắt đầu 0/MST/tài khoản theo ngữ cảnh; bí danh hỏng không được làm mất dấu vết. Chuỗi dài bệnh lý chưa kiểm hết phải chặn, không cắt đầu vào.
- Bốn tài nguyên vn_surnames.txt, vn_places.txt, common_acronyms.txt, leftover_allowlist.txt hiện chưa được cấp sạch. Chỉ nạp nguồn được lead whitelist qua cấu hình; chưa có thì MASK_THIEU_TAI_NGUYEN. Không tự tải/tạo từ điển thay thế. Tests mock từ vựng DEMO tường minh, dọn cache từng ca, không biến mock thành fallback vận hành.
- Còn sót/đổi tiền-ngày/lỗi detector không công bố văn bản; sau này adapter đổi thành LoiNghiepVu MASK_DINH_DANH_CHUA_DAT hoặc MASK_TIEN_NGAY_THAY_DOI bằng câu cố định, không nội dung gốc.
Test DEMO gồm đúng/vượt trần, NFD/vị trí, nhãn nhiều dòng, mất/thêm tiền-ngày, thiếu một tài nguyên, lỗi detector; giữ test hiệu năng 3 chuỗi 500.000 ký tự, không tự nới ngưỡng cũ. CoreGia vẫn kiểm đường stub; pytest và kiem_doc_lap phải có kết quả thật. Ghi giới hạn heuristic tên người viết thường không nhãn; chưa chứng minh đủ điều kiện Cloud. Không sửa ma-nguon/ hay gọi engine khác.
```

### MASK-3 — Kho tạm, quyền và chốt chống trùng
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md §2–3, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md §2.4 và QUYET-DINH-CUOI-e_mask.md. Làm MASK-3 sau MASK-2, chỉ DEMO.
Tối đa 4 tệp mã: kho_tam.py, kho_dinh_danh.py, kho_qua_core.py, quyen_yeu_cau.py. Tái dùng protocol Kho và nguyên tắc snapshot/nhật ký/chốt của ma-nguon/kho_qua_core.py; bỏ import SDK cũ/goi_mask/SQL, không tự sáng tác API ngăn.
- kho_tam đúng KTT_ENGINE_DU_LIEU/mặc định ProgramData của phiếu: ghi tạm + os.replace, khóa tệp đa tiến trình Windows/Linux. Chỉ mã/băm/số đếm; không tên gốc, bảng ánh xạ, toàn văn hoặc kết quả mở che. Lỗi/hỏng/không ghi được -> LoiNghiepVu MASK_KHO_TAM_LOI, không fallback RAM âm thầm.
- Kho bí danh lâu dài/quyền là port chưa có transport SDK 2.0: mặc định MASK_KHO_CHUA_NOI hoặc MASK_NGU_CANH_CHUA_XAC_MINH. Không lấy module/người gửi từ tham_so/dau_vao/phap_nhan_id. Core cấp mã yêu cầu ổn định, kiểm quyền cả snapshot, chốt và đọc lại.
- Test dùng KhoBoNho chuyển vào tests/ho_tro_core_gia.py, không gói chạy; fixture tin cậy gắn phiên/module/người/tài liệu và cấp mã. Bảng chung toàn tập đoàn, tách DEMO/thật, không chia bí danh theo pháp nhân. Chốt nguyên tử alias mới/hàng chờ/đếm gặp/tham chiếu/yêu cầu; xung đột -> MASK_XUNG_DOT, thu_lai_duoc=True.
- Retry cùng việc/bước dùng cùng mã ổn định, không tính lan_thu vào khóa, không cấp alias/đếm mới. Bên lưu trữ đã nhận chốt chưa trả thì ghi mã/băm rồi raise ChuaRo; giao lại hỏi port trước. Mất ACK kết quả SDK để SDK xử lý, không dựng lại vòng gửi cũ.
Test bằng CoreGia + port kho/quyền giả: toàn bộ vector_kho_luot.json hiện có, hai tiến trình tranh ghi, rollback, gặp lại, retry/khởi động lại engine với cùng bên kho giả, sai module/người/mã đã đóng, ChuaRo. Kiểm byte kho tạm không có tên DEMO/toàn văn. Không gọi đây là bằng chứng bền PostgreSQL. Ghi Cần Core về ngăn/CAS/danh tính/mã yêu cầu và chạy pytest/kiem_doc_lap.
```

### MASK-4 — Phong bì và schema dữ liệu chung
```
Đọc AGENTS.md, API-ENGINE-v1.md b.2–b.5, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md gồm đề xuất MASK-P, e_mask/docs/GIAO-CODEX-e_mask.md và QUYET-DINH-CUOI-e_mask.md. Làm MASK-4 sau MASK-3; phần đề xuất chưa được chốt thì giữ nó là đề xuất, chưa phát hành schema thay nghĩa.
Tối đa 5 tệp mã/schema: phong_bi.py, _chung/contract/van_ban_da_che.schema.json và bản chép trong gói, bản chép schema van_ban_tai_lieu/tra_loi_ai trong gói. Không sửa hai schema chung đã có hoặc docs/goi-gui-engine/.
- Phong bì loại riêng theo {loai: ma, ma: payload}; van_ban_da_che đủ 6 trường gốc của §2.4 sổ chung, bổ sung báo cáo tùy chọn đúng phần được duyệt. So SHA bản chung/bản gói trong test, gói không đọc _chung lúc chạy.
- Chỉ nhận/ra 3 loại gốc và mã riêng đã khai; truong_ra bộ M/C/T đúng phiếu, mảng/object thành chuỗi JSON có kiểm cấu trúc, null khi không có giá trị. Không thêm khóa root để mang quyền hoặc mã yêu cầu.
- Kiểm JSON UTF-8/khóa trùng/NaN, trần văn bản lồng 500.000, chuyen_tiep 64 KiB JSON UTF-8. Không bỏ dữ liệu thừa bằng cắt ngầm. Cụm gốc/metadata OCR gốc không đi vào chuyen_tiep hoặc báo cáo che.
- LoiNghiepVu MASK_DAU_VAO/MASK_QUA_GIOI_HAN cho payload sai; chưa tạo van_ban_da_che nếu con_sot khác [] hoặc kiem_tien_ngay không true.
Test DEMO: shape hợp lệ/sai, trường tùy chọn không đổi phiên bản 1, biên UTF-8, tên loại khớp Hỏi AI, bản gói độc lập; CoreGia kiểm lỗi/loại phong bì, không giả định SDK tự kiểm schema loại riêng. Chạy pytest/kiem_doc_lap, cập nhật VIEC.md; không sửa ma-nguon/.
```

### MASK-5 — Che và mở che văn bản qua SDK
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md §2 và QUYET-DINH-CUOI-e_mask.md §3, §5.1. Làm MASK-5 sau MASK-4.
Tối đa 5 tệp mã: chay.py, che_van_ban.py, phong_bi.py, kho_dinh_danh.py, engine.json. Viết handler @app.nang_luc cho mask.che_van_ban@1 và mask.mo_che_van_ban@1, dùng viec.dau_vao/tham_so/ngu_canh/mo_tep, không socket cũ.
- Che nhận van_ban/van_ban_tai_lieu hoặc tệp JSON mẫu 1, trả van_ban_da_che. Mã yêu cầu do port Core tin cậy cấp; cụm nghi ngờ che ngay bằng alias tạm và ghi chờ. Hậu kiểm tiền/ngày/còn sót đạt và chốt kho rồi mới return; thất bại -> LoiNghiepVu MASK_DINH_DANH_CHUA_DAT/MASK_TIEN_NGAY_THAY_DOI, không trả nội dung chưa đạt.
- Mở nhận tệp JSON mẫu 3 hoặc tra_loi_ai có chuyen_tiep.ma_yeu_cau, trả bộ truong M đúng phiếu. Kiểm quyền trước tra; mã thiếu/sai/khác module/người/đã đóng -> MASK_MA_YEU_CAU. Không dùng mã như mật khẩu. Tra chính thức + tạm toàn bảng, mở mềm hoa/thường/khoảng trắng, giữ phần AI thêm; bí danh lạ/hỏng -> danh sách + vị trí, giữ yêu cầu mở, không đoán.
- Với tra_loi_ai mở cả tra_loi, giá trị chuỗi du_lieu và câu trích; không bỏ cấu trúc. Trả bản AI trong tra_loi_ai_da_mo_json, hạ kiểm trích dẫn đã đổi chữ thành cần kiểm lại, không tự nhận offset mới là đúng. dong_viec mặc định false, chỉ đóng khi yêu cầu rõ và mở đủ.
- Gọi tien_do/kiem_huy trước-sau xử lý/chốt; stderr chỉ mã/băm/số đếm/thời gian. Mất lease dừng, không nộp; để SDK retry cùng Idempotency-Key. Không bật Cloud hoặc gọi Hỏi AI/OCR.
Tạo tests/chay_demo.py: tiêm kho/quyền/từ vựng DEMO, chạy CoreGia().chay_thu_demo(app); không có chế độ DEMO mở kho giả trong gói. README ghi lệnh này thay CLI kho_tri_thuc_sdk.thu vì CLI mặc định thiếu các port. CoreGia không có sẵn kho/danh tính Mask; fixture phải khai rõ.
Test chỉ DEMO: khứ hồi Công ty DEMO Ánh Dương, 1.000.000 VND, 30/10/2026; trực tiếp/OCR; cụm mới không lộ; 500.000/500.001; sai quyền; tra_loi_ai có du_lieu/trích dẫn; alias chưa mở/dong_viec; gay_mat_xac_nhan("ket_qua")/"ket_thuc" không chốt/đếm trùng; hủy. Chạy chay_demo.py, pytest e_mask/tests -q, kiem_doc_lap.py; ghi “đã kiểm bằng Core giả (CoreGia)”.
```

### MASK-6 — Duyệt danh sách chờ và vòng đời bí danh
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, QUYET-DINH-CUOI-e_mask.md §3 và YEU-CAU-VA-HIEN-TRANG.md. Làm MASK-6 sau MASK-5, chỉ DEMO.
Tối đa 4 tệp mã: duyet_dinh_danh.py, kho_dinh_danh.py, kho_qua_core.py trong gói và e_mask/cong-cu/chuyen_danh_muc_demo.py ngoài gói. Logic qua port kho/quyền chung, chưa tạo UI/route/SQL hoặc năng lực Admin tin cờ caller.
- Admin đã được bên tin cậy xác minh mới xem/duyệt/từ chối. Duyệt cấp mã chính thức (giữ mã Junsky nếu có), alias tạm cũ sang cột tạm; từ chối bỏ hàng chờ, không làm mất tham chiếu cần mở của yêu cầu còn xử lý. Dọn chỉ khi không còn yêu cầu DANG_XU_LY dùng; tệp ở ngoài giữ trạng thái đó.
- Khóa/CAS chống dọn trúng alias đang được lượt mới tham chiếu; nhiều yêu cầu dùng cùng alias phải còn mở được sau duyệt. Không chia danh mục theo pháp nhân, không tự áp hạn lượt cũ.
- Chuyển danh mục DEMO: tận dụng quy tắc chuẩn hóa/kiểm trùng từ công cụ cũ nhưng bỏ kết nối CSDL/SQL; port giả cấp/tra mã. Mặc định chạy khô, chỉ thống kê số dòng trước/sau, lỗi theo loại. Không đọc danh mục thật, không suy mã Junsky từ token cũ, không ghi đè khi xung đột tiền tố/nhóm.
- LoiNghiepVu MASK_KHONG_CO_QUYEN hoặc MASK_MA_YEU_CAU cho quyền sai; thiếu cửa thật vẫn MASK_KHO_CHUA_NOI; mọi câu cố định tiếng Việt, không cụm gốc.
Test CoreGia + kho/quyền giả DEMO: Admin/người thường, duyệt/từ chối/gặp lại, hai yêu cầu giữ một alias, dọn đồng thời mở che, đóng rõ ràng, chuyển lần hai không thêm trùng, tiền tố trùng bị từ chối. UI lọc kiểu Excel và quyền đọc kết quả ghi Cần Core, không đánh dấu đã làm UI. Chạy chay_demo.py/pytest/kiem_doc_lap; cập nhật VIEC.md.
```

### MASK-7 — Chốt mức hỗ trợ và phương án tệp
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, QUYET-DINH-CUOI-e_mask.md §2.2, §3, §5.2, ma-nguon/NGUON.md §4 và nguon/PHU-THUOC.md. Làm MASK-7 sau MASK-6, chỉ khảo sát/test DEMO, không thêm thuật toán hoặc năng lực tệp.
Lập bảng bằng chứng từng vùng: Word thân/đầu-chân/footnote-endnote/bình luận/lịch sử sửa/thuộc tính; Excel tên sheet/sheet ẩn/ô ẩn/bình luận/chart/thuộc tính/công thức/liên kết ngoài. Đọc đúng mã nguồn trong repo, không mở kho dữ liệu nguồn ngoài.
- Word make_docx chỉ dựng mới, accept_tracked_changes có thể trả nguyên byte khi không an toàn; chưa có che DOCX gốc/mở mềm. Excel có blocker và disclosures chưa che, chưa có unmask; excel_values cắt ô/đổi sheet, không thay đầu ra giữ định dạng.
- Tạo DEMO trong tests, không tệp lớn trong goi/. Đo byte nén/giải nén, ký tự vào/ra, RAM/thời gian ở các kích thước thử; ghi số đo và môi trường, không bịa ngưỡng. Trình lead/Anh trần tệp, đầu ra và giới hạn ZIP; 20/80 MiB, 4 MiB chỉ là số kỹ thuật cũ để đối chiếu.
- Trình nguồn sạch cần bổ sung hoặc phương án/tập tệp/giờ mới cho MASK-8…11; chưa được chốt thì chưa code phần thiếu. Chọn PDF yêu cầu tệp -> từ chối rõ, scan -> Core OCR; không gọi OCR trong Mask.
Kiểm CoreGia DEMO văn bản đang có vẫn đạt; lỗi tệp chưa hỗ trợ thiết kế là LoiNghiepVu MASK_TEP_CHUA_HO_TRO/MASK_TEP_CHUA_CHOT_GIOI_HAN, không thành công rỗng. Báo cáo ghi “đã kiểm bằng Core giả (CoreGia)” và phần chưa kiểm. Nếu lát chỉ sửa tài liệu thì kiểm khối lệnh/UTF-8/diff; nếu thêm test thì chạy bộ tương ứng và kiem_doc_lap. Không sửa ma-nguon/, Core, SDK hoặc tạo UI.
```

### MASK-8 — Đọc DOCX và PDF có chữ để che văn bản
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md và kết luận MASK-7, QUYET-DINH-CUOI-e_mask.md §5.2. Làm MASK-8 sau MASK-7, chỉ phần nguồn/phương án và trần đã được chốt; chưa có thì ghi Chờ Anh, tiếp tục phần độc lập đã được phép.
Tối đa 5 tệp mã: doc_tep.py, doc_word.py, doc_pdf.py, chay.py, engine.json. Viết mask.che_tep_van_ban@1 cho DOCX/PDF có lớp chữ; nhận tep hoặc JSON mẫu 5 có tham chiếu tệp cùng việc, trả van_ban_da_che. XLSX bổ sung ở MASK-9; chỉ khai MIME đã đạt.
- Đọc bytes bằng viec.mo_tep, kiểm độ dài thực và giới hạn được duyệt; JSON không cho đọc path/URL hoặc giả quyền. Dò tất cả vùng có chữ, gắn vị trí nội bộ, không chỉ lấy thân Word/bản xem trước. Vùng không đọc/quét đủ -> LoiNghiepVu MASK_TEP_CHUA_HO_TRO, không lấy phần đọc được để báo đạt.
- PDF chỉ đọc lớp chữ, không render/OCR; trang scan/thiếu chữ -> MASK_PDF_CAN_OCR. Có thể chép phần đọc chữ thuần từ e_ocr/ma-nguon/lop_chu.py sau bỏ nhãn ABBYY/luồng chọn OCR; không import/gọi e_ocr. Cho phép tập dependency PDF đã ghim ở e_ocr/ma-nguon/requirements.lock, chỉ phần thực dùng và bắc cầu, kiểm artifact/hash/giấy phép trong gói riêng; thiếu artifact offline thì ghi Cần cài, không tải mạng hoặc đoán hash. DOCX ưu tiên zip/XML stdlib, không cần Office COM.
- Che bằng lõi MASK-5, giữ tiền/ngày, hậu kiểm và chốt kho trước trả; không có mapping/cụm gốc trong phản hồi. Tệp tạm nếu có dọn finally cả lỗi/hủy. Gọi kiem_huy giữa trang/phần.
Test chỉ DEMO với CoreGia/kho giả: DOCX/PDF có tiền-ngày và vùng ẩn, PDF lẫn trang scan, tệp hỏng/mật khẩu/sai MIME, quá trần, ZIP bất thường, hủy, tham chiếu tệp khác việc bị từ chối; không nối OCR/Cloud. Chạy chay_demo.py/pytest/kiem_doc_lap; ghi giới hạn thật, không sửa ma-nguon/ hay SDK.
```

### MASK-9 — Che Excel và giữ phần ẩn
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, kết luận MASK-7 và QUYET-DINH-CUOI-e_mask.md §2.2. Làm MASK-9 sau MASK-8; phần Excel thiếu chỉ làm khi nguồn/phương án được chốt.
Tối đa 5 tệp mã: nguon/privacy/excel.py, excel_values.py (nếu còn được tham chiếu), tep_excel.py, chay.py, engine.json. Chép từ ma-nguon/ rồi sửa ở gói mới, không sửa nguồn cũ. Không thêm dependency Excel nếu chưa cần, lõi hiện dùng stdlib.
- Bổ sung XLSX cho mask.che_tep_van_ban@1 -> van_ban_da_che, và mask.che_tep_giu_dinh_dang@1 -> bộ truong C, tep_da_che cùng XLSX qua viec.tai_tep_ra. Cùng mã yêu cầu/quyền/hậu kiểm của MASK-5.
- Chuyển rule/token sang [[...]], không dùng validate_rules/suggest cũ để cắt 500 cụm. Quét tên sheet, sheet/ô ẩn, shared/inline/rich text, bình luận, nhãn chart, thuộc tính và dữ liệu giữ lại. Chỗ chưa xử lý được, công thức/liên kết ngoài/disclosures còn định danh -> LoiNghiepVu MASK_TEP_CHUA_HO_TRO/MASK_DINH_DANH_CHUA_DAT, không “giữ nguyên có cảnh báo” rồi báo che đủ.
- Giữ byte/giá trị tiền-ngày ở ô số, công thức/định dạng/ô gộp/bố cục trong phạm vi đã kiểm. Không fallback excel_values bản chỉ giá trị, không cắt ô 32.767 ký tự hoặc đổi tên sheet âm thầm. Không trả changes/disclosures chứa tên gốc/đường nguồn.
- vung_da_quet chỉ liệt kê vùng thật đã kiểm bằng mã/chỉ số an toàn; kiểm ZIP/XML/trần được duyệt, không tệp gốc còn trên đĩa. Không trả tệp nếu hậu kiểm/chốt lỗi; hủy đúng lúc trước upload/chốt.
Test CoreGia chỉ DEMO: sheet/ô ẩn, tên sheet/bình luận/chart/thuộc tính, ô số 1000000 VND và ngày, ô gộp/định dạng, formula/link blocker, XLS/XLSM/XLSB từ chối, tệp >trần. Ca thiếu hỗ trợ phải lỗi rõ, chưa công bố là đạt đủ Excel. Chạy chay_demo.py/pytest/kiem_doc_lap, cập nhật VIEC.md/NGUON.md/CHANGELOG.
```

### MASK-10 — Che Word giữ định dạng
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, kết luận MASK-7 và QUYET-DINH-CUOI-e_mask.md §2.2. Làm MASK-10 sau MASK-9, chỉ sau khi nguồn sạch/phương án bổ sung Word được chốt; không tự viết thay phần chưa được duyệt.
Tối đa 5 tệp mã: tep_word.py, doc_word.py, nguon/privacy/docx_revisions.py, chay.py, engine.json. Bổ sung DOCX cho mask.che_tep_giu_dinh_dang@1, nhận tep/JSON mẫu 5, trả bộ truong C có DOCX cùng định dạng bằng viec.tai_tep_ra.
- Che đủ thân, đầu/chân trang, footnote/endnote, bình luận, lịch sử sửa và thuộc tính; tên bị tách nhiều run vẫn che đủ. Giữ format, bảng/ô gộp và phần không cần thay. core.make_docx dựng mới không phải giải pháp giữ bố cục.
- Không dùng accept_tracked_changes để tự bỏ lịch sử/nội dung chưa che; helper trả nguyên byte không phải chứng nhận an toàn. Vùng/đối tượng chưa hỗ trợ -> LoiNghiepVu MASK_TEP_CHUA_HO_TRO, còn định danh/tiền-ngày sai -> MASK_DINH_DANH_CHUA_DAT/MASK_TIEN_NGAY_THAY_DOI.
- Dùng mã yêu cầu/quyền/kho và hậu kiểm như MASK-5; mọi vùng thật đã quét nằm trong báo cáo không chứa cụm gốc. Kiểm ZIP/XML/trần được duyệt, dọn tạm finally, hủy trước chốt/upload. Không Word COM, OCR, AI hoặc nguồn ngoài.
Test bằng CoreGia và port giả, chỉ DEMO: tên ở toàn bộ vùng ẩn, run tách/format, tiền 1.000.000 VND/ngày 30/10/2026, bảng/bố cục, thành phần chưa hỗ trợ, lỗi và hủy không còn bản gốc trên đĩa. Kiểm lại XML/DOCX thực trả, không chỉ preview; ghi phần cần Anh mở trên Word ở MASK-13. Chạy chay_demo.py/pytest/kiem_doc_lap và ghi đúng “đã kiểm bằng Core giả (CoreGia)”.
```

### MASK-11 — Mở che tệp sau AI sửa
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, kết luận MASK-7 và QUYET-DINH-CUOI-e_mask.md §2.2, §3, §5.2. Làm MASK-11 sau MASK-9/10 và khi phương án mở che tệp được chốt; nguồn hiện chưa có chức năng này.
Tối đa 5 tệp mã: mo_tep_word.py, mo_tep_excel.py, phong_bi.py, chay.py, engine.json. Viết mask.mo_che_tep@1: nhận tep JSON mẫu 7 có mã yêu cầu và tham chiếu DOCX/XLSX cùng việc, trả bộ truong T, tệp cùng định dạng qua viec.tai_tep_ra.
- Kiểm mã/module/người gửi và quyền tệp qua port tin cậy trước đọc/tra/upload. Thiếu/sai mã hoặc quyền -> LoiNghiepVu MASK_MA_YEU_CAU; không coi sở hữu tep_id hoặc biết mã là đủ quyền.
- Tra toàn bảng chính thức + tạm; nhận bí danh đổi hoa/thường/thừa khoảng trắng/tách run Word, giữ nội dung AI thêm và định dạng. Mở cả vùng ẩn đã hỗ trợ, kiểm tiền/ngày kể cả ô số Excel. Không đoán bí danh hỏng/lạ.
- Còn alias chưa mở -> vẫn trả tệp đúng quyền, bi_danh_khong_ro_json kèm sheet/ô hoặc phần/đoạn/offset, mo_day_du=false, giữ DANG_XU_LY. dong_viec mặc định false; chỉ đóng khi yêu cầu rõ và không còn bí danh chưa mở. Giữ tham chiếu tạm tới lúc đóng, không dọn vì tệp ở ngoài quá lâu.
- Tệp hỏng/vượt trần/vùng không kiểm được -> LoiNghiepVu tiếng Việt, không đường dẫn/nội dung. Dọn tạm khi lỗi/hủy, không cache bản gốc hay bản mở che trong kho_tam.
Test CoreGia DEMO với AI sửa giả lập bằng mã test, không gọi AI: thêm đoạn, hoa/thường, thừa dấu cách, tách run, một alias hỏng; giữ đoạn mới/tiền/ngày/format và vị trí. Thử sai module/người, mã đóng, dọn đồng thời, hủy/upload mất ACK không trùng. Chạy chay_demo.py/pytest/kiem_doc_lap, cập nhật trạng thái theo mức đã kiểm.
```

### MASK-12 — DEMO tổng thể và gói máy sạch
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md và QUYET-DINH-CUOI-e_mask.md §4–5. Làm MASK-12 sau MASK-5/6 và các lát tệp đã được duyệt; phần chưa được duyệt ghi chưa kiểm, không mô phỏng thành chức năng có thật.
Tối đa 3 tệp mã triển khai ngoài test: requirements.lock, tests/kiem_may_sach.sh, tests/KIEM-MAY-SACH.cmd (ASCII). Còn lại test/DEMO nhỏ/NGUON.md/README/CHANGELOG/VIEC.md, không sửa ma-nguon/ hay SDK.
- Chạy chay_thu_demo qua tests/chay_demo.py tiêm fixture kho/quyền/từ vựng DEMO bên ngoài gói, dùng CoreGia thật của SDK. Bài 11 bước của quyết định: phần engine kiểm tự động; UI/quyền Core thật/scan OCR chưa nối ghi rõ chưa kiểm. Không gọi Cloud, đếm 0 lời gọi engine khác/nguồn ngoài.
- Thêm test MayChuGia HTTP loopback cho app.chay đọc dòng stdin, không dựa API/private SDK cũ. Test thành công của port nội bộ không biến thành chứng nhận Core có ngăn/quyền. Bản mặc định không có port phải raise LoiNghiepVu MASK_KHO_CHUA_NOI/MASK_NGU_CANH_CHUA_XAC_MINH với câu tiếng Việt cố định.
- Test mất xác nhận ket_qua/ket_thuc/tep cùng Idempotency-Key không ghi/chốt/đếm trùng; hủy/mất lease; restart engine khi chốt chưa rõ; đồng thời duyệt/dọn; lỗi không lọt tên gốc vào log/phản hồi che/kho tạm. Kiểm chính bytes DOCX/XLSX trả về, trần văn bản 500.000, không tệp gốc còn sau việc.
- Chép nguồn sạch/giấy phép nội bộ, lập NGUON.md đường cũ->mới + SHA, ghi tài nguyên detector và giới hạn heuristic. requirements.lock chỉ deps thật dùng và bắc cầu, pin+hash artifact được kiểm Windows x64/Linux. Không tự dùng pin lịch sử thay bằng chứng artifact; cryptography chỉ giữ nếu dependency PDF thực cần, không khôi phục mã hóa danh mục. Thiếu wheel thì báo Cần cài, không tải mạng trong lát offline.
- Script máy sạch tạo venv riêng, cài SDK wheel --no-index --no-deps rồi deps đã ghim từ kho wheel được chỉ định; không thay deps Core. Ngăn tạo pycache bằng -B/PYTHONDONTWRITEBYTECODE; kiểm độc lập gói không symlink/.pyc/tệp lớn.
Chạy và dán kết quả thật: python e_mask/tests/chay_demo.py (cổng thay thế python -m kho_tri_thuc_sdk.thu vì thiếu port Core), python -m pytest e_mask/tests -q, python e_mask/tests/kiem_doc_lap.py; dùng .venv/Scripts/python trên Windows. Không ghi “SẴN SÀNG”; ghi “đã kiểm bằng Core giả (CoreGia)”, số ca đạt/skip và lý do. Không đăng ký tám tên contract lịch sử thành API riêng khi Core chưa duyệt.
```

### MASK-13 — Công cụ thử trên máy thật, Anh tự chạy
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md §2/5, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_mask/docs/GIAO-CODEX-e_mask.md, QUYET-DINH-CUOI-e_mask.md §4 và kết quả MASK-12. Làm MASK-13, Codex KHÔNG chạy bản thật, chỉ dữ liệu DEMO.
Tạo tối đa 2 tệp mã: e_mask/cong-cu/thu_mask_that.py và THU-MASK-THAT.cmd ASCII, hướng dẫn ngắn trong README. Mặc định chạy khô: kiểm phiếu/cấu hình DEMO, in danh sách ca và điều kiện còn thiếu, không ghi kho vận hành/không mạng/không đổi Windows.
- Chế độ --that chỉ Anh tự chạy sau khi MASK-7/nguồn/trần và cửa Core cần thiết đã chốt. Dùng thư mục DEMO riêng do Anh chỉ định; không dò dữ liệu/cấu hình thật hoặc dùng mặc định ProgramData làm kho thử. Sinh DEMO có nhãn, so đáp án tiền/ngày/alias và kiểm file trả, thời gian/bộ nhớ/không còn tệp gốc. Không đọc khóa hay ghi đường máy vào báo cáo.
- Thử thư viện/khóa tệp/cleanup trên Windows bằng CoreGia thì ghi đúng “đã kiểm bằng Core giả (CoreGia)”; thiếu port thật -> LoiNghiepVu MASK_KHO_CHUA_NOI, không gọi nó là kiểm tích hợp Core.
- Chuẩn bị checklist 11 bước/135 phút ước tính cho Anh/lead bấm trong Core DEMO, mở Word/Excel kiểm bố cục và lưu ảnh/phút từng bước. Tool không bịa client gửi việc vì API engine v1 chỉ kéo việc; không tạo route riêng Mask. Thiếu ngăn/quyền/UI/chuỗi OCR thì ghi ca chưa kiểm và lý do, không chạy vòng qua cổng cũ.
- Báo cáo JSON chỉ tên ca/mã lỗi/số đếm/băm/thời gian/kết luận, không toàn văn, bảng ánh xạ, mã yêu cầu hoặc path thật. Cloud/Junsky thật và chuyển danh mục thật ngoài phạm vi.
Codex test nhánh chạy khô và --that bằng mock + CoreGia DEMO, kiểm .cmd ASCII và tham số được trích dẫn đúng; chạy bộ DEMO/pytest/kiem_doc_lap. Cập nhật VIEC.md: chờ Anh chạy máy thật, chờ lead xác nhận Core; không commit/push nếu handoff giao lead làm.
```

## 5. Cần Core / Chờ Anh của engine này

**Cần Core (qua Anh, không sửa trong project này):**

1. **Ngăn dữ liệu engine** cho bảng định danh chung, bí danh chính thức/tạm, danh sách chờ, chủ/trạng thái yêu cầu, quan hệ giữ alias và chống đếm lặp. Cần ghi lô nguyên tử, CAS/phiên bản, duy nhất theo giá trị chuẩn và bí danh, kiểm quyền trong từng thao tác; chuyển dữ liệu/cửa cũ 113, 117–120 do lead Core xử lý. `kho_tam` chỉ giữ mã/băm/số đếm, không khôi phục được tên gốc từ băm.
2. **Danh tính tin cậy và mã yêu cầu:** cổng chung cấp mã ổn định, xác minh module + người gửi + tài liệu và DEMO/thật cho engine; hiện `ngu_canh` chưa đủ. Kiểm lại khi phát lại/mở che/đọc kết quả/tải tệp; bí danh chung không phải quyền đọc chung. Xác nhận cách tệp JSON tham chiếu tệp tài liệu cùng việc đi qua `mo_tep`.
3. **Chốt ngăn và bàn giao kết quả:** đối soát mất ACK (nợ J8b), cùng mã ổn định khi giao lại; không lặp tạo/đếm/đóng yêu cầu. Lượt bền #10 khi bên lưu trữ đã nhận mà chưa trả; giữ/chốt/đọc chưa có trong đợt 1. Không dùng tên operation `snapshot_luot/chot_luot` cũ làm API riêng mới.
4. Cấu hình tới `Engine` theo `GIAO-CODEX-THU-TU` §3.1, nhật ký kỹ thuật/thẻ trạng thái, UI quản trị ngăn và màn thử chung chỉ Admin. Thiết kế màn duyệt/lọc kiểu Excel thuộc cửa chung; phiếu `PHIEU-MASK-CHAY-THU-DEMO.md` còn chờ duyệt, không nối route riêng cũ.
5. Chuỗi và nguồn sinh `van_ban_da_che`: Core kiểm nó thực sự do Mask tạo và đủ điều kiện trước bước Cloud; không chỉ tin mã loại/cờ caller tự điền. Hỏi AI bản 2 chỉ gửi nội dung đã che, không `ma_yeu_cau`, `chuyen_tiep`, báo cáo hoặc bảng đối chiếu. Bản 1 Cloud vẫn tắt; ngăn/kho giả đạt không thay bằng chứng bảo toàn và đánh giá detector khi bật Cloud.
6. Lead đối chiếu tên tám contract lịch sử và `noi_dung_da_che.v1` còn lượt/hạn/danh mục; không đổi nghĩa v1, không đăng ký route/contract riêng trái SDK 2.0. Tám mẫu nghiệp vụ được ánh xạ §2, tên cụ thể chỉ kích hoạt sau duyệt và đủ kiểm. Chuỗi mở che AI có cấu trúc nối tiếp Trích xuất cần thiết kế riêng nếu muốn giữ `tra_loi_ai` thay bộ M.

**Chờ Anh/lead:**

- Q1 (cấu hình ngoài gói), Q3 (tên loại riêng), Q4 (Cloud chỉ sau Mask) của phiếu thứ tự; bổ sung áp dụng kho tạm cho Mask trong giới hạn mã/băm/số đếm. Không mặc nhiên coi Q2 dành cho OCR là đã duyệt lưu tên gốc của Mask.
- Chốt đề xuất bổ sung `van_ban_da_che` ở cuối sổ chung; không tạo loại mới hoặc đổi trường bắt buộc cũ trong MASK-P.
- Cấp whitelist **tài nguyên detector sạch**; xác minh tiền tố tự sinh `MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC`, `MASKTAM` không trùng Junsky; cấu trúc bản xuất danh mục sạch/quan hệ tên khác. Không cấp danh mục thật làm fixture.
- MASK-7: chốt trần tệp/đầu ra sau đo DEMO, nguồn/phương án cho Word giữ bố cục, sheet/chart Excel và mở che tệp còn thiếu; cập nhật giờ trước viết phần bổ sung. Giữ nguyên điều kiện phải trình phần chưa có của quyết định 06/11.
- Duyệt màn thử DEMO/tên contract ở mức còn áp dụng cổng chung; Anh/lead chạy công cụ Windows và bài trình duyệt 11 bước sau khi Core đủ cửa. Chuyển danh mục thật là việc vận hành riêng, Anh xác nhận số dòng trước/sau.

**Kiểm riêng MASK-P:** chỉ tài liệu, không tạo `goi/`/`tests/`, không sửa `ma-nguon/`; ba lệnh kiểm gói tại AGENTS.md §5 không áp dụng theo handoff. Thay bằng đọc UTF-8, đối chiếu bảng lát/tổng giờ, `git diff --check` và trích đủ 14 khối §4 bằng regex Anh chỉ định, với cờ MULTILINE/DOTALL và mã lát `MASK-\d+`. Mọi dòng mở/đóng fence là ba backtick trơn; không language tag. Không chạy commit/push, PR do lead mở.

## 6. MASK-2c — Lớp AI cục bộ

*MASK-2c-P, 15/11/2026; chỉ tài liệu, chưa triển khai. Không đổi API v1, SDK 2.0.0, schema chung hoặc bật Cloud. Phiếu giao không nêu giờ ước tính riêng cho MASK-2c-P; giờ bên dưới chỉ dành cho các lát triển khai tương lai.*

**Quyết định của Anh 15/11/2026 (nguyên văn): "Thêm AI cục bộ"** — trước khi bật Cloud, thêm lớp AI cục bộ (Local AI) nhận diện tên người như lớp an toàn thứ hai cho Mask.

### 6.1 Căn cứ và lựa chọn

Held-out mới do lead báo trong `BAO-CAO-MASK-2b.md`: quy tắc lọt **4/45 tên**, báo nhầm **15/75 câu thường (20%)**. Đây khác tập t9/t10 cũ; không lấy 0/32 và 4,88% thay nền held-out. Không vá thêm bốn tên để tuyên bố đạt. Local AI cũng có thể bỏ sót; hai lớp là biện pháp giảm rủi ro, **0 lọt là mục tiêu đo, không phải bảo đảm toán học hoặc quyền bật Cloud**.

| Phương án | Lợi ích | Chi phí / quyết định |
|---|---|---|
| **Core điều phối Mask → Hỏi AI Local → Mask** | Đúng cổng chung; tái dùng chọn model, kiểm IP/Tailscale, JSON; tách quyền và truy vết từng bước | Cần Core giữ snapshot, lặp đoạn và ghép phản hồi. **Chọn**, thiếu cửa thì fail-closed và test bằng CoreGia |
| Mask tự gọi HTTP Local AI | Ít bước điều phối, giữ map trong cùng lời gọi | Nếu endpoint là engine thì vi phạm engine-to-engine. Nếu là model server thuần thì không tự động vi phạm điều đó, nhưng phải nhân đôi transport, chọn model, timeout, nhật ký và chính sách chống Cloud; không chọn trong MASK-2c |
| Chỉ mở rộng quy tắc/danh sách | Ít chi phí vận hành | Held-out đã cho thấy giới hạn, không thực hiện quyết định thêm lớp AI; chỉ giữ làm lớp 1 |

Phạm vi đầu tiên là **văn bản**; tên người, tổ chức, địa chỉ. Không tự mở năng lực tệp giữ định dạng của MASK-8…11. Không giảm lớp số/MST/tài khoản, tiền/ngày, quyền, Cf/NFD hoặc các chặn của MASK-2b. Prompt có mã/phiên bản do module/quy trình khai; engine kiểm profile và băm khuôn, không tạo kho sửa prompt riêng.

### 6.2 Chuỗi và cửa phát hành

Chuỗi logic do **Core** gọi từng engine; không engine nào gọi hoặc import engine kia:

1. **Mask chạy quy tắc MASK-2b như hiện nay.** Năng lực mới dự kiến `mask.chuan_bi_ai_cuc_bo@1` nhận `van_ban`/`van_ban_tai_lieu`/`tep` JSON như đầu vào che hiện tại, tái dùng lõi và quyền. Lỗi hoặc `con_sot` lớp 1 vẫn chặn, AI không được gỡ chặn. Kết quả quy tắc đạt được giữ trong snapshot nội bộ, **chưa phải kết quả cho Cloud**. Năng lực trả một `yeu_cau_ai` cho đoạn đầu, không trả `van_ban_da_che` trung gian. Không đổi `tra` của `mask.che_van_ban@1`; đường cũ không có chứng cứ lớp 2 sẽ bị cửa Cloud từ chối.
2. **Core → `e_hoi_ai`: `ai.hoi_mask_cuc_bo@1` (AI-9)**, nhận `yeu_cau_ai`, trả `tra_loi_ai`. `tai_lieu` là lát nguyên văn **GỐC**, chưa che, bất biến; chỉ gửi Local. Core phát đủ các đoạn theo kế hoạch trong snapshot, giữ từng yêu cầu/phản hồi, không engine nào tự gọi bước sau. Chưa có cửa lặp/ghép thì chỉ test adapter ngoài gói, không công bố runtime chuỗi dài đạt.
3. **Core → `mask.hau_kiem_ai_cuc_bo@1`**, nhận duy nhất `tra_loi_ai`. Phản hồi cuối mang tham chiếu tập phản hồi Core đã tập hợp; bước 3 đọc snapshot **văn bản đã che + map + gốc** và tập phản hồi được Core cấp quyền qua `viec.mo_tep`. Không thêm đầu vào thứ hai vào API. Kiểm toàn bộ đoạn, đối chiếu thực thể AI với vùng đã che; vùng còn nguyên chỉ che thêm khi đủ căn cứ, còn nghi vấn vào `con_sot` nội bộ và từ chối phát hành. Không dùng `mask.mo_che_van_ban@1` cho bước này.
4. Chỉ khi mọi kiểm tra đạt, chốt alias/hàng chờ/dấu chống trùng qua `Ngan`, kiểm tiền/ngày lại trên gốc và kết quả cuối, rồi trả **`van_ban_da_che`** đúng contract hiện có (`con_sot=[]`, `kiem_tien_ngay=true`). Core ghi nguồn kết quả bước 3, băm bản cuối và kết quả kiểm đủ đoạn làm chứng cứ; chỉ nguồn này mới được nối Cloud về sau. Trong cả loạt MASK-2c, **Cloud vẫn tắt cứng**.

Snapshot gồm gốc, bản quy tắc, bảng map, kế hoạch đoạn, băm và phiên bản; là tệp tạm **Core quản có ACL**, không tệp bền trên máy engine. `chuyen_tiep.mask_2c` chỉ chứa mã opaque, tham chiếu+băm, chỉ số đoạn, profile (đề xuất ở sổ loại chung §6). Không mang văn bản/map/tên gốc trong chuyển tiếp. Cấu hình và chỉ mục trạng thái qua `Ngan`, `chon_ngan(app)`/`NganBoNho` theo SDK 2.1 đề nghị; không đổi hai mẫu `ngan.py`/`cau_hinh.py`. Mất RAM/restart/không có snapshot → phải làm lại chuỗi, không tái dùng cờ đạt cũ.

**Ràng buộc Local hai phía:** AI-9 bắt buộc profile `nha_cung_cap_bat_buoc=local`, chọn duy nhất provider `local`, từ chối thiếu/khác giá trị, không fallback Cloud ngay cả khi module bật Cloud. Giữ kiểm IP loopback/LAN/Tailscale, không DNS/proxy/redirect, chặn model remote/cloud hiện có. URL riêng tư không chứng minh server không chuyển tiếp: lead phải xác nhận model chạy tại chỗ và egress server chặn Cloud trước dùng thật; chưa xác minh thì chưa nghiệm thu. Bước 3 kiểm `tra_loi_ai.nha_cung_cap == "local"` **cho mọi đoạn**, profile chuyển tiếp cũng bằng local, và chứng cứ Core xác nhận kết quả thực sự từ AI-9 trên đúng snapshot. Không tin cờ do model/caller tự tạo; sai nguồn thì lỗi. Cloud chỉ nhận nội dung cuối đã che, không snapshot, yêu cầu Local, prompt chứa gốc, trích dẫn gốc hoặc metadata.

### 6.3 JSON, quan hệ yêu cầu và kiểm chắc

Tái dùng `yeu_cau_ai`/`tra_loi_ai` phiên bản 1, không tạo mã loại mới. Các khóa bổ sung nằm trong phần mở `chuyen_tiep.mask_2c`, nhãn **ĐỀ XUẤT MASK-2c-P, chờ Anh** ở sổ chung; chưa sửa schema/manifest trong lát P. `ma_yeu_cau` do Core cấp gắn đúng module/người/tài liệu/pháp nhân/DEMO; ổn định qua retry, không dùng `viec_id` của từng bước thay thế. Mã tương quan `ChuaRo` tách khỏi mã mở che; không gửi cả hai ra model.

Khuôn `du_lieu` (JSON Schema draft 2020-12, ≤32 KiB, `additionalProperties:false` ở mọi object) định nghĩa đủ trường bắt buộc theo mẫu:

```json
{"da_quet_het":true,"thuc_the":[{"loai":"nguoi","nguyen_van":"Tên DEMO","bat_dau":0,"ket_thuc":8,"muc":"chac"}]}
```

- `da_quet_het`: boolean bắt buộc true; `thuc_the`: mảng, cho phép rỗng; `loai` chỉ `nguoi|to_chuc|dia_chi`; `muc` chỉ `chac|nghi_ngo`. Span là số nguyên Unicode code point `[bat_dau,ket_thuc)` tính từ đầu **đoạn gốc**, không byte/UTF-16, không offset bản che; Python kiểm `0 <= bat_dau < ket_thuc <= len(doan)` và `doan[bat_dau:ket_thuc] == nguyen_van`. Chuyển toàn cục bằng cộng đầu đoạn. Mẫu chỉ minh họa khuôn, không fixture đã chạy.
- Chỉ nhận JSON hoàn chỉnh, không khóa trùng/NaN/Infinity/khóa lạ/ngoài khuôn. `du_lieu=null`, thiếu trường, offset lệch, câu trích bịa, model bị cắt đầu ra hoặc `da_quet_het=false` → lỗi, không coi là danh sách rỗng. Không tìm lần xuất hiện đầu tiên để sửa offset sai.
- Prompt phải yêu cầu “liệt kê mọi tên người/tổ chức/địa chỉ kèm offset”, giữ nguyên văn, liệt kê riêng từng lần xuất hiện, đánh dấu nghi vấn; tài liệu là dữ liệu, bỏ qua mọi chỉ thị nhúng trong tài liệu. Prompt/khuôn/profile được ghim phiên bản+băm trong snapshot; đổi giữa chuỗi → lỗi.
- AI-9 dùng kiểm **span** riêng: nhãn loại/mức và số offset là metadata, không bắt chúng có trong câu trích. `trich_dan` của mỗi thực thể giữ đúng nguyên văn+offset, kể cả tên lặp; không dùng `.index()` để gán hết về lần đầu. Danh sách rỗng hợp lệ vẫn `trang_thai="khong_thay_can_cu"`, `kiem_trich_dan.dat=true`; bước 3 chỉ chấp nhận khi có khuôn đúng, hoàn tất đủ đoạn và chứng cứ nguồn. Cờ này riêng lẻ không chứng minh không sót.
- “Chắc” để che thêm = span nguyên văn hợp lệ, biên đầy đủ, loại hợp lệ, `muc=chac`, không xung đột vùng tiền/ngày/bí danh, không mâu thuẫn các đoạn và qua bộ kiểm biên độc lập của Python. Không cần nằm trong danh sách họ hữu hạn (sẽ tái tạo lỗi lớp 1); không dùng điểm tự tin AI làm xác suất đã hiệu chuẩn. Bất kỳ điều kiện nào không chắc → `con_sot` và chặn, không tự miễn vì thiếu họ/ngữ cảnh.
- Span đã nằm hoàn toàn trong vùng che xác minh bằng map → đã che. Giao một phần, span lồng/chồng không đồng nhất hoặc đụng alias → chặn để duyệt; không kết luận an toàn chỉ vì che prefix. Che bổ sung theo vị trí từ phải sang trái, không replace toàn cục. Alias mới dùng quy tắc MASKCN/MASKCT/MASKDC/MASKTAM và hàng chờ/quyền hiện có; không trả tên gốc hoặc map ra kết quả.

### 6.4 Ánh xạ, Unicode và văn bản dài

- Giữ ba hệ riêng: **gốc bất biến**, bản dò NFC/Cf của MASK-2b, bản đã che. Ghi edit script gồm span gốc, span bản che, loại thao tác (giữ nguyên/bỏ ký tự vô hình/thay alias), phiên bản và băm hai đầu. Map là quan hệ khoảng, **không giả song ánh**: nhiều code point NFD có thể về một ký tự NFC, Cf có thể bị bỏ, tên nhiều ký tự thành alias. Vùng alias map về toàn bộ span gốc; không suy offset bằng chênh độ dài tổng.
- Bản gốc gửi Local giữ nguyên NFD, Cf, selector, tab/NBSP/xuống dòng. Bộ so kiểm ánh xạ về đúng gốc qua phép dò hiện có; Cf chèn giữa tên/Cf thay dấu cách phải có hồi quy riêng. Không normalize gốc rồi dùng offset trên chuỗi cũ. Tên NFD khi thay phải lấy đủ dấu kết hợp; Cf ở trong vùng phải được loại theo chính sách hiện có; span cắt giữa cụm ký tự → không chắc, chặn. UI nếu dùng UTF-16 phải chuyển hệ trước hiển thị, không gửi offset UI làm offset chuẩn.
- Giữ trần nghiệp vụ đầu vào **500.000 code point**, vượt từ chối. Đề xuất kỹ thuật thử: đoạn ≤8.000 code point, overlap **512 mỗi phía** quanh vùng chính, ≤128 đoạn, một lượt đồng thời; span thực thể ≤300 theo trần giá trị hiện có, vượt không cắt mà chặn. Cắt tại ranh câu/khoảng trắng, không cắt giữa dấu kết hợp/Cf/từ; không tìm được biên trong trần thì từ chối. Khoảng chính phải phủ `[0,len(goc))` không hở; đoạn gồm ngữ cảnh lấn hai bên, không vượt trần 8.000. Đo trên model thật rồi chốt, không nhận là model đã chứa được 8.000 ký tự.
- Tính budget token cho cả prompt+khuôn+ngữ cảnh+đầu ra theo model; không suy token bằng ký tự rồi coi chính xác. Chưa biết sức chứa thì không gửi văn bản dài thật; nhận báo cắt/context overflow hoặc vượt giới hạn phản hồi hiện có → chặn, không lấy phần đầu. Mọi trần (số thực thể, JSON bytes, tổng thời gian) phải khai/đo, vượt từ chối, không truncate. Deadline từng Local và toàn chuỗi do Core giữ, không tăng hạn vô hạn khi chia đoạn; quá hạn giữ fail-closed.
- Core lập kế hoạch bất biến, giao từng `yeu_cau_ai`/nhận từng `tra_loi_ai`, lưu kết quả ghép trong kho tệp Core. Bước 3 kiểm đủ đúng bộ chỉ số+băm, không thiếu/trùng khác nội dung/đổi thứ tự nguồn. Trùng cùng `(loai,bat_dau,ket_thuc)` và cùng nguyên văn thì gộp, tính một lần; xung đột → chặn. Span chạm mép đoạn hoặc bị cắt chưa có bản bao đầy đủ ở đoạn kế bên → chặn. Lần xuất hiện khác giữ riêng. Thiếu một đoạn là chưa kiểm đủ, không phát hành một phần.

### 6.5 Lỗi, retry và tính an toàn

| Tình huống | Bắt buộc |
|---|---|
| Không kết nối trước gửi | `LoiNghiepVu` tiếng Việt, cho thử lại; không phát hành/không Cloud |
| POST có thể đã nhận nhưng timeout/mất phản hồi/202 chưa kết quả | `raise ChuaRo(ma_tuong_quan)`; Core giữ chưa rõ, không tự đổi thành kết quả rỗng hoặc fallback Cloud |
| Sai JSON/khuôn, thiếu/chưa đủ đoạn, sai nguồn local/băm/map/quyền | Lỗi cố định, không kèm nội dung; `MASK_AI_CHUA_DAT`/mã chuyên biệt; không trả bản che dở |
| Thực thể nghi vấn/che một phần/tiền-ngày bị đổi | `con_sot` nội bộ chỉ nhóm/vị trí/lý do; `LoiNghiepVu`, không tạo `van_ban_da_che` |
| Hủy/mất lease/lỗi chốt/ACK chưa rõ | Dừng trước nộp; retry cùng mã+băm không cấp alias/đếm gặp/chốt lần nữa |

Không để AI gỡ, sửa hay mở alias lớp 1; chỉ thêm che. Sau thêm che chạy lại hậu kiểm cũ và kiểm tiền/ngày trên **toàn văn**. Kết quả AI không là bằng chứng quyền. Không ghi gốc, trích dẫn gốc, phản hồi AI, URL thật, mã yêu cầu ra log/báo cáo; stderr chỉ mã lỗi/số đếm/thời gian/phiên bản. Tệp tạm nếu thư viện buộc cần phải dọn `finally`; không cấu hình/sổ/cache bền tại engine. CAS/lô giữ nguyên giới hạn SDK đề nghị (≤100 lệnh); vượt thì chặn hoặc báo Cần Core, không chia lô rồi giả nguyên tử.

### 6.6 Bộ đo và điều kiện nghiệm thu

Bộ **held-out mới**, chỉ DEMO, do lead/người soạn độc lập đóng băng đáp án+băm **trước** chạy; không lấy các ca MASK-2b/t9/t10 hoặc bốn tên đã biết làm tập mới. Tập phát triển riêng để chỉnh prompt/ngưỡng. Sau khi xem held-out để chỉnh bất kỳ lớp nào, tập đó thành hồi quy, phải soạn held-out khác.

- Tối thiểu **45 tên người viết thường mới** ở ≥45 ngữ cảnh có gold span từng lần; có họ hiếm, không danh xưng, trùng từ thường/địa danh, viết tắt, tên nước ngoài, dấu gạch/nháy, lặp tên; thêm ≥15 tổ chức và ≥15 địa chỉ DEMO có gold span. Mọi tên/địa chỉ là giả, không hồ sơ người thật. Tạo biến thể NFD/Cf/selector/tab/NBSP, tên ở mép đoạn, lặp overlap và văn bản dài; báo riêng biến thể, không dùng chúng thổi mẫu số 45 tên cơ sở.
- Tối thiểu **75 câu thường mới**, không có định danh cần che theo gold, gồm số văn bản/số sổ cái, từ trùng âm tiết tên, nghiệp vụ tài chính, tiền 1.000.000 VND và ngày dữ liệu `2026-10-30`. Ca mập mờ có quy tắc gold từ trước; giữ trong mẫu số, không loại sau chạy.
- Chạy cùng đầu vào cho **lớp quy tắc** và **hai lớp**, cùng quyền DEMO/config/model/profile đã ghim. `lọt`: có phát hành và còn bất kỳ phần nhận diện được của gold span (dò độc lập bỏ dấu/Cf/khoảng trắng/dấu câu và kiểm che đủ span bằng map, gồm che prefix). Báo cả số ca lẫn số thực thể lọt, mẫu số tên cơ sở, tổng gold span và số thực sự phát hành. **Mục tiêu lọt sau hai lớp = 0**, không đạt nếu có một ca lọt.
- Tên bị chặn nghiệp vụ được tính chặn an toàn và báo riêng; **timeout, ChuaRo, sai khuôn, thiếu quyền/model/đoạn là lỗi kỹ thuật/chưa đo**, không tính chúng là detector đạt 0 lọt. Tất cả bị chặn không chứng minh chất lượng: báo số tên che thành công/chặn nghiệp vụ/lỗi kỹ thuật, số câu thường phát hành nguyên vẹn; chưa có lượt AI thực tế đầy đủ thì kết luận chưa đo. Không tuyên bố recall chỉ từ số ca không phát hành.
- `báo nhầm = |câu thường bị che thừa hoặc bị chặn nghiệp vụ| / N_câu_thường`; một câu bị cả hai chỉ tính một lần. In tử/mẫu/phần trăm **số thật** trước/sau, không hứa giảm dưới 20% và không giấu ca lỗi. Lỗi kỹ thuật báo riêng trên toàn mẫu và trên số đo hợp lệ; không gộp thành không báo nhầm.
- Báo theo model và phiên bản/băm prompt, khuôn, engine, cấu hình đoạn; tổng/số thực sự gọi, độ phủ đoạn, thời gian p50/p95, timeout/ChuaRo/sai khuôn, số Cloud/engine-to-engine = 0. Không có số thật thì ghi **chưa đo**, không ước lượng thay kết quả.
- Công cụ `e_mask/cong-cu/THU-MASK-LOCAL-AI-THAT.cmd` ASCII gọi Python, mặc định **chạy khô**, chỉ `--that --url <IP_Local_DEMO> --model <model>` mới gửi DEMO. Adapter ngoài gói đóng vai Core điều phối ba bước bằng CoreGia, không đặt lệnh gọi engine khác trong gói Mask. Cấu hình URL/model chỉ trong RAM/ngăn DEMO, không tệp cấu hình; công cụ báo cáo DEMO chỉ ghi ra tệp khi Anh chỉ định `--bao-cao`, không chứa nội dung gốc/URL/path thật. Codex kiểm mock/chạy khô; **Anh chạy Local AI thật**, đây vẫn là “đã kiểm bằng Core giả (CoreGia)”, không nghiệm thu Core thật.

### 6.7 Bảng lát và phụ thuộc

Mỗi dòng một lát/PR, tối đa 5 tệp mã kể cả manifest/schema, test và tài liệu không tính. Đường Python tương đối `e_mask/goi/e_mask/e_mask/` trừ ghi khác. Không thêm dependency; cần vượt tệp phải tách trước. **25 giờ ƯỚC TÍNH Mask + 6 giờ ƯỚC TÍNH AI-9 = 31 giờ ƯỚC TÍNH**, chưa gồm code/chờ Core, Anh chạy model thật và phần tệp. Không phải thời gian MASK-2c-P đã thực hiện.

| Lát | Nội dung | Phụ thuộc | Giờ ƯỚC TÍNH | Độ khó | Tệp mã tối đa |
|---|---|---|---:|---|---|
| MASK-2c-1 | Map gốc ↔ che và snapshot có phiên bản | MASK-2b, MASK-3b…6 | 6 | kho | 4: `anh_xa_ai.py`, `ho_so_ai.py`, `che_van_ban.py`, `nguon/privacy/types.py` |
| MASK-2c-2 | Chuẩn bị yêu cầu Local, kế hoạch đoạn | MASK-2c-1; duyệt đề xuất dữ liệu; Core giả | 6 | kho | 5: `chuan_bi_ai.py`, `chay.py`, `phong_bi.py`, `kho_dinh_danh.py`, `../engine.json` |
| AI-9 | Năng lực Local nhận diện theo span | AI-8, profile MASK-2c | 6 | kho | Xem phiếu e_hoi_ai §6 |
| MASK-2c-3 | Nhận AI, đối chiếu/che bổ sung, chặn phát hành | MASK-2c-2, AI-9; Core giả | 8 | kho | 5: `hau_kiem_ai.py`, `chay.py`, `phong_bi.py`, `kho_dinh_danh.py`, `../engine.json` |
| MASK-2c-4 | Held-out mới, công cụ .cmd, báo cáo thật | MASK-2c-3; Anh có model thật | 5 | vua | 3: `e_mask/cong-cu/thu_mask_local_ai_that.py`, `THU-MASK-LOCAL-AI-THAT.cmd`, dữ liệu DEMO held-out JSON ngoài gói |

### MASK-2c-1 — Ánh xạ gốc và bản che
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, SDK 2.0.0 HUONG-DAN-VIET-ENGINE.md/MAU-PHIEU-ENGINE.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md §6; e_mask/CLAUDE.md, docs/YEU-CAU-VA-HIEN-TRANG.md, QUYET-DINH-CUOI-e_mask.md, BAO-CAO-MASK-2b.md, GIAO-CODEX-e_mask.md §6, VIEC.md. Quyết định Anh 15/11: "Thêm AI cục bộ". Làm MASK-2c-1, 6 giờ ƯỚC TÍNH, kho; sau MASK-2b và MASK-3b…6; không bật Cloud/gọi engine khác.
Chỉ tối đa 4 tệp mã trong e_mask/goi/e_mask/e_mask/: anh_xa_ai.py, ho_so_ai.py, che_van_ban.py, nguon/privacy/types.py; test/tài liệu ngoài trần. Giữ nguyên API và kết quả công khai hiện tại. Xuất nội bộ edit script gốc Unicode ↔ bản dò NFC/Cf ↔ bản che, quan hệ khoảng cho Cf bị bỏ/NFD gộp/alias thay tên; băm/phiên bản, snapshot bất biến. Không coi map song ánh, không suy bằng chênh độ dài, không để prefix được coi đã che cả tên.
Snapshot gốc/bản che/map/kế hoạch đoạn chỉ RAM hoặc tệp tạm Core qua port tin cậy; chỉ mục qua Ngan theo mẫu chung, không ghi đĩa engine/không sửa ngan.py,cau_hinh.py. Chưa có Core thật thì adapter CoreGia DEMO ngoài gói; thiếu quyền/tham chiếu phải từ chối. Bất kỳ tài nguyên thiếu/quy tắc MASK-2b chặn vẫn chặn.
Test round-trip map trên phần giữ nguyên và quan hệ bao span tên, NFD/Cf thay dấu cách/selector/tab/NBSP, alias dài ngắn, tên lặp/chồng/che prefix, tiền/ngày không đổi, biên 500000/500001; map sai/băm sai không phát hành. Không nới xfail bốn ca held-out; chúng là giới hạn lớp 1. Chạy .venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask; -B -m pytest e_mask/tests -q; -B e_mask/tests/kiem_doc_lap.py; -B e_mask/tests/chay_demo.py. Dán kết quả thật cả CLI thiếu quyền, ghi đã kiểm bằng Core giả (CoreGia); git diff --check. Cập nhật VIEC.md/CHANGELOG nếu có, PR chờ lead mở, không commit/push; không sửa Core/SDK/nguồn cũ/schema chung, không dependency. Báo cáo §6 AGENTS.md với giờ thực tế và lệch phiếu.
```

### MASK-2c-2 — Chuẩn bị Local AI và chia đoạn
```
Đọc AGENTS.md, API-ENGINE-v1.md/SDK 2.0.0 trong docs/goi-gui-engine; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md §6; e_mask/CLAUDE.md, docs/YEU-CAU-VA-HIEN-TRANG.md, QUYET-DINH-CUOI-e_mask.md, BAO-CAO-MASK-2b.md, GIAO-CODEX-e_mask.md §6, VIEC.md. Làm MASK-2c-2 sau MASK-2c-1 và duyệt profile dữ liệu, 6 giờ ƯỚC TÍNH, kho. Chưa duyệt thì chỉ fixture/kiểm độc lập, không kích hoạt runtime profile. Quyết định Anh: "Thêm AI cục bộ".
Tối đa 5 tệp mã: e_mask/goi/e_mask/e_mask/{chuan_bi_ai.py,chay.py,phong_bi.py,kho_dinh_danh.py}, e_mask/goi/e_mask/engine.json. Thêm mask.chuan_bi_ai_cuc_bo@1 nhận van_ban/van_ban_tai_lieu/tep JSON như che hiện tại, trả yeu_cau_ai; không đổi tra của năng lực cũ. Chạy nguyên lớp MASK-2b trước, còn sót/lỗi vẫn chặn. Giữ snapshot bản quy tắc đạt ở Core; không trả van_ban_da_che trung gian. Mã yêu cầu do Core cấp ổn định gắn quyền; không tự khai từ payload.
Tạo kế hoạch đoạn phủ đủ gốc, tối đa 8000 code point gồm overlap 512 mỗi phía, tối đa 128 đoạn, tên dài hơn 300/không có biên an toàn thì từ chối. Không cắt NFD/Cf/từ; không cắt ngầm vượt 500000. Ghim prompt/khuôn/profile/băm/đoạn, kiểm budget model và deadline qua Core; chưa biết sức chứa thì không công bố chạy dài thật. Khuôn đủ theo §6.3, liệt kê mọi người/tổ chức/địa chỉ+offset, nguyen_van, muc, da_quet_het; schema đặt trong chuan_bi_ai.py, không thêm tệp thứ sáu. Prompt do module/quy trình cấp có mã/phiên bản, không thêm kho prompt engine.
Yeu_cau_ai.tai_lieu là đoạn GỐC chỉ Local; chuyen_tiep.mask_2c đúng đề xuất §6 sổ chung, không gốc/map/tên. Snapshot/ngăn/ACL qua port Core, RAM CoreGia ngoài gói khi chưa có; Ngan không đọc chéo engine. Core điều phối lặp/ghép/ghim nguồn; KHÔNG import/gọi e_hoi_ai hoặc HTTP model trong Mask. Thiếu cửa Core thì fail-closed và ghi VIEC.md Cần Core; không giả API chuỗi đã có.
Test CoreGia: cấu trúc yeu_cau_ai, SHA profile, local bắt buộc, giữ nguyên gốc Cf/NFD, map không rò chuyển tiếp, đủ phủ/overlap/biên/lặp, quá trần, thiếu snapshot/quyền/hủy/retry không cấp alias hai lần; 0 Cloud/engine-to-engine. Chạy bằng .venv/Scripts/python -B cả SDK thu e_mask/goi/e_mask, pytest e_mask/tests -q, e_mask/tests/kiem_doc_lap.py, e_mask/tests/chay_demo.py; dán kết quả thật và giới hạn CLI quyền. git diff --check; VIEC.md/CHANGELOG nếu có, đã kiểm bằng Core giả (CoreGia), báo cáo AGENTS.md §6, PR chờ lead mở; không commit/push, không sửa Core/SDK/nguồn cũ/schema chung/dependency.
```

### MASK-2c-3 — Hậu kiểm Local và che bổ sung
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md và hướng dẫn SDK 2.0.0; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md §6; e_mask/CLAUDE.md, docs/YEU-CAU-VA-HIEN-TRANG.md, QUYET-DINH-CUOI-e_mask.md, BAO-CAO-MASK-2b.md, GIAO-CODEX-e_mask.md §6, VIEC.md; e_hoi_ai/docs/GIAO-CODEX-e_hoi_ai.md AI-9 và kết quả bàn giao. Làm MASK-2c-3 sau MASK-2c-2, AI-9 và duyệt profile; 8 giờ ƯỚC TÍNH, kho. Quyết định Anh: "Thêm AI cục bộ".
Tối đa 5 tệp mã: e_mask/goi/e_mask/e_mask/{hau_kiem_ai.py,chay.py,phong_bi.py,kho_dinh_danh.py}, e_mask/goi/e_mask/engine.json. Thêm mask.hau_kiem_ai_cuc_bo@1 nhan tra_loi_ai, tra van_ban_da_che cố định. Không mở che ở bước này. Đọc snapshot gốc+bản che/map và tập phản hồi qua tham chiếu Core cấp quyền; không đầu vào thứ hai, không path/URL, không đọc ngăn e_hoi_ai/gọi engine khác.
Kiểm nguồn Core chứng thực AI-9, nha_cung_cap=local ở MỌI phản hồi và profile bắt buộc local; ma_yeu_cau/module/người/tài liệu/pháp nhân, SHA gốc/che/request/khuôn/prompt/profile/map, đủ đúng đoạn không hở. bam_dau_vao AI là SHA JSON chuẩn của toàn yeu_cau_ai, không nhầm SHA riêng tai_lieu. Không tin cờ caller/model. Rỗng chỉ hợp lệ nếu JSON/khuôn/hoàn tất đủ đoạn+kiểm trích dẫn đúng; khong_thay_can_cu riêng lẻ không chứng minh an toàn.
Đối chiếu span code point gốc qua map §6.3–6.4: đã che toàn phần bỏ qua; thực thể mới chắc qua biên/loại/nguyên văn/không xung đột tiền-ngày thì che bổ sung vị trí phải→trái, cấp alias/hàng chờ qua kho hiện có. Nghi vấn/mâu thuẫn overlap/che prefix/span chạm biên chưa có bản bao đủ → con_sot nội bộ và LoiNghiepVu, không phát hành. Không cho AI xóa alias hoặc gỡ chặn MASK-2b. Gom trùng đúng span, giữ từng lần xuất hiện, không dùng replace toàn cục. Sau che thêm chạy hậu kiểm cũ và kiểm tiền/ngày toàn văn; chốt Ngan CAS/chống lặp trước kết quả, không chia lô giả nguyên tử >100 lệnh.
AI lỗi/timeout/ChuaRo/sai khuôn/thiếu đoạn/finish bị cắt/quyền sai/map sai/hủy/mất lease đều KHÔNG phát hành; đã nhận chưa trả → ChuaRo, không kết quả rỗng. Chỉ thành công trả contract van_ban_da_che hiện có, con_sot=[],kiem_tien_ngay=true từ kiểm thực; Core gắn chứng cứ nguồn bước 3+băm kết quả cuối. Cửa Core phải chặn đường cũ thiếu chứng cứ lớp 2 khi nối Cloud; thiếu cửa ghi VIEC.md, không bật BAT_CLOUD.
Test CoreGia nguồn giả: tên lớp 1 bỏ sót nhưng AI thấy, người/tổ chức/địa chỉ, partial overlap/NFD/Cf/alias/lặp, JSON rỗng hợp lệ và rỗng giả, phản hồi cloud trộn một đoạn, giả ma_yeu_cau/SHA/quyền/nguồn, prompt injection, timeout/ChuaRo/mất ACK/CAS/hủy; log/phản hồi không có gốc. Chạy .venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask; -B -m pytest e_mask/tests -q; -B e_mask/tests/kiem_doc_lap.py; -B e_mask/tests/chay_demo.py; git diff --check. Ghi kết quả thật, đã kiểm bằng Core giả (CoreGia), chưa kiểm Core/model thật; cập nhật VIEC.md/CHANGELOG, báo cáo AGENTS.md §6, PR chờ lead mở, không commit/push. Không sửa Core/SDK/schema chung/nguồn cũ/dependency.
```

### MASK-2c-4 — Held-out và công cụ thử Local thật
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md/hướng dẫn SDK 2.0.0; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md §6; e_mask/CLAUDE.md, docs/YEU-CAU-VA-HIEN-TRANG.md, QUYET-DINH-CUOI-e_mask.md, BAO-CAO-MASK-2b.md, GIAO-CODEX-e_mask.md §6, VIEC.md; e_hoi_ai/docs/GIAO-CODEX-e_hoi_ai.md AI-9. Làm MASK-2c-4 sau MASK-2c-3, 5 giờ ƯỚC TÍNH, vua. Quyết định Anh: "Thêm AI cục bộ". Codex KHÔNG có model thật, không chạy --that.
Tối đa 3 tệp mã/dữ liệu ngoài gói: e_mask/cong-cu/thu_mask_local_ai_that.py, e_mask/cong-cu/THU-MASK-LOCAL-AI-THAT.cmd (ASCII), bộ DEMO held-out JSON mới có gold và SHA. Không sửa runtime engine. Nhờ lead giữ khâu đóng băng/gold độc lập trước khi chạy; nếu chưa có bộ độc lập thì soạn bộ ứng viên mới, ghi chưa là nghiệm thu held-out độc lập, không giả đã được lead xác nhận. Tối thiểu 45 tên viết thường mới/45 ngữ cảnh +75 câu thường mới, thêm 15 tổ chức+15 địa chỉ, biến thể Unicode/mép đoạn/overlap/lặp/văn bản dài; tách development và bốn ca lead cũ. Không dùng hồ sơ thật, không bỏ ca mập mờ khỏi mẫu số.
Tool mặc định chạy khô không mạng; chỉ --that --url --model cho Anh gọi Local thật bằng DEMO. Adapter ngoài gói đóng vai Core gọi tuần tự chuẩn bị Mask → AI-9 → hậu kiểm Mask bằng CoreGia, lặp/ghép đủ đoạn; gói Mask không gọi engine khác. Cấu hình chỉ RAM/ngăn DEMO; kiểm mạng/model của e_hoi_ai không bypass. Báo rõ CoreGia không chứng nhận cửa Core thật. --bao-cao tùy chọn ghi số đếm/phiên bản/băm/thời gian, không gốc/trích dẫn/URL/path thật/mã mở che; không lưu báo cáo runtime trong engine.
Đo hai chế độ cùng bộ: quy tắc và hai lớp. Theo §6.6, mục tiêu lọt=0 nhưng báo riêng phát hành che đủ/chặn nghiệp vụ/lỗi kỹ thuật/chưa rõ; timeout/sai khuôn/model thiếu không được biến thành 0 lọt đạt. Báo nhầm bằng số thật (hợp câu che thừa hoặc chặn nghiệp vụ)/75+, tỷ lệ, số ca hợp lệ và tổng; số tên/span, model/prompt/khuôn/profile, p50/p95, đủ đoạn, 0 Cloud. Chưa Anh chạy thì ghi CHƯA ĐO Local thật, không điền số giả hoặc tuyên bố đạt 0. Không dùng held-out đã xem để chỉnh rồi báo cùng tập là held-out mới. Local đạt cũng không bật Cloud; nợ CAO giữ mở đến lead review đủ bằng chứng và Core thật.
Test dry-run/mock bằng Local HTTP giả và CoreGia: cmd ASCII/quote/thư mục có khoảng trắng, 0 mạng mặc định, toàn chuỗi thành công, thiếu đoạn, sai JSON, NFD/Cf, model không có, timeout/ChuaRo, 0 Cloud. Chạy .venv/Scripts/python -B cả SDK thu e_mask/goi/e_mask, pytest e_mask/tests -q, e_mask/tests/kiem_doc_lap.py, e_mask/tests/chay_demo.py; chạy lại bộ e_hoi_ai nếu adapter làm lộ hồi quy; git diff --check. Dán kết quả thật, đã kiểm bằng Core giả (CoreGia), ghi chờ Anh chạy .cmd thật. Cập nhật VIEC.md/CHANGELOG nếu có, báo cáo AGENTS.md §6, giờ thực tế/ước tính, PR chờ lead mở; không commit/push/đổi Core/SDK/nguồn cũ/dependency.
```

### 6.8 Cần Core / chưa thể chứng nhận

Cần **cửa chung**, không route riêng Mask: (a) nút quy trình giữ gốc và kết quả bước quy tắc, snapshot/ACL/tệp con qua các bước; (b) phát yêu cầu theo kế hoạch đoạn, ghim phiên bản/băm, lặp/ghép đủ phản hồi và deadline/hủy/ChuaRo; (c) chứng thực nguồn AI-9 Local, mã yêu cầu ổn định và quyền đúng người/module/tài liệu; (d) cửa trước Cloud kiểm chứng cứ bước 3 gắn băm kết quả cuối, từ chối đường quy tắc cũ/giả loại, lọc toàn bộ metadata và prompt chưa che; (e) ngăn SDK 2.1 CAS/nguyên tử/chống lặp và bàn giao kết quả khi mất ACK. API v1/SDK 2.0 chưa chứng minh đủ các cửa này; ghi chi tiết trong VIEC.md, không sửa Core/SDK hoặc nhận test CoreGia là nghiệm thu vận hành.

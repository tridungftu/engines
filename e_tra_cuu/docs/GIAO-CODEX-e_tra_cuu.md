# Giao Codex — `e_tra_cuu` (Tra cứu tài liệu) theo SDK 2.0

*Lập 15/11/2026 · TC-P, chỉ tài liệu · Nhánh `codex/e_tra_cuu-tc-p` · PR: chờ lead mở. Mọi giờ triển khai là **ƯỚC TÍNH, chưa đo**, không gồm chờ Core, quyết định hoặc Anh chạy máy thật.*

Căn cứ: `AGENTS.md`; `docs/goi-gui-engine/API-ENGINE-v1.md`; SDK 2.0.0 `HUONG-DAN-VIET-ENGINE.md`, `MAU-PHIEU-ENGINE.md`; `_chung/docs/GIAO-CODEX-THU-TU.md`, `QUYET-DINH-ANH-20261115.md`, `GIAO-CODEX-DOT-2.md` §2, `DE-NGHI-SDK-2.1.md`, `LOAI-DU-LIEU-RIENG.md`; mẫu Đối chiếu mới nhất, Hỏi AI, OCR; thiết kế TX-0; `e_tra_cuu/CLAUDE.md` và toàn bộ ba tệp trong `e_tra_cuu/docs/` trước TC-P. Theo Anh/lead, TX-0 và phiếu Đối chiếu đã xong, đủ điều kiện lập phiếu Tra cứu (quyết định 15/11 câu 12); điều này không có nghĩa Core hoặc các engine đã nối thật.

## 1. Kết luận

- **12 lát TC-0…TC-11, tổng 45 giờ công ƯỚC TÍNH.** TC-P lập phiếu **1 giờ ƯỚC TÍNH**, ngoài tổng triển khai. Đây là thiết kế để lead/Anh review và giao từng lát; không tự phê duyệt toàn bộ đặc tả nháp ngày 31/10. Khung SDK có thể làm trước các nhánh còn chờ; contract mới chỉ kích hoạt sau duyệt.
- Đích: `e_tra_cuu/goi/e_tra_cuu/`, engine SDK 2.0 **chỉ tính toán**: phân loại, cắt đoạn, phân tích câu hỏi, xếp hạng lại, soạn/hậu kiểm câu trả lời. Core điều phối OCR, AI, Trích xuất và ba tầng hỏi đáp. **0 lượt Cloud ở bản đầu**; M9 và nhóm 07 luôn chỉ Local. Engine không gọi engine, không SQL, không giữ chỉ mục/cache/kho tài liệu.
- **Kiểm kê thực tế:** chỉ có `CLAUDE.md`, `docs/DAC-TA-e_tra_cuu.md`, `YEU-CAU-VA-HIEN-TRANG.md`, `VIEC.md`. Không có `ma-nguon/`, `goi/`, `tests/`, `QUYET-DINH-CUOI-*`, `PHIEU-ENGINE-*.md`. Không có lõi Tra cứu tại chỗ để tuyên bố tái dùng; không tạo `ma-nguon/` theo khung cũ trong CLAUDE.md.
- Tái dùng: ba phong bì/schema `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`; API tệp và mẫu `Engine` của SDK; **chép nguyên** `_chung/mau-ma/ngan.py`, `cau_hinh.py` đã có, test SHA-256 sau chuẩn hóa CRLF→LF. Tham khảo cách ghim snapshot/hậu kiểm của TX-0 và DC-P, không sao chép cả pipeline, không import engine khác. `van_ban_da_che` giữ cho nhánh Cloud sau này, không đổi loại hoặc coi văn bản thường là đã Mask.
- Bỏ khỏi thiết kế chạy mới: socket/`Bootstrap`/`SDKEngine`, `cau_hinh_may`, `kho_tam`, DTO `.v1` lịch sử chưa đăng ký, route/API riêng trong engine, tự gọi model/vector, tự xếp kho/duyệt/tạo loại tài liệu/chuyển nhóm. Không xóa hay sửa tài liệu gốc. Chỉ mục, vector, cache, nhật ký hỏi đáp, RLS và K5 thuộc Core.
- Dự toán 45 giờ chỉ gồm engine, test, UI cấu hình/trạng thái và công cụ đo. **Không gồm** Kho tài liệu, PostgreSQL/pgvector, embedding của Hỏi AI, runner ba tầng, SDK JS hỏi đáp hay nạp hàng loạt. Chưa đo sức chứa model/chất lượng; không dùng dự toán này để cam kết vận hành 150 người/20 người đồng thời.

## 2. Thiết kế `engine.json` 2.0

### 2.1 Khung và năng lực

Khung: `phien_ban_manifest: 2`, `loai: "engine"`, `ma: "e_tra_cuu"`, `ten: "Tra cứu tài liệu"`, `phien_ban: "0.1.0"`; `tuong_thich: {core: ">=2.0.0 <3.0.0", api: "v1", sdk: ">=2.0.0 <3.0.0"}`; `che_do_chay: "cuc_bo"`; `diem_vao: {lenh: ["{python}", "-m", "e_tra_cuu.chay"], thu_muc: "."}`; `tai_nguyen.so_viec_dong_thoi: 1`; `readiness.thoi_han_giay: 30`; `bi_mat: []`; `webhook: null`. Tất cả năng lực `huy_duoc: true`. Chỉ khai năng lực đã triển khai hoặc stub có lỗi rõ, không thêm khóa SDK 2.1 vào manifest 2.0.

| Năng lực | `nhan` | `tra` | Vai trò / lát |
|---|---|---|---|
| `tra_cuu.nhan_yeu_cau@1` | `tep` (JSON Core/module ghép) | `ho_so_tra_cuu` — đề xuất | Kiểm đầu vào, phạm vi, nguồn và snapshot; TC-2 |
| `tra_cuu.cat_doan@1` | `ho_so_tra_cuu` | `ho_so_tra_cuu` | Cắt cấu trúc tài liệu nguyên vẹn, giữ nguồn/vị trí; TC-3 |
| `tra_cuu.chuan_bi_ai@1` | `ho_so_tra_cuu` | `yeu_cau_ai` | Chuẩn bị một trong bốn tác vụ AI, không gọi model; TC-4 |
| `tra_cuu.phan_loai_tai_lieu@1` | `tra_loi_ai` | `ho_so_tra_cuu` | Hậu kiểm phân loại + quy tắc nhóm bằng Python; TC-5 |
| `tra_cuu.phan_tich_cau_hoi@1` | `tra_loi_ai` | `ho_so_tra_cuu` | Hậu kiểm ý định/thực thể/hàm được phép; TC-6 |
| `tra_cuu.xep_hang_lai@1` | `tra_loi_ai` | `ho_so_tra_cuu` | Hậu kiểm hoán vị ứng viên và điểm xếp hạng; TC-6 |
| `tra_cuu.soan_tra_loi@1` | `tra_loi_ai`, `ho_so_tra_cuu` | `ho_so_tra_cuu` | Hậu kiểm câu trả lời Local; hoặc trả trực tiếp tầng 1 bằng mẫu xác định, không LLM; TC-7 |
| `tra_cuu.xuat_ket_qua@1` | `ho_so_tra_cuu` | `truong` tĩnh | Tệp JSON đầy đủ + trường ghép cột; TC-8 |

Năm tên nghiệp vụ trong đặc tả §9 được giữ, nhưng tách phần **chuẩn bị → AI do Core gọi → hậu kiểm** để tuân thủ cấm engine gọi engine. Đây là **đề xuất hợp đồng đầu vào/đầu ra mới**, chờ TC-Q13, không tuyên bố tương thích DTO cũ chưa có mã. `phan_loai_tai_lieu`, `phan_tich_cau_hoi`, `xep_hang_lai` nhận phản hồi AI thay vì tự gọi AI trong hàm. Cắt đoạn luôn Python; tạo vector/tìm lai luôn nằm ngoài engine này.

`loai_du_lieu_rieng` sau duyệt gồm đúng tên: `van_ban_tai_lieu` — “Văn bản tài liệu có vị trí”; `yeu_cau_ai` — “Yêu cầu hỏi AI”; `tra_loi_ai` — “Trả lời AI có trích dẫn”; **mới đề xuất** `ho_so_tra_cuu` — “Hồ sơ tính toán tra cứu”. `van_ban_tai_lieu` được tái dùng nguyên trong snapshot; không tự tạo loại `du_lieu_bang`, `tham_so`, `doan_van.v1`, `cau_hoi_tra_cuu.v1`, `tra_loi_tra_cuu.v1`, `ham_tra_cuu.v1` vì chúng chưa là mã đã duyệt ở tài liệu loại chung.

`truong_ra` cố định của `xuat_ket_qua`: `tac_vu`, `trang_thai`, `tra_loi`, `nhan`, `nhom_de_xuat`, `loai_de_xuat` (`van_ban`); `tang`, `so_doan`, `so_ung_vien` (`so`); `co_can_cu`, `co_mau_thuan`, `can_duyet` (`co_khong`); `tep_json` (`tep`). Luôn có mọi trường, không áp dụng/chưa xác định thì `null`, không dùng 0/false để giả đã kiểm. `trang_thai` chỉ `da_cat_doan`, `cho_phan_loai`, `da_phan_loai`, `da_phan_tich`, `da_xep_hang`, `co_can_cu`, `khong_thay_can_cu`; `nhan` chỉ `xanh`, `vang`, `null`. Xuất trạng thái trung gian `da_nhan`/`cho_ai` bị từ chối. Trường `can_duyet` là đề nghị cho Core/K5, không phải lệnh duyệt hay xác nhận bền. Kết quả chi tiết/danh sách nguồn nằm ở JSON, không JSON hóa hàng nghìn mục vào một cột chữ.

### 2.2 Một phong bì, snapshot nguồn và sơ đồ Core điều phối

API v1 chỉ nhận **một** phong bì mỗi bước. Đầu vào `nhan_yeu_cau` là tệp JSON trong kho Core, gồm `phien_ban: 1`, `ma_yeu_cau`, `tac_vu` và các tham chiếu tệp có metadata+băm; nội dung cụ thể:

| Tác vụ | Dữ liệu Core/module phải ghép trước khi giao |
|---|---|
| `phan_loai` | Tệp gốc/băm/phiên bản, nguyên phong bì `van_ban_tai_lieu`, snapshot danh mục nhóm/loại/trạng thái/loại hình pháp nhân, mã đối tượng được phép; phân loại cũ và quan hệ phụ lục nếu có |
| `cat_doan` | Cùng nguồn văn bản có vị trí + cấu trúc bảng nếu nguồn có; nhóm/loại/hiệu lực đã được Core cấp. Phân loại chưa duyệt không tự trở thành metadata đã duyệt |
| `phan_tich_cau_hoi` | Câu hỏi, phạm vi do Core cấp, thời điểm hỏi tin cậy, danh sách hàm tra cứu được phép và schema tham số/đầu ra; không có SQL, URL hoặc mã thực thi |
| `xep_hang_lai` | Câu hỏi + thực thể đã kiểm, danh sách ứng viên **Core đã lọc quyền/hiệu lực**; mỗi ứng viên có mã ổn định, nguồn/băm/phiên bản, nội dung/vị trí/điểm tìm kiếm |
| `soan_tra_loi` | Câu hỏi/thực thể, tầng, bằng chứng được phép: trường tầng 1 và trạng thái duyệt/hiệu lực/độ tin cậy/mốc công bố hoặc đoạn tầng 2/kết quả tầng 3; cờ có văn bản mới chờ duyệt, nguồn và tập phụ thuộc cache |

Tệp con chứa phong bì chung thì giữ nguyên, không đổi nghĩa để nhét dữ liệu cặp/bảng vào `van_ban`. Kết quả TX còn chờ chi tiết `bang_trich_xuat`: TC chỉ nhận adapter bằng chứng của Core theo contract được duyệt, không mặc định loại TX đã hoạt động, không sửa TX. DOCX chưa có reader được giao thì Core cấp `van_ban_tai_lieu` đúng loại; TC không mở phạm vi viết OCR/DOCX reader mới.

`ho_so_tra_cuu` mang `phien_ban: 1`, mã yêu cầu, tác vụ, giai đoạn, tham chiếu+băm snapshot, băm cấu hình/danh mục, phiên bản engine và tóm tắt nhỏ (§6 đề xuất cuối tài liệu loại chung). Toàn bộ nguồn, câu hỏi, ứng viên, dẫn chứng, ánh xạ ngữ cảnh AI và kết quả ở snapshot JSON do **Core giữ**. Tệp snapshot không phải kho trên máy engine. Không nhét toàn văn/danh mục vào `chuyen_tiep`.

Nguồn phải mở qua `viec.mo_tep`; snapshot ra dùng `viec.tai_tep_ra`. Core phải cấp quyền tệp con và giữ chúng xuyên bước trong cùng ngữ cảnh pháp nhân/nhóm/module/người hỏi. `tep_id`, mã yêu cầu và băm **không tự chứng minh quyền hoặc nguồn tin cậy**. Cửa ghép/tái nhập kết quả, cấp dữ liệu nghiệp vụ, dữ liệu đã duyệt và Local-only là C-TC-02/03; thiếu thì từ chối, không nhận cờ do caller tự khai như đã được Core xác thực. CoreGia chỉ mô phỏng, không chứng nhận RLS thật.

Các nhánh do Core/module chọn:

- Nạp: `OCR/đọc văn bản → [Core ghép nguồn/danh mục thành tep JSON] → nhan_yeu_cau → chuan_bi_ai(phan_loai) → ai.hoi_theo_yeu_cau@1 Local → phan_loai_tai_lieu → xuat_ket_qua`. Core xếp kho/K5 sau đó; Core ghép nguồn/metadata cho nhánh `nhan_yeu_cau(cat_doan) → cat_doan → xuat_ket_qua`, rồi Hỏi AI tạo vector và Core lập chỉ mục.
- Phân tích hỏi: `tep JSON → nhan_yeu_cau → chuan_bi_ai(phan_tich_cau_hoi) → [Local/Core] → phan_tich_cau_hoi → xuat_ket_qua`. Core chọn tầng 1; thiếu căn cứ mới tìm lai tầng 2, cần nữa mới tầng 3.
- Xếp hạng: Core ghép ứng viên được phép thành tệp mới → `nhan_yeu_cau → chuan_bi_ai(xep_hang_lai) → [Local/Core] → xep_hang_lai → xuat_ket_qua`.
- Trả lời có LLM: Core ghép bằng chứng → `nhan_yeu_cau → chuan_bi_ai(soan_tra_loi) → [Local/Core] → soan_tra_loi → xuat_ket_qua`. Tầng 1 không LLM: `nhan_yeu_cau → soan_tra_loi → xuat_ket_qua` dùng mẫu Python đã duyệt. Không có căn cứ cũng qua nhánh Python, không tạo phản hồi AI giả.

Các chỗ “Core ghép” là phụ thuộc cửa chung, **không có sẵn fan-in/vòng lặp trong SDK 2.0**. Engine không tự lấy `ket_qua_id`, gọi hàm module, gọi engine hoặc chọn tầng bằng truy vấn CSDL. Core sở hữu dừng đúng tầng, HTTP 200/202, cache và các sự kiện. Nếu module chưa chạy, Core ghi “chờ” tầng 1 và có thể tiếp tầng 2 với nguồn đúng quyền, không giả hàm đã trả thành công.

### 2.3 Tham số, giới hạn và quy tắc kiểm

| Năng lực | `tham_so` cụ thể |
|---|---|
| `nhan_yeu_cau` | `bam_yeu_cau`: `van_ban`, bắt buộc, tối đa 71 ký tự (`sha256:` + 64 hex), tính trên bytes JSON chính xác trước parse |
| `cat_doan` | `do_dai_muc_tieu`: `so`, mặc định 2000, 200…8000; là mục tiêu gom đơn vị cấu trúc, **không** lệnh cắt tại ký tự thứ n. Kiểm số nguyên hữu hạn |
| `chuan_bi_ai` | `tac_vu`: `chon` bắt buộc (`phan_loai`, `phan_tich_cau_hoi`, `xep_hang_lai`, `soan_tra_loi`), phải khớp hồ sơ; `ma_prompt`, `phien_ban_prompt`, `prompt`: `van_ban` bắt buộc, tối đa lần lượt 200/100/16000 ký tự; `model_uu_tien`: `van_ban` tùy chọn ≤ 200. Prompt thuộc module; không prompt mặc định chung |
| Bốn hậu kiểm AI | Không tham số đổi nguồn/ngưỡng giữa lượt; ghim từ hồ sơ và yêu cầu AI. `soan_tra_loi` tự phân biệt đường Python bằng giai đoạn/tầng đáng tin, không công tắc caller xin nhãn Xanh |
| `xuat_ket_qua` | Không tham số; luôn xuất JSON đầy đủ, không dùng bộ lọc UI làm mất nguồn/kết quả |

Ngưỡng phân loại/tin cậy và cắt đoạn chi tiết thuộc cấu hình ngăn; danh mục/hàm/nguồn thuộc Core/module và được snapshot riêng mỗi việc. `ngu_canh` SDK 2.0 chỉ đảm bảo `viec_id`, `buoc`, `phap_nhan_id`, không suy quyền/module từ `ma_prompt`. Thời điểm chuẩn, định danh người và quyền nhóm cần Core cung cấp tin cậy, không nhận từ model.

Trần thiết kế ban đầu **đề xuất, cần đo TC-11**:

| Nhóm năng lực | `gioi_han` hợp lệ của manifest | Engine tự kiểm thêm |
|---|---|---|
| `nhan_yeu_cau` | `tep_toi_da_mib: 20`, `mime: ["application/json"]`, `thoi_han_giay: 120` | **JSON yêu cầu chính ≤ 1 MiB** do engine tự kiểm trước parse; JSON nghiêm, không khóa trùng/NaN, không đường máy/URL/base64; tệp con qua Core ≤ 20 MiB/tệp, tổng bytes đọc ≤ 64 MiB/việc |
| `cat_doan` | `ky_tu_toi_da: 500000`, `thoi_han_giay: 120` | Văn bản nguồn ≤ 500.000 ký tự, ≤ 60 trang nếu có trang; ≤ 5000 đoạn; đơn vị cấu trúc đơn lẻ > 8000 ký tự từ chối để trình phương án, không cắt hàng bảng/Điều ngầm |
| Chuẩn bị và hậu kiểm AI | `ky_tu_toi_da: 500000`, `thoi_han_giay: 180` | Câu hỏi ≤ 4000 ký tự; ≤ 100 hàm, ≤ 1000 mục danh mục, ≤ 50 ứng viên; ngữ cảnh `tai_lieu` ≤ 100.000 ký tự, khuôn ≤ 32 KiB, `chuyen_tiep` ≤ 64 KiB (mục tiêu ≤ 4 KiB) |
| `xuat_ket_qua` | `ky_tu_toi_da: 500000`, `thoi_han_giay: 120` | Phong bì hồ sơ ≤ 64 KiB UTF-8; snapshot/JSON kết quả ≤ 20 MiB, không chép nguyên kho tài liệu |

`gioi_han` chỉ áp đầu vào, không phát minh khóa như `so_doan_toi_da` trong manifest. **Đã đọc mã wheel SDK 2.0.0:** `Viec.mo_tep` dùng `tep_toi_da_mib` của bước cho mọi tệp mở, không có tham số đổi trần từng tệp. Vì vậy khai 20 MiB cho bước nhận, engine tự kiểm JSON chính ≤ 1 MiB; các bước đọc snapshot cũng khai `tep_toi_da_mib: 20`. Không sửa private SDK hoặc ngầm khai 1 MiB mà hứa đọc tệp con 20 MiB. Engine kiểm sâu cả JSON loại riêng/tham số/tệp con và đầu ra thực. Quá ngân sách → `TC_QUA_GIOI_HAN`/`TC_QUA_NGAN_SACH_AI`, không `[:n]`, top-k cắt ngầm, tự chia nhiều lượt hoặc chuyển Cloud. Trần ký tự không chứng minh context model đủ; đo token/context thật rồi chốt. AI do phiếu Hỏi AI quy định thời hạn (hiện 600 giây).

Quy tắc nghiệp vụ và an toàn:

- Phân loại theo thứ tự DAC-TA §3.3: không rõ pháp nhân → chờ; công trình/thiết bị lắp đặt/vật tư cấp công trình/sửa chữa có thông tin công trình → 04, thuê máy → 03; quy chế người lao động → 07, còn lại → 08. Không có BOQ không đủ đưa vật tư/sửa chữa vào 03. Thiếu thông tin công trình thì chờ, không đoán. Loại chờ kích hoạt/ngừng nhận mới không tự xếp; phụ lục đổi bản chất chỉ gắn cờ Core chuyển cả bộ sau duyệt.
- Cắt theo Điều/Khoản/câu/khối/bảng/trang, nguyên văn và offset Unicode `[bat_dau, ket_thuc)` bất biến. Bảng giữ tiêu đề/ô rỗng/ô gộp, liên kết về hàng/cột nguồn; không biến bảng thành chuỗi mất quan hệ. Chỗ lớn không chia an toàn thì lỗi rõ. Không có vị trí thực để `null`; DOCX chưa phân trang giữ `so_trang=0`, `trang=[]` trong phong bì gốc, không bịa trang/hộp.
- Chọn hàm theo allowlist Core cấp, kiểm tên/kiểu/schema/giới hạn tham số/thực thể, không SQL/code/hàm ngoài danh sách. Điểm xếp hạng không phải xác suất đúng; đủ và đúng tập mã ứng viên, không thêm nguồn/đổi nguồn/cắt ứng viên. Nội dung tài liệu không được thay chỉ dẫn/quyền.
- Tầng 1 không đủ khi thiếu, chưa duyệt, độ tin cậy dưới ngưỡng, hết hiệu lực hoặc ngoài trường đã trích; engine trả lý do cho Core, không tự chạy tầng tiếp. Không đối chiếu ngược tầng 1 với tệp mỗi câu (QĐ-4). Cờ có văn bản mới chờ duyệt → cảnh báo + tối đa Vàng. Tầng 2–3 mới tìm thấy → đề nghị K5; không tự ghi ngược dữ liệu đã duyệt.
- Trích dẫn phải đúng nguyên văn/offset, đúng nguồn/phiên bản/đối tượng; map từ ngữ cảnh AI về đoạn/nguồn thật. Mọi khẳng định gắn bằng chứng; kiểm tiền/ngày/số gắn **đúng trường và thực thể**, không chỉ tìm thấy cùng con số ở đâu đó. Tiền `{so, tien_te}`, không float làm mất độ chính xác; ngày `YYYY-MM-DD`; giữ số 0 đầu của mã. Chỉ cho phép diễn đạt/chuyển kiểu theo quy tắc kiểm được, không tự tính số mới.
- Thiếu căn cứ hoặc số/nguồn không kiểm được → `khong_thay_can_cu`, không giữ câu trả lời bịa rồi chỉ hạ màu. Mâu thuẫn đã có bằng chứng hai bên → trả cả hai và cờ, không chọn bên; Core tạo K5. Không tự phát hiện mâu thuẫn bằng cách đọc lại mọi tệp tầng 1 trái QĐ-4.
- **TC-Q14 đã duyệt chiều 15/11/2026:** giải quyết mâu thuẫn nhãn trong đặc tả §5. Xanh chỉ đường Python từ tầng 1 đã duyệt, hiệu lực, đủ căn cứ/ngưỡng đo và không cờ chờ; mọi câu có LLM soạn tối đa Vàng. Cờ văn bản mới chờ duyệt luôn hạ Vàng. TC-7 đã kiểm chính sách bằng DEMO/CoreGia; tích hợp thật vẫn chờ C-TC-01…04 và số đo TC-Q15, không coi fixture là ngưỡng thật đã duyệt.
- Cache chỉ Core giữ; xuất tập nguồn phụ thuộc, thực thể chính xác, phạm vi và cờ phụ thuộc thời điểm. Core kiểm lại quyền **mọi nguồn** mỗi lần lấy cache, hết hạn khi thay phiên bản/đổi nhóm/duyệt/công bố đổi hoặc thu quyền. Không dùng cache A cho khoản vay B dù câu giống nghĩa. Câu phụ thuộc thời điểm chưa có TTL đã duyệt thì đề xuất không tái dùng cache; không đổi thành chính sách đã chốt.

Lỗi ở biên SDK dùng `LoiNghiepVu`, câu Việt cố định không nội dung nguồn/path/khóa: `TC_DAU_VAO_KHONG_HOP_LE`, `TC_SAI_NGUON`, `TC_THIEU_NGU_CANH`, `TC_CHUA_CO_CUA_CORE`, `TC_SAI_GIAI_DOAN`, `TC_QUA_GIOI_HAN`, `TC_QUA_NGAN_SACH_AI`, `THIEU_PROMPT`, `TC_AI_SAI_KHUON`, `TC_HAM_KHONG_DUOC_PHEP`, `TC_CHI_LOCAL`, `TC_KHONG_CAT_DUOC`, `CHUA_CAU_HINH`. Ví dụ `LoiNghiepVu("TC_SAI_NGUON", "Chưa kiểm chứng được nguồn tra cứu. Anh gửi lại yêu cầu từ hồ sơ được cấp quyền.")`. Không rõ phân loại/không thấy căn cứ là trạng thái nghiệp vụ có lý do, không giả thành lỗi hệ thống. Nguồn ngoài đã nhận chưa trả → tầng sở hữu lượt báo `ChuaRo(ma_tuong_quan)`; TC không dựng phản hồi thành công hay tự gửi lại model.

### 2.4 Ngăn, cấu hình và màn engine

Mẫu NGAN-0 **đã có trong worktree**. Chép nguyên hai tệp, không import `_chung` lúc chạy, không sửa mẫu để hợp engine. So SHA-256 trên bytes chỉ thay `b"\r\n"` thành `b"\n"`, không strip/đổi dấu/đổi nội dung. `chon_ngan(app)` dùng ngăn SDK khi có; SDK 2.0 gắn `NganBoNho(khai_bao)` một lần rồi gọi `chon_ngan`, tránh tạo RAM riêng mỗi việc. Cảnh báo RAM stderr một lần đúng đợt 2. RAM mất khi khởi động lại; không phải lưu bền.

| Bảng ngăn dự kiến | Phạm vi / khóa / duy nhất | Nội dung và cách ghi |
|---|---|---|
| `cau_hinh` | `engine`, khóa **`{}`**, `khoa: []`, không unique bổ sung | Bản duy nhất đúng mẫu NGAN-0; `doc_cau_hinh(ngan, schema)` trả cấu hình/None, CAS lấy `row_version` từ `ngan.doc("cau_hinh", {})`; không dùng khóa `ma="cau_hinh"` của bản thiết kế cũ |
| `dot_kiem` | `phap_nhan`, khóa `ma_dot`, duy nhất `[phap_nhan_id, ma_dot]` | Trạng thái bài đo DEMO, băm bộ/cấu hình/phiên bản, tử số/mẫu số, tham chiếu+băm báo cáo Core; không câu hỏi/nguyên văn/nguồn ngoài quyền; `lay_hoac_tao` chống trùng, cập nhật CAS trong một lô, không cộng dồn khi gửi lại |

Đây không phải bảng `luot_hoi`/`cache_tra_loi`/`doan_van` thứ hai. Engine không cần lưu lịch sử hỏi đáp hay danh mục nghiệp vụ trong ngăn của mình; Core sở hữu các dữ liệu đó. Bản ghi JSON ≤ 64 KiB, lô ≤ 100 lệnh, tìm phân trang ≤ 500. Không tự đặt TTL xóa kết quả trước chính sách lưu trữ được duyệt.

Mọi thao tác bảng `dot_kiem` phải có `phap_nhan_id` lấy từ `viec.ngu_canh` đã được Core cấp: ưu tiên `viec.ngan`, RAM dùng `.cho_phap_nhan(p)`; vẫn truyền `p` trong `khoa`/`loc` của `doc`, `tim`, lệnh lô, không chỉ trong `gia_tri`. Ghi từ UI phải được Core kiểm pháp nhân/quyền, không tin dropdown của trình duyệt. Thử chéo pháp nhân, cursor tái dùng, unique và CAS đều bắt buộc. Ngoại lệ mẫu ngăn/cấu hình đổi sang `LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc)`; không tự nuốt xung đột hay thử vô hạn.

`cau_hinh.schema.json`: `additionalProperties: false`, chỉ tập từ khóa mà mẫu hỗ trợ; phiên bản cấu hình, ngưỡng phân loại đã đo (chưa đo dùng trạng thái chưa có, không mặc định số đẹp), tham chiếu/băm bộ quy tắc nhóm, mục tiêu/trần cắt đoạn và ngân sách xử lý §2.3. Schema máy là tệp **đóng gói chỉ đọc**, không phải tệp giá trị cấu hình bền. Không chứa địa chỉ/model Local AI, khóa Cloud, đường Hot Folder (thuộc Hỏi AI/OCR). Default chỉ điền sau khi đã có bản ghi cấu hình; thiếu bản ghi không tự tạo: `LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.")`. Khởi động vẫn được. Việc ghim cấu hình và `row_version` cùng một bản đọc, không đọc ngưỡng khác nhau giữa việc.

`goi/e_tra_cuu/KHAI-SDK-2.1.json` chứa dự kiến `ngan_du_lieu`, `cau_hinh: {schema: "cau_hinh.schema.json"}`, `giao_dien_quan_tri`; tuyệt đối chưa chép các khóa này vào `engine.json` 2.0. Màn ở `goi/e_tra_cuu/ui/cau_hinh.js`, `trang_thai.js`, dùng `KttCore.engine("e_tra_cuu").cau_hinh/.ngan`, nạp như màn module. Màn trạng thái chỉ xem bài đo theo pháp nhân; màn hỏi đáp/cây kho/K5 vẫn của Core, không làm lại trong engine. Chỉ gọi Core, không mạng ngoài/`eval`/`innerHTML` chưa lọc; dùng `textContent`, ngày dd/mm/yyyy, tiền dấu chấm nghìn + mã tiền tệ, không lộ mã kỹ thuật trong luồng chính. Test Node với `KttCore` giả, chưa chứng nhận trình duyệt Core thật.

### 2.5 DEMO và khoảng trống CLI SDK 2.0

Mọi ví dụ dùng “Công ty DEMO Ánh Dương”, “DEMO-VAY-A/B”, 1.000.000 VND, 2026-10-30 và mã pháp nhân giả. Không đọc tài liệu/Hot Folder/CSDL/máy thật. `chay_thu_demo` khung `[]` phải báo **0 ví dụ, chưa kiểm nghiệp vụ**. Từ TC-2 thêm mẫu có nguồn/băm thật và các mẫu hậu kiểm khi hạ tầng fixture cho phép; không hardcode ID tệp giả thành nguồn có thật, không runtime tự nạp cấu hình DEMO.

SDK CLI 2.0 chưa có cửa nạp cấu hình `Ngan`/tệp con theo chuỗi: phải chạy và dán **kết quả thật** của ba lệnh chuẩn ở lát code; nếu CLI báo `CHUA_CAU_HINH`/thiếu tệp con thì ghi chưa đạt cổng chuẩn, không tuyên bố mọi demo đạt. Bổ sung `tests/chay_demo_voi_core_gia.py` gắn `NganBoNho`, cấu hình và tệp DEMO rồi chạy cùng ví dụ qua CoreGia. Cổng bổ sung cần lead review C-TC-01/05, không phải tự sửa AGENTS.md hay SDK để làm xanh. Lát TC-P chỉ kiểm tài liệu bằng regex theo chỉ đạo riêng; **không chạy ba lệnh engine** khi chưa có gói/tests, không tạo gói rỗng để chạy.

## 3. Bảng lát

Mã TC-0…TC-11 dưới đây **thay cách chia TC-0…TC-7 lịch sử của DAC-TA §14 trong phạm vi engine**; không đổi tên công việc Core trong tài liệu gốc. TC-0 mới không phải khảo sát PostgreSQL. Trần khoảng 5 tệp mã/lát tính Python/JS/schema có logic; test/tài liệu/DEMO/manifest/bản khai metadata không tính. Nếu cần hơn, tách lát trước và ghi lý do. Schema nguồn và bản chép đều được tính, không lách bằng đếm thư mục.

| Lát | Yêu cầu / kết quả | Phụ thuộc | Tệp mã dự kiến (trong gói trừ khi ghi khác) | Giờ ƯỚC TÍNH |
|---|---|---|---|---:|
| TC-0 | Khung SDK 2.0 + `ngan/cau_hinh` + `kiem_doc_lap` + `KHAI-SDK-2.1.json` | NGAN-0 đã có; lead giao khung | `__init__.py`, `chay.py`, `ngan.py`, `cau_hinh.py`, `cau_hinh.schema.json` (5) | 3 |
| TC-1 | Contract hồ sơ, schema mới và ba schema chung nguyên trạng | TC-0, TC-Q13 | Schema nguồn `_chung/contract/ho_so_tra_cuu.schema.json` + bản chép + ba schema chung chép (5) | 3 |
| TC-2 | Nhận tệp yêu cầu, kiểm nguồn/phạm vi/snapshot | TC-1; C-TC-02/03/05 giả trong test | `ho_so.py`, `kiem_dau_vao.py`, `chay.py` (3) | 4 |
| TC-3 | Cắt Điều/Khoản/bảng, bảo toàn offset/nguồn | TC-2 | `cat_doan.py`, `vi_tri.py`, `chay.py` (3) | 4 |
| TC-4 | Chuẩn bị bốn tác vụ AI dùng loại chung | TC-2; AI-2; prompt module | `chuan_bi_ai.py`, `ngu_canh_ai.py`, `chay.py` (3) | 4 |
| TC-5 | Hậu kiểm phân loại, quy tắc 8 nhóm/hàng chờ | TC-4; TC-Q02/03/09…11 cho chính sách thật | `phan_loai.py`, `quy_tac_nhom.py`, `chay.py` (3) | 4 |
| TC-6 | Hậu kiểm câu hỏi/hàm và xếp hạng ứng viên | TC-4; C-TC-03; schema allowlist đã duyệt | `cau_hoi.py`, `xep_hang.py`, `chay.py` (3) | 4 |
| TC-7 | Trả lời hai đường Python/Local, kiểm chứng và mâu thuẫn | TC-4, 6; TC-Q14; C-TC-03/04 | `tra_loi.py`, `kiem_chung.py`, `bang_chung.py`, `chay.py` (4) | 5 |
| TC-8 | Xuất JSON + `truong` tĩnh và metadata cache/K5 | TC-3, 5, 6, 7 | `xuat_ket_qua.py`, `chay.py` (2) | 3 |
| TC-9 | Màn cấu hình/trạng thái bài đo, CAS/pháp nhân | TC-8; C-TC-01 giả | `ui/cau_hinh.js`, `ui/trang_thai.js`, `trang_thai.py`, `chay.py` (4) | 3 |
| TC-10 | DEMO toàn tuyến, bộ chấm chất lượng, độc lập/máy sạch | TC-3…9; TC-Q15 cho kích hoạt thật | Runtime tối đa `chay.py`; còn lại test/DEMO/lock/tài liệu (≤ 1) | 4 |
| TC-11 | Công cụ đo thật và `.cmd` ASCII, **Anh tự chạy** | TC-10; Core/AI/OCR/TX thật cho phép đo tương ứng | `cong-cu/thu_tra_cuu_that.py`, `THU-TRA-CUU-THAT.cmd` (2) | 4 |
| | **Tổng triển khai** | | | **45** |

Bảng độ khó gợi ý (chưa phải phân công model; `de`/`vua`/`kho`):

| Lát | Độ khó | Lý do |
|---|---|---|
| TC-0 | vua | Chép mẫu nhưng phải đúng CAS/cấu hình RAM/manifest khóa |
| TC-1 | vua | Contract đa tác vụ, tách schema với quan hệ Python phải kiểm |
| TC-2 | kho | Nguồn tệp con, snapshot, ranh giới quyền và trần SDK |
| TC-3 | kho | Điều/Khoản/bảng, nguồn OCR không đồng đều, offset không được sai |
| TC-4 | vua | Dựng ngữ cảnh có map nguồn và ngân sách, không tự gọi AI |
| TC-5 | kho | 03/04 và trạng thái danh mục dễ phân loại sai nghiệp vụ |
| TC-6 | kho | Allowlist tham số/thực thể và xếp hạng không thêm nguồn |
| TC-7 | kho | Kiểm khẳng định/số/tiền/nhãn, không biến bịa thành Vàng |
| TC-8 | de | Xuất xác định khi hồ sơ đã kiểm, giữ đủ metadata |
| TC-9 | vua | UI CAS, lỗi và phạm vi pháp nhân; SDK thật còn thiếu |
| TC-10 | kho | Chuỗi giả có đáp án và bộ đo chống rò quyền/cache sai thực thể |
| TC-11 | vua | Công cụ an toàn, phân biệt số thật/chưa đo và ranh giới Core |

Kho tài liệu/Core TC-1 cũ, khảo sát pgvector TC-0 cũ, tìm lai, cache TC-5 cũ, SDK JS TC-6 cũ và nạp hàng loạt TC-7 cũ **không nằm trong 45 giờ**. `ai.nhung_vector@1` thuộc Hỏi AI, thiếu thì ghi Cần Core/lead, không làm bù tại TC.

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

Mỗi khối độc lập đọc cùng phiếu §2–5, chỉ làm lát được giao. Python venv: Windows `.venv/Scripts/python`, Linux `.venv/bin/python`; đặt `PYTHONDONTWRITEBYTECODE=1`/`PYTHONUTF8=1`. Các lệnh kiểm cuối khối áp cho lát code; xử lý CLI ngăn theo §2.5, không ghi đạt thay kết quả lỗi. Mỗi lát một nhánh `codex/e_tra_cuu-tc-n` và một PR do lead mở, không tự commit/push.

### TC-0 — Khung gói SDK 2.0, ngăn và cấu hình
```
Đọc AGENTS.md; docs/goi-gui-engine/API-ENGINE-v1.md; SDK 2.0.0 HUONG-DAN-VIET-ENGINE.md và MAU-PHIEU-ENGINE.md; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §1–5, CLAUDE.md, DAC-TA và YEU-CAU-VA-HIEN-TRANG.md.
Làm TC-0 sau khi lead giao; 3 giờ ƯỚC TÍNH, tối đa 5 tệp mã theo §3:
1. Tạo e_tra_cuu/goi/e_tra_cuu/ theo SDK 2.0: __init__.py, chay.py dùng Engine.tu_khai_bao/app.chay. Không tạo ma-nguon/. Không socket/Bootstrap/SDKEngine, import kho_tri_thuc.*, SQL hoặc gọi engine khác.
2. Chép NGUYÊN _chung/mau-ma/ngan.py, cau_hinh.py vào gói Python. Test SHA-256 sau CRLF→LF cho cả hai, không strip/biên tập; không import _chung ở runtime. Gắn NganBoNho(khai_bao) một lần khi thiếu app.ngan, giữ ngăn SDK khi có; chon_ngan cảnh báo RAM stderr một lần. Cấu hình đọc khóa {} đúng mẫu, không cau_hinh_may/kho_tam.
3. Tạo cau_hinh.schema.json theo §2.4 và KHAI-SDK-2.1.json với cau_hinh/dot_kiem, pham_vi/khoa/duy_nhat/truong và hai màn ui dự kiến. Không đưa trường SDK 2.1 vào manifest 2.0. Schema chỉ dùng tập từ khóa mẫu cấu hình hỗ trợ, additionalProperties=false. Giá trị cấu hình/dữ liệu chỉ qua Ngan; thiếu bản ghi không tự tạo default, việc cần cấu hình trả LoiNghiepVu CHUA_CAU_HINH, câu Việt theo §2.4, khởi động vẫn được.
4. SDK yêu cầu ít nhất một năng lực: khung dùng tra_cuu.kiem_khung@1 (chỉ nội bộ trước phát hành), tep JSON → truong với truong_ra trang_thai van_ban; stub chỉ raise LoiNghiepVu("CHUA_LAM", "Chức năng tra cứu đang được hoàn thiện."). Không có thành công giả, không khai ho_so_tra_cuu trước TC-Q13. TC-1 thay stub bằng năng lực đích trước phát hành, ghi rõ chưa có quy trình người dùng phụ thuộc stub. chay_thu_demo=[] ở khung; 0 demo không phải đã kiểm nghiệp vụ.
5. tests/kiem_doc_lap.py quét gói cấm import Core/engine khác, kênh socket cũ, pycache/pyc/symlink; mã 0/1. CoreGia + NganBoNho chỉ DEMO: stub CHUA_LAM, thiếu/sai cấu hình, default trên bản sao, CAS rollback/unique, dot_kiem bắt buộc phap_nhan_id trong khoa/loc từng lệnh, không đọc chéo/cursor chéo. Không sửa hai mẫu để làm test qua.
Không lưu gì bền trên máy; tạm dọn finally, 0 Cloud/mạng ngoài. Chạy bằng venv (Linux đổi Scripts thành bin), dán kết quả thật:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Lệnh thu khung phải kiểm phiếu và báo 0 demo, pytest không lỗi/skip có lý do, độc lập mã 0. Ghi đã kiểm bằng Core giả (CoreGia) chỉ cho test thực chạy. Cập nhật VIEC/CHANGELOG/NGUON.md và Cần Core; không sửa nguồn cũ/Core/SDK, không commit/push. Báo cáo AGENTS.md §6.
```

### TC-1 — Contract hồ sơ và chỗ nối dữ liệu
```
Đọc AGENTS.md; API-ENGINE-v1.md và hai hướng dẫn SDK 2.0.0; _chung/docs/LOAI-DU-LIEU-RIENG.md (đề xuất TC-P), QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, DAC-TA và YEU-CAU.
Làm TC-1 sau TC-0 và Anh duyệt TC-Q13; 3 giờ ƯỚC TÍNH. Chưa duyệt chỉ hoàn thiện nháp tài liệu, không tạo/kích hoạt schema loại mới:
1. Tạo _chung/contract/ho_so_tra_cuu.schema.json đúng đề xuất đã duyệt ở cuối tài liệu loại chung, chép vào gói; chép ba schema van_ban_tai_lieu/yeu_cau_ai/tra_loi_ai hiện có nguyên trạng. Tối đa 5 tệp schema nguồn/bản chép; test so SHA-256, không thay schema đã khóa hoặc tự đăng ký DTO .v1 lịch sử.
2. Chốt required/enum/trần cho phong bì phien_ban=1, tac_vu/giai_doan, tham chiếu+băm snapshot, băm cấu hình/danh mục, phiên bản engine và tom_tat. Đặc tả snapshot riêng từng tác vụ, mapping nguồn/offset và trạng thái kết quả theo §2; API chỉ một phong bì, không nhan_2. Băm/tep_id không thay quyền Core.
3. Ghi docs/TC-1-CONTRACT.md: JSON yêu cầu và snapshot qua kho Core, danh mục/hàm/bằng chứng do Core cấp tin cậy, quan hệ Python phải kiểm, lỗi LoiNghiepVu TC_SAI_NGUON/TC_SAI_GIAI_DOAN/TC_THIEU_NGU_CANH/TC_QUA_GIOI_HAN. Ba schema chung có $ref/oneOf/type mảng: bộ đọc cau_hinh.py tối thiểu KHÔNG phải validator chung; runtime kiểm miền dữ liệu rõ bằng Python ở TC-2…7, không giả toàn bộ JSON Schema đã được nó hỗ trợ. Không thêm dependency trong lát này.
4. Ghi bản thiết kế metadata cho loại mới đã duyệt và tám năng lực §2.1 vào TC-1-CONTRACT.md. Lát này giữ manifest/chay.py khung TC-0 nhất quán để không phải sửa tệp mã thứ sáu; TC-2 đồng thời thay manifest và stub kiem_khung bằng handler đích trước phát hành. Chưa handler thì không thêm demo thành công. Test CoreGia kiểm đường khung/lỗi hiện có; fixture contract chỉ DEMO, metadata/băm tính thật, không placeholder như kết quả đã tải.
5. Test cặp sai tác vụ/giai đoạn, tham chiếu hỏng, số đếm không khớp, phap_nhan giả khác ngữ cảnh; tệp con giả CoreGia chỉ trong tests. Không chạy Core/AI thật, 0 Cloud. Mọi cấu hình/dữ liệu cần giữ qua Ngan, snapshot ở Core, không tệp bền trên máy.
Chạy và dán kết quả thật bằng venv; 0 demo báo đúng 0, không coi nghiệp vụ đạt:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia) cho phần thực chạy, Cần Core C-TC-02/03/05, cập nhật VIEC/CHANGELOG. Không sửa ma-nguon/, mẫu ngăn/Core/SDK, không commit/push; báo cáo AGENTS.md §6.
```

### TC-2 — Nhận yêu cầu và ghim nguồn qua Core
```
Đọc AGENTS.md, API-ENGINE-v1.md, hướng dẫn SDK 2.0.0; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, LOAI-DU-LIEU-RIENG.md; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5 và TC-1-CONTRACT.md, DAC-TA §2–5.
Làm TC-2 sau TC-1; 4 giờ ƯỚC TÍNH; chỉ ho_so.py, kiem_dau_vao.py, chay.py (3 tệp mã). C-TC-02/03 chưa thật thì dùng adapter tin cậy trong tests, runtime thiếu cửa trả lỗi rõ:
1. tra_cuu.nhan_yeu_cau@1: tep JSON → ho_so_tra_cuu. Đọc via viec.mo_tep, kiểm bam_yeu_cau trên bytes chính xác, JSON ≤1 MiB trước parse; manifest tep_toi_da_mib=20 vì SDK áp trần chung cho tệp con. JSON khóa trùng/NaN/Infinity/UTF-8 hỏng/URL/đường máy/base64 bị từ chối. Không nhận một cờ caller "đã lọc quyền" như chứng nhận Core.
2. Nhận năm tác vụ theo §2.2, mở tệp con chỉ bằng mo_tep khi được Core cấp, kiểm metadata/băm/phiên bản nguồn và quan hệ với nguyên phong bì van_ban_tai_lieu; không tự đọc kết quả engine khác hay CSDL. Pháp nhân lấy từ ngu_canh, thiếu thì TC_THIEU_NGU_CANH; khác phạm vi/quyền nguồn chưa xác thực thì TC_CHUA_CO_CUA_CORE, sai băm thì TC_SAI_NGUON. Module/quyền không suy từ ma_prompt. Kiểm trần 20 MiB/tệp, tổng 64 MiB, văn bản 500000 ký tự/60 trang và danh mục/câu hỏi/hàm/ứng viên §2.3, không cắt ngầm.
3. Ghim cấu hình một snapshot + row_version từ bản đọc nhất quán; thiếu → LoiNghiepVu CHUA_CAU_HINH, sai cấu hình đổi lỗi mẫu thành câu Việt an toàn. Snapshot đầy đủ tải lên Core qua tai_tep_ra, ho_so chỉ tham chiếu+băm+tom_tat nhỏ. Dữ liệu/config chỉ Ngan/kho Core, RAM mất công bố rõ; không tạo cache/sổ trên máy. Không ghi câu hỏi/toàn văn vào log.
4. Đồng thời cập nhật manifest sang tám năng lực/loại đã duyệt §2.1, bỏ stub nội bộ kiem_khung (chưa phát hành). Đăng ký các handler còn chưa làm bằng stub LoiNghiepVu CHUA_LAM, không nộp thành công giả. Chay_thu_demo thêm yêu cầu DEMO có tệp/băm thật khi harness cấp được; tests/chay_demo_voi_core_gia.py nạp NganBoNho và tệp con, không tự khởi tạo dữ liệu DEMO ở runtime. CLI SDK 2.0 không có cấu hình/ngăn thì ghi đúng CHUA_CAU_HINH và cổng bổ sung §2.5, không sửa SDK/đọc env cấu hình cho qua.
Test CoreGia: năm yêu cầu hợp lệ DEMO, sai băm/phiên bản, quá 1 MiB JSON chính, tệp con >1 MiB nhưng ≤20 MiB, >20 MiB, tổng >64 MiB, khóa trùng, không quyền/khác pháp nhân, nguồn OCR rỗng, hủy/mất lease/mất xác nhận. Không adapter test trong runtime; đếm mạng ngoài/Cloud=0. Tạm nếu có dọn finally.
Chạy ba lệnh chuẩn và harness, dán kết quả thật/giới hạn CLI:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), chưa chứng nhận quyền Core thật; cập nhật VIEC/CHANGELOG/Cần Core, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-3 — Cắt cấu trúc và giữ vị trí nguồn
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, TC-1-CONTRACT.md và DAC-TA §3.4, §8–9.
Làm TC-3 sau TC-2; 4 giờ ƯỚC TÍNH; cat_doan.py, vi_tri.py, chay.py (3 tệp). tra_cuu.cat_doan@1: ho_so_tra_cuu tác vụ cat_doan/giai đoạn da_nhan → cùng loại da_cat_doan:
1. Đọc snapshot đã ghim qua Core, giữ nguyên van_ban_tai_lieu và băm bytes nguồn riêng với băm UTF-8 toàn văn. Cắt theo Điều → Khoản → câu/khối/bảng/trang, ghép đơn vị cấu trúc đến mục tiêu do_dai_muc_tieu. Không lấy từng N ký tự hoặc bỏ đuôi; đơn vị >8000 không chia an toàn thì LoiNghiepVu TC_KHONG_CAT_DUOC, vượt tổng trần thì TC_QUA_GIOI_HAN.
2. Đoạn có ma_doan ổn định theo nguồn/phiên bản/offset/bản thuật toán, loại khối, nguyên văn, offset Unicode [bat_dau,ket_thuc), nhãn Điều/Khoản, tep_id/băm/phiên bản, vị trí trang/hộp thực hoặc null, nhóm/hiệu lực từ Core và tình trạng duyệt. Không để phân loại đề xuất tự trở thành metadata đã duyệt. Không bỏ dấu trên nguyên văn; index bỏ dấu/vector do Core quản.
3. Bảng giữ tiêu đề, hàng/cột, ô rỗng/gộp và nguồn ô. Khi tạo đoạn lặp tiêu đề để có ngữ cảnh phải đánh dấu phần ngữ cảnh và map về nguồn; không coi chuỗi tổng hợp là một lát nguyên văn liên tục. Văn bản/ô không có map kiểm được thì từ chối nguồn không nhất quán, không bịa vị trí. DOCX chưa render giữ phong bì so_trang=0/trang=[], đoạn so_trang=null/hop=null.
4. Lưu danh sách đoạn/snapshot qua tai_tep_ra, phong bì tóm tắt so_doan đúng tổng. Không gọi nhung_vector/tìm kiếm/AI, không lưu chỉ mục. kiem_huy theo cụm, tiến độ không chứa nội dung. Config qua Ngan, không tệp bền; tạm dọn finally.
Test CoreGia chỉ DEMO: Điều/Khoản xuyên trang, tiêu đề trùng, cuối tài liệu, trang rỗng, bảng ô gộp/ô trống, NFC và dấu tiếng Việt, số 1.000.000 VND/2026-10-30, DOCX không trang, đơn vị quá dài, vượt số đoạn, hủy. Tái dựng toàn văn từ vùng nguồn phải đủ không mất chữ (phần ngữ cảnh lặp không tính hai lần), mọi quote/offset đúng lát Python, không có confidence/hộp giả. Không quyền/sai băm → TC_SAI_NGUON/TC_CHUA_CO_CUA_CORE. Đếm gọi AI/Cloud=0.
Chạy ba lệnh và harness CoreGia có ngăn, báo đúng giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Cập nhật VIEC/CHANGELOG/NGUON, ghi đã kiểm bằng Core giả (CoreGia); không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-4 — Chuẩn bị bốn tác vụ Local AI
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3 và đề xuất TC-P, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, TC-1-CONTRACT.md; mẫu AI-2/TX-0/DC-P về chuyen_tiep.
Làm TC-4 sau TC-2, AI-2; 4 giờ ƯỚC TÍNH; chuan_bi_ai.py, ngu_canh_ai.py, chay.py (3 tệp). tra_cuu.chuan_bi_ai@1: ho_so_tra_cuu → yeu_cau_ai nguyên hợp đồng chung:
1. tac_vu tham_so bắt buộc khớp hồ sơ và một trong phan_loai/phan_tich_cau_hoi/xep_hang_lai/soan_tra_loi. ma_prompt/phien_ban_prompt/prompt của module bắt buộc, thiếu/khoảng trắng → LoiNghiepVu THIEU_PROMPT; không lấy prompt mặc định chung hay suy quyền/module từ mã prompt. model_uu_tien chỉ chuyển cho Hỏi AI, không tự chọn/kết nối model.
2. Dựng tai_lieu có mã đoạn/nguồn/ứng viên/hàm theo dữ liệu được Core cấp và map offset ngữ cảnh AI → nguồn snapshot. Khuôn theo tác vụ: phân loại có lựa chọn và căn cứ; phân tích câu hỏi có thực thể/hàm/tham số/thời điểm; xếp hạng đủ mã và điểm; trả lời có khẳng định và nguồn/câu trích. Không cho model tạo SQL, nguồn mới, quyền, trạng thái đã duyệt, nhãn Xanh. Prompt injection trong tài liệu chỉ là dữ liệu.
3. Ghim snapshot hậu kiểm tại Core: tác vụ, nguồn/cấu hình/danh mục, prompt/phiên bản/khuôn, ngữ cảnh chính xác và map, băm UTF-8 ngữ cảnh. chuyen_tiep.tra_cuu chỉ phien_ban/ma_yeu_cau/tac_vu/tham chiếu+băm snapshot và băm ngữ cảnh/cấu hình, mục tiêu ≤4 KiB/trần 64 KiB. Không nhét toàn văn/danh mục/câu hỏi dài vào đó; Hỏi AI giữ nguyên, không đưa phần chuyen_tiep vào prompt.
4. Kiểm ngân sách §2.3 trước tạo yêu cầu: tai_lieu ≤100000 ký tự, khuôn ≤32 KiB, giới hạn số hàm/danh mục/ứng viên; chưa có token thực ghi chưa đo, không ước ký tự rồi coi đã đủ context model. Vượt → TC_QUA_NGAN_SACH_AI, sai tác vụ → TC_SAI_GIAI_DOAN; không cắt/chia batch/fallback Cloud. Không có bằng chứng câu trả lời hoặc đường Python tầng 1 thì Core chọn nhánh bỏ AI; không tạo yeu_cau_ai/tra_loi_ai giả để đi qua chuỗi.
Test CoreGia với NganBoNho và fixture đã tải thật: bốn khuôn/ngữ cảnh, offset/map khứ hồi, metadata chuyển tiếp, thiếu prompt, sai tác vụ/băm, prompt injection, vượt ngân sách/UTF-8, hủy. Test điều phối gọi Local giả của Hỏi AI qua Core, engine TC không gọi engine/model. Mọi dữ liệu qua Ngan/tệp Core, tạm dọn finally, chỉ DEMO, 0 Cloud. Nguồn ngoài đã nhận chưa trả do tầng Hỏi AI báo ChuaRo(ma_tuong_quan), TC không đổi thành XONG.
Chạy và báo kết quả thật cùng harness/giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/Cần Core. Không sửa ma-nguon/mẫu chung/Core/SDK, không commit/push; báo cáo §6.
```

### TC-5 — Hậu kiểm phân loại và quy tắc tám nhóm
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5 và DAC-TA §3.2–3.7, YEU-CAU §1.
Làm TC-5 sau TC-4; 4 giờ ƯỚC TÍNH; phan_loai.py, quy_tac_nhom.py, chay.py (3 tệp). Chính sách thật phụ thuộc TC-Q02/03/09/10/11, chưa duyệt chỉ fixture DEMO:
1. tra_cuu.phan_loai_tai_lieu@1: tra_loi_ai → ho_so_tra_cuu da_phan_loai/cho_phan_loai. Kiểm nha_cung_cap=local, đúng tác vụ/prompt/phiên bản/chuyen_tiep/băm, mở snapshot qua Core; cloud → LoiNghiepVu TC_CHI_LOCAL, đổi nguồn → TC_SAI_NGUON, sai khuôn → TC_AI_SAI_KHUON. Không tin riêng kiem_trich_dan.dat của Hỏi AI, tự kiểm căn cứ và offset map.
2. Chỉ chọn nhóm/loại/đối tượng từ snapshot danh mục Core cấp, kiểm trạng thái và loại hình CP/TNHH. Không rõ pháp nhân/bên ký khớp ngữ cảnh → hàng chờ, không chuyển ngữ cảnh sang pháp nhân model đoán. Thiếu ngưỡng phân loại đã đo → không tự xếp; điểm model tự báo không phải xác suất đã hiệu chỉnh. Mọi quyết định máy vẫn là đề xuất, Core quyết xếp/duyệt.
3. Python áp thứ tự đặc tả: công trình/thiết bị lắp đặt/vật tư chủ đầu tư cấp/sửa chữa có thông tin công trình →04; thuê máy dù thi công →03; quy chế lao động/phúc lợi/thưởng phạt →07, còn lại→08. Vật tư/sửa chữa thiếu thông tin công trình →chờ, không suy 03 vì thiếu BOQ. Nhánh nhựa/điện chờ kích hoạt hoặc loại ngừng nhận mới →chờ. Nhóm 06 đúng loại hình, 08 không tự tạo loại/thư mục.
4. Phụ lục làm đổi bản chất chỉ đề nghị chuyển cả bộ kèm căn cứ và trạng thái chờ; Core duyệt/chuyển/ghi nhật ký. Không ghi cây kho, danh mục hay K5 từ engine, không tự tích lũy tài liệu để tạo loại nhóm 08. Cấu hình/dữ liệu cần giữ qua Ngan, snapshot Core, không đĩa bền.
Test CoreGia chỉ DEMO: ma trận tám nhóm và các ranh giới thuê máy/thiết bị lắp/vật tư không BOQ/sửa chữa không dự án/thông tin công trình thiếu, nhựa/điện chưa bật, CP/TNHH, quy chế thưởng phạt, loại lạ/ngừng/thiếu căn cứ/ngưỡng chưa đo, pháp nhân khác, phụ lục đổi bản chất, nguồn sai/Cloud/prompt injection/hủy. Hàng chờ có lý do là kết quả nghiệp vụ, không giả đã xếp. 0 Cloud/AI thật.
Chạy ba lệnh + harness CoreGia có ngăn, dán kết quả thật/giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/Cần Core/Chờ Anh một bảng §5, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-6 — Hậu kiểm câu hỏi, hàm được phép và xếp hạng
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, TC-1-CONTRACT.md và DAC-TA §5–7, §12.
Làm TC-6 sau TC-4; 4 giờ ƯỚC TÍNH; cau_hoi.py, xep_hang.py, chay.py (3 tệp). C-TC-03 thật chưa có chỉ test adapter CoreGia, không gọi hàm module từ engine:
1. tra_cuu.phan_tich_cau_hoi@1: tra_loi_ai Local → ho_so_tra_cuu da_phan_tich. Hậu kiểm cùng nguồn/băm/prompt/tác vụ/chuyen_tiep; kiểm ý định, tập thực thể chính xác với căn cứ câu hỏi, mã có 0 đầu không đổi; ngữ cảnh không rõ thì ghi cần làm rõ, không chọn bừa khoản vay/hợp đồng. Cờ thời điểm lấy từ câu hỏi và mốc Core cấp, không giờ máy/model tự đoán.
2. Hàm chỉ từ allowlist Core cấp: tên/phiên bản/schema tham số, kiểu/ràng buộc/thực thể/phạm vi phải khớp. Sai hàm/SQL/code/URL hay khóa thừa → LoiNghiepVu TC_HAM_KHONG_DUOC_PHEP hoặc TC_AI_SAI_KHUON. Không tự thực thi hàm/truy vấn. Hàm module chưa chạy thì nêu chờ/không khả dụng cho Core chọn tầng 2; không trả dữ liệu tầng 1 giả.
3. tra_cuu.xep_hang_lai@1: tra_loi_ai Local → ho_so_tra_cuu da_xep_hang. Bắt buộc đủ tập mã ứng viên gốc, mỗi mã đúng một lần, điểm hữu hạn trong thang khuôn đã ghim, tie-break ổn định; cấm thêm/bớt/đổi nguồn/phiên bản/nội dung. Điểm chỉ thứ tự, không phải độ tin cậy được duyệt. 0 ứng viên đi đường Core không-AI, không tạo phản hồi giả. Quá 50 ứng viên/ngân sách từ chối TC_QUA_GIOI_HAN/TC_QUA_NGAN_SACH_AI, không top-k ngầm.
4. Snapshot kết quả lưu Core, xuất nguyên tập nguồn phụ thuộc và thực thể cho downstream/cache. RLS lọc TRƯỚC khi ứng viên vào engine/AI là trách nhiệm Core; test giả không chứng minh RLS. Sai nguồn/Cloud → TC_SAI_NGUON/TC_CHI_LOCAL; hủy kiểm từng cụm. Config Ngan, tạm dọn finally, không lưu cache/chỉ mục/nhật ký câu hỏi trên máy.
Test CoreGia chỉ DEMO: VAY-A/VAY-B câu giống nghĩa vẫn khác thực thể; 0 đầu; tháng này theo mốc tin cậy; nhiều thực thể mơ hồ; tên hàm lạ/SQL/kiểu sai/tham số thừa; module chưa chạy; đổi/trùng/thiếu mã ứng viên, NaN/điểm quá thang, tie, khác pháp nhân/nhóm 07, Cloud, hủy. Dùng phản hồi Local giả do test Core điều phối, 0 model thật.
Chạy ba lệnh + harness, dán kết quả thật/giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/Cần Core, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-7 — Soạn và kiểm chứng câu trả lời ba tầng
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5 và DAC-TA §5–7, đặc biệt QĐ-2/QĐ-4 và mâu thuẫn nhãn TC-Q14.
Làm TC-7 sau TC-4/6; 5 giờ ƯỚC TÍNH; tra_loi.py, kiem_chung.py, bang_chung.py, chay.py (4 tệp). Nhãn Xanh thật chờ TC-Q14, test đề xuất DEMO được làm trước. tra_cuu.soan_tra_loi@1: tra_loi_ai hoặc ho_so_tra_cuu → ho_so_tra_cuu da_soan:
1. Đường Local hậu kiểm đúng snapshot/tác vụ/băm/prompt/chuyen_tiep và nha_cung_cap=local, dữ liệu có khuôn/khẳng định/nguồn. Đường ho_so chỉ nhận hồ sơ đã có bằng chứng tầng 1 hợp lệ để điền mẫu Python xác định, hoặc không có căn cứ để trả khong_thay_can_cu; không cho caller truyền văn bản tự do rồi xin Xanh. Không gọi AI/OCR/TX hoặc tự truy vấn tầng khác.
2. Kiểm từng khẳng định: quote nguyên văn/offset đúng ngữ cảnh AI và map về đúng nguồn/phiên bản/Điều/trang thực; tiền/số/ngày gắn đúng trường, thực thể, đơn vị, hiệu lực. Số có trong nguồn nhưng thuộc khoản vay khác không đạt. Tiền luôn {so,tien_te}, dùng số nguyên/Decimal khi kiểm, không suy tỷ giá/tổng/đơn vị; số 0 đầu của mã giữ nguyên. Chuyển định dạng chỉ quy tắc đã khai có căn cứ; không tự suy số mới.
3. Thiếu căn cứ/trích sai/số sai/hỏng quan hệ → trạng thái khong_thay_can_cu, không giữ nội dung bịa rồi hạ Vàng. Sai khuôn metadata/Cloud → LoiNghiepVu TC_AI_SAI_KHUON/TC_SAI_NGUON/TC_CHI_LOCAL. Không có số/căn cứ trả câu Việt rõ, nhan=null. Không biến thiếu quyền/thất bại nguồn thành "không có dữ liệu" thành công.
4. Tầng 1 chỉ đủ nếu đã duyệt, còn hiệu lực, đủ độ tin cậy theo ngưỡng đã đo và đúng trường; thiếu thì ghi lý do để Core quyết tầng tiếp. Không đối chiếu ngược tệp mỗi câu. Cờ văn bản mới chờ duyệt → cảnh báo, tối đa Vàng. Theo phương án TC-Q14: không LLM/tầng 1 đủ mới Xanh, có LLM luôn tối đa Vàng. Model không được cấp nhãn.
5. Nếu bằng chứng được Core cung cấp đã cho thấy mâu thuẫn, trả cả hai nguồn/giá trị kèm co_mau_thuan/can_duyet, không chọn một bên. Dữ liệu mới từ tầng 2–3 đề nghị K5, chưa trở thành dữ liệu đã duyệt. Tập phụ thuộc cache gồm nguồn/phiên bản/mốc công bố/duyệt, thực thể chính xác, phạm vi và cờ thời điểm, không tạo cache trong engine. Snapshot và kết quả ở Core, config qua Ngan, tạm dọn finally.
Test CoreGia/NganBoNho chỉ DEMO: 1.000.000 VND/2026-10-30 đúng nguồn; trích bịa/sai offset/trang giả; số đúng nhưng sai thực thể/tiền tệ; tiền khác tỷ lệ; chưa duyệt/hết hiệu lực/độ tin cậy thấp; ngoài trường đã trích; thiếu ngưỡng; văn bản mới chờ duyệt; hai nguồn mâu thuẫn; không căn cứ không số; Python tầng 1, AI tầng 1, tầng 2/3; Cloud/hủy/sai băm. Đếm Cloud/model thật=0. Không báo ba tầng thật đã chạy khi chỉ adapter nguồn giả.
Chạy và dán kết quả thật cùng harness, giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/Cần Core/bảng chọn TC-Q14; không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-8 — Xuất kết quả tĩnh và nguồn phụ thuộc
```
Đọc AGENTS.md, API-ENGINE-v1.md b.2–b.5, _chung/docs/LOAI-DU-LIEU-RIENG.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, TC-1-CONTRACT.md và DAC-TA §5–6.
Làm TC-8 sau TC-3/5/6/7; 3 giờ ƯỚC TÍNH; xuat_ket_qua.py, chay.py (2 tệp). tra_cuu.xuat_ket_qua@1: ho_so_tra_cuu → truong tĩnh đúng §2.1:
1. Mở snapshot qua Core, kiểm băm/tác vụ/giai đoạn/số đếm và nguồn. Chỉ xuất kết quả đã hậu kiểm/da_cat_doan; da_nhan/cho_ai/sai tác vụ → LoiNghiepVu TC_SAI_GIAI_DOAN, sai nguồn → TC_SAI_NGUON. Không lấy phong bì tóm tắt giả thay danh sách thực trong snapshot.
2. Tải JSON chuẩn UTF-8 lên Core bằng tai_tep_ra, tep_json có tep_id/tên/MIME/kích thước thật; bao gồm đủ kết quả phân loại/đoạn/hàm/xếp hạng/câu trả lời theo tác vụ, căn cứ/nguyên văn/vị trí, băm cấu hình/nguồn/engine, thực thể/tập phụ thuộc cache và cờ K5. Không xuất đường máy/khóa, không chép toàn kho hoặc thêm nguồn không quyền. Không tự lưu JSON trên đĩa.
3. Trả mọi trường khai truong_ra: tac_vu/trang_thai/tra_loi/nhan/nhom_de_xuat/loai_de_xuat/tang/so_doan/so_ung_vien/co_can_cu/co_mau_thuan/can_duyet/tep_json; không áp dụng dùng null, chưa kiểm không gán 0/false. Nhãn đúng cổng TC-7/TC-Q14, không tự nâng ở bước xuất. Tiền/ngày trong JSON vẫn kiểu có tiền tệ/ISO, không chuỗi mất kiểu.
4. Cache/thu quyền/hết hạn/K5 là Core thực thi. Engine chỉ trả metadata/cờ; không ghi "đã lưu cache/đã tạo K5/đã duyệt" nếu chưa có xác nhận Core. Giới hạn JSON ≤20 MiB/phong bì hồ sơ ≤64 KiB, quá → TC_QUA_GIOI_HAN, không cắt danh sách vì bộ lọc UI. Tạm dọn finally, cấu hình/dữ liệu cần giữ chỉ Ngan/Core.
Test CoreGia chỉ DEMO: mỗi tác vụ xuất đủ metadata/tệp, số đếm chính xác, null hợp nghĩa, Vàng/Xanh theo trạng thái duyệt, không căn cứ, mâu thuẫn cả hai bên, nguồn sai/thiếu quyền, tải tệp lỗi/hủy/mất xác nhận không tạo thành công giả, quá trần. Không AI/Cloud thật. Lệnh CLI thiếu cấu hình/tệp con báo đúng §2.5, thêm harness cấp NganBoNho và nguồn DEMO.
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/Cần Core; không sửa ma-nguon/Core/SDK, không commit/push; báo cáo AGENTS.md §6.
```

### TC-9 — Màn cấu hình và trạng thái bài đo trong ngăn
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-DOT-2.md §2, QUYET-DINH-ANH-20261115.md câu 1/2/13, DE-NGHI-SDK-2.1.md §3–5, _chung/mau-ma/README.md; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5.
Làm TC-9 sau TC-8; 3 giờ ƯỚC TÍNH; ui/cau_hinh.js, ui/trang_thai.js, trang_thai.py, chay.py (4 tệp). Đầu vào cấu hình/dot_kiem từ Ngan; đầu ra màn engine và bản ghi có CAS, không phải cây kho/màn hỏi đáp/K5:
1. UI ở e_tra_cuu/goi/e_tra_cuu/ui/, nạp như màn module qua KttCore.engine("e_tra_cuu"). Cấu hình đọc/lưu .cau_hinh, đúng schema §2.4, phien_ban_cau_hinh/CAS; hiển thị ngưỡng chưa đo và chưa cho kích hoạt giả. Không nhập URL/model/khóa AI của engine khác. Thiếu cấu hình runtime vẫn LoiNghiepVu CHUA_CAU_HINH.
2. Màn trạng thái chỉ .ngan.doc/.tim đọc dot_kiem theo pháp nhân Core cho phép; mọi truy vấn kèm phap_nhan_id trong khoa/loc và phân trang ≤500, cursor không đổi phạm vi. Không cấp user quyền Admin để đọc mọi bài đo; Core phải kiểm quyền. Mã/yêu cầu/băm không tự xác thực người dùng.
3. trang_thai.py cập nhật bài đo DEMO qua Ngan: lay_hoac_tao theo phap_nhan_id+ma_dot, cùng khóa gửi lại không nhân số đếm, sửa bằng row_version trong lô. Chỉ tham chiếu/băm báo cáo Core và tử số/mẫu số, không nguyên văn/câu hỏi/tài liệu. Không nhận lời gọi quản trị SDK 2.1 chưa có như đã tồn tại; tests gọi seam thuần, tích hợp ghi bài đo thật chờ cửa Core.
4. KHAI-SDK-2.1.json khai hai màn/quyền và bảng đúng, không thêm trường vào engine.json. Không fetch mạng ngoài, eval, innerHTML chưa lọc; textContent và sự kiện DOM an toàn, ngày dd/mm/yyyy, tiền dấu chấm hàng nghìn kèm tiền tệ, lỗi Việt không lộ path/data. CAS xung đột đọc lại/hiện câu yêu cầu thử lại, không ghi đè âm thầm. Ngăn RAM cảnh báo mất dữ liệu khi khởi động lại.
Test Node tests/ui/ với KttCore giả không mạng: đọc/lưu, thiếu/sai cấu hình, CAS lỗi, XSS chuỗi, chưa đo/null không thành 0%, pháp nhân/cursor chéo bị từ chối, lỗi quyền không hiện dữ liệu. CoreGia+NganBoNho: lay_hoac_tao hai lượt cùng khóa, CAS cả lô rollback, dot_kiem có phap_nhan_id từng thao tác. Chỉ DEMO, 0 Cloud; không ghi tệp cấu hình/sổ/cache, tạm dọn finally.
Chạy ba lệnh + harness §2.5 và node --test e_tra_cuu/tests/ui/*.test.js (hoặc runner Node đã ghi README), báo đúng phần chưa có SDK thật:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia)/KttCore giả, chưa kiểm trình duyệt thật; cập nhật VIEC/CHANGELOG/Cần Core, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-10 — DEMO toàn tuyến, đo chất lượng và gói độc lập
```
Đọc AGENTS.md, API-ENGINE-v1.md, hai hướng dẫn SDK 2.0.0; _chung/docs/LOAI-DU-LIEU-RIENG.md, GIAO-CODEX-DOT-2.md §2; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5 và DAC-TA §6–7/13, mẫu AI/OCR DEMO và TX-6.
Làm TC-10 sau TC-3…9; 4 giờ ƯỚC TÍNH. Chủ yếu test/DEMO/lock/tài liệu, runtime tối đa chay.py; lỗi lớn thì tách lát. TC-Q15 chưa duyệt chỉ đo DEMO, không kích hoạt nhóm:
1. Bộ DEMO có đáp án và nguồn đúng, ưu tiên nhóm 02; có ca tám nhóm/ràng buộc 03/04, câu không đáp án, VAY-A/B, đổi bản/hiệu lực, nhóm 07, mâu thuẫn, câu phụ thuộc thời điểm. Mỗi chỉ số báo tử số/mẫu số riêng: trả lời đúng, trích dẫn đúng, từ chối khi không căn cứ đúng, phân loại đúng; không gộp trung bình hoặc tính ca skip/chưa đo là đạt. Mẫu nghiệp vụ chưa duyệt không coi đã nghiệm thu. Không gắn accuracy thật cho điểm model tự khai.
2. Harness tests/chay_demo_voi_core_gia.py nạp NganBoNho/cấu hình và tệp con DEMO thật; Core điều phối các chuỗi nhận → chuẩn bị → Hỏi AI Local giả → hậu kiểm → xuất; cắt đoạn thuần Python và tầng 1 không LLM có chuỗi riêng. Kiểm đủ năm tác vụ, chỗ nối theo loại, tiền/ngày/offset/snapshot, hủy/mất lease/mất xác nhận. Một ca MayChuGia HTTP loopback kiểm app.chay đọc bootstrap stdin. Không cho engine TC tự gọi provider/engine khác; 0 Cloud.
3. Mô phỏng Core: dữ liệu tầng 1 thiếu/chưa duyệt/hết hiệu lực/ngưỡng thấp/ngoài trường mới đi tầng 2, tầng 3 nền; cache chỉ khớp đúng thực thể/pháp nhân và quyền mọi nguồn, thu quyền/đổi nhóm/phiên bản/duyệt/công bố đổi làm hết hiệu lực; bo_qua_cache có tác dụng. Đây là bài kiểm adapter hợp đồng cho Core, KHÔNG triển khai cache/RLS/runner vào engine hay chứng nhận Core thật. M9/nhóm 07 mọi nhánh Local, nguồn ngoài quyền không được vào ngữ cảnh AI giả. Không có phép đo Core thật thì ghi chưa kiểm.
4. chay_thu_demo có dữ liệu thật/băm thật cho năng lực đã làm; chạy CLI chuẩn và ghi trung thực lỗi CHUA_CAU_HINH/tệp con nếu còn. Cổng harness cùng ví dụ và cấu hình ngăn bổ sung để lead review C-TC-01/02/05, không tự tạo cấu hình mặc định ở runtime hay bỏ demo khó để làm xanh. Không coi 0 demo là đạt nghiệp vụ.
5. requirements.lock chỉ SDK wheel repo + thư viện chuẩn; nếu cần thư viện mới dừng phần phụ thuộc và ghi đề nghị ghim/nguồn/giấy phép, không tự cài. NGUON.md nguồn/băm hai mẫu ngăn và ba schema chung + schema hồ sơ, so CRLF→LF đúng quy định. Công cụ máy sạch .sh/.cmd ASCII cài offline, không bytecode trong goi/. Chạy Linux khi có môi trường, chưa chạy ghi chưa kiểm, không bịa kết quả Windows/Linux.
Test CoreGia/Node UI/máy sạch chỉ DEMO, lỗi LoiNghiepVu theo §2.3, nguồn ngoài đã nhận chưa trả ChuaRo ở tầng sở hữu, không XONG giả. Runtime không lưu bền; tạm dọn finally. Cổng chất lượng đề xuất TC-Q15 cần số đo thật, không lấy test đơn vị thay độ chính xác thực tế.
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Chạy thêm harness/Node và báo số thực + ca chưa kiểm/skip lý do. Ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/NGUON/README và Cần Core, không ghi SẴN SÀNG, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo §6.
```

### TC-11 — Công cụ thử thật và đo model, Anh tự chạy
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, GIAO-CODEX-THU-TU.md §5; e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md §2–5, DAC-TA §13 và công cụ AI-7/TX-6. Lát cuối sau TC-10, 4 giờ ƯỚC TÍNH; Codex KHÔNG chạy máy thật.
1. Tạo e_tra_cuu/cong-cu/thu_tra_cuu_that.py, THU-TRA-CUU-THAT.cmd ASCII và README ngắn. Mặc định CHẠY KHÔ không mạng/ghi bền; chỉ --that cùng địa chỉ Core/đầu vào DEMO do Anh cấp mới gửi việc qua cửa chung Core, không gọi thẳng engine/provider. Khóa nếu cần từ nhập ẩn/handle, không CLI/log/tệp; không đọc .env/cau_hinh.that.toml hoặc dò máy/CSDL/Hot Folder. Cấu hình engine vẫn Ngan, không JSON cấu hình trên máy.
2. Đầu vào bộ câu hỏi/nguồn/đáp án DEMO đã ghim và danh mục/phiên bản/prompt/cấu hình. Kiểm môi trường Core/AI/OCR/TX và embedding có thật; thiếu → LoiNghiepVu("TC_CHUA_CO_MOI_TRUONG_THU", "Chưa đủ môi trường để thử tra cứu. Anh nhờ quản trị viên kiểm tra các dịch vụ cần thiết."). Không sửa Core/Hỏi AI để bù cửa thiếu. Nguồn ngoài đã nhận chưa trả → ChuaRo(ma_tuong_quan), không tự gửi lại mù.
3. Đo phân loại, cắt đoạn/vị trí, câu hỏi/hàm, xếp hạng, câu trả lời/trích dẫn/từ chối, tiền/ngày, bốn tỷ lệ DAC-TA §13/TC-Q15 với tử số/mẫu số. Thử gpt-oss 20B, Qwen3 8B, Gemma đúng ID/runtime phát hiện qua Hỏi AI/Core; model embedding tiếng Việt do lead chọn ứng viên, không đoán hỗ trợ từ tên. Ghi model/version/context hiệu dụng, token vào/ra khi runtime có, thời gian giây, số đoạn/ứng viên; thiếu số=null+kèm lý do. Ký tự/4 chỉ ước lượng, không số đo runtime. Vượt context từ chối, không cắt/chuyển Cloud/tự mở batch.
4. Anh/lead kiểm Core thật: RLS hai pháp nhân/nhóm 07 trước AI, quyền mọi nguồn cache, thực thể A/B, thay phiên bản/đổi nhóm/thu quyền/duyệt/công bố làm hết cache, nút Tra lại từ đầu, tầng 1/2/3 dừng đúng và HTTP 202 cho tầng 3, K5 dữ liệu mới/mâu thuẫn, mở trích dẫn đúng trang hoặc ghi không có trang. Thiếu cửa thì đánh dấu chưa kiểm, không tính đạt. Màn cấu hình/trạng thái nạp đúng khung Core; hỏi đáp/cây kho là UI Core, không sản xuất màn thứ hai.
5. Khảo sát PostgreSQL/pgvector/unaccent/pg_trgm thuộc lead Core: công cụ chỉ nhận kết quả kiểm của Core, không kết nối CSDL hoặc cài extension. Chỉ đo 20 người đồng thời/150 người khi Core có bài tải riêng, không suy từ một lượt model. Chưa có số đo thì không chốt model/ngưỡng hoặc công bố accuracy >90%.
6. Kết quả ưu tiên gửi Core/giữ RAM; chỉ khi Anh chỉ định --bao-cao công cụ đo ngoài runtime mới xuất một artifact DEMO trong workspace được chọn. Không ghi khóa/đường máy/nội dung hồ sơ thật; không phải kho bền của engine. Tạm dọn finally, không ghi vào goi/. Anh tự chạy .cmd, lead review biên bản; không tự chạy --that hoặc thay đổi hệ thống Windows.
Codex test dry-run/parse/lỗi/hủy/chưa rõ/báo cáo thiếu đo bằng CoreGia/adapter giả, 0 Cloud/máy thật. Chạy ba lệnh + harness/Node hồi quy và báo đúng giới hạn CLI §2.5:
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
Ghi đã kiểm bằng Core giả (CoreGia), phép đo thật CHỜ ANH TỰ CHẠY; cập nhật VIEC/CHANGELOG/Cần Core và bảng chọn duy nhất, không ghi SẴN SÀNG, không sửa ma-nguon/Core/SDK, không commit/push; báo cáo AGENTS.md §6.
```

## 5. Cần Core / Chờ Anh của engine này

### 5.1 Cần Core / phụ thuộc lead

| Mã | Cửa chung / việc bên ngoài engine | Làm tạm và giới hạn | Chặn |
|---|---|---|---|
| C-TC-01 | SDK 2.1 ngăn thật/lô/CAS/unique/pháp nhân, cấu hình và nạp UI; CLI/CoreGia nạp ngăn | Mẫu NGAN-0 đã có: chép nguyên, RAM + KttCore giả; `KHAI-SDK-2.1.json` riêng. CLI lỗi phải báo thật + harness bổ sung, không ghi cấu hình đĩa | Tích hợp cấu hình/UI TC-9…11; cổng CLI từ TC-2 |
| C-TC-02 | Ghép nguồn/danh mục/kết quả nhiều bước vào một tệp; quyền mở tệp con và vòng đời/ACK xuyên bước; chuỗi/nhánh Local-only | Adapter CoreGia trong tests; runtime thiếu cửa trả TC_CHUA_CO_CUA_CORE. Không tự đọc đĩa/ket_qua_id hoặc gọi engine | Runtime thật TC-2…8, 10…11 |
| C-TC-03 | Cửa dữ liệu tin cậy: RLS pháp nhân + nhóm + người trước truy vấn, allowlist hàm chỉ đọc, danh mục/hiệu lực/duyệt, thời điểm chuẩn và phạm vi M9/07 | Test CoreGia không chứng minh quyền thật; caller tự khai đã duyệt/đã lọc không đủ. Không đòi route/bảng riêng trong engine | Phân loại/tra cứu thật TC-5…7, 10…11 |
| C-TC-04 | Kho/pgvector/tìm lai/cache/hết hạn theo sự kiện/thu quyền, K5, điều phối 3 tầng, SDK JS hỏi đáp | Engine chỉ xuất kết quả+nguồn+thực thể+cờ. Core/module thực thi, không tạo kho thứ hai. Không có bằng chứng tầng thì không báo tầng đã chạy | Nghiệm thu ba tầng/cache/quyền TC-10…11 |
| C-TC-05 | Log SDK an toàn, kiểm văn bản loại riêng, lỗi quá trần và lease; tùy chọn SDK sau này tách trần đọc tệp con | Mã wheel xác nhận mo_tep dùng trần bước: khai 20 MiB, tự kiểm JSON chính 1 MiB; không sửa private SDK. Kiểm sâu tại engine, báo nợ SDK 2.1 §7; CLI/tệp con kiểm qua harness | An toàn/test tích hợp TC-2, 10…11; không còn chặn do giả định mo_tep 1 MiB |
| L-TC-01 | Hỏi AI `ai.nhung_vector@1` Local, chọn/đo model tiếng Việt; OCR vị trí/bảng và Trích xuất trường mục tiêu sau TX-0 | Không sửa engine khác tại TC; Core giả/adapter bằng chứng DEMO; vector chưa có không báo tìm lai đã đạt | Nhánh tìm lai/tầng 3 và đo TC-11 |
| L-TC-02 | Lead phân định dịch vụ Kho tài liệu dùng chung theo G14 và giao phần Core, đặt bộ DEMO/đáp án do nghiệp vụ duyệt | Không tự triển khai route `/tra-cuu/*`, cây kho/K5/SDK JS trong gói engine. Bộ mẫu chưa duyệt chỉ thử lõi, không bật nhóm | Kích hoạt nghiệp vụ TC-10…11 |
| C-TC-06 | Hợp đồng public discovery/runtime/context/tokenizer/embedding, bài thử nhiều bước và kết quả đo đầy đủ qua cửa chung Core | TC-11 chỉ seam adapter giả; CoreThat khóa trước mạng/khóa, trả TC_CHUA_CO_MOI_TRUONG_THU. Cửa chạy nút module hiện có chưa xác nhận đầy đủ bài đo; không tự đặt route/schema hoặc sửa Core/Hỏi AI | Phép đo thật TC-11; xem TC-11-ADAPTER.md |

### 5.2 Một bảng chọn duy nhất chờ Anh

**Cập nhật 15/11/2026 chiều:** Anh đã duyệt theo cột đề xuất, trừ TC-Q06
tiếp tục **không tự xóa** (`QUYET-DINH-ANH-20261115-CHIEU.md` câu 7).
TC-Q09 là duyệt hướng rà nghiệp vụ rồi chốt danh mục, không tự duyệt mọi
loại hoặc kích hoạt nhựa/điện. TC-Q03/15 vẫn cần số đo/duyệt ngưỡng trước áp
dụng thật; fixture DEMO không chứng nhận các điều kiện đó. Giữ nguyên bảng
duy nhất bên dưới để theo dõi, các nhãn TC-P “chưa duyệt” là lịch sử.

**Đề xuất TC-P, chưa phải quyết định.** Gom toàn bộ chỗ còn hỏi trong DAC-TA §3, 6, 7, 13, 15/YEU-CAU §4, tách câu nhiều ý; bổ sung contract, mâu thuẫn nhãn và tiêu chí đo. Không hỏi lại bốn quyết định QĐ-1…4, ngăn/không lưu máy, 8 nhóm, Local-only M9/07. Cấu hình máy đã biết có GPU và ba họ model không còn là câu hỏi có GPU hay không; chỉ còn runtime/model/context thực tế cần đo. Không có con số chất lượng nào đã đo trong TC-P.

| Mã câu | Câu hỏi một dòng | Lựa chọn đề xuất | Lý do một dòng | Lát nào bị chặn khi chưa chốt |
|---|---|---|---|---|
| TC-Q01 | Tên tệp do Core đặt có thêm mã pháp nhân không? (§3.5/15.1) | Có mã pháp nhân | Dễ phân biệt khi tải khỏi cây kho | Đặt tên thật phía Core/TC-11; không chặn engine |
| TC-Q02 | Ai được sửa danh mục nhóm/loại? (§3.6/15.2) | Chỉ Admin hệ thống; bộ phận gửi đề nghị | Danh mục dùng chung, tránh thay quyền/cấu trúc tùy ý | Quản trị danh mục thật TC-5, 11; DEMO không chặn |
| TC-Q03 | Khi nào gợi ý loại mới nhóm 08? (§3.6/15.2) | Đo và duyệt ngưỡng trước; đợt đầu chỉ đề nghị thủ công | Chưa có dữ liệu để đặt số; không tự tạo thư mục | Gợi ý tự động nhóm 08, ngoài lõi TC-5 |
| TC-Q04 | Cloud mặc định ngoài M9 và nhóm 07 thế nào? (§7/15.3) | Giữ tắt bản đầu; mở sau qua Mask và duyệt riêng | Chưa có nghiệm thu/bí mật; không lách quyết định Mask | Cloud tương lai; không chặn 12 lát Local |
| TC-Q05 | Câu hỏi phụ thuộc thời điểm có tái dùng cache không? (§6/15.4) | Không tái dùng ở bản đầu | Tránh trả lãi suất/trạng thái cũ khi chưa có TTL đo | Cache thời điểm thật C-TC-04/TC-11 |
| TC-Q06 | Giữ nhật ký hỏi đáp bao lâu trước lưu trữ? (§13/15.4) | Chờ Anh chọn theo chính sách lưu trữ doanh nghiệp; không tự xóa | Chưa có chính sách/thẩm quyền để đặt số ngày | Chính sách Core vận hành TC-11; không chặn lõi |
| TC-Q07 | Sao lưu phần chỉ mục dựng lại được theo chu kỳ nào? (§13/15.4) | Lead Core trình theo RPO/RTO và thời gian dựng lại đo được | Không đo thì chưa biết đánh đổi mất dữ liệu/thời gian | Vận hành Core TC-11; tệp gốc vẫn bắt buộc sao lưu |
| TC-Q08 | Dùng model/runtime/context nào cho embedding và bốn tác vụ Local? (§13/15.5) | Đo gpt-oss 20B, Qwen3 8B, Gemma đúng ID phát hiện và model embedding ứng viên | Có GPU không chứng minh sức chứa/chất lượng tiếng Việt; TC-11 chưa đo thật, không chốt model | Chốt model/ngân sách thật TC-11 chờ C-TC-06; DEMO không chặn |
| TC-Q09 | Duyệt danh sách loại chi tiết nhóm 01–07 trong đặc tả chứ? (§3.2/15.6) | Duyệt sau nghiệp vụ rà một lượt; 05 nhựa/điện vẫn chờ kích hoạt | 8 nhóm đã chốt, loại chi tiết chưa chốt toàn bộ | Danh mục thật/phân loại TC-5, 11 |
| TC-Q10 | Bán điện độc lập khác điện năng KCN ở nhóm 05 thế nào? (§15.7) | Điện năng gắn hợp đồng KCN ở 05/kcn; bán điện độc lập ở nhánh chờ kích hoạt | Giữ phân biệt đối tượng nghiệp vụ, không bật nhánh ngầm | Ca phân loại tương ứng TC-5, 11 |
| TC-Q11 | Sửa chữa/bảo trì không gắn dự án xếp dưới đối tượng nào của 04? (§15.8) | 04/sua-chua-bao-tri theo mã tài sản/công trình do Core cấp | Giữ quy tắc đã chốt, không tự ép sang 03; thiếu đối tượng thì chờ | Ca không có dự án TC-5, 11 |
| TC-Q12 | Có nạp hàng loạt tệp rải rác qua hộp nhận không? (§15.9) | Làm sau nghiệm thu nhóm 02, có danh sách DEMO và kế hoạch lưu trữ bản cũ | Không mở phạm vi di chuyển dữ liệu thật trong TC | Nạp hàng loạt phía Core, ngoài 45 giờ |
| TC-Q13 | Duyệt một loại ho_so_tra_cuu và tám năng lực tách chuẩn bị/hậu kiểm theo §2 chứ? (mới, contract) | Lead review rồi Anh duyệt đề xuất ở cuối LOAI-DU-LIEU-RIENG.md | Tái dùng ba loại chung nguyên trạng, không tăng năm loại DTO lịch sử | Schema TC-1 và runtime TC-2 trở đi; TC-0 không chặn |
| TC-Q14 | Xanh chỉ đường Python tầng 1 đã duyệt, câu do LLM soạn tối đa Vàng chứ? (§5 có mâu thuẫn) | **Anh đã duyệt 15/11 chiều:** Có; cờ văn bản mới chờ duyệt luôn hạ Vàng | Giữ trần tin cậy LLM và tránh nhãn do model tự cấp; TC-7 kiểm cả hai đường DEMO | Không còn chờ quyết định nhãn; chạy thật TC-8/11 vẫn chờ Core/quyền và ngưỡng đo TC-Q15 |
| TC-Q15 | Duyệt bộ câu hỏi mẫu/tiêu chí đo và ngưỡng tin cậy trước khi bật từng nhóm chứ? (§13) | Nhóm 02 trước; đo riêng bốn tỷ lệ, mục tiêu >90% từng chỉ số, không rò quyền và không số bịa trong bộ | Không lấy điểm trung bình che lỗi trích dẫn/từ chối; TC-11 chỉ CoreGia/adapter giả, chưa có accuracy/ngưỡng thật | Kích hoạt/hiệu chỉnh TC-5, 7, 10…11 chờ bộ nghiệp vụ/đáp án bổ sung và phép đo thật; không chặn viết công cụ |

Các lựa chọn chưa duyệt chỉ là phương án để test bằng DEMO; không mặc định áp chính sách thật. Phần Core thiếu là yêu cầu bổ sung cửa chung, không xin Anh cho phép engine truy cập SQL/đĩa/gọi engine khác. Trước nối Core thật chỉ ghi “đã kiểm bằng Core giả (CoreGia)” cho phần thực sự đã chạy; **TC-P chưa chạy engine/CoreGia**.

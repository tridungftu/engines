# Giao Codex — `e_doi_chieu` (Đối chiếu bản ký) theo SDK 2.0

*Lập 15/11/2026 · Lát DC-P, chỉ tài liệu · Nhánh `codex/e_doi_chieu-dc-p` · PR: chờ lead mở. Mọi số giờ dưới đây là **ƯỚC TÍNH, chưa đo**, không gồm thời gian chờ quyết định, Core hoặc Anh chạy máy thật.*

Căn cứ: `AGENTS.md`; `API-ENGINE-v1.md`; SDK 2.0.0 `HUONG-DAN-VIET-ENGINE.md`, `MAU-PHIEU-ENGINE.md`; `_chung/docs/GIAO-CODEX-THU-TU.md`, `QUYET-DINH-ANH-20261115.md` (câu 1, 2, 12, 13), `GIAO-CODEX-DOT-2.md` §2, `DE-NGHI-SDK-2.1.md`, `LOAI-DU-LIEU-RIENG.md`; hai phiếu mẫu Hỏi AI/OCR; `CLAUDE.md` và toàn bộ ba tài liệu hiện có trong `e_doi_chieu/docs/`. Đã đọc thiết kế TX-0 sau khi lead báo đã gộp. Quyết định ngày 15/11 thắng cách lưu cấu hình/kho tạm trong mẫu cũ. Tên lát trong phiếu này **thay cách chia DC-0…DC-6 lịch sử**, không ghi đè đặc tả gốc.

## 1. Kết luận

- **14 lát DC-0…DC-13, tổng 57 giờ công ƯỚC TÍNH.** DC-P lập phiếu khoảng **1 giờ ƯỚC TÍNH**, ngoài tổng triển khai. Chỉ giao code sau khi lead/Anh duyệt phần thiết kế tương ứng; DC-P không phải phê duyệt đặc tả nháp. Có thể làm khung và test DEMO trong khi chờ những quyết định chỉ chặn tích hợp.
- Đích: `e_doi_chieu/goi/e_doi_chieu/`, SDK 2.0, Python so toàn văn + quy tắc cứng; Core điều phối OCR và Local AI; **0 lượt Cloud**. Báo cáo giữ mọi điểm lệch, bằng chứng hai bên, vùng sửa tay và tình trạng chưa kiểm. Chặn/mở hiệu lực do module thực hiện qua cửa chung của Core.
- **Hiện trạng kiểm kê:** worktree không có `e_doi_chieu/ma-nguon/`, `goi/`, `tests/`, `QUYET-DINH-CUOI-*` hoặc `PHIEU-ENGINE-*.md`. Chỉ có `CLAUDE.md`, `DAC-TA-e_doi_chieu.md`, `YEU-CAU-VA-HIEN-TRANG.md`, `VIEC.md`. Không có lõi đối chiếu tại chỗ để tuyên bố đã tái dùng. Các đường K2 nêu trong tài liệu là tham chiếu chưa được cấp, không truy cập ngoài workspace.
- Tái dùng: ba loại chung và schema hiện có; mẫu SDK; **chép** `ngan.py`, `cau_hinh.py` từ `_chung/mau-ma/` sau NGAN-0; tham khảo bộ đọc DOCX/định vị của Trích xuất và bộ ảnh/OCR của OCR sau khi ghi nguồn, băm và loại hết phụ thuộc cũ. Không import engine khác. `e_ocr/ma-nguon/vung.py` chỉ là tư liệu: còn DTO/import Core cũ, **không chứng minh** năng lực trích vùng đã chạy trên SDK 2.0.
- Không đưa vào gói mới: socket, `Bootstrap`, `SDKEngine`, SQL, route `/doi-chieu` riêng, schema CSDL `loi_doi_chieu` tự quản, gọi OCR/AI trực tiếp, tự phát sự kiện nghiệp vụ hoặc tự mở hiệu lực. Bỏ khỏi thiết kế mới không có nghĩa xóa mã/tài liệu cũ. Engine **không ghi cấu hình, kết quả, sổ hay đệm bền trên máy**.
- Rủi ro lớn: phân trang Word, chữ/số trong bảng, lệch dấu đổi nghĩa, phát hiện sửa tay, quyền đọc nhiều tệp trong một việc. **57 giờ chỉ là dự toán phạm vi đầu**, nhất là DC-8 là bản đầu cần đo; nếu phương pháp sửa tay không đạt thì trình lát bổ sung và dự toán mới, không giảm tiêu chí để khép lát.

## 2. Thiết kế `engine.json` 2.0

### 2.1 Khung và năng lực

Khung: `phien_ban_manifest: 2`, `loai: "engine"`, `ma: "e_doi_chieu"`, `ten: "Đối chiếu bản ký"`, phiên bản đầu `0.1.0`; `tuong_thich: {core: ">=2.0.0 <3.0.0", api: "v1", sdk: ">=2.0.0 <3.0.0"}`; `che_do_chay: "cuc_bo"`; `diem_vao: {lenh: ["{python}", "-m", "e_doi_chieu.chay"], thu_muc: "."}`; `tai_nguyen.so_viec_dong_thoi: 1`, `readiness.thoi_han_giay: 30`, `bi_mat: []`, `webhook: null`. Mọi năng lực `huy_duoc: true`. Không thêm khóa SDK 2.1 vào manifest 2.0.

| Năng lực đề xuất | Nhận | Trả | Vai trò / lát |
|---|---|---|---|
| `doi_chieu.doc_docx@1` | `tep` (DOCX) | `van_ban_tai_lieu` | Đọc bản chuẩn, chặn track changes/comment; DC-2 |
| `doi_chieu.nhan_cap@1` | `tep` (JSON mô tả cặp, do Core/module lập) | `ho_so_doi_chieu` **đề xuất** | Kiểm hai nguồn, băm, snapshot và quyền tệp được Core cấp; DC-3 |
| `doi_chieu.so_van_ban@1` | `ho_so_doi_chieu` | `ho_so_doi_chieu` | Chuẩn hóa, căn đoạn, so hai lượt và quy tắc cứng; DC-3…5 |
| `doi_chieu.phat_hien_sua_tay@1` | `ho_so_doi_chieu` | `ho_so_doi_chieu` | Quét ảnh trang, cắt ảnh vùng nghi sửa; DC-8 |
| `doi_chieu.chuan_bi_ai@1` | `ho_so_doi_chieu` | `yeu_cau_ai` | Chuẩn bị một yêu cầu có khuôn, giữ hồ sơ ở tệp Core; DC-6 |
| `doi_chieu.phan_loai_diem_lech@1` | `tra_loi_ai` | `ho_so_doi_chieu` | Hậu kiểm phản hồi Local; không gọi AI trong hàm; DC-6…7 |
| `doi_chieu.xuat_ket_qua@1` | `ho_so_doi_chieu` | `truong` tĩnh | JSON chuẩn + báo cáo PDF + kết luận/số đếm; DC-9 |

`truong_ra` của bước xuất: `ket_luan` (`van_ban`: mã cố định `khop`, `khop_co_thay_doi_hinh_thuc`, `can_xem`, `lech_nghiem_trong`, `chua_doi_chieu_duoc`), `so_nghiem_trong`, `so_can_xem`, `so_hinh_thuc`, `so_nhieu_ocr`, `so_vung_sua_tay`, `so_trang_ocr_kem` (đều `so`), `da_kiem_du` và `de_nghi_chan` (`co_khong`), `tep_json`, `tep_pdf` (`tep`). Cờ `de_nghi_chan` là khuyến nghị kết quả máy, **không phải** trạng thái xác nhận hay quyền mở hợp đồng. Mọi trường luôn có, chưa có giá trị dùng `null` theo API; không gán số 0 cho hạng mục chưa đo rồi hiểu là sạch.

Danh sách `loai_du_lieu_rieng` dùng đúng tên nguồn: `van_ban_tai_lieu` — “Văn bản tài liệu có vị trí”; `yeu_cau_ai` — “Yêu cầu hỏi AI”; `tra_loi_ai` — “Trả lời AI có trích dẫn”; thêm **sau duyệt DC-Q17** `ho_so_doi_chieu` — “Hồ sơ đối chiếu bản ký”. Không dùng tên DTO cũ `tham_chieu_tep.v1`, `diem_lech.v1`, `ket_qua_doi_chieu.v1` làm loại đã đăng ký.

### 2.2 Đưa hai tài liệu vào một phong bì, nối chuỗi qua Core

API v1 nhận **một** phong bì mỗi bước, không có `nhan_2`, tự ghép nhánh hoặc tự đọc `ket_qua_id`. Đề xuất: Core/module chuẩn bị tệp JSON DEMO trong kho Core gồm `phien_ban: 1`, `ma_cap`, tham chiếu tệp Word/PDF gốc và phiên bản/băm; tham chiếu JSON của hai kết quả **nguyên phong bì `van_ban_tai_lieu`**; danh sách ảnh trang, bản phân trang Word nếu có; metadata kiểm đầu vào, bằng chứng OCR lại và snapshot bộ/quy tắc đã duyệt. Mỗi tệp có đối tượng `tep` chuẩn API + băm bytes. Không nhận đường máy, URL ngoài hoặc bytes base64 lách trần.

Core điều phối riêng `doc_docx` và `ocr.doc_tai_lieu@1`, rồi ghép các tham chiếu thành đầu vào của `nhan_cap`. Nhánh chuẩn bị cặp là **phụ thuộc Core C-DC-02**, không giả định runner tuyến tính 2.0 đã có fan-in. Core phải cấp quyền mở từng tệp con bằng `viec.mo_tep` trong cùng phạm vi pháp nhân/module/việc; băm không thay thế quyền. Chưa có cửa thật thì CoreGia + adapter tệp giả trong tests; runtime thật từ chối `DC_THIEU_NGUON`, không đọc đĩa hoặc tự gọi engine để bù.

Chuỗi sau khi Core chuẩn bị cặp:

`tep JSON cặp → nhan_cap → so_van_ban → phat_hien_sua_tay → chuan_bi_ai → [Core: ai.hoi_theo_yeu_cau@1, chỉ Local] → phan_loai_diem_lech → xuat_ket_qua → truong`.

OCR lại vùng là bước **do Core** bố trí khi có yêu cầu bằng chứng. DC-7 chỉ nhận kết quả đã ghim đúng cặp/điểm/vùng; thiếu thì giữ `can_xem`. Không thêm vòng lặp/fan-out ngầm trong engine. Chưa có cửa OCR vùng thì vẫn thử được đường bảo thủ, chưa nghiệm thu đầy đủ xử lý lệch dấu. Nếu toàn hồ sơ không có điểm cần AI, Core cần cửa chung bỏ qua bước hoặc một chuỗi không AI kết thúc ở bước xuất; engine không trả `tra_loi_ai` giả. Năng lực xuất phải từ chối hồ sơ còn điểm cần phân loại chưa được xử lý.

`ho_so_doi_chieu` chỉ là **một loại mới đề xuất**, dùng cho cả trạng thái và kết quả trung gian (§5 cuối tài liệu loại chung). Tệp snapshot đầy đủ ở kho Core, phong bì mang tham chiếu+băm+giai đoạn+số đếm; không mang toàn văn lặp nhiều lần. Đã cân nhắc:

| Cách mang dữ liệu | Đánh giá |
|---|---|
| `van_ban_tai_lieu` hiện có | Tái dùng nguyên cho **mỗi tài liệu**; không đổi nghĩa một tài liệu thành cặp hay kết quả đối chiếu |
| `bang_trich_xuat` | Không dùng làm hồ sơ: đó là bảng trường theo bộ, không giữ toàn bộ edit script, cặp nguồn, vùng sửa tay và trạng thái kiểm; phần chi tiết còn chờ duyệt TX-0 |
| `tep` JSON ở mọi bước / loại `ho_so_doi_chieu` | `tep` dùng được để vận chuyển file nhưng Core không kiểm được chỗ nối nghiệp vụ; đề xuất một loại riêng để phân biệt hồ sơ, vẫn dùng `tep` cho tệp gốc và snapshot. Chờ DC-Q17, không tự kích hoạt |

### 2.3 Tham số bước, cấu hình và giới hạn

**`tham_so` không chứa cấu hình máy hoặc bí mật.** Bảng dưới là thiết kế cụ thể để Codex khai bằng các kiểu API cho phép; chuỗi JSON kiểm nghiêm, trùng khóa/NaN/sai băm đều từ chối.

| Năng lực | `tham_so` | Kiểu / mặc định / kiểm |
|---|---|---|
| `doc_docx` | Không có | Không tự Accept All, xóa comment hoặc chọn phiên bản |
| `nhan_cap` | `bam_yeu_cau` | `van_ban`, bắt buộc, `toi_da: 71`; `sha256:` + 64 hex của bytes tệp JSON được ghim |
| `so_van_ban` | `bo_quy_tac_json`, `bam_bo_quy_tac` | `van_ban`, bắt buộc; JSON ≤ 64 KiB UTF-8, chuỗi ≤ 65.536 ký tự; băm ≤ 71 ký tự. Bộ khai vùng bảo vệ/bên ký/từ điển/ngưỡng **đã được duyệt**, không có bộ nới lỏng mặc định |
| `phat_hien_sua_tay` | `che_do` | `chon`, chỉ `day_du` ở bản đầu; không có chế độ bỏ quét rồi kết luận Khớp |
| `chuan_bi_ai` | `ma_prompt`, `phien_ban_prompt`, `prompt`, `model_uu_tien` | `van_ban`; ba trường đầu bắt buộc, mã ≤ 200, phiên bản ≤ 100, prompt ≤ 16.000 ký tự; model tùy chọn ≤ 200. Prompt thuộc module, thiếu → `THIEU_PROMPT` |
| `phan_loai_diem_lech` | Không có | Dùng snapshot/băm và bộ quy tắc đã ghim từ hồ sơ, không nạp bộ mới để đổi kết quả giữa chừng |
| `xuat_ket_qua` | Không có | Bản đầu luôn xuất JSON + PDF; không cắt danh sách theo bộ lọc UI |

**Trần đề xuất để đo lại ở DC-13:** `doc_docx`: 20 MiB DOCX, 120 giây, MIME DOCX chuẩn; `nhan_cap`: JSON 1 MiB, `application/json`, 120 giây; các bước hồ sơ/hậu kiểm: `ky_tu_toi_da: 500000`, 300 giây; sửa tay 900 giây; xuất 180 giây. Tất cả có `gioi_han.thoi_han_giay`. Bước AI do phiếu Hỏi AI quản lý (hiện 600 giây). `gioi_han` chỉ áp đầu vào, không gán trần mới lạ vào manifest.

Engine tự kiểm thêm: ≤ 60 trang bản ký; ≤ 500.000 ký tự **mỗi** tài liệu và tổng hai bản ≤ 1.000.000; ≤ 10.000 điểm lệch; hồ sơ JSON ≤ 20 MiB/tệp; ≤ 20 MiB/mỗi tệp gốc/ảnh, ≤ 20 triệu pixel/ảnh, tổng bytes tệp con đọc trong một việc ≤ 128 MiB; DOCX ZIP giải nén ≤ 100 MiB và ≤ 2.000 mục. Kiểm metadata trước, kiểm byte thật khi đọc; vượt trần từ chối `DC_QUA_GIOI_HAN`, không cắt ngầm hoặc trả báo cáo thiếu. Một yêu cầu AI ≤ 100 điểm, `tai_lieu` ≤ 500.000 ký tự, khuôn ≤ 32 KiB, `chuyen_tiep` ≤ 64 KiB (mục tiêu ≤ 4 KiB); vượt → `DC_QUA_NGAN_SACH_AI`, trình thiết kế chia lượt riêng, không tự gửi nhiều lượt. Ngân sách này chưa là số đo sức chứa model.

Thiếu hạng mục kiểm **không được tính là khớp**. Lỗi đầu vào/OCR lỗi là `LoiNghiepVu` (Core/module hiển thị “Chưa đối chiếu được”), không chuyển thành kết quả `khop`. Báo cáo dở chỉ phục vụ xem; `da_kiem_du=false`, `ket_luan=chua_doi_chieu_duoc`, `de_nghi_chan=true` bảo thủ khi thiếu kiểm bắt buộc; cách module chặn trường hợp này cần C-DC-04. Nếu đã có Nghiêm trọng thì vẫn giữ cờ/mọi điểm đó dù lượt chưa kiểm đủ, không che chúng bằng lỗi chung.

**Nguyên tắc so:** giữ nguyên văn bất biến + ánh xạ offset Unicode `[bat_dau, ket_thuc)` từ bản chuẩn hóa về nguồn; tiền `{"so": 1000000, "tien_te": "VND"}`, ngày `2026-10-30`. Không dùng float cho so tiền; không đoán dấu phân cách/tiền tệ. DOCX không được render thì `so_trang=0`, `trang=[]` theo schema có sẵn; giữ cấu trúc/offset ở trường tùy chọn và ghi chưa phân trang, không bịa trang/hộp. So trang vật lý chỉ khi có bản chuẩn phân trang đáng tin, không kết luận đảo/thiếu trang từ hai số trang khác do dàn trang. Thiếu Điều/Khoản khác thiếu trang vật lý; dữ liệu chưa đủ thì báo giới hạn.

### 2.4 Ngăn, cấu hình và màn của engine

Chép mẫu `Ngan`, `NganBoNho`, `NganXungDot`, `chon_ngan(app)` và `doc_cau_hinh` đúng NGAN-0. Tại thời điểm DC-P **chưa có `_chung/mau-ma/` trong worktree**: DC-0 phụ thuộc lead gộp NGAN-0; không tự chế bản thay thế không tương thích. Khi SDK có `app.ngan` thì dùng ngăn thật; chưa có dùng RAM và cảnh báo stderr một lần đúng `GIAO-CODEX-DOT-2.md` §2. Mất RAM khi khởi động lại là giới hạn được công bố, không được coi dữ liệu xác nhận đã bền.

| Bảng ngăn dự kiến | Phạm vi / khóa / duy nhất | Nội dung, nguyên tử/CAS |
|---|---|---|
| `cau_hinh` | `engine`; khóa `ma="cau_hinh"` | Cấu hình, schema và phiên bản; ghi CAS. Không chứa khóa, đường tệp cấu hình hay URL AI/OCR |
| `luot_doi_chieu` | `phap_nhan`; khóa `ma_luot`; duy nhất pháp nhân + băm cặp + băm bộ + phiên bản engine | Tham chiếu/băm snapshot, trạng thái, số đếm; `lay_hoac_tao` chống trùng, cập nhật CAS; không nhét toàn văn vào ô JSON ≤ 64 KiB |
| `xac_nhan` | `phap_nhan`; khóa `ma_xac_nhan`; duy nhất pháp nhân + mã yêu cầu xác nhận | Nhật ký chỉ thêm, lựa chọn/lý do, tham chiếu điểm và danh tính/giờ **Core xác thực**; chốt cùng phiên bản lượt trong một lô |
| `loi_ocr_de_xuat` | `phap_nhan`; khóa băm cặp từ không đổi nghĩa | Số lần/xuất xứ xác nhận, trạng thái chờ/duyệt; duyệt CAS, không tự nhận cặp đổi nghĩa |
| `loi_ocr_da_duyet` | `engine`; khóa băm cặp từ + phiên bản | Admin duyệt thành bộ dùng chung không chứa định danh; người dùng không được ghi trực tiếp. Mỗi lượt ghim snapshot bộ |

Chính sách giữ/xóa do Core/module áp theo hồ sơ, **không tự đặt TTL làm mất nhật ký xác nhận**. Bảng `xac_nhan` cần cửa chung chỉ-thêm + nguồn danh tính tin cậy C-DC-03; API ghi ngăn Admin tổng quát hiện chưa chứng minh các bảo đảm đó. Trong RAM chỉ test mô phỏng, chưa triển khai xác nhận thật. Chưa có cửa này, màn xem được báo cáo nhưng không được hiện “đã lưu xác nhận” hoặc tự mở chặn.

`cau_hinh.schema.json` trong gói: phiên bản cấu hình, mã/băm bộ chuẩn hóa và từ điển đã duyệt, phương pháp/phân bản detector, ngưỡng OCR kém đã đo, các trần nêu §2.3. Cấu hình rỗng không làm engine chết; việc cần cấu hình → `LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › Đối chiếu bản ký › Cấu hình.")`. Ngưỡng chưa đo để `null` và không cho phép kết luận sạch từ detector/trang OCR chưa kiểm; không đặt con số cho đẹp. Địa chỉ Local/model thuộc Hỏi AI; Hot Folder/Tesseract thuộc OCR.

`KHAI-SDK-2.1.json` khai dự kiến các bảng trên (`khoa`, `duy_nhat`, `truong`, `pham_vi`), `cau_hinh.schema`, `giao_dien_quan_tri`; chưa nhập vào `engine.json`. Màn đặt ở `goi/e_doi_chieu/ui/cau_hinh.js`, `ket_qua.js`, `loi_ocr.js`, nạp như màn module, dùng `KttCore.engine("e_doi_chieu")`. Không mở HTTP riêng, không gọi mạng ngoài, không `eval` hoặc `innerHTML` chưa lọc; dựng chữ bằng `textContent`. Test bằng `KttCore` giả ở `tests/ui/`, Node không mạng. Quyền xem kết quả theo hồ sơ cần Core cấp, không cho người dùng quyền Admin ngăn để lách. Ngày dd/mm/yyyy, tiền dấu chấm hàng nghìn kèm mã tiền tệ; ẩn mã kỹ thuật khỏi luồng thao tác.

## 3. Bảng lát

Trần dưới đây tính tệp Python/JS và schema có logic, không tính test/tài liệu/DEMO, manifest và bản khai metadata. Mỗi lát ≤ khoảng 5 tệp mã; nếu triển khai cần hơn phải tách trước và ghi lý do. Schema chung chỉ tạo **sau duyệt**; không sửa API hoặc ba schema đã khóa.

| Lát | Nội dung / yêu cầu | Phụ thuộc | Tệp mã dự kiến (tương đối trong gói, trừ khi ghi khác) | Giờ ƯỚC TÍNH |
|---|---|---|---|---:|
| DC-0 | Khung SDK 2.0 + ngăn/cấu hình + `kiem_doc_lap`; nền mọi DC | NGAN-0; lead giao khung | `__init__.py`, `chay.py`, `ngan.py`, `cau_hinh.py`, `cau_hinh.schema.json` (5) | 3 |
| DC-1 | Chốt contract, khảo sát tệp/OCR, schema; DC-b, f, j | DC-0; DC-Q17 | Schema hồ sơ nguồn + bản chép, ba schema chung chép (5) | 3 |
| DC-2 | Đọc DOCX, chặn sửa đổi/comment; DC-a | DC-0, 1; quy ước vị trí | `doc_docx.py`, `cau_truc.py`, `chay.py` (3) | 4 |
| DC-3 | Nhận cặp, chuẩn hóa, bảo toàn vị trí; DC-b, d | DC-1, 2; C-DC-02 giả trong test; Q16 | `ho_so.py`, `chuan_hoa.py`, `vi_tri.py`, `chay.py` (4) | 4 |
| DC-4 | Căn đoạn/bảng, so hai lượt, kiểm trang/Điều; DC-c, e | DC-3 | `can_chinh.py`, `so_chu.py`, `chay.py` (3) | 4 |
| DC-5 | Quy tắc cứng, tiền bằng chữ; DC-g | DC-4; bộ vùng bảo vệ DEMO | `quy_tac.py`, `tien_chu.py`, `chay.py` (3) | 5 |
| DC-6 | Chuẩn bị/hậu kiểm Local qua Core; DC-h | DC-5; AI-2; C-DC-02; prompt module | `chuan_bi_ai.py`, `hau_kiem_ai.py`, `chay.py` (3) | 5 |
| DC-7 | Lệch dấu 5 bước, OCR lại, OCR kém; DC-f | DC-5, 6; Q12, 14, 15; OCR vùng cho nhánh đủ bằng chứng | `lech_dau.py`, `tu_dien.py`, `chay.py` (3) | 4 |
| DC-8 | Khảo sát + bản đầu phát hiện sửa tay, cắt ảnh; DC-j | DC-3; Q07, 08, 13; nguồn ảnh và detector đo được | `sua_tay.py`, `anh.py`, `chay.py` (3) | 7 |
| DC-9 | Tổng hợp 5 kết luận, JSON/PDF; DC-i, k, l phần máy | DC-5…8; Q04, 15 | `tong_hop.py`, `bao_cao.py`, `chay.py` (3) | 4 |
| DC-10 | Màn cấu hình/kết quả, xác nhận CAS; DC-k, l phần engine | DC-9; Q01…03; C-DC-01, 03, 04 | `ui/cau_hinh.js`, `ui/ket_qua.js`, `xac_nhan.py`, `chay.py` (4) | 4 |
| DC-11 | Danh mục OCR có duyệt, màn Admin; DC-m | DC-7, 10; Q14; C-DC-03 | `loi_ocr.py`, `ui/loi_ocr.js`, `chay.py` (3) | 4 |
| DC-12 | DEMO toàn tuyến, nguồn/thư viện, máy sạch; DC-n phần giả | DC-9…11 | Chỉ sửa `chay.py` nếu cần móc khởi động an toàn (≤ 1) | 3 |
| DC-13 | Công cụ đo trên máy thật, **Anh tự chạy**; DC-n | DC-12; quyết định/bộ mẫu DEMO; Core/OCR/AI thật | `cong-cu/thu_doi_chieu_that.py`, `THU-DOI-CHIEU-THAT.cmd` (2) | 3 |
| | **Tổng triển khai** | | | **57** |

**Độ khó gợi ý** (để phân công, không phải kết quả đo):

| Lát | Mức | Lý do |
|---|---|---|
| DC-0 | de | Theo mẫu SDK/ngăn đã có; cần tránh trường 2.1 trong phiếu 2.0 |
| DC-1 | vua | Ranh giới hai tài liệu, quyền tệp và contract phải thống nhất |
| DC-2 | vua | XML DOCX, bảng/ô gộp và sửa đổi nhiều vùng |
| DC-3 | kho | Chuẩn hóa có thể làm mất khác biệt; cần ánh xạ về nguyên văn |
| DC-4 | kho | Văn bản lặp, bảng và chèn/xóa cấu trúc dễ căn sai |
| DC-5 | kho | Tiền bằng chữ, số/mã/vùng bảo vệ; không được bỏ lọt |
| DC-6 | kho | Ghim hồ sơ và kiểm trích dẫn hai bên, Local-only, chống AI hạ mức |
| DC-7 | kho | Từ có nghĩa và bằng chứng OCR lại quyết định có được ẩn |
| DC-8 | kho | Chưa có detector/số đo; chữ ký, con dấu có thể gây lệch giả |
| DC-9 | vua | Tổng hợp nhất quán và xuất PDF tiếng Việt không cắt nội dung |
| DC-10 | kho | Quyền, xác nhận chỉ-thêm và CAS cần bảo đảm từ Core |
| DC-11 | vua | Quy tắc học có duyệt; không tự học cặp đổi nghĩa |
| DC-12 | vua | Test tích hợp, đóng gói độc lập và kiểm nguồn offline |
| DC-13 | vua | Đo có đáp án, phân biệt thiếu đo và thất bại, cần máy thật |

Lát Core/module không tính vào 57 giờ: cửa ghép cặp/tệp, điều phối OCR/AI/OCR lại, phân quyền/xác nhận bền, hiệu lực CRM/M2/M4/M9 và thông báo. Dự toán này không bao gồm máy OCR/Local AI, model mới hay nguồn từ điển chưa được cấp.

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

Mỗi khối là một lệnh giao độc lập; đọc §2–3 của phiếu để lấy contract, trần, sơ đồ và bảng phụ thuộc. Ba lệnh kiểm áp cho **lát triển khai** dùng Python venv: Windows `.venv\Scripts\python`, Linux `.venv/bin/python`. Không commit/push khi lead chưa giao; nếu worktree đã có nhánh đúng lát thì dùng nhánh đó.

### DC-0 — Khung gói SDK 2.0, ngăn và cấu hình
```
Đọc AGENTS.md, docs/goi-gui-engine/API-ENGINE-v1.md, SDK 2.0.0 HUONG-DAN-VIET-ENGINE.md và MAU-PHIEU-ENGINE.md; _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md, LOAI-DU-LIEU-RIENG.md; e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §1–3 và DAC-TA-e_doi_chieu.md.
Làm DC-0 cho e_doi_chieu, chỉ sau NGAN-0 và khi lead giao lát; khoảng 5 tệp mã, 3 giờ ƯỚC TÍNH:
1. Tạo e_doi_chieu/goi/e_doi_chieu/ theo mẫu SDK; __init__.py, chay.py dùng Engine.tu_khai_bao, không socket/Bootstrap/import kho_tri_thuc.*. Không tạo hoặc sửa ma-nguon/.
2. Chép nguyên _chung/mau-ma/ngan.py và cau_hinh.py vào gói Python; test so SHA-256. Thiếu mẫu thì ghi Cần Core/lead, không tự viết bản khác. chon_ngan(app) chọn app.ngan nếu có, nếu không RAM và cảnh báo stderr một lần theo đợt 2. Không đọc cấu hình đĩa hoặc ghi sổ bền.
3. Tạo cau_hinh.schema.json theo §2.4 và KHAI-SDK-2.1.json cho ngăn/cấu hình/màn. Không cho ba trường SDK 2.1 vào engine.json 2.0. Đầu vào/đầu ra khung chỉ khai doi_chieu.doc_docx@1: tep DOCX → van_ban_tai_lieu; hàm tạm raise LoiNghiepVu("CHUA_LAM", "Chức năng đọc bản Word đang được hoàn thiện."). Chưa khai loại mới chưa được duyệt.
4. chay_thu_demo để [] ở lát khung; không có ví dụ thành công giả. Test CoreGia kiểm CHUA_LAM; việc cần cấu hình thiếu trả CHUA_CAU_HINH, khởi động vẫn được. Không coi 0 ví dụ là bằng chứng nghiệp vụ đã đạt.
5. Tạo tests/kiem_doc_lap.py: quét goi/ không import kho_tri_thuc.*, không socket cũ, __pycache__/.pyc/symlink; trả 0/1. Dùng PYTHONDONTWRITEBYTECODE=1 trong test. Không thêm thư viện ngoài SDK/thư viện chuẩn.
Chỉ DEMO. Chạy .venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu; -m pytest e_doi_chieu/tests -q; e_doi_chieu/tests/kiem_doc_lap.py (đổi sang .venv/bin/python trên Linux). Báo rõ lệnh đầu 0 ví dụ ở khung, đã kiểm bằng Core giả (CoreGia). Cập nhật VIEC.md, CHANGELOG.md; không xóa, không sửa Core/tài liệu cổng, không commit/push. Báo cáo theo AGENTS.md §6.
```

### DC-1 — Contract hồ sơ và khảo sát nguồn
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md (đề xuất DC-P), QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5; đọc DAC-TA và YEU-CAU của engine.
Làm DC-1 sau DC-0; 3 giờ ƯỚC TÍNH. DC-Q17 chưa duyệt thì chỉ hoàn thiện khảo sát/nháp, không tạo schema mới hoặc kích hoạt loại mới:
1. Sau duyệt tạo _chung/contract/ho_so_doi_chieu.schema.json theo đề xuất DC-P đã chốt, chép vào gói cùng ba schema van_ban_tai_lieu, yeu_cau_ai, tra_loi_ai hiện có; đúng 5 tệp schema, test so băm. Không đổi schema chung đã khóa.
2. Thiết kế đầu vào nhan_cap = tep JSON tham chiếu hai bản và đầu ra ho_so_doi_chieu có giai đoạn, tham chiếu snapshot+băm; ghi rõ required/enum/giới hạn và quan hệ cần kiểm bằng Python. Chưa viết handler trong lát này. Không tự thêm nhan_2 hoặc route ghép riêng.
3. Lập docs/DC-1-KHAO-SAT.md: khả năng tọa độ từ/cờ nghi ngờ của nguồn hiện có, DOCX chưa phân trang, OCR vùng SDK 2.0 chưa khai trong phiếu OCR, quyền tệp con C-DC-02, nguồn từ điển/giấy phép, phương án phát hiện sửa tay. Phân biệt đọc được từ mã với CẦN ĐO máy thật; không đọc Hot Folder hay thư mục ngoài workspace.
4. Chỉ dùng fixture DEMO cho phong bì hợp lệ/sai loại/sai băm/hết quyền/thiếu trang ảnh; không bịa confidence hoặc hop. Chưa đủ quyền mở tệp thì đặc tả LoiNghiepVu DC_THIEU_NGUON, không fallback đọc đường máy.
Test schema và manifest bằng CoreGia, giữ test khung CHUA_LAM. Cấu hình/dữ liệu chỉ qua Ngan RAM; không mạng/Cloud. Chạy đủ ba lệnh AGENTS.md §5 bằng venv (thu vẫn 0 demo nghiệp vụ), ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG và Cần Core. Không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-2 — Đọc Word chuẩn và chặn sửa đổi chưa chốt
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §3, YEU-CAU DC-a.
Làm DC-2 sau DC-0, DC-1; 4 giờ ƯỚC TÍNH; tối đa doc_docx.py, cau_truc.py, chay.py. Chỉ SDK + thư viện chuẩn zipfile/XML; nếu chép thuật toán DOCX của Trích xuất phải ghi nguồn/băm, bỏ import engine khác, không sửa nguồn:
1. doi_chieu.doc_docx@1: tep DOCX đọc bytes qua viec.mo_tep → van_ban_tai_lieu, nguon_doc=docx, bam_dau_vao trên bytes thật, nguyên văn và cấu trúc theo thứ tự đoạn/bảng, giữ ô rỗng/ô gộp. Không gọi OCR/AI hoặc chuyển DOCX ra chương trình ngoài.
2. Quét thay đổi chưa chấp nhận và comment ở các phần Word liên quan, kể cả đầu/chân trang, bảng, chú thích. Có thì LoiNghiepVu("DC_WORD_CHUA_CHOT", "Bản Word còn sửa đổi hoặc bình luận. Anh chọn bản đã chốt để đối chiếu."). Không tự Accept All/xóa bình luận. Hỏng/không hỗ trợ vùng chứa nội dung thì DC_WORD_KHONG_DOC_DUOC, không bỏ qua.
3. Chặn ZIP bomb, mục trùng/traversal, XML nguy hiểm, quan hệ ngoài, trần §2.3 trước giải nén; không mở link hoặc nhúng. Cảnh báo vùng chưa xử lý không được coi là đã đọc đủ.
4. Chưa có bản render Word: so_trang=0, trang=[]; thêm cấu trúc/offset tùy chọn theo schema mở, ghi cảnh báo chưa phân trang. Không tạo trang/hộp giả. Bản văn và offset Unicode bất biến để đối chiếu sau.
5. Chay_thu_demo tối thiểu DOCX DEMO sạch → thành công. CoreGia: track changes, comment, tệp hỏng, bảng/ô gộp/ô trống, tiếng Việt, 1.000.000 VND và 2026-10-30, vượt trần, hủy. Kiểm đúng nguyên văn và không mất nội dung bảng.
Không lưu đĩa; tệp tạm nếu bắt buộc dọn trong finally, cấu hình qua Ngan. Chỉ DEMO, 0 Cloud. Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/NGUON.md; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-3 — Nhận cặp và chuẩn hóa có dấu vết
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §3–4.
Làm DC-3 sau DC-1, DC-2, theo DC-Q16 đã chốt; 4 giờ ƯỚC TÍNH; ho_so.py, chuan_hoa.py, vi_tri.py, chay.py:
1. doi_chieu.nhan_cap@1: tep JSON → ho_so_doi_chieu đúng schema được duyệt. Kiểm bam_yeu_cau trước parse nghiêm, tham chiếu/băm/phiên bản hai bản, bytes nguồn, kết quả van_ban_tai_lieu, ảnh trang. Mở mọi tệp qua viec.mo_tep, quyền Core cấp; không tin phap_nhan_id/module tự khai hoặc băm như bằng chứng quyền.
2. Snapshot đầy đủ tải lên Core bằng tai_tep_ra, phong bì chỉ giữ tham chiếu+băm; dùng Ngan.lay_hoac_tao chống trùng theo pháp nhân+băm cặp+bộ+phiên bản engine, CAS khi cập nhật, không ghi sổ đĩa. Thiếu quyền/tệp → LoiNghiepVu DC_THIEU_NGUON; sai băm → DC_SAI_NGUON; OCR lỗi/chuỗi rỗng không thành cặp khớp.
3. Chuẩn hóa NFC, khoảng trắng, dấu nháy/gạch nối và ngắt dòng theo bộ đã duyệt. Giữ nguyên bản gốc, ánh xạ mọi offset chuẩn hóa về nguyên văn và cấu trúc; không bỏ dấu trên bản so chính. Đầu/chân/số trang chỉ bỏ khi nhận diện được và lưu dấu vết; không bỏ số tiền, số hợp đồng hoặc nội dung giống header một cách máy móc.
4. Thiếu cấu hình → CHUA_CAU_HINH. Vượt trần bytes/ký tự/pixel/giải nén theo §2.3 → DC_QUA_GIOI_HAN, không cắt. Không vẽ trang Word giả.
Test CoreGia + NganBoNho + adapter tệp con giả: đúng cặp DEMO, sai băm, nguồn OCR rỗng/lỗi, không quyền/khác pháp nhân, hai việc đồng thời cùng cặp, CAS xung đột, hủy. Test ánh xạ NFC/khoảng trắng/ngắt dòng về đúng lát nguồn, header chứa 1.000.000 VND vẫn giữ. Runtime thiếu cửa Core phải từ chối; không đưa adapter test vào đường chạy thật.
Chỉ DEMO, 0 Cloud/engine khác. Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/Cần Core; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-4 — Căn cấu trúc và so toàn văn hai lượt
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §3–5.
Làm DC-4 sau DC-3; 4 giờ ƯỚC TÍNH; can_chinh.py, so_chu.py, chay.py:
1. doi_chieu.so_van_ban@1: ho_so_doi_chieu → cùng loại ở giai đoạn da_so; ghim snapshot/băm nguồn/bộ. Căn Điều → Khoản → câu, bảng → dòng → ô, giữ các đoạn không ghép được như chèn/xóa, không bỏ đuôi hoặc chỗ lặp.
2. Tạo edit script đầy đủ bằng so có dấu; lượt bỏ dấu chỉ gắn nhóm chi_lech_dau, không xóa điểm. Mỗi điểm có mã ổn định, nguyên văn hai bên, offset Unicode nửa mở, vị trí thực hoặc null, phép chèn/xóa/thay/đảo và căn cứ. Kiểm tái dựng được văn bản hai bên từ edit script, không có đoạn mất.
3. Kiểm thứ tự/thiếu/thừa Điều/Khoản; số trang vật lý chỉ so khi bản chuẩn có phân trang tin cậy. Thay dàn trang không được tự coi thiếu trang. Thiếu bằng chứng phân trang ghi trạng thái chưa kiểm; cấu trúc không căn được → LoiNghiepVu("DC_KHONG_CAN_DUOC", "Chưa căn được cấu trúc hai bản. Anh kiểm tra bản chuẩn và bản nhận dạng.").
4. Giới hạn điểm/ký tự/thời gian §2.3; gọi kiem_huy theo cụm, báo tiến độ không kèm nội dung. Lưu snapshot bằng tai_tep_ra, dữ liệu cần giữ qua Ngan, không đĩa bền.
Test CoreGia: cặp DEMO giống nhau, chèn/xóa cả khoản, đảo Điều, đoạn trùng, thêm cuối văn bản, bảng nhiều ô trống/ô gộp, ngắt dòng khác, cặp thuê/thuế vẫn có điểm, thiếu bằng chứng trang và trang thực bị đảo. Chưa có quy tắc cứng không quảng cáo kết luận sạch. Vượt trần → DC_QUA_GIOI_HAN, không cắt danh sách.
Chỉ DEMO, 0 Cloud/gọi engine khác. Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-5 — Quy tắc cứng và số tiền bằng chữ
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §5.1, YEU-CAU DC-g.
Làm DC-5 sau DC-4; 5 giờ ƯỚC TÍNH; quy_tac.py, tien_chu.py, chay.py:
1. Hoàn thiện so_van_ban: nhận/trả ho_so_doi_chieu, mỗi điểm có muc_san từ Python và danh sách quy tắc trúng. Mọi khác chữ số, ngày/thời hạn, tiền/tỷ lệ/tiền tệ, phủ định/bắt buộc, bên ký/người đại diện/chức vụ/MST/STK/địa chỉ/số hợp đồng, thiếu/thừa/đảo cấu trúc phải lên nghiem_trong. Không chỉ xét vùng AI nhận diện; vùng bảo vệ theo bộ/metadata kiểm được, thiếu nhận diện không được kết luận đã kiểm đủ.
2. Chuẩn dấu phân cách chỉ theo quy ước đã khai; giữ chuỗi số có 0 đầu; 0/O, 1/l, 5/S, 8/B là nghi nhầm OCR vẫn báo. Decimal hoặc số nguyên, không float, không đoán tiền tệ. Tiền luôn {so, tien_te}; ngày YYYY-MM-DD.
3. Kiểm số tiền bằng số ↔ bằng chữ ngay trong bản ký dù hai bản giống nhau. Chỉ tính khi nhận diện đủ cụm/đơn vị; mơ hồ hoặc không phân tích được thì can_xem + da_kiem_du=false cho hạng mục, không mặc nhiên khớp. Chênh đã kiểm được → nghiem_trong, giữ cả nguyên văn/căn cứ.
4. Giữ muc_san và lịch sử quy tắc bất biến cho bước AI; mọi hạ mức trái quy tắc bị chặn. Sai snapshot/bộ → LoiNghiepVu DC_SAI_NGUON hoặc DC_BO_QUY_TAC_KHONG_HOP_LE. Không log số/tên/nguyên văn nghiệp vụ.
Test CoreGia bằng ma trận DEMO mỗi dòng quy tắc ≥ 1 ca dương và ca không lệch: 1.000.000 VND ↔ 1.100.000 VND, VND/USD, 2026-10-30, MST 0 đầu, thêm không/chưa/phải, thuê/thuế trong tên bên ký, mất Điều, số tiền chữ trái số trong cùng bản ký, phân cách mơ hồ. Yêu cầu bắt đủ toàn bộ điểm Nghiêm trọng đã cài trong bộ DEMO, không suy thành tỷ lệ thực tế.
Không ghi đĩa; Ngan + tệp Core, tạm dọn finally. Chỉ DEMO, 0 Cloud. Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-6 — Chuẩn bị Local AI và hậu kiểm phản hồi
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md §2.2–2.3, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §5.2.
Làm DC-6 sau DC-5, AI-2; 5 giờ ƯỚC TÍNH; chuan_bi_ai.py, hau_kiem_ai.py, chay.py:
1. doi_chieu.chuan_bi_ai@1: ho_so_doi_chieu → yeu_cau_ai chuẩn, prompt/module/phiên bản từ tham_so bắt buộc, thiếu → LoiNghiepVu THIEU_PROMPT. Đưa ngữ cảnh nguyên văn có định danh bên trái/phải vào tai_lieu; khuôn gồm ma_diem, nhan, ly_do, câu trích/offset hai bên. Không cho model tự cấp nguồn, quyền hoặc muc_san.
2. Ghim hồ sơ hậu kiểm bằng tệp Core + băm; chuyen_tiep.doi_chieu chỉ mã cặp/phiên bản/tham chiếu/băm, ≤ 64 KiB, mục tiêu ≤ 4 KiB. Hỏi AI phải giữ nguyên chuyen_tiep. Hết trần điểm/ngữ cảnh/khuôn → DC_QUA_NGAN_SACH_AI, không cắt hoặc tự chia lượt.
3. doi_chieu.phan_loai_diem_lech@1: tra_loi_ai → ho_so_doi_chieu; chỉ chấp nhận nha_cung_cap=local, đúng nguồn/cặp/băm/ma_prompt/phiên bản, không thiếu/thừa/trùng mã điểm. Cloud → DC_CHI_LOCAL; sai ghim → DC_SAI_NGUON; sai cấu trúc → DC_AI_SAI_KHUON. Nội dung model không được đổi nguyên văn hay quy tắc Python.
4. Kiểm trích dẫn/offset hai bên trong đúng tai_lieu AI và quay về đúng nguồn. Trích bịa/AI không chắc/khong_thay_can_cu → giữ can_xem; không làm lỗi OCR có căn cứ. AI không hạ muc_san, điểm cứng luôn giữ Nghiêm trọng. Phần chưa được quy tắc cứng xếp là ứng viên, chỉ quyết định hình thức/nhiễu theo đầy đủ bằng chứng DC-7, không coi đó là phép hạ điểm cứng.
5. Engine không gọi Local/Cloud hoặc engine khác; Core gọi ai.hoi_theo_yeu_cau@1. Không có điểm cần AI: kiểm đường Core bỏ qua/chạy chuỗi không AI, không dựng tra_loi_ai thành công giả. Không dùng ChuaRo cho thiếu cấu hình; nguồn ngoài đã nhận mà chưa trả do tầng sở hữu lượt báo ChuaRo(ma_tuong_quan).
Test CoreGia bằng phản hồi DEMO/Local giả do test điều phối: đúng, hạ Nghiêm trọng, trích sai phía/offset, prompt injection trong nguồn, thiếu/trùng mã, cloud, đổi chuyen_tiep, vượt ngân sách, hủy/mất xác nhận ket_qua không nộp trùng. Đếm provider Cloud = 0; không gọi máy thật.
Mọi dữ liệu qua Ngan/tệp Core, không đĩa bền. Chạy ba lệnh AGENTS.md §5 bằng venv; ghi đã kiểm bằng Core giả (CoreGia), cập nhật VIEC/CHANGELOG/Cần Core; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-7 — Lệch dấu năm bước và bằng chứng OCR lại
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §4, YEU-CAU DC-f.
Làm DC-7 sau DC-5, DC-6; 4 giờ ƯỚC TÍNH; lech_dau.py, tu_dien.py, chay.py. Nguồn từ điển thật chờ DC-Q14; chỉ fixture DEMO trong khi chờ, ghi rõ thiếu:
1. Đầu vào/ra ho_so_doi_chieu qua lõi so/hậu kiểm đã có. Phân nhóm chỉ lệch dấu từ edit script; tra âm tiết/từ có nghĩa theo từ điển được ghim phiên bản/băm/nguồn. Không có mục trong từ điển hữu hạn không đủ chứng minh vô nghĩa: không chắc → can_xem. Từ OCR vô nghĩa có căn cứ + không nằm vùng bảo vệ mới xét nhieu_ocr.
2. Các cặp thuê/thuế, lãi/lại, phạt/phát, bán/bàn, không/khống, hạn/hàn đều có nghĩa: không tự bỏ qua. Chỉ xếp nhieu_ocr khi AI Local có căn cứ và OCR lại đúng vùng cùng đọc ra bản Word; cờ nghi ngờ ABBYY chỉ là bằng chứng phụ, không thay OCR lại. Thiếu/vắng/khác kết quả OCR lại → can_xem + ảnh cắt nếu có. Vùng quy tắc cứng không bao giờ thành nhiễu.
3. Core điều phối ocr.trich_vung@1/bộ OCR thứ hai; engine không gọi OCR/Tesseract/Hot Folder. Kiểm bằng chứng đúng băm bản ký, trang, vùng, điểm, phiên bản nguồn, kết quả không rỗng; không nhận cờ tự khai của caller như kết quả nguồn tin cậy. Contract OCR vùng chưa có SDK 2.0 thì ghi Cần Core và giữ can_xem.
4. Tính tỷ lệ lệch dấu theo mẫu số đã định nghĩa (số từ OCR trên trang); 0 từ không phải 0% lỗi. Ngưỡng CẦN ĐO chưa có thì chưa kết luận trang tốt; khi vượt, đánh dấu trang OCR kém và ảnh trang, gom phần nhiễu để xem nhưng vẫn giữ mọi điểm gốc và riêng toàn bộ Nghiêm trọng. Không xóa điểm khỏi snapshot.
5. Thiếu bộ đã duyệt → LoiNghiepVu DC_THIEU_TU_DIEN nếu bước cần nó; sai nguồn → DC_SAI_NGUON; thiếu ngưỡng giữ chưa kiểm, không giả thành công sạch.
Test CoreGia: ma trận cặp có nghĩa, từ vô nghĩa DEMO được chứng minh, từ lạ không trong từ điển, vùng bên ký/tiền bằng chữ, AI đồng ý nhưng OCR lại thiếu/sai/rỗng, OCR đồng ý nhưng AI không chắc, cả hai đồng ý, trang kém vẫn giữ điểm cứng. Dữ liệu/cấu hình qua Ngan, tệp Core, không ghi bền. Chỉ DEMO, 0 Cloud.
Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/Cần Core; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-8 — Phát hiện vùng nghi sửa tay và cắt ảnh
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §6, DC-1-KHAO-SAT.md.
Làm DC-8 sau DC-3; 7 giờ ƯỚC TÍNH cho khảo sát/bản đầu, chưa cam kết tỷ lệ phát hiện; sua_tay.py, anh.py, chay.py. Quyết định phạm vi ký nháy/giáp lai/model thị giác theo Q07, Q08, Q13:
1. Lập so sánh xử lý ảnh dựa vùng chữ/vết đè và Local vision do Core điều phối: dữ liệu/nguồn cần có, ưu/nhược, số đo DEMO, chọn phương pháp có căn cứ. Không tự tải model, không coi mực màu hoặc mọi nét ngoài OCR đều là sửa tay. Chưa chọn/đo được thì báo DC_CHUA_CO_BO_PHAT_HIEN, ghi việc tiếp, không trả danh sách rỗng giả.
2. doi_chieu.phat_hien_sua_tay@1: ho_so_doi_chieu → cùng loại; đọc ảnh trang được Core cấp, kiểm băm/kích thước/pixel/hệ tọa độ; ghi trang đã quét và phương pháp/phiên bản. Phát hiện vết viết/gạch/chèn, trả vùng nghi ngờ, hop, ảnh cắt tai_tep_ra, chữ in bị đè nếu có căn cứ. Không tự đọc chữ tay.
3. Loại trừ khối chữ ký/con dấu/ký nháy chỉ khi có vùng và căn cứ đủ; vùng chồng nội dung hợp đồng không bị loại cả khối để che sửa thật. Không biết thì đánh dấu cần xem. Chỉ danh sách vùng do caller đưa không được tính là detector đã quét đủ trang.
4. Được phép dùng Pillow theo phiên bản/hash đã ghim trong lock OCR của repo sau khi chép đúng dependency cần dùng vào lock engine và ghi NGUON.md; không nhập dependency mới ngoài phần này. Detector khác chưa có nguồn phải trình riêng, không tự cài mạng. Tệp tạm xóa finally; mọi ảnh kết quả ở Core, không đệm trên đĩa.
5. Thiếu ảnh/trang/phương pháp → LoiNghiepVu DC_THIEU_ANH hoặc DC_CHUA_CO_BO_PHAT_HIEN; vượt trần → DC_QUA_GIOI_HAN. Không khẳng định không sửa tay từ kết quả chưa kiểm. Vùng nghi sửa theo chính sách Q04 được giữ để xác nhận, không AI hạ mức cứng.
Test CoreGia + detector giả kiểm giao thức và riêng thuật toán thật trên ảnh DEMO có đáp án: vết gạch/chèn, chữ ký/dấu, nét sát chữ in, không có vết, xoay/tỷ lệ tọa độ, thiếu một trang, detector lỗi, ảnh quá lớn/hỏng, hủy. Tách số đo thuật toán khỏi kết quả mock; thiếu đo ghi null/chưa đo. 0 Cloud, không gọi engine khác.
Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/NGUON và rủi ro/dự toán bổ sung nếu phương pháp không đạt. Không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-9 — Tổng hợp kết luận và xuất báo cáo
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §5.3, §7.
Làm DC-9 sau DC-5…8, theo Q04/Q15; 4 giờ ƯỚC TÍNH; tong_hop.py, bao_cao.py, chay.py:
1. doi_chieu.xuat_ket_qua@1: ho_so_doi_chieu → truong tĩnh đúng §2.1, JSON chuẩn đầy đủ + PDF trong kho Core qua tai_tep_ra. Kiểm snapshot/schema/băm/giai đoạn, không xuất hồ sơ đang chờ phân loại như kết quả cuối. Sai → LoiNghiepVu DC_HO_SO_CHUA_DU hoặc DC_SAI_NGUON.
2. Tổng hợp năm kết luận đúng DAC-TA §5.3. Khop chỉ khi mọi kiểm bắt buộc hoàn thành, không có điểm cần xem/nghiêm trọng/vùng sửa tay/trang OCR kém; nếu chỉ hình thức/nhiễu thì khop_co_thay_doi_hinh_thuc. Chưa kiểm đủ → chua_doi_chieu_duoc, da_kiem_du=false; vẫn giữ điểm Nghiêm trọng đã biết và de_nghi_chan bảo thủ. Không biến OCR lỗi/không căn được/thiếu detector thành khớp. Cần xem không tự chặn khi đã kiểm đủ theo đặc tả; chặn hiệu lực thực tế thuộc module.
3. Báo cáo đầu trang kết luận/số đếm/phần chưa kiểm; từng điểm nguyên văn hai phía, mức/sàn/lý do/vị trí thực/ảnh cắt; toàn bộ nhiễu vẫn trong JSON và phụ lục PDF. UI ẩn mặc định không được làm thiếu tệp báo cáo. Không ghi người đã xác nhận nếu chưa có dữ liệu tin cậy.
4. PDF có tiếng Việt đúng dấu, nhiều trang, không cắt dòng/điểm/ảnh. Cho phép Pillow đã ghim ở DC-8 để dựng trang PDF, dùng font được cấp nguồn/giấy phép và ghi NGUON.md; không lấy font từ đường máy thật hoặc tự thêm thư viện mạng. Thiếu font → DC_THIEU_TAI_NGUYEN; lỗi xuất → DC_KHONG_XUAT_DUOC, không báo thành công thiếu PDF. Kiểm render thủ công trang DEMO dài và trang ảnh.
5. Không phát sự kiện riêng, không SQL hoặc đổi hiệu lực. Tất cả tệp trong RAM hoặc tạm dọn finally, cấu hình và chỉ mục qua Ngan.
Test CoreGia: đủ năm kết luận, thiếu kiểm không Khớp, OCR lỗi, không điểm nhưng thiếu trang, hình thức+nhiễu, đếm khớp JSON/PDF, nhiều điểm dài và ký tự Việt/tiền/ngày, tải tệp lỗi/hủy/mất xác nhận không nhân đôi lượt. Chỉ DEMO, 0 Cloud. Chạy ba lệnh AGENTS.md §5 bằng venv, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-10 — Màn engine và xác nhận có kiểm soát
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §7. Đọc quyết định Q01…04 và hợp đồng Core C-DC-01/03/04 trước tích hợp thật.
Làm DC-10 sau DC-9; 4 giờ ƯỚC TÍNH; ui/cau_hinh.js, ui/ket_qua.js, xac_nhan.py, chay.py:
1. Màn ở goi/e_doi_chieu/ui/, dùng KttCore.engine("e_doi_chieu").cau_hinh/.ngan và cửa chung Core được cấp, không route riêng, HTTP server riêng hoặc mạng ngoài. Không eval/innerHTML chưa lọc; textContent, ẩn mã kỹ thuật, ngày dd/mm/yyyy và tiền có đơn vị. KHAI-SDK-2.1.json khai màn/quyền, không đổi manifest 2.0 bằng khóa mới.
2. Cấu hình đọc/lưu schema + CAS; lỗi xung đột nhắc tải lại, không ghi đè. Màn kết quả hai cột Word/OCR+ảnh, bộ lọc mức, Nhiễu OCR ẩn mặc định nhưng xem được, phần chưa kiểm hiện rõ. Chỉ dùng tham chiếu có quyền Core cấp.
3. Xác nhận bốn lựa chọn: loi_ocr, thay_doi_da_thong_nhat (nội dung đúng bắt buộc), ban_ky_sai, khong_anh_huong (lý do bắt buộc). Người/giờ/quyền lấy từ Core tin cậy, không từ JSON UI. Q03 yêu cầu hai người thì phải đủ và khác người; chưa có cửa quyền thì chỉ mock, không nút lưu thật.
4. Ngan ghi xác nhận chỉ-thêm + CAS phiên bản lượt trong một lô; mã yêu cầu chống trùng. Hai người cùng xác nhận không đè nhau; NganXungDot → LoiNghiepVu("DC_XUNG_DOT", "Kết quả vừa thay đổi. Anh tải lại trước khi xác nhận.", thu_lai_duoc=True). Không cho .ngan.ghi_lo từ UI ghi trực tiếp để vượt nhật ký/quyền; cần cửa C-DC-03. Thiếu → DC_CHUA_CO_CONG_XAC_NHAN, không giả đã lưu.
5. Module/Core tính mở chặn khi mọi điểm bắt buộc được xác nhận hợp lệ, không còn ban_ky_sai và không thiếu kiểm bắt buộc; engine không tự mở. Gửi yêu cầu module qua cửa chung C-DC-04, không phát event hoặc gọi engine khác. Không có Core thật thì ghi rõ phần tích hợp chưa kiểm.
Test CoreGia + NganBoNho và tests/ui Node KttCore giả không mạng: lưu cấu hình, CAS, nội dung HTML độc hại hiện như chữ, bốn lựa chọn, người không quyền, khác pháp nhân, hai xác nhận đồng thời, gửi lại cùng mã, hai người duyệt, còn ban_ky_sai giữ chặn. Ngăn RAM không chứng minh nhật ký đã bền. Chỉ DEMO, không đĩa bền, 0 Cloud.
Chạy ba lệnh AGENTS.md §5 bằng venv và tests/ui bằng Node, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/Cần Core. Không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-11 — Danh mục lỗi OCR có duyệt
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, DE-NGHI-SDK-2.1.md và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §4 (học dần), §8. Phải có Q14 và cửa quyền/xác nhận C-DC-03 trước vận hành thật.
Làm DC-11 sau DC-7, DC-10; 4 giờ ƯỚC TÍNH; loi_ocr.py, ui/loi_ocr.js, chay.py:
1. Đầu vào nghiệp vụ là xác nhận loi_ocr hợp lệ do Core cấp và cặp từ từ hồ sơ đã ghim; đầu ra là đề xuất/bộ từ điển phiên bản mới trong Ngan, không thêm năng lực giả vào manifest 2.0. Chưa có thao tác quản trị SDK thì chỉ test hàm thuần và màn đọc; ghi Cần Core, không tự tạo decorator/API chưa tồn tại.
2. Tự đếm/đề xuất không đồng nghĩa tự duyệt. Chỉ cặp được chứng minh không đổi nghĩa, không vùng bảo vệ/định danh, không cặp thuê/thuế/lãi/lại…; mức tin cậy không rõ → không cho duyệt. Ngưỡng số lần đề xuất phải là cấu hình đã đo/duyệt, không bịa số; đề xuất chưa duyệt không ảnh hưởng kết quả máy.
3. Admin duyệt qua cửa chung, CAS, ghi nhật ký; Ngan.lo nguyên tử khi đổi trạng thái đề xuất và thêm bản đã duyệt. Phạm vi đề xuất theo pháp nhân; bộ chung engine chỉ chứa cặp vô danh đã duyệt. Mỗi lượt cũ giữ snapshot, không đổi kết quả hồi tố.
4. Màn ui/loi_ocr.js trong gói, KttCore.engine("e_doi_chieu"), textContent, không mạng ngoài/eval/HTML chưa lọc. Không tự cho quyền Admin hoặc cho người dùng ghi trực tiếp kho đã duyệt. Lỗi: LoiNghiepVu DC_CAP_DOI_NGHIA, DC_KHONG_DU_CAN_CU, DC_XUNG_DOT (thu_lai_duoc=True); câu Việt không lộ dữ liệu/đường máy.
Test CoreGia + NganBoNho, KttCore giả: đề xuất từ DEMO không đổi nghĩa, cấm cặp đổi nghĩa/vùng bảo vệ, chưa duyệt không dùng, Admin duyệt, gửi lại không đếm hai lần, CAS rollback cả lô, tách pháp nhân, không sửa bộ snapshot lượt cũ. Mọi dữ liệu qua Ngan, không JSON đĩa, chỉ DEMO, 0 Cloud.
Chạy ba lệnh AGENTS.md §5 bằng venv và tests/ui Node, ghi đã kiểm bằng Core giả (CoreGia); cập nhật VIEC/CHANGELOG/Cần Core; không sửa ma-nguon/, không commit/push; báo cáo §6.
```

### DC-12 — DEMO toàn tuyến và gói độc lập
```
Đọc AGENTS.md, API-ENGINE-v1.md, SDK 2.0.0 HUONG-DAN-VIET-ENGINE.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2, LOAI-DU-LIEU-RIENG.md và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §11.
Làm DC-12 sau DC-9…11; 3 giờ ƯỚC TÍNH. Chủ yếu test/tài liệu/DEMO/lock; nếu cần sửa runtime chỉ chay.py, phát hiện lỗi lớn thì tách lát:
1. Chay_thu_demo có đường DOCX DEMO sạch chạy trực tiếp bằng python -m kho_tri_thuc_sdk.thu. Ví dụ hồ sơ có tệp con/ngăn/Local cần fixture: tạo tests/chay_demo_voi_core_gia.py nạp NganBoNho và tệp DEMO, Core điều phối Local/OCR giả; không cài cờ DEMO trong runtime, không ID tệp giả như tệp đã tải thật. Lệnh thu gốc không cần máy AI, tất cả ví dụ đang khai phải đạt; ghi riêng độ phủ còn cần harness.
2. Test toàn chuỗi tep cặp → ho_so → yeu_cau_ai → [Local giả/Core] → tra_loi_ai → ho_so → truong, đủ/sai bằng chứng, năm kết luận, thiếu detector/ảnh/tọa độ, hủy/mất lease/mất xác nhận, CAS/chống trùng/quyền giả. Một ca MayChuGia HTTP loopback kiểm app.chay đọc dòng khởi động. Không sửa SDK để test dễ qua.
3. Đáp án DEMO cài điểm nghiêm trọng và sửa thật đã biết: bắt đủ mọi điểm nghiêm trọng, số sửa thật bị ẩn thành nhiễu = 0. Báo mẫu số/số đếm, không quảng cáo độ chính xác ngoài bộ. Thiếu kiểm/skip phải có lý do, không tính là đạt bài đo đó. CoreGia phải kiểm LoiNghiepVu cho DC_SAI_NGUON, DC_QUA_GIOI_HAN, CHUA_CAU_HINH và lỗi nguồn OCR, không chỉ ca thành công.
4. requirements.lock ghim đúng thư viện/hash được cho phép (SDK cài wheel repo riêng); NGUON.md có nguồn/băm/giấy phép từng phần chép, font/từ điển/detector và dependency. Không tự tải mạng hoặc nhập thư viện mới. Bộ máy sạch .sh và .cmd ASCII cài offline, không tạo pycache trong goi. Không có wheel phù hợp thì ghi thiếu, không tuyên bố đã kiểm Linux nếu chưa chạy.
5. Dữ liệu cần giữ và cấu hình chỉ Ngan, tệp gốc/snapshot/báo cáo ở Core, tạm dọn finally. So băm ba schema chung và mẫu ngăn; không sửa ma-nguon/ hoặc cổng Core. Kiểm UI bằng KttCore giả/Node; chưa xác nhận thao tác trên trình duyệt Core thật.
Chỉ DEMO, 0 lượt Cloud/OCR/AI thật. Chạy đủ ba lệnh AGENTS.md §5 bằng venv, thêm harness và tests/ui; ghi số demo/test thật, đã kiểm bằng Core giả (CoreGia). Cập nhật VIEC/CHANGELOG và danh sách chưa kiểm, không ghi SẴN SÀNG. Không commit/push; báo cáo §6.
```

### DC-13 — Công cụ thử và đo máy thật, Anh tự chạy
```
Đọc AGENTS.md, API-ENGINE-v1.md, _chung/docs/QUYET-DINH-ANH-20261115.md, GIAO-CODEX-DOT-2.md §2 và e_doi_chieu/docs/GIAO-CODEX-e_doi_chieu.md §2–5, DAC-TA §11. Lát cuối, 3 giờ ƯỚC TÍNH; chỉ sau DC-12; không cho Codex chạy bản thật.
1. Tạo e_doi_chieu/cong-cu/thu_doi_chieu_that.py và THU-DOI-CHIEU-THAT.cmd ASCII. Mặc định CHẠY KHÔ, không gọi mạng/ghi báo cáo bền. Chỉ chạy thật khi Anh cấp --that và các tham số/handle cần thiết; không đọc .env/cau_hinh.that.toml hoặc tự tìm thư mục máy thật. Khóa Core nếu cần chỉ từ nhập ẩn/handle, không trong dòng lệnh, tệp hoặc log.
2. Đầu vào bộ DEMO Word, bản in ký/gạch/chèn/scan có đáp án cài sẵn và cấu hình Core theo tham số; không dùng hồ sơ thật. Công cụ gửi việc qua cửa chung Core, không gọi engine trực tiếp hay đọc Hot Folder. Cần Core/OCR/Local thật chưa có thì báo LoiNghiepVu DC_CHUA_CO_MOI_TRUONG_THU; không giả kết quả đạt. Chưa rõ nguồn ngoài đã nhận việc thì báo ChuaRo(ma_tuong_quan), không tự gửi lại gây trùng.
3. Đo tọa độ từ/cờ nghi ngờ ABBYY có thật hay không, OCR lại vùng, thời gian/sức chứa theo số trang/số điểm, từ điển, detector sửa tay, lệch giả/trang, tỷ lệ sửa thật bị ẩn. Ghi tử số/mẫu số, trường chưa đo=null và lý do. Cổng đạt: bắt đủ 100% điểm Nghiêm trọng đã cài và 0 sửa thật bị ẩn trong bộ mẫu; hai chỉ tiêu này không chứng minh bảo đảm trên mọi tài liệu. Ngưỡng detector/lệch giả/OCR kém trình Anh dựa số đo, không đặt trước.
4. Anh kiểm trên trình duyệt Core thật: màn hai cột/ảnh, bốn xác nhận, CAS/quyền, chặn và mở hiệu lực của module, hai người nếu Q03 chọn; lưu bằng chứng DEMO theo hướng dẫn. Codex chỉ test công cụ bằng CoreGia/adapter giả và chạy khô, không báo các ca máy thật đã đạt.
5. Kết quả ưu tiên trả Core/tạm trong RAM. Nếu Anh chỉ định --bao-cao thì công cụ đo ngoài runtime mới ghi một tệp DEMO do Anh chọn trong workspace, không lưu khóa/đường máy/nội dung ngoài DEMO; đây không phải kho/cấu hình của engine. Tệp tạm dọn finally. Không ghi gì vào thư mục gói.
Test chạy khô và parse tham số, hủy/lỗi/chưa rõ, báo cáo thiếu đo không thành đạt bằng CoreGia, 0 Cloud. Chạy ba lệnh AGENTS.md §5 bằng venv để tránh hồi quy, ghi đã kiểm bằng Core giả (CoreGia) và các phép đo thật CHỜ ANH TỰ CHẠY. Cập nhật VIEC/CHANGELOG; không sửa ma-nguon/, không commit/push; báo cáo §6, không ghi SẴN SÀNG.
```

## 5. Cần Core / Chờ Anh của engine này

### 5.1 Cần Core và phụ thuộc lead

| Mã | Cửa chung / phụ thuộc cần có | Làm tạm và giới hạn | Chặn |
|---|---|---|---|
| C-DC-01 | NGAN-0; SDK 2.1 ngăn lô/CAS/duy nhất/phạm vi, cấu hình, nạp màn engine | Chép mẫu khi lead gộp; RAM + KttCore giả; KHAI-SDK-2.1 riêng. Không tệp cấu hình/kho đĩa | DC-0 thiếu mẫu; tích hợp thật DC-10…11 |
| C-DC-02 | Ghép nhiều đầu vào/tệp tham chiếu trong một việc, quyền và vòng đời xuyên bước; điều phối Local-only/OCR vùng/bỏ qua AI không có điểm | CoreGia + tệp giả trong tests; runtime thiếu quyền từ chối; không sửa runner/Core. Nội dung đầu vào không chứng minh nguồn tin cậy | Tích hợp thật DC-3, 6, 7, 12…13 |
| C-DC-03 | Cửa xác nhận/chỉ-thêm có danh tính/giờ/quyền tin cậy, CAS nguyên tử, chống trùng; phân quyền xem hồ sơ và Admin duyệt | Mô phỏng CoreGia/NganBoNho; không cho UI ghi trực tiếp để tự xác nhận; không coi RAM là nhật ký bền | Xác nhận thật DC-10…11 |
| C-DC-04 | Sự kiện kết quả chung và mapping module: chặn/mở hiệu lực, giữ tầng 1, gửi đúng người, giữ chặn khi chưa kiểm được | Engine trả trường/cờ + JSON; Core/module chịu quy trình và trạng thái. Không route/bảng/sự kiện engine tự tạo | Tích hợp hiệu lực/thông báo DC-10, 13 |
| C-DC-05 | Nguồn OCR vùng SDK 2.0, metadata trang/từ/hộp/cờ nghi ngờ, ảnh và bản chuẩn phân trang nếu có | Hợp đồng phối hợp với lead OCR; thiếu bằng chứng giữ cần xem/chưa kiểm, không tự thêm năng lực ở project OCR | Đủ bằng chứng DC-7; kiểm trang DC-4; đo DC-13 |
| C-DC-06 | Log SDK an toàn, trần văn bản trong loại riêng, lease theo Core trả và lỗi giới hạn tệp rõ (SDK 2.1 §7) | Tự kiểm sâu/trần trước xử lý, log mã chung; SDK 2.0 vẫn có nợ chưa khép; không tuyên bố đã vá SDK | Nghiệm thu an toàn/integration DC-12…13 |
| L-DC-01 | Lead cung cấp nguồn được phép dùng: mẫu ngăn, từ điển/font/detector và thư viện offline; K2 nếu muốn tham khảo | Không truy cập đường ngoài repo; nguồn chưa có ghi thiếu, fixture DEMO không thay tài nguyên thật | DC-0, 7…9, 12…13 tùy nguồn |

### 5.2 Một bảng chọn duy nhất chờ Anh

**Đề xuất, chưa phải quyết định.** Tám nhóm câu ở DAC-TA §13/YEU-CAU §4 được tách vì có nhiều ý trong một câu; bổ sung những quyết định triển khai còn hở trong đặc tả thành **17 dòng**. Không có một danh sách gốc đúng 17 câu để chép nguyên. Cột nguồn phân biệt câu gốc và câu rút từ yêu cầu ngầm. Các lựa chọn dưới đây để lead trình Anh **một lượt**, không hỏi rải rác từng lát. Các nguyên tắc đã chốt (Local-only, ngăn, không lưu máy, chặn khi Nghiêm trọng) không hỏi lại.

| Mã câu | Câu hỏi một dòng (nguồn) | Lựa chọn đề xuất | Lý do một dòng | Lát nào bị chặn khi chưa chốt |
|---|---|---|---|---|
| DC-Q01 | Gửi kết quả cho người nộp, phụ trách hợp đồng hay cả hai? (DAC-TA §7.2, §13.1) | **Cả hai**, theo quyền Core | Tránh kết quả nằm ở người tải tệp nhưng không xử lý hợp đồng | Thông báo thật DC-10, 13 |
| DC-Q02 | Ai có quyền xác nhận từng điểm? (DAC-TA §13.1) | **Người phụ trách được module giao quyền**; người nộp có thể đề nghị | Tách gửi tệp với trách nhiệm quyết định | Xác nhận thật DC-10…11, 13 |
| DC-Q03 | Điểm Nghiêm trọng chọn “Thay đổi đã thống nhất” có cần người thứ hai? (§13.1) | **Có**, người có thẩm quyền khác người xác nhận đầu | Tránh một người tự chấp nhận thay đổi trọng yếu | Đường xác nhận/mở chặn DC-10, 13 |
| DC-Q04 | Giữ quy tắc vùng sửa tay chặn như Nghiêm trọng chứ? (DAC-TA §5.1/§13.2 còn hỏi; YEU-CAU §0 đã ghi chặn) | **Giữ chặn**, thống nhất hai tài liệu | Nội dung chưa đọc được không đủ căn cứ mở hiệu lực; đây là khép mâu thuẫn nhãn, không nới quyết định đã chốt | Chốt chính sách DC-9…10, 13; detector vẫn làm |
| DC-Q05 | Nhóm hợp đồng nào phải đối chiếu 100%? (DAC-TA §13.3) | **Vay và xây dựng trước**, nhóm khác Anh chọn | Ưu tiên rủi ro cao; danh sách này là đề xuất, chưa tự áp | Chính sách module/đo nghiệm thu DC-13; không chặn lõi |
| DC-Q06 | Nhóm chưa bắt buộc giữ kiểm mẫu CRM-G5 hay chạy mọi bản ký? (§13.3, quan hệ TL41) | **Giữ kiểm mẫu hiện hành và cho yêu cầu thủ công** | Không tự thay chính sách vận hành CRM | Tích hợp module DC-13 |
| DC-Q07 | Có kiểm đủ ký nháy từng trang trong đợt đầu không? (DAC-TA §6/§13.4) | **Chưa**, chỉ loại trừ vùng ký nháy có căn cứ | Phát hiện sửa tay và kiểm đủ chữ ký là hai bài toán | Phạm vi detector DC-8; không chặn khung |
| DC-Q08 | Có kiểm dấu giáp lai từng trang trong đợt đầu không? (§6/§13.4) | **Chưa**, giữ phạm vi sửa tay | Cần tiêu chí và bộ mẫu riêng để kiểm dấu | Phạm vi detector DC-8, đo DC-13 |
| DC-Q09 | Bản ký vào kho có tự gợi ý đối chiếu khi có Word cùng số không? (§10/§13.5) | **Có gợi ý**, người dùng bấm mới chạy | Giữ quyền chọn cặp/phiên bản, tránh chạy nhầm | Cửa gợi ý Core/module DC-13 |
| DC-Q10 | Có hợp đồng song ngữ trong phạm vi đầu không? (§13.6) | **Có nhận**, ghi rõ ngôn ngữ mỗi phần | Không loại hồ sơ song ngữ một cách ngầm | Phạm vi bộ quy tắc DC-5…7, đo DC-13 |
| DC-Q11 | Nếu song ngữ thì so cả hai phần hay chỉ tiếng Việt? (§13.6) | **So cả hai**, Python giữ mọi khác biệt; chưa đủ từ điển thì cần xem | Không ẩn khác biệt phần có thể có hiệu lực | Đủ kiểm ngôn ngữ DC-5…7, DC-13 |
| DC-Q12 | Có cấp bộ OCR thứ hai và vị trí cho công cụ Anh chạy không? (§13.7) | **Cấp qua cấu hình OCR/công cụ**, lead không chép đường thật vào repo; chưa có giữ cần xem | Có thêm bằng chứng, giữ engine không biết đường máy | Nhánh đầy đủ DC-7, DC-13 |
| DC-Q13 | Máy Local có model thị giác được phép dùng và đủ tài nguyên không? (§13.8) | **Anh/lead xác nhận qua công cụ đo**; chưa có ưu tiên khảo sát ảnh | Quyết định detector cần số đo, không đoán từ tên model | Chọn phương pháp DC-8, đo DC-13 |
| DC-Q14 | Duyệt nguồn từ điển tiếng Việt và bộ cặp không đổi nghĩa sau khảo sát chứ? (bổ sung từ §4, §12 khảo sát) | **Nguồn có giấy phép, bản ghim sạch do lead trình**; chưa cấp dùng DEMO | Từ lạ không tự là từ vô nghĩa; tránh tự ẩn sửa thật | Đủ tài nguyên DC-7, duyệt học DC-11 |
| DC-Q15 | Chốt ngưỡng trang OCR kém, sửa tay và lệch giả sau đo thay vì đặt sẵn chứ? (bổ sung từ §4.5, §6, §11) | **Đo DC-13 rồi duyệt ngưỡng**; giữ bắt đủ điểm cứng/0 sửa thật bị ẩn | Không có cơ sở cam kết accuracy trước khi đo | Chỉ mock khi chưa đo; nghiệm thu DC-7…9, 13 |
| DC-Q16 | Duyệt chuẩn hóa có dấu vết và chỉ bỏ đầu/chân trang được xác minh chứ? (bổ sung từ §3.5, DC-d) | **Có**, không tự bỏ số/tiền/mã; Word chưa render không so trang vật lý | Tránh chuẩn hóa xóa chính khác biệt cần bắt | Quy tắc chính thức DC-3…5 |
| DC-Q17 | Duyệt một loại `ho_so_doi_chieu` thay hai DTO cũ và đường tệp cặp qua Core chứ? (bổ sung từ §9, TL55 §11.4) | **Duyệt sau lead review payload ở cuối tài liệu loại chung** | Ba loại chung giữ nguyên; một hồ sơ mang đủ cặp/bằng chứng, không lạm dụng bảng trích xuất | Schema mới DC-1 và runtime từ DC-3 |

Không coi các giá trị đề xuất trong bảng là mặc định đã được Anh phê duyệt. Core/SDK còn thiếu không phải câu hỏi xin Anh cho phép lách cổng. Trước nối Core thật, mọi báo cáo kiểm phải ghi **“đã kiểm bằng Core giả (CoreGia)”**; việc máy thật và hiệu lực thực tế vẫn chưa kiểm.

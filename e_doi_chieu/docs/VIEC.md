# VIỆC — danh sách việc duy nhất của project `e_doi_chieu`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| DC-S22 | Chuyển Đối chiếu sang SDK 2.2.0, ngăn/cấu hình/SQL, vai trò trường DC-6 và tích hợp Hỏi AI | CHUYEN-SDK-2.2 §2, §4 | Xong mã/kiểm CoreGia; chờ lead merge Git — 15/11/2026 | PR: **chờ lead mở**. DEMO 1/1 ĐẠT; pytest **898 passed, 0 skipped**, kể cả Hỏi AI; kiểm độc lập mã 0; kiểm kê 31 tệp khớp. Nội dung main `12ed8db` đã đồng bộ; merge Git metadata cần lead hoàn tất vì sandbox chỉ cho ghi worktree. |
| DC-7 (phiếu mới) | Lệch dấu năm bước, từ điển ghim, bằng chứng OCR lại và tỷ lệ trang | DC-f; Q12/14/15 | Xong phạm vi CoreGia — 15/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest **881 passed, 0 skipped** (85 ca DC-7); kiểm độc lập ĐẠT, ba mã thoát 0. Chỉ DEMO, 0 Cloud. Nguồn từ điển thật DC-Q14, ngưỡng DC-Q15 và contract OCR vùng C-DC-05 vẫn thiếu. |
| DC-6 (phiếu mới) | Chuẩn bị yêu cầu Local AI, ghim hồ sơ Core và hậu kiểm độc lập nguồn/trích dẫn/sàn Python | DC-h | Xong phạm vi CoreGia — 15/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 796 passed, 0 skipped (88 ca DC-6); kiểm độc lập ĐẠT, ba mã thoát 0. Provider Cloud = 0. Tích hợp Hỏi AI còn C-DC-07, giữ Cần xem bảo thủ. |
| DC-5 (phiếu mới) | Quy tắc cứng, bảo vệ số/định danh và kiểm tiền bằng số ↔ chữ trong bản ký | DC-g | Xong — 15/11/2026 | PR: **chờ lead mở**. Đã sửa ba điểm kiểm độc lập lead. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 629 passed, 0 skipped (222 ca DC-5); kiểm độc lập ĐẠT; cả ba lệnh mã 0. Bộ quét tiền 400.000–500.000 ký tự <2 giây và hủy giữa chừng đạt. Thiếu nhận diện/phân tích giữ chưa đủ kiểm. |
| DC-8 (phiếu mới) | Khảo sát và bản đầu vùng nghi sửa tay, ảnh cắt Core, so sánh phương pháp và đo DEMO | DC-j; Q04/07/08/13 | Xong phạm vi khảo sát/bản đầu — 15/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest **486 passed, 0 skipped** (79 ca DC-8); kiểm độc lập mã 0. Thuật toán thật 12 ca: TP=3/FP=0/FN=3, recall 50%; **chưa đạt vận hành**, giữ chặn/chưa kiểm đủ. Local vision chưa đo. |
| DC-4 (phiếu mới) | Căn cấu trúc, so hai lượt, edit script đầy đủ và kiểm thứ tự trang có bằng chứng | DC-c, e | Xong — 15/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 407 passed, 0 skipped (110 ca DC-4); kiểm độc lập mã 0. Lõi 450.000 ký tự lặp: 1,1848 giây; 500 bảng: 0,1856 giây. Tích hợp phân trang tin cậy vẫn chờ C-DC-05. |
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | DC-0: khảo sát ABBYY (tọa độ từ, cờ nghi ngờ), từ điển tiếng Việt, cách phát hiện sửa tay; dựng bộ mẫu | — | Chờ làm |  |
| 2 | DC-1: đọc DOCX, chuẩn hóa, kiểm trang, căn đoạn, so 2 lượt, quy tắc cứng | DC-a…g | Chờ làm |  |
| 3 | DC-2: lệch dấu 5 bước + dùng `ocr.trich_vung@1` + phân loại qua chuỗi (Local) | DC-f, h | Chờ làm |  |
| 4 | DC-3: phát hiện vùng sửa tay | DC-j | Chờ làm |  |
| 5 | Schema `loi_doi_chieu`, quy trình, sự kiện chặn/mở chặn | DC-l | Chờ Core |  |
| 6 | 8 câu trả lời sau (đặc tả §13) | — | Chờ Anh |  |
| DC-P | Lập phiếu giao Codex theo SDK 2.0 và quyết định 15/11 | DC-a…n | Xong — 15/11/2026 | PR: **chờ lead mở**. Phiếu `GIAO-CODEX-e_doi_chieu.md`: 14 lát DC-0…DC-13, 57 giờ **ƯỚC TÍNH**, bảng độ khó và 14 khối lệnh; 17 câu chọn gom duy nhất tại §5.2. Chỉ tài liệu, chưa tạo gói/chưa code; chờ duyệt thiết kế và giao từng lát. |
| DC-2 (phiếu mới) | Đọc DOCX đã chốt, giữ nguyên văn/bảng/offset, chặn đầu vào không an toàn | DC-a | Xong — 15/11/2026 | PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia): DEMO 1/1 ĐẠT; pytest 153 passed, 0 skipped; kiểm độc lập mã 0. Chi tiết DC-2 bên dưới. |
| DC-3 (phiếu mới) | Nhận cặp, ghim snapshot, chuẩn hóa và ánh xạ về nguyên văn/cấu trúc | DC-b, d; DC-Q16 | Xong — 15/11/2026 | PR: **chờ lead mở**. Đã sửa theo kiểm độc lập lead; đã kiểm bằng Core giả (CoreGia): DEMO Word 1/1 ĐẠT; pytest 297 passed, 0 skipped (144 ca DC-3); kiểm độc lập mã 0. 12.000 nút OCR lề lặp: 0,1190 giây. Tích hợp thật vẫn chờ C-DC-01/02/05/06. |

**Cập nhật sau DC-P:** hàng 0…6 phía trên giữ làm lịch sử cách chia lát cũ, không dùng để giao code. Mã DC-0…DC-13 và phụ thuộc hiện hành theo phiếu mới §3; 8 nhóm câu cũ đã tách/gom thành DC-Q01…DC-Q17 (§5.2). Quyết định chiều 15/11 đã duyệt cả 17 câu theo đề xuất; trạng thái hiện hành theo các dòng phiếu mới và báo cáo từng lát bên dưới.

- Kiểm kê 15/11: không có `ma-nguon/`, `goi/`, `tests/`, `QUYET-DINH-CUOI-*`, `PHIEU-ENGINE-*.md` trong engine; không truy cập mã K2 ngoài workspace, không có mã cũ tại chỗ để port.
- Đề xuất loại `ho_so_doi_chieu` đã ghi **ĐỀ XUẤT DC-P, chờ Anh** ở cuối `_chung/docs/LOAI-DU-LIEU-RIENG.md` §5; chưa tạo schema/kích hoạt. Tái dùng nguyên ba loại `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`; không đổi `bang_trich_xuat`.
- Quy tắc mới: không lưu gì bền trên máy engine; cấu hình/chỉ mục/danh mục/xác nhận qua `Ngan`, snapshot/ảnh/báo cáo qua kho tệp Core; màn trong `goi/e_doi_chieu/ui/`. Không dùng `cau_hinh_may`/`kho_tam` cũ.
- Kiểm DC-P ngày 15/11/2026: regex theo yêu cầu đọc **14/14 khối** §4 (DC-0…DC-13, fence mở trơn); đủ §1…§5; tổng bảng **57 giờ ƯỚC TÍNH**; bảng chọn **17 mã duy nhất**; `git diff --check` mã thoát 0; phạm vi đúng **3 tệp Markdown**, không tạo `goi/`, `ma-nguon/`, `tests/`. Ba lệnh AGENTS.md §5 **không áp dụng cho lát chỉ tài liệu**, theo yêu cầu riêng DC-P; không ghi kết quả CoreGia hoặc test engine như đã chạy.

## DC-9 — 15/11/2026

**Kết luận: Đạt phạm vi DC-9; PR: chờ lead mở.**
Thời điểm bắt đầu **18:39 ngày 15/11/2026 (UTC+7)** theo lead giao;
ước tính trong phiếu **4 giờ**. Đã kiểm bằng Core giả (CoreGia), chỉ DEMO,
0 Cloud; chưa kiểm Core thật/Linux thật hoặc chất lượng OCR/detector thật.

Đã làm trong đúng ba mô-đun runtime `tong_hop.py`, `bao_cao.py`, `chay.py`:

- Đăng ký `doi_chieu.xuat_ket_qua@1`, đúng 11 trường tĩnh §2.1. Mở lại
  snapshot và mọi nguồn bằng `mo_tep`, kiểm schema/băm/kích thước/quyền,
  phong bì/số đếm/giai đoạn, nguyên văn/offset/edit script và sàn Python.
  Phong bì phải khớp chỉ mục Ngăn tin cậy. Còn chờ phân loại/`cho_ai`
  từ chối `DC_HO_SO_CHUA_DU`; sai nguồn/schema/quyền/băm trả `DC_SAI_NGUON`.
- Tổng hợp năm kết luận đúng Q04/Q15, giữ Nghiêm trọng/vùng sửa tay dù
  chưa kiểm đủ. OCR lỗi/thiếu trang/chưa căn được/thiếu detector/ngưỡng
  chưa đo không thành Khớp; số chưa đo là null. Chỉ Cần xem khi kiểm đủ
  không đề nghị chặn. Không xác nhận thay người dùng hoặc đổi hiệu lực.
- Ngoại lệ DC-7 thấp hơn sàn được tính lại bằng **validator DC-7** từ
  snapshot tiền nhiệm, từ điển và manifest OCR vùng tin cậy; không tin
  boolean `ai_dat`/`ocr_lai_dat` trong nội dung. Thiếu manifest cần thiết
  từ chối nguồn, không xuất một nhãn nhiễu không kiểm chứng được.
- Ghim đầu ra DC-8 trong `chay.py` bằng Ngăn/CAS/chống trùng, sau khi
  xác nhận đầu vào cũng đã được engine ghim. Đây là bổ sung cần cho kiểm
  nguồn DC-9; không đổi detector. Snapshot DC-8 lịch sử chưa có chỉ mục
  cần chạy lại bước quét, không tự hợp thức hóa snapshot tự băm.
- JSON chuẩn giữ mọi điểm/nguyên văn/bằng chứng/snapshot, tham chiếu đầu
  vào và băm PDF. PDF có kết luận/số đếm/phần thiếu kiểm ở đầu; từng điểm
  có hai phía, mức/sàn/lý do/vị trí thực và ảnh cắt khi đủ hệ tọa độ; vùng
  sửa tay giữ crop thực DC-8. Không suy đoán trang Word, không ghi người
  đã xác nhận. Toàn bộ nhiễu có trong JSON và phụ lục PDF.
- PDF dựng trong RAM bằng Pillow 12.3.0 đã ghim; Roboto 2.137 nguyên bản
  phân phối offline trong CustomTkinter 5.2.2, Apache 2.0/copyright/SHA
  đóng trong gói, ghi NGUON. Không dùng font hệ điều hành hoặc dò đường
  máy thật. Thiếu/sai font → `DC_THIEU_TAI_NGUYEN`; lỗi dựng/tải đầy đủ
  hai tệp → `DC_KHONG_XUAT_DUOC`; hủy/ChuaRo giữ ngữ nghĩa SDK.
- Lượt xuất qua `viec.ngan`, CAS/chống trùng; gửi lại kết quả đã chốt
  phải mở/kiểm cả JSON/PDF, không báo thành công tệp cũ mất quyền. Tệp
  chỉ ở RAM, không tệp tạm/kho bền trên engine, không SQL/sự kiện riêng.

Kiểm render thủ công bằng `tests/kiem_pdf_dc9_demo.py` + pypdfium2 5.13.0
offline (chỉ QA, đã ghim trong requirements kiểm thử): **8 trang**, PDF
**5.732.118 bytes**, render và xem trang **1, 3, 4, 8**, ảnh cắt tại **4, 8**.
Đã xem lại bản render cuối: chữ Việt đúng dấu, không ô vuông, dòng/điểm
dài xuống trang đủ, ảnh và chân trang không bị cắt. DEMO tại thư mục
ignored `.pytest-tmp-dc9/pdf/`, ngoài gói runtime; không là dữ liệu thật.
PDF dùng raster xấp xỉ 150 dpi, không có lớp text tìm kiếm; JSON là dữ liệu
chuẩn. Trần PDF theo `tep_mib` ≤20 MiB, bảo vệ ≤2.000 trang và thời hạn
180 giây; vượt trần từ chối toàn lượt, không cắt danh sách.

44 ca DC-9 kiểm bảng năm kết luận, thiếu từng kiểm/OCR/trang/detector,
giữ điểm nghiêm trọng, hình thức+nhiễu, đếm khớp tệp, tiếng Việt/tiền/ngày,
12 điểm nguyên văn dài không mất dòng, đường DC-5…8 thật, validator DC-7,
font thiếu/hỏng, tải tệp lỗi/hủy/ChuaRo/mất ACK/gọi lại/mất quyền PDF cũ.
Fixture đủ kiểm là upstream **giả** có nhãn DEMO, không là số đo thật.

Kết quả kiểm cuối bằng `.venv/Scripts/python` Python 3.13.14, SDK 2.2.0
cài offline `--no-index --no-deps` từ wheel repo, băm khớp SHA256SUMS;
Pillow 12.3.0/pytest 9.1.1 có sẵn offline qua system-site-packages.
Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.7.1: mọi ví dụ chạy thử DEMO đều đạt.
1/1 DEMO ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
942 passed in 137.68s (0:02:17)
0 skipped; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0; không __pycache__/.pyc trong gói.

git diff --check
Không có lỗi; mã thoát 0.
```

Đã cập nhật kiểm kê 36 tệp/bytes/SHA của gói; chỉ cập nhật metadata
`sql/kiem_ke.json`, không sửa/chạy SQL. Giữ phiên bản 0.7.1 **chưa phát
hành** của worktree; lead quyết phiên bản phát hành khi gom các lát.
Thời gian thực tế **18:39–19:11 ngày 15/11/2026 (UTC+7)**, khoảng
**0,53 giờ**, so với **4 giờ ƯỚC TÍNH** trong phiếu. Không có quyết định
tạm nới tiêu chí. Bổ sung ghim đầu ra DC-8 nằm trong `chay.py` đã giao;
ba mô-đun runtime đúng phạm vi, thêm metadata/font/giấy phép/test/tài liệu.

### Cần Core / lead — DC-9

- **C-DC-02 (làm rõ):** giữ quyền/vòng đời nguồn, snapshot tiền nhiệm,
  từ điển, crop và báo cáo xuyên bước. Bước xuất phải được Core gắn lại
  manifest `doi_chieu_ocr_vung` tương ứng khi cần kiểm lại ngoại lệ DC-7;
  không lấy metadata quyền từ JSON caller. Core xử lý vòng đời tệp đã tải
  nhưng lượt thất bại/hủy trước khi chốt đủ hai tệp; engine không có API
  xóa tệp và không tự đặt TTL/xóa snapshot.
- **C-DC-03/04:** xác nhận/danh tính/giờ/quyền và hiệu lực thực tế vẫn do
  cửa chung Core/module. DC-9 chỉ trả khuyến nghị và báo cáo máy.
- **Q15/DC-13:** detector DC-8 vẫn thử nghiệm, chưa đủ căn cứ sạch;
  không đổi thành `da_kiem_du=true` chỉ để kiểm năm nhãn đi qua runtime.
  Chờ đo/duyệt thật ngưỡng OCR/detector và cấp từ điển ngoài DEMO.
- Không phát sinh câu cần Anh quyết định mới. Không sửa `ma-nguon/`,
  `_chung/**`, API/SDK/Core, không commit/push.

## DC-S22 — 15/11/2026

**Kết luận: Chưa đạt toàn bộ bước bàn giao vì merge Git metadata bị
sandbox chặn; phần mã và điều kiện kiểm DC-S22 đã đạt.
PR: chờ lead mở.** Bắt đầu **17:51 ngày 15/11/2026
(UTC+7)** theo giờ lead giao. Phiếu `CHUYEN-SDK-2.2.md` §4 chưa có dòng
ước tính riêng DC-S22; không lấy 4 giờ DC-7 làm dự toán chuyển SDK.
Đã kiểm bằng Core giả (CoreGia), dữ liệu/provider Local DEMO, 0 Cloud;
chưa kiểm Core thật hoặc Linux.

**Thời gian thực tế DC-S22: 17:51–18:34:08 ngày 15/11/2026 (UTC+7), khoảng 0.72 giờ.** Phiếu chưa nêu ước tính riêng DC-S22.

- Nhánh `codex/e_doi_chieu-dc-s22` bắt đầu đúng tại DC-7 `9123c48`.
  Đã thử `git merge --no-commit --no-ff origin/main`; sandbox từ chối ghi
  `ORIG_HEAD.lock` vì Git metadata chung nằm ngoài worktree. Không commit/
  push. Đã kiểm không có tệp giao nhau giữa DC-7 và main rồi áp nội dung
  merge từ main **`12ed8db`** (gồm AI-11/AI-12); đây là đồng bộ nội dung,
  **chưa phải merge trong lịch sử Git**. Lead cần hoàn tất bước Git này
  trước khi commit/mở PR; patch đối chiếu ở `.venv/origin-main.patch`.
- `.venv` mới, Python 3.13.14; wheel SDK 2.2.0 cài offline
  `--no-index --no-deps`, SHA-256
  `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`
  khớp `SHA256SUMS.txt`. Pillow 12.3.0 và dependency test ghim đúng bản,
  kiểm bằng pip `--no-index --no-deps`; máy không có wheel dependency
  offline nên dùng `system-site-packages`. SDK cài riêng trong venv.
  Khác với môi trường cô lập hoàn toàn; không tải mạng.
- Manifest 0.7.1 dùng `sdk >=2.2.0 <3.0.0`, khai bốn bảng ngăn và cấu
  hình thật, bỏ bảng `cau_hinh`; thêm SQL chỉ CREATE TABLE trong
  `eng_e_doi_chieu`, đủ bảy cột hệ thống, kiểu và unique khớp manifest.
  `sql/kiem_ke.json` gồm mọi tệp gói trừ chính nó, bytes và SHA thực.
- Bảng pháp nhân chỉ qua `viec.ngan`, bỏ pháp nhân khỏi khóa/lọc/giá trị
  ghi. Dùng `lo.ket_qua` sau lô và đọc lại đúng id/row_version; giữ thử
  lại CAS, chủ/hạn chiếm, chống trùng, phục hồi snapshot, hủy/ACK/giao lại.
  Không xóa/TTL mất lịch sử; nhường `can_thu_lai`. Cột số SDK trả chuỗi,
  chuyển số khi so hạn. Cột `phong_bi` là chuỗi JSON nhỏ vì SDK chưa có
  kiểu json; toàn văn/snapshot/ảnh vẫn ở Core.
- Cấu hình đọc từ bản chụp `viec.cau_hinh`; không đệm cấu hình, không cần
  hook làm mới. Khởi động chưa cấu hình được phép; thiếu từng trường bắt
  buộc vẫn `CHUA_CAU_HINH`. Cấu hình sai kiểu/trần được Core từ chối ngay
  khi `dat_cau_hinh`, test giữ mọi giá trị lỗi cũ và kiểm thời điểm mới.
- Chuyển nguyên bytes ba bản cổng tạm/bản khai vào `LUU-TRU/DC-S22/`,
  không xóa. Bỏ đúng kiểm so băm mẫu tạm; giữ băm bốn schema chung và
  mọi ca/tham số hành vi cũ. Test dùng ngăn/cấu hình CoreGia 2.2.0,
  `dat_cau_hinh/gay_xung_dot_ngan/xem_ngan`; helper chỉ giao việc DEMO
  qua SDK để sửa ngăn, không tự triển khai kho thay thế.
- DC-6 gắn `$comment`: `ma_diem/nhan/ly_do=metadata`,
  `trai/phai=trich_dan`, đúng profile DC-6 của AI-12. Không đổi schema
  loại chung/API, không cho metadata miễn hậu kiểm nguồn/sàn. Hai ca
  nạp handler Hỏi AI mới dùng cấu hình CoreGia thật và provider Local
  giả: phản hồi hợp lệ được nhận có căn cứ; nguồn đã nhận chưa trả giữ
  `CHUA_RO`. Đóng phần lỗi kỹ thuật C-DC-07 trong môi trường CoreGia.
- Lệch phạm vi cần thiết: chuyển đồng bộ bảy module đang gọi ngăn; chia
  nội bộ DC-S22a (chay/ho_so/so_chu/quy_tac + schema) và DC-S22b
  (chuan_bi_ai/hau_kiem_ai/lech_dau + SQL), mỗi nhóm tối đa năm tệp mã.
  Không thể để nửa đường chạy còn import cổng tạm. Một nhánh theo lệnh
  lead; lead commit/mở PR. Ngoài nội dung main đã đồng bộ, không sửa
  engine khác, `_chung/**`, tài liệu cổng hoặc mã Core/SDK.
- Test hiệu năng cũ `nhieu_cum` 500.000 ký tự vượt trần 2 giây trên máy
  này (2,1351 và 2,3119 giây). Giữ nguyên test/ngưỡng; thêm đệm phân tích
  cụm tiền hữu hạn (128 cụm), chỉ tồn tại trong một lượt quét, không lưu
  bền. Mỗi vị trí vẫn có bản giá trị/offset riêng. Đo lại ca đó 0,5992 giây;
  sáu ca hiệu năng cũ xanh, thêm ca không chia sẻ giá trị giữa vị trí.

### Kết quả kiểm DC-S22

Đã kiểm bằng Core giả (CoreGia). Môi trường có
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.7.1: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q --basetemp=.pytest-tmp
898 passed in 393.05s (0:06:33)
0 skipped; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

- Bộ cũ 881 ca giữ nguyên tình huống/tham số, thay đúng ca băm cổng tạm
  bằng kiểm đã lưu trữ; thêm 17 ca DC-S22, không skip hay bỏ ca hành vi.
  Hai ca Hỏi AI (thành công/CHUA_RO) nằm trong bộ đầy đủ; 0 Cloud.
- `sql/kiem_ke.json`: **31/31 tệp**, bytes/SHA thực khớp; mọi tệp văn bản
  trong gói chuẩn LF. SQL khai đủ bốn bảng, cột hệ thống/kiểu/unique khớp.
- Sau chốt README/CHANGELOG/NGUON, tái tạo kiểm kê và kiểm lại bộ 17 ca
  DC-S22, CLI DEMO và kiểm độc lập; không đổi runtime sau lượt 898 ca.
- Đối chiếu 120 tệp thêm/sửa/chuyển từ main `12ed8db`: nội dung ngoài
  engine khớp main (sau chuẩn CRLF→LF), không chỉnh riêng engine khác.
- `git diff --check -- e_doi_chieu`: mã 0; chưa commit/push.

### Cần Core — cập nhật DC-S22

- C-DC-01: **đã có** ngăn/cấu hình SDK 2.2.0; không còn RAM fallback.
  Chưa nghiệm thu Core thật/migration CSDL thực tế. Ba màn dự kiến
  DC-10/DC-11 chưa có tệp UI, SDK 2.2.0 chưa nhận khóa
  `giao_dien_quan_tri` trong manifest; cần cửa nạp màn chung ở Core.
- SDK 2.2.0 chưa có kiểu cột `json`: tạm dùng cột `van_ban` tuần tự hóa
  phong bì ≤64 KiB. Không nới SDK hoặc đưa SQL vào runtime.
- CLI SDK chưa đọc cấu hình riêng từng ví dụ `chay_thu_demo`; DEMO Word
  hiện tại không cần cấu hình nên CLI chuẩn đạt toàn bộ, không có cổng
  DEMO thay thế. Nếu thêm DEMO nghiệp vụ cần cấu hình/quyền tệp con thì
  Core/SDK cần cách cấp tương ứng; không tự đặt cấu hình DEMO mặc định.
- C-DC-02/03/04/05 tiếp tục mở: quyền/vòng đời tệp con, provenance và
  điều phối OCR vùng/nhánh bỏ AI; xác nhận chỉ-thêm có danh tính/quyền;
  mapping chặn hiệu lực; từ điển/DC-Q14, ngưỡng/DC-Q15 và detector/model
  thật có nguồn/giấy phép/số đo. CoreGia không chứng minh các cửa này.
- C-DC-06: giữ giới hạn tệp chung của SDK; engine tự kiểm JSON yêu cầu
  ≤1 MiB và tệp con ≤20 MiB/tổng ≤128 MiB. SDK đã đổi lỗi HTTP 413 khi
  mở tệp thành `VUOT_GIOI_HAN`; engine đổi lại `DC_QUA_GIOI_HAN` để giữ
  hành vi. Chưa coi test là nghiệm thu lease/log/Core thật.
- Chưa phát sinh câu hỏi mới cần Anh chốt.

## DC-7 — 15/11/2026

**Kết luận: Đạt phạm vi DC-7 kiểm CoreGia; chưa nghiệm thu nguồn thật.
PR: chờ lead mở.** Thời gian **17:02–17:34 ngày 15/11/2026 (UTC+7),
khoảng 0,53 giờ**. Phiếu: **4 giờ ƯỚC TÍNH**.
Đã kiểm bằng Core giả (CoreGia), NganBoNho/adapter quyền và OCR vùng
DEMO; chưa kiểm Core thật/Linux/OCR/Local AI hoặc từ điển thật.

- Đúng ba tệp runtime: mới `lech_dau.py`, `tu_dien.py`; nối `chay.py`
  sau so DC-5 và hậu kiểm DC-6. Manifest chỉ tăng phiên bản `0.7.0`,
  không đổi capability/API/schema, mẫu NGAN-0 hoặc lõi DC-5/DC-6/DC-8.
  Không thêm dependency, sửa `ma-nguon/`, engine khác hay tài liệu cổng.
- Nhóm chỉ lệch dấu từ edit script có kiểm tái dựng. Tra token trọn vẹn
  quanh ký tự sửa, từ/âm tiết có nghĩa hoặc cặp vô nghĩa có chứng nhận
  cụ thể, ghim đúng mã/phiên bản/băm/nguồn/giấy phép. Vắng mục trong bộ
  hữu hạn là chưa biết, giữ Cần xem kể cả AI/OCR đồng ý. Thiếu bộ hoặc
  quyền khi cần → `DC_THIEU_TU_DIEN`; sai nguồn → `DC_SAI_NGUON`.
  **Nguồn thật DC-Q14 vẫn chưa có**, không có từ điển mặc định trong gói.
- Cặp có nghĩa chỉ thành nhiễu khi Local AI đã hậu kiểm đủ và OCR lại
  đọc đúng toàn cụm Word, khớp băm/phiên bản bản ký, mã điểm, trang, hộp,
  offset, hệ tọa độ, băm ảnh và nguồn/phiên bản. Hộp khối lớn không đủ
  chứng minh OCR từ. Manifest trong ngữ cảnh Core phải gắn capability
  `ocr.trich_vung@1` và kết quả nguồn; tệp/cờ caller tự khai không đủ.
  Nhiều nguồn cùng khớp mới chấp nhận; không chọn một kết quả thuận lợi.
- Thiếu/rỗng/khác OCR, mất tệp/quyền OCR lại, thiếu phiên bản hoặc AI
  chưa chắc giữ Cần xem. Cờ ABBYY chỉ phụ. Ảnh cắt nguồn cấp được kiểm
  quyền/byte/băm/pixel và giữ nếu có; không có thì null cùng ảnh trang.
  Engine không gọi OCR/Tesseract/Hot Folder/Local AI hoặc Cloud.
- Giữ nguyên mọi điểm/edit/nguyên văn, `muc_san` và nhật ký DC-5. Chỉ
  Python DC-7 có thể phân loại ứng viên tạm can_xem thành nhiễu, có
  validator tính lại từ bộ/tệp/manifest tin cậy; không tin boolean trong
  output. Vùng cứng và điểm AI đã nâng Nghiêm trọng không bị hạ. Lưu
  `ho_so_truoc_dc7` để DC-9 đọc lại gốc độc lập và dùng validator DC-7.
- Mẫu số: token OCR trên nguyên văn từng trang, tách khoảng trắng, bỏ
  dấu câu hai mép, giữ dấu câu bên trong (1.000.000 là một token), phải
  chứa chữ/số; không đếm trùng khối/dòng/từ. Tử số là token OCR phân biệt
  giao edit chỉ lệch dấu, gồm điểm cứng; nhiều edit trong token tính một.
  Lưu phân số và tỷ lệ; 0 từ → null/chưa kiểm. Thiếu ngưỡng không kết
  luận trang tốt, `so_trang_ocr_kem=null`. Ngưỡng mô phỏng trong bộ test
  chỉ DEMO; **DC-Q15 chưa có số đo/ngưỡng vận hành được duyệt**.
- Khi vượt ngưỡng ghim, đánh dấu OCR kém/ảnh trang, nhóm mã nhiễu và
  riêng toàn bộ mã Nghiêm trọng. Không xóa điểm khỏi snapshot. Chưa tổng
  hợp DC-9: `da_kiem_du=false`, `ket_luan=null`, `de_nghi_chan=true`.
- Ngan giữ/chốt/CAS từng bước; snapshot đầy đủ và tiền nhiệm chỉ ở
  kho Core, không cấu hình/sổ/đệm bền/tệp tạm trên engine. SDK chỉ nộp
  một kết quả; mất ACK/giao lại không tạo trùng từng bước. Snapshot cũ
  hết quyền được dựng lại từ nguồn còn quyền, không trả ref đã hỏng.
  Test DC-4/DC-6 cập nhật số snapshot do có bước DC-7 độc lập, giữ các
  kiểm CAS/chống trùng/hủy và một lần nộp kết quả.
- 85 ca DC-7: 24 tổ hợp sáu cặp có nghĩa/hai chiều/có-vắng OCR; hơp→hợp
  có chứng nhận DEMO; từ lạ không trong bộ; bên ký/tiền chữ; AI đồng ý
  nhưng OCR thiếu/sai/rỗng/khác nguồn/vùng/băm/phiên bản; OCR đồng ý
  nhưng AI chưa chắc; cả hai đồng ý; caller tự khai/cờ ABBYY; hai OCR
  mâu thuẫn; ảnh cắt; từ điển thiếu/sai/mất quyền; tỷ lệ từng trang,
  nhiều edit một token/0 token/biên ngưỡng; trang kém vẫn giữ điểm cứng;
  NFD/offset Unicode; chống trùng/ACK, hủy/giao lại, cấm mạng/ghi bền.

### Kết quả kiểm DC-7

Python **3.13.14**, `.venv` trong worktree dùng system-site-packages cho
pytest **9.1.1**/Pillow **12.3.0** đã có; SDK **2.0.0** cài offline
`--no-index --no-deps`. Engine chưa chuyển 2.2, giữ NGAN-0 nguyên bản
theo lệnh lead; không tự làm lát chuyển SDK. Wheel SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`. `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.

Kết quả cuối, **đã kiểm bằng Core giả (CoreGia)**:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.7.0: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
881 passed in 122.67s (0:02:02)
0 skipped; 85 ca DC-7; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

Quét riêng **500.000 ký tự**: chuỗi lặp tiếng Việt/tiền, **80.000 token,
0,1363 giây**; một token dài, **0,0911 giây**. Test `<2 giây` và hủy
giữa token dài đạt. Không suy thành tốc độ toàn tuyến/chất lượng OCR.
Git diff --check mã 0; gói không có `__pycache__`/`.pyc`.

Kiểm bàn giao: 6/6 băm nguồn hiện hành trong NGUON khớp LF; 2/2 bản
chép NGAN-0 giữ nguyên LF. Vẫn ở `codex/e_doi_chieu-dc-7`; không
commit/push, PR **chờ lead mở**.

### Cần Core / lead — cập nhật DC-7

- **C-DC-05 (còn thiếu):** contract OCR vùng SDK thật, nguồn/trang/hộp/
  cờ nghi ngờ và ảnh cắt. Đề nghị manifest Core ràng buộc ref+băm tới
  kết quả của `ocr.trich_vung@1`/bộ OCR thứ hai, có phiên bản nguồn và
  đúng bản ký/phiên bản/điểm/vùng. Core phải chứng thực producer/quyền,
  không chép trường caller thành ngữ cảnh tin cậy. Adapter ở tests chỉ
  mô phỏng hợp đồng; runtime vắng nó giữ Cần xem cho cặp có nghĩa.
- **C-DC-02:** Core điều phối OCR lại sau khi có mã điểm và chuyển kết
  quả/provenance tin cậy sang hậu kiểm, kể cả khi phát lại cùng phản hồi
  AI với bằng chứng mới. Cấp quyền tất cả tệp con/crop/snapshot xuyên
  bước/ACK/pháp nhân/module. Lượt OCR đã nhận nhưng chưa trả thuộc tầng
  OCR báo `ChuaRo`; DC-7 không tự gọi hoặc giả có kết quả nguồn.
- **L-DC-01 / DC-Q14 (còn thiếu):** lead trình bản từ điển sạch có giấy
  phép/phiên bản/băm/nguồn và chứng nhận cặp không đổi nghĩa. Fixture
  DEMO không thay nguồn này, không chứng nhận vốn từ/ngữ nghĩa tiếng
  Việt thật. Không phát sinh câu xin Anh duyệt lại.
- **DC-Q15:** cần đo DC-13 rồi duyệt ngưỡng OCR kém. Giữ null ở cấu hình;
  nhánh vượt ngưỡng chỉ kiểm bằng bộ DEMO ghim, không tự đặt mặc định.
- **C-DC-07 / Hỏi AI** vẫn mở: metadata phân loại còn bị handler AI-2
  coi là giá trị trích xuất. Các ca đồng ý AI/OCR của DC-7 dùng provider
  DEMO, không tuyên bố khép tích hợp Hỏi AI/Local AI thật.
- **DC-9:** dùng validator DC-7 với gốc đọc độc lập từ Core/chỉ mục Ngan
  và nguồn OCR đã chứng thực. Validator DC-5 vẫn chặn mọi hạ sàn; không
  nới nó để tin cờ `ai_dat`/`ocr_lai_dat` hoặc chứng nhận trong output.
- Ngăn bền/cấu hình SDK 2.2, vòng đời tệp và chặn hiệu lực module còn
  theo C-DC-01/02/04; không đóng các nợ này bằng CoreGia/RAM. Không có
  Chờ Anh mới, không sửa Core/schema chung, không commit/push.

## DC-6 — 15/11/2026

**Kết luận: Đạt phạm vi DC-6 kiểm CoreGia; chưa khép tích hợp Hỏi AI
C-DC-07. PR: chờ lead mở.** Thời gian **16:20–16:58 ngày 15/11/2026
(UTC+7), khoảng 0,64 giờ**; phiếu ước tính **5 giờ**.
Đã kiểm bằng Core giả (CoreGia), NganBoNho và adapter
quyền/tệp con DEMO; chưa kiểm Core thật/Linux/OCR/model thật.

- Thêm `chuan_bi_ai.py`, `hau_kiem_ai.py`; đăng ký hai handler trong
  `chay.py`. Manifest SDK 2.0 phiên bản `0.6.0` thêm hai năng lực đúng
  phiếu; không thêm khóa SDK 2.1, sửa API/schema chung, mẫu NGAN-0,
  DC-5/DC-8, `ma-nguon/` hoặc engine khác. Hai test manifest cũ cập
  nhật danh sách năng lực; test DC-6 do Core giả điều phối.
- Prompt/module/mã/phiên bản bắt buộc nghiệp vụ từ `tham_so`, không
  mặc định; thiếu/rỗng → `THIEU_PROMPT`, thiếu cấu hình → `CHUA_CAU_HINH`.
  Module khớp ngữ cảnh Core, không là quyền do caller/model tự cấp.
  SDK 2.0 còn chặn mã lỗi trước handler khi `bat_buoc=true`, nên manifest
  ghi bắt buộc ở nhãn/mô tả và handler kiểm; nợ C-DC-06 giữ nguyên.
- Snapshot `cho_ai` trong kho Core giữ nguyên hồ sơ, yêu cầu/khuôn,
  ngữ cảnh nguyên văn có định danh trái/phải, bản đồ Unicode AI→nguồn,
  phạm vi tin cậy và tham chiếu bản DC-5. `chuyen_tiep.doi_chieu` chỉ mã
  cặp/phiên bản/tham chiếu/băm, ≤4 KiB trong DEMO kể cả 100 điểm; trần
  chung 64 KiB. Hỏi AI phải chép nguyên, model không tạo metadata này.
- Đọc lại bản ghim Ngan/tệp Core cùng snapshot DC-5 độc lập, kiểm bằng
  `kiem_bat_bien(out,goc)`. Đúng provider Local, cặp/nguồn/bộ/băm và
  prompt/phiên bản, đủ mã điểm, đúng khuôn chặt; model thêm quyền/nguồn/
  sàn/nguyên văn thay thế bị từ chối. Không ghép điểm theo vị trí mảng.
- Kiểm câu trích trong đúng block AI/đúng phía/đúng điểm, ánh xạ về
  nguyên văn và phủ vị trí lệch. Sai trích/offset, không chắc hoặc
  `khong_thay_can_cu` giữ Cần xem. Chỉ nâng Nghiêm trọng khi có căn cứ;
  điểm cứng và nhật ký Python giữ nguyên. Hình thức/nhiễu là đề nghị
  `ai.ket_qua[].cho_dc7`, chưa hạ sàn; chờ đủ bằng chứng DC-7.
- Trần 100 điểm/500.000 ký tự ngữ cảnh/32 KiB khuôn/64 KiB chuyển tiếp;
  quá → `DC_QUA_NGAN_SACH_AI`, không cắt hoặc chia nhiều lượt. Core giả
  kiểm nhánh không AI và từ chối gọi nhầm `DC_KHONG_CAN_AI`, không dựng
  `tra_loi_ai` giả cho trường hợp này. Lượt ngoài chưa trả thuộc Hỏi AI
  báo `ChuaRo`, không dùng nó cho thiếu cấu hình.
- Giữ/chốt lượt bằng Ngan `lay_hoac_tao`/CAS có pháp nhân từng lệnh.
  Cùng đầu vào giao lại dùng cùng tham chiếu; ACK tệp/kết quả/kết thúc
  SDK gửi lại cùng khóa, mỗi việc chỉ một bản `ket_qua`. Không sổ/kho/
  cấu hình/đệm bền ở engine; toàn văn tại Core/RAM, không tạo tệp tạm.
- Bộ DEMO gồm phản hồi đúng, giữ điểm Nghiêm trọng khi AI đề nghị hạ,
  nâng có căn cứ, thiếu/thừa/trùng mã, Cloud, sửa chuyển tiếp/băm/cặp/
  prompt/phiên bản, trích sai phía/offset/header/vị trí lặp, prompt
  injection, không chắc/không căn cứ, Unicode/emoji, thiếu phía nguồn,
  NaN/Infinity/surrogate, thiếu cấu hình, quyền/pháp nhân/module, tự băm
  lại sàn, đúng 100/vượt 101 điểm, biên 500.000 ký tự, ngân sách và CAS,
  hủy, mất ACK và giao lại không nộp trùng. Đếm provider **Cloud = 0**.
- Test thêm **handler Hỏi AI-2 hiện tại**, provider Local DEMO không mạng,
  Cloud bị cấm: giữ nguyên chuyển tiếp và băm toàn phong bì; `ChuaRo`
  đúng tầng sở hữu lượt. Phát hiện nợ kiểm metadata trong khuôn phân
  loại, ghi rõ bên dưới; không sửa engine Hỏi AI hoặc lách dẫn chứng.

### Kết quả kiểm DC-6

Đã chạy đủ ba lệnh bằng `.venv/Scripts/python`, Python 3.13.14,
SDK 2.0.0 cài offline, SHA wheel khớp `SHA256SUMS.txt`, pytest 9.1.1,
Pillow 12.3.0 theo lock đã có. `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.

Kết quả cuối, **đã kiểm bằng Core giả (CoreGia)**:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.6.0: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
796 passed in 58.04s
0 skipped; 88 ca DC-6; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

Không commit/push. Không lệch số tệp runtime (đúng ba tệp); cách kiểm
bắt buộc prompt ở handler là lớp bọc cho hạn chế SDK 2.0, đã nêu ở
C-DC-06. Không phát sinh Chờ Anh. Băm LF hiện hành tại NGUON.md.

Lượt tổng trước nghiệm thu cuối: **794 passed, 1 failed**; ca hiệu năng
DC-5 `nhieu_cum` đo **2,2455 giây**, vượt ngưỡng 2 giây. Không sửa bộ quét
hoặc ngưỡng. Chạy riêng lại cả sáu ca hiệu năng đạt **6 passed in 13.92s**:
`nam` 0,1218; `mot_tram` 0,1501; `nhieu_cum` 1,0163;
`nhieu_cum_mot_dong` 0,1087; `so_thieu_don_vi` 1,1415;
`so_co_don_vi` 1,1693 giây. Có dao động thời gian trên máy dùng chung;
không suy các số này thành tốc độ toàn tuyến hoặc chất lượng OCR/AI.

### Cần Core / Hỏi AI — cập nhật DC-6

- **C-DC-02:** cấp `ngu_canh.module`/pháp nhân tin cậy, quyền tất cả tệp
  con/snapshot/ảnh và vòng đời xuyên chuẩn bị→Hỏi AI→hậu kiểm, cả lúc
  gửi lại/ACK. Core bảo đảm phản hồi thực sự do bước Hỏi AI Local tạo;
  chuỗi `nha_cung_cap=local` hay băm không tự chứng minh provenance.
  Adapter CoreGia chỉ là test. Thiếu quyền/module từ chối, không fallback.
- **C-DC-02 — nhánh không AI:** runner dùng bỏ qua bước hoặc chuỗi riêng
  khi không còn ứng viên. Đã kiểm lựa chọn nhánh bằng điều phối test;
  bước xuất DC-9 chưa được triển khai trong DC-6. Không tạo phản hồi AI
  hoặc kết luận cuối giả để làm chuỗi chạy qua.
- **C-DC-07 / lead Hỏi AI (mới):** `hoi_yeu_cau._kiem_tra_loi` của AI-2
  kiểm tất cả lá `du_lieu` như giá trị trích xuất, gồm mã điểm, nhãn,
  lý do và offset. Test handler hiện tại + provider DEMO trả khuôn đúng/
  câu trích đúng vẫn bị `DU_LIEU_NGOAI_TRICH_DAN`, `khong_thay_can_cu`.
  Cần cách phân biệt metadata điều khiển với bằng chứng trong profile
  Đối chiếu, giữ nguyên loại/schema/API chung và kiểm span độc lập.
  Không nhét nhãn/offset vào câu trích để qua kiểm. DC-6 hiện giữ Cần xem;
  chưa khép tích hợp phân loại có căn cứ qua handler Hỏi AI hiện tại.
- **C-DC-01/06:** cần ngăn bền/CAS và mã lỗi tham số do handler quyết
  định. RAM mất chỉ mục khi khởi động lại thì hồ sơ chưa chứng thực lại
  bị từ chối; không suy quyền từ tệp/băm còn tồn tại. Nợ SDK log/lease/
  trần đọc tệp giữ theo mục chung. Chưa phát sinh câu Chờ Anh.
- **C-DC-05 / DC-7:** từ điển và OCR lại đúng vùng/nguồn còn là điều kiện
  quyết định nhiễu/hình thức. DC-6 không đóng nợ này hoặc hạ điểm cứng.

## DC-5 — 15/11/2026

### Sửa theo kiểm độc lập lead

**Kết luận: Đạt ba điểm sửa được giao; PR: chờ lead mở.** Đã kiểm bằng
Core giả (CoreGia), chỉ DEMO, 0 Cloud, không commit/push.

- Chỉ sửa `quy_tac.py`, `tien_chu.py`, `tests/test_dc5.py` cùng ba tài
  liệu VIEC/CHANGELOG/NGUON. Giữ `_chung/**`, `ngan.py`, `cau_hinh.py`,
  API/schema/manifest và các phần DC-3/4/8.
- Bỏ `.*` giữa từ chỉ số và đơn vị, thay bằng một lần quét token, kiểm
  hủy mỗi 256 token. Rà regex cả hai tệp và đổi hai mẫu số kèm đơn vị
  sang quét số một lần rồi kiểm đơn vị tại cuối số. Không còn `.*`/`.+`;
  regex số có phân cách trong `doc_so` đã chặn đầu vào 200 ký tự, các
  nhóm còn lại không có hậu tố bắt buộc khiến quét lại dãy số.
- Thêm kiểm hủy khi lập chỉ mục từ, quét số/nhãn/đơn vị/phủ định/ngày.
  Giới hạn toàn cụm tiền chữ 64 từ; không cắt ngầm, vượt giữ nguyên văn,
  `can_xem`, `khop=null` và lý do nêu giới hạn.
- Parser hỗ trợ một nghìn tỷ, một nghìn hai trăm tỷ, hai nghìn linh/lẻ
  năm, hai mươi năm, mười năm, một trăm năm; một cấp tỷ, số nguyên dưới
  10^15. Thiếu/lặp/đảo cấp hoặc cách đọc chưa chắc vẫn cần xem.
- Chỉ ghép ngoặc không nhãn khi ngay sau một số tiền duy nhất cùng
  dòng/ô và không có đuôi mơ hồ/ngoặc lồng. Chữ đọc được trái số/tiền tệ
  → Nghiêm trọng; không đọc được → Cần xem. Offset giữ đúng nguyên văn.
- Nâng thuật toán `DC-5-1 → DC-5-2` trong khóa/băm hiện có, tránh tái
  dùng snapshot có kết quả phân tích cũ; không đổi cổng API.

Thêm 49 ca (tổng 222 ca DC-5): ngữ pháp/cặp tiền mới, ngoặc đúng/lệch/
không đọc được/mơ hồ/khác dòng ô, trần 64 từ, hiệu năng và hủy giữa chừng.
Test hiệu năng chạy trong tiến trình con với timeout 10 giây để test
hồi quy không treo cả pytest. Số đo thực trên bộ quét tiền, adapter offset
đồng nhất DEMO (không bao gồm chuẩn hóa/đối chiếu toàn tuyến Core/OCR):

| Đầu vào | Ký tự | Giây |
|---|---:|---:|
| `"năm " * 100000`, không đơn vị | 400.000 | 0,0640 |
| `"một trăm " * 50000`, không đơn vị | 450.000 | 0,0690 |
| Nhiều cặp tiền hợp lệ, mỗi cặp một dòng | 500.000 | 0,4418 |
| Nhiều cụm tiền trên cùng một dòng, giữ mơ hồ | 500.000 | 0,0482 |
| Dãy `1.1.1…` thiếu đơn vị | 500.000 | 0,4450 |
| Dãy số dài có đơn vị | 499.999 | 0,4591 |

Hai dòng cuối lấy thời gian lớn hơn giữa bộ quét tiền nội bộ và bộ quét
đặc trưng. Tất cả dưới 2 giây; không suy thành tốc độ toàn tuyến hoặc
chất lượng nhận dạng. Các test hủy giữa quét token, số và lập chỉ mục
đạt; ngữ cảnh thật vẫn nhận `viec.kiem_huy` qua lớp bọc hiện có.

Kết quả thật bằng `.venv/Scripts/python`, Python 3.13.14, pytest 9.1.1,
SDK 2.0.0 offline (SHA wheel khớp `SHA256SUMS.txt`), có
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
.venv/Scripts/python -m pytest e_doi_chieu/tests -q --basetemp=.pytest-tmp
629 passed in 32.33s
0 skipped; mã thoát 0.

.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

Thời gian sửa thực tế: **16:04–16:17 ngày 15/11/2026 (UTC+7), khoảng
0,22 giờ**; phiếu DC-5 ước tính **5 giờ**,
không có dự toán riêng cho lượt sửa. SHA-256 chuẩn LF hiện hành ở NGUON.
Không lệch phạm vi; **không phát sinh Cần Core/Chờ Anh mới**. Các C-DC
hiện có tiếp tục mở, chưa kiểm Linux/Core thật/OCR/model thật.

### Bản bàn giao trước kiểm độc lập (lịch sử)

**Kết luận: Đạt phạm vi DC-5; PR: chờ lead mở.** Đã kiểm bằng Core giả
(CoreGia), NganBoNho và adapter tệp con/ảnh/phân trang DEMO kế thừa DC-3/4.
Chưa kiểm Core thật/Linux/OCR/model thật; **0 Cloud, 0 OCR/AI thật**.

Đã làm:

- Đúng ba tệp runtime `quy_tac.py`, `tien_chu.py`, `chay.py`; khối nối
  DC-5 riêng trong `chay.py`, giữ API/năng lực và schema/manifest hiện có.
  Không sửa `so_chu.py`, `can_chinh.py`, `sua_tay.py`/`anh.py`, mã Core,
  `ma-nguon/`, mẫu NGAN-0 hoặc `_chung/docs/LOAI-DU-LIEU-RIENG.md`.
- Dùng kiểm nguồn/băm/quyền/căn/so DC-4, `da_nhan → da_so`. Mọi điểm có
  sàn Python/quy tắc/căn cứ. Chữ số, ngày/thời hạn, tiền/chữ/tiền tệ/tỷ
  lệ, định danh, phủ định/bắt buộc, cấu trúc và nghi nhầm OCR được bảo vệ.
  Các lát chữ/ngắt dòng liên quan Điều/Khoản thiếu/thừa/đảo cùng lên
  Nghiêm trọng, không chỉ điểm cấu trúc tổng hợp.
- Quét toàn văn hai bên, cả phần chuẩn hóa đã loại khỏi so; nhãn Python
  Việt/Anh + vùng bộ/metadata có băm/offset/nguyên văn đúng nguồn, không
  dựa vào AI. Nhãn tự động không tự chứng nhận đã nhận diện đủ mọi bên.
  Kiểm lại lát tương đương chuẩn hóa trên bản chỉ NFC: gạch/nháy/khoảng
  trắng không được che khác biệt mã/số/vùng bảo vệ. Không mất nguyên văn.
- Phân cách chỉ theo bộ đã ghim; giữ chuỗi số 0 đầu, báo 0/O, 1/l, 5/S,
  8/B. Decimal/int; không float hoặc đoán tiền tệ. Tiền `{so, tien_te}`,
  phần lẻ JSON dùng chuỗi thập phân chính xác; ngày đã đọc về ISO.
- Kiểm tiền số ↔ chữ ngay trong bản ký, kể cả khi Word giống hệt. Chỉ
  ghép một cặp cùng dòng/ô với đủ đơn vị và ngữ pháp; chênh đã phân tích
  được giữ Nghiêm trọng, cả nguyên văn/offset/giá trị/căn cứ. Thiếu, nhiều
  cụm, mơ hồ phân cách/tiền tệ, chưa hiểu chữ hoặc ngôn ngữ giữ Cần xem,
  `khop=null` và hạng mục `da_kiem_du=false`; không ghép qua dòng/ô.
- Ghim nhật ký/băm sàn và quy tắc. Cửa thuần cho DC-6 kiểm với snapshot
  gốc đọc lại từ Core; chặn tự băm lại, thay căn cứ/xóa điểm/hạ mức. Áp
  lại không reset mức đã nâng. Chưa thực hiện hậu kiểm trích dẫn/Local
  DC-6/DC-7; không coi cửa thuần là đã tích hợp AI.
- Chỉ snapshot/tệp Core và chỉ mục qua Ngan; không tệp tạm/cấu hình/sổ/
  đệm bền. Giữ CAS/chủ lượt/hạn chiếm/chống trùng/phục hồi/hủy DC-4, khóa
  thêm `DC-5-1` để không tái dùng kết quả chưa có quy tắc. Trần điểm và
  bytes tính cả lịch sử/bằng chứng, kiểm dần trước khi nhân dữ liệu vào
  điểm; vượt từ chối, không cắt. Vùng dài giữ offset/băm tới nguyên văn.

Ma trận DEMO và giới hạn:

- `tests/test_dc5.py`: 29/29 cặp cài thay đổi Nghiêm trọng được bắt; mỗi
  cặp có ca giữ nguyên tương ứng (29/29 không phát sinh Nghiêm trọng).
  Bao gồm 1.000.000 VND ↔ 1.100.000 VND, VND/USD, 2026-10-30, MST 0 đầu,
  không/chưa/phải/chỉ/trừ/ngoại trừ/được/có thể, thuê/thuế trong tên bên
  ký, định danh còn lại, Điều thiếu/thừa/đảo và bốn cặp nghi nhầm OCR.
- 4/4 ca tiền chữ trái số/tiền tệ trong bản ký giống Word bị bắt; 8/8 ca
  tiền số/chữ khớp được phân tích đúng. Thêm phân cách mơ hồ/không khai,
  cụm thiếu/sai/ngôn ngữ khác, tiền lẻ/số lớn, cấm ghép qua dòng/ô,
  metadata giả/thiếu, NFC/NFD, chuẩn hóa che mã, nhật ký/AI giả, không
  ghi đĩa/gọi mạng/log nội dung, hủy và trần. Tổng 173 ca DC-5.
- Chỉ xác nhận bộ DEMO này; không suy thành tỷ lệ phát hiện thực tế.
  Parser tiền chữ hữu hạn tiếng Việt số nguyên dưới 10^12. Phần ngoài
  ngữ pháp/tiền lẻ bằng chữ, ngày/thời hạn bằng lời chưa phân tích đủ và
  vùng chưa có metadata giữ chưa kiểm đủ. Bộ thật/nhận diện đủ cần lead/
  module cấp; DC-5 không tự chọn mặc định nới lỏng.
- `ket_luan=null`, `da_kiem_du=false`, `de_nghi_chan=true` toàn lượt;
  số Nghiêm trọng đã biết vẫn giữ dù các hạng mục khác chưa kiểm. Không
  mở hiệu lực. Mức Cần xem chưa đủ căn cứ không được AI tự hạ thành nhiễu.

Kết quả thật bằng `.venv/Scripts/python`, Python **3.13.14**, pytest
**9.1.1** có sẵn qua system-site-packages. SDK **2.0.0** cài offline
`--no-index --no-deps`; wheel SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`. Có `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:
## DC-8 — 15/11/2026

**Kết luận: Đạt phạm vi khảo sát/bản đầu; detector chưa đạt để vận hành độc
lập. PR: chờ lead mở.** Đã kiểm bằng Core giả (CoreGia), với adapter quyền
tệp/metadata ảnh và ngăn RAM; không phải kiểm Core thật hoặc đo chất lượng
OCR/model/scan thật. Nghiên cứu và dự toán ở [DC-8-KHAO-SAT.md](DC-8-KHAO-SAT.md),
số đo thật từ thuật toán trên DEMO ở [DC-8-SO-DO-DEMO.json](DC-8-SO-DO-DEMO.json).

- Đúng ba tệp runtime dự kiến: `sua_tay.py`, `anh.py`, `chay.py`. Thêm
  công cụ đo ngoài gói và `.cmd` ASCII theo Q13; tổng bốn tệp mã ngoài test.
  Manifest SDK 2.0 thêm năng lực, phiên bản 0.4.8 chưa phát hành; lead thống
  nhất phiên bản khi gộp DC-5 song song. Không sửa `quy_tac.py`, `tien_chu.py`,
  API/SDK/Core, schema chung, mẫu NGAN-0 hoặc `ma-nguon/`; không commit/push.
- Nhận hồ sơ sau DC-3 hoặc sau so văn bản, giữ mọi điểm/sàn/bằng chứng đã
  có; kiểm snapshot/phong bì, đọc lại nguồn/bộ/text và quyền tệp con. Ảnh
  phải đủ từng trang, băm/bytes/giải mã/pixel và phép xoay/tỷ lệ đúng nguồn.
  Không tin vùng tự khai từ caller để chứng minh đã quét toàn trang.
- Detector pixel và ngưỡng DEMO có phiên bản/băm; quét mọi dòng pixel,
  không dùng sắc mực làm nhãn. Vùng ký/dấu/nháy chỉ loại khi có căn cứ Core
  đúng ảnh và không chồng nội dung. Chưa rõ/chồng chữ vẫn có ảnh để xem;
  nguồn `metadata_can_xem` tách khỏi `detector_pixel`, không cộng vào TP.
- Ảnh cắt có lề ngữ cảnh, hộp nguồn/hộp nét pixel/hộp cắt thực, băm và
  tham chiếu kho Core; `chu_tay=null`, sàn Nghiêm trọng và cần xác nhận.
  Quét xong mọi trang trước tải crop. Không tệp tạm hoặc đệm đĩa; ảnh RAM
  đóng bằng context manager khi lỗi/hủy. Phần tệp Core mồ côi cần vòng đời
  C-DC-02, không tự xóa nhật ký hoặc dùng sổ máy.
- Snapshot `da_quet_anh` ghi trang/phạm vi/số pixel/phương pháp/phiên bản,
  cấu hình/ngưỡng/metadata đã băm. Do chưa đủ recall, **luôn** giữ
  `kiem_tra.sua_tay=chua_kiem`, `da_kiem_du=false`, `ket_luan=null`,
  `de_nghi_chan=true`; `[]` sau quét không có nghĩa không sửa tay.
- Thiếu ảnh/phép đổi/quyền ảnh/hỏng ảnh → `DC_THIEU_ANH`; thiếu phương
  pháp/phiên bản/hộp từ/kiểm toàn trang → `DC_CHUA_CO_BO_PHAT_HIEN`;
  vượt trần → `DC_QUA_GIOI_HAN`. Không log ngoại lệ/nội dung/đường máy.
  Trần 60 trang, 20 triệu pixel, 20 MiB/ảnh, 128 MiB đầu vào/việc,
  10.000 vùng, 900 giây và các trần thuật toán tại khảo sát; không cắt ngầm.

### Kết quả kiểm DC-8

Venv `.venv` trong đúng worktree/nhánh `codex/e_doi_chieu-dc-8`, Python
3.13.14, SDK 2.0.0 cài offline từ wheel repo; SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp SHA256SUMS.txt. Pytest 9.1.1 và Pillow 12.3.0 có sẵn qua venv
system-site-packages; không mạng. Có `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.
Lock engine chỉ chép Pillow và hai hash Windows/Linux từ lock OCR; chưa
có wheel Pillow trong repo để kiểm cài máy sạch, không tuyên bố đã kiểm.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
580 passed in 30.62s
0 skipped; mã thoát 0.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

DEMO `thu` trực tiếp chỉ là Word (DC-2); 173 ca DC-5 chạy qua CoreGia trong
pytest với tệp/ngăn/metadata DEMO. Không thêm ID giả hay nhánh DEMO vào
runtime để làm ví dụ `thu` có hồ sơ cặp. Các test hash schema/mẫu NGAN-0,
quyền/băm/CAS/lease/chống trùng/hủy DC-0…4 vẫn đạt. Một số assertion DC-4
cập nhật theo hành vi DC-5: có sàn thực, điểm cần xem khi thiếu chữ, và
không ẩn khác biệt số chưa có quy ước; vẫn kiểm tái dựng đầy đủ hai bản.

Lệch khỏi phiếu / quy ước triển khai: không mở thêm phạm vi/tệp runtime.
Phần `quy_tac_cung` là quy ước nội bộ trong bộ opaque đã ghim, tài liệu
README mô tả đầy đủ; không đổi schema/API chung. Coordinator dùng lại
lõi DC-4, giữ vòng CAS tại DC-5 để không sửa tệp DC-4 hoặc tạo snapshot
trung gian. Tiền lẻ JSON giữ chuỗi chính xác vì không dùng float.

Thời gian thực tế: **15:09–15:55 ngày 15/11/2026 (UTC+7), khoảng 0,77 giờ**;
phiếu **5 giờ ƯỚC TÍNH**. Không commit/push; lead commit và mở PR.

### Cần Core — cập nhật DC-5

- Không phát sinh yêu cầu đổi API/SDK/schema hoặc câu Chờ Anh mới.
  C-DC-01/02/05/06 tiếp tục mở: ngăn bền, quyền/vòng đời tệp con và
  provenance OCR/ảnh/phân trang, nợ log/lease/trần SDK; CoreGia/RAM không
  chứng nhận các cổng thật. Chưa kiểm Linux, Core thật hoặc model thật.
- Lead/module cần cấp bộ thật đã duyệt cùng vùng bảo vệ đủ căn cứ của
  cả hai nguồn. Chưa có giữ hạng mục chưa đủ kiểm. DC-6 phải đọc lại
  snapshot tin cậy từ Core để kiểm bất biến, không nhận bản gốc/nhật ký
  do model gửi; DC-7 vẫn cần đủ bằng chứng OCR trước xử lý nhiễu.
- Chặn/mở hiệu lực vẫn thuộc module qua C-DC-04; DC-5 chỉ trả cờ bảo thủ,
  không tự mở hiệu lực hoặc ghi xác nhận. Không tuyên bố đã đo tỷ lệ
  OCR/detector trên máy thật; DC-Q13 và DC-13 giữ kế hoạch lead đã giao.
Engine e_doi_chieu 0.4.8: mọi ví dụ chạy thử DEMO đều đạt.
1/1 ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
486 passed in 24.24s
0 skipped; mã thoát 0. Nền DC-0…4: 407; DC-8 mới: 79.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0; không import Core/kênh cũ, pycache/pyc/symlink trong gói.
```

SDK DEMO hiện là Word; kiểm giao thức DC-8 trong pytest với CoreGia và
detector giả **tách riêng** thuật toán pixel thật trên ảnh DEMO có đáp án.
Bao gồm gạch/chèn/nét sát chữ, chữ ký/dấu/nháy, chồng chữ và thiếu căn cứ,
chữ in màu/nét xa chữ/trang không vết, 12 tổ hợp tỷ lệ/xoay, biên làm tròn
pixel, hai trang/thiếu trang, sai băm/size/quyền/metadata, thiếu detector/
hộp từ, detector lỗi/không quét đủ, PNG/JPEG hỏng/EXIF, ảnh quá lớn,
timeout/hủy trong pixel/cắt/tải, giữ điểm lệch cũ, không ghi đĩa/mạng và
không lộ nội dung lỗi. Hai mẫu NGAN-0 và bốn schema so băm LF vẫn đạt.

`cong-cu/DO-SUA-TAY-DEMO.cmd` đã chạy **khô**, mã 0; không gọi AI. Số đo
thật tách mock, từ `--do-demo`: **12 ca/11 raster, 6 vùng có đáp án,
TP=3/FP=0/FN=3**, IoU ghép một-một ≥0,3; recall 50%, precision 100% chỉ
trên 3 dự đoán, 0 lệch giả/12 ca. Bỏ sót nét mờ, nét trong chữ và ký chồng
chữ; runtime giữ ký chồng để xem qua metadata không biến FN thành TP.
Thời gian có tracemalloc **0,152430 giây**; đỉnh Python **297.204 bytes**;
RAM tiến trình/native/VRAM **null/chưa đo**. Local vision/model/tất cả
chỉ số **null/chưa đo**. Không suy ra accuracy hoặc hiệu năng hồ sơ thật.

**Thời gian thực tế:** bắt đầu 15/11/2026 **15:09:00**, chốt ba lệnh kiểm
và báo cáo **15:42:04** (UTC+7), khoảng **0,55 giờ**; phiếu **7 giờ ƯỚC TÍNH**.
Không thay 7 giờ bằng cam kết tỷ lệ phát hiện; số đo toy DEMO không thay DC-13.

**Lệch/phương án tạm:** detector chỉ tạo ứng viên thử nghiệm, chưa đủ để
ghi sửa tay đã kiểm đạt. Local vision chưa được cấp, chỉ có công cụ chấm
file export và chạy khô, không bịa phép đo. Metadata ảnh Core là quy ước
adapter tạm cần review, không đổi API/SDK. Không cần bảng ngăn mới: cấu
hình qua Ngan, mọi snapshot/ảnh qua kho Core. Phiên bản/lock/README và
test manifest cũ được cập nhật để đăng ký năng lực; chưa tích hợp DC-5.

### Cần Core — cập nhật DC-8

- **C-DC-02/05:** Core cấp quyền ảnh/text/nguồn/snapshot xuyên bước và
  metadata `doi_chieu_anh` tin cậy gắn đúng snapshot/PDF/trang/băm ảnh,
  toàn trang/gốc tọa độ/tỷ lệ/xoay. Nguồn loại trừ ký/dấu cần căn cứ được
  xác nhận; danh sách caller không đủ. Quy ước cụ thể tại khảo sát §3.
- **C-DC-02:** vòng đời/thu hồi ảnh đã tải nếu hủy/lỗi trước nộp snapshot,
  cấp lại quyền tệp con ở việc sau; CoreGia không chứng minh ACL/RLS thật.
- **C-DC-04:** tổng hợp/module giữ chặn khi `sua_tay=chua_kiem` dù số vùng
  bằng 0, và giữ riêng các vùng phải xác nhận theo Q04. Chưa kiểm hiệu lực thật.
- **C-DC-05/L-DC-01:** nguồn DEMO scan có đáp án, render/căn chỉnh và/hoặc
  model Local được phép dùng, phiên bản/hash/giấy phép/RAM/VRAM; Core điều
  phối vision, engine không gọi trực tiếp. Model chưa cấp thì chọn vision
  trả `DC_CHUA_CO_BO_PHAT_HIEN`.
- C-DC-01/06 giữ nợ ngăn bền/log SDK/trần sâu/lease chung, không vá SDK/Core.

**Việc tiếp / dự toán bổ sung, chưa được giao:** bộ DEMO scan/đáp án
**4–6 giờ ước tính**; sau đó nhánh ảnh render+căn chỉnh **8–12 giờ ước tính**
hoặc nhánh so Local vision qua Core **6–10 giờ ước tính**, phụ thuộc nguồn/
máy/giấy phép. Không tự thêm dependency/model hoặc giảm tiêu chí DC-13.
Không phát sinh câu xin lại Q04/Q07/Q08; cần lead/Anh xác nhận nguồn model
theo Q13 khi thực hiện nhánh đó. Chi tiết so sánh/rủi ro ở khảo sát §1, §6.

## DC-4 — 15/11/2026

**Kết luận: Đạt phạm vi DC-4; PR: chờ lead mở.** Đã kiểm bằng Core giả
(CoreGia), NganBoNho và adapter tệp con/phân trang DEMO chỉ ở tests.
Chưa kiểm Core thật/Linux hoặc chất lượng OCR/render. Không kết luận sạch
từ bước so; quy tắc cứng/phân loại/sửa tay còn thuộc các lát sau.

- Đúng ba tệp runtime: `can_chinh.py`, `so_chu.py`, `chay.py`; manifest
  SDK 2.0 phiên bản 0.4.0, thêm `doi_chieu.so_van_ban@1`. Không sửa DC-3,
  `ma-nguon/`, API/SDK/Core, schema chung hoặc hai bản chép NGAN-0.
- Hồ sơ `da_nhan → da_so`; kiểm sâu băm/quyền mọi nguồn và snapshot/bộ,
  tái tính chuẩn hóa để không dùng map/văn bản bị sửa. Bộ ở tham số phải
  khớp nguyên bytes đã ghim. Snapshot mới có tham chiếu+băm tiền nhiệm.
- Căn Điều → Khoản → câu, bảng → dòng → ô (cả bảng lồng/rỗng/gộp); neo
  từng lần xuất hiện + LIS, so ký tự trong cụm nhỏ, giữ trọn cụm chưa có
  neo. Không bỏ đuôi/đoạn lặp. Không căn được trả đúng mã/câu
  `DC_KHONG_CAN_DUOC`. Nhãn NFD vẫn căn; số tiền đầu dòng không là Khoản.
- Script phủ liên tục, kiểm tái dựng cả nguyên văn lẫn chuẩn hóa hai bên;
  giữ mọi ký tự bị chuẩn hóa trong lát nguồn, không tách cụm NFC co/giãn
  dùng chung nguồn. Điểm có mã băm ổn định, hai lát Unicode nửa mở/vị trí
  thực hoặc null, phép/căn cứ. Bỏ dấu chỉ gắn `chi_lech_dau`; thuê/thuế,
  các cặp đổi nghĩa và toàn bộ ma trận giữ khác biệt DC-3 vẫn còn điểm.
- Kiểm thiếu/thừa/đảo Điều/Khoản, cả Khoản trong Điều bị đảo; hình dạng
  bảng/ô cũng giữ điểm khi chữ không đổi. Trang chưa có bằng chứng giữ
  `chua_kiem`; đổi dàn trang/số trang khác không tự coi thiếu trang.
- Ứng viên `cho_phan_loai=true`, mức/sàn chưa đặt; số điểm đã biết, các số
  mức chưa phân loại null. `quy_tac_cung/lech_dau/sua_tay/phan_loai_ai`
  còn chưa kiểm; `da_kiem_du=false`, `ket_luan=null`, `de_nghi_chan=true`.
- Trần ký tự/điểm/bytes/snapshot/300 giây và mức thấp hơn của cấu hình;
  gọi hủy theo cụm, tiến độ không nội dung; vượt `DC_QUA_GIOI_HAN`, không
  tải danh sách cắt. 10.000 điểm lõi giữ đủ; 10.001 điểm từ chối.
- Snapshot/tệp chỉ tải Core; chỉ mục/lượt riêng bước so qua Ngan, không
  ghi đĩa bền, Cloud hay gọi engine khác. CAS/chủ lượt/hạn chiếm, tranh
  lượt, phục hồi tệp hết quyền, hủy và mất xác nhận không chốt trùng hoặc
  đè chủ mới. Tái dùng kiểm lại quyền và tái dựng.

### Kết quả kiểm DC-4

Venv tại worktree, Python **3.13.14**, pytest **9.1.1** có sẵn qua
system-site-packages. SDK **2.0.0** cài wheel nội bộ bằng
`--no-index --no-deps`; SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp SHA256SUMS.txt. Có `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
1/1 DEMO ĐẠT; mã thoát 0.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
407 passed in 29.67s
0 skipped; mã thoát 0. Nền DC-0…3: 297; DC-4 mới: 110.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0; không import Core/kênh cũ, không pycache/pyc/symlink trong gói.
```

Đường nhận cặp/so cần cấu hình và quyền tệp con nên nằm trong pytest
CoreGia; không thêm DEMO thành công giả vào manifest. Bao gồm cặp giống,
khoản/Điều chèn/xóa/đảo, lặp, đuôi, bảng rỗng/gộp/lồng, ngắt dòng, Unicode
co/giãn, 60 cặp ngẫu nhiên có seed cố định, thiếu/sai bằng chứng trang,
trang PDF/ảnh DEMO đảo thực về thứ tự tham chiếu, quyền/CAS/hủy/giới hạn,
log an toàn và không đọc đĩa/mạng/engine khác. Phép kiểm thời hạn dùng
đồng hồ giả; không giữ máy chờ 300 giây.

Đo riêng sau lần sửa cuối (thư viện chuẩn, dữ liệu DEMO, chỉ **lõi so**):
**450.000 ký tự lặp: 1,1848 giây; 500 bảng: 0,1856 giây**; mỗi ca dưới
5 giây. Không phải số đo toàn tuyến/render/OCR, không suy ra accuracy thật.
`git diff --check` mã 0 sau cập nhật tài liệu; bản chép schema/mẫu so băm
LF nằm trong bộ pytest. SHA-256 runtime hiện hành ở NGUON.md.

**Thời gian thực tế:** 14:19:00–14:59:10 ngày 15/11/2026 (UTC+7), khoảng
**0,67 giờ**, so với **4 giờ ƯỚC TÍNH** trong phiếu. Thời điểm chốt kết
quả kiểm và báo cáo; không commit/push, lead mở PR.

**Lệch/phương án bảo thủ:** chỉ ba tệp runtime như phiếu; manifest/test/
README/NGUON/VIEC/CHANGELOG là metadata/tài liệu. Cụm lớn không có neo
giữ nguyên cả cụm thành phép thay; không cam kết script tối thiểu.
Quy ước liên kết phân trang Core dưới đây là lớp bọc tạm C-DC-05, chưa
phải cửa Core đã có. Chỉ kiểm thứ tự vật lý khi ghép được toàn bộ ảnh
trùng băm; chưa có ánh xạ nội dung đáng tin thì không kết luận thiếu/thừa
trang từ số trang. Điểm trang giữ ảnh/số trang, lát chữ chưa ánh xạ là null.

### Cần Core — cập nhật DC-4

- **C-DC-05:** cần nguồn render đúng DOCX/font/phiên bản và liên kết
  DOCX → PDF render → ảnh; cung cấp qua ngữ cảnh Core tin cậy, không lấy
  tuyên bố của caller làm bằng chứng. Lớp bọc đề nghị dùng
  `viec.ngu_canh.doi_chieu_phan_trang` gồm `phien_ban=1`,
  `bam_word/phien_ban_word/bam_pdf_chuan/bam_ban_ky/anh_word/anh_ban_ky`
  (hai mảng băm ảnh theo thứ tự), ≤16 KiB. Kiểm đúng nguồn ghim;
  thiếu → chưa kiểm, sai → `DC_SAI_NGUON`. Không sửa API/manifest 2.0
  hoặc schema chung để ép Core hỗ trợ. Test chỉ gắn bởi adapter CoreGia.
  Cần Core/lead thống nhất cửa này trước tích hợp thật; hiện mặc định thiếu.
- Khi đủ liên kết và ảnh trùng băm: kiểm được thứ tự; ảnh scan khác pixel/
  khác dàn trang vẫn cần ánh xạ nội dung trang đáng tin để kiểm thiếu/thừa/
  đảo đầy đủ. Không coi parser PDF tối thiểu của DC-3 hoặc byte ảnh như
  kết quả renderer/OCR đã kiểm thật.
- C-DC-01/02/03/04/06 giữ mở: ngăn bền, phạm vi/quyền/vòng đời tệp và
  snapshot xuyên bước, xác nhận/chặn hiệu lực, lease/log an toàn phía SDK.
  Ngăn RAM mất khi khởi động lại; chưa kiểm Core thật/Linux.
- **Không có câu Chờ Anh mới.** Chưa phát sinh mã cũ cần chuyển LUU-TRU.

## DC-3 — 15/11/2026

**Kết luận: Đạt phạm vi DC-3; PR: chờ lead mở.** Đã kiểm bằng Core giả
(CoreGia), NganBoNho và adapter tệp con DEMO chỉ trong tests. Chưa kiểm
Core thật/Linux, chất lượng OCR hoặc đối chiếu toàn tuyến; không kết luận
Khớp từ bước nhận cặp. Theo DC-Q16/DC-Q17 và quyết định chiều 15/11 đã duyệt.

### Sửa theo kiểm độc lập lead — kết quả hiện hành

- Sửa `ho_so.py`, `chuan_hoa.py`, `chay.py`; bổ sung schema cấu hình và
  bản khai ngăn dự kiến SDK 2.1 (tổng 5 tệp mã/metadata). `vi_tri.py`,
  `_chung/**`, `ngan.py`, `cau_hinh.py`, API/SDK và manifest giữ nguyên.
- Lượt `dang_nhan` ghi `luc_chiem`/`han_chiem` theo giây Unix UTC.
  Cấu hình tùy chọn `thoi_han_chiem_luot_giay` phải là số nguyên dương;
  mặc định lấy thời hạn bước nhận cặp + 60 giây (hiện 180 giây).
  Hết hạn/thiếu hạn được chiếm lại bằng CAS; chưa hết hạn trả
  `DC_DANG_XU_LY`, cho thử lại. Mã chủ riêng mỗi lần thực thi + CAS
  ngăn worker cũ quay lại chốt hoặc cleanup đè chủ mới.
- `da_nhan` nhưng tệp Core cũ thiếu/hết hạn/không còn quyền đọc: chuyển
  `can_thu_lai` bằng CAS rồi chiếm và dựng lại từ nguồn hiện tại đã kiểm
  quyền/băm/trần. Sai băm không bị bỏ qua; lỗi truyền/hủy giữ ngữ nghĩa SDK.
- Khóa chống trùng ghim thêm `ma_cap`, cảnh báo đầu vào và băm JSON toàn
  cấu hình đã điền mặc định (gồm trần pixel/trang/bytes/ký tự/giải nén).
  Cùng mã/nội dung với ID mới vẫn tái dùng khi đủ quyền nguồn cũ; đổi
  metadata/cấu hình tạo lượt mới. Không tái dùng metadata cũ cho mã mới.
- `_vung_bo` dựng chỉ mục văn bản → tập số trang một lần; story DOCX và
  whitelist dùng tập hợp. Kiểm hủy trong lúc lập chỉ mục, duyệt và gom
  vùng bỏ; giữ điều kiện ít nhất hai trang thật, nhiều nút một trang
  không đủ căn cứ. 12.000 nút khối/dòng OCR lề lặp qua 60 trang: **0,1190
  giây** khi đo riêng trên Windows, test bắt buộc `< 2 giây` đã qua.
- Soft hyphen kiểm liền kề trước/sau ký tự và từng khoảng trắng; map
  không nuốt qua vùng đã bỏ. Bảng test giữ phân biệt đủ 14 cặp Anh nêu;
  7 cặp NBSP/tab/nhiều dấu cách/en–em dash/nháy cong chỉ bằng nhau theo
  bộ ghim, tắt từng quy tắc thì lại khác nhau. Thêm test hủy giữa các
  vòng dài, phục hồi/đua CAS/chủ cũ quay lại và 5 kiểu cấu hình hạn sai.
- Không thêm thư viện, không ghi dữ liệu bền trên engine; chỉ DEMO.
  NGUON ghi SHA-256 sau CRLF→LF của mã, schema/bản khai và test hiện tại.
  README/CHANGELOG đã đồng bộ. Không commit/push; PR: **chờ lead mở**.

Kết quả thật bằng `.venv/Scripts/python`, Python 3.13.14, SDK 2.0.0,
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; **đã kiểm bằng Core giả
(CoreGia)**, ngăn RAM và adapter DEMO; chưa kiểm Core thật/Linux:

```text
.venv/Scripts/python -m pytest e_doi_chieu/tests -q --basetemp=.pytest-tmp
297 passed in 4.19s
Mã thoát 0; 0 skipped; 144 ca DC-3 (thêm 60 so với bản bàn giao trước).

.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.3.0: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; 1/1 DEMO ĐẠT (Word).

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0.
```

Lệch/quyết định tạm: biên giữ lượt 60 giây theo yêu cầu sửa của lead;
vẫn ở phiên bản 0.3.0 chưa phát hành. Cần Core mới: không thêm cửa;
đồng hồ worker, quyền/vòng đời tệp và CAS bền vẫn theo C-DC-01/02/06 bên
dưới. Không có câu Chờ Anh mới.

Thời gian thực tế vòng sửa: **14:00–14:17 ngày 15/11/2026 (UTC+7), khoảng
0,28 giờ**. Phiếu DC-3 gốc ước tính **4 giờ**; lead chưa có ước tính riêng
cho vòng sửa. `git diff --check` mã 0; SHA-256 LF hiện hành 7/7 khớp
NGUON, AST bốn tệp DC-3 hợp lệ, không pycache/pyc trong gói. Không có
thay đổi `_chung/**`, `ngan.py`, `cau_hinh.py` hoặc `vi_tri.py`.

### Bản bàn giao trước kiểm độc lập (lịch sử)

- Đúng bốn tệp runtime: thêm `ho_so.py`, `chuan_hoa.py`, `vi_tri.py`, sửa
  `chay.py`. Manifest phiên bản 0.3.0 thêm `doi_chieu.nhan_cap@1`, nhận `tep`
  JSON và trả `ho_so_doi_chieu` đúng schema đã duyệt; cập nhật metadata
  `KHAI-SDK-2.1.json` đủ trường trạng thái/chủ lượt/phong bì ngăn.
- Băm nguyên bytes yêu cầu trước parse; JSON UTF-8 nghiêm, khóa trùng,
  NaN/Infinity, surrogate lẻ, đuôi thừa và độ sâu >64 bị từ chối. Kiểm
  refs/băm/kích thước/phiên bản và quan hệ kết quả văn bản với nguồn gốc;
  đọc lại Word bằng DC-2, không tin `word_da_chot`. OCR lỗi/rỗng/thiếu trang
  không tạo hồ sơ thành công. Mọi tệp qua `viec.mo_tep`, không quyền trả
  `DC_THIEU_NGUON`, sai băm trả `DC_SAI_NGUON`; không đọc đĩa để bù.
- Cấu hình qua ngăn; thiếu trả `CHUA_CAU_HINH`. Bộ chuẩn hóa phải khớp mã,
  phiên bản và băm đã ghim trong cấu hình; không có bộ nới lỏng mặc định.
  Quy ước nội bộ của bộ/snapshot/map được ghi trong README gói để lead cấp
  bộ thật đúng dạng. Không sửa schema chung hoặc văn bản loại dữ liệu.
- NFC/khoảng trắng/nháy/gạch/ngắt dòng theo bộ, giữ dấu, nguyên văn và cây
  khối/ô rỗng/gộp. Map Unicode nửa mở nén theo run; `ve_nguon` trả lát nguồn
  và cấu trúc, kể cả lát rời nhau khi bỏ soft hyphen. Header/footer chỉ bỏ
  chuỗi whitelist có căn cứ story/vùng lề; số trang phải khớp trang thật.
  Header có 1.000.000 VND, mã hợp đồng và nội dung thân giống header vẫn giữ.
  Không dựng trang/hộp Word; OCR không neo duy nhất giữ trang/cảnh báo.
- Snapshot đầy đủ tải lên Core qua `tai_tep_ra`; phong bì chỉ tham chiếu,
  băm/tóm tắt. Chưa so/đo giữ `null`/`chua_kiem`, `ket_luan=null`,
  `da_kiem_du=false`, `de_nghi_chan=true`. Không toàn văn trong ngăn.
- `lay_hoac_tao` chống trùng pháp nhân + băm cặp + bộ + phiên bản engine;
  băm cặp ghim thêm phiên bản/đầu ra OCR/ảnh/bằng chứng, không phụ thuộc ID
  hay tên tệp. Lượt đồng thời chỉ một snapshot/lượt; cập nhật CAS, xung đột
  thử lại hữu hạn không tải lại snapshot. Tái dùng mở lại snapshot **và mọi
  tham chiếu cũ**, không lấy băm/quyền tới ID mới làm quyền tới ID cũ.
  Hủy/lỗi nhường thử lại bằng CAS; mất chủ lượt không đè bản ghi chủ khác.
- Trần §2.3 kiểm metadata và bytes: JSON yêu cầu 1 MiB, nguồn/ảnh/JSON
  20 MiB, tổng đọc 128 MiB (tính bảo thủ cả yêu cầu/snapshot cũ), 60 trang,
  20 triệu pixel, 500.000 ký tự/bản và tổng 1.000.000, snapshot 20 MiB và
  phong bì 64 KiB; ZIP theo DC-2 và trần cấu hình. Vượt trả
  `DC_QUA_GIOI_HAN`, không cắt đuôi. PNG kiểm CRC/DEFLATE/đủ dòng/filter;
  JPEG chỉ kiểm khung/kích thước, **chưa giải mã/quét**. Không gọi AI/Cloud,
  engine khác, chương trình ngoài hoặc mạng ngoài Core; không ghi tệp bền.
- Khép nợ test DC-2: CoreGia gọi handler Word/nhận cặp ném lỗi lạ chứa
  `DEMO_BI_MAT_KHONG_DUOC_LO`; kết quả/stderr không lộ. Lớp bọc handler
  trả câu cố định, giữ ngữ nghĩa hủy/ChuaRo/lỗi truyền; không sửa SDK.
- Hai mẫu NGAN-0, bốn schema dữ liệu tiếp tục nguyên bản; test so băm LF.
  Không thêm dependency runtime, không sửa `ma-nguon/`/Core/API/SDK/
  `docs/goi-gui-engine/`, không xóa tệp, không commit/push. Không có nguồn
  cũ mới cần đưa vào LUU-TRU. README/NGUON/CHANGELOG đã cập nhật.

84 ca DC-3 gồm nhận cặp/băm/schema/snapshot/nguồn thật trong RAM; JSON
nghiêm, OCR rỗng/lỗi, quyền/tệp/khác pháp nhân/module, runtime CoreGia
thiếu cửa từ chối, hai việc đồng thời, tải lại cùng bytes với ID mới,
phiên bản/nguồn dẫn xuất thay đổi, CAS một/nhiều lần/mất chủ, hủy giữa
luồng, mất ACK, trần bytes/ký tự/pixel/giải nén/snapshot, ánh xạ
NFC/NFD/emoji/Hangul/CRLF/khoảng trắng, header tiền/mã và biên bảng/ô rỗng.
Test ảnh còn dùng PNG/JPEG DEMO có sẵn trong repo; không phải số đo OCR.

Môi trường `.venv` trong worktree, Python **3.13.14**, pytest **9.1.1**
qua system-site-packages; SDK **2.0.0** cài offline `--no-index --no-deps`.
SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`. Có `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.3.0: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; 1/1 DEMO ĐẠT (Word).

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
237 passed in 5.36s
Mã thoát 0; 0 skipped.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0; không import Core/kênh cũ, không pycache/pyc/symlink trong gói.
```

Thời gian thực tế: **13:18–13:52:16 ngày 15/11/2026 (UTC+7), khoảng 0,57 giờ**;
ước tính trong phiếu: **4 giờ**. `git diff --check` mã 0; AST bốn tệp
runtime đạt, 0 bộ đệm trong gói; hai mẫu NGAN-0 so băm LF đúng nguồn.

Lệch/phương án bảo thủ: trần đọc manifest 20 MiB nhưng JSON yêu cầu vẫn
1 MiB do SDK dùng chung trần cho tệp con (DC-1 đã ghi); JSON sâu tối đa
64; PNG interlace từ chối và JPEG chưa giải mã DCT tới DC-8. Chuỗi không
neo OCR duy nhất không được đoán hộp. `thu` chỉ có DEMO Word; 84 ca DC-3
end-to-end/thuật toán ở pytest vì runtime chưa có cấu hình/quyền tệp con.
Không nới Word hoặc bịa adapter chạy thật để tạo ví dụ thành công.

### Cần Core — cập nhật DC-3

- **C-DC-02:** cửa cấp/thu hồi tệp con và snapshot xuyên bước, phạm vi
  pháp nhân/module/việc, nguồn gốc đã xác thực của OCR/ảnh/bản render và
  phiên bản gắn với đúng nguồn gốc. SDK `mo_tep` chỉ chứng minh quyền mở
  tệp mà Core cho phép; engine không thể tự chứng minh provenance từ
  chuỗi/băm/boolean của caller. Bản ghép cặp thật phải do Core/module lập.
  CoreGia mặc định thiếu cửa đã test trả `DC_THIEU_NGUON`, adapter ở tests.
- **C-DC-01/02/06:** lưu bền/CAS ngăn thật, cấu hình theo snapshot việc,
  vòng đời tệp kết quả và thu hồi tệp tải lên nhưng việc hủy/lỗi trước chốt.
  Sau kiểm lead, lượt nhận đã có hạn cấu hình và thu hồi CAS theo đồng
  hồ Unix UTC; cần Core xác nhận đồng bộ đồng hồ giữa worker và phối hợp
  lease việc thật. CAS + mã chủ ngăn worker cũ ghi đè; không tự xóa sổ.
  Cleanup bình thường vẫn CAS sang `can_thu_lai`. RAM mất dấu chống trùng
  khi dừng, chưa kiểm ngăn bền/RLS thật.
- **C-DC-05:** chưa kiểm nguồn phân trang/DPI/phép xoay/đổi hệ tọa độ thật.
  PNG interlace chưa hỗ trợ; JPEG chưa giải mã DCT. DC-8 phải dùng thư viện
  đã ghim theo phiếu để giải mã/kiểm ảnh trước detector; dữ liệu CRC/khung
  và pixel ở DC-3 không phải kết quả quét sửa tay. Không so trang Word giả.
- **C-DC-06:** lớp bọc đã ngăn lỗi bất ngờ **bên trong handler** lộ stderr;
  nợ log ngoài handler, lease, lỗi trần SDK còn mở; không tuyên bố vá SDK.
- **Nợ DC-2 theo lead:** `fldChar`/`instrText`/`fldSimple` (số trang,
  mục lục…) và `mc:AlternateContent` hiện làm **từ chối cả tài liệu**.
  Cần xem lại phạm vi khi có hợp đồng thật; **không tự nới trong DC-3**.
- C-DC-03/04 và L-DC-01 giữ mở theo phiếu; chưa xác nhận/đổi hiệu lực,
  detector/từ điển/bộ thật vẫn cần nguồn và phê duyệt theo lát tương ứng.
  **Không có câu Chờ Anh mới.**

## DC-2 — 15/11/2026

**Kết luận: Đạt phạm vi DC-2; PR: chờ lead mở.** Đã kiểm bằng Core giả
(CoreGia); chưa kiểm Core thật, Linux hoặc chất lượng đối chiếu bản ký.

- Đúng ba tệp runtime: `doc_docx.py`, `cau_truc.py`, `chay.py`. Năng lực
  `doi_chieu.doc_docx@1` nhận bytes qua `viec.mo_tep`, băm bytes thật,
  trả loại `van_ban_tai_lieu` phiên bản 1, `nguon_doc=docx`.
- Giữ nguyên văn Unicode, khoảng trắng, đoạn/bảng lồng, ô trống và gộp
  ngang/dọc; đọc đầu/chân trang, footnote/endnote. Cấu trúc và offset
  `[bat_dau, ket_thuc)` đối chiếu lại đúng lát nguyên văn. Không render:
  `so_trang=0`, `trang=[]`, cảnh báo chưa phân trang, không tạo hộp giả.
- Quét sửa đổi/comment trong mọi XML Word, cả phần phụ/thuộc tính; trả
  đúng `DC_WORD_CHUA_CHOT`, không Accept All/xóa bình luận. Node/vùng
  không hỗ trợ, tệp/quan hệ/kiểu phần hỏng trả `DC_WORD_KHONG_DOC_DUOC`.
- Kiểm trước giải nén: DOCX 20 MiB, ZIP 2.000 mục/100 MiB, trùng tên,
  traversal/alias/symlink/encryption, tỷ lệ nén. XML chặn DTD/XXE và có
  trần kích thước/độ sâu/tổng node. Kiểm EOF/CRC/bytes thực độc lập để
  không giấu đuôi nén bằng kích thước tự khai. Cấm quan hệ ngoài/nhúng;
  không truy cập URL, OCR/AI/Cloud hoặc chương trình ngoài.
- Thêm DOCX DEMO sạch vào manifest, phiên bản 0.2.0. Các kiểm tra khung
  DC-0/DC-1 được cập nhật sang hành vi thật; app test contract riêng không
  sao chép DEMO của năng lực khác. **Khép nợ danh sách DEMO rỗng** của
  DC-0/DC-1; các ghi nhận lỗi mã 1 bên dưới là kết quả lịch sử.
- 107 ca DC-2 mới (tổng 153), gồm nguyên văn tiếng Việt/NFD/emoji,
  1.000.000 VND và 2026-10-30, bảng/ô gộp/rỗng/lồng, story phụ, sửa đổi,
  comment, XML/ZIP hỏng/nguy hiểm, quan hệ ngoài, ZIP giả CRC/kích thước,
  DEFLATE nhiều chunk/data descriptor, vượt trần, hủy, không truy cập đĩa.
- Không sửa nguồn Trích xuất, `ma-nguon/`, API/SDK/Core, schema chung hoặc
  hai mẫu NGAN-0. Bản chép schema/mẫu vẫn được test so băm LF. Nguồn/băm
  chuyển thuật toán và DEMO ghi tại `goi/e_doi_chieu/NGUON.md`.
  Không có mã cũ mới cần chuyển LUU-TRU; không commit/push.

Kiểm bằng `.venv/Scripts/python`, Python 3.13.14; SDK 2.0.0 cài offline
`--no-index --no-deps`, wheel SHA-256 khớp SHA256SUMS.txt; pytest 9.1.1
có sẵn qua system-site-packages. Biến kiểm `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1`, không tạo bộ đệm trong gói:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
[ĐẠT] Đọc bản Word DEMO đã chốt, có bảng ô gộp và ô trống
Engine e_doi_chieu 0.2.0: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; 1/1 DEMO ĐẠT.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
153 passed in 0.62s
Mã thoát 0; 0 skipped.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
ĐẠT: kiểm độc lập
Mã thoát 0; không import Core/kênh cũ, không pycache/pyc/symlink trong gói.
```

Thời gian thực tế: 12:52–13:15:09 ngày 15/11/2026 (UTC+7), khoảng **0.39 giờ** (ước tính trong phiếu: **4 giờ**).

Lệch/phạm vi bảo thủ: ngoài trần §2.3, có trần phòng vệ XML 16 MiB/phần,
128 mức/200.000 node toàn gói, tỷ lệ nén 200, bảng 256 cột/50.000 ô gốc,
cây khối 16 mức. Phần Word chưa hiểu (field, hình/textbox, công thức,
Strict OOXML, nhúng, danh sách liên kết style/picture bullet…) bị từ chối;
không thay thành cảnh báo đọc thiếu. Quy ước tuần tự hóa/offset và danh
sách hỗ trợ ghi đầy đủ tại README gói, không đổi API/schema chung.

### Cần Core — cập nhật DC-2

- C-DC-05 giữ mở: chưa có bản render Word tin cậy; không so trang vật lý
  bằng DOCX XML. Core/lead cần cấp bản phân trang và ánh xạ khi mở lát đó.
- C-DC-01/02/03/04/06 giữ các phụ thuộc DC-1 đã ghi; riêng bộ đọc DC-2
  không cần cấu hình máy/ngăn bền hay cửa gọi engine khác. Không thêm
  blocker mới; ngăn RAM vẫn mất khi dừng. Không coi test DEMO là kiểm Core
  thật hoặc nghiệm thu toàn tuyến. Không có câu Chờ Anh mới.

## Cần Core (chuyển lead Core qua Anh)

**Cập nhật DC-1 — 15/11/2026, PR: chờ lead mở:**

- DC-Q17 và 17 câu Đối chiếu đã duyệt theo đề xuất trong quyết định chiều
  15/11. Nhãn chờ duyệt DC-P và kiểm kê trước DC-0 bên trên là lịch sử.
- C-DC-02: Core cần cấp/thu hồi quyền từng tệp con trong JSON yêu cầu,
  snapshot, văn bản và ảnh, giữ vòng đời xuyên bước/ACK, cô lập pháp nhân/module.
  CoreGia 2.0 chỉ thấy ID trong phong bì, không lần theo bytes JSON.
  Adapter DEMO chỉ ở tests; thiếu quyền/nguồn/ảnh thiết kế trả `DC_THIEU_NGUON`.
- C-DC-02/06: SDK 2.0 dùng cùng trần `mo_tep` cho tệp JSON yêu cầu và tệp
  con. DC-3 cần khai trần đọc 20 MiB, tự kiểm JSON yêu cầu ≤1 MiB và tổng
  tệp con ≤128 MiB. Chưa đổi năng lực runtime ở DC-1; đề nghị SDK tách trần.
- C-DC-05: phiếu OCR SDK 2.0 chưa khai OCR vùng; nhánh PDF/ABBYY/Tesseract
  hiện không xuất cờ nghi ngờ. Lead OCR cần chốt nguồn cờ, ảnh và ánh xạ
  tọa độ/OCR lại; DOCX chưa render không kiểm trang vật lý bằng số trang suy đoán.
- C-DC-01/03/04/06 và L-DC-01 tiếp tục mở: ngăn bền, quyền/danh tính xác
  nhận chỉ-thêm, mapping chặn hiệu lực, nợ log/lease/trần SDK; từ điển,
  font/detector/model có nguồn/băm/giấy phép và số đo thật. Không phát sinh
  yêu cầu Anh duyệt lại DC-Q17 hoặc cho phép lách cổng.
- Lead/Core cần thống nhất nghiệm thu lát khung `chay_thu_demo=[]`:
  `kho_tri_thuc_sdk.thu` 2.0.0 trả mã 1 khi không có ví dụ. Giữ nguyên SDK
  và 0 demo nghiệp vụ theo lệnh giao, không thêm thành công giả để đạt mã 0.

## DC-1 — 15/11/2026

**Xong phần contract/khảo sát; chưa đạt điều kiện kiểm chung vì `thu` không
có demo; PR: chờ lead mở.** Chi tiết tại `DC-1-KHAO-SAT.md`. Đã kiểm bằng
Core giả (CoreGia), chưa kiểm Core thật hoặc chất lượng OCR/detector.

- Thêm đúng 5 tệp schema: nguồn `ho_so_doi_chieu` + bản chép trong gói +
  ba bản chép schema chung đã khóa; test so SHA-256 sau CRLF→LF. Schema
  cấu hình DC-0 giữ nguyên, tổng trong gói là 5 schema. Hai mẫu NGAN-0 giữ
  nguyên và so băm LF. Không thêm dependency runtime.
- Manifest đăng ký đúng tên bốn loại đã duyệt, sửa nhãn tiếng Việt;
  chỉ giữ năng lực khung Word `CHUA_LAM`, không thêm `nhan_cap`, `nhan_2`
  hoặc route. Thiết kế required/enum/trần và kiểm Python riêng cho đầu vào
  JSON cặp, snapshot và phong bì theo DC-P; không viết handler nghiệp vụ.
- Khảo sát từ mã trong workspace: tọa độ từ/cờ nghi ngờ, Word chưa phân
  trang/khác chính sách Accept All, OCR vùng cũ/chưa có ở phiếu SDK 2.0,
  quyền tệp con, nguồn từ điển/giấy phép và 3 hướng detector. Tách rõ
  **CẦN ĐO** máy thật. Không đọc Hot Folder/ngoài workspace, không mạng/Cloud.
- Fixture DEMO có băm/kích thước đo từ bytes CoreGia; kiểm hợp lệ, sai
  loại/sai băm/hết quyền/chưa có cửa Core/thiếu ảnh/tóm tắt lệch. Không tạo
  confidence hoặc hộp chữ giả, chưa đo giữ null. Adapter không nằm trong gói.

Kiểm bằng Python **3.13.14** của `.venv` (system-site-packages cho pytest
**9.1.1** có sẵn), SDK **2.0.0** cài offline `--no-index --no-deps` từ wheel
trong repo; SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`. Có `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát 1; 0 demo nghiệp vụ, không có kết quả x/x ĐẠT.

.venv/Scripts/python -m pytest e_doi_chieu/tests -q
46 passed in 0.28s
Mã thoát 0; 0 skipped; giữ test khung CHUA_LAM.

.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
Mã thoát 0; dòng in kế thừa DC-0 bị mất dấu; kiểm AST/import và gói đạt.
```

Không sửa `ma-nguon/`, ba schema nguồn đã khóa, API/SDK/Core hoặc mẫu NGAN-0;
không commit/push. Thời gian thực tế: 12:36–12:51 ngày 15/11/2026 (UTC+7),
khoảng **0,25 giờ**, so với **3 giờ ƯỚC TÍNH** trong phiếu.

## Cần Core — các mục lịch sử DC-P

- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

**Bổ sung DC-P — 15/11/2026 (PR: chờ lead mở):** mục cổng chung cũ ở trên là lịch sử, chưa được kiểm lại Core thật. Chi tiết cửa cần hiện hành tại phiếu §5.1:

| Mã | Thiếu / yêu cầu cửa chung | Ảnh hưởng và cách làm tạm |
|---|---|---|
| C-DC-01 | NGAN-0 và SDK 2.1: ngăn lô/CAS/duy nhất/phạm vi, cấu hình, nạp màn | `_chung/mau-ma/` chưa có trong worktree lúc lập phiếu; DC-0 chờ lead gộp mẫu. Sau đó RAM/KttCore giả; bản khai riêng KHAI-SDK-2.1, không thêm khóa mới vào manifest 2.0 |
| C-DC-02 | Ghép hai tài liệu/tệp con, quyền/vòng đời giữa bước, Local-only và điều phối OCR lại/bỏ qua AI | CoreGia + adapter test; runtime thiếu quyền/nguồn từ chối. Không đọc đĩa, không tự gọi engine khác/fan-in |
| C-DC-03 | Xác nhận chỉ-thêm, danh tính/giờ/quyền tin cậy, CAS/chống trùng; quyền xem hồ sơ/duyệt từ điển | Chỉ mô phỏng khi chưa có cửa; UI không ghi ngăn trực tiếp để vượt kiểm quyền. RAM không chứng minh lưu bền/xác nhận thật |
| C-DC-04 | Cửa sự kiện/mapping module cho chặn/mở hiệu lực, giữ tầng 1, thông báo và chưa kiểm được | Engine trả kết quả/cờ, module quyết định trạng thái. Không tự tạo route, schema SQL hoặc phát sự kiện riêng |
| C-DC-05 | Lead OCR chốt OCR vùng SDK 2.0, tọa độ/cờ nghi ngờ/ảnh; nguồn phân trang Word nếu có | Chưa có bằng chứng giữ Cần xem/chưa kiểm; không bịa trang/hộp hoặc coi mã OCR vùng cũ là đã tích hợp |
| C-DC-06 | Log SDK an toàn, kiểm trần sâu loại riêng, lease và ánh xạ lỗi trần tệp theo SDK 2.1 §7 | Tự kiểm sâu và log mã chung; giữ nợ SDK rõ, không sửa SDK/Core trong engine |

Nguồn lead cần cấp L-DC-01: mẫu ngăn, từ điển/font/detector có nguồn/băm/giấy phép và dependency offline; K2 chỉ khi lead cung cấp bản tham chiếu trong workspace. Thiếu nguồn dùng DEMO để test giao thức, không coi là detector/từ điển đã đạt.

## DC-0 ? 15/11/2026

**Ch?a ??t ?i?u ki?n ki?m chung; PR: ch? lead m?.** ?? t?o khung SDK 2.0, ch?p nguy?n m?u NGAN-0, schema c?u h?nh v? b?n khai d? ki?n SDK 2.1. N?ng l?c ??c Word tr? `CHUA_LAM`; vi?c c?n c?u h?nh thi?u tr? `CHUA_CAU_HINH`. Kh?ng c? v? d? th?nh c?ng gi?; ch?a tri?n khai m?n. ?? ki?m b?ng Core gi? (CoreGia), kh?ng ch?ng minh nghi?p v?.

- `python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu`: **0 v? d?**, b?o ?Phi?u ch?a c? v? d? chay_thu_demo.?, m? tho?t **1**. SDK 2.0 kh?ng coi danh s?ch r?ng l? th?nh c?ng; y?u c?u khung r?ng xung ??t v?i ?i?u ki?n m? tho?t 0. Kh?ng th?m v? d? gi? v? kh?ng s?a SDK.
- `python -m pytest e_doi_chieu/tests -q`: **5 passed**, 0 skipped, m? tho?t 0.
- `python e_doi_chieu/tests/kiem_doc_lap.py`: ??t, m? tho?t 0. D?ng Python c?a `.venv` v? `PYTHONDONTWRITEBYTECODE=1`.

### C?n Core / lead ? DC-0

- Lead/Core quy?t ??nh c?ch nghi?m thu khung c? `chay_thu_demo: []`: SDK 2.0 tr? m? 1 khi kh?ng c? v? d?, trong khi ?i?u ki?n chung ??i m? 0.
- SDK 2.1/Core c?n c?p ng?n b?n, c?u h?nh v? n?p m?n theo C-DC-01; RAM m?t khi d?ng. `KHAI-SDK-2.1.json` ch? l? d? ki?n, c?c m?n ch?a t?n t?i ??n DC-10/DC-11; quy?n xem k?t qu? c?n Core x?c ??nh.
- M?u NGAN-0 quy ??nh b?ng c?u h?nh kh?a `{}`, thay cho kh?a `ma` trong b?ng d? ki?n DC-P ?2.4; d?ng API m?u ?? g?p. Ng??ng OCR k?m gi? null v? ch?a ?o.

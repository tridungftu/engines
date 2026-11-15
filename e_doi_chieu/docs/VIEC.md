# VIỆC — danh sách việc duy nhất của project `e_doi_chieu`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
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

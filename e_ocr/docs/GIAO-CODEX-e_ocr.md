# Giao Codex — `e_ocr` (Nhận dạng văn bản) theo SDK 2.0

*Lập 14/11/2026 (Claude, lead). Ưu tiên 1 (song song Hỏi AI). Căn cứ: `QUYET-DINH-CUOI-e_ocr.md` (06/11 21:00), `YEU-CAU-VA-HIEN-TRANG.md`, `KS-OCR-CHUA-RO.md` (phương án B), `API-ENGINE-v1.md`, `_chung/docs/GIAO-CODEX-THU-TU.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`.*

## 1. Kết luận

- **8 lát, khoảng 27 giờ công (ước tính, chưa đo).** OCR-0 → OCR-1 trước; OCR-2, OCR-3 song song sau OCR-1; OCR-4 sau OCR-2.
- Đích: gói `e_ocr/goi/e_ocr/` chạy bằng SDK 2.0: **ABBYY Hot Folder trước, tự chuyển Tesseract (mask_ocr)** khi hết hạn mức 5.000 trang/30 ngày, ABBYY tắt hoặc lỗi/quá giờ; kết quả ghi rõ nguồn đọc; "chưa rõ" không báo thành công giả.
- Đợt 1 ABBYY dùng **Hot Folder trên cùng máy** (Core chạy loopback). Cầu nối HTTPS có khóa (OCR-9, ca 8) để khi Core có bí mật và ABBYY lên máy chủ.
- `ocr.trich_vung@1` **chưa khai phiếu**: đầu vào là vùng do bước trước tạo, cần chốt cùng `e_doi_chieu`. Mã `vung.py` giữ nguyên ở `ma-nguon/`.
- Lõi tái dùng: `lop_chu.py`, `van_ban.py`, `bang.py`, `ban_giao.py`, `abbyy.py`, `chon_nguon.py`, `vendor/mask_ocr/`. **Bỏ** `lib/cong_ocr.py` (import `kho_tri_thuc.sdk_core`), vỏ `chay.py` cũ, hàm SDK riêng `ocr_*_luot`.

## 2. Thiết kế phiếu `engine.json` 2.0 (Codex được chỉnh chi tiết, ghi lý do trong PR)

| Năng lực | Nhận | Trả | Dùng khi |
|---|---|---|---|
| `ocr.doc_tai_lieu@1` | `tep` (PDF, PNG, JPEG) | `van_ban_tai_lieu` | Bước chuẩn cho chuỗi: Hỏi AI, Trích xuất, Đối chiếu, Tra cứu |
| `ocr.doc_van_ban@1` | `tep` | `van_ban` | Bước sau chỉ nhận văn bản thuần, hoặc ghép thẳng vào cột |
| `ocr.xuat_word@1` | `tep` | `tep` (DOCX giữ bảng, ô trống, ô gộp) | Người dùng cần bản Word |

- **Cài đặt bước** (cả 3): `nguon` kiểu `chon`: `tu_dong` (mặc định) / `chi_abbyy` / `chi_tesseract`.
- **Giới hạn:** `tep_toi_da_mib` 20, `mime` `["application/pdf","image/png","image/jpeg"]`, `thoi_han_giay` 900. **Trần 60 trang** không có khóa trong `gioi_han`, nên engine tự đếm và từ chối `LoiNghiepVu("QUA_SO_TRANG", …)` **trước khi trừ hạn mức**.
- **Cấu hình máy** (tệp ngoài gói): `abbyy.bat`, `abbyy.thu_muc_vao`, `abbyy.thu_muc_ra`, `abbyy.thoi_han_giay`, `abbyy.han_muc_trang_30_ngay` (5000), `tesseract.duong_dan`, `tesseract.ngon_ngu` (`vie+eng`). Không chứa khóa.
- **Dữ liệu tạm** (`kho_tam`, thư mục dữ liệu engine — chờ Anh Q2): sổ hạn mức theo ngày, nhật ký lượt ABBYY (`ma_tuong_quan`, `bam_noi_dung`, `phap_nhan_id`, số trang, trạng thái), dấu chống trùng. **Không lưu nội dung tệp.**

## 3. Các lát

| Lát | Nội dung | Yêu cầu | Phụ thuộc | Giờ (ước tính) |
|---|---|---|---|---:|
| OCR-0 | Khung gói SDK 2.0, `cau_hinh_may`, `kho_tam`, kiểm độc lập | OCR-6 | — | 2 |
| OCR-1 | Nguồn ABBYY: lớp chữ PDF + Hot Folder cục bộ → `doc_tai_lieu`, `doc_van_ban` | OCR-2, 3, 4, 7 | OCR-0 | 5 |
| OCR-2 | Dự phòng Tesseract + chọn nguồn + sổ hạn mức | OCR-8 | OCR-1 | 5 |
| OCR-3 | `ocr.xuat_word@1` giữ bảng | OCR-4, 5 | OCR-1 | 3 |
| OCR-4 | "Chưa rõ" (phương án B) + chống trùng bền | OCR-13, 14 | OCR-2 | 4 |
| OCR-5 | Bộ DEMO + chạy thử DEMO + bài OCR-MAY trên Core giả | OCR-11, 15, 16 | OCR-2, 3, 4 | 4 |
| OCR-6 | Ghim thư viện, `NGUON.md`, cài máy sạch | OCR-6 | OCR-5 | 2 |
| OCR-7 | Công cụ thử ABBYY thật trên máy hiện tại (Anh chạy) | OCR-12 | OCR-5 | 2 |
| | **Tổng** | | | **27** |

Ngoài phạm vi Codex đợt này: ca 1 (màn Quản lý engine: chờ thẻ "Trạng thái" của Core), ca 8 (cầu nối có khóa: chờ bí mật), ca 6 (trích vùng: chờ thiết kế cùng `e_doi_chieu`).

## 4. Lệnh giao Codex từng lát (dán nguyên khối)

### OCR-0 — Khung gói
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_ocr/docs/GIAO-CODEX-e_ocr.md, e_ocr/docs/QUYET-DINH-CUOI-e_ocr.md.
Làm lát OCR-0 cho e_ocr:
1. Tạo e_ocr/goi/e_ocr/ theo AGENTS.md §3 (mẫu: docs/goi-gui-engine/sdk-2.0.0/engine-demo/e_demo_doc_tep).
2. engine.json 2.0 theo GIAO-CODEX-e_ocr.md §2 (3 năng lực, tham_so "nguon", loai_du_lieu_rieng van_ban_tai_lieu). Hàm tạm raise LoiNghiepVu("CHUA_LAM", ...).
3. Nếu _chung/contract/van_ban_tai_lieu.schema.json chưa có (do lát AI-0 tạo) thì tạo theo LOAI-DU-LIEU-RIENG.md §2.1; chép vào gói; test so băm.
4. e_ocr/goi/e_ocr/e_ocr/cau_hinh_may.py (JSON ngoài gói, KTT_ENGINE_CAU_HINH, có schema) và kho_tam.py (thư mục KTT_ENGINE_DU_LIEU; ghi nguyên tử tệp tạm + os.replace; khóa tệp đa tiến trình; API nho: doc/ghi theo khóa, không nhận bytes nội dung tài liệu). Test cả hai, gồm hai tiến trình ghi đồng thời.
5. e_ocr/tests/kiem_doc_lap.py như AGENTS.md (không kho_tri_thuc.*, không __pycache__).
Không sửa ma-nguon/. Đạt: tu_khai_bao không lỗi; pytest xanh; kiem_doc_lap mã 0.
```

### OCR-1 — Nguồn ABBYY
```
Làm lát OCR-1 cho e_ocr.
Chép và sửa từ e_ocr/ma-nguon/: lop_chu.py (đọc lớp chữ "text under image" của PDF ABBYY, không OCR lại ảnh nền), van_ban.py, bang.py, abbyy.py (Hot Folder: thả tệp vào thu_muc_vao, chờ kết quả ở thu_muc_ra theo ma_tuong_quan, có thời hạn và hủy). Bỏ mọi phụ thuộc kho_tri_thuc.* và lib/cong_ocr.py.
Viết ocr.doc_tai_lieu@1 (tep → van_ban_tai_lieu, nguon_doc="abbyy" hoặc "lop_chu_san" khi PDF đã có lớp chữ) và ocr.doc_van_ban@1 (tep → van_ban, dùng chung lõi).
- Đọc tệp bằng viec.mo_tep; tệp tạm trong thư mục tạm riêng của việc, xóa ở finally.
- Tự đếm trang trước khi gửi ABBYY; > 60 trang → QUA_SO_TRANG; tệp hỏng → TEP_HONG. Câu lỗi tiếng Việt, không lộ đường dẫn.
- viec.tien_do theo bước; viec.kiem_huy() trong vòng chờ ABBYY; hủy thì rút tệp khỏi thu_muc_vao nếu ABBYY chưa nhận.
- bam_dau_vao = sha256 tệp; phien_ban_engine; canh_bao.
Test Linux: ABBYY giả = luồng nền đọc thu_muc_vao, ghi PDF có lớp chữ vào thu_muc_ra (dùng pymupdf nếu đã ghim trong requirements cũ, nếu không thì dựng PDF DEMO bằng mã thuần trong tests/demo); CoreGia().chay_thu: PDF DEMO 3 trang → đúng "Công ty DEMO Ánh Dương", 1.000.000 VND, 30/10/2026, có vị trí trang; PDF đã có lớp chữ → không gửi ABBYY; quá trang; tệp hỏng; hủy.
```

### OCR-2 — Dự phòng Tesseract và chọn nguồn
```
Làm lát OCR-2 cho e_ocr.
- Chép vendor/mask_ocr (CHỈ nhánh Tesseract, đọc PDF có chữ sẵn, DOCX, giữ bảng) vào gói; KHÔNG chép VietOCR, model VietOCR, review dual. Ghi giấy phép "phần mềm nội bộ, dùng nội bộ tập đoàn" trong NGUON.md.
- Chọn nguồn (chép logic chon_nguon.py, bỏ phần luot_ben cũ): ABBYY trước; chuyển Tesseract khi (a) sổ hạn mức kho_tam cho thấy đã dùng + số trang việc này > han_muc_trang_30_ngay (cửa sổ trượt 30 ngày), (b) ABBYY tắt (thư mục không truy cập được / abbyy.bat=false), (c) ABBYY lỗi hoặc quá abbyy.thoi_han_giay mà CHẮC CHẮN ABBYY chưa nhận tệp. ABBYY đã nhận mà chưa trả → không chuyển, để OCR-4 xử lý.
- tham_so nguon: chi_abbyy → không chuyển, báo lỗi rõ; chi_tesseract → bỏ ABBYY.
- Ghi nguon_doc + ly_do_chuyen_nguon vào kết quả. Trừ hạn mức chỉ khi ABBYY đã nhận; không trừ khi bị từ chối trước khi gửi.
- Thiếu tesseract → LoiNghiepVu NGUON_DU_PHONG_CHUA_CAI khi cần dùng; ghi vào VIEC.md "Cần cài" (hướng dẫn .cmd cho Anh).
Test: giả hết hạn mức, ABBYY tắt, ABBYY quá giờ trước khi nhận; Tesseract giả (mock) cho CI; 1 test dùng tesseract thật nếu có trên máy (skip có lý do nếu không).
```

### OCR-3 — Xuất Word giữ bảng
```
Làm lát OCR-3 cho e_ocr.
Viết ocr.xuat_word@1 (tep → tep): dựng DOCX từ van_ban_tai_lieu (chép bang.py, ban_giao.py, phần xuất Word của mask_ocr), giữ ô trống, ô gộp (gop_hang/gop_cot), vị trí bảng, thứ tự trang. Gửi bằng viec.tai_tep_ra(ten, bytes, mime docx); tên tệp "<tên gốc>-OCR.docx".
Test: bảng DEMO có ô trống và ô gộp → mở lại DOCX bằng zipfile + XML, kiểm số ô, gridSpan/vMerge, ô trống còn nguyên; tiền/ngày nguyên văn.
```

### OCR-4 — "Chưa rõ" và chống trùng
```
Làm lát OCR-4 cho e_ocr (đọc e_ocr/docs/KS-OCR-CHUA-RO.md, phương án B).
- Trước khi thả tệp vào ABBYY: ghi lượt vào kho_tam {ma_tuong_quan (tất định từ phap_nhan_id + bam_noi_dung + lan gửi), bam, so_trang, trang_thai="dang_gui"}; giữ hạn mức.
- ABBYY đã nhận (tệp biến khỏi thu_muc_vao) mà quá thời hạn chưa có kết quả → raise ChuaRo(ma_tuong_quan). KHÔNG chuyển Tesseract, KHÔNG hoàn hạn mức.
- Việc mới (hoặc Core giao lại, lan_thu>1) cùng phap_nhan + bam: đọc lượt trong kho_tam → nếu "dang_gui"/"chua_ro": tìm kết quả ở thu_muc_ra theo ma_tuong_quan trước; có thì chốt "xong" và trả; chưa có thì lại ChuaRo, không gửi lại. Chỉ hoàn hạn mức khi có căn cứ (ABBYY trả lỗi rõ).
- Chống trùng: cùng phap_nhan + bam đang có lượt dở → không gửi ABBYY lần hai. Dấu bền qua khởi động lại (kho_tam), khắc phục ghi chú OCR-14 "mất khi khởi động lại".
- Ghi vào VIEC.md: khi Core có thao tác #10 luot-ben thì thay kho_tam phần lượt.
Test: khởi động lại tiến trình giữa chừng (tạo App mới, cùng kho_tam), giao lại, tệp trùng đồng thời, ABBYY trả muộn sau ChuaRo.
```

### OCR-5 — DEMO và bài OCR-MAY
```
Làm lát OCR-5 cho e_ocr.
- Chuyển e_ocr/ma-nguon/tests/demo/tao_bo_demo.py: sinh bộ DEMO giả (PDF quét 3 trang có bảng ô trống/ô gộp, 2 ảnh PNG/JPEG, Word đáp án "Công ty DEMO Ánh Dương", 1.000.000 VND, 30/10/2026; PDF 61 trang; tệp > 20 MiB; tệp hỏng). Tệp nhỏ đặt trong goi/e_ocr/demo/ cho chay_thu_demo; tệp lớn chỉ sinh lúc test, không commit.
- chay_thu_demo: PDF DEMO và 1 ảnh DEMO cho cả 3 năng lực, tham_so nguon=chi_tesseract để chạy được không cần ABBYY; e_ocr/tests/chay_demo.py chạy CoreGia().chay_thu_demo với Tesseract giả khi máy không có tesseract (ghi rõ).
- e_ocr/tests/test_ocr_may.py: ca 2, 3, 4, 5, 7, 9 của YEU-CAU-VA-HIEN-TRANG.md §3 trên CoreGia + ABBYY giả; ca 9: nhật ký stderr có thời gian chờ/chạy và nguồn đọc, không có nội dung/đường dẫn. Ghi rõ ca 1, 6, 8 ngoài đợt này và lý do.
- Cập nhật VIEC.md, YEU-CAU-VA-HIEN-TRANG.md ("đã kiểm bằng Core giả").
```

### OCR-6 — Ghim và máy sạch
```
Làm lát OCR-6 cho e_ocr.
- goi/e_ocr/requirements.lock: chỉ thư viện thật dùng (rà lại pymupdf, defusedxml, Pillow từ requirements.lock cũ; bỏ cái không dùng), ghim phiên bản + hash, Windows x64 CPython 3.13 và Linux cho CI.
- NGUON.md: nguồn từng tệp (ma-nguon → goi), giấy phép nội bộ, SHA-256 tệp trong gói.
- tests/kiem_may_sach.sh và KIEM-MAY-SACH.cmd (ASCII): venv mới, cài SDK wheel --no-index --no-deps, cài lock, chạy tests/chay_demo.py.
```

### OCR-7 — Thử ABBYY thật (lát 9)
```
Làm lát OCR-7 cho e_ocr. Codex KHÔNG chạy bản thật.
- e_ocr/cong-cu/thu_abbyy_that.py: mặc định chạy khô; --that mới thả PDF DEMO (từ tao_bo_demo) vào Hot Folder theo tệp cấu hình máy Anh chỉ định; đo thời gian, so đáp án tiền/ngày, kiểm bảng Word, ghi JSON kết quả. Không đọc/chép in\ out\ jobs\ state\ có sẵn của abbyy-hotfolder; dùng thư mục DEMO riêng.
- THU-ABBYY-THAT.cmd (ASCII) + 5 dòng hướng dẫn trong README.
```

## 5. Cần Core / Chờ Anh của engine này
- Cần Core: `GIAO-CODEX-THU-TU.md` §3 điểm 1, 2, 3, 4, 7.
- Chờ Anh: Q1, Q2, Q3 (`GIAO-CODEX-THU-TU.md` §4). Giữ nguyên ba việc chờ của `YEU-CAU-VA-HIEN-TRANG.md` §6: giấy phép FineReader Corporate, chuyển hồ sơ thật ở `abbyy-hotfolder\in\`, `out\` vào lưu trữ, ngưỡng đúng/sai của Tesseract sau lần đo đầu.

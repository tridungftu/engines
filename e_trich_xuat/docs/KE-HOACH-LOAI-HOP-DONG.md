# Kế hoạch LHD — Loại hợp đồng và import danh mục tham số cho engine trích xuất (CD-072 + CD-071)

**Ngày lập:** 05/11/2026 · **Nhánh:** `lat/loai-hd-tk` (HEAD `fbfe4f53`) · **Trạng thái:** KẾ HOẠCH, chưa code, chờ Anh chọn các câu ở mục 9.
**Thứ tự Anh chốt:** làm SAU CD-060 Mốc II và SAU đóng gói G3-GOI (`docs/47-core/g3/KE-HOACH-G3-GOI.md`). Mọi đường dẫn mã trong kế hoạch này viết theo vị trí **sau đóng gói**: thư mục thật `engines/e_trich_xuat/` (tên Python vẫn là `kho_tri_thuc.engines.e_trich_xuat`, shim ở `src/kho_tri_thuc/engines/e_trich_xuat/__init__.py`; nguồn review thuần nằm ở `engines/e_trich_xuat/vendor/review/` theo lát G3-GOI 32). Riêng dẫn chứng "đang ở đâu" trỏ vào vị trí hiện tại `src/kho_tri_thuc/engines/e_trich_xuat/` và nguồn gốc `D:\Claude\Ho tro review ho so xay dung\review_xaydung\trich_xuat\`.
**Cách khảo sát:** chỉ đọc mã và tài liệu. Không chạy pipeline, không gọi AI, không chạy PostgreSQL/server. Không mở nội dung hợp đồng thật, không mở tệp đáp án `DAP_AN_*.tsv` (chỉ đếm tên tệp). SHA-256 nguồn gốc đã đối chiếu khớp với giá trị engine đang ghim (`doc_hop_dong.py` bbe8d957…, `danh_muc.py` 4309decb…, `logic.py` f7cfcf37…, `DANH_MUC_THAM_SO.xlsx` 05846a2a…).

---

## Phần A — Tóm tắt cho người đọc nghiệp vụ

**Câu hỏi 1 của Anh (CD-071 a): hợp đồng xây dựng nhưng mẫu khác thì engine có chạy được không?**
Có. Công cụ gốc tìm thông tin **theo nội dung**, không theo vị trí trang hay ô cố định: tách hợp đồng theo dòng "Điều N", chấm điểm từng Điều/Khoản bằng từ khoá trong danh mục, đoạn nào không khớp từ khoá thì AI tự tìm qua mục lục, cuối cùng **rà lại toàn bộ hợp đồng** cho các ô còn vàng và kiểm trích dẫn có đúng nguyên văn. Mẫu khác chỉ làm **giảm độ chính xác** (nhiều ô vàng hơn) ở 6 trường hợp đã thấy trong mã (mục 2.2), ví dụ hợp đồng không đánh "Điều 1, Điều 2…", tiêu đề Điều kết thúc bằng một con số, hay dùng từ khác với từ khoá. Không trường hợp nào làm engine "đọc nhầm chỗ" một cách im lặng: ô nghi ngờ đều thành ô vàng kèm lý do.

**Câu hỏi 2 của Anh (CD-071 b): loại hợp đồng khác, bộ tham số khác?**
Hiện **chưa chạy được** (engine khoá cứng loại XD, 37 mã). Phần lõi đọc/tìm/hỏi AI/kiểm đã dùng danh mục làm đầu vào, nên **không phải viết lại engine**; cần làm: sổ loại hợp đồng, nạp danh mục từ Excel thành phiên bản có mã băm, chạy thử trước khi dùng, engine nhận loại + phiên bản, kiểm logic theo loại. Ước tính **15 lát lập trình + 3 bước lead tự chạy**. Sau khi xong, thêm một loại mới **không cần sửa mã**: người phụ trách tải Excel → hệ thống kiểm → chạy thử 3–5 hợp đồng mẫu → bấm Kích hoạt.

**Sẽ có 3 màn trong Quản trị Core** (làm trước bằng dữ liệu giả có nhãn để Anh góp ý — CD-058):

```
 Loại hợp đồng ──► Import danh mục (Excel) ──► Chạy thử 3–5 HĐ mẫu ──► Kích hoạt ──► Module (CRM…) gửi hợp đồng
  (XD, DV, …)       kiểm từng dòng, lỗi        bảng kết quả từng          người có        kèm loại; Core ghim
                    tiếng Việt; mỗi lần        tham số, ô vàng            quyền bấm        phiên bản đang dùng;
                    nạp = 1 phiên bản          + lý do                                     kết quả ghi loại +
                    có mã băm, xem khác biệt                                               phiên bản để truy vết
```

**Điều không đổi:** loại **XD — Hợp đồng xây dựng** dùng đúng danh mục 37 mã hiện tại (cùng mã băm), đúng 9 bước của công cụ gốc; kết quả phải giống hệt trước khi đổi (kiểm bằng phép so tự động trên mẫu DEMO và kiểm nhanh 2 hợp đồng có đáp án — mục 6). Tham số hỏi thêm một lượt (Y-01, Y-02…) giữ cách của công cụ gốc. Kiểm chéo Cloud vẫn tắt; thử chỉ bằng dữ liệu DEMO.

**Cần Anh chọn** (chi tiết mục 9): loại làm đầu tiên sau XD (đề xuất **DV — dịch vụ bản gọn**, đã có danh mục nháp TL 44); một người được tự import và tự kích hoạt hay phải hai người; quy tắc logic cho loại mới đặt trong Excel hay để trống; sổ loại dùng chung hay theo pháp nhân; quyền đặt ở Quản trị Core; chỉ có **2** hợp đồng có đáp án cho kiểm nhanh (một tệp là `.doc`).

**Dự kiến (ước tính):** màn dữ liệu giả 06/11; phần Core 07–08/11; phần engine trong 2–3 ngày sau khi G3-GOI xong nhóm lát trích (31–37); thử DEMO trọn luồng khoảng 12/11. Ngày phụ thuộc tiến độ G3-GOI và câu trả lời mục 9.

---

## 1. Căn cứ và phạm vi

| Căn cứ | Nội dung dùng |
|---|---|
| `docs/46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md` CD-071 (dòng 737–745) | Hủy đo lớn TRICH-4b; kiểm nhanh "ra cùng kết quả" 2–3 hợp đồng có đáp án; trả lời (a) mẫu khác, (b) loại khác bằng ước lượng; không làm (b) khi Anh chưa chọn loại ưu tiên. |
| CD-072 (dòng 747–759) | 7 mục phạm vi: sổ loại, import Excel thành phiên bản ghim mã băm, chạy thử trước Kích hoạt (quyền MTQ), engine nhận loại + phiên bản, logic theo loại (L1/L4 chung, L2/L3/L5 chỉ XD), Y-01/Y-02 giữ nguyên, không dữ liệu thật/Cloud chỉ qua Mask. |
| CD-058, CD-070 mục 1, CD-075 (mục 1 MTQ làm lại, mục 2 pháp nhân ra khỏi Core), CD-080 + `docs/47-core/chuan/DU-THAO-CHUOI-ENGINE-v1.md` câu C3-4 | Giao diện song song; vị trí sau đóng gói; MTQ sắp theo vai × module; chuỗi OCR → trích do Core điều phối, đầu vào trích mang loại + phiên bản danh mục. |
| TL 41 (`..\41-crm-g-giao-ket-va-engine-trich-theo-loai-hop-dong.md`) §4 | E1 danh mục theo loại, E2 quy tắc logic theo loại ("hành vi XD không đổi"), E3 tham số dạng bảng, E4 output kèm loại. |
| TL 44 (`..\44-bo-tham-so-hop-dong-mua-theo-loai.md`) | 5 loại mua (MUA_HH, DV, DV_KY, THUE_TS, DV_1L, NHAP_KHAU) cùng 10 cột; "cùng mã = cùng nghĩa ở mọi loại"; danh mục nháp ở `THIET-KE-MODULE-DE-CHOT-2026-10-20\tham-so-hop-dong\`. |
| TRICH-2b (`docs/47-core/g2/KE-HOACH-LAT-G2-G3.md:118`, `docs/47-core/engine/GIAO-ENGINE-2.md:82`) | Danh mục theo loại; "thiếu/sai loại không fallback XD". Kế hoạch này **thay** TRICH-2b. |
| Mã đã có (tái dùng, không viết lại) | Bản vá E1-MUA cũ `tools/source6_g5_e5/trich_xuat/{danh_muc,logic}.py` (sổ catalog theo loại có SHA, chuỗi phiên bản qua nhật ký, quy tắc L2/L3/L5 cho loại mua); `engines/e_trich_xuat/do_chinh_xac.py` (chấm theo `compare` gốc); `review_xaydung/tests/mau_gia_lap.py` (hợp đồng XD giả lập + đáp án giả). |

**Mâu thuẫn đã thấy, theo bản mới hơn:** TL 44 §7 (20/10) chốt "kế toán tổng hợp sửa danh mục có hiệu lực ngay, không qua duyệt". CD-072 (05/11) yêu cầu **chạy thử trước, người có quyền mới Kích hoạt**. Kế hoạch theo CD-072.

**Ngoài phạm vi:** trích tham số dạng bảng (`trich.bang@1`, TRICH-2a — vẫn chờ); đo độ chính xác lớn (đã hủy); kiểm chéo Cloud (mặc định tắt); dùng hợp đồng thật để chạy thử; đổi CHECK `danh_muc.hop_dong.loai`.

---

## 2. Trả lời CD-071

### 2.1. (a) Pipeline gốc đọc theo nội dung hay theo vị trí/mẫu — dẫn chứng mã

Kết luận: **theo nội dung** (cấu trúc chữ "Điều/Khoản" + từ khoá + AI + kiểm trích dẫn nguyên văn). Không có toạ độ trang, số dòng cố định, tên style Word hay ô bảng cố định nào trong 9 bước.

| Bước gốc | Cách làm | Dẫn chứng (nguồn gốc `review_xaydung\trich_xuat\…`; engine tương ứng ở `src/kho_tri_thuc/engines/e_trich_xuat/…`) |
|---|---|---|
| 1. Đọc file | Đọc XML của DOCX, **giữ số Điều/Khoản đánh tự động** của Word, chấp nhận sửa đổi theo dõi | `doc_hop_dong.py:233–274` (`Numbering.label` dựng lại số tự động), `:296` `read_docx`; engine bọc ở `docx.py:47–61` (chỉ DOCX, chặn COM) |
| 2. Tách Điều/Khoản | Tách theo dòng bắt đầu bằng `Điều N` / `ĐIỀU N` / `Article N`; Khoản theo số dạng `5.3` | `doc_hop_dong.py:371` (`ART`), `:374–389` (`split_articles`); `cau_truc.py:12` (`KHOAN`), `:15–45` (`build_structure`) |
| 2'. Không có "Điều N" | Tự chia đoạn ~3.000 ký tự, vị trí ghi "Đoạn k", có cảnh báo | `doc_hop_dong.py:293` (`CHUNK_CHARS`), `:487` (`chunks = [] if nums else chunk_text(text)`), `:491–495` (cảnh báo); `cau_truc.py:24–28` |
| 3. Dò vị trí | Chấm điểm mọi Điều/Khoản theo **từ khoá** danh mục: tiêu đề ×10, `@mo_dau` +20, nội dung tối đa 5 → 3 vị trí tốt nhất | `cau_truc.py:86–117` (`locate`; `:104–105` `@mo_dau`, `:106` ×10, `:108–111` tối đa 5, `:112–113` lấy 3) |
| 3'. Từ khoá không khớp | AI tìm vị trí qua **mục lục** ID/Điều/Khoản/đầu nội dung | engine `quy_trinh.py:258–271` (`ai_tim_vi_tri`, `:116–136`) |
| 4. Hỏi AI theo nhóm | Gửi các đoạn ứng viên (≤ 14.000 ký tự) + mô tả tham số; nhóm theo cột Nhóm liên tiếp, tối đa 8 mã | engine `quy_trinh.py:276–318`, `:43–60` (`build_prompt`), `:29–30` (giới hạn) |
| 5. Tự kiểm trích dẫn | Trích dẫn phải có **nguyên văn** trong hợp đồng, số liệu của giá trị phải nằm trong trích dẫn, Điều/Khoản thuộc đoạn đã gửi | `kiem_tra.py:97–127` (`check`) |
| 6. Rà lại ô vàng | Quét **toàn bộ** hợp đồng theo đoạn cho tham số chưa chắc; nhiều giá trị khác nhau → ô vàng liệt kê | engine `quy_trinh.py:139–221`, gọi ở `:326–328` |
| 7. Kiểm logic | L1, L4 theo danh mục; L2/L3/L5 theo mã TT-20/21/52/53/54 | `logic.py:70–77` (L1), `:79–97` (L2/L3), `:99–113` (L4 đọc `bat_buoc`/`loai_tru` từ danh mục), `:115–131` (L5) |
| 8. Kiểm chéo Cloud | Tắt trong engine | engine `quy_trinh.py:355–356` |
| 9. Xuất | Bảng tham số + phiếu đầu vào + JSON/Excel | engine `quy_trinh.py:372–400` |

### 2.2. Những chỗ phụ thuộc hình thức — mẫu khác sẽ làm giảm độ chính xác ở đâu

| # | Tình huống mẫu khác | Mã gây ra | Hậu quả | Có báo không |
|---|---|---|---|---|
| 1 | Không đánh "Điều N" (dùng "Mục I", "Phần 1", "Article I" số La Mã) | `doc_hop_dong.py:371` chỉ nhận `\d+` | Chia đoạn 3.000 ký tự; vị trí ghi "Đoạn k"; `@mo_dau` chỉ còn đoạn 1 | Có — cảnh báo phiếu đầu vào (`:491–493`) |
| 2 | Tiêu đề Điều **kết thúc bằng số** 1–3 chữ số (vd "Điều 5. Thanh toán đợt 2") | `doc_hop_dong.py:379` coi là dòng mục lục | Điều đó bị gộp vào Điều trước; vị trí ghi sai số Điều, nội dung vẫn có | Một phần — "Thiếu Điều số" (`:489–490`) nếu tạo lỗ |
| 3 | Khoản đánh "1.", "a)", "-" thay vì "5.3" | `cau_truc.py:12`, `:37` (số Khoản phải bắt đầu bằng số Điều) | Cả Điều thành một khối; Điều dài > 14.000 ký tự bị cắt khi gửi AI (`quy_trinh.py:51–52`) | Có — cảnh báo Khoản dài ở phiếu đầu vào |
| 4 | Dùng từ khác từ khoá (vd "ứng trước" thay "tạm ứng") | `cau_truc.py:86–117` | Không khớp → AI tìm qua mục lục (bước 3') → rà lại toàn hợp đồng (bước 6) | Ô vàng nếu không chắc |
| 5 | Thông tin các Bên đặt sau "Điều 1" | `cau_truc.py:104` (`@mo_dau` chỉ cho phần trước Điều 1) | Mất +20 điểm cho TC-xx; vẫn có điểm từ khoá | Ô vàng nếu sai |
| 6 | Bảng giá/tiến độ dạng ảnh scan trong phụ lục; bảng rất lớn | `doc_hop_dong.py:496–500` | Không đọc được ảnh; bảng lớn bị cắt | Có — cảnh báo |

Ngoài ra (riêng engine, không phải công cụ gốc): chỉ nhận **DOCX** (`docx.py:27–31`); `.doc` và PDF phải chuyển trước (PDF qua `e_ocr` theo chuỗi CD-080). Danh mục giữ **thứ tự dòng**: nhóm AI dựng từ cột Nhóm **liên tiếp** (`quy_trinh.py:277–280`), nên đổi thứ tự dòng trong Excel có thể đổi kết quả AI — màn so khác biệt phải báo "đổi thứ tự".

### 2.3. Cách lead thử (a) trên mẫu DEMO — không dùng hồ sơ thật mới

Bộ mẫu hiện có không có hợp đồng XD "mẫu khác" đã ẩn danh; chỉ có hợp đồng giả lập `review_xaydung\tests\mau_gia_lap.py` (tên/số hư cấu, kèm đáp án giả). Đề xuất lát **LHD-02** sinh **5 biến thể DEMO** từ cùng nội dung giả lập, mỗi biến thể chạm đúng một rủi ro ở 2.2:

| Biến thể | Thay đổi bố cục | Rủi ro thử |
|---|---|---|
| V0 | Nguyên mẫu giả lập | Nền |
| V1 | "ĐIỀU 1:" chữ hoa, Khoản "1.1." có dấu chấm cuối | #1 biến thể nhẹ, #3 |
| V2 | Không có "Điều N" — dùng "I., II., III." | #1 |
| V3 | Tiêu đề "Điều 5. Thanh toán đợt 2" | #2 |
| V4 | Thông tin các Bên chuyển xuống sau Điều 1; đổi "tạm ứng" thành "ứng trước" | #4, #5 |

Lead chạy bước 1–3 (tất định, không AI) bằng test, rồi chạy trọn 9 bước với Local AI trên máy, **báo số đúng/sai từng mã tham số so với đáp án giả**, không gửi nội dung lên Cloud. Báo cáo cho Anh: bảng 37 mã × 5 biến thể, ô = Đúng / Sai / Ô vàng.

### 2.4. (b) Ước lượng việc cho loại hợp đồng khác

| Hạng mục | Việc | Số lát (mục 7) |
|---|---|---|
| Sổ loại + phiên bản danh mục + kích hoạt (Core) | 1 migration, 1 bộ kiểm Excel thuần, 1 nhóm route | 4 (C1–C4) |
| Engine nhận loại + phiên bản | Bỏ 9 chỗ khoá cứng (mục 3), câu hỏi AI theo tên loại, logic theo loại, Y-xx, manifest/contract | 6 (E1–E6) |
| Giao diện (dữ liệu giả trước) | 3 màn | 2 (U1a, U1b) |
| Công cụ thử | Kiểm nhanh, biến thể DEMO XD, hợp đồng DEMO dịch vụ | 3 (01, 02, 02b) |
| **Cộng** | | **15 lát + 3 bước lead** |

**Sau khi xong, thêm một loại = không sửa mã:** khoảng nửa ngày công người nghiệp vụ (soạn/tải Excel, chạy thử, kích hoạt). Danh mục nháp 5 loại mua đã có (TL 44).

**Rủi ro khi sang loại khác:**
1. Câu hỏi AI đang ghi cứng "hợp đồng xây dựng" (`ai_chung.py:40–41`, câu gốc `:73–76`) — phải theo tên loại, riêng XD giữ nguyên từng chữ.
2. Tham số dạng bảng (lịch đợt, bảng hàng hóa TT-05 ở MUA_HH/NHAP_KHAU/DV) chưa trích được (TRICH-2a chờ) → chỉ ra dạng chữ, thường thành ô vàng.
3. Hợp đồng nhập khẩu tiếng Anh: `Article N` được nhận, nhưng từ khoá danh mục là tiếng Việt → phần lớn đi đường AI tìm qua mục lục, chậm và nhiều ô vàng hơn.
4. Bộ đọc danh mục gốc **mượn mặc định XD** khi thiếu cột (`danh_muc.py:168–182`: mức quan trọng và từ khoá L4 lấy từ `MAC_DINH` của XD theo mã) và cho ô Mức trống thành 0/2 (`:110–115`) → import phải **bắt buộc đủ 10 cột, không ô Mức trống** để loại mới không ngầm dùng giá trị của XD.
5. Từ khoá và mức quan trọng chỉ ổn định sau khi chạy trên hợp đồng thật có đáp án — ngoài phạm vi CD-071 (không đo lớn); chạy thử DEMO chỉ chứng minh luồng chạy, không chứng minh độ chính xác.

**Cần Anh cung cấp:** (1) loại ưu tiên; (2) khi muốn biết độ chính xác thật của loại đó: 2–3 hợp đồng đã ký mỗi loại + đáp án do kế toán điền — chạy trên máy, chỉ báo số, ngoài luồng DEMO.

---

## 3. Hiện trạng mã: các chỗ khoá cứng XD cần gỡ

Vị trí hiện tại `src/kho_tri_thuc/engines/e_trich_xuat/` → sau G3-GOI là `engines/e_trich_xuat/` cùng tên tệp.

| Tệp:dòng hiện tại | Khoá cứng | Đường chạy |
|---|---|---|
| `tich_hop.py:54–55`, `:97–114` (`danh_muc_xd`, ép đúng 37 mã), `:125–126`, `:142`, `:249`, `:485` (logic không biết loại), `:699–704`, `:727–728` | `DANH_MUC_ID="XD"`, SHA cố định, `TRICH_DANH_MUC_KHONG_HO_TRO` | **Đường đang chạy** (manifest `diem_vao = tich_hop.chay_noi`) |
| `tham_so.py:34–46`, `:87–88`, `:104` | Như trên | Đường TRICH-1a cũ |
| `quy_trinh.py:96`, `:332` | `self.params = danh_muc_xd()`; logic không truyền loại | Đường TRICH-1b cũ |
| `chay.py:22`, `:36`, `:39–41` | Như trên | Đường TRICH-3a cũ |
| `ai_chung.py:40–41` | "Trích tham số hợp đồng xây dựng" | Chung |
| `engine.json` `ten` | "Trích 37 tham số XD từ DOCX…" | Manifest |
| `do_chinh_xac.py:25`, `:33` | Danh mục XD | Công cụ chấm |

`tich_hop.py` là bản chép của `quy_trinh/tham_so/chay` (`NGUON_CHEP`, `:39–48`). Kế hoạch chỉ đổi **đường đang chạy** (`tich_hop.py`) để nhận loại; ba tệp đường cũ giữ XD-only và vẫn báo `TRICH_DANH_MUC_KHONG_HO_TRO` với loại khác (không sửa ba nơi cùng một thay đổi). `tich_hop.danh_muc_xd` đã đọc **đúng 10 ô mỗi dòng, không mượn mặc định** (`:103–110`) — đây là nền cho bộ đọc chặt dùng chung (mục 4.8).

Hợp đồng đầu vào hiện đã mang `loai_hop_dong`, `danh_muc_id`, `danh_muc_sha256` (`tich_hop.py:585–587`), và contract kết quả `tham_so.v1` đã bắt buộc ba trường này (`core/contract/ky_thuat.json:410–430`) → **không phải đổi contract kết quả**.

---

## 4. Thiết kế dữ liệu

### 4.1. Nguyên tắc

- Tái dùng bảng Core có sẵn; chỉ thêm **1 bảng** chỉ-ghi-thêm cho phiên bản danh mục. Không thêm cột vào bảng cũ.
- **Một bản** bộ đọc/kiểm danh mục, đặt ở SDK, Core và engine cùng gọi (CD-019; Core không import mã engine — G3-GOI §3.3).
- Phiên bản = **mã băm SHA-256 của bytes tệp Excel** (giữ tương thích XD `05846a2a…` và trường `danh_muc_sha256`); kèm **mã băm nội dung** (JSON chuẩn của 10 cột theo thứ tự dòng) để nhận ra "lưu lại tệp nhưng không đổi nội dung".
- Sổ loại hợp đồng **dùng chung toàn hệ thống**, không theo pháp nhân (đề xuất, câu Q4) — phù hợp CD-075 mục 2. Chỉ dữ liệu chạy thử nằm trong pháp nhân DEMO (`la_demo`, CD-044).

### 4.2. Sổ loại hợp đồng → cấu hình engine (không bảng mới)

Dùng `loi.ho_so_chay_engine.cau_hinh` của `e_trich_xuat` (`core/sql/038_ho_so_chay_engine.sql:55–70`): đã chỉ-ghi-thêm theo `phien_ban_dong`, có lược đồ ghim mã băm (`ho_so_chay_schema`), có bảng kiểm toán thay đổi (`ho_so_chay_kiem_toan`, `:80–91`). Đây đúng là "lựa chọn bên trong engine" của CD-045 mục 3.

```json
{"loai_hop_dong": {
  "XD": {"ten": "Hợp đồng xây dựng", "mo_ta": "…", "trang_thai": "dang_dung",
         "danh_muc_dang_dung": "05846a2a…", "nhom_danh_muc_hop_dong": "XAY_DUNG",
         "co_kiem_logic_rieng": true},
  "DV":  {"ten": "Hợp đồng dịch vụ", "mo_ta": "…", "trang_thai": "nhap",
         "danh_muc_dang_dung": null, "nhom_danh_muc_hop_dong": "DICH_VU",
         "co_kiem_logic_rieng": false}}}
```

- Mã loại: `^[A-Z][A-Z0-9_]{1,15}$`. Trạng thái: `nhap` / `dang_dung` / `ngung`. Không xoá loại; "Ngừng" thì module không gửi mới, kết quả cũ vẫn xem được.
- `nhom_danh_muc_hop_dong`: ánh xạ sang CHECK có sẵn của `danh_muc.hop_dong.loai` (`core/sql/012_danh_muc.sql:94`: XAY_DUNG/THUE_DAT/BAN_NHA/VAY/MUA/DICH_VU/KHAC) — vì mã loại của engine (XD, DV, MUA_HH…) khác bộ mã đó; không đổi CHECK đợt này.
- Đổi tên/trạng thái/con trỏ phiên bản = một dòng `phien_ban_dong` mới qua hàm SQL có sẵn, ghi kiểm toán. Việc đang chạy giữ phiên bản đã ghim lúc gửi.
- Nếu lead thấy đổi `cau_hinh` làm engine phải nạp lại hồ sơ chạy (drain) quá nặng cho thao tác nghiệp vụ, phương án dự phòng: thêm bảng nhỏ `loi.trich_loai_hop_dong`. Lead chốt ở lát C1 sau khi đọc `ho_so_chay.py` (không đổi kế hoạch lát).

### 4.3. Phiên bản danh mục → 1 bảng mới chỉ-ghi-thêm

Đề xuất tên chung để engine khác (mẫu Mask, mẫu OCR) dùng lại: `loi.engine_tep_cau_hinh`.

| Cột | Nghĩa |
|---|---|
| `id` uuid | Khoá |
| `ma_engine` text | `e_trich_xuat` |
| `nhom` text | `danh_muc_tham_so` |
| `khoa` text | Mã loại hợp đồng |
| `so_phien_ban` integer | 1, 2, 3… theo `(ma_engine, nhom, khoa)` |
| `ma_bam` text | SHA-256 bytes Excel (`UNIQUE(ma_engine, nhom, khoa, ma_bam)`) |
| `ma_bam_noi_dung` text | SHA-256 JSON chuẩn 10 cột |
| `tep_id` uuid | Tệp Excel trong kho tệp Core (4.4) |
| `tom_tat` jsonb | Số tham số, số đang dùng, số mức 3, số "luôn hỏi", có sheet quy tắc hay không — **không** chứa nội dung mô tả |
| `tao_boi`, `tao_luc`, `kiem_toan_id` | Người nạp, lúc nạp, dòng nhật ký kiểm toán |

Trạng thái hiển thị **suy ra**, không lưu cột trạng thái: *Đang dùng* = con trỏ ở 4.2 trỏ tới; *Đã chạy thử đạt* = có ≥ 3 việc chạy thử XONG với `ma_bam` này (4.5); *Hết hiệu lực* = từng là con trỏ, nay không; còn lại *Nháp*. RLS + REVOKE theo mẫu bảng Core (`038:92–100`).

### 4.4. Tệp Excel → kho tệp Core

Lưu bytes bằng `core/tep.py` (`KhoTep`, ghi bất biến, mã băm), không lưu Excel trong CSDL. Mẫu Excel trống tải từ màn là tệp sinh từ bộ đọc ở SDK (cùng 10 tiêu đề `HEADER` của gốc `danh_muc.py:24–25`, sheet `Danh_muc`, thêm sheet `Huong_dan` và sheet tùy chọn `Quy_tac`).

### 4.5. Chạy thử → hàng việc + kết quả có sẵn

- Mỗi hợp đồng mẫu = một việc trích bình thường trong `loi.hang_viec` (pháp nhân DEMO), đầu vào thêm cờ `chay_thu = true` + phiên bản nháp. Core chỉ cho cờ này khi người gửi có quyền SUA danh mục và tệp mẫu thuộc pháp nhân DEMO.
- Kết quả lưu như mọi kết quả engine (`loi_tai_lieu.ket_qua_xu_ly`, `core/sql/009_tai_lieu.sql:101–125`) — `tham_so.v1` đã có loại + mã băm.
- Hợp đồng mẫu: tệp DEMO trong pháp nhân DEMO, gắn nhãn "mẫu chạy thử loại X". Không có đường tải hợp đồng thật vào DEMO (CD-044). Bản ẩn danh qua Mask chỉ dùng được khi MASK-2/3 xong.

### 4.6. Kích hoạt

Hàm SQL `loi.trich_danh_muc_kich_hoat(loai, ma_bam, ly_do)` kiểm ở máy chủ, đủ cả mới đổi con trỏ:

1. Phiên bản thuộc đúng loại; loại không ở trạng thái Ngừng.
2. Có ≥ 3 việc chạy thử **XONG** (không lỗi engine) với đúng `ma_bam` này trong 30 ngày; số ô vàng không chặn (người duyệt tự đánh giá), nhưng hộp xác nhận hiện tổng số ô vàng.
3. Người bấm có quyền kích hoạt (4.7); lý do ≥ 10 ký tự.
4. Ghi một dòng `ho_so_chay_engine` mới + nhật ký kiểm toán (trước/sau, người, giờ, lý do, danh sách việc chạy thử làm căn cứ).
5. Kích hoạt lại một phiên bản từng "Đang dùng" (quay lui) không cần chạy thử lại.

**XD:** phiên bản 1 của XD được tạo sẵn bằng migration từ đúng bytes `DANH_MUC_THAM_SO.xlsx` đang ghim (`05846a2a…`), trạng thái Đang dùng, lý do "chuyển từ công cụ gốc, đã kiểm nhanh CD-071" — không cần chạy thử lại. Nạp XD phiên bản 2 về sau phải chạy thử như loại khác.

### 4.7. Quyền (MTQ)

CHECK hành động hiện chỉ có `XEM/LAP/SUA/KIEM/DUYET/HUY` (`core/sql/006_mtq.sql:54`) → không có `KICH_HOAT`. Đề xuất (câu Q5): đặt dưới Quản trị Core, không phải module:

| Hành động | Tên hiển thị | Cho phép |
|---|---|---|
| `CORE:DANH_MUC_TRICH:XEM` | Xem danh mục trích xuất | Xem sổ loại, phiên bản, kết quả chạy thử |
| `CORE:DANH_MUC_TRICH:SUA` | Sửa danh mục trích xuất | Thêm/sửa loại, import, gửi chạy thử |
| `CORE:DANH_MUC_TRICH:DUYET` | Kích hoạt danh mục trích xuất | Kích hoạt / quay lui |

Khi MTQ làm lại theo vai × module (CD-075 mục 1), ba hành động này thuộc ô "Quản trị Core → Danh mục trích xuất". Màn không xưng "Anh" (QĐ-20261104-02).

### 4.8. Quy tắc kiểm Excel khi import (Core kiểm, báo lỗi từng dòng tiếng Việt)

Bộ đọc chặt đặt ở SDK `src/kho_tri_thuc/sdk_core/danh_muc_tham_so.py`, nhận **danh sách dòng** (đọc bằng `xlsx_mini` — một bản, theo G3-GOI lát 04 đưa hàm thuần vào SDK). Với tệp XD `05846a2a…`, kết quả tham số phải **bằng đúng** `danh_muc_xd()` hiện tại (test bắt buộc).

| Kiểm | Lỗi hiển thị (ví dụ) |
|---|---|
| Tệp `.xlsx`, ≤ 2 MiB, không macro, có sheet `Danh_muc` (hoặc sheet đầu) | "Tệp không phải Excel .xlsx" |
| Dòng 1 đủ **10 cột** đúng tên (chấp nhận "khoá"/"khóa"), đúng thứ tự | "Thiếu cột 'Từ khoá loại trừ (L4)'" |
| Mã: không trống, dạng `^[A-Z]{2,3}-\d{2,3}$`, **không trùng**, không bắt đầu `Y-` (dành cho hỏi thêm) | "Dòng 12: mã TT-20 trùng dòng 9" |
| Mô tả cho AI: không trống, ≤ 1.000 ký tự | "Dòng 5: thiếu mô tả cho AI" |
| Nhóm: không trống | "Dòng 7: thiếu nhóm" |
| Từ khoá: tách bằng `;`, mỗi từ ≤ 60 ký tự; chỉ `@mo_dau` được dùng `@`, và chỉ ở cột Từ khoá tiêu đề | "Dòng 3: '@dau' không hợp lệ" |
| Dùng / Luôn hỏi Claude: chỉ `Có` / `Không` | "Dòng 8 cột Dùng: 'x' — ghi Có hoặc Không" |
| Mức quan trọng: số nguyên 0–3, **không để trống** | "Dòng 4: mức quan trọng phải 0–3" |
| Ô công thức, ô gộp ở vùng dữ liệu | "Dòng 6: ô công thức — ghi giá trị" |
| Ít nhất 1 tham số Dùng = Có | "Danh mục không có tham số nào đang dùng" |
| Cảnh báo (không chặn): > 60 tham số đang dùng; trùng mã băm nội dung với phiên bản có sẵn; tham số không có từ khoá nào (sẽ đi đường AI mục lục, chậm hơn) | — |
| Sheet `Quy_tac` (nếu có, câu Q3): kiểu quy tắc thuộc danh sách cho phép, mã tham số tồn tại | "Quy tắc 2: mã TT-99 không có trong danh mục" |

### 4.9. Khác biệt giữa hai phiên bản

So theo mã: **Thêm** / **Bỏ** / **Đổi** (cột nào: trước → sau) / **Đổi thứ tự** (cảnh báo vì ảnh hưởng nhóm hỏi AI, mục 2.2) / **Bật–tắt**. Hàm thuần trong cùng tệp SDK; màn hiện bảng khác biệt, không cần tải Excel.

### 4.10. Engine nhận loại + phiên bản

- **Đầu vào** theo câu C3-4 của `DU-THAO-CHUOI-ENGINE-v1.md` (đề xuất (a)): contract `yeu_cau_trich.v1` = tham chiếu tệp hợp đồng + `loai_hop_dong` + `ten_loai` + `danh_muc {tep_id, sha256}` + `tham_so_them` (tùy chọn); capability `trich.tham_so_hop_dong@2`, giữ `@1` (XD) tới khi gỡ. Contract mới cần Anh duyệt (CD-032).
- **Core** kiểm lúc tạo việc: `sha256` = phiên bản Đang dùng của loại (hoặc = phiên bản nháp khi `chay_thu`, có quyền). **Engine** đọc bytes Excel qua SDK, so `sha256`; lệch → `TRICH_DANH_MUC_SAI_HASH`. Loại chưa có phiên bản → `TRICH_DANH_MUC_KHONG_HO_TRO` (không mượn XD).
- **9 bước giữ nguyên**: chỉ thay nguồn `params` và tên loại trong câu hỏi; XD giữ nguyên **từng chữ** câu hỏi hiện tại.
- **Logic theo loại** — tệp mới `engines/e_trich_xuat/logic_loai.py`: XD gọi `vendor/review/logic.kiem_tra_logic` nguyên trạng (L1–L5, không đổi một byte); loại khác chỉ giữ L1 + L4 của chính hàm đó (lọc theo tiền tố "L2:/L3:/L5:" để không chép thuật toán) + quy tắc cấu hình (Q3). Không có quy tắc riêng → màn ghi "Chưa có kiểm logic riêng". Bộ quy tắc mua đã viết ở E1-MUA (`tools/source6_g5_e5/trich_xuat/logic.py:103–158`) dùng làm **mẫu tham khảo**, chỉ đưa vào khi Anh chọn.
- **Tham số hỏi thêm Y-01, Y-02…**: như gốc `danh_muc.py:195–202` — mỗi dòng "Nhóm | Mô tả", mức 2, không từ khoá → AI tự tìm vị trí. Giới hạn số dòng/lượt theo câu Q9. Không thuộc danh mục, không vào mã băm; `anh_xa_tham_so` (`tich_hop.py:117`) phải cho phép đúng các mã Y-xx đã khai trong đầu vào, `canh_bao` ghi "Tham số hỏi thêm một lượt, ngoài danh mục".
- **Truy vết**: kết quả `tham_so.v1` mang `loai_hop_dong`, `danh_muc_id` (= mã loại), `danh_muc_sha256`; phản hồi nguồn (`tich_hop.py:726–733`) thêm `so_phien_ban`, `tham_so_them`.

---

## 5. Màn hình (Quản trị Core → Danh mục trích xuất) — dữ liệu giả có nhãn trước

Chung: banner vàng "**Dữ liệu giả — chỉ để góp ý giao diện**" tới khi nối API; ngày dd/mm/yyyy; không hiện mã kỹ thuật (mã băm chỉ 8 ký tự trong "Chi tiết kỹ thuật"); xưng hô trung tính; nút không có quyền thì mờ kèm chú thích.

**5.1. Loại hợp đồng**
Bảng: Mã loại · Tên · Mô tả ngắn · Trạng thái (Nháp / Đang dùng / Ngừng) · Danh mục đang dùng ("Phiên bản 3 · 05/11/2026 · người kích hoạt") · Số tham số · Kiểm logic riêng (Có / "Chưa có kiểm logic riêng"). Nút: Thêm loại · Sửa tên/mô tả · Ngừng / Dùng lại · Xem phiên bản. Dòng XD có nhãn "Loại gốc — phải ra kết quả giống công cụ gốc". Dữ liệu giả: XD (Đang dùng, 37), DV (Nháp, 30), MUA_HH (Nháp, chưa có phiên bản).

**5.2. Import danh mục**
Chọn loại → "Tải mẫu Excel trống" → chọn tệp → "Kiểm tra". Kết quả: (i) lỗi: bảng Dòng · Cột · Lỗi · Cách sửa, nút Lưu bị khoá; (ii) đạt: tóm tắt (số tham số, số đang dùng, số mức 3, số "luôn hỏi") + bảng **Khác biệt so với bản đang dùng** (Thêm / Bỏ / Đổi trước → sau / Đổi thứ tự) → nút "Lưu thành phiên bản nháp" (không ghi đè bản đang dùng). Khung **Lịch sử phiên bản**: Số · Ngày nạp · Người nạp · Trạng thái · chọn 2 dòng → "So sánh".

**5.3. Chạy thử**
Chọn phiên bản nháp → chọn 3–5 hợp đồng mẫu (danh sách mẫu DEMO của loại, nhãn "DEMO") → "Gửi chạy thử" → dòng hàng chờ (CD-081: "Việc ở vị trí thứ N…"). Bảng kết quả: hàng = tham số, cột = hợp đồng mẫu; ô = giá trị ngắn, xanh (đạt) / vàng (cần xem) — bấm ô hiện lý do + trích dẫn; dòng cuối: số ô vàng mỗi hợp đồng; nếu loại đã có bản đang dùng chạy trên cùng mẫu thì đánh dấu ô **đổi kết quả**. Nút "**Kích hoạt phiên bản này**" (mờ khi chưa đủ 3 hợp đồng chạy xong hoặc không có quyền) → hộp xác nhận liệt kê khác biệt + tổng ô vàng + ô lý do.

Ảnh 3 màn gửi Anh ngay khi bản dữ liệu giả xong (lát U1a/U1b), kèm đường mở DEMO.

---

## 6. Kiểm nhanh "ra cùng kết quả" (CD-071) — cách đo, lead tự chạy trên máy

Không giao Codex (có thể là hồ sơ thật), không gửi nội dung lên Cloud, chỉ báo số. Kế hoạch này không chạy.

**6.1. Bộ hợp đồng.** `review_xaydung\du_lieu_mau\` có **2** tệp đáp án `DAP_AN_HD_*.tsv`, 1 tệp `.docx` và 1 tệp **`.doc`** (đếm tên tệp, không mở). Engine chỉ đọc DOCX → tệp `.doc` chuyển **một lần** bằng chính hàm `chuyen_docx` của công cụ gốc (Word, chấp nhận mọi sửa đổi) trên máy, ghi SHA tệp DOCX ra; cả công cụ gốc lẫn engine dùng **cùng** tệp DOCX đó để loại khác biệt do bộ chuyển. CD-071 nói "2–3": hiện chỉ đủ 2; hợp đồng thứ 3 (tùy chọn) dùng hợp đồng giả lập `mau_gia_lap` có đáp án giả (câu Q8).

**6.2. Điều kiện chung.** Cùng máy Local AI, cùng model (ghi tên + giờ), rà lại bật, Cloud tắt, danh mục XD `05846a2a…`, không tham số hỏi thêm. Kết quả ghi vào `var\kiem-nhanh-trich\<ngày>\` (ngoài git).

**6.3. Các bước.**
1. Ghi SHA tệp hợp đồng, tệp đáp án, nguồn gốc (`quy_trinh.py`, `danh_muc.py`, `kiem_tra.py`) và engine.
2. Chạy công cụ gốc (`python -m trich_xuat` trong `review_xaydung`) → `*_KET_QUA.json`. Nếu Anh xác nhận kết quả cũ "đã đúng" cùng model còn giữ, có thể dùng lại, ghi rõ ngày chạy.
3. Chạy engine (đường `BackendTrichXuat` trong `tich_hop.py`, cổng AI Local) bằng một kịch bản riêng của lead, cùng tệp DOCX → `phan-hoi-nguon.json`.
4. **Phần tất định** (không phụ thuộc AI): so `<tên>_cau_truc.json` (phiếu đầu vào, cấu trúc Điều/Khoản, vị trí 3 ứng viên mỗi tham số — ghi bởi `cau_truc.save`) giữa gốc và engine → phải **trùng 100%**.
5. **Phần AI**: chấm cả hai bằng `do_chinh_xac.py` (dùng nguyên `compare` của gốc) → mỗi mã: Đúng / Sai / Không có đáp án; và so engine với gốc bằng `giong_nhau` → Khớp / Khác.
6. **Báo số** (không in giá trị, trích dẫn, tên tệp hợp đồng): mỗi hợp đồng — số mã có đáp án; gốc Đúng *x*; engine Đúng *y*; engine khớp gốc *z*; danh sách **mã** lệch kèm mức quan trọng.

**6.4. Tiêu chí.** Đạt khi: bước 4 trùng 100%; *y ≥ x*; không có mã mức 3 mà gốc Đúng, engine Sai. Có lệch → chạy lại engine **một lần** cho hợp đồng đó (AI không tất định); vẫn lệch → **dừng, báo Anh** bảng mã + mức, không chỉnh danh mục để "đẹp số". Ghi chú khi báo: engine đã đổi cách hỏi AI qua cổng chung (4 thay đổi ghi ở `ai_chung.py:21–38`, `CAU_HOI_DOI`), nên lệch ở phần AI có thể do cổng, không do danh mục.

**6.5. "XD giống hệt" sau khi làm sổ loại (gate của lát E6).**
- **Tự động, DEMO**: test ghi–phát lại — AI giả trả lời cố định theo mã băm câu hỏi; chạy engine ở commit nền (trước LHD) trên 5 biến thể DEMO V0–V4, lưu "bản vàng" (câu hỏi gửi AI + phản hồi đầy đủ, bỏ trường giờ/thời lượng); chạy engine mới qua sổ (XD phiên bản 1) → **trùng từng byte**. Câu hỏi gửi AI của XD phải trùng từng chữ.
- **Trên máy**: lặp 6.3 cho engine mới → số Đúng/Khớp phải **bằng** lần đo trước khi đổi.

---

## 7. Lát dự kiến (≤ 3 tệp mỗi lát; N = tệp mới, S = tệp sửa)

Đường tắt: `E = engines/e_trich_xuat`, `C = src/kho_tri_thuc/core`, `S = src/kho_tri_thuc/sdk_core`, `T = tests`.

| Lát | Người làm | Nội dung | Tệp | Phụ thuộc | Ước tính |
|---|---|---|---|---|---|
| **LHD-00** | Lead | Kiểm nhanh CD-071 (mục 6.1–6.4) trên engine hiện tại | Không sửa mã | Mốc II xong; LHD-01 | 0,5 ngày |
| **LHD-01** | Codex | Kịch bản so/chấm chỉ in số (dùng `do_chinh_xac`, `giong_nhau`, so `_cau_truc.json`); test trên hợp đồng giả lập | N `tools/kiem_nhanh_trich.py`, N `T/test_kiem_nhanh_trich.py` | — | 0,5 |
| **LHD-02** | Codex | 5 biến thể DEMO XD (mục 2.3) + test bước 1–3 tất định (số tham số có vị trí, cảnh báo phiếu) | N `T/fixtures/trich_bien_the_xd.py`, N `T/test_trich_bien_the_xd.py` | — | 0,5 |
| **LHD-02b** | Codex | 3 hợp đồng dịch vụ DEMO + đáp án giả cho chạy thử loại DV | N `T/fixtures/trich_mau_dv_demo.py`, N `T/test_trich_mau_dv_demo.py` | — | 0,5 |
| **LHD-U1a** | Worker Claude (Sonnet) | Màn Loại hợp đồng + Import danh mục, dữ liệu giả có nhãn; ô mới trong Quản trị Core | N `C/ui/danh_muc_trich_mau.js`, S `C/ui/quan_tri.js`, N `T/danh_muc_trich_mau.cjs` | Mốc II (tệp `quan_tri.js` dùng chung — giữ khoá) | 1 |
| **LHD-U1b** | Worker Claude (Sonnet) | Màn Chạy thử + hộp Kích hoạt, dữ liệu giả | S `C/ui/danh_muc_trich_mau.js`, S `T/danh_muc_trich_mau.cjs` | U1a | 0,5 |
| **LHD-E1** | Codex, review Opus | Bộ đọc/kiểm chặt danh mục + khác biệt + mẫu Excel trống, ở SDK; test: XD `05846a2a…` ra đúng `danh_muc_xd()`; lỗi từng dòng | N `S/danh_muc_tham_so.py`, N `T/test_lhd_e1_danh_muc.py` | G3-GOI 04 (xlsx_mini ở SDK) | 1 |
| **LHD-C1** | Codex, review Opus (quyền) | Migration: bảng `loi.engine_tep_cau_hinh`, hàm ghi phiên bản, hàm kích hoạt (mục 4.6), 3 hành động MTQ, seed XD phiên bản 1 | N `C/sql/1xx_danh_muc_trich.sql`, N `T/test_lhd_c1_pg.py` | E1 (định dạng tóm tắt) | 1 |
| **LHD-C2** | Codex, review Opus | Route: sổ loại, import (kho tệp → kiểm → ghi nháp), lịch sử/so sánh, tải mẫu, gửi chạy thử, kích hoạt | N `C/routes_danh_muc_trich.py`, S `C/ung_dung.py` (đăng ký route), N `T/test_lhd_c2_routes.py` | C1 | 1 |
| **LHD-C3** | Codex | Core dựng đầu vào trích: ghim phiên bản Đang dùng / nháp khi chạy thử; từ chối loại chưa kích hoạt | S `C/dich_vu_engine.py` (hoặc nơi dựng đầu vào chuỗi CE — lead chốt), N `T/test_lhd_c3_ghim.py` | C1; CE (chuỗi CD-080) | 0,5 |
| **LHD-C4** | Worker Claude (Sonnet) | Nối 3 màn vào API thật, bỏ dữ liệu giả, ảnh từng màn | S `C/ui/danh_muc_trich_mau.js`, S `T/danh_muc_trich_mau.cjs` | U1b, C2 | 0,5 |
| **LHD-E2** | Codex, review Opus | Engine nhận loại + phiên bản (đường `chay_noi`): đọc Excel qua SDK, kiểm mã băm; câu hỏi AI theo tên loại (XD nguyên chữ) | S `E/tich_hop.py`, S `E/ai_chung.py`, N `T/test_lhd_e2_loai.py` | G3-GOI 31–37, E1 | 1 |
| **LHD-E3** | Codex | Logic theo loại (mục 4.10) + quy tắc cấu hình nếu Q3 chọn (a) | N `E/logic_loai.py`, S `E/tich_hop.py`, N `T/test_lhd_e3_logic.py` | E2 | 0,5 |
| **LHD-E4** | Codex | Tham số hỏi thêm Y-xx | S `E/tich_hop.py`, N `T/test_lhd_e4_hoi_them.py` | E2 | 0,5 |
| **LHD-E5** | Codex | Manifest `@2` + contract `yeu_cau_trich.v1` (bản phân phối) + ví dụ DEMO | S `E/engine.json`, S `E/contract/schemas.json`, S `E/contract/vi_du.json` | E2; Anh duyệt C3-4 | 0,5 |
| **LHD-E6** | Codex, review Opus | Gate "XD giống hệt" ghi–phát lại (mục 6.5) | N `T/test_lhd_xd_giong_het.py`, N `T/fixtures/trich_ban_vang_xd.json` (lead sinh ở commit nền) | E2–E4, LHD-02 | 0,5 |
| **LHD-N1** | Lead | Lặp kiểm nhanh 6.3 trên engine mới; số phải bằng LHD-00 | Không sửa mã | E6 | 0,5 |
| **LHD-N2** | Lead | Thử trọn trên Core thử 8796 (DEMO): XD chạy như cũ; import danh mục DV (bản nháp TL 44) → chạy thử 3 hợp đồng DV DEMO → kích hoạt; ảnh 3 màn + Hàng việc | Không sửa mã | C4, E5, 02b | 0,5 |

Song song được ngay sau Mốc II: 01, 02, 02b, U1a → U1b. Phần Core (E1 → C1 → C2/C3 → C4) chạy song song với G3-GOI. Phần engine (E2 → E3/E4/E5 → E6) chờ G3-GOI xong nhóm trích 31–37. Đường găng: G3-GOI trích → E2 → E6 → N1.

Cổng gộp mỗi lát như quy định repo: không thêm mã lỗi so nền, không tăng skip, kiểm chữ Việt không thành `?`, route mới phải đăng ký + test `tao_ung_dung`; lát quyền/kích hoạt review Opus (CD-049).

---

## 8. Ngày dự kiến (ước tính)

| Mốc | Ngày ước tính | Điều kiện |
|---|---|---|
| Kiểm nhanh CD-071 + báo số (LHD-00) | 06/11 | Mốc II xong, Anh trả lời Q8 |
| Ảnh 3 màn dữ liệu giả (U1a, U1b) | 06/11 | Có chỗ trống worker Claude |
| Biến thể DEMO + kết quả câu (a) | 06–07/11 | LHD-02 gộp, máy Local AI rảnh |
| Phần Core xong (E1, C1–C4) | 08/11 | Anh trả lời Q2, Q4, Q5; C3 cần khung chuỗi CE |
| Phần engine xong (E2–E6) | 2–3 ngày sau khi G3-GOI gộp lát 37 (dự kiến khoảng 10–11/11) | G3-GOI; Anh duyệt C3-4 |
| Thử DEMO trọn luồng (N1, N2) | khoảng 12/11 | Như trên |

Ghi vào TRANG-THAI: "CD-072: 15 lát + 3 bước lead; dự kiến ~12/11 (ước tính, phụ thuộc G3-GOI trích)".

---

## 9. Câu chọn cho Anh

**Q1. Loại hợp đồng làm đầu tiên sau XD?**
- ☑ (a) **DV — dịch vụ bản gọn** (30 mã, đã có danh mục nháp và đáp án nháp, TL 44 §6)
- ☐ (b) MUA_HH — mua hàng hóa trong nước
- ☐ (c) THUE_TS — thuê tài sản
- ☐ (d) NHAP_KHAU — nhập khẩu (rủi ro hợp đồng tiếng Anh, bảng hàng hóa)

**Q2. Ai được kích hoạt phiên bản danh mục?**
- ☑ (a) Người có quyền Kích hoạt, **kể cả chính người đã nạp** (có nhật ký; Admin muốn tách thì cấp quyền cho hai người khác nhau)
- ☐ (b) Bắt buộc người khác người nạp (hai người)

**Q3. Kiểm logic cho loại mới?**
- ☑ (a) Sheet `Quy_tac` tùy chọn trong cùng tệp Excel, 3 kiểu đơn giản: tổng các tỷ lệ = / ≤ 100%; ngày A ≤ ngày B; có A thì phải có B — ghim cùng mã băm danh mục
- ☐ (b) Đợt này để trống, màn ghi "Chưa có kiểm logic riêng"
- ☐ (c) Dùng bộ quy tắc mua/dịch vụ đã viết ở E1-MUA (tổng lịch ≤ 100%, cọc không nằm trong lịch, phạt × ngày ≤ 8%, cần thời hạn hợp đồng)

**Q4. Sổ loại hợp đồng?**
- ☑ (a) Dùng chung toàn hệ thống (không theo pháp nhân)
- ☐ (b) Theo từng pháp nhân

**Q5. Quyền danh mục trích xuất đặt ở đâu?**
- ☑ (a) Quản trị Core → "Danh mục trích xuất" (Xem / Sửa / Kích hoạt)
- ☐ (b) Trong từng module dùng trích xuất (CRM…)

**Q6. Số hợp đồng chạy thử tối thiểu trước khi kích hoạt?**
- ☑ (a) 3
- ☐ (b) 5

**Q7. Đầu vào engine trích (câu C3-4 của tài liệu chuỗi engine)?**
- ☑ (a) Contract mới `yeu_cau_trich.v1` (tệp + loại + phiên bản danh mục), engine `@2`, giữ `@1` cho XD
- ☐ (b) Mỗi loại một chuỗi riêng, không contract mới

**Q8. Kiểm nhanh CD-071: hiện chỉ có 2 hợp đồng có đáp án (1 tệp `.doc`)?**
- ☑ (a) Kiểm 2 hợp đồng này (tệp `.doc` chuyển DOCX bằng chính công cụ gốc) + 1 hợp đồng giả lập có đáp án giả
- ☐ (b) Anh gửi thêm 1 hợp đồng XD có đáp án

**Q9. Tham số hỏi thêm một lượt (Y-01…)?**
- ☑ (a) Tối đa 5 dòng mỗi lượt, người gửi việc trong module tự thêm
- ☐ (b) Tối đa 10 dòng

---

## 10. Rủi ro và điều không làm

| Rủi ro | Cách giữ |
|---|---|
| Đổi XD làm lệch kết quả | XD đi đường vendor nguyên trạng; gate ghi–phát lại trùng từng byte (E6) + lặp kiểm nhanh (N1) |
| Bộ đọc Core và engine hiểu Excel khác nhau | Một bộ đọc ở SDK; test XD ra đúng tham số hiện tại |
| Loại mới ngầm mượn mặc định XD | Bắt buộc đủ 10 cột, không ô Mức trống; không fallback XD |
| `cau_hinh` engine đổi làm nạp lại engine | Lead đánh giá ở C1; dự phòng bảng sổ loại riêng (4.2) |
| Chạy thử tốn máy AI | Hàng chờ CD-081, mỗi lần tối đa 5 hợp đồng, một việc đồng thời theo manifest |
| Danh mục nháp TL 44 chưa qua hợp đồng thật | Màn ghi rõ "chưa đo độ chính xác"; chạy thử DEMO chỉ kiểm luồng |

**Không làm:** trích bảng (TRICH-2a); đo độ chính xác lớn; Cloud; hợp đồng thật trong DEMO; sửa nguồn `review_xaydung`; sửa vendor review trong engine; đổi CHECK `danh_muc.hop_dong.loai`; xoá phiên bản/loại (chỉ Ngừng / Hết hiệu lực).

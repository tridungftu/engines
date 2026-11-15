# DC-1 — Contract hồ sơ và khảo sát nguồn

Ngày 15/11/2026 · PR: **chờ lead mở** · 3 giờ **ƯỚC TÍNH**.

DC-Q17 và DC-Q01…Q17 đã được Anh duyệt theo cột đề xuất, căn cứ
`_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` §2 dòng 4, 6. Nhãn
“chưa duyệt” trong phần minh họa DC-P là lịch sử. API v1/SDK 2.0 giữ nguyên.
DC-1 chỉ chốt contract, khảo sát và kiểm DEMO; chưa viết handler nhận cặp,
so chữ, detector, AI hoặc xuất báo cáo. Test khung `CHUA_LAM` được giữ.

## 1. Phạm vi schema và manifest

Đúng **5 tệp schema thêm trong lát**: `_chung/contract/ho_so_doi_chieu.schema.json`,
bản chép trong `goi/e_doi_chieu/`, và ba bản chép `van_ban_tai_lieu`,
`yeu_cau_ai`, `tra_loi_ai` tại cùng thư mục gói. Schema cấu hình DC-0 đã có
không tính vào năm tệp thêm. Bốn schema trong gói so SHA-256 với nguồn chung
sau CRLF→LF; hai mẫu NGAN-0 cũng giữ nguyên và được test so băm LF.
Không sửa ba schema chung đã khóa hay văn bản loại dữ liệu chung.

Manifest đăng ký đúng tên bốn loại được duyệt; chỉ giữ năng lực khung
`doi_chieu.doc_docx@1`. `nhan_cap` và các năng lực tiếp theo chưa đăng ký chạy.
`chay_thu_demo=[]`: **0 demo nghiệp vụ**, không có thành công giả.
SDK 2.0 kiểm phong bì loại riêng theo mã, không tự kiểm JSON Schema sâu.
Test schema nằm ngoài gói, dùng bộ kiểm tập con bằng thư viện chuẩn; không
phải chứng nhận đầy đủ metaschema draft 2020-12, không tải schema từ mạng.

## 2. Đầu vào `doi_chieu.nhan_cap@1` — thiết kế cho DC-3

Một phong bì API chuẩn: `{"loai":"tep","tep":{tep_id,ten,mime,kich_thuoc}}`.
`mime=application/json`. `tham_so.bam_yeu_cau` bắt buộc, đúng `sha256:` +
64 hex, trên **bytes nguyên tệp JSON**; không hash lại bản JSON đã parse.
Tệp yêu cầu không chứa quyền tự khai, đường máy, URL hoặc bytes base64.

| Trường JSON | Required / kiểu / giới hạn / ý nghĩa |
|---|---|
| `phien_ban` | Có, integer const `1` |
| `ma_cap` | Có, string 1…200 ký tự; chỉ mã tương quan, không cấp quyền |
| `nguon` | Có, object đúng hai khóa `word`, `ban_ky`; mỗi bên `{tep, phien_ban, bam}` |
| `van_ban` | Có, object đúng `word`, `ban_ky`; mỗi bên `{tep,bam}` trỏ JSON **nguyên phong bì** `van_ban_tai_lieu` |
| `anh_trang` | Có, array 0…60 phần tử `{so,tep,bam}` của bản ký; `so` integer 1…60, duy nhất và phủ đủ trang bản ký trước quét ảnh |
| `ban_chuan_phan_trang` | Có, `null` nếu chưa có; nếu có `{tep,bam,phien_ban}` trỏ PDF render Word và thêm `anh_trang_word` (định dạng như trên, đủ trang render); không đoán từ số ngắt trang DOCX |
| `bo_quy_tac` | Có, `{tep,bam,phien_ban}` trỏ JSON snapshot bộ đã duyệt; ghim từ điển, vùng bảo vệ, chính sách kiểm, ngưỡng và nguồn phê duyệt |
| `kiem_dau_vao` | Có, `{word_da_chot:boolean, ocr_day_du:boolean, canh_bao:string[]}`; Core phải cung cấp provenance xác thực của kết quả kiểm, không tin boolean do caller tùy ý viết |
| `bang_chung_ocr_lai` | Có, array 0…10000 tham chiếu `{tep,bam}`; có thể rỗng ở đầu; mỗi JSON bằng chứng phải ghim `ma_cap`, mã điểm, nguồn trang, hộp, băm ảnh, bộ đọc/phiên bản và văn bản thực |

Không nhận khóa ngoài bảng ở JSON yêu cầu v1. Đây là đặc tả đầu vào,
**không tạo schema thứ sáu**. `anh_trang_word` chỉ có khi render khác null.
Mỗi `tep` đúng bốn trường API, `tep_id` 1…200, `ten` 1…255 ký tự,
`mime` đúng loại thực, `kich_thuoc` integer dương. `phien_ban` của tham chiếu
là string 1…100, mọi `bam` dài đúng 71 ký tự. Nguồn Word MIME DOCX,
bản ký PDF, văn bản/bộ/bằng chứng JSON, ảnh PNG/JPEG; kiểm chữ ký định dạng
và giải mã thực ở lát xử lý, tên/MIME không đủ chứng minh nội dung.

Tệp JSON yêu cầu ≤1 MiB, mỗi tệp con ≤20 MiB, tổng bytes đọc ≤128 MiB/việc;
không đọc lặp để lách ngân sách. ≤60 trang bản ký, ≤20 triệu pixel/ảnh;
mỗi bản ≤500.000 ký tự và tổng ≤1.000.000. Snapshot ≤20 MiB, ≤10.000 điểm.
JSON UTF-8 nghiêm: từ chối khóa trùng, NaN/Infinity, surrogate lẻ và cây quá
sâu (trần an toàn triển khai 64 mức); không cắt đuôi để đạt trần.

**Nợ SDK cần áp dụng khi khai nhan_cap:** `gioi_han.tep_toi_da_mib=20`,
`mime=["application/json"]`, `thoi_han_giay=120`; engine tự kiểm tệp yêu cầu
≤1 MiB. Phiếu DC-P đề xuất trần 1 MiB cho bước nhưng SDK 2.0 dùng **cùng
trần khi mo_tep cho tệp con**, nên 1 MiB sẽ chặn DOCX/PDF/ảnh hợp lệ.
Đây là điều chỉnh kỹ thuật cần lead theo dõi C-DC-02/06, không nâng trần JSON.

## 3. Đầu ra `ho_so_doi_chieu` và snapshot

Schema nguồn là hợp đồng phong bì, required ở mọi object được ghi ngay trong
schema; cấm trường thừa để tránh nhét toàn văn/ảnh/prompt/quyền vào phong bì.
`phien_ban=1`; phong bì UTF-8 ≤64 KiB (Python kiểm bytes).

| Trường required trong payload | Kiểu / enum / giới hạn |
|---|---|
| `phien_ban`, `ma_cap` | Integer const 1; string 1…200 |
| `giai_doan` | `da_nhan`, `da_so`, `da_quet_anh`, `cho_ai`, `da_hau_kiem`, `da_tong_hop` |
| `nguon.word`, `nguon.ban_ky` | Mỗi bên đúng `{tep_id,phien_ban,bam}`; metadata đầy đủ ở snapshot, khớp đầu vào |
| `ho_so`, `bam_ho_so` | Tệp API `application/json`, 1…20 MiB; SHA-256 bytes snapshot |
| `bam_bo_quy_tac`, `phien_ban_engine` | Băm bộ đã ghim; chuỗi `e_doi_chieu x.y.z` ≤100 ký tự |
| `tom_tat` | Required cả 7 trường của DC-P; 5 số điểm integer 0…10000 hoặc null; số vùng integer ≥0 hoặc null; số trang OCR kém integer 0…60 hoặc null |
| `kiem_tra` | Required `doc_hai_ban`, `so_van_ban`, `quy_tac_cung`, `trang`, `lech_dau`, `sua_tay`, `phan_loai_ai`; mỗi giá trị `dat/khong_dat/chua_kiem/khong_ap_dung` |
| `da_kiem_du`, `de_nghi_chan` | Boolean; chỉ đề nghị máy, không trạng thái hiệu lực/xác nhận |
| `ket_luan` | null trước tổng hợp; sau tổng hợp một trong `khop`, `khop_co_thay_doi_hinh_thuc`, `can_xem`, `lech_nghiem_trong`, `chua_doi_chieu_duoc` |
| `canh_bao` | Array 0…100 câu, mỗi câu 1…1000 ký tự; quá trần từ chối, không lặng lẽ bỏ cảnh báo |

Snapshot JSON ở kho Core giữ required `phien_ban`, `ma_cap`, `giai_doan`,
`nguon`, `van_ban`, `anh_trang`, `ban_chuan_phan_trang`, `bo_quy_tac`,
`kiem_dau_vao`, `bang_chung_ocr_lai`, `phien_ban_engine`, `tom_tat`,
`kiem_tra`, `da_kiem_du`, `ket_luan`, `de_nghi_chan`, `canh_bao`,
và các phần sau (lúc chưa xử lý là null, khi đã kiểm không có mục là []):

| Phần snapshot | Dữ liệu phải giữ và quan hệ Python cần kiểm ở các lát sau |
|---|---|
| `chuan_hoa` | Nguyên văn mỗi nguồn bất biến; văn bản chuẩn hóa + map Unicode nửa mở `[bat_dau,ket_thuc)` về nguồn; giữ ô rỗng/gộp, không bỏ đuôi hay phần không căn được |
| `edit_script`, `diem_lech` | Tái dựng đủ hai văn bản; mã điểm ổn định duy nhất, phép thêm/xóa/thay/đảo; trích nguyên văn/offset/vị trí hai bên; vùng bảo vệ, quy tắc trúng, `muc_san`, mức cuối, lý do, nguồn, cờ còn chờ phân loại |
| `quet_anh`, `vung_sua_tay`, `trang_ocr_kem` | Tập trang thực sự đã quét; detector/phiên bản, băm cấu hình/ngưỡng đã đo, mẫu số tỷ lệ; mỗi vùng trỏ ảnh cắt thật + băm, trang/hộp trong hệ tọa độ nguồn. Không tự đọc chữ tay |
| `ai` | null khi không qua AI; nếu có giữ tác vụ, prompt/phiên bản/khuôn, ngữ cảnh AI chính xác và map trái/phải→nguồn, băm ngữ cảnh, tham chiếu/băm phản hồi Local; model không thay metadata |

Snapshot không chứa `bam_ho_so` của chính nó (tránh băm tự tham chiếu).
Không nhét nội dung nguồn vào ngăn engine; mỗi tệp nguồn/text có tham chiếu+băm
để tái lập, nguồn Word/PDF có phiên bản. Băm bytes nguồn khác băm UTF-8 văn bản.
Tiền dùng `{so,tien_te}` không float để so; ngày `YYYY-MM-DD` và phải kiểm ngày thật.

**Quan hệ ngoài khả năng schema, bắt buộc Python:**

1. C-DC-02 cấp quyền cho từng tệp con trước đọc; so kích thước/băm bytes thật,
   MIME thật, phiên bản và `van_ban_tai_lieu.bam_dau_vao` khớp nguồn gốc.
   Kiểm `so_trang` khớp danh sách trang, thứ tự/số trang duy nhất; ảnh phủ đúng
   từng trang bản ký, không lấy ảnh của cặp khác. Hộp hữu hạn, đúng đơn vị,
   `0≤x0<x1≤rong`, `0≤y0<y1≤cao`, map pt↔px phải có nguồn/DPI/phép xoay thật.
2. Phong bì khớp toàn bộ metadata/tóm tắt/trạng thái trong snapshot đã băm;
   snapshot bộ và mọi tham chiếu băm có thể mở lại trong cùng phạm vi Core.
   Schema chỉ kiểm hình dạng băm, **không chứng minh bytes hoặc quyền**.
3. `da_nhan` chỉ đã đọc hai bản; mọi số chưa đo null. `da_so` sau so + quy tắc;
   `da_quet_anh` sau quét đủ ảnh. `cho_ai` ghim snapshot trước AI;
   hậu kiểm chỉ từ phản hồi Local đúng snapshot để ra `da_hau_kiem`.
   `da_tong_hop` chỉ sau hậu kiểm hoặc nhánh Core bỏ qua AI có căn cứ không
   còn điểm chờ; xuất từ chối `da_nhan/cho_ai` và mọi điểm chưa phân loại.
   Không nhảy/lùi giai đoạn bằng nhãn caller hoặc nạp bộ quy tắc mới giữa lượt.
4. Số đếm bằng tập điểm thực, không trùng/mất mã; tổng mức cuối bằng `so_diem`
   chỉ khi đã phân loại hết. Trước đó các nhóm chưa tính là null; số Nghiêm
   trọng đã biết luôn giữ. Số vùng/số trang dựa trên danh sách thực, chưa quét
   giữ null. Vùng sửa tay có đề nghị chặn ngay cả chưa phân loại chữ.
5. `khong_ap_dung` cần chính sách đã duyệt + lý do trong snapshot. Chưa phân
   trang Word thì kiểm trang vật lý `chua_kiem`, không kết luận đảo/thiếu trang
   chỉ bằng số trang khác. Kiểm Điều/Khoản độc lập. Thiếu kiểm bắt buộc →
   `da_kiem_du=false`, tổng hợp `chua_doi_chieu_duoc`, `de_nghi_chan=true`.
   Trước tổng hợp `ket_luan=null`. Chỉ cho Khớp khi đủ kiểm, không còn điểm
   hoặc vùng chưa giải quyết; không che Nghiêm trọng đã biết khi báo chưa đủ.
6. Python bảo toàn sàn cứng; AI không hạ sàn/đổi nguồn/xóa điểm. Lệch dấu đổi
   nghĩa chỉ thành nhiễu khi đủ AI + OCR lại vùng đúng điểm/cặp/băm và ngoài
   vùng cứng. Thiếu cờ không tự gán false. Không có confidence/hộp thì bỏ;
   không điền số/hộp giả để vượt kiểm.

`yeu_cau_ai.chuyen_tiep.doi_chieu` gồm `phien_ban`, `ma_cap`, `ho_so`,
`bam_ho_so`, `bam_bo_quy_tac`, `bam_ngu_canh_ai`; mục tiêu ≤4 KiB, trần chung
64 KiB. Hỏi AI trả nguyên sang `tra_loi_ai`; Core điều phối Local, không gọi
engine khác trong engine. Ngân sách một lượt ≤100 điểm, tài liệu ≤500.000 ký
tự, khuôn ≤32 KiB; vượt `DC_QUA_NGAN_SACH_AI`, không tự chia nhiều lượt.

## 4. Quyền và lỗi thiết kế

SDK 2.0 `CoreGia._mo_tep` chỉ cho đọc ID thấy trong phong bì đầu vào, không
mở rộng quyền theo tham chiếu nằm trong **bytes JSON**. Vì vậy đọc được JSON
cặp không đồng nghĩa đọc được tệp con. Core phải ghép/cấp tập quyền, cô lập
pháp nhân/module/việc, phiên bản, thu hồi, giữ vòng đời xuyên bước và ACK.
Không thêm `nhan_2`, fan-in engine, route ghép riêng hoặc truy cập kết quả bất kỳ.

| Tình huống | Lỗi thiết kế cho DC-3 trở đi |
|---|---|
| Không có quyền/hết quyền/thiếu tệp/thiếu trang ảnh | `LoiNghiepVu("DC_THIEU_NGUON", "Chưa đủ nguồn hoặc quyền đọc tài liệu để đối chiếu. Anh kiểm tra lại hồ sơ được cấp.")` |
| Sai loại/phong bì/JSON/metadata | `DC_SAI_DAU_VAO` — “Dữ liệu đối chiếu chưa đúng định dạng. Anh kiểm tra lại hồ sơ.” |
| Sai băm/kích thước/nguồn không khớp | `DC_SAI_BAM` — “Nguồn đối chiếu đã thay đổi hoặc chưa khớp bản được ghim. Anh chọn lại hồ sơ.” |
| Vượt trần | `DC_QUA_GIOI_HAN` — “Hồ sơ vượt giới hạn đối chiếu của lượt này.” |

Lỗi không chứa đường dẫn, ID nguồn hay nội dung nghiệp vụ. Không fallback
đọc máy, không kết luận Khớp khi thiếu nguồn. Adapter cấp quyền DEMO chỉ ở
tests, không gắn vào runtime; không chứng minh RLS/ACL thật. Nguồn ngoài đã
nhận mà chưa trả phải `ChuaRo`, không báo thành công giả.

## 5. Khảo sát đọc được từ mã trong workspace

| Nguồn đọc | Bằng chứng tại mã | Kết luận có căn cứ / giới hạn |
|---|---|---|
| PDF lớp chữ | `e_ocr/goi/e_ocr/e_ocr/lop_chu.py::_doc_trang`, `_bbox`, `_hop` | `extract_text_lines` + `extract_words`; giữ từ/hộp `pt`, kiểm biên và hướng trang. Không xuất `nghi_ngo` hay confidence; có vị trí không chứng minh chữ nhận đúng |
| ABBYY hiện có | `abbyy.py::BackendABBYY.doc_pdf`, `chon_nguon.py` → `doc_lop_chu` | Nhận PDF lớp chữ rồi đọc như trên; không parser XML cờ nghi ngờ. Không suy cờ ABBYY từ PDF hoặc tên bộ đọc |
| Tesseract | `tesseract.py::_doc_tsv` | TSV level 5 có left/top/width/height, đổi pixel sang pt theo kích thước trang; output từ/hộp. Parser không chuyển cột conf thành confidence/cờ nghi ngờ. Không gán ngưỡng chưa đo |
| DOCX tham khảo | `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py::doc_bytes` | `so_trang=0`, `trang=[]`, cây `khoi_docx` + Unicode offset, cảnh báo chưa phân trang. Có Accept All trong RAM, chỉ đọc thân và cảnh báo phần khác: **không tái dùng nguyên** cho Đối chiếu, phải chặn track changes/comment theo DC-2 |
| OCR vùng cũ | `e_ocr/ma-nguon/vung.py` | Crop bốn điểm, phụ thuộc DTO/import Core cũ, `do_tin_cay=None` và cờ thận trọng. Chỉ tư liệu, không phải nguồn cờ ABBYY |
| OCR SDK 2.0 | `e_ocr/goi/e_ocr/engine.json` | Chỉ `doc_tai_lieu`, `doc_van_ban`, `xuat_word`; **chưa khai `ocr.trich_vung@1`**. DC-7 không được tự gọi hay giả rằng vùng đã có |

Chỉ đọc mã và manifest trong workspace, không chạy nguồn OCR, không đọc Hot
Folder hay đường K2/ổ máy ngoài workspace. Không port hoặc sửa `ma-nguon/`.

## 6. Từ điển, giấy phép và phát hiện sửa tay

**Nguồn hiện có:** chưa có bộ từ điển DC đã được cấp kèm băm/giấy phép/phê duyệt;
fixture chỉ là chuỗi DEMO để kiểm giao thức, không phải từ điển nghiệp vụ.
Không kết luận từ vắng trong từ điển là “vô nghĩa”, nhất là tên riêng/song ngữ.

| Phương án nguồn từ điển | Ưu/nhược và điều kiện nhận |
|---|---|
| Bộ cặp không đổi nghĩa do lead chuẩn bị, Admin duyệt | Kiểm soát tốt, phủ hẹp; cần bản sạch DEMO/nguồn gốc, quyền dùng/phân phối và SHA-256; không tự học thành đã duyệt |
| Bộ âm tiết/từ tổng quát offline | Phủ rộng hơn, có thể thiếu thuật ngữ; lead phải cấp tên, phiên bản, LICENSE/quyền thương mại/phân phối, tác giả, băm từng tệp và phê duyệt; chưa chọn/tải nguồn cụ thể |

Không tra web hoặc tải dữ liệu trong DC-1. DC-Q14 cho phép khảo sát rồi trình
nguồn ghim sạch, không đồng nghĩa mọi từ điển ngoài đều đã được duyệt.

| Phương án detector để đo DC-8/13 | Trade-off / điều kiện |
|---|---|
| Ảnh: căn chỉnh bản render Word với scan, tìm nét dư/gạch xóa ngoài vùng loại trừ có căn cứ | Đề xuất đo trước khi có render đáng tin; nhạy lệch dàn trang/nhiễu scan, cần đo recall vùng và lệch giả. Thiếu render không được coi phép trừ ảnh là đã kiểm |
| Detector đặc trưng nét/màu/thành phần trên scan | Có thể khảo sát khi chưa render, nhưng mực in/scan đen trắng/chữ ký chồng nội dung dễ gây nhầm; chỉ trả ứng viên, không tự đọc chữ tay |
| Model thị giác Local | Chỉ sau Anh/lead xác nhận model, quyền dùng và đo tài nguyên; Core điều phối, không gọi mạng/AI trong DC-1. Không mặc định model đã có hoặc độ chính xác đã đạt |

Chữ ký/con dấu/ký nháy chỉ loại trừ khi có vùng và căn cứ được ghim; không
che toàn vùng có chữ hợp đồng. Không kiểm đủ ký nháy/dấu giáp lai trong phạm
vi đầu (Q07/08). Không có detector/ngưỡng đã đo thì trạng thái `chua_kiem`,
số vùng null; không cho kết luận sạch. Mọi vùng thật phải có trang/hộp/ảnh
cắt do kho Core giữ, và đề nghị chặn. Thư viện/font/model cần gói offline,
giấy phép, nguồn/băm, lead duyệt trước thêm dependency ở lát triển khai.

## 7. CẦN ĐO trên máy thật — chưa thực hiện

- ABBYY: giấy phép FineReader Corporate và định dạng xuất thực có cờ nghi
  ngờ theo từ/ký tự không; khả năng ánh xạ XML/PDF/ảnh, đơn vị/góc xoay.
- Tesseract/bộ OCR thứ hai: tiếng Việt/song ngữ, dấu/số/tiền trong bảng,
  ổn định tọa độ khi render/scan; không tự đổi conf thành xác suất đúng.
- Word render: font/phiên bản/phân trang tin cậy, mapping DOCX→PDF→scan;
  kiểm thiếu/đảo trang tách với thiếu Điều/Khoản.
- Detector: DEMO in/ký/sửa tay/scan nhiều chất lượng, có đáp án vùng; đo
  vùng bị bỏ sót, lệch giả/trang, trang không xử lý, runtime/RAM. Ngưỡng để
  null tới khi DC-13 đo và Anh duyệt; không bịa accuracy hoặc cam kết đạt.
- C-DC-02: quyền tệp con xuyên bước, thu hồi/hết quyền, RLS/cô lập và vòng
  đời snapshot/ảnh; CoreGia không thay nghiệm thu Core thật.

Tiêu chí DC-13 giữ bắt đủ điểm Nghiêm trọng cài sẵn và **0 sửa thật bị ẩn
thành Nhiễu OCR**; DC-1 không tuyên bố đã đạt chất lượng đối chiếu.

## 8. Kiểm và lưu trữ

Fixture pytest chỉ DEMO, băm/kích thước đo từ bytes được `CoreGia.them_tep`
cấp. Chúng kiểm phong bì hợp lệ, sai loại, sai băm, hết quyền, thiếu ảnh;
không kiểm OCR/DOCX/detector thật. Adapter tests mô phỏng cửa cấp quyền để
chứng minh thiếu cửa mặc định thất bại và lỗi được thiết kế bảo thủ.
Manifest thật khởi động bằng CoreGia, khung Word vẫn `CHUA_LAM`.

Cấu hình và chỉ mục lượt qua `Ngan` (RAM tới SDK 2.1), `khai_bao` theo mẫu,
bảng pháp nhân phải có `phap_nhan_id` trong từng `khoa/loc`; chỉ đọc
`KetQuaLenh` sau commit, CAS/lô nguyên tử. Snapshot/ảnh/báo cáo qua kho Core,
không đệm bền trên engine; tệp tạm việc sau này dọn `finally`. Không TTL tự
xóa xác nhận; C-DC-03 cần danh tính/quyền/giờ tin cậy và nhật ký chỉ-thêm.

**Đã kiểm bằng Core giả (CoreGia)**; kết quả ba lệnh và nợ `thu` 0 demo ghi
trong `VIEC.md`. Chưa kiểm Core thật, nguồn OCR thật, từ điển thật hay detector.

# Đối chiếu bản ký — SDK 2.0, đến DC-5
# Đối chiếu bản ký — DC-8, phiên bản 0.4.8 chưa phát hành

DC-8 thêm `doi_chieu.phat_hien_sua_tay@1`: `ho_so_doi_chieu` → cùng loại,
quét ảnh qua SDK, phát hiện ứng viên gạch/chèn, tải PNG vùng có ngữ cảnh và
snapshot lên Core. Cần Pillow 12.3.0 theo `requirements.lock`, cấu hình
`phuong_phap_detector=net_de_vung_chu`, `phien_ban_detector=DC-8.1-thu-nghiem`
trong ngăn; Core cấp metadata ảnh tin cậy. Không đọc máy hoặc gọi AI/OCR.

Phương pháp **chỉ thử nghiệm**: DEMO 12 ca có 3 TP/0 FP/3 FN, recall 50%.
Đã quét pixel vẫn giữ `sua_tay=chua_kiem`, `da_kiem_du=false`, đề nghị chặn;
không kết luận sạch. Vùng ký/dấu chưa đủ căn cứ hoặc chồng nội dung được giữ
để xem, tách nguồn `metadata_can_xem` khỏi phát hiện pixel. Local vision
chưa đo. Quy ước nguồn/biến đổi, đầu ra và số đo tại
`../../docs/DC-8-KHAO-SAT.md`, `DC-8-SO-DO-DEMO.json`. Các mục DC-3/DC-4 dưới
đây ghi phạm vi từng bước trước đó, không phải kết luận cuối hồ sơ.

`doi_chieu.doc_docx@1` nhận DOCX qua `viec.mo_tep`, kiểm bản đã chốt và
trả `van_ban_tai_lieu`. Đọc trong RAM bằng SDK và thư viện chuẩn, không
OCR/AI/Cloud, không chương trình ngoài. `doi_chieu.nhan_cap@1` nhận JSON cặp,
kiểm nguồn và chuẩn hóa có dấu vết. `doi_chieu.so_van_ban@1` so toàn văn,
căn cấu trúc và áp sàn quy tắc Python; kết luận toàn tuyến còn ở các lát sau.

## Quy tắc cứng và tiền bằng chữ — DC-5

Handler vẫn nhận hồ sơ `da_nhan`, trả hồ sơ `da_so`, không thêm năng lực
hay sửa hợp đồng API/schema chung. `quy_tac.py` dùng kiểm nguồn/căn/so của
DC-4, chốt snapshot một lần bằng cùng cơ chế Ngan/CAS/chủ lượt/hạn chiếm;
khóa chống trùng có thêm `DC-5-1`. Không sửa `so_chu.py`/`can_chinh.py`
hoặc phần ảnh DC-8. Snapshot đã áp quy tắc không được áp lại để reset mức.

Các quy tắc bắt buộc luôn bật: `DC_CHU_SO`, `DC_NGAY_THOI_HAN`,
`DC_TIEN_TY_LE`, `DC_TIEN_CHU`, `DC_DINH_DANH`, `DC_CAU_TRUC`,
`DC_PHU_DINH_BAT_BUOC`, `DC_OCR_NHAM`. Quét Python trên toàn văn NFC có
ánh xạ về nguồn, giữ cả đầu/chân trang, tab/ranh giới ô và nguyên văn;
không phụ thuộc vùng AI. Diff chỉ chứa một chữ vẫn xét từ/cụm đầy đủ.
Các lát chữ/ngắt dòng của Điều/Khoản thiếu/thừa/đảo giữ sàn cấu trúc.
0/O, 1/l, 5/S, 8/B không bị sửa ngầm, vẫn Nghiêm trọng và có ghi chú.
Lát được DC-4 coi tương đương chuẩn hóa vẫn kiểm lại trên bản chỉ NFC:
gạch/nháy/khoảng trắng không được che khác biệt số, mã hoặc vùng bảo vệ.

Phần tùy chọn `quy_tac_cung` của **bộ JSON đã được duyệt và ghim bytes**
có quy ước nội bộ dưới đây. Ví dụ DEMO, không phải bộ dùng trên hồ sơ thật:

```json
{
  "phien_ban": 1,
  "dinh_dang_so": [{"nghin": ".", "thap_phan": ","}],
  "don_vi_tien": {"VND": "VND", "đồng": "VND", "USD": "USD"},
  "dinh_dang_ngay": ["YYYY-MM-DD"],
  "vung_bao_ve": []
}
```

- `dinh_dang_so`: tối đa 10 quy ước. `nghin` nhận null/chấm/phẩy/khoảng
  trắng; `thap_phan` nhận null/chấm/phẩy, phải khác dấu nghìn. Nhiều quy
  ước đọc cùng chuỗi ra nhiều giá trị → mơ hồ. Thiếu quy ước chỉ đọc số
  nguyên không phân cách. Chỉ khác phân cách được coi hình thức khi bộ
  đọc được cùng giá trị và **cùng chuỗi chữ số, giữ mọi số 0 đầu**, ngoài
  vùng định danh. Không dùng giá trị Decimal để gộp hai MST/STK/mã khác.
- `don_vi_tien`: ánh xạ tên/đơn vị ghi rõ sang mã ba chữ hoa; không suy
  mã tiền từ dấu phân cách hoặc ký hiệu `$`. Ký hiệu chỉ đọc được khi bộ
  khai tường minh. Mã VND/USD… không được ánh xạ sang mã khác.
- `dinh_dang_ngay`: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`; chỉ xuất
  ngày ISO đã kiểm lịch. Nhiều cách đọc khác nhau, ngày sai hoặc thời hạn
  bằng lời chưa có parser giữ hạng mục chưa đủ kiểm; không tự đoán.
- Mỗi `vung_bao_ve` có `ben` (word/ban_ky), `loai`, `bat_dau`, `ket_thuc`,
  `nguyen_van`, `bam_van_ban` (SHA-256 UTF-8 nguyên văn). Phải khớp chính
  xác nguồn; sai → `DC_SAI_NGUON`. Các loại: `ben_ky`, `nguoi_dai_dien`,
  `chuc_vu`, `mst`, `stk`, `dia_chi`, `so_hop_dong`. Nhãn Python Việt/Anh
  cũng bảo vệ điểm lệch nhưng **không tự chứng nhận nhận diện đủ**. Muốn
  đánh dấu đủ vùng phải có metadata khớp nguồn cho mọi loại ở cả hai bản.
  Metadata thuộc bộ đã ghim, không nhận từ nội dung model.

Bộ DC-3 cũ thiếu phần trên vẫn áp tất cả quy tắc bắt buộc, giữ
`quy_tac_cung=chua_kiem`. Phần khai sai/null/khóa tắt hoặc hạ quy tắc bị
từ chối `DC_BO_QUY_TAC_KHONG_HOP_LE`. Không có bộ nới lỏng mặc định.

Kiểm tiền nội bộ bản ký: chỉ ghép duy nhất một cụm bằng số + đơn vị với
nhãn “Bằng chữ” trong cùng dòng/ô, giữ cả hai nguyên văn, offset, giá trị
và căn cứ. Ngữ pháp tiếng Việt hỗ trợ số nguyên từ 0 đến dưới 10^12,
nghìn/ngàn, tỷ/tỉ, linh/lẻ, mốt/tư/lăm ở vị trí hợp lệ, đơn vị/chẵn.
Số tiền hoặc tiền tệ trái nhau sau khi phân tích đủ → Nghiêm trọng, kể
cả nguyên văn hai bản giống nhau. Thiếu nhãn/cụm/đơn vị, nhiều số tiền,
ngữ pháp khác, tiền lẻ bằng chữ hoặc phần ngôn ngữ chưa hiểu → Cần xem,
`khop=null`, `da_kiem_du=false`. Không ghép qua dòng/ô, không diễn giải
viết tắt/OCR hoặc tự coi danh sách chưa nhận diện được là đã kiểm xong.

Tính số bằng Decimal hoặc int. Trong JSON snapshot, tiền luôn có
`{so, tien_te}`: `so` nguyên dùng int, phần thập phân dùng chuỗi chính xác
(ví dụ `"1000.25"`), không đi qua float. Ngày đã đọc dùng `YYYY-MM-DD`;
nguyên văn, mã và số 0 đầu giữ riêng nguyên vẹn.

Mỗi điểm có `muc_san`, `muc`, `quy_tac_trung`, `can_cu_quy_tac`,
`vung_bao_ve`. Phần còn chưa đủ căn cứ giữ `can_xem`; hạng mục cụ thể ở
`kiem_quy_tac`, số đếm giữ các Nghiêm trọng đã biết. `nhat_ky_quy_tac`
cùng băm ghim sàn/lịch sử; `kiem_bat_bien(snapshot, goc)` so với bản gốc
**đọc lại từ Core**, chặn tự băm lại, xóa điểm, thay căn cứ hoặc hạ mức.
`ap_muc_ai` chỉ nhận mã/mức/lý do, không nhận sàn/quy tắc, chặn mọi hạ
mức. Đây là cửa thuần cho DC-6; chưa thay hậu kiểm nguồn/trích dẫn Local
của DC-6/DC-7. DC-5 không gọi Local hoặc Cloud.

`ket_luan=null`, `da_kiem_du=false`, `de_nghi_chan=true` ở bước này vì
còn các hạng mục khác; không tự mở hiệu lực. Bộ DEMO chỉ kiểm hành vi đã
cài, không chứng minh tỷ lệ phát hiện trên tài liệu thực tế. Đã kiểm bằng
Core giả (CoreGia); chi tiết ma trận và giới hạn tại `docs/VIEC.md`.

## Đọc DOCX — DC-2

Đọc thân, đầu/chân trang, footnote/endnote, đoạn và bảng lồng; giữ ô trống,
gộp ngang/dọc. Quét sửa đổi/comment trong mọi phần XML Word, kể cả phần
phụ và thuộc tính: có thì `DC_WORD_CHUA_CHOT`, không Accept All. Vùng không
hỗ trợ hoặc hỏng trả `DC_WORD_KHONG_DOC_DUOC`, không trả văn bản thiếu.

Phạm vi hỗ trợ: WordprocessingML transitional, danh sách đánh số thông dụng
(decimal, decimalZero, letter, Roman, bullet). Chưa hỗ trợ Strict OOXML,
field động/kết quả field, hình/textbox, công thức, OLE/altChunk, danh sách
liên kết style/picture bullet và markup khác chưa hiểu; các vùng này bị
từ chối. Mọi quan hệ ngoài đều bị từ chối, kể cả hyperlink và template.

Trần cứng: DOCX 20 MiB; ZIP 2.000 mục/100 MiB giải nén, tỷ lệ nén ≤200;
XML mỗi phần 16 MiB, sâu ≤128, tổng ≤200.000 node; văn bản ≤500.000 ký tự;
JSON kết quả ≤20 MiB; bảng ≤256 cột/50.000 ô gốc, cây khối sâu ≤16.
Kiểm danh mục trước giải nén, kiểm bytes/EOF/CRC thật khi đọc XML.
Vượt trần trả `DC_QUA_GIOI_HAN`, không cắt nội dung.

Quy ước nguyên văn và vị trí (không chuẩn hóa NFC/strip ở bước đọc):

- Giữ nguyên chuỗi XML `w:t` đã giải mã, tab/ngắt dòng/gạch nối và nhãn
  đánh số nguồn. Các đoạn nối `\n`; bảng nối cột bằng ` | `, dòng bằng
  `\n`; ô phủ bởi ô gộp giữ chỗ trống, gốc ghi `gop_hang`/`gop_cot`.
- `khoi_docx` giữ thứ tự đoạn/bảng trong từng phần, gồm khối/ô lồng và
  offset `[bat_dau, ket_thuc)` theo Unicode code point trong đúng `van_ban`.
  Mỗi lát chuỗi bằng chính `van_ban` của khối/ô; offset không phải UTF-16/byte.
  Chỉ số `so_doan` chạy xuyên các phần; ngữ cảnh Điều/danh sách tách story.
- Thân trước, phần phụ theo tên OPC, từng chú thích theo thứ tự XML.
  `vung_docx` ghi phần/loại/ID chú thích, chỉ số khối bắt đầu và số khối;
  khối gốc ghi `phan`/`ma_chu_thich`, đoạn có tham chiếu ghi `chu_thich`.
  Đây là thứ tự tuần tự hóa ổn định, không phải vị trí trang vật lý.
- Chưa render Word: `so_trang=0`, `trang=[]`, cảnh báo chưa phân trang;
  không có trang/hộp giả. `bam_dau_vao` băm SHA-256 bytes DOCX thật.

SDK 2.0 dùng ngăn RAM, mất khi dừng; ngăn bền và màn quản trị chờ Core/SDK
2.1. Các màn trong bản khai là dự kiến, chưa có tệp UI. Cấu hình và dữ liệu
cần giữ chỉ qua Ngan; snapshot/ảnh do kho Core giữ, không lưu bền trên engine.

DEMO `demo/DEMO-ban-chot.docx` có nhãn DEMO, bảng gộp/ô trống, 1.000.000 VND
và 2026-10-30; không chứa hồ sơ thật. Chạy bằng venv và
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`:

```text
python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
python -m pytest e_doi_chieu/tests -q
python e_doi_chieu/tests/kiem_doc_lap.py
```

Đã kiểm bằng Core giả (CoreGia), chưa kiểm Core thật/Linux. Kết quả thật
và các cửa Core còn thiếu tại `e_doi_chieu/docs/VIEC.md`; nguồn/băm tại
`NGUON.md`. DC-2 có DEMO sạch chạy trực tiếp bằng lệnh `thu`.

## Nhận cặp — DC-3

Đầu vào theo `docs/DC-1-KHAO-SAT.md` §2: một tệp JSON UTF-8, kèm
`tham_so.bam_yeu_cau` băm **nguyên bytes**, kiểm trước parse. JSON từ chối
khóa trùng, NaN/Infinity, surrogate lẻ, đuôi thừa và cây sâu hơn 64 mức.
Không nhận khóa quyền/pháp nhân/module tự khai, đường máy, URL hoặc base64.
Mọi tham chiếu đều mở bằng `viec.mo_tep`; kiểm kích thước/băm thật,
phiên bản nguồn, quan hệ `bam_dau_vao` của từng kết quả đọc, trang/hộp/ảnh.
Word được đọc lại bằng DC-2 và so nguyên kết quả đã ghim (trừ phiên bản
engine tạo kết quả); không lấy `word_da_chot=true` làm chứng nhận đã chốt.
OCR lỗi, thiếu trang hoặc nguyên văn rỗng đều từ chối, không ra `khop`.

Core phải cấp quyền tệp con và bảo đảm provenance/phiên bản gắn nguồn,
bao gồm kết quả OCR và ảnh đúng bản ký. Băm chỉ kiểm bytes. SDK 2.0 mặc
định thiếu cửa tệp con sẽ trả `DC_THIEU_NGUON`; adapter DEMO chỉ ở tests,
không có nhánh giả lập/fallback trong runtime. PDF được kiểm dấu định dạng
vận chuyển, không tự đọc PDF hoặc gọi OCR để chứng thực lại nội dung.

Cấu hình đọc từ ngăn, thiếu trả `CHUA_CAU_HINH`. Bộ JSON do Core cấp được
ghim nguyên bytes, SHA-256 phải khớp `cau_hinh.bam_bo_chuan_hoa` và mã bộ
khớp `ma_bo_chuan_hoa`. Quy ước nội bộ của bộ tại DC-3 (không đổi schema
loại chung): `phien_ban=1`, `phien_ban_bo` khớp tham chiếu, mã bộ và
`chuan_hoa` bắt buộc; các phần quy tắc khác giữ nguyên cho lát tiếp theo.
Ví dụ **DEMO**, không phải bộ nghiệp vụ đã cấp để chạy thật:

```json
{
  "phien_ban": 1,
  "phien_ban_bo": "DEMO-1",
  "ma_bo_chuan_hoa": "DEMO-NFC-1",
  "chuan_hoa": {
    "unicode": "NFC",
    "khoang_trang": "gop",
    "dau_nhay": "thang",
    "gach_noi": "thong_nhat",
    "ngat_dong": "noi_trong_doan",
    "ngat_tu_cuoi_dong": "chi_gach_noi_mem",
    "dau_chan_trang": [],
    "bo_so_trang": false
  }
}
```

Không có bộ nới lỏng mặc định. Ngoài `unicode`, các lựa chọn dạng chuỗi
còn nhận `giu_nguyen`; danh sách đầu/chân trang và cờ số trang luôn phải
khai rõ. NFC giữ dấu tiếng Việt, emoji và hỗ trợ cả Hangul Jamo. Nháy cong
đổi sang nháy thẳng; gạch U+2010…U+2014 đổi `-`, giữ dấu trừ U+2212.
Khoảng trắng được gộp; chỉ nối ngắt dòng bên trong đoạn, giữ biên cấu trúc
và `\f` giữa trang. Chỉ bỏ **soft hyphen + ngắt dòng giữa chữ** trong một
đoạn; không xóa gạch nối cứng hoặc nối số/mã hợp đồng. Không tự chuẩn kiểu
đánh số, từ vựng hay bỏ dấu trên bản so chính.
Khoảng trắng sau soft hyphen phải liền kề trong nguồn; không nối chữ hoặc
gộp ánh xạ qua một vùng đầu/chân trang đã bỏ.

Đầu/chân trang chỉ bỏ chuỗi đúng whitelist đã ghim và có story DOCX thật;
OCR còn cần vị trí lề và lặp ở ít nhất hai trang. Số trang chỉ bỏ nguyên
dòng `Trang n` hoặc `Trang n/tổng` ở lề, khớp số trang thật. Tiền, chữ số,
mã và nội dung thân giống header vẫn giữ. Mỗi vùng bỏ có offset/lý do;
không suy trang Word từ XML hoặc dựng hộp tọa độ mới.

Snapshot có hai nguyên phong bì văn bản, tham chiếu/băm nguồn, bộ/cấu hình,
ảnh/bằng chứng và bản chuẩn hóa. Mỗi bên `chuan_hoa` chứa `nguyen_van`,
`van_ban`, `anh_xa`, `vi_tri`, `da_bo`, `chua_neo_cau_truc`. Run ánh xạ là
`[đầu_chuẩn, cuối_chuẩn, đầu_gốc, cuối_gốc]`, Unicode nửa mở. Độ dài bằng
nhau là tịnh tiến; vùng co/giãn trỏ cả cụm gốc, ví dụ `Á` → `A\u0301`.
`vi_tri.ve_nguon(ban_chuan_hoa, a, b)` trả **các lát nguồn** và nút cấu trúc
giao nhau; lát có thể rời nhau khi bỏ soft hyphen/header. Đường dẫn nút
tính trong payload `van_ban_tai_lieu`, không phải đường tệp. Ô rỗng/gộp
vẫn có nút/offset; khối OCR lặp hoặc không neo được duy nhất chỉ có vị trí
trang và cảnh báo, không gán hộp đoán cho chữ. Giữ nguyên cây OCR gốc.

Snapshot đầy đủ tải bằng `tai_tep_ra`; phong bì schema đã duyệt chỉ giữ
tham chiếu/băm, trạng thái và số đếm. `da_nhan`: mới kiểm hai bản, các số
chưa đo là `null`, các bước sau `chua_kiem`, `ket_luan=null`,
`da_kiem_du=false`, `de_nghi_chan=true`. Không coi đây là kết luận máy.

Ngăn `luot_doi_chieu` dùng `lay_hoac_tao` theo pháp nhân, băm cặp, băm bộ
và phiên bản engine. Băm cặp gồm băm/phiên bản hai bản và băm các đầu ra
dẫn xuất/ảnh/bằng chứng, `ma_cap`, cảnh báo đầu vào và SHA-256 JSON cấu
hình đã điền mặc định (gồm các trần). Không phụ thuộc ID/tên tệp; đổi mã
cặp, cảnh báo hoặc cấu hình thì tạo lượt mới, không trả metadata cũ.

Chủ lượt có mã riêng mỗi lần thực thi, `luc_chiem`/`han_chiem` theo giây
Unix UTC. Cấu hình ngăn `thoi_han_chiem_luot_giay` là số nguyên dương,
không bắt buộc; khi bỏ trống, dùng `gioi_han.thoi_han_giay` của bước nhận
cặp cộng biên 60 giây (**180 giây** với manifest hiện tại). Lượt quá hạn
hoặc hàng cũ thiếu hạn được chiếm lại bằng CAS; chưa quá hạn đợi tối đa
khoảng một giây rồi trả `DC_DANG_XU_LY`, cho thử lại. Chủ cũ quay lại không
được chốt/cleanup đè chủ mới. Không dùng hạn này để xóa nhật ký hay ngăn.

CAS chốt thử lại tối đa ba lần, không tải lại tệp để thử CAS. Tái dùng
phải mở lại snapshot và **mọi tham chiếu cũ** bằng quyền việc hiện tại.
Nếu tệp cũ thiếu/hết hạn/không còn quyền, CAS chuyển `can_thu_lai`, rồi
chiếm lượt và dựng lại từ các nguồn **hiện tại đã kiểm quyền/băm/trần**.
Sai băm vẫn từ chối `DC_SAI_NGUON`, lỗi truyền vẫn giữ ngữ nghĩa SDK.
Hủy/lỗi nhường `can_thu_lai` bằng CAS, không xóa sổ hoặc đè chủ khác.
Ngăn chỉ giữ phong bì nhỏ, không toàn văn. Ngăn RAM mất khi khởi động lại;
quyền/vòng đời snapshot, đồng hồ giữa worker, lease Core và CAS bền vẫn
cần Core xác nhận.

Các trần §2.3 được kiểm cả metadata và bytes thật: yêu cầu 1 MiB; từng tệp
gốc/ảnh/JSON nguồn ≤20 MiB, toàn việc ≤128 MiB bytes đọc (kể cả yêu cầu và
snapshot tái dùng); ≤60 trang, ≤20 triệu pixel/ảnh; ≤500.000 ký tự/bản và
tổng ≤1.000.000; snapshot ≤20 MiB, phong bì ≤64 KiB. Cấu hình chỉ được hạ
trần cứng, không cắt nội dung. ZIP vẫn chịu trần DC-2 và trần cấu hình.
Manifest khai trần đọc 20 MiB để SDK cho mở tệp con, engine tự giữ JSON
yêu cầu 1 MiB. SDK có thể từ chối đầu vào quá trần manifest trước handler.

PNG kiểm IHDR/pixel, CRC, EOF DEFLATE và đủ dòng/filter trong RAM; PNG
interlace chưa hỗ trợ sẽ từ chối. JPEG kiểm marker/khung/kích thước, **chưa
giải mã DCT** (`da_giai_ma=false`): DC-8 phải giải mã thực bằng thư viện đã
ghim trước quét. Không suy phép đổi `pt`↔`px`, DPI hoặc xoay từ metadata tự
khai; giữ tọa độ nguồn và kích thước ảnh riêng. DC-3 không đánh dấu đã quét.

`thu` tiếp tục kiểm DEMO Word 1/1; nhận cặp được kiểm end-to-end trong
pytest với CoreGia/NganBoNho/adapter tệp con, không thêm DEMO thành công
giả vào runtime thiếu quyền/cấu hình. Lớp bọc handler đổi lỗi bất ngờ thành
câu cố định để SDK 2.0 không in nội dung ngoại lệ; không sửa SDK và chưa
khép nợ log lỗi ngoài handler của SDK.

## DC-4 — So văn bản hai bên

`doi_chieu.so_van_ban@1` nhận hồ sơ `da_nhan`, trả `da_so`. Hai tham số
`bo_quy_tac_json` và `bam_bo_quy_tac` phải khớp **nguyên bytes** bộ đã ghim
ở DC-3, không chỉ cùng nội dung JSON. Bước so đọc lại snapshot và mọi nguồn
qua SDK, kiểm băm/quyền/cấu hình/chuẩn hóa. Không sửa nguồn DC-3; snapshot
mới giữ `ho_so_truoc` (tham chiếu+băm), nguồn/bộ và nguyên văn bất biến.

Căn Điều → Khoản → câu, bảng → dòng → ô, kể cả bảng lồng, ô trống và ô gộp.
Nhãn NFC/NFD được nhận diện; không biến số tiền đầu dòng thành Khoản.
Neo theo từng lần xuất hiện và chuỗi có thứ tự (LIS); không bật autojunk,
không chạy phép so ký tự bậc hai trên cả tài liệu. Cụm lớn không có neo
được giữ như phép thay đầy đủ; không có neo để căn hai tài liệu hoặc bảng
không định vị được thì trả `DC_KHONG_CAN_DUOC`. Bảng OCR lặp cần offset
nguồn kiểm lại được; không có offset thì phải tìm được duy nhất trong trang.

Snapshot có `edit_script` (toàn văn) và `diem_lech` (ứng viên):

- Mỗi bước script có `phep`, `word`, `ban_ky`, `can_cu`, `ma_diem` hoặc null.
  Mỗi bên giữ `nguyen_van`, offset Unicode `[bat_dau,ket_thuc)`, lát
  `chuan_hoa` và `vi_tri` thật hoặc null. Script phủ liên tục từ 0 đến hết
  **cả nguyên văn và bản chuẩn hóa**; kiểm tái dựng trước khi tải lên Core.
  Không tách cụm Unicode co/giãn dùng chung nguồn; phần chuẩn hóa đã duyệt
  vẫn giữ nguyên văn bằng phép `tuong_duong_chuan_hoa`.
- Điểm chữ giữ phép `chen`/`xoa`/`thay`; điểm cấu trúc còn có `dao`, thiếu/
  thừa Điều/Khoản/bảng và đổi hình dạng bảng. Đảo Điều vẫn kiểm các Khoản
  bên trong. Script chữ giữ thứ tự hai nguồn bằng chèn/xóa; điểm cấu trúc
  ghi riêng căn cứ đảo, không làm mất văn bản để tạo một neo giao nhau.
- `ma_diem` băm nguồn/phiên bản/bộ/văn bản/offset/phép/căn cứ, không dùng UUID
  hoặc vị trí mảng. Lượt bỏ dấu chỉ thêm nhóm `chi_lech_dau`; thuê/thuế và
  mọi ứng viên vẫn còn. `cho_phan_loai=true`, `muc_san=null`, `muc=null`;
  `quy_tac_cung`, `lech_dau`, AI, OCR kém và sửa tay còn chưa kiểm.
- Điểm trang giữ ảnh/băm/số trang thực trong căn cứ; chưa có ánh xạ chữ
  Word của ảnh render thì hai lát chữ là null, không dựng offset giả.
  `tom_tat.so_diem` đã biết; số mức chưa phân loại vẫn null. Luôn giữ
  `da_kiem_du=false`, `ket_luan=null`, `de_nghi_chan=true` ở DC-4.

Kiểm trang bảo thủ: có PDF render và ảnh trong JSON chưa chứng minh render
thuộc Word này. Cửa **C-DC-05 chưa có thật**. Lớp bọc tạm chỉ nhận liên kết
do Core gắn trong `viec.ngu_canh.doi_chieu_phan_trang` (không lấy từ JSON
caller/snapshot). Quy ước đề nghị, chưa phải API Core đã nghiệm thu:

| Trường | Giá trị phải khớp nguồn ghim |
|---|---|
| `phien_ban` | Số nguyên 1 |
| `bam_word`, `phien_ban_word` | Bản DOCX gốc |
| `bam_pdf_chuan` | PDF render của đúng bản Word, Core kiểm nguồn tạo |
| `bam_ban_ky` | PDF bản ký |
| `anh_word`, `anh_ban_ky` | Danh sách băm ảnh từng bên theo thứ tự trang |

Core phải tự xác minh liên kết render/ảnh, không chép lại tuyên bố của
caller; metadata ≤16 KiB. Thiếu cửa → `trang=chua_kiem`. Liên kết sai băm
→ `DC_SAI_NGUON`. Khi đủ liên kết và toàn bộ ảnh ghép được bằng băm trùng
chính xác, kiểm được thứ tự trang; đảo trang tạo điểm `dao`. Ảnh scan khác
pixel, khác dàn trang, thiếu ánh xạ nội dung trang hoặc số trang khác →
vẫn `chua_kiem`, không tự suy thiếu/thừa trang. Không dùng số dòng DOCX.

Ngăn có lượt riêng cho bước so, khóa gồm băm snapshot nhận, bộ, phiên bản,
trần hiệu lực và bằng chứng phân trang Core. `lay_hoac_tao` + CAS/chủ lượt/
hạn chiếm chống chốt trùng; cạnh tranh đang chạy trả `DC_DANG_XU_LY`, cho
thử lại. Không đổi hàng `da_nhan` của DC-3. Tái dùng kiểm lại quyền, snapshot
tiền nhiệm và tái dựng; tệp cũ hết quyền được dựng lại, sai băm bị từ chối.
Lỗi/hủy nhường bằng CAS, không ghi đè chủ khác. RAM mất khi khởi động lại.

Trần §2.3 và trần cấu hình lấy mức thấp hơn; kiểm 10.000 điểm, ký tự cả
nguyên văn/bản chuẩn hóa, tệp/phong bì/bytes và hạn 300 giây. Vượt trả
`DC_QUA_GIOI_HAN`, không tải bản cắt. Gọi `kiem_huy` theo cụm; tiến độ chỉ
câu cố định, không nội dung. Toàn bộ runtime dùng RAM/Ngan/tệp Core.

**Đã kiểm bằng Core giả (CoreGia):** ba lệnh bắt buộc đạt, 407 tests
(110 ca DC-4), 0 skipped. DEMO Word của lệnh `thu`: 1/1; đường nhận cặp
và so nằm trong pytest vì cần cấu hình/quyền tệp con. Phân trang dùng
provider DEMO giả (PDF có trang/ảnh thực); chưa đo renderer/OCR/Core thật.

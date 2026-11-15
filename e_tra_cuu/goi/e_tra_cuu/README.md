# Tra cứu tài liệu — TC-3: nhận và cắt cấu trúc

Phiên bản 0.1.0, SDK 2.0.0, chưa phát hành. TC-Q13 đã duyệt chiều 15/11/2026.
Manifest đăng ký tám năng lực và bốn loại đúng phiếu §2.1; stub nội bộ
`kiem_khung` đã bỏ. `tra_cuu.nhan_yeu_cau@1` nhận tệp JSON, kiểm và ghim dữ liệu
thành `ho_so_tra_cuu` ở giai đoạn `da_nhan`. `tra_cuu.cat_doan@1` chuyển hồ sơ
`cat_doan/da_nhan` sang `da_cat_doan`. Sáu năng lực còn lại luôn báo `CHUA_LAM`,
chờ TC-4…8. Nhận/cắt thành công không có nghĩa đã phân loại hoặc trả lời.

Có **5 ví dụ chay_thu_demo**, tệp và băm thật trong `demo/`. Cổng bổ sung ở
`tests/chay_demo_voi_core_gia.py` nạp ngăn/cấu hình, nguồn, giấy cấp quyền giả
rồi chạy đúng các ví dụ và bốn ca nhận → cắt (9/9). **Đã kiểm bằng Core giả (CoreGia)**; chưa chứng nhận
quyền Core thật. CLI SDK gốc thiếu cấu hình vẫn lỗi `CHUA_CAU_HINH`, không tự
khởi tạo dữ liệu DEMO hoặc đọc cấu hình từ môi trường để vượt cổng.

## Khởi động và cấu hình

Core khởi động trong thư mục gói bằng `{python} -B -m e_tra_cuu.chay`;
`Engine.tu_khai_bao` kiểm manifest 2.0 và `app.chay()` dùng cổng SDK chung.
Core cần dùng `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` khi chạy gói để tránh bytecode.

`ngan.py`, `cau_hinh.py` chép nguyên mẫu NGAN-0. SDK có `app.ngan` thì giữ nguyên;
thiếu mới gắn một `NganBoNho(khai_bao)` dùng lại trong tiến trình. Cảnh báo RAM ra
stderr một lần; khởi động lại mất dữ liệu. Không tệp cấu hình/sổ/cache bền,
không Cloud, không kết nối mạng ngoài, không SQL hoặc gọi engine khác.

Giá trị cấu hình là một bản ghi `cau_hinh`, khóa `{}`, trong ngăn.
Schema và bản khai SDK 2.1 là metadata chỉ đọc, không phải nơi lưu giá trị cấu hình.
`chup_cau_hinh(ngan)` lấy giá trị và `row_version` từ **một lần đọc** nhất quán.
Mẫu `doc_cau_hinh` chỉ kiểm/điền mặc định trên bản vừa đọc, không đọc lại ngăn.
`yeu_cau_cau_hinh` giữ tiện ích trả giá trị cho các phần chỉ cần đọc cấu hình:

- Thiếu bản ghi: `CHUA_CAU_HINH`, câu hướng dẫn Admin vào Cấu hình; khởi động vẫn được.
- Sai kiểu/trường/trần: `CAU_HINH_KHONG_HOP_LE`; ngoại lệ ngăn đổi sang lỗi SDK an toàn.
- Bản ghi phải có `phien_ban=1` và `quy_tac_nhom={tep_id,bam}`; băm dạng SHA-256.
  Tham chiếu/băm không tự chứng minh quyền hoặc nguồn hợp lệ; kiểm nguồn ở TC-2.
- Default chỉ điền trên bản sao sau khi có bản ghi. `phan_loai.trang_thai=chua_do`
  không có số ngưỡng mặc định. `da_do` phải có `nguong` và `bam_bo_do`;
  trạng thái chưa đo không được mang hai trường này. Metadata này chưa chứng nhận
  chất lượng hoặc cho phép kích hoạt nhóm nghiệp vụ (TC-Q15).
- `cat_doan` mặc định mục tiêu 2000 ký tự, đơn vị tối đa 8000, tối đa 5000 đoạn;
  mục tiêu không vượt trần đơn vị. `ngan_sach` chứa các trần thiết kế phiếu §2.3,
  chỉ cho giảm. Đây chưa là số đo token/context/model thực tế.

`phien_ban` là phiên bản cấu trúc cấu hình, khác phiên bản CAS. RAM mất cả
cấu hình/bài đo khi khởi động lại; chưa có lưu bền Core/SDK 2.1.

## Chuẩn bị Local AI — TC-4

`tra_cuu.chuan_bi_ai@1` nhận `da_nhan` cho `phan_loai`, `phan_tich_cau_hoi`,
`xep_hang_lai`, `soan_tra_loi`. Tham số tác vụ phải khớp hồ sơ. Mã/phiên bản/
prompt module bắt buộc và giữ nguyên; không suy quyền/module từ mã prompt.
`model_uu_tien` chỉ chuyển cho Hỏi AI, TC không chọn/gọi model.

Cửa tin cậy cấp lại `dau_vao` đúng nguyên phong bì bước nhận cùng request/task/
ngữ cảnh và từng ref/nguồn. Kiểm lại bytes snapshot, cấu hình đã ghim và nguồn
qua `mo_tep`; không đọc cấu hình mới giữa chuỗi. Core điều phối Local AI rồi
giao phản hồi cho TC-5…7. Tầng 1 Python hoặc không có bằng chứng bị từ chối
chuẩn bị (`TC_SAI_GIAI_DOAN`) để Core đi nhánh bỏ AI; không dữ liệu AI giả.

Bốn khuôn: lựa chọn phân loại/căn cứ; ý định/thực thể/hàm/phiên bản/tham số/
thời điểm; xếp hạng hoán vị đủ mã đúng một lần trong thang; câu trả lời có
khẳng định/thực thể/giá trị/đơn vị/nguồn/câu trích. Model không cấp quyền,
duyệt hoặc nhãn Xanh. Tham số hàm đóng thuộc tính chưa khai; `$ref` nội bộ
được chuyển gốc vào `$defs` riêng từng hàm, không tải ref ngoài. Schema đệ quy
hoặc từ khóa consumer AI-2 chưa hỗ trợ bị từ chối. Đây không phải validator
schema tổng quát; AI-2 vẫn kiểm schema, TC-6 phải kiểm sâu hàm/tham số/quyền.

`tai_lieu` có nhãn kỹ thuật JSON và các chuỗi nguồn nguyên vẹn. Mã `tc-ai-…`
ổn định theo nguồn/phiên bản/băm/span, chỉ là mã vùng AI, không giả đoạn đã
lập chỉ mục TC-3. `ai.map_nguon` ghi span AI → offset toàn văn nguồn cùng
`duong_dan_snapshot`/span trong chuỗi snapshot; Unicode code point, nửa mở
`[bat_dau,ket_thuc)`, không byte/UTF-16. Map câu hỏi/mô tả hàm có
`ma_nguon=null`, không giả nguồn tài liệu. Nhãn kỹ thuật không là chứng cứ;
nguyên văn trùng ở các ứng viên vẫn có map/mã ứng viên riêng. Không đổi NFC/NFD.

Snapshot `cho_ai` có `ai={ma_prompt,phien_ban_prompt,prompt,model_uu_tien,
khuon_tra_loi,tai_lieu,map_nguon,doan,bam_ngu_canh_ai,ngan_sach}`, cùng nguồn/
danh mục/cấu hình ở Core. Băm ngữ cảnh trên đúng UTF-8 `tai_lieu`. Chuyển tiếp
chỉ khóa `tra_cuu` với đúng `phien_ban,ma_yeu_cau,tac_vu,ho_so,bam_ho_so,
bam_cau_hinh,bam_ngu_canh_ai`; không prompt/toàn văn/danh mục/câu hỏi. Hỏi AI
giữ nguyên, không đưa vào prompt provider. TC hậu kiểm phải dựng lại yêu cầu
canonical để so `bam_dau_vao` AI-2, tự kiểm quote/map và loại nhãn kỹ thuật;
XONG AI-2/`kiem_trich_dan.dat` không chứng nhận nghiệp vụ Tra cứu.

Trần tài liệu 100000 ký tự, khuôn 32 KiB, chuyển tiếp 64 KiB (mục tiêu 4 KiB),
100 hàm/1000 mục danh mục/50 ứng viên; cấu hình đã ghim chỉ cho giảm. Tính byte
UTF-8 thật; quá trả `TC_QUA_NGAN_SACH_AI`, không cắt/batch/Cloud. Snapshot vẫn
≤20 MiB. Token thực để null, `trang_thai_token=chua_do`; chưa chứng minh đủ
context model. Core/Hỏi AI phải đo/chặn context model thật.

SDK 2.0 kiểm required/enum/độ dài tham số trước handler: thiếu hẳn prompt/tác
vụ, tác vụ ngoài enum hoặc quá trần khai báo trả `CAI_DAT_BUOC_KHONG_HOP_LE`.
Handler tự kiểm đúng `THIEU_PROMPT`/`TC_SAI_GIAI_DOAN`/ngân sách; prompt trắng
đúng kiểu qua SDK trả `THIEU_PROMPT`. Đây là nợ C-TC-05/SDK 2.1 §7.3; giữ nguyên
manifest/SDK. Không lưu bền/tệp tạm; adapter CoreGia/Local giả chỉ trong tests.
Fixture injection kiểm dữ liệu bất hoạt, chưa chứng nhận model thật. CLI còn
thiếu cấu hình; harness bổ sung không thay cổng chuẩn.

## Đầu vào và cửa nguồn tin cậy

JSON chính có `phien_ban=1,ma_yeu_cau,tac_vu,ngu_canh_core,du_lieu`; xem năm tệp
`demo/yeu-cau-*-DEMO.json` và TC-1-CONTRACT. Năm tác vụ là `phan_loai`, `cat_doan`,
`phan_tich_cau_hoi`, `xep_hang_lai`, `soan_tra_loi`.

- Tham số `bam_yeu_cau` băm bytes chính xác trước parse. JSON chính ≤1 MiB;
  manifest khai **20 MiB** vì SDK dùng trần đó cho mọi `mo_tep` trong bước.
- Từ chối khóa trùng, NaN/Infinity/overflow, UTF-8/surrogate hỏng. Kiểm đường máy/
  URL/base64 ở khóa, định danh/tham chiếu; khóa mở kênh ngoài/SQL/mã thực thi/cờ
  `da_loc_quyen` bị từ chối. Câu hỏi, nguyên văn và giá trị là dữ liệu bất hoạt:
  cho phép URL trong hợp đồng hoặc dấu `/` trong “Chi phí / doanh thu”.
- Tham chiếu `{tep:{tep_id,ten,mime,kich_thuoc},bam}` phải khớp metadata/băm Core.
  Tệp con ≤20 MiB, tổng tệp con thực đọc ≤64 MiB; còn kiểm ngân sách cấu hình
  thấp hơn nếu có. Không cắt ngầm. Nguồn gồm `ma_nguon,phien_ban_nguon,goc,van_ban`;
  `van_ban` là ref tới nguyên phong bì `van_ban_tai_lieu`, không chuỗi thay thế.
- Đối chiếu `bam_dau_vao` OCR với bytes gốc và băm UTF-8 toàn văn với nguồn Core
  đã cấp. Kiểm văn bản ≤500000 ký tự, ≤60 trang, câu hỏi ≤4000, hàm ≤100,
  tổng mục danh mục ≤1000, ứng viên ≤50. Văn bản OCR rỗng bị từ chối.
- Danh mục/metadata/hàm/ứng viên/bằng chứng có thể là nội dung JSON hoặc ref JSON
  khi thuộc trường đã khai; sau mở được ghim thành giá trị trong snapshot. Nguồn
  của ứng viên/tầng 2–3 nằm ở `du_lieu.nguon`, các đoạn khớp nguồn/phiên bản/băm/
  offset. Tầng 1 dùng descriptor và bằng chứng Core cấp, không mở lại gốc/OCR.
- Snapshot lưu nguyên phong bì ở `du_lieu.tai_lieu.van_ban_tai_lieu` hoặc từng
  phần tử `du_lieu.nguon`. `nguon` ở gốc snapshot giữ ref/băm/phiên bản đã kiểm.
  Cấu hình có `{gia_tri,row_version}`, `ket_qua=null`; chưa có kết quả nghiệp vụ.
  Chỉ tải bytes bằng `tai_tep_ra` rồi mới dựng ref. Phong bì ≤64 KiB chỉ có
  tham chiếu+băm và tóm tắt nhỏ, chưa tính thì null.

**C-TC-02/03 chưa có thật.** `app.cua_nguon` là seam để bên chủ Core tích hợp
sau review, không phải API mới đã phát hành của SDK. Runtime hiện không tự gắn
seam, không có adapter giả trong gói. Chỉ tests gắn đối tượng có
`doc_quyen(viec_id)` trả giấy cấp độc lập với JSON:

```text
{ma_yeu_cau,tac_vu,bam_yeu_cau,ngu_canh_core,
 tep:{tep_id:{tep:{tep_id,ten,mime,kich_thuoc},bam}},
 nguon:{ma_nguon:{ma_nguon,phien_ban_nguon,tep_id,bam_goc,bam_van_ban}}}
```

Giấy cấp phải ràng buộc việc/request/task, pháp nhân/module/nhóm/người/thời điểm/
phạm vi và từng nguồn. Core vẫn kiểm quyền sống mỗi lần `mo_tep`. `tep_id`, băm,
prompt hay cờ caller không chứng minh quyền. Thiếu pháp nhân SDK →
`TC_THIEU_NGU_CANH`; thiếu cửa/ngoài phạm vi/quyền → `TC_CHUA_CO_CUA_CORE`;
lệch nguồn/băm/phiên bản → `TC_SAI_NGUON`. Theo lệnh TC-2 mới nhất, pháp nhân
khác phạm vi cũng trả `TC_CHUA_CO_CUA_CORE` (mô hình TC-1 lịch sử dùng mã khác).

Không ghi câu hỏi/toàn văn vào log. Không tạo tệp tạm hoặc kho/cache/sổ trên máy.
Hủy/mất lease/ACK do SDK xử lý; không nhận ACK tải tệp thì không nộp hồ sơ giả.
Tệp đã tải mà việc chưa xong thuộc vòng đời kho Core, chờ C-TC-02.

## Cắt cấu trúc và vị trí nguồn — TC-3

`tra_cuu.cat_doan@1` chỉ nhận `cat_doan/da_nhan`. Cửa `doc_quyen(viec_id)` của
**bên chủ Core** cần cấp lại giấy cho việc mới, có `dau_vao` là nguyên phong bì
đã nhận ở bước trước, `metadata_core` tin cậy, cùng ngữ cảnh/tập `tep`/`nguon`
như trên. Đây là seam chờ C-TC-02/03 review, **chưa là API SDK đã phát hành**.
Không đưa adapter trong tests vào runtime. Thiếu cửa/quyền từ chối
`TC_CHUA_CO_CUA_CORE`; đổi ref/băm/phiên bản/nội dung trả `TC_SAI_NGUON`.

Snapshot, gốc và JSON OCR đều mở bằng `mo_tep`, kiểm băm bytes/kích thước thực.
Giữ nguyên toàn phong bì `van_ban_tai_lieu`; băm bytes gốc riêng với băm UTF-8
toàn văn. Cấu hình dùng `{gia_tri,row_version}` đã ghim từ Ngan ở bước nhận,
không đọc lại cấu hình mới giữa chuỗi. Tham số mục tiêu do SDK cấp (mặc định
2000, nguyên 200…8000); trần đơn vị và số đoạn lấy cấu hình đã ghim.

- Nhận Điều/Khoản, kể cả Unicode NFC/NFD; nhóm các đơn vị cùng Điều tới mục
  tiêu. Đơn vị dài được tách theo câu/khối/xuống dòng/trang; bảng theo nhóm
  hàng không xuyên ô gộp. Không cắt tại ký tự thứ N. Không chia an toàn dưới
  trần đơn vị (mặc định 8000) → `TC_KHONG_CAT_DUOC`; quá 5000 đoạn/ngân sách
  đã ghim → `TC_QUA_GIOI_HAN`, không upload kết quả thiếu đuôi.
- Khối chữ có thể khai `bat_dau,ket_thuc` toàn cục; thiếu thì căn tuần tự
  trong đúng trang, chỉ đi qua khoảng trắng. Số lần xuất hiện trùng không
  được tìm lại từ đầu tài liệu. Trang phân định bằng `\f`; map khối/dòng/từ
  không khớp chữ nguồn bị từ chối. Không bỏ dấu hoặc chuẩn hóa nguyên văn.
- Bảng giữ ô gốc với `hang,cot,gop_hang,gop_cot,van_ban`; phải đủ lưới, kể cả
  ô trống, không chồng ô. Dùng `bat_dau,ket_thuc` của bảng và từng ô, hoặc chỉ
  suy map khi phép chiếu xác định khớp toàn bộ nguồn: ô gốc cùng hàng nối TAB,
  hàng nối LF/CRLF (hàng không có ô gốc là dòng rỗng). Kiểu chiếu khác cần map
  tường minh của Core; không tìm từng giá trị ô rời rạc để đoán vị trí.
- `hang_tieu_de` tùy chọn là danh sách hàng đầu liên tục do nguồn xác định,
  ví dụ `[0]`. Không có thì không tự lấy hàng đầu làm tiêu đề. Tiêu đề lặp có
  `vai_tro=ngu_canh_lap`, cùng map về nguồn; nội dung lần đầu là `noi_dung`.
  Hàng có ô gộp dọc giữ chung. Các trường offset/tiêu đề nằm trong phần mở
  sẵn có của loại v1; không sửa schema chung. DOCX có cấu trúc có thể mang
  `khoi` ở payload, giữ `so_trang=0,trang=[]`, hộp/trang mọi đoạn đều null.

Kết quả ở `snapshot.ket_qua={doan,ban_thuat_toan,do_dai_muc_tieu}`. Mã đoạn là
SHA-256 canonical JSON của phiên bản thuật toán `tc3-cau-truc-1`, descriptor
nguồn (mã/tệp/phiên bản/băm bytes/băm toàn văn) và danh sách vùng + vai trò;
không phụ thuộc mã việc. Mỗi đoạn có nguyên văn, loại khối, nhãn Điều/Khoản,
`nhan_cau_truc`, nguồn và `metadata_core` (nhóm/loại/hiệu lực/duyệt). Không đưa
đề xuất phân loại vào metadata, không tạo confidence hoặc chỉ mục bỏ dấu/vector.

`map_nguon[]` gồm `doan_bat_dau,doan_ket_thuc,ma_nguon,nguon_bat_dau,
nguon_ket_thuc,vai_tro`; mỗi lát Python phải bằng lát toàn văn nguồn tương ứng.
`bat_dau,ket_thuc` trên đoạn chỉ có số khi là **một lát liên tục**; đoạn tổng
hợp tiêu đề lặp dùng null và map từng phần. Ô bảng giữ cả offset toàn văn và
offset trong đoạn. Ghép các vùng `noi_dung` theo thứ tự phải tái dựng đúng đủ
toàn văn, kể cả khoảng trắng/cuối tài liệu/trang rỗng; không tính ngữ cảnh hai lần.

`so_trang` và `vi_tri.trang` là số trang thực hoặc null. Hộp chỉ lấy từ khối/ô
nguồn, không ghép bao hoặc suy hộp từ số ký tự. `vung_vi_tri` giữ từng vùng và
`muc_hop=khoi`: hộp khối có thể bao cả câu, không khẳng định hộp riêng của chữ.
Đoạn qua nhiều trang/khối không có một hộp chung thì để null. Hộp ô thiếu để
null, không mượn hộp bảng. Không phân trang hoặc bịa tọa độ DOCX.

Snapshot đầy đủ/danh sách đoạn chỉ gửi Core bằng `tai_tep_ra`; tóm tắt
`so_doan=len(doan)`, trạng thái `da_cat_doan`, các kết quả chưa chạy giữ null.
Kiểm hủy theo cụm và báo tiến độ câu cố định không nội dung. Chỉ RAM, không tạo
tệp tạm, cấu hình bền, chỉ mục hoặc gọi AI/tìm kiếm. DEMO cố định LF bằng
`e_tra_cuu/.gitattributes` vì băm tệp luôn tính trên bytes, không chữa băm khi đọc.

## Bản khai dự kiến SDK 2.1

`KHAI-SDK-2.1.json` tách khỏi manifest 2.0:

- `cau_hinh`: phạm vi engine, khóa rỗng, không unique bổ sung.
- `dot_kiem`: phạm vi pháp nhân, khóa `ma_dot`, unique `[phap_nhan_id,ma_dot]`;
  chỉ metadata/băm, tử số/mẫu số trong `chi_so`, tham chiếu+băm báo cáo Core.
  Không ghi câu hỏi/nguyên văn, không đặt TTL khi chính sách chưa duyệt.
- Hai màn dự kiến `ui/cau_hinh.js`, `ui/trang_thai.js`, quyền `admin_core`;
  **chưa có mã UI**, làm ở TC-9, dùng `KttCore.engine("e_tra_cuu")` và Core kiểm quyền.

Mọi thao tác `dot_kiem` phải có pháp nhân tin cậy trong `khoa/loc` từng lệnh,
ưu tiên `viec.ngan`; RAM dùng view cùng pháp nhân. Ngăn gốc RAM phục vụ test,
không thay phân quyền Core. Không dùng cursor đổi bảng/bộ lọc/pháp nhân.

## Kiểm từ gốc repo

Python >=3.11. Tạo `.venv` bằng `python -m venv --system-site-packages .venv`
để dùng pytest 9.1.1 có sẵn; không tải mạng. Cài SDK từ wheel trong repo:

```powershell
.venv/Scripts/python -B -m pip install --no-index --no-deps --find-links docs/goi-gui-engine/sdk-2.0.0 --require-hashes -r e_tra_cuu/goi/e_tra_cuu/requirements.lock
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
```

Linux đổi `Scripts/python` thành `bin/python`, đặt hai biến môi trường tương ứng.
Test chặn mạng, chỉ DEMO. Handler nhận/cắt, stub và cổng cấu hình
**đã kiểm bằng Core giả (CoreGia)**; adapter quyền/tệp con chỉ trong tests.
CAS/unique/rollback/pháp nhân/cursor kiểm trực tiếp trên `NganBoNho`.
Symlink của bộ quét kiểm bằng giả lập cờ, không yêu cầu Windows cấp quyền tạo symlink.
Chưa kiểm Core thật, lưu bền, UI thật hoặc Linux.

**Cổng CLI chuẩn chưa đạt:** SDK 2.0.0 chạy cả 5 demo và trả mã 1 vì thiếu
ngăn/cấu hình (`CHUA_CAU_HINH`). Harness bổ sung có 9/9 ĐẠT (5 nhận, 4 nhận → cắt), không
thay kết quả CLI chuẩn. Cần Core C-TC-01/02/03/05; số kiểm thật ở VIEC.md ngoài
gói. Chưa nối Core thật, chưa kiểm RLS/AI/UI/Linux hoặc chất lượng tra cứu.

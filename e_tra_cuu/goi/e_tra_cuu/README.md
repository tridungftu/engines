# Tra cứu tài liệu — TC-7: trả lời có kiểm chứng

Phiên bản 0.1.0, SDK 2.0.0, chưa phát hành. TC-Q13 đã duyệt chiều 15/11/2026.
Manifest đăng ký tám năng lực và bốn loại đúng phiếu §2.1; stub nội bộ
`kiem_khung` đã bỏ. `tra_cuu.nhan_yeu_cau@1` nhận tệp JSON, kiểm và ghim dữ liệu
thành `ho_so_tra_cuu` ở giai đoạn `da_nhan`. `tra_cuu.cat_doan@1` chuyển hồ sơ
`cat_doan/da_nhan` sang `da_cat_doan`. TC-4 chuẩn bị bốn tác vụ Local AI;
TC-5 hậu kiểm phân loại; TC-6 hậu kiểm câu hỏi/hàm và xếp hạng; TC-7 soạn/kiểm
chứng câu trả lời hai đường Python/Local. Xuất còn `CHUA_LAM`, chờ TC-8.
Mọi phân loại máy chỉ là đề xuất cho Core.
Các trạng thái trung gian không xác nhận đã có câu trả lời tầng 1.

Có **5 ví dụ chay_thu_demo**, tệp và băm thật trong `demo/`. Cổng bổ sung ở
`tests/chay_demo_voi_core_gia.py` nạp ngăn/cấu hình, nguồn, giấy cấp quyền giả
rồi chạy 36 DEMO (5 nhận, 4 cắt, 4 chuẩn bị, 11 phân loại/hàng chờ TC-5,
4 hậu kiểm TC-6, 8 trả lời/từ chối TC-7). **Đã kiểm bằng Core giả (CoreGia)**; chưa chứng nhận
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

## Hậu kiểm Local — TC-6

`phan_tich_cau_hoi@1` và `xep_hang_lai@1` chỉ nhận `tra_loi_ai` Local, khôi
phục snapshot `cho_ai` bằng `mo_tep`, kiểm metadata/băm bytes/quyền/cấu hình
đã ghim và toàn bộ nguồn. Tái dựng ngữ cảnh/map/khuôn/ngân sách TC-4; so
prompt/phiên bản/tác vụ/chuyển tiếp và `bam_dau_vao` trên **toàn phong bì
yeu_cau_ai canonical**. Không tin `kiem_trich_dan.dat`: quote phải khớp nguyên
văn/offset trong vùng map; nhãn kỹ thuật không là chứng cứ. Lỗi/sai khuôn
không trả XONG rỗng; Cloud `TC_CHI_LOCAL`, nguồn lệch `TC_SAI_NGUON`.

Seam `doc_quyen(viec_id)` cần cấp lại `dau_vao` nguyên phản hồi và quyền
snapshot/gốc/OCR. Riêng TC-6 bổ sung metadata **ngoài payload người gửi**:

```json
{"phan_giai_cau_hoi": {
  "bam_cau_hoi": "sha256:<băm UTF-8 câu hỏi>",
  "thuc_the": [{"loai":"khoan_vay","ma":"0007","gia_tri":"0007"}],
  "y_dinh": [{"ma":"gia_tri","cum_tu":["Giá trị","Số tiền"],"phu_thuoc_thoi_diem":false}],
  "can_lam_ro": false,
  "ham": {"m9.gia_tri": {
    "phien_ban":"1", "y_dinh":["gia_tri"], "trang_thai":"chua_chay", "moc_cong_bo":null,
    "rang_buoc":{"ma_khoan_vay":{"loai":"thuc_the","loai_thuc_the":"khoan_vay","truong":"ma"}}
  }}
}}
```

Ví dụ trên là mô tả cấu trúc, không phải fixture băm/tệp hợp lệ. Metadata
phân giải ≤64 KiB, mỗi danh sách thực thể/ý định ≤1000. Đây là **quy ước tạm
cho adapter CoreGia**, chưa phải API C-TC-03/SDK đã phát hành; runtime không
có cửa/thiếu metadata phải từ chối `TC_CHUA_CO_CUA_CORE`. Core phải cấp danh
mục thực thể đúng quyền/đủ cho câu hỏi, bộ ý định đã duyệt và cờ cần làm rõ
khi gặp tham chiếu chưa phân giải. Không lấy model tự khai danh mục này.

- Thực thể khớp **nguyên chuỗi với ranh giới mã** trong câu hỏi; giữ Unicode,
  kiểu chuỗi và số 0 đầu. Căn cứ thực thể/ý định là offset câu hỏi được quote
  thực sự bao phủ. Phản hồi phải có đúng tập thực thể, không thêm/bớt/trùng.
- Ý định chỉ xác nhận khi đúng một bộ cụm từ Core cấp khớp câu hỏi. Không
  khớp/nhiều ý định → `y_dinh=can_lam_ro`; chưa có thực thể, nhiều thực thể
  cùng loại, cùng span trỏ nhiều đối tượng hoặc Core yêu cầu làm rõ thì
  `can_lam_ro=true`, bỏ mọi đề xuất hàm. Đây là kiểm literal bảo thủ; chưa
  chứng minh hiểu ngữ nghĩa tổng quát hoặc chất lượng model thật.
- Cờ thời điểm = cụm thời gian tương đối trong câu hỏi hoặc chính sách ý định
  Core cấp; model không được sửa. “Tháng này” dùng năm/tháng/múi giờ của
  `ngu_canh_core.thoi_diem`, có ngày đầu/cuối tháng thực, không giờ máy.
- Hàm phải đúng allowlist tên/phiên bản và ý định; tham số theo khuôn đã ghim
  và schema Core, kín cả object con/ref nội bộ. Kiểm kiểu/range/enum/const,
  composition/array và phạm vi pháp nhân/nhóm/module/người/ma_pham_vi.
  Mỗi tham số phải có binding Core: `thuc_the` như ví dụ; `ngu_canh` gồm
  `{loai,truong}`; hoặc `gia_tri` gồm `{loai,cho_phep:[...giá trị chính xác...]}`.
  Binding thực thể/ngữ cảnh luôn phải được truyền, không bỏ để mở rộng phạm vi.
  SQL/code/URL/hàm lạ/khóa thừa → `TC_HAM_KHONG_DUOC_PHEP` hoặc `TC_AI_SAI_KHUON`.
- `ham.trang_thai` Core cấp: `chua_chay` → `cho`, `khong_kha_dung` giữ nguyên,
  `kha_dung` → `de_xuat_cho_core`. `tang_1` chỉ có trạng thái/lý do, không giá
  trị nghiệp vụ giả; hàm chưa chạy/không khả dụng đề nghị Core chọn tầng 2.
  Không hàm/truy vấn/module nào được thực thi trong engine.

Xếp hạng bắt buộc đủ đúng tập mã ứng viên, mỗi mã một lần; điểm số hữu hạn
đúng thang đã ghim. Kết quả sắp điểm giảm, bằng điểm giữ **thứ tự gốc Core**,
không theo thứ tự model gửi. Mỗi hàng kết quả chép nguyên ứng viên gốc, chỉ
thêm `diem_xep_hang`; không nhận model viết lại nguồn/phiên bản/nội dung.
Điểm chỉ thứ tự, không là độ tin cậy đã duyệt. Quá 50 từ chối tại nhận;
quá ngân sách đã ghim từ chối `TC_QUA_NGAN_SACH_AI`, không top-k ngầm.
**0 ứng viên:** Core rẽ nhánh từ `da_nhan`; handler chuẩn bị từ chối nhánh AI
rỗng sau kiểm nguồn, không upload snapshot AI/phản hồi giả.

Với xếp hạng, giấy cấp có `phu_thuoc_thoi_diem` boolean từ Core; kết hợp
cụm thời điểm trong câu hỏi để cấm dùng lại cache cho câu thời điểm. Cả hai
kết quả giữ `phu_thuoc_cache` gồm **nguyên tập nguồn**, thực thể, ngữ cảnh
Core, hàm/phiên bản/mốc công bố và cờ thời điểm. `duoc_tai_dung_cache` chỉ
false khi phụ thuộc thời điểm, còn lại null vì Core chưa kiểm quyền/cache.
Phân tích còn lưu băm metadata phân giải Core để truy vết.

Kết quả/snapshot chỉ tải Core và kiểm ACK trước trả hồ sơ `da_phan_tich` /
`da_xep_hang`; tóm tắt `co_can_cu,nhan` tiếp tục null. Hủy kiểm theo cụm;
ChuaRo/mất lease/ACK sai không báo XONG. Không tạo tệp tạm, cache, chỉ mục,
nhật ký câu hỏi hay tệp cấu hình trên máy. Cấu hình lấy snapshot Ngan đã ghim.
RLS phải lọc **trước khi ứng viên vào engine/AI**, Core giả không chứng minh
RLS thật. TC-6 dùng phản hồi Local giả theo protocol do CoreGia điều phối;
0 model/provider thật. Chưa kiểm nối thật C-TC-02/03 hoặc chất lượng AI.

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

## Hậu kiểm phân loại — TC-5

`tra_cuu.phan_loai_tai_lieu@1`: `tra_loi_ai` → `ho_so_tra_cuu`, trạng thái
`da_phan_loai` hoặc `cho_phan_loai`. Không tham số thay nguồn/ngưỡng giữa lượt.
Hàng chờ có lý do là kết quả nghiệp vụ, không có nghĩa đã xếp hoặc tạo K5.
Không tạo danh mục/thư mục, chuyển hồ sơ hoặc ghi ngăn từ handler này.

Cửa nguồn tin cậy **chưa có trong SDK 2.0** vẫn là dependency
`app.cua_nguon.doc_quyen(viec_id)`, chỉ tests gắn CoreGia. Ngoài request/task,
`ngu_canh_core`, các ref và nguồn đã cấp, bước này cần:

- `yeu_cau_ai`: nguyên phong bì yêu cầu do Core nhận từ TC-4, độc lập phản hồi;
- `nguon_ai={nha_cung_cap,model,phien_ban_engine}`: provenance bước Hỏi AI do
  Core cấp. Không lấy từ JSON caller/model rồi tự coi đã xác thực.

Thiếu cửa/provenance/quyền tệp con trả `TC_CHUA_CO_CUA_CORE`. Chuyển tiếp,
prompt/version/model/nguồn/băm lệch trả `TC_SAI_NGUON`; Cloud trả `TC_CHI_LOCAL`
trước khi mở tệp. Khuôn phân loại đóng đúng bảy trường TC-4, mã chỉ trong danh
mục và loại hoạt động, điểm hữu hạn 0…1, bool không là số; sai trả
`TC_AI_SAI_KHUON`. Loại không hoạt động phải để null theo khuôn; Python nhận
diện nhánh đó và trả hàng chờ. Model cố trả mã loại đã bị loại khỏi enum bị
từ chối sai khuôn, không giả là đã chọn loại hợp lệ.

Snapshot/gốc/OCR mở qua Core, kiểm lại bytes/băm/phiên bản, ngữ cảnh/cấu hình
đã ghim. Dựng lại toàn bộ ngữ cảnh/khuôn/map/mã đoạn và yêu cầu canonical;
so băm yêu cầu AI-2. Tự kiểm cả trích dẫn ngoài và `du_lieu.can_cu`: nguyên văn,
offset Unicode/map/vùng nguồn đúng; nhãn kỹ thuật/danh mục không là chứng cứ.
Đổi mã nguồn/đoạn trả `TC_SAI_NGUON`, quote/offset sai trả `TC_AI_SAI_KHUON`.
Không phụ thuộc riêng `kiem_trich_dan.dat`. Phản hồi báo không căn cứ vẫn chờ;
không dùng việc tự kiểm quote để giả rằng upstream đã xác nhận đầy đủ.

Bộ quy tắc nghiệp vụ là tài nguyên JSON Core cấp theo
`cau_hinh.gia_tri.quy_tac_nhom={tep_id,bam}` đã ghim, không có bộ mặc định
trong runtime. Bộ miền phiên bản 1 (không phải loại dữ liệu/API SDK mới):

| Trường | Nội dung Core phải ghim và cấp quyền |
|---|---|
| `phien_ban` | Integer 1 |
| `phap_nhan[]` | `{ma,loai_hinh,dau_hieu_ben_ky[]}`; CP/TNHH trong danh mục; dấu hiệu là cả dòng bên ký, không tên được nhắc trong câu kể |
| `loai[]` | `{ma,quy_tac,loai_hinh[],dau_hieu[]}`; mã loại phải thuộc snapshot và nhóm đúng quy tắc cố định Python; `loai_hinh=[]` nghĩa dùng chung |
| `doi_tuong[]` | `{ma,nhom[],loai[],dau_hieu[],thong_tin_cong_trinh}`; mã trong danh mục, liên kết đúng nhóm/loại; dấu hiệu nguồn phải chứng minh công trình/tài sản cụ thể, không chỉ cờ |
| `quy_che_khac[]` | Dấu hiệu cho đề xuất ở gốc 08, không phải mã loại/thư mục mới |
| `phep_do` | null, hoặc `{bam_bo_do,ma_prompt,phien_ban_prompt,model,phien_ban_engine_ai}` khớp bản ngưỡng đã đo và provenance AI |

`quy_tac` chỉ nhận `cong_trinh,thiet_bi_lap_dat,vat_tu_cdt_cap,sua_chua_bao_tri,
thue_may,mua_hang,quy_che_lao_dong,quy_che_khac,nhan_su,phap_ly_du_an,vay,
ban_nha,kcn,ban_nhua,ban_dien_doc_lap,phap_ly_cong_ty`. Bộ có mã/quy tắc/quan
hệ sai bị từ chối, không nhận quy tắc thực thi hoặc import bộ từ repo chung.

Python ưu tiên 04 cho công trình/thiết bị lắp/vật tư cấp/sửa chữa có thông tin
công trình; thuê máy thi công vẫn 03; quy chế người lao động 07, quy chế khác
08. Không lấy thiếu BOQ để suy 03. Thiếu công trình/đối tượng/bên ký, CP/TNHH
không phù hợp, hỗn hợp, nhánh chưa bật/ngừng, ngoài phạm vi hoặc chưa có
ngưỡng đo đúng model/prompt đều chờ. Dấu hiệu phải có trong một câu trích đã
kiểm; toàn văn dùng phát hiện bản chất bị model bỏ sót. Không nối các lát xa
nhau làm câu mới. So khớp dấu hiệu dùng NFC/casefold trên bản tạm; không đổi
văn bản hoặc offset nguyên bản. Đây là quy tắc đề xuất có giới hạn, chưa là
số đo chất lượng hay bảo đảm hiểu mọi phủ định/ngữ nghĩa tài liệu thật.

Điểm giữ ở `diem`, `kiem_tra.diem_la_xac_suat=false`, xác suất hiệu chỉnh null.
`da_phan_loai` vẫn `can_duyet=true`, không phải lệnh tự xếp. Nhóm 08 có thể đề
xuất gốc với loại/đối tượng null; không tích lũy tài liệu tạo loại. Phụ lục đổi
nhóm hoặc bản chất loại chỉ đề nghị chuyển cả bộ khi có quan hệ Core/mã bộ và
căn cứ; trạng thái luôn chờ. Core duyệt/chuyển/ghi nhật ký, engine chỉ xuất
tham chiếu và đề nghị. `can_cu` sau kiểm chứa offset nguồn, offset AI và
descriptor nguồn/băm/phiên bản; `kiem_tra` giữ lý do cố định, không phản chiếu
chuỗi tự do của model vào cảnh báo.

**Giới hạn nối Hỏi AI:** consumer AI-2 0.5.0 hiện kiểm mọi lá `du_lieu`
(kể cả mã/điểm/offset/boolean) như giá trị phải xuất hiện nguyên văn trong
trích dẫn. Test nối consumer có thật với Local giả nhận `XONG` ở Hỏi AI nhưng
`khong_thay_can_cu`/`DU_LIEU_NGOAI_TRICH_DAN`; TC-5 trả hàng chờ đúng lý do,
không sửa response để làm xanh. Lead Hỏi AI/Core cần rà cách kiểm metadata
và giá trị nghiệp vụ (Cần Core/L-TC-01 trong VIEC). Các ca đề xuất tám nhóm
dùng phản hồi fixture DEMO hợp lệ độc lập; không chứng nhận nối model thật.

## Bản khai dự kiến SDK 2.1

`KHAI-SDK-2.1.json` tách khỏi manifest 2.0:

- `cau_hinh`: phạm vi engine, khóa rỗng, không unique bổ sung.
- `dot_kiem`: phạm vi pháp nhân, khóa `ma_dot`, unique `[phap_nhan_id,ma_dot]`;
  chỉ metadata/băm, tử số/mẫu số trong `chi_so`, tham chiếu+băm báo cáo Core.
  Không ghi câu hỏi/nguyên văn, không đặt TTL khi chính sách chưa duyệt.
- Hai màn TC-9 `ui/cau_hinh.js`, `ui/trang_thai.js` dùng
  `KttCore.engine("e_tra_cuu")`. Cấu hình cần `admin_core`; trạng thái đề nghị
  quyền riêng `xem_dot_kiem_theo_phap_nhan`, Core kiểm quyền từng truy vấn.
  Tên quyền này là **bản khai đề nghị**, chưa có SDK/Core thật; Core chưa hỗ trợ
  thì không mở màn, không thay bằng quyền Admin toàn engine cho người xem.

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
node --test e_tra_cuu/tests/ui/*.test.js
```

Linux đổi `Scripts/python` thành `bin/python`, đặt hai biến môi trường tương ứng.
Test chặn mạng, chỉ DEMO. Handler nhận/cắt/chuẩn bị/hậu kiểm TC-5…7, stub và cổng cấu hình
**đã kiểm bằng Core giả (CoreGia)**; adapter quyền/tệp con chỉ trong tests.
CAS/unique/rollback/pháp nhân/cursor kiểm trên `NganBoNho`; seam TC-9 cũng
được gọi qua handler chỉ có trong test CoreGia. Node 24.18.0 chạy test DOM/
KttCore giả không mạng, không cần npm/dependency. Chưa kiểm trình duyệt thật.
Symlink của bộ quét kiểm bằng giả lập cờ, không yêu cầu Windows cấp quyền tạo symlink.
Chưa kiểm Core thật, lưu bền, UI thật hoặc Linux.

**Cổng CLI chuẩn chưa đạt:** SDK 2.0.0 chạy cả 5 demo và trả mã 1 vì thiếu
ngăn/cấu hình (`CHUA_CAU_HINH`). Harness bổ sung có 43/43 ĐẠT, không
thay kết quả CLI chuẩn. Cần Core C-TC-01/02/03/05; số kiểm thật ở VIEC.md ngoài
gói. Chưa nối Core thật, chưa kiểm RLS/AI/UI thật/Linux hoặc chất lượng tra cứu.

## Màn cấu hình/trạng thái — TC-9

Core nạp module ES và gọi `mount(goc, {KttCore})`; màn trạng thái nhận thêm
`phapNhanId` từ ngữ cảnh host Core đã cấp quyền. Host đổi pháp nhân phải gọi
`unmount()` rồi mount lại; không lấy pháp nhân từ query string hoặc mã bài đo.
Hàm trả về có `unmount()` để gỡ sự kiện, bỏ các response đến sau khi đóng màn.
Trạng thái chỉ dùng `.ngan.tim/.doc("dot_kiem", ...)`, mỗi truy vấn có
`phap_nhan_id` trong `loc/khoa`, tối đa 500 bản/trang. Cursor chỉ được dùng
trong màn/phạm vi đã nhận; Core vẫn phải xác thực cursor và quyền mỗi lần.
Lỗi 401/403 xóa dữ liệu đang hiển thị; lỗi đọc phần nào báo tại phần đó.
Không có cây kho, hỏi đáp, K5, mạng ngoài hoặc quyền ghi bài đo từ UI.

Màn cấu hình dùng `.cau_hinh.doc()` → `null` hoặc
`{gia_tri,phien_ban_cau_hinh}`; `.luu(gia_tri,phien_ban_cau_hinh)` nhận
`null` khi tạo lần đầu, phiên bản đã đọc khi sửa. Đây là quy ước KttCore giả
chờ đối chiếu SDK thật. Không tự ghi default khi mở màn; Core kiểm lại schema.
CAS 409 đọc lại, yêu cầu Anh kiểm tra và lưu lại, không retry/ghi đè tự động.
Ngưỡng chưa đo không có số mặc định; ngưỡng đã đo chỉ đọc, không có nút kích hoạt
hoặc ô URL/model/khóa AI. Các giới hạn/mục tiêu bám schema đóng gói, có test so.

`trang_thai.py` cung cấp seam thuần `lay_hoac_tao_dot` và
`cap_nhat_cac_dot`; `chay.ghi_bai_do_demo(viec,ung_dung,...)` lấy pháp nhân
từ ngữ cảnh việc, ưu tiên ngăn việc, fallback view RAM cùng pháp nhân.
**Không đăng ký thao tác quản trị hoặc năng lực mới**, không tự ghi khi xuất
kết quả TC-8. Core phải xác thực quyền, nguồn báo cáo và gọi seam khi có cửa
chung; mã/băm/`ma_dot` không chứng minh danh tính/quyền đọc tệp báo cáo.

Bài đo dùng mã `DEMO-...`; dữ liệu đóng theo bản khai, bốn chỉ số
`tra_loi_dung,trich_dan_dung,tu_choi_dung,phan_loai_dung` đều `null` hoặc
`{tu_so,mau_so}` nguyên không âm, tử số không vượt mẫu số. `null`/mẫu số 0
hiện “Chưa đo”; không gộp tỷ lệ hoặc lấy điểm model làm accuracy. Trạng thái
`chua_do` chỉ chứa các chỉ số null; `da_do` cần ít nhất một mẫu số dương và
báo cáo Core. Báo cáo chỉ giữ đối tượng tệp (`ten=bao-cao-DEMO.json`) + băm,
không nội dung câu hỏi/tài liệu. Tham chiếu thật/băm thật do CoreGia tạo trong
test, chưa chứng minh cửa ghi bài đo thật. Sửa nhận ảnh số đo tuyệt đối cùng
`row_version` trong một lô ≤100; lệch một mục hủy cả lô, đọc lại/thử lại có chủ ý.
Gửi lại cùng khóa tạo trả bản cũ, không cộng số đếm và không sửa bản cũ ngầm.

Đã kiểm bằng Core giả (CoreGia)/NganBoNho/KttCore giả; chưa kiểm trình duyệt thật,
SDK 2.1, lưu bền/RLS hay chất lượng model. Tất cả chỉ DEMO, 0 Cloud. Runtime/UI
không tạo tệp cấu hình, sổ, cache hoặc tệp tạm. Hai mẫu NGAN-0 giữ nguyên.

## TC-7 — Bằng chứng trả lời do Core cấp

TC-Q14 đã duyệt 15/11 chiều: Xanh chỉ Python tầng 1 đã duyệt/còn hiệu lực,
đủ ngưỡng đo đã duyệt và đúng trường/thực thể. Có LLM hoặc văn bản mới chờ
duyệt tối đa Vàng. Không căn cứ/số sai/trích sai thì bỏ lời đề xuất, trả câu
Việt không số và nhãn null. Mâu thuẫn hợp lệ giữ cả hai nguồn/giá trị, cờ
cần duyệt; dữ liệu mới tầng 2/3 chỉ đề nghị K5, chưa xác nhận lưu/duyệt.

Seam tạm C-TC-03 `doc_quyen(viec_id)` cần cấp ngoài payload thêm
`kiem_chung_tra_loi` với các khóa đóng `phien_ban=1`, `trang_thai_nguon=da_tra`,
`bam_du_lieu`, `truong_can_tra_loi`, `nguong_tin_cay`,
`phu_thuoc_thoi_diem`, `bang_chung`. Thiếu seam trả lỗi, không tin cờ caller.
Ngưỡng null/chưa đo/chưa duyệt không đủ tầng 1; cấu hình engine vẫn từ Ngan,
không tự tạo ngưỡng hoặc tệp cấu hình riêng. Đây chưa phải API SDK thật.

Mỗi quan hệ bằng chứng có đúng các khóa `nguon`, `thuc_the`, `truong`,
`kieu`, `gia_tri`, `don_vi`, `quy_tac`, `hien_thi`, `cau`, `bat_dau`,
`ket_thuc`, `vi_tri_gia_tri`, `vi_tri`, `trang_thai_duyet`, `con_hieu_luc`,
`do_tin_cay`, `moc_cong_bo`, `moc_duyet`, `hieu_luc_tu`, `hieu_luc_den`.
`truong_can_tra_loi` là các `{ma,ten,kieu,don_vi}`; ngưỡng là null hoặc
`{trang_thai,gia_tri,bam_bo_do,da_duyet}`. Mỗi locator `vi_tri` chứa
`{trang,hop,dieu}`, `vi_tri_gia_tri=[a,z]` là offset nguồn Unicode tuyệt đối.
Tầng 1 dùng quote/locator đã duyệt đi cùng trường Core, không mở lại tệp.
Tầng 2/3 tự map quote/offset và trang/hộp/Điều về nguồn thực.

Chỉ nhận mẫu `Tên trường (thực thể): giá trị.`; ví dụ
`Giá trị (DEMO-VAY-A): 1.000.000 VND.`. Cụm thực thể và nhãn trường phải có
trong quote. Các quy tắc khai rõ: `tien_chuan`, `tien_nhom_ba`, `so_chuan`,
`ngay_iso`, `ngay_viet`, `nguyen_van`, `co_khong`. Tiền int/chuỗi Decimal
kèm tiền tệ, không float/tỷ giá/tổng/tỷ lệ hoặc đổi đơn vị tự suy. Diễn giải
ngoài mẫu hoặc binding thiếu không được xem là đã chứng minh ngữ nghĩa.
Không lấy văn bản tự do ngoài `du_lieu` của Hỏi AI làm câu trả lời nghiệp vụ.

Lớp bọc chuẩn bị AI tầng 1 chỉ mở khi Core cấp profile đủ điều kiện, ghim nó
trong snapshot `kiem_chung_core`, kiểm lại khi hậu kiểm; đầu ra vẫn Vàng.
Tập nguồn/phiên bản/mốc duyệt/công bố, thực thể/phạm vi/cờ thời điểm xuất cho
Core quản cache; engine không tạo cache/K5 hay tự chạy tầng tiếp. Adapter
tầng 3 DEMO không chứng minh OCR/TX hoặc ba tầng thật đã chạy.

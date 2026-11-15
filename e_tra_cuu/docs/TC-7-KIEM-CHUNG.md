# TC-7 — Hai đường trả lời và ranh giới kiểm chứng

Ngày 15/11/2026; 5 giờ **ƯỚC TÍNH** trong phiếu. Đã kiểm bằng Core giả
(CoreGia), NganBoNho và Local giả theo protocol; 0 Cloud/model thật. Không
chứng nhận RLS, tìm lai, OCR/TX, ba tầng hoặc K5/cache thật đã chạy.

## Phạm vi và nhãn

TC-7 ban đầu có bốn tệp runtime: `tra_loi.py`, `kiem_chung.py`, `bang_chung.py`,
`chay.py`. Vòng sửa theo kiểm độc lập của lead lúc 15:52 ngày 15/11/2026 chỉ
sửa `kiem_chung.py`, `tra_loi.py`; giữ nguyên `bang_chung.py`, `chay.py`.
`soan_tra_loi@1` nhận `ho_so_tra_cuu/da_nhan` hoặc `tra_loi_ai` Local khớp
snapshot `cho_ai`; chỉ trả `ho_so_tra_cuu/da_soan` khi Core ACK upload.
Tóm tắt khớp kết quả thực; không lưu ngăn/kho/cache thứ hai hay tệp cục bộ.

TC-Q14 **đã duyệt** theo quyết định chiều 15/11: Python tầng 1 đã duyệt,
còn hiệu lực, đủ ngưỡng đo được duyệt, đúng trường/thực thể và không cờ chờ
mới Xanh. AI tầng 1/2/3 tối đa Vàng. Văn bản mới chờ duyệt có cảnh báo và
tối đa Vàng. Model không có trường cấp nhãn/duyệt trong khuôn.

Đường Python chỉ điền mẫu từ trường đã kiểm hoặc trả câu Việt không số,
`nhan=null`. Hồ sơ có đoạn tầng 2/3 nhưng chưa qua AI không được tự chèn văn
bản xin Xanh. Không đủ tầng 1 có mã lý do để Core chọn bước tiếp; không tự
gọi AI/OCR/TX hay truy vấn tầng khác. Nguồn lỗi/thiếu quyền/chưa rõ không
được đổi thành `khong_thay_can_cu` thành công.

## Seam C-TC-03 tạm, chưa phải API SDK đã phát hành

Cửa `app.cua_nguon.doc_quyen(viec_id)` được chủ Core gắn ngoài payload như
TC-2/6, kiểm nguyên đầu vào/ngữ cảnh/nguồn/ref mỗi việc. TC-7 cần thêm
`kiem_chung_tra_loi` từ cửa này; thiếu trả `TC_CHUA_CO_CUA_CORE`. Không lấy
profile từ caller/model, không tạo endpoint hay sửa contract chung.

Profile đóng có các khóa:

| Khóa | Nội dung |
|---|---|
| `phien_ban` | Số nguyên 1 |
| `trang_thai_nguon` | Chỉ `da_tra` là nguồn đã trả thành công; trạng thái khác từ chối; nguồn đang nhận do adapter/tầng sở hữu ném `ChuaRo` |
| `bam_du_lieu` | Băm JSON canonical của **du_lieu trong snapshot đã nhận**, gồm nguồn đã nạp nếu tầng 2/3 |
| `truong_can_tra_loi` | Danh sách đóng `{ma,ten,kieu,don_vi}` do Core/module xác định từ câu hỏi; không do model chọn |
| `nguong_tin_cay` | `null` nếu chưa có; hoặc `{trang_thai,gia_tri,bam_bo_do,da_duyet}`. Tầng 1 cần `da_do`, `da_duyet=true` và từng điểm không dưới ngưỡng. Số trong test chỉ DEMO, không là phép đo model thật |
| `phu_thuoc_thoi_diem` | Boolean tin cậy; kết hợp cờ Core và dấu hiệu câu hỏi để đề nghị không tái dùng cache |
| `bang_chung` | Danh sách quan hệ trường/thực thể có nguồn và vị trí bên dưới; không thay thế đoạn văn bằng một cờ đúng/sai |

Mỗi bằng chứng có đúng các khóa:

`nguon`, `thuc_the`, `truong`, `kieu`, `gia_tri`, `don_vi`, `quy_tac`,
`hien_thi`, `cau`, `bat_dau`, `ket_thuc`, `vi_tri_gia_tri`, `vi_tri`,
`trang_thai_duyet`, `con_hieu_luc`, `do_tin_cay`, `moc_cong_bo`, `moc_duyet`,
`hieu_luc_tu`, `hieu_luc_den`.

- `nguon` là descriptor TC-2 nguyên trạng; `thuc_the` nguyên `{loai,ma,gia_tri}`,
  không bỏ số 0 đầu/đổi hoa thường. Cụm thực thể phải có nguyên vẹn trong câu
  hỏi và quote. Thực thể và nhãn trường phải liên kết với **đúng vị trí giá
  trị**, theo quy tắc đoạn bên dưới. Core chịu trách nhiệm cấp **quan hệ
  nghiệp vụ đã xác thực**; engine vẫn kiểm liên kết trong quote, không tin
  riêng profile hoặc sự xuất hiện của tên/nhãn ở đâu đó trong cùng câu.
- `vi_tri_gia_tri=[a,z]` là offset Unicode tuyệt đối trong văn bản nguồn,
  `[bat_dau,ket_thuc)` là quote liên tục; lát ở vị trí giá trị phải khớp toàn
  bộ `hien_thi`, có ranh giới, không nhận `5` trong `5.000.000`.
- `vi_tri={trang,hop,dieu}` giữ trang/hộp thực hoặc null, nhãn Điều lấy từ
  cấu trúc dòng nguồn. Tầng 2/3 kiểm trên văn bản thực qua `mo_tep`, tái dùng
  map TC-3 và đối chiếu đoạn đã cấp; trang tồn tại nhưng sai đoạn vẫn không
  đạt. Tầng 1 dùng **trích dẫn đã duyệt đi cùng trường Core cấp**, kiểm kiểu
  locator và provenance; theo QĐ-4 không mở lại gốc/OCR mỗi câu.
- Hiệu lực xét boolean và ngày bắt đầu/kết thúc theo thời điểm Core; công
  bố/duyệt ở tương lai không thành dữ liệu tầng 1 hợp lệ. Mốc duyệt nullable
  chỉ cho nguồn chưa duyệt; tầng 1 thiếu mốc duyệt thì không đủ.
- `tu_choi` ở mọi tầng: loại khỏi căn cứ và mâu thuẫn, lý do
  `BANG_CHUNG_BI_TU_CHOI`, không có căn cứ/nhãn null. Cả ba tầng đều xét mốc
  duyệt, độ tin cậy và ngưỡng đã đo/được duyệt. Tầng 1 chưa đủ thì từ chối;
  tầng 2/3 có quan hệ đúng nhưng chờ duyệt, dưới ngưỡng hoặc thiếu ngưỡng chỉ
  được Vàng/cần duyệt, giữ `CHUA_DUYET`, `DUOI_NGUONG_TIN_CAY`,
  `THIEU_NGUONG_DA_DO` trong `ly_do` và câu Việt trong `canh_bao`. Những lý
  do này không được miễn kiểm quan hệ/giá trị/nguồn hoặc phản hồi AI.
- Profile/nguồn sai metadata hoặc băm trả `TC_SAI_NGUON`; Cloud trả
  `TC_CHI_LOCAL`; khuôn phản hồi AI sai trả `TC_AI_SAI_KHUON`. Quan hệ/trích
  dẫn/vị trí/giá trị không đạt trả `khong_thay_can_cu`, xóa toàn bộ khẳng định
  khỏi **câu trả lời**, không giữ lời bịa dưới nhãn Vàng.

## Bổ sung sau kiểm độc lập KHÔNG ĐẠT — 15/11/2026

1. **Thực thể gần nhất trước giá trị.** Chỉ xét đoạn cùng dòng/mệnh đề/ô:
   LF/CRLF, ngắt trang, TAB, `|`, chấm câu ngoài số, `;`, `!`, `?`, và các
   liên từ phân tách đã khai là ranh giới. Dấu phẩy cho phép nhiều trường
   của cùng thực thể; thực thể khác xuất hiện trước giá trị sẽ chặn kế thừa.
   Không dùng thực thể nằm sau giá trị. Cả mã dạng ghép và đầu mục thực thể
   khác trong quote đều chặn, kể cả không thuộc tập thực thể của câu hỏi.
   Tầng 2/3 còn giới hạn theo map khối/ô TC-3 đã kiểm, kể cả nguồn ghép ô chỉ
   bằng dấu cách. Không kế thừa từ ô bên cạnh hoặc tự suy từ tiêu đề bảng.
2. **Nhãn trường gần nhất trước giá trị.** Nhận nhãn Core cấp và bộ cụm từ
   giới hạn trong `_NHAN_TRUONG`: ngày ký, hiệu lực, hạn trả, giải ngân,
   ngày chung, giá trị/số tiền, lãi suất, số lượng, diện tích, khối lượng.
   Nhãn cạnh tranh vẫn được xét dù câu hỏi chỉ yêu cầu một trường. Cụm dài
   như `hạn trả ngày` thắng `ngày` nằm bên trong. Hai trường cùng nhãn ở
   cùng vị trí là mơ hồ, không chọn theo thứ tự mảng. Từ nối chỉ cho nhóm
   cố định (`là`, `bằng`, `ở mức` và dấu phân cách); nhãn/từ lạ giữa quan hệ
   và giá trị không được suy diễn. Không lấy nhãn của giá trị trước cho thực
   thể mới; nhãn xuất hiện sau giá trị không chứng minh được trường.
3. **Duyệt/độ tin cậy mọi tầng.** Phân biệt lý do cần duyệt ở tầng 2/3 với
   lý do chặn trả lời; bằng chứng bị từ chối, sai quan hệ, hết hiệu lực hoặc
   AI không khớp luôn làm kết quả không có căn cứ. Ngưỡng so bằng Decimal;
   điểm bằng ngưỡng vẫn đủ. Không có nhánh nâng bằng chứng chờ duyệt thành
   Xanh hoặc tự duyệt K5.
4. **Không bỏ đơn vị/quy mô.** Hậu tố `%`, `‰`, tiền tệ, nghìn/ngàn/triệu/
   tỷ/tỉ/đồng, đơn vị đo (kể cả m²/m³), khoảng trắng Unicode và đơn vị trong
   ngoặc được xét ngoài span giá trị. Số kiểu `so` chưa khai `don_vi` mà
   ngay sau có từ cũng bị từ chối, kể cả đơn vị chưa nằm trong danh sách.
   Chỉ giữ `triệu` mà bỏ `VND`, hoặc cắt quote ngay trước hậu tố, không đạt.
   Quote của số/tiền phải có ngữ cảnh sau giá trị; dừng đúng cuối giá trị
   chưa chứng minh đã lấy đủ cụm nên bị từ chối. Tầng 2/3 kiểm thêm trên
   toàn văn thực. `so_chuan` nhận đơn vị khai rõ viết sát số hoặc cách một
   dấu trắng nếu khớp nguồn từng ký tự; không quy đổi quy mô/tiền tệ.

Vi phạm/mơ hồ ở (1), (2), (4) trả `QUAN_HE_GIA_TRI_KHONG_DAT`,
`khong_thay_can_cu`, nhãn null, không giữ số trong câu trả lời. Đây là ngữ
pháp hạn chế để từ chối khi chưa chứng minh được, chưa là bộ phân giải
ngôn ngữ tự nhiên; nguồn ngoài ngữ pháp cần binding/cụm từ được review.

Test hồi quy riêng: `tests/test_kiem_chung_tc_7.py`, tham số hóa tầng 1/2/3,
hai dòng/hai thực thể trong một ô, đổi thứ tự thực thể/giá trị, ô liền nhau,
ba ngày và nhãn chỉ một trường, trạng thái duyệt/ngưỡng, đơn vị bị bỏ và
quote bị cắt. Có ca đúng giữ Xanh/Vàng, số trần thực sự không có đơn vị,
đơn vị khai tường minh và điểm bằng ngưỡng. Số kiểm/thời gian vòng sửa tại
`VIEC.md`; toàn bộ **đã kiểm bằng Core giả (CoreGia)**, 0 Cloud/model thật.

## Mẫu diễn đạt và giới hạn có chủ ý

Đợt này chỉ nhận mẫu xác định `Tên trường (thực thể): giá trị.` cho từng
khẳng định. Ví dụ: `Giá trị (DEMO-VAY-A): 1.000.000 VND.` và
`Ngày (DEMO-VAY-A): 2026-10-30.`. Câu trong `du_lieu.tra_loi` phải khớp mẫu
Python dựng lại từ **tất cả** bằng chứng của các trường cần trả lời; mỗi
khẳng định đúng một quote thuộc ngữ cảnh AI và đúng map nguồn/phiên bản.
Không dùng văn xuôi ngoài khuôn để suy rằng ngữ nghĩa đã được chứng minh.
`tra_loi_ai.tra_loi` ngoài cùng không được coi là câu trả lời đã kiểm và không
chép vào kết quả; đầu ra nghiệp vụ lấy từ khuôn `du_lieu`.

Các quy tắc định dạng có sẵn, chỉ áp khi profile khai rõ và kết quả khớp
nguồn từng ký tự: `tien_chuan`, `tien_nhom_ba`, `so_chuan`, `ngay_iso`,
`ngay_viet`, `nguyen_van`, `co_khong`. Không quy đổi tỷ giá/tỷ lệ/đơn vị,
không tổng/làm tròn/tự tính số mới. Kiểm số bằng int/Decimal, tiền `{so,tien_te}`;
chuỗi thập phân giữ chính xác, số float không được dùng để xác nhận tiền.
Nguồn thiếu nhãn trường/thực thể trong vùng quote hoặc cần diễn giải phức
tạp thì từ chối có lý do, chờ bổ sung binding/ngữ pháp đã review.

TC-4 trước đây từ chối AI tầng 1. TC-7 thêm lớp bọc `chuan_bi_tang_mot` trong
`bang_chung.py` và đăng ký ở `chay.py`: chỉ chạy khi Core cấp profile tầng 1
đủ điều kiện. Ghim profile vào snapshot `kiem_chung_core`, dựng quote/map từ
bằng chứng đã duyệt, kiểm lại profile và nguyên yêu cầu AI khi hậu kiểm.
Không sửa `chuan_bi_ai.py`/`ngu_canh_ai.py` hoặc dùng công tắc caller xin nhãn.
Nhánh thiếu profile vẫn từ chối như TC-4. AI tầng 1 vẫn Vàng.

## Mâu thuẫn, cache và K5

Hai giá trị khác nhau cho cùng trường/thực thể được giữ cùng nguồn, cờ
`co_mau_thuan/can_duyet`, tối đa Vàng; không chọn bên. Nếu AI giấu một bên,
câu trả lời bị từ chối và `mau_thuan` vẫn giữ hai căn cứ **do Core đã cấp và
đã kiểm được** cho người duyệt. Không tìm mâu thuẫn bằng cách mở ngược tệp
tầng 1. Dữ liệu mới tầng 2/3 chỉ `de_nghi_k5`, `da_duyet=false`,
`da_tao_viec=false`; Core tạo việc, không ghi dữ liệu đã duyệt từ engine.

`phu_thuoc_cache` chứa nguyên nguồn/phiên bản/băm/ref, thực thể, ngữ cảnh
pháp nhân/nhóm/module/người/phạm vi, cờ thời điểm/văn bản mới và mốc công
bố/duyệt/hiệu lực từng quan hệ. Engine không tạo cache. Khi phụ thuộc thời
điểm, `duoc_tai_dung_cache=false`; trường hợp khác để null cho Core quyết,
không tự chứng nhận quyền nguồn còn hợp lệ. Core vẫn phải kiểm quyền mọi
nguồn/hết hạn theo sự kiện, nguồn thu quyền và chính sách TC-Q05/15.

## Các phần cần kiểm tiếp

CLI SDK chuẩn vẫn 0/5 `CHUA_CAU_HINH`, mã 1 vì SDK 2.0 chưa nạp Ngan/cấu hình
và tệp con xuyên bước. Harness bổ sung nạp fixture thật/băm thật qua CoreGia,
không thay kết quả CLI. Kết quả/số kiểm/thời gian thực tại `VIEC.md`.

Chờ Core đối chiếu seam profile với dữ liệu trường đã duyệt/binding miền,
ngưỡng đo đã duyệt, RLS/quyền sống và vòng đời snapshot; chờ Core điều phối
tầng 2/3/cache/K5. Chưa kiểm Core thật, model thật, Linux hoặc trình duyệt.
Không dùng test đơn vị/adapter để công bố độ chính xác nghiệp vụ.

Test consumer Hỏi AI hiện có với Local giả cũng đã chạy: consumer từ chối
khuôn do bộ kiểm metadata/giá trị nguyên văn; TC-7 giữ không căn cứ. Các
nhánh trả lời thành công trong harness dùng fixture Local theo protocol,
chưa chứng nhận consumer/model thật trả lời thành công; cần lead Hỏi AI/Core
rà giới hạn giống TC-5, không sửa engine Hỏi AI trong TC-7.

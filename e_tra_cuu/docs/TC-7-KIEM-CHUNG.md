# TC-7 — Hai đường trả lời và ranh giới kiểm chứng

Ngày 15/11/2026; 5 giờ **ƯỚC TÍNH** trong phiếu. Đã kiểm bằng Core giả
(CoreGia), NganBoNho và Local giả theo protocol; 0 Cloud/model thật. Không
chứng nhận RLS, tìm lai, OCR/TX, ba tầng hoặc K5/cache thật đã chạy.

## Phạm vi và nhãn

Đúng bốn tệp runtime: `tra_loi.py`, `kiem_chung.py`, `bang_chung.py`, `chay.py`.
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
  hỏi và quote; nhãn trường `ten` phải có nguyên cụm trong quote (so chữ hoa
  thường cho nhãn trường). Core chịu trách nhiệm cấp **quan hệ nghiệp vụ đã
  xác thực**, không chỉ ghép một con số bất kỳ ở cùng tệp.
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
- Profile/nguồn sai metadata hoặc băm trả `TC_SAI_NGUON`; Cloud trả
  `TC_CHI_LOCAL`; khuôn phản hồi AI sai trả `TC_AI_SAI_KHUON`. Quan hệ/trích
  dẫn/vị trí/giá trị không đạt trả `khong_thay_can_cu`, xóa toàn bộ khẳng định
  khỏi **câu trả lời**, không giữ lời bịa dưới nhãn Vàng.

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

# Hướng dẫn viết module cho Core

SDK 2.3.0 dùng chung cho module và engine. Bắt đầu từ `module-demo/demo_ho_so/` trong bộ phát hành: `module.json` là phiếu khai báo; `backend/` xử lý; `frontend/` hiển thị; `schema/` và `contract/` mô tả dữ liệu. Xem `API-CORE-v1.md` để tra API chung.

## Khai báo gói

Trong `module.json`, đặt `phien_ban_manifest: 2`, `loai: "module"`, `ma`, `ten`, `phien_ban`, `nha_phat_trien`, `tuong_thich`, `goi`, `backend`, `tien_trinh`, `giao_dien`, `quyen`, `hanh_dong`, `ma_loi`, `du_lieu`, `contract`, `nut`. Mã module gồm 3–31 ký tự, bắt đầu bằng chữ thường; các ký tự sau là chữ thường, số hoặc dấu gạch dưới. `goi` khai `tep_kiem_ke`, thuật toán băm và `phu_thuoc_module` (có thể rỗng). `backend.diem_vao` trỏ tới điểm vào Python; `tien_trinh` khai cả `nhan_listener` và `che_do_mac_dinh`. `giao_dien.tai_nguyen` phải chứa `diem_vao`.

Mỗi quyền có mã `<tai_nguyen>.<dong_tu>` và tên hiển thị. Động từ chỉ được là `xem`, `xem_du`, `lap`, `sua`, `kiem`, `duyet`, `huy`; nút tạo bản ghi dùng `lap`, sửa bản ghi dùng `sua`. Core gắn mã module vào quyền khi cài. Xem các quyền `ho_so.xem`, `ho_so.lap` trong mẫu.

Mỗi phần tử `hanh_dong` khai `ma`, `ten`, `phuong_thuc`, `duong_dan`, `quyen`, schema `dau_vao`/`dau_ra` khi cần, `kieu` (`dong_bo` hoặc `nen`) và `chong_trung`. Bộ chạy SDK hiện chưa hỗ trợ hành động `nen`; mẫu dùng `dong_bo`. Core tạo route `/api/v1/module/{ma}{duong_dan}`, kiểm phiên, quyền và schema trước khi chuyển yêu cầu cho module. Đường dẫn có thể chứa biến như `{id}`. Với `chong_trung: true`, bên gọi gửi `Idempotency-Key`. Xem hai hành động đọc trong mẫu.

Khai `ma_loi` gồm `ma`, mã `http`, `thong_diep` tiếng Việt dễ hiểu; backend trả mã lỗi nghiệp vụ đã khai. Phong bì API dạng phẳng gồm `ma`, `thong_diep`, `request_id`, `thu_lai_duoc`, và có thể có `chi_tiet`. Màn hiển thị `thong_diep`; mã và `request_id` đặt trong “Chi tiết hỗ trợ” thu gọn. Không đưa dữ liệu nghiệp vụ hoặc bí mật vào câu lỗi.

`du_lieu.ngan` khai từng ngăn và các cột `ma`, `ten`, `kieu`; Core tạo khối và cột chuẩn, phân tách dữ liệu theo pháp nhân. Các kiểu gồm `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`, `khoa_noi` (khai thêm `ngan_dich`). Mẫu khai ngăn `ho_so`, trong đó `tep_goc` tham chiếu tệp. `contract.cong_bo` khai dữ liệu công bố: mã, phiên bản, module sở hữu, tệp mô tả, schema, ví dụ, quyền đọc và ngăn nguồn; xem các tệp tương ứng trong `contract/` của mẫu.

`nut` khai mã (tối đa 32 ký tự, khớp `^[a-z][a-z0-9_]{0,31}$`), tên, phần hiển thị, thao tác đầu, loại và giới hạn tệp nhận, ngăn kết quả, quyền và `sdk_dung`. Khai đúng các thao tác SDK cần dùng trong `hanh_dong[].sdk_dung` hoặc `nut[].sdk_dung`, chẳng hạn `quy_trinh.ket_qua`, `ngan.doc`, `ngan.them`, `ngan.sua`. Admin gắn quy trình và ghép trường kết quả với cột ngăn trên Core; gói không ấn định quy trình.

## Viết backend và giao diện

Trong `backend/xu_ly.py`, viết hàm `(sdk, yeu_cau)` và bảng `XU_LY` theo `hanh_dong.ma`. `yeu_cau` gồm `duong_dan`, `truy_van`, `than`, `ngu_canh`; kết quả phải khớp schema đầu ra. `backend/chay.py` chuyển bảng xử lý, bảng sự kiện và lớp lỗi cho `module_runtime.chay_theo_khai_bao`. SDK nhận ngữ cảnh do Core cấp và kiểm quyền; không tự chọn pháp nhân hay kết nối riêng từ yêu cầu.

`sdk.ngan(ma).doc(loc, gioi_han, con_tro)` trả `danh_sach` và `con_tro_tiep`; `loc` lọc bằng theo cột. Dùng `sdk.ngan(ma).them(dong)` hoặc `sdk.ngan(ma).sua(id, dong)` để ghi ngăn thuộc module, với thao tác được khai tương ứng. Mẫu đọc ngăn trong `danh_sach_ho_so` và `xem_ho_so`.

Khi quy trình gắn với nút hoàn tất, Core gửi `quy_trinh.xong` qua route nội bộ của nút; module không phải khai sự kiện nhận trong phiếu. SDK đọc tham chiếu kết quả rồi gọi hàm nhận với `tep_nut` và `ghep`. Xem `SU_KIEN` và `nhan_quy_trinh_xong` trong mẫu: hàm tự chọn cột tệp và ghi các giá trị được ghép vào ngăn bằng `ngan.them`. Không coi tham chiếu trên bus là toàn bộ nội dung kết quả.

### Nhận việc lỗi của nút (SDK 2.5.0)

Đăng ký thêm `quy_trinh.loi` trong cùng bảng `SU_KIEN` chuyển cho
`module_runtime.chay_theo_khai_bao`. Core gửi qua cùng kênh nội bộ có ký,
ủy nhiệm theo người bấm nút và pháp nhân của việc:

```python
def nhan_quy_trinh_loi(sdk, su_kien):
    ngan = sdk.ngan('ket_qua')
    dong = ngan.doc({'viec_id': su_kien['viec_id'], 'da_luu_tru': False},
                    gioi_han=2, con_tro=None)['danh_sach']
    if len(dong) != 1:
        raise LoiNghiepVu('VIEC_CHUA_GAN')  # Khai lớp lỗi và mã trong gói.
    return ngan.sua(str(dong[0]['id']), {
        'trang_thai': 'LOI', 'ma_loi': su_kien['ma_loi'],
        'thong_diep': su_kien['thong_diep']})

SU_KIEN = {'quy_trinh.xong': nhan_quy_trinh_xong,
           'quy_trinh.loi': nhan_quy_trinh_loi}
```

Payload tối thiểu gồm `su_kien`, `viec_id`, `ma_loi`, `thong_diep`.
`thong_diep` là câu tiếng Việt an toàn do Core cấp, không phải log engine.
SDK gọi hàm nhận lỗi trực tiếp, không đọc `quy_trinh.ket_qua` hay tệp kết quả.
SDK cũng cung cấp `loi = {ma, thong_diep, thu_lai_duoc: False}` cho hàm nhận.
Khai `ngan.doc`, `ngan.sua` trong `nut[].sdk_dung` nếu dùng như ví dụ;
không cần sửa ngăn nếu các cột đã có. Module dùng hàm mới khai SDK `>=2.5.0 <3.0.0`.

Dùng `viec_id` để tra đúng dòng, ghi trạng thái Lỗi và dừng polling dòng đó;
chỉ hiện thông điệp, mã lỗi nằm trong “Chi tiết hỗ trợ” thu gọn.
Module cũ không đăng ký hàm nhận lỗi vẫn được SDK trả nhận no-op.
Core giao lại **thông báo** nếu hàm nhận chưa thành công, tối đa 5 lần với giãn cách tăng dần;
không tự chạy lại việc. Biên nhận module ngăn ghi trùng khi giao lại.
Nếu sự kiện về trước lúc lưu liên kết, hãy báo chưa nhận để lần giao sau tra lại.

Để thử bằng CoreGia sau `chay_thu`/`chay_thu_demo`, gọi:
`core.phat_su_kien_quy_trinh(kq['id'], SU_KIEN, sdk_gia, viec_quy_trinh_id=viec_id)`.
`viec_id` là UUID đã lưu trong ngăn giả; bỏ tham số này thì dùng UUID ổn định từ mã việc giả.
CoreGia phát theo trạng thái XONG/LOI, dùng cùng hàm xử lý SDK, không phát lại khi đã nhận,
cho thử tối đa 5 lần khi hàm nhận ném lỗi, không chạy lại engine. Mỗi lời gọi thử giao một lần,
không chờ giãn cách thời gian thật. Với XONG có thể truyền thêm `tep_nut`, `ghep`.
Ca lỗi mẫu: gửi tệp `.txt` có byte sai UTF-8 qua quy trình dùng engine xuất thống kê DEMO;
`demo_ket_qua_nut` 1.0.2 nhận lỗi và ngừng chờ kết quả.

Trong `frontend/chinh.js`, đánh dấu phần tử bằng `data-ktt-nut="doc_tep"` và gọi `sdk.nut.dat('doc_tep', phan_tu)` như mẫu. Core chỉ vẽ nút khi quy trình đã áp dụng và người dùng có quyền; nếu không đánh dấu vị trí, Core đặt nút ở thanh thao tác của phần.

`hienThi(phan_tu, tuy_chon)` nhận hàm `tuy_chon.quyen(op, {phap_nhan_id})` để màn tự ẩn chức năng. `op` là **mã hành động** trong `hanh_dong[].ma` (hoặc `xem_<phần>` / `danh_sach_<phần>` cho thao tác đọc của phần), **không** phải mã quyền như `dot_demo.lap`. Truyền mã quyền thì hàm luôn trả `false` và màn có thể trống. Máy chủ vẫn kiểm quyền thật ở từng API.

Khi gắn quy trình vào nút, Admin phải ghép **ít nhất một** trường kết quả vào một cột ngăn của module, và kiểu phải khớp. Quy trình trả tệp thì ngăn cần một cột kiểu `tep` (ví dụ cột "Tệp kết quả" của `demo_ket_qua_nut`), kể cả khi module tự đọc tệp bằng `sdk.ket_qua.doc_tep`. Hãy khai cột này ngay từ bản đầu: Core chưa hỗ trợ nâng module khi ngăn thêm cột.

### Gửi tệp qua nút (C-RV-02)

SDK trình duyệt có `sdk.nut.chay(ma_nut, tep, {idempotency_key?})` trả Promise `{viec_id, vi_tri_cho}` (`vi_tri_cho` là số nguyên không âm hoặc `null`). Module và pháp nhân lấy từ ngữ cảnh hiện tại, không nhận từ tham số. SDK dùng route chạy nút hiện có, multipart một tệp, CSRF và khóa chống trùng tự sinh; máy chủ vẫn kiểm phiên, quyền nút, loại/dung lượng tệp, pháp nhân và chống trùng. Nếu gửi lại cùng ý định, giữ cùng khóa và cùng tệp.

Ví dụ trong hàm xử lý lựa chọn tệp của màn module; `tep` là File người dùng vừa chọn:

```javascript
const { viec_id, vi_tri_cho } = await sdk.nut.chay('doc_tep', tep);
// Lưu viec_id vào bản ghi module qua hành động đã khai của module.
// Khi hàm nhận quy trình về, dùng viec_id để tra đúng bản ghi.
```

Với nút tệp mặc định do Core vẽ, cũng nhận được mã việc:

```javascript
const huyNhan = sdk.nut.khi_gui('doc_tep', ({ viec_id, vi_tri_cho }) => {
  // Lưu liên kết bản ghi ↔ viec_id như khi tự gửi ở trên.
});
// Khi rời màn: huyNhan();
```

Muốn tự vẽ nút, dùng `sdk.nut.dat('doc_tep', phan_tu, {tu_ve:true})`, rồi gắn xử lý gửi ở trên. **Module phải tự ẩn nút khi người dùng không có quyền** hoặc chưa có quy trình áp dụng; lấy danh sách nút được phép qua `GET /api/v1/module/{ma}/nut` với pháp nhân hiện tại, cập nhật khi đổi ngữ cảnh. Core không tự ẩn phần tử module tự vẽ; máy chủ vẫn kiểm quyền và chặn 403. Dùng giao diện mặc định thì Core tự lọc quyền trước khi vẽ.

### Đọc tệp trong hàm nhận quy trình (C-RV-01)

SDK Python thêm `sdk.ket_qua.ds_tep(viec_id)` trả danh sách `{tep_id, ten, mime, kich_thuoc, sha256}` và `sdk.ket_qua.doc_tep(viec_id, tep_id)` trả **bytes**. Hai thao tác kênh tương ứng là `quy_trinh.ds_tep_ket_qua`, `quy_trinh.doc_tep_ket_qua`, đều là **đọc** và **không thuộc bộ mặc định**. Phải tự khai trong `nut[].sdk_dung` của nút có hàm nhận `quy_trinh.xong`; nếu đọc trong hành động thì khai ở `hanh_dong[].sdk_dung`. Ví dụ phần khai báo của nút (giữ các thao tác đang dùng):

```json
{"sdk_dung":["ngan.them","quy_trinh.ket_qua","quy_trinh.ds_tep_ket_qua","quy_trinh.doc_tep_ket_qua"]}
```

Module đã cài phải **phát hành lại gói** với khai báo mới; nâng wheel không tự bổ sung quyền. Ví dụ đọc một tệp JSON engine nộp trong hàm nhận:

```python
import json


def nhan_quy_trinh_xong(sdk, su_kien):
    viec_id = su_kien['viec_id']
    for tep in sdk.ket_qua.ds_tep(viec_id):
        if tep['mime'] == 'application/json':
            noi_dung = sdk.ket_qua.doc_tep(viec_id, tep['tep_id'])
            ket_qua = json.loads(noi_dung.decode('utf-8'))
            # Tự kiểm schema nghiệp vụ, tra bản ghi theo viec_id rồi lưu qua ngăn.
            return ket_qua


SU_KIEN = {'quy_trinh.xong': nhan_quy_trinh_xong}
```

Chỉ đọc việc thuộc nút của **chính module, cùng pháp nhân, đã XONG**, chỉ tệp engine nộp trong kết quả lượt XONG; không đọc tệp đầu vào. Core kiểm SHA-256/kích thước, trần cấu hình và `GIOI_HAN_TEP = 20_971_520` byte (20 MiB); SDK kiểm lại kích thước/SHA-256 trước khi trả bytes. Ngoài phạm vi, chưa xong, không có tệp (kể cả danh sách rỗng) hoặc tệp trong kho thiếu/sai băm/kích thước đều trả `KHONG_TIM_THAY`; vượt trần đọc Core trả `VUOT_GIOI_HAN_KICH_THUOC`; thiếu kho/kênh trả `CHUA_SAN_SANG`; phản hồi sai dạng, quá trần SDK hoặc sai kích thước/băm trả `PHAN_HOI_SAI_CONTRACT`. Hiện câu lỗi dễ hiểu; mã để trong “Chi tiết hỗ trợ” thu gọn. SDK 2.3.0 chỉ bổ sung, tương thích ngược với 2.2.0.

## Đóng gói và cài

Hoàn thiện các tệp được phiếu tham chiếu, cập nhật `KIEM-KE.json` với mã băm đúng cho gói. Không đưa mật khẩu, khóa, địa chỉ hay đường dẫn cố định của máy vào gói. Trong Quản trị Core, chọn thêm module, đưa gói lên, xem quyền và thay đổi dữ liệu, duyệt cài rồi bật module. Sau đó Admin gắn quy trình đã áp dụng vào nút và ghép kết quả với ngăn. Kiểm thử với dữ liệu DEMO trước khi đưa vào sử dụng.

# TX-3 — Lõi hậu kiểm và xuất, biên bản review

> **Cập nhật TX-3b, 15/11/2026:** Anh đã duyệt toàn bộ chi tiết tại
> `_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` câu 3.
> Schema chung/bản trong gói, hai năng lực và hai DEMO đã đăng ký ở bản
> **0.4.0**; test dùng manifest/handlers thật. Các nhãn “chưa đăng ký /
> chờ Anh / đề xuất” bên dưới là lịch sử TX-3 trước duyệt.
> Kết quả hiện tại và giới hạn CLI xem biên bản TX-3b trong `VIEC.md`.

Ngày **15/11/2026** · PR: **chờ lead mở** · Dự toán **8 giờ công ước tính**.
Hướng T2 bảng + Excel đã chốt. Tài liệu này trình chi tiết để lead/Anh review,
không hỏi lại hướng. **Chưa đăng ký** `bang_trich_xuat`,
`trich.hau_kiem@1` hoặc `trich.xuat_ket_qua@1` trong manifest/runtime.
Chưa tạo schema bảng tại `_chung/contract/` hay gói.

Lõi TX-3 gồm `hau_kiem.py`, `kiem_tra.py`, `logic.py`, `xlsx_mini.py`,
`xuat.py`. Đợt sửa theo kiểm độc lập của lead chạm đúng **5 tệp mã**:
`kiem_tra.py`, `hau_kiem.py`, `xuat.py` và hai tệp nền TX-2
`tich_hop.py`, `cau_truc.py` để đóng nợ RAM. Không đổi hai mẫu NGAN-0,
manifest/runtime hoặc mã cũ; không commit/push.

## Chi tiết đề nghị review

| Phần | Hành vi của lõi DEMO |
|---|---|
| Đầu vào hậu kiểm | `tra_loi_ai` v1, nguồn `local`. Mở hồ sơ thật trong kho CoreGia qua `viec.mo_tep`; kiểm kích thước, băm bytes, phiên bản, snapshot/bộ E1/quy tắc, danh sách mã, module/loại/phiên bản bộ, prompt, đúng văn bản/khuôn và ngân sách đã ghim |
| Băm | `nguon.bam_dau_vao` là băm bytes tài liệu gốc; `nguon.bam_van_ban` là băm UTF-8 toàn văn chuẩn hóa. Băm request của AI-2 là băm **toàn phong bì** `yeu_cau_ai`, có chuyển tiếp; khác băm `bam_yeu_cau_ai` nội bộ của TX-2. Không dùng hash thay ACL/Core |
| Mã thiếu | Đề nghị: mã AI bỏ sót được bổ sung đúng vị trí, giá trị null/cần soát, lý do “AI bỏ sót mã cần trích.”; nếu toàn bộ `du_lieu=null` và trạng thái không thấy căn cứ thì mỗi ô có lý do không tìm thấy. Mã lạ, dữ liệu dạng danh sách lặp, đảo thứ tự hoặc ô sai trường → `AI_TRA_SAI_KHUON`. Không bỏ dòng thiếu khỏi bảng |
| Từng dẫn chứng | Kiểm `0≤bat_dau<ket_thuc≤len(tai_lieu)` và lát chuỗi Python bằng nguyên văn; không normalize, không tin cờ chung. Chỉ một dẫn chứng giả cũng hạ ô đó về null. Dẫn chứng đúng còn lại được giữ; nguyên phản hồi AI ở trường riêng |
| Giá trị | Chỉ xác nhận trọn token hoặc trọn cụm nguyên văn trong câu đã kiểm; `strip()` cả giá trị lẫn câu khi so, giữ nguyên giá trị AI để kiểm toán. Số nối bằng `. , / -`, dấu âm, `%` và khoảng trắng phân nhóm (kể cả NBSP) không được cắt một phần. Không lấy số lớn nhất, đoán đơn vị hoặc tự tính. Mọi giá trị ghi “suy ra” chưa có quy tắc duyệt đều null/cần soát; giữ nguyên byte bộ 37, chưa duyệt TT-21 |
| Kiểu | Snapshot E1 của TX-2 hiện chỉ có 10 cột, chưa khai kiểu/quy tắc chuyển kiểu; hậu kiểm giữ `kieu=van_ban`, `kieu_da_chuyen=false`, kể cả chuỗi tiền/ngày. Bộ kiểm bảng và exporter hỗ trợ sáu kiểu chung, tiền `{so,tien_te}` với `so` chỉ là int (không bool) hoặc chuỗi thập phân chính xác dùng dấu chấm (không float/ký pháp mũ/dấu phân nhóm), ngày ISO. Test typed round trip kiểm exporter bằng bảng DEMO khai kiểu; **không coi đó là bộ module đã được duyệt chuyển kiểu** |
| Logic | Chép có sửa L1–L5; XD chạy đủ, loại khác chỉ L1/L4. Ba quy tắc E1 trong snapshot: “Có thì phải có”, “Tổng tỷ lệ”, “Ngày không sau”. Chỉ chạy quy tắc liên trường khi đủ mã trong phạm vi hỏi; không coi mã ngoài danh sách trích có mục tiêu là AI bỏ sót. Vi phạm giữ giá trị có căn cứ, bật cờ/ghi lý do, không sửa |
| Vị trí | Payload khai `don_vi_offset="unicode"`, đếm Unicode code point theo Python, không phải byte/UTF-16. DOCX không phân trang: đoạn/Điều/Khoản, trang/hộp null. OCR giữ trang thực; câu qua nhiều trang/khối được tách thành các dẫn chứng có offset thật, giữ câu AI gốc riêng; chỉ gắn hộp nguồn khi tái lập đúng khối tại offset, kể cả câu lặp hai trang. Không lấy hộp của lần xuất hiện đầu hoặc đoán tọa độ; hồ sơ gốc giữ nguyên cấu trúc OCR |
| Tổng hợp | Đúng một dòng/mã theo thứ tự snapshot; `so_tham_so=len(bang)`, `so_can_soat` đếm cờ, `co_can_cu` là ít nhất một giá trị đã kiểm (ô logic cần soát vẫn có căn cứ). Tối đa 200 dòng và **phong bì** JSON UTF-8 20 MiB |
| Xuất | `bang_trich_xuat → truong`: `tep_json:tep`, `tep_excel:tep`, `so_tham_so:so`, `so_can_soat:so`, `co_can_cu:co_khong`. Tạo xong cả hai tệp trong RAM rồi tải qua SDK; không XONG nếu một tệp lỗi/thiếu metadata |
| Excel | Writer thư viện chuẩn chuyển từ `xlsx_mini.py`; không cắt `[:32000]`. Kiểm 32.767 đơn vị UTF-16 trên giá trị trước XML escape; chữ ngoài BMP tính hai. Text luôn inlineStr, không công thức; tiền/số dài dùng text JSON để không mất độ chính xác; ngày ISO và nguyên văn giữ riêng |
| RAM và ACK | Tài liệu nguồn và hồ sơ hậu kiểm mỗi phần ≤20 MiB JSON UTF-8; `trang` ≤2.000 phần tử và ≤8 MiB; `canh_bao` ≤200 phần tử và ≤64 KiB (tính cả JSON). Kiểm nguồn trước deepcopy, tuần tự hóa có trần trước tải Core; vượt trả `VUOT_GIOI_HAN`, không cắt. Hồ sơ chỉ giữ toàn văn ở `tai_lieu.van_ban`, bỏ bản chép trong `yeu_cau_ai`; hậu kiểm dựng lại đúng request để kiểm hash và vẫn đọc hồ sơ TX-2 cũ. BytesIO đóng trong finally khi thành công/lỗi/hủy. Không tệp tạm trên đĩa. SDK giữ khóa chống trùng riêng cho từng tệp, retry cùng khóa; test mất ACK tệp/kết quả/kết thúc không nộp trùng. Tệp đã lên Core trước lỗi/hủy chờ Core dọn theo C-TX-02 |

## Trường bổ sung so với ví dụ §4 loại chung

Lõi dùng nguyên các trường bắt buộc trong đề xuất. Các trường sau chỉ là
**chi tiết đề nghị review**, chưa phải sửa contract chung:

- Payload: `ma_bam_noi_dung`, `bam_tep_goc`, tách khỏi `bam_bo_tham_so`;
  `don_vi_offset: "unicode"` áp cho mọi dẫn chứng trong bảng.
- Mỗi dòng có `kieu_da_chuyen: false` khi E1 chưa khai quy tắc chuyển kiểu;
  kiểu khác `van_ban` phải khai cờ true. Cờ này không thay quy tắc nghiệp vụ
  được duyệt; fixture typed của exporter chỉ là DEMO.
- `nguon`: thêm băm gốc bắt buộc theo §4.3.2 và phiên bản engine đọc/chuẩn bị.
- `ai`: thêm phiên bản engine AI, băm đầu vào request, trạng thái và cờ kiểm
  chung để truy vết; cờ này không quyết định việc xác nhận từng ô.
- Mỗi dòng: đổi `kiem_tra_legacy` thành **`dau_kiem_tam_e6`** để nói rõ
  đây là dấu chấm tạm của cách cũ, chỉ dùng E6 đối chiếu, không xác nhận ô.
  `phan_hoi_ai` là trường **chỉ để kiểm toán**, giữ đối tượng ô trước hậu kiểm
  (null khi AI bỏ sót), kể cả dẫn chứng giả; **có thể lộ nội dung tài liệu**.
  **Module không hiển thị mặc định** và không ghép cột từ trường này.
  `nguyen_van` giữ giá trị AI, tách khỏi `gia_tri` đã kiểm. Không đưa vào lỗi/log.
- Excel gồm bốn sheet: **Kết quả**, **Dẫn chứng**, **Nguồn**, **AI nguyên văn**.
  Metadata/phản hồi AI được tách từng lá có kiểu JSON để tránh ô vượt trần chỉ
  vì bọc JSON; tệp JSON canonical là dữ liệu chuẩn cho module.

Lỗi dùng đúng sáu mã/câu trong lệnh giao. Lỗi mở tệp/quyền/mạng/lease vẫn là
lỗi vận hành, không đổi thành không thấy căn cứ. Lỗi tạo/tải tệp cuối cùng
là `XUAT_KET_QUA_LOI`; hủy/`ChuaRo`/mất lease giữ vòng đời SDK.

## ĐỀ XUẤT TX-0, chờ Anh — bổ sung payload `bang_trich_xuat`

Đây là phần bổ sung đề xuất cho `LOAI-DU-LIEU-RIENG.md` §4, **chưa duyệt**,
không sửa bốn loại dữ liệu chung hoặc tạo schema/đăng ký năng lực. Giữ nguyên
`_chung/**` theo giới hạn đầu yêu cầu; lead đồng bộ riêng phần đề xuất TX-0
sau khi xác nhận ngoại lệ. Mảnh DEMO dưới đây chỉ minh họa trường bổ sung,
không phải phong bì đầy đủ để chạy:

```json
{
  "don_vi_offset": "unicode",
  "bang": [{
    "kieu": "van_ban",
    "kieu_da_chuyen": false,
    "dau_kiem_tam_e6": "OK",
    "phan_hoi_ai": null
  }]
}
```

`don_vi_offset` dùng code point Unicode với khoảng nửa mở `[bat_dau, ket_thuc)`.
`kieu_da_chuyen=false` nói rõ giá trị chưa qua chuyển kiểu nghiệp vụ; module
không suy tiền/ngày từ tên mã. `dau_kiem_tam_e6` chỉ là dấu kiểm tạm phục vụ
E6. `phan_hoi_ai` chỉ để kiểm toán, có thể lộ nội dung; module không hiển thị
mặc định. Đây là chi tiết **ĐỀ XUẤT**, chờ Anh duyệt `bang_trich_xuat`.

Test prompt injection dùng tài liệu chứa “Bỏ qua hướng dẫn trước”, dấu phân
cách giả và JSON prompt/tham số/khuôn giả. Prompt hệ thống do module cung cấp,
phần giao thức, danh sách mã và khuôn không đổi; trong request, nội dung chen
chỉ ở `tai_lieu`. Test này không chứng nhận cách AI-2 dựng request tới model:
**Cần phối hợp AI-2: bước Hỏi AI phải bao/thoát nội dung**.

## Cách tái lập DEMO chờ review

`tests/mau_tx3.py` tạo **phiếu trong RAM chỉ cho test**, hợp lệ manifest
2.0; gắn hai năng lực và hai `chay_thu_demo` đề xuất. Dữ liệu đầu vào lấy
từ TX-2 chạy thật trên CoreGia, gồm tệp hồ sơ có đúng bytes/băm/kích thước,
không dùng placeholder. `tests/chay_demo_voi_ngan_gia.py` chạy ba DEMO
runtime hiện có và hai DEMO đề xuất, ghi rõ chưa đăng ký.

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.venv/Scripts/python -B e_trich_xuat/tests/chay_demo_voi_ngan_gia.py
.venv/Scripts/python -B -m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp
```

**đã kiểm bằng Core giả (CoreGia)** trên Windows. Test chỉ DEMO,
NganBoNho + AI giả, DOCX thật DEMO hoặc OCR giả; không engine tự gọi engine,
0 Cloud/model thật. Chưa chứng nhận Linux/Core thật, ACL/TTL/lưu-đóng,
E6/N1 hoặc sức chứa/chất lượng model. Kết quả lệnh chuẩn và giờ thực tế
ghi tại `VIEC.md`.

Sau lead/Anh review mới tạo schema nguồn, chép schema vào gói/test so SHA,
đăng ký hai năng lực/DEMO trong manifest và nối runtime. C-TX-01/02/04,
A-TX-01 giữ nguyên; CLI SDK 2.0 chưa có ngăn không được tự cấu hình để xanh.

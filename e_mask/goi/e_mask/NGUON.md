# NGUỒN — gói e_mask, MASK-1…7, MASK-2b và sửa an toàn

## MASK-B11 lượt 4 — 17/11/2026, danh sách đóng nhãn kế toán sau marker

Tiếp tục nguồn nội bộ của lượt 3 theo đúng danh sách 21 cụm lead giao ngày 17/11; không nguồn ngoài hoặc dependency mới. Chỉ sửa runtime `e_mask/tep_word.py`: hằng số có chú thích `NHAN_KE_TOAN_SAU_MARKER`, regex ranh giới từ `_NHAN_KE_TOAN_SAU_MARKER`, hàm `_duoi_marker_hop_le` và chỗ gọi trong `_canh_bao_chu_chua_dat`. Dùng `unicodedata.normalize` thư viện chuẩn để NFC, gọn khoảng trắng trên bản sao kiểm đuôi; không đổi bytes/offset nguồn. Khớp nhãn và tiền/ngày từ `_cac_tien_ngay` hiện có trên cùng chuỗi rồi xét hợp các khoảng: giữ ngày viết bằng chữ, không tạo ranh giới giả bằng cách xóa span. Không chuyển chữ thường hoặc bỏ dấu; mọi chữ ngoài danh sách còn chặn. Nhánh `_duoi_tong_hop_hop_le` và `_TONG_HOP` giữ nguyên lượt 3.

Excel và hậu kiểm cuối dùng lại bộ lọc chung, không sửa thêm `tep_excel.py`/`hau_kiem_tep.py`. Giữ detector, nhãn định danh, kiểm số/tiền/ngày, Local, map chỉ RAM, trần, API v1 và manifest 1.6.0. Giữ toàn bộ 156 regression lượt 3; 255 ca mới trong `tests/test_mask_b11_nhan_ke_toan.py` chỉ dùng DEMO lead giao và các biến thể development, không nhập công cụ/recipe B10. B10/held-out/gold/MASK-2c/fixture R3 giữ nguyên bytes. Kiểm kê LF sinh từ bytes thật, phiên bản bằng engine.json. Đã kiểm bằng Core giả (CoreGia), Local giả; chưa Core/Office/Local/Linux thật; Cloud tắt, PR: chờ lead mở. Kết quả thật và giới hạn mẫu đo tại VIEC.md.

| Tệp | Mốc | Bytes | SHA-256 bytes = SHA-256 LF |
|---|---|---:|---|
| `e_mask/tep_word.py` | trước lượt 4 (lượt 3) | 20684 | `7ecfef3d145d9d4fe1eea76ca2db4056832c6ed300b3c030d3009e4cc6e901ab` |
| `e_mask/tep_word.py` | sau lượt 4 | 22227 | `0772b09c56eaea87c164ff723a52193c5e226451074d23d46b29136895d4f114` |

## MASK-B9 — 16/11/2026, nối SDK và bàn giao tệp trong cùng chu kỳ

**Nguồn/quyền:** tiếp tục mã nội bộ Mask đã được Anh/lead giao, giữ quyền sử dụng nội bộ đã ghi bên dưới. Không lấy nguồn ngoài hoặc thêm dependency; không sửa nguồn tham chiếu, Core/SDK, nguồn cũ hoặc engine khác. Tái dùng các primitive B8/R4/R6 và thiết kế lô SDK R2 bằng import nội bộ hoặc chép có sửa orchestration. SHA-256 bytes và LF của bốn nguồn sau giống nhau ở checkout này và giữ nguyên so với HEAD:

| Nguồn trong gói Python / symbol | SHA-256 bytes = LF | Tái dùng / khác biệt B9 |
|---|---|---|
| `ho_so_tep.py`: `MoTepRAM.mo`, `bao_ve`, `MIME` | `80b3e511a3912c0fcb10efc120d1049ffaa14675837706fca6847256d80ecafa` | Bố trí handle RAM và context bàn giao → `MoTepSDK` ở `kho_dinh_danh.py`; thêm parse mẫu 7 dưới handle, upload SDK trong cách ly, bộ T và kiểm lại lifecycle sau tiêu thụ. Không sửa B8. |
| `kho_ngan.py`: `KhoNganBiMat._sua_lo`, `_ket_qua` | `83c6cce6a586ae2901f3e5a40161e917999d8eeb8951b501d580e3db6b262fde` | Tái dùng nguyên tắc CAS/lô và metadata null+cờ → `CongHauKiemTepSDK` ở `kho_qua_core.py`; chỉ sửa `so_gap` theo ID trong một lô ≤100. Không ghi tên/map hoặc dùng kho lịch sử. |
| `mo_tep_word.py`: `mo_word` | `3bced79c8a887e167a9dae39133e9675f2e847893de35355be3d435f544d48cb` | Gọi primitive B8 nguyên trạng, không chép reader/writer hoặc mở rộng whitelist. |
| `mo_tep_excel.py`: `mo_excel` | `d75afb2eee7886ed9f6ab55cee021257233ba216f465bf741c3452b3ddd87c7f` | Gọi primitive B8 nguyên trạng, giữ kiểm ô số/tiền/ngày và phần mới của AI. |

`phong_bi.py` bổ sung parser/bọc đọc mẫu 5/7; `chay.py` nối ba bước B7 và năng lực mở tệp; `engine.json` chỉ tăng gói 1.6.0 và thêm bộ T. Bảy định nghĩa năng lực cũ và schema chung giữ nguyên. Băm đích sau sửa và đối chiếu nguồn nằm ở `docs/SHA-NGUON-MASK-B9.json` ngoài gói; kiểm kê đề nghị cũng ở ngoài gói, chờ lead áp dụng. Các port Core còn thiếu được ghi C-P4-01…05, không xem adapter DEMO là binding vận hành. Chỉ DEMO, Cloud tắt, đã kiểm bằng Core giả (CoreGia), chưa Core/Office/Local thật.

## MASK-B8 — 16/11/2026, mở tệp một lần từ RAM

**Nguồn/quyền:** Anh/lead cho phép tiếp tục và chép có sửa mã nội bộ B1…B7/R4/R6 của chính gói Mask. Giữ quyền sử dụng nội bộ từ các mục nguồn bên dưới, không suy quyền phân phối ngoài tổ chức. Không chép nguồn ngoài, không sửa nguồn cũ/Core/SDK/engine khác, không thêm dependency. SDK 2.2.0 cài offline từ wheel repo, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp phát hành.

| Nguồn trong gói Python | Symbol tái dùng/chép có sửa → đích |
|---|---|
| `mo_che_ram.py`, `che_van_ban.py` | `kiem_map_ram`, `_VUNG`, `_DoManhBiDanh`, `chuan_bi_danh`, `_BI_DANH`, `_kiem_tien_ngay`; chuyển vòng mở chuỗi thành script vị trí `_MoAliasTep` trong `mo_tep_word.py`. Không dùng detector sau mở, không tra kho. Giữ bảng dò có trần và checkpoint. |
| `ho_so_tep.py` (HEAD B7), `kho_anh_xa_ram.py`, `quyen_yeu_cau.py` | `bao_ve`, `loi`, `KhoAnhXaRAM.buoc`, `_BuocRAM`, `_bam`, `_bo_tham_chieu`, `xac_minh`; thêm `MoTepRAM`/`TepDaMoRAM`. Bàn giao theo mô hình `MoCheRAM.mo` R6, context Core thoát sau chốt RAM; lỗi ACK không cache. |
| `tep_word.py`, `tep_excel.py` | Tái dùng thiết kế map/state B5/B6 và cleanup trong `_bao_ve` → `_doc_map`/`_bao_ve_mo`; chỉ nhận state B7 đã hậu kiểm đủ vùng. Không gọi đường che để mở tên. |
| `doc_word.py`, `doc_excel.py`, `xml_word.py`, `xml_excel.py`, `zip_an_toan.py` | Reader/gate/map nguyên trạng, ghép run cùng đơn vị logic, ST_Xstring, băm/trần/whitelist và từ chối phần lạ. Không nới profile hoặc đổi tên sheet. |
| `va_xml.py`, `ghi_zip.py` | `lap_kich_ban`, `ghi_goi`, `_goc_vung`, `chu_vung`, `bam`; patch theo byte trên chính tệp AI, shared chỉ patch một nguồn, đọc lại cả gói/ô số/bố cục đã nhận. Không serialize XML hoặc nén lại thành viên bất biến. |

Chỉ ba runtime đổi/thêm: `ho_so_tep.py`, `mo_tep_word.py`, `mo_tep_excel.py`. Word chứa primitive chung `_mo_tep`, Excel chỉ chọn reader của định dạng; không gọi/import engine khác. Phần mới giữ map, gốc và buffers trong handle RAM; không tệp tạm, hồ sơ Core, log, ngăn hoặc chuyển tiếp để phục hồi. Cả alias chính thức/tạm chỉ được mở nếu thuộc map bản cuối của đúng yêu cầu. Với tệp AI sửa, alias đã phát hành bị mất hoàn toàn cũng bị chặn; không đoán nội dung bị xóa. Map rỗng hợp lệ vẫn được khứ hồi.

`kiem_tep_mo` và `ban_giao_cuoi` là protocol tích hợp C-P4-05, **chưa phải API SDK**. Port xác minh quyền tệp/budget và cách ly bytes kết quả, chỉ phát hành sau RAM đã tiêu thụ và còn quyền/hạn. Descriptor budget chỉ số byte/trần, không phải đo OS peak hoặc xác nhận budget production. Reader vẫn trần bảo thủ 500.000 ký tự cả chiều đọc lại; không cam kết đạt đủ trần ra 2 triệu/8 MiB. B9 còn phải nối mẫu 7/bộ T, ACL tham chiếu con, upload và chốt SDK. Đã kiểm bằng Core giả (CoreGia); chưa Office/Local/Core/Linux thật, Cloud tắt.

Băm nguồn dưới dùng blob Git HEAD trước B8 (bytes gốc và LF giống nhau), kèm bytes checkout và LF thực tại lúc chốt; hiện vật ngoài gói `e_mask/docs/SHA-NGUON-MASK-B8.json` ghi đủ mốc Git và đối chiếu. `ho_so_tep.py` là đích sửa, 13 nguồn còn lại giữ nguyên nội dung LF. Không thay các băm lịch sử của các lát trước.

| Nguồn | SHA-256 blob HEAD (bytes = LF) | SHA-256 checkout bytes | SHA-256 checkout LF |
|---|---|---|---|
| `ho_so_tep.py` | `e09533a55d77c090c41d2bc15761a8ecb3fb0464fd26e5405e2818ccb10eb3c7` | `80b3e511a3912c0fcb10efc120d1049ffaa14675837706fca6847256d80ecafa` | `80b3e511a3912c0fcb10efc120d1049ffaa14675837706fca6847256d80ecafa` |
| `mo_che_ram.py` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` |
| `kho_anh_xa_ram.py` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` |
| `quyen_yeu_cau.py` | `ff44033652a45a7b70effb4e8f6cbb0217c50f85551a912a2657e779be2ba123` | `ff44033652a45a7b70effb4e8f6cbb0217c50f85551a912a2657e779be2ba123` | `ff44033652a45a7b70effb4e8f6cbb0217c50f85551a912a2657e779be2ba123` |
| `tep_word.py` | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` |
| `tep_excel.py` | `b22d1e60bacd13b7f10874b30d8d6d0b9685c88697e4c02fe27dfe5437758972` | `b22d1e60bacd13b7f10874b30d8d6d0b9685c88697e4c02fe27dfe5437758972` | `b22d1e60bacd13b7f10874b30d8d6d0b9685c88697e4c02fe27dfe5437758972` |
| `doc_word.py` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` |
| `doc_excel.py` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` |
| `va_xml.py` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` |
| `ghi_zip.py` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` |
| `xml_word.py` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` |
| `xml_excel.py` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` |
| `zip_an_toan.py` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` |
| `che_van_ban.py` | `206140bfe74302bcf560ba8020bf47835115284bab1d43dc2b14bb233fc32a83` | `206140bfe74302bcf560ba8020bf47835115284bab1d43dc2b14bb233fc32a83` | `206140bfe74302bcf560ba8020bf47835115284bab1d43dc2b14bb233fc32a83` |

| Đích mới | SHA-256 sau (bytes = LF) |
|---|---|
| `e_mask/mo_tep_word.py` | `3bced79c8a887e167a9dae39133e9675f2e847893de35355be3d435f544d48cb` |
| `e_mask/mo_tep_excel.py` | `d75afb2eee7886ed9f6ab55cee021257233ba216f465bf741c3452b3ddd87c7f` |

Kiểm kê gói nằm ngoài danh sách năm tệp runtime được giao: sinh bản đề nghị ngoài gói cho lead, không sửa kiểm kê thật. Kết quả lệnh chuẩn (kể cả lỗi nền) và thời gian thực tế tại VIEC/báo cáo B8.

## MASK-B6b l??t 2 ? 16/11/2026, quy?t ??nh lead v? ? ti?n

**Ngu?n/quy?n:** ti?p t?c ??ng runtime n?i b? `e_mask/tep_excel.py` c?a l??t 1 theo l?nh lead 16/11; kh?ng ch?p ngu?n ngo?i/th?m dependency. Symbol s?a: `_kiem_so_bat_bien`, h?m l?ng `kiem_da_khai`; d?ng l?i `PHIEN_BAN_CHUAN_HOA` n?i b? v? `viec.ngan.tim` SDK 2.2.0. Format th?c t? TI?N/K? TO?N gi? s? c? ph?n l? kh?c 0 ho?c s? nguy?n ?12 ch? s?; ?13 ch? s? d?ng c?ng gate General. Kh?ng s?a reader, API v1, Core ho?c c?c t?p B7.

??nh danh khai trong ds v?n qua ki?m ??u v?o; ? ti?n ???c mi?n detector ph?i tra ng?n b? m?t b?ng ??ng raw value/d?ng Decimal g?n, g?m d?u v? tr? tuy?t ??i. Serial ng?y h?p l? c?ng tra ??ng raw value. L?c ch?nh x?c gi? tr? chu?n h?a + phi?n b?n + v?ng tin c?y R4, ch? ki?m c? k?t qu?/tiep, kh?ng ??c b?n r? ho?c li?t k? kho, kh?ng ghi ng?n. Ki?m h?n/quy?n tr??c/sau t?ng truy v?n; cache ?ng vi?n ch? RAM, t?i ?a 2.000, v??t t? ch?i. Gi? nguy?n mi?n serial ng?y, General/0 v? gi?i h?n exponent `[-128,308]` t? l??t 1. Kh?ng g?i detector h?nh d?ng tr?n ? ti?n ???c mi?n theo quy?t ??nh m?i.

| Runtime n?i b? | SHA-256 tr??c l??t 2 (bytes = LF) | SHA-256 sau l??t 2 (bytes = LF) |
|---|---|---|
| `e_mask/tep_excel.py` | `dc62e2b3f0f3de0351b45e87c7b81d7cdc8a0b76a4f89533582e2401cd24ebbb` | `b22d1e60bacd13b7f10874b30d8d6d0b9685c88697e4c02fe27dfe5437758972` |

Ch? d? li?u DEMO, ?? ki?m b?ng Core gi? (CoreGia); ch?a Core/Local/Office/Linux th?t, Cloud t?t. Kh?ng s?a test B6 c?: k? v?ng ti?n `1000000000` gi? nguy?n nay ??ng quy?t ??nh lead. B6b b? sung ca 12/13/16 ch? s? v? ??nh danh ?? khai. R?i ro s? ??nh danh ch?a khai ?12 ch? s? c? ? ??nh d?ng ti?n ch? Anh x?c nh?n; k?t qu? v? gi? th?c t? ? VIEC.md. Ph?n l??t 1 b?n d??i gi? l?m l?ch s?.

## MASK-B6b — 16/11/2026, kiểm ô số theo format và giá trị

**Nguồn/quyền:** Anh/lead giao sửa `tep_excel.py` nội bộ của MASK-B6, tái dùng `_kiem_con_sot` và style hiệu lực từ reader B3 nguyên trạng. Không chép mã ngoài, không thêm dependency; `datetime.date` và `decimal.Decimal` thuộc thư viện chuẩn Python. Không sửa `xml_excel.py`, Core, API v1 hoặc tệp của B7; map và phép chuẩn hóa để kiểm chỉ trong RAM.

**Symbol sửa/thêm:** `_kiem_so_bat_bien`, `_format_so`, `_FORMAT_SAN`, `_FORMAT_NGAY`, `_FORMAT_TIEN`. Ưu tiên `style['formatCode']` đã được reader lấy từ khai báo; builtin chỉ là bảng format mặc định khi không khai báo. Reader B3 vốn từ chối khai lại ID dưới 164: giữ nguyên chốt này. Dùng tập format chính xác của profile, không tìm ký tự y/d/h/s trong chuỗi bất kỳ. Ngày có cận trên loại trừ 01/01/2101: epoch 1900 `[1,73416)`, epoch 1904 `[0,71954)`; phần thập phân là giờ.

Tiền không được miễn detector vì có style. Số nguyên từ 9 chữ số bị chặn, cả khi viết exponent/.0/dấu; chuẩn hóa Decimal chỉ để kiểm, giữ nguyên lexical đầu ra. Detector văn bản có thể nhận `1234567.89` như số tài khoản do ghép dấu chấm: chỉ dung sai cảnh báo thuộc nhóm số phủ toàn giá trị khi hai vế thập phân riêng đều qua cùng detector. Cảnh báo một phần/nhóm khác/chưa quét đủ vẫn từ chối. Exponent ngoài khoảng bảo thủ `[-128,308]` bị chặn trước khi mở rộng thành chuỗi; không cấp phát theo exponent cực đoan. Không suy mục đích số từ nhãn tiền.

| Runtime nội bộ | SHA-256 trước (bytes = LF) | SHA-256 sau (bytes = LF) |
|---|---|---|
| `e_mask/tep_excel.py` | `ef670c9775ec5ea97981d181324490433fc44ea3779edc473a1f78a8911a796c` | `dc62e2b3f0f3de0351b45e87c7b81d7cdc8a0b76a4f89533582e2401cd24ebbb` |

Held-out MASK-2c giữ nguyên blob Git LF `b3569b357132a7f7e0a7202b6e3d3c0b5fec2228c6ebd09604e7d05092485dd8`, băm nội dung `sha256:b720fb2d9a330110ed5c4d5fd777b9728887f863651a2b0c46dc395dc45c95ad`; gold R3 giữ SHA `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`. Chỉ trả CRLF checkout về byte LF đã khóa, không đổi nội dung/gold/assertion/ngưỡng. Đã kiểm bằng Core giả (CoreGia), không chứng nhận Local/Office/Core/Linux thật; Cloud tắt. Kết quả thật và giới hạn ở VIEC.md.

## MASK-B6 — 16/11/2026, Excel chỉ RAM

**Quyền và nguồn gốc:** Anh/lead giao MASK-B6 cho phép tái dùng mã nội bộ B1/B3/B4, MASK-2b và R2…R6 trong chính gói Mask. Các mục tương ứng bên dưới ghi nguồn/giấy phép trước đó; không suy quyền phân phối ngoài tổ chức. Chuyển có sửa khung nội bộ B5 (`tep_word.py`) sang Excel để dùng cùng hợp đồng R4/R5; không gọi đường Word hoặc import engine khác. Không sửa nguồn cũ, Core, SDK, manifest hay dependency. Đóng băng 19 nguồn trước sửa tại `e_mask/docs/SHA-NGUON-MASK-B6-TRUOC.json`; cả 19 nguồn giữ nguyên bytes sau lát. `tep_excel.py` trước chưa tồn tại.

| Nguồn trong gói Python | Symbol dùng lại / chép có sửa | Đích và khác biệt |
|---|---|---|
| `tep_word.py` (B5) | `_bao_ve`, `_kiem_buoc`, `_KhoWord`, `_LuotVung`, `_phep_alias`, `_kiem_vung`, `_gop_alias`, `_ghi`, `_luu_ram`, `_doc_ram`, `che_word`, `che_them_word`, `DauWordRAM` | Chuyển sang symbol Excel tương ứng trong `tep_excel.py`; giữ cleanup R4 và lỗi an toàn. Budget vị trí dùng chỉ số vùng; map shared có một nguồn, mọi nơi dùng phải khớp; patch một lần và cập nhật chung khi bổ sung Local. Thêm kiểm ô số/metadata số cần che thì chặn thay vì đổi kiểu. |
| `doc_excel.py`, `xml_excel.py` | `doc_excel`, `ExcelDaDoc`, `VungExcel.kiem_thay_the`, map chuỗi/ô/rich run/attribute/byte | Gọi reader B3 nguyên trạng trước và sau patch; giữ UTF-16/entity/ST/NFD/Cf, mọi nơi dùng shared và unused; không ghép hai ô, không đổi tên sheet. |
| `doc_tep.py`, `zip_an_toan.py`, `xml_an_toan.py`, `ghi_zip.py`, `va_xml.py` | Cổng B1/B3; `ghi_goi`, `bam`, `lap_kich_ban`, `_goc_vung` | ZIP/XML/trần/whitelist và writer B4 giữ nguyên. Script chỉ sửa vùng canonical của shared, đối chiếu lại chuỗi ở mọi ô, index/style/merge/epoch và lexical/bytes ô bất biến trên bytes ra thật. |
| `che_van_ban.py`, `tra_cuu_dinh_danh.py` | `_kiem_dinh_danh`, `thu_thap_ung_vien`, `_kiem_con_sot`, `_kiem_tien_ngay`, `numeric_review`, `TraCuuDinhDanh`, `UngVien`, các trần và cửa chặn R3 | Detector riêng từng vùng; tìm chính xác từng ứng viên qua R2, cache/budget chung trong RAM, không liệt kê danh mục bản rõ. Mơ hồ alias chặn toàn lượt. Cửa chất lượng R3 và hai lớp chưa được mở. |
| `chuan_bi_ai.py`, `anh_xa_ai.py`, `hau_kiem_ai.py` | `ket_qua_ram`, `_kiem_span`, `tao_anh_xa`, `kiem_anh_xa`, `alias_nguyen_van`, `_bien_thuc_the` | Kiểm map/tiền/ngày R5; giữ phép đối chiếu số nằm trọn ngày ISO của B5, vẫn chặn số/nghi vấn ngoài ngày. Primitive Local không chứng thực nguồn hoặc đủ đoạn và không đánh dấu đã kiểm Local. |
| `kho_anh_xa_ram.py`, `quyen_yeu_cau.py`, `ho_so_ai.py`, `kho_dinh_danh.py`, `kho_ngan.py`, `mo_che_ram.py` | `_BuocRAM`, `_bo_tham_chieu`, `loi_ram`, `loi_kho`, `json_chuan`, `KhoDinhDanh.mo_kho_nhan_dien`, kho R2, `_don_ngoai_le` | Handle R4 kiểm mã Core/quyền/instance/TTL. Tệp/map/bytes/script/budget chỉ ở `tep_excel` trong RAM; không snapshot, ngăn map, tệp tạm, upload hoặc chuyển tiếp. Kết quả primitive chỉ băm/số đếm, luôn `CHO_LOCAL`. |

| Tệp nguồn (từ gốc repo) | SHA-256 bytes trước = sau | SHA-256 LF trước = sau |
|---|---|---|
| `e_mask/goi/e_mask/e_mask/tep_word.py` | `cc46f3619c676ed5d7124387ee870e8a74f737baf55f07777a1b6b588e33eb0c` | `cc46f3619c676ed5d7124387ee870e8a74f737baf55f07777a1b6b588e33eb0c` |
| `e_mask/goi/e_mask/e_mask/doc_excel.py` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` |
| `e_mask/goi/e_mask/e_mask/xml_excel.py` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` |
| `e_mask/goi/e_mask/e_mask/doc_tep.py` | `7169ad765f8566479e9b88f4907be2d37e70fbaded112f2ced6dd75e18567646` | `7169ad765f8566479e9b88f4907be2d37e70fbaded112f2ced6dd75e18567646` |
| `e_mask/goi/e_mask/e_mask/zip_an_toan.py` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` |
| `e_mask/goi/e_mask/e_mask/xml_an_toan.py` | `b44819c30f722ce833329a945e97b6d72540fc2c83eb7c4444599570032d21be` | `b44819c30f722ce833329a945e97b6d72540fc2c83eb7c4444599570032d21be` |
| `e_mask/goi/e_mask/e_mask/ghi_zip.py` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` |
| `e_mask/goi/e_mask/e_mask/va_xml.py` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `fb20d043b46cddea2080b50904f88533c0990b7cf21cc434be8089beb72ead81` | `fb20d043b46cddea2080b50904f88533c0990b7cf21cc434be8089beb72ead81` |
| `e_mask/goi/e_mask/e_mask/tra_cuu_dinh_danh.py` | `11ec834e6a181c2dcdcb625677f6920e1996aeceead7c4fe465f617d403f7ddf` | `11ec834e6a181c2dcdcb625677f6920e1996aeceead7c4fe465f617d403f7ddf` |
| `e_mask/goi/e_mask/e_mask/chuan_bi_ai.py` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` |
| `e_mask/goi/e_mask/e_mask/anh_xa_ai.py` | `a507690ccb59886bfadc2723d49d5efe6ac2c99249dc3d5e029b8c4b64e4af82` | `a507690ccb59886bfadc2723d49d5efe6ac2c99249dc3d5e029b8c4b64e4af82` |
| `e_mask/goi/e_mask/e_mask/kho_anh_xa_ram.py` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` |
| `e_mask/goi/e_mask/e_mask/quyen_yeu_cau.py` | `ff44033652a45a7b70effb4e8f6cbb0217c50f85551a912a2657e779be2ba123` | `ff44033652a45a7b70effb4e8f6cbb0217c50f85551a912a2657e779be2ba123` |
| `e_mask/goi/e_mask/e_mask/ho_so_ai.py` | `17b86042a1f38159af789c2de746bfe68b98f2ea38de08a6dbd35330c8322b17` | `17b86042a1f38159af789c2de746bfe68b98f2ea38de08a6dbd35330c8322b17` |
| `e_mask/goi/e_mask/e_mask/kho_dinh_danh.py` | `fd8633450de5ae85484d78d74a8583b3efd5078f19a27221f14326975b16ecb9` | `fd8633450de5ae85484d78d74a8583b3efd5078f19a27221f14326975b16ecb9` |
| `e_mask/goi/e_mask/e_mask/kho_ngan.py` | `83c6cce6a586ae2901f3e5a40161e917999d8eeb8951b501d580e3db6b262fde` | `83c6cce6a586ae2901f3e5a40161e917999d8eeb8951b501d580e3db6b262fde` |
| `e_mask/goi/e_mask/e_mask/hau_kiem_ai.py` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` |
| `e_mask/goi/e_mask/e_mask/mo_che_ram.py` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` |

| Tệp đích mới | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|
| `e_mask/goi/e_mask/e_mask/tep_excel.py` | `ef670c9775ec5ea97981d181324490433fc44ea3779edc473a1f78a8911a796c` | `ef670c9775ec5ea97981d181324490433fc44ea3779edc473a1f78a8911a796c` |

**Giới hạn:** chưa có handler tệp/phát hành trong B6. B7/B9 phải kiểm hai lớp đủ mọi vùng và ngữ cảnh ô số/metadata, nguồn Local, quyền/lease/deadline và bàn giao thật; thiếu thì chặn. Primitive không nhận cờ caller để bỏ chặn. Writer/reader B1/B3/B4 hiện giữ bộ đếm bảo thủ 500.000 ký tự cả chiều đọc lại, sớm hơn trần ra 2.000.000; không tự nới profile. Trần ô 32.767 UTF-16 và trần ZIP/bytes ra vẫn kiểm riêng, không truncate. Format tiền/ngày thuộc whitelist giữ số và kiểu; số General hoặc metadata số mà detector yêu cầu che thì từ chối cả tệp. Sửa tệp đã phát hành/mở che thuộc B8; Core/Office/Local/Linux thật chưa kiểm. Đã kiểm bằng Core giả (CoreGia), chỉ DEMO, Cloud tắt.


Ngày bắt đầu đối chiếu: 14/11/2026. Chỉ DEMO. Lõi nội bộ từ Mask v2; nguồn cũ giữ nguyên. Handler che/mở che hiện đã có nghiệp vụ qua ngăn; các mô tả stub/kho tệp dưới đây là lịch sử từng lát. Trạng thái và băm mới nhất của lượt sửa nằm tại mục Sửa MASK-2b theo kiểm độc lập ở cuối tài liệu. Đã kiểm bằng Core giả (CoreGia).

## MASK-B5b — 16/11/2026, sửa miễn ngày theo nhãn và lịch

**Nguồn/quyền:** Anh/lead giao sửa hai runtime nội bộ đã có trong gói, dựa trên MASK-B5 và MASK-2b/R3/R6b. Không chép mã hoặc thêm thư viện bên ngoài; dùng `datetime.date` của thư viện chuẩn Python để kiểm lịch. Nguồn cũ giữ nguyên. Không sửa Core, SDK, engine khác hoặc mã Excel; map vẫn chỉ RAM theo MASK-P4.

**Symbol sửa/thêm:** `che_van_ban._cac_tien_ngay`, `_kiem_con_sot`, `_nhan_dinh_danh_truoc`, `_ngay_hop_le`, `_so_dang_ngay_co_nhan`, `_duoc_mien_ngay`; `tep_word._kiem_vung`. Cửa sổ nhãn 120 ký tự, dừng tại biên đoạn/trường; bản dò bỏ dấu/Cf, tọa độ và nội dung gốc giữ nguyên. Vùng giá trị đã gắn nhãn bằng `_vung_nhan`/mẫu tài khoản R5 là bằng chứng độc lập, vẫn chặn miễn ngày khi nhiều khoảng trắng đẩy nhãn ra ngoài cửa sổ gần. Năm ngoài 1900–2100 hoặc hai chữ số không được miễn theo ngày; không đoán thế kỷ. Ngày viết chữ không có năm chỉ kiểm ngày/tháng, cho phép 29/2. Không thêm tài nguyên detector từ held-out.

| Runtime nội bộ | SHA-256 trước (bytes = LF) | SHA-256 sau (bytes = LF) |
|---|---|---|
| `e_mask/che_van_ban.py` | `fb20d043b46cddea2080b50904f88533c0990b7cf21cc434be8089beb72ead81` | `206140bfe74302bcf560ba8020bf47835115284bab1d43dc2b14bb233fc32a83` |
| `e_mask/tep_word.py` | `cc46f3619c676ed5d7124387ee870e8a74f737baf55f07777a1b6b588e33eb0c` | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` |

SDK 2.2.0 cài offline từ wheel repo, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp sổ phát hành; không thêm dependency. Kiểm kê bao mọi tệp gói theo bytes LF thực tế, trừ chính kiểm kê. Đã kiểm bằng Core giả (CoreGia), chưa Core/Local/Office/Linux thật. Phép đo hồi quy nhánh quy tắc lịch sử không chứng nhận chất lượng Local/hai lớp; Cloud tắt.

## MASK-B5 — 16/11/2026, Word chỉ RAM

**Quyền tái dùng:** Anh/lead giao MASK-B5 cho phép dùng B1/B2/B4, MASK-2b và R2…R6 trong chính gói này. Đây là mã nội bộ đã có nguồn/quyền ở các mục tương ứng của NGUON; không suy thêm quyền phân phối ngoài tổ chức. Không chép hoặc import engine khác, không sửa nguồn cũ, Core, SDK hoặc thêm dependency. Runtime mới chỉ dùng SDK 2.2.0 và thư viện chuẩn. Nguồn bytes trước được đóng băng tại `e_mask/docs/SHA-NGUON-MASK-B5-TRUOC.json`; mọi nguồn liệt kê bên dưới giữ nguyên bytes sau lát.

| Nguồn trong gói Python | Symbol dùng lại / chuyển có sửa | Đích và khác biệt |
|---|---|---|
| `doc_word.py`, `xml_word.py` | `doc_word`, `TaiLieuWord`, `VungWord`, map lexical và whitelist | Gọi reader B2 nguyên trạng trước/sau patch; không tự mở rộng whitelist |
| `va_xml.py`, `ghi_zip.py` | `bam`, `lap_kich_ban`, `ghi_goi` | Gọi writer B4 nguyên trạng; chuyển map gốc/che thành lệnh theo span, không serialize cây |
| `che_van_ban.py`, `tra_cuu_dinh_danh.py` | `_kiem_dinh_danh`, `thu_thap_ung_vien`, `_kiem_con_sot`, `_kiem_tien_ngay`, `numeric_review`, `TraCuuDinhDanh`, `UngVien` | Detector riêng mỗi vùng; cache tìm chính xác, số ứng viên/vị trí/chi phí dùng chung mọi vùng trong RAM; không matcher danh mục |
| `chuan_bi_ai.py`, `anh_xa_ai.py` | `ket_qua_ram`, `_kiem_span`, `tao_anh_xa`, `kiem_anh_xa`, `alias_nguyen_van` | Chép chọn lọc kiểm map/tiền/ngày vào `_kiem_vung`: khi R5 báo số nằm trọn ngày ISO mà MASK-2b đã nhận diện thì đối chiếu từng khoảng, vẫn kiểm đủ và số/tiền/ngày; nghi vấn ngoài ngày vẫn chặn. Không tạo phong bì có cờ phát hành |
| `kho_anh_xa_ram.py`, `ho_so_ai.py`, `kho_dinh_danh.py` | `_BuocRAM`, `_bo_tham_chieu`, `json_chuan`, `KhoDinhDanh.mo_kho_nhan_dien` | Dùng handle R4 thật, lấy quyền từ chính kho sở hữu; dữ liệu tệp chỉ trong dictionary `tep_word`, không tạo hồ sơ hoặc mã yêu cầu riêng |
| `hau_kiem_ai.py`, `mo_che_ram.py` | `_bien_thuc_the`, `_don_ngoai_le` | Kiểm biên primitive che bổ sung và bỏ frame lỗi nhạy cảm; không dùng primitive làm chứng thực Local hoặc đường mở tệp |

| Tệp nguồn (từ gốc repo) | SHA-256 bytes trước = sau | SHA-256 LF trước = sau |
|---|---|---|
| `e_mask/goi/e_mask/e_mask/doc_word.py` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` |
| `e_mask/goi/e_mask/e_mask/xml_word.py` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` |
| `e_mask/goi/e_mask/e_mask/va_xml.py` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` |
| `e_mask/goi/e_mask/e_mask/ghi_zip.py` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `90bc453bd4aa8fcca5d770d69f888d6ec6a779c718432433b6ccf16728fcce40` | `90bc453bd4aa8fcca5d770d69f888d6ec6a779c718432433b6ccf16728fcce40` |
| `e_mask/goi/e_mask/e_mask/tra_cuu_dinh_danh.py` | `11ec834e6a181c2dcdcb625677f6920e1996aeceead7c4fe465f617d403f7ddf` | `11ec834e6a181c2dcdcb625677f6920e1996aeceead7c4fe465f617d403f7ddf` |
| `e_mask/goi/e_mask/e_mask/chuan_bi_ai.py` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` |
| `e_mask/goi/e_mask/e_mask/kho_anh_xa_ram.py` | `05449c3e3664b596fc567e355617db97d23935fc0d94d8bc5850b25dcef07f01` | `05449c3e3664b596fc567e355617db97d23935fc0d94d8bc5850b25dcef07f01` |
| `e_mask/goi/e_mask/e_mask/ho_so_ai.py` | `17b86042a1f38159af789c2de746bfe68b98f2ea38de08a6dbd35330c8322b17` | `17b86042a1f38159af789c2de746bfe68b98f2ea38de08a6dbd35330c8322b17` |
| `e_mask/goi/e_mask/e_mask/hau_kiem_ai.py` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` |
| `e_mask/goi/e_mask/e_mask/mo_che_ram.py` | `0e2e43e91a90d668725fb3440300f4453447e8c37ce93d7d9560b48badfac87b` | `0e2e43e91a90d668725fb3440300f4453447e8c37ce93d7d9560b48badfac87b` |
| `e_mask/goi/e_mask/e_mask/kho_dinh_danh.py` | `fd8633450de5ae85484d78d74a8583b3efd5078f19a27221f14326975b16ecb9` | `fd8633450de5ae85484d78d74a8583b3efd5078f19a27221f14326975b16ecb9` |
| `e_mask/goi/e_mask/e_mask/anh_xa_ai.py` | `a507690ccb59886bfadc2723d49d5efe6ac2c99249dc3d5e029b8c4b64e4af82` | `a507690ccb59886bfadc2723d49d5efe6ac2c99249dc3d5e029b8c4b64e4af82` |

| Tệp đích mới | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|
| `e_mask/tep_word.py` | `cc46f3619c676ed5d7124387ee870e8a74f737baf55f07777a1b6b588e33eb0c` | `cc46f3619c676ed5d7124387ee870e8a74f737baf55f07777a1b6b588e33eb0c` |

`tep_word.py` là tệp mới, trước lát chưa tồn tại. Ngoài tệp đó không sửa runtime nào trong bốn tệp được giao. Băm sau là toàn tệp, không phải băm artifact phát hành. LF chỉ thay CRLF thành LF, không chuẩn hóa Unicode. Các hàm gọi lại nguồn, không phải các bản chép nguyên tệp; phần kiểm ngày ISO được chuyển có sửa như mô tả trên.

`che_word(bytes, buoc=handle_R4, dinh_danh=...)` và `che_them_word(((ma_vung, UngVien), ...), buoc=handle_R4)` chỉ trả `DauWordRAM` gồm băm và số đếm. Gốc, reader, bytes che, map Unicode/byte, script patch, alias → nguyên văn, cache và budget chỉ ở `buoc.du_lieu['tep_word']`. Trạng thái luôn `CHO_LOCAL`, tập vùng đã kiểm Local rỗng; không nhận cờ caller chứng nhận Local. B7 phải kiểm nguồn/đủ đoạn/span rồi mới gọi primitive; B9 kiểm lại nguồn/quyền trước upload. Không tự lấy nguyên văn model hoặc tên từ ngăn để lập map. Tên mới chưa có bảo đảm C-P4-03 bị chặn; chất lượng R3 vẫn chưa chứng minh.

NFD ngoài vùng thay và tiền/ngày giữ nguyên; Cf/selector bỏ đúng map MASK-2b. Tên nhiều run chỉ trong cùng vùng logic; alias mới ghi vào span đầu, giữ các thẻ/format của mọi run. Không xóa markup Cf hoặc vùng chưa hiểu: từ chối toàn tệp. Phần bất biến giữ payload nén/local record gốc bằng B4; reader lại bytes và đối chiếu từng vùng. Kết quả băm/số vùng chỉ xác nhận xử lý nội bộ, không là báo cáo an toàn hai lớp.

TTL/vòng đời theo R4, snapshot cấu hình SDK 600 giây trong 60–900; retry không kéo dài. Ghi hoặc cập nhật trạng thái tệp dưới cùng khóa timer/hủy R4, kiểm sở hữu/hạn ngay trong khóa; không gọi port dưới khóa và không dựng lại dictionary đã dọn sau checkpoint. Dọn dữ liệu ngay khi lỗi, chặn tái dùng bước lỗi và để R4 kết thúc bản ghi lúc ra `with`; timer/hủy/kết thúc/tiêu thụ bỏ cả bytes/map. Python không bảo đảm xóa vật lý mọi bản sao RAM. Không log/stderr/tệp tạm/ngăn/hồ sơ/chuyển tiếp map. Trần ZIP/XML vào/ra giữ nguyên B1/B4; reader đọc lại vẫn bảo thủ 500.000 ký tự trước trần ra 2 triệu, chưa mở rộng profile.

Test Word nội bộ dùng ngăn SDK null+cờ/tìm chính xác thật với CoreGia và adapter quyền/vòng đời ngoài gói; không nguồn Local thật và không handler tệp. Đã kiểm bằng Core giả (CoreGia), chưa Core/Office/Local/Linux thật; Cloud tắt. C-P4-01…05 và kết quả thật tại VIEC/báo cáo B5. Không có quyền phục hồi từ Core hoặc giải mã trường bí mật.

## MASK-R1 — sửa tương thích cấu hình, 15/11/2026

Sửa mã nội bộ `e_mask/chay.py` theo ngoại lệ lead cho phép thêm tệp ngoài giới hạn 5 tệp R1. Bỏ guard cấu hình phải rỗng đã lỗi thời; SDK 2.2.0 kiểm schema và điền TTL default 600 trước handler. Giữ nguyên các bước xác minh ngữ cảnh/port, mã lỗi, hậu kiểm và kho RAM vận hành cũ tới R2/R4. Không chép nguồn ngoài hoặc thêm dependency; schema đã có default cho mọi trường mới, TTL số nguyên 60–900. Test cập nhật ở `e_mask/tests/test_mask_s22.py`; đã kiểm bằng Core giả (CoreGia).

SHA-256 LF của `e_mask/chay.py`: trước `3afb29b2364a5dca5d35f6dc5a1ca12a447badf52f77a281aecb1f6bfbadc5ff`, sau `028927044ad00d3533bcfc81c94326a9348a194ab21030ff36002a2ad6c46811`. Kiểm kê gói giữ bytes/SHA thực tế của toàn gói trừ chính kiểm kê, bao gồm tài liệu đã cập nhật; không dùng SHA LF thay SHA bytes đóng gói.

## Năm tệp chép vào gói

Đường nguồn tính từ gốc repo; đường đích tính từ thư mục chứa tài liệu này. SHA trước giữ bản nguồn, SHA sau trong bảng privacy phản ánh bản gói hiện tại. Hai cột SHA LF tính sau đổi CRLF thành LF để kiểm trên Linux/Windows; không đổi nội dung ngoài xuống dòng. Test so SHA LF, vì checkout Git có thể đổi xuống dòng. Hai matcher tên chép nguyên byte trong worktree này.

| Đường nguồn | Đích trong gói | SHA trước (byte) | SHA sau (byte) | SHA trước (LF) | SHA sau (LF) | Điều chỉnh |
|---|---|---|---|---|---|---|
| `e_mask/ma-nguon/nguon/privacy/__init__.py` | `e_mask/nguon/privacy/__init__.py` | `ad88cdef05aa5862fb2e34bab1b19bc2e80727e40cabdbe9246133f8e846096f` | `bff7a8d02fd5f38b6876ea7930a2cdbcbbed9e85d2b3b6883005506a92f602c3` | `089a17a5759e62cb2e7a4f160bb88ac248ea4a8e2a507f1c7aad323a123e6845` | `584c0a757e561d88a1d2e624400c3f41908ae59167c7e734c02e19cdaa9cf181` | Ghi rõ phiên bản nguồn 2.7.2 chỉ là thông tin nguồn; không gọi ứng dụng cũ. |
| `e_mask/ma-nguon/nguon/privacy/types.py` | `e_mask/nguon/privacy/types.py` | `c99ab1584d732dd35938d2cca4202129673bb4507ada4ec77a96cea7eaa1141a` | `4a9c8ba7c5e75a10e4dd7aea371c40298742c85fbbd00a4e6dd1977c1a5105ef` | `59acab78646831909af6da5d54b292c0ad35929fbbff8b526084853bbf02c562` | `962dccced2516f246db56ab84be07d3cb3d6fdd4dfcfe43c937c3795aa5a49d4` | Bỏ Cf/selector trước NFC, ánh xạ nguyên văn; MASK-2c-1 thêm khoảng bỏ và biên tổ hợp dùng chung. |
| `e_mask/ma-nguon/nguon/privacy/core.py` | `e_mask/nguon/privacy/core.py` | `1b0cc53af256f6cfcb3ce2eeebe28eabb574c3b2cf3f82e1bdb4535732876029` | `842a978dafacb1d9e92ebc235917cab15910c66140380f7a695b87fc94255f75` | `287616e854e5c6a59be5a2531638dd5f68dda2df387b0ff778b770da4ff44075` | `80b89e308d02212f42e3bc4ea23fcd60fdd146d2593cf5fe45ec600ccc7df990` | Bỏ mã hóa bảng và xuất TXT/Word/ZIP cùng import liên quan; detector import khi gọi, thiếu thì từ chối. Giữ KnownText/nhóm/vị trí/bảo vệ số/numeric_review; thay bí danh [[...]], giữ mã Junsky, số tự sinh tối thiểu 4 chữ số không cắt; bỏ cụm gốc khỏi lỗi trùng; replace giữ phần NFD chưa thay và verify giữ ranh giới bí danh. MASK-2: numeric_review giữ ranh giới số bằng NUL thay vì nối qua bí danh. |
| `e_mask/ma-nguon/nguon/privacy/company_names.py` | `e_mask/nguon/privacy/company_names.py` | `b3c595c193b3711737846762112654e45d8448fd9b6922903154b1d3d302d958` | `b3c595c193b3711737846762112654e45d8448fd9b6922903154b1d3d302d958` | `56a6b584d2e78161182413df61c6391e21c9c6fa8f64d2c483e5f849fc3a2fb3` | `56a6b584d2e78161182413df61c6391e21c9c6fa8f64d2c483e5f849fc3a2fb3` | Chép nguyên byte; giữ matcher và vị trí tên doanh nghiệp. |
| `e_mask/ma-nguon/nguon/privacy/person_names.py` | `e_mask/nguon/privacy/person_names.py` | `68d77c172b618a309722350af8910cc7323d93f11c6347cbc152dbe4d70aed7a` | `68d77c172b618a309722350af8910cc7323d93f11c6347cbc152dbe4d70aed7a` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | Chép nguyên byte; giữ gợi ý tên người có nhãn. |

## Đoạn mã tham chiếu trong repo

Ngoài năm tệp trên, chỉ đọc các đoạn sau; không mang thêm mô-đun vào gói:

- `e_mask/ma-nguon/nguon/privacy/detectors.py` — SHA byte: `b184b163d1b1f9c17fce2fe00f443b39b54d3894c8e4b054d0482f58a0a41ce0`; SHA LF: `793419cc7e649947040dd0abd1be2d76a02a038f8f92580bf56fb44cf64f5039`. Chép nguyên ba regex MONEY_NEAR, MONEY, DATE vào core.py để bảo vệ số mà không nạp detector/tài nguyên.
- `e_mask/ma-nguon/che_van_ban.py` — SHA byte: `0d8427b52e24d58abd12c036eecb55fb00dc71c125bc103cca814df387602244`; SHA LF: `f390dc60df977b768e1bcede3ec90ba63f20d0d79cd36507313c7ecd1c9221cd`. Tham khảo nguyên tắc _nfc_vi_tri, bản dò NFC trả khoảng vị trí gốc; hiện thực chuan_hoa_vi_tri trong types.py, dùng None cho ánh xạ đồng nhất.
- `e_mask/ma-nguon/kho_bo_nho.py` — SHA byte: `587b72a8a6b3ddea29aa12175fa877e994486a2719cca74b7fedb71336b54e22`; SHA LF: `e02c9582872cc289fe0e46683f81ca9c0a3c9a3e8d1a4db38b2eb874079c7d62`. Đối chiếu khuôn bí danh 1–100 ký tự và họ tiền tố MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC; không chép kho DEMO vào gói.

## Giới hạn và quyết định tạm

- Chỉ dùng thư viện chuẩn Python và SDK 2.0.0; không thêm thư viện chạy. Đã tách import cryptography/python-docx, encrypt_mapping/decrypt_mapping, make_docx/export_document/export_bundle khỏi bản chép. Hiện vật nguồn vẫn giữ để lead xem xét lưu trữ sau.
- `suggest` chỉ là gợi ý thủ công có trần 500 dòng; không dùng làm bộ che tự động. `suggest`, `dau_vet` và `verify(known=...)` chưa có detector sẽ báo lỗi nội bộ cố định, không trả kết quả kiểm giả. Detector/hậu kiểm đầy đủ thuộc MASK-2.
- Khuôn bí danh bọc `[[...]]`, mã bên trong tối đa 100 ký tự theo lõi văn bản cũ. Mã Junsky do danh mục cấp được giữ nguyên, không đánh lại số. Mã tự sinh nội bộ dùng họ MASK theo nhóm, tối thiểu bốn chữ số, nối tiếp số lớn nhất đã dùng theo tiền tố không phân biệt hoa thường; số vượt khuôn bị từ chối. Đây chỉ là helper DEMO, không cấp mã chung có giao dịch; kho cấp mã ở MASK-3.
- Họ tiền tố MASK còn chờ lead xác nhận không trùng Junsky thật. Không có bằng chứng danh mục thật; không tự đổi mã Junsky. Cổng chưa dùng helper này để phát hành bí danh.
- normalize giữ NFC và quy tắc ký tự điều khiển cũ. Bản dò có ánh xạ để matcher/replace nhận NFC/NFD nhưng giữ nguyên phần chưa thay của chuỗi gốc; vị trí tính theo chỉ số ký tự Python trong đầu vào.
- numeric_review đối chiếu chuỗi số sau thay theo danh sách đã chấp nhận. Đây chưa phải hậu kiểm tiền/ngày độc lập đầy đủ; không dùng để xác nhận an toàn Cloud.
- Lỗi trùng không chứa cụm gốc. Cổng vẫn chỉ trả LoiNghiepVu CHUA_LAM tiếng Việt cố định từ MASK-0; khi nối lõi ở lát sau phải ánh xạ PrivacyError sang mã/câu cố định theo phiếu, không dùng str(lỗi).
- Không chạy nguồn ngoài, bộ nhận dạng, dịch vụ hoặc AI. Không có kho bảng ánh xạ/tệp tài liệu trong gói.

## Dependency và môi trường kiểm

- Checkout lúc bắt đầu chưa có MASK-0; khôi phục đúng 10 tệp e_mask từ commit `c3e68148b5db837912a40ea39aa4539f53c3fca0` bằng đọc Git object vào worktree. Không đổi Git index, không commit/push. Lead cần đồng bộ dependency khi mở PR; tập mã MASK-1 chỉ gồm năm tệp nêu trên.
- `.venv` cài SDK offline từ wheel trong repo, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`, khớp SHA256SUMS; SDK in 2.0.0. Dùng --system-site-packages để dùng pytest 9.1.1 có sẵn làm công cụ kiểm, không cài thêm thư viện ngoài SDK. Test import riêng dùng -I -S -B để chứng minh năm tệp chỉ cần thư viện chuẩn.
- Đặt PYTHONDONTWRITEBYTECODE=1 và PYTHONUTF8=1 khi chạy ba lệnh kiểm; gói không có tệp biên dịch.

## Bổ sung MASK-2 — 14/11/2026

Chỉ năm tệp mã chạy thay đổi: `nguon/privacy/{detectors,leftovers,core}.py`, `che_van_ban.py`, `tai_nguyen.py`. Bảng MASK-1 phía trên cập nhật SHA đích core.py theo bản hiện tại; nguồn cũ giữ nguyên. Ba bản chép bổ sung:

| Đường nguồn | Đích trong gói | SHA trước (byte) | SHA sau (byte) | SHA trước (LF) | SHA sau (LF) | Điều chỉnh |
|---|---|---|---|---|---|---|
| `e_mask/ma-nguon/nguon/privacy/detectors.py` | `e_mask/nguon/privacy/detectors.py` | `b184b163d1b1f9c17fce2fe00f443b39b54d3894c8e4b054d0482f58a0a41ce0` | `af46757cdc72c4841ae49dbc3472423eed2aca6936db65074485fe868c471b8e` | `793419cc7e649947040dd0abd1be2d76a02a038f8f92580bf56fb44cf64f5039` | `c252cc424c43bae0b832902006ba558702b4ff6add09e51604f921032a023a00` | Bỏ đường data mặc định; nạp whitelist, cache có thu hồi; kiểm đủ bốn nguồn cả khi không khớp mẫu. |
| `e_mask/ma-nguon/nguon/privacy/leftovers.py` | `e_mask/nguon/privacy/leftovers.py` | `36c43a45c06bd321a5296860ff3e93d31bd7c99af080db42c56cfd259df190e7` | `928277ea2ff26bd2815f423c18628ee9b74fb7aa80642dc7e67335deaeaab744` | `978f8e4dcf0155e2ae1b6c3b3f9ef23085416239e4327ebdef7f48a76144a163` | `ca7611b817a22927f5d33b55bae6f601461ccacaa88c97c2f43ffd3f45b8ab72` | Nạp allowlist qua nguồn được whitelist; giữ lớp quét hậu kiểm nguồn. |
| `e_mask/ma-nguon/che_van_ban.py` | `e_mask/che_van_ban.py` | `0d8427b52e24d58abd12c036eecb55fb00dc71c125bc103cca814df387602244` | `93f1c505b399d0a6f5186160f25b8194afb2bd89ebf5c07d696891dadd36cfac` | `f390dc60df977b768e1bcede3ec90ba63f20d0d79cd36507313c7ecd1c9221cd` | `14e9c626e8f4de6d603ea9b6af4ca51694a433376514f6a070f500ddab3ee63d` | Giữ trần, matcher, hậu kiểm độc lập, Counter tiền/ngày, chặn chuỗi chưa kiểm hết; chỉ ẩn token đúng khuôn, giữ dấu vết ngoặc hỏng, ranh giới mã và kiểm tiền/ngày khi mở. |

`tai_nguyen.py` viết mới bằng thư viện chuẩn: `nap_cau_hinh` chỉ nhận cấu hình nội bộ tin cậy `{tai_nguyen: {<tên>: {duong_dan, sha256}}}` cho đúng bốn nguồn. Đường tuyệt đối ngoài gói, tệp thường, UTF-8 và SHA-256 khớp; đọc trọn snapshot rồi mới dùng, cấu hình lỗi thu hồi snapshot/cache cũ. Mặc định không có whitelist, luôn `MASK_THIEU_TAI_NGUYEN`; không dò thư mục, tải nguồn, tạo từ điển hoặc dùng fixture làm fallback. SHA do lead cung cấp, không do đầu vào công việc tự khai. Kênh cấu hình máy MASK-0 vẫn giữ schema rỗng: chưa nối nạp whitelist vào adapter khi chưa được lead cấp nguồn sạch; hàm nạp này chỉ là giao diện nội bộ cho adapter sau.

`tests/ho_tro_kho_demo.py` chép từ `ma-nguon/kho_bo_nho.py`, chỉ đổi import về gói mới, không nằm trong gói chạy. Tận dụng toàn bộ test_che_van_ban.py, tự chứa fixture DEMO, bỏ import engines/tests/tools/Core cũ; test không chứng minh giao dịch/quyền Core thật. Kho được bên tin cậy tiêm; lõi không tự cấp quyền hoặc mã yêu cầu. Port/transport vận hành thuộc MASK-3; hai handler vẫn là stub.

Giới hạn được giữ: 500.000 ký tự đầu vào, 500 định danh đã biết, giá trị tối đa 300, nhóm tối đa 20 và phải thuộc danh mục nhóm. Detector tìm 501 cụm vẫn quét và che cả 501, không đi qua suggest/validate_rules có trần danh sách. Chuỗi liền quá dài được đánh dấu chưa kiểm đủ, không cắt đầu vào và không công bố văn bản; ba chuỗi hiệu năng 500.000 ký tự giữ ngưỡng xử lý 5 giây, tiến trình con 12 giây.

Khi còn sót/lỗi detector/chưa kiểm đủ/đổi tiền-ngày, kết quả nội bộ chặn văn bản. ThieuTaiNguyen mang mã cố định `MASK_THIEU_TAI_NGUYEN`; adapter sau ánh xạ cờ hậu kiểm sang `LoiNghiepVu` mã `MASK_DINH_DANH_CHUA_DAT` hoặc `MASK_TIEN_NGAY_THAY_DOI`, dùng câu cố định và không dùng str(lỗi)/cụm gốc. Chưa thay mẫu 1–4 hay phong bì Core.

Heuristic không bảo đảm phát hiện tên người viết thường không nhãn. Ca DEMO minh họa giới hạn được giữ trong test; từ vựng DEMO ít và test đạt không chứng minh đủ điều kiện Cloud. Bốn tài nguyên sạch vẫn chờ lead whitelist, Cloud chưa bật. Những mô tả “chưa có detector” ở phần MASK-1 là lịch sử; MASK-2 đã có mã detector nhưng chưa có nguồn vận hành sạch.

## Bổ sung MASK-3 — 14/11/2026

Chỉ bốn tệp mã chạy mới. Không thêm dependency ngoài thư viện chuẩn và SDK 2.0.0; hai handler vẫn là stub, việc nối nghiệp vụ thuộc MASK-5. Chỉ DEMO, đã kiểm bằng Core giả (CoreGia) và port kho/quyền giả. Không có transport kho/danh tính mặc định, không có kho tên gốc trên đĩa hoặc kho RAM vận hành.

| Tệp trong gói Python | Nguồn / điều chỉnh | SHA-256 đích (byte và LF giống nhau tại bàn giao) |
|---|---|---|
| `e_mask/kho_qua_core.py` | Chuyển nguyên tắc snapshot/nhật ký/chốt từ `e_mask/ma-nguon/kho_qua_core.py`; giữ hai thao tác port nội bộ và toàn bộ 11 vector cũ. Bỏ phụ thuộc cổng thế hệ trước, thêm nguồn quyền tin cậy, mã opaque, dấu chống trùng và đối soát chốt chưa rõ. | `5914a2818f0ff8bad6aa217dcd7e9ef466c116d51670fa35a7cd3cb017f0d86e` |
| `e_mask/LUU-TRU/mask_truoc_ngan/kho_tam.py` (ngoài gói chạy) | Hiện vật lịch sử MASK-3: kho tệp theo phiếu §2.4 cũ; đã chuyển nguyên byte ra LUU-TRU ngày 15/11/2026, không còn trên đường chạy. Kho hiện tại dùng cổng Ngan. | `f59171f0094a6093a338a9894a0695f6ce8d2a2d66f4acd1769714c1555714f5` |
| `e_mask/kho_dinh_danh.py` | Viết lớp ghép port/quyền cho protocol Kho có sẵn; kiểm kết quả trước chốt và sau đọc lại, không có vòng gửi kết quả riêng. | `c23be50fd1d64a32f142a1a9eb5b870f624e667f4640387cb8f05fd76e5766a4` |
| `e_mask/quyen_yeu_cau.py` | Viết port danh tính/quyền; thiếu nguồn xác minh thì từ chối, không suy từ tham số/đầu vào/pháp nhân. | `4f44b32ec0c89ee40023dbd38502e9615f3522aaf648b9b15bb4b3c00cd17a4c` |

Nguồn `ma-nguon/kho_qua_core.py` giữ nguyên: SHA byte `2dd5c5f3ea64711a31f17265ba4e3b75a17e136258ae94c157cf2e6bb91dee15`; SHA LF `3608e50f82c76cde036afcc309bc4f01656e1a0cb4a17679ba9c7e106a547c78`. KhoBoNho từ nguồn cũ đã được MASK-2 chép ra helper test, nay tập trung tại `tests/ho_tro_core_gia.py`; helper `ho_tro_kho_demo.py` chỉ chuyển tiếp import. Fixture quyền/kho, máy chia sẻ RAM cho hai tiến trình và adapter SDK thử nghiệm đều ngoài gói chạy. Mã nguồn gốc giữ nguyên, không xóa/di chuyển.

Port này chưa công bố API ngăn mới. Core cần cấp mã ổn định theo việc/bước, kiểm phiên/module/người/tài liệu/vùng, quyền và lease tại snapshot/chốt/đọc lại, cùng CAS/duy nhất/ghi lô nguyên tử phía kho. Kho tạm chỉ băm mã và nội dung, không lưu nhật ký chứa cụm gốc hay kết quả; `ChuaRo` chỉ khi bên kho đã nhận chốt chưa trả, giao lại hỏi nguồn trước. Phần gửi lại kết quả thuộc SDK. Tiền tố cấp alias tại MASK-3 tập trung trong `TIEN_TO_TU_SINH`; còn chờ xác nhận họ MASK không trùng Junsky thật. Không đổi helper/matcher thuộc các lát lõi trước.


## Bổ sung MASK-3b → MASK-6 — 15/11/2026

Các mô tả stub/chờ tài nguyên/kho tệp ở các mục trên là lịch sử bàn giao. Handler hiện dùng ngăn và tài nguyên sạch đã duyệt theo lệnh giao mới nhất. Hai bản ngan.py, cau_hinh.py viết tạm bằng thư viện chuẩn theo đặc tả SDK 2.1 vì mẫu NGAN-0 đang làm song song; lead thay nguyên tệp khi gộp, hai test so SHA tạm skip. Không thêm dependency chạy.

Bốn từ điển chép nguyên byte từ e_mask/tham-chieu/tu-dien/ vào e_mask/tu_dien/. Nguồn là Mask v2 nội bộ đã được lead lọc sạch; ghi chú chờ duyệt trong bản nguồn là lịch sử, lệnh giao mới nhất xác nhận Anh đã duyệt. Gói không chứa danh mục đối tác thật. Nạp kiểm SHA bằng SHA256.json, test so byte với bản tham chiếu.

| Tệp | SHA-256 nguồn và bản gói |
|---|---|
| `common_acronyms.txt` | `920f0952f2584ece4c37d5419c073cd6f60cf151da3b38b1e68fdd6a2bb24f4e` |
| `leftover_allowlist.txt` | `7074f53c296bd7be258610335adc270879eccb2db63fa412c7a9088b077aea4b` |
| `vn_places.txt` | `e991d899a1fa2265082e871715a653c9ca4fd7ed233a8d3951fb80b7a2d41847` |
| `vn_surnames.txt` | `b9fc76e5fa1ebb6abca7f4bc7c58d0dd9ecffc992e642a21958449080b2aaad1` |

Kho mới giữ nguyên nguyên tắc snapshot/chốt của MASK-3, chuyển thành adapter API ngăn chung; dùng dòng CAS bảo vệ năm bảng. Chỉ dấu/băm/số đếm và định danh cần che được giữ; không cache tài liệu hoặc kết quả AI. Cổng quyền vẫn là port được bên tích hợp tin cậy cấp. Tệp kho_tam.py/cau_hinh_may.py đã chuyển nguyên byte sang `e_mask/LUU-TRU/mask_truoc_ngan/`, ngoài gói chạy; handler không import các hiện vật này.

Schema van_ban_da_che tạo theo phần đã duyệt của sổ loại riêng, chép nguyên byte vào gói; hai schema van_ban_tai_lieu/tra_loi_ai chép từ sổ chung, không sửa nguồn. Test so SHA cả ba. Bản khai chờ 2.1 độc lập phiếu 2.0. Màn duyệt viết bằng JavaScript chuẩn, chỉ gọi KttCore, Node dùng riêng cho kiểm với bản giả. Công cụ chuyển DEMO chỉ nhận danh sách giả tích hợp sẵn, không đọc danh mục thật.

Đã kiểm bằng Core giả (CoreGia) và KttCore giả; chưa kiểm Core thật, Linux thực tế hoặc Cloud. CLI SDK chuẩn chưa được tiêm quyền Mask nên từ chối xử lý; adapter DEMO có port nằm ngoài gói. Trần 100 lệnh/lô và trần kỹ thuật JSON 4 MiB được ghi ở README; băm nội bộ chưa có khóa HMAC từ Core.

## Nối ngăn chung NGAN-0 — 15/11/2026

Đã nối ngăn chung NGAN-0 (PR chung #34 đã gộp). Mục này cập nhật các ghi chú chờ mẫu/skip ở các lần bàn giao trước: hai tệp mẫu đã do lead chép, phiên này giữ nguyên, không sửa `_chung/**`. Khai báo RAM lấy từ `KHAI-SDK-2.1.json/ngan_du_lieu`, đổi tên bảng từ `ma` sang `bang` đúng hợp đồng chung; không đổi engine.json 2.0. Không thêm thư viện chạy. Các test an toàn MASK-5 giữ nguyên hành vi và xanh; không gọi Cloud.

**Quy ước SHA-256 LF:** tính trên `read_bytes().replace(b'\r\n', b'\n')`, không bỏ BOM/khoảng trắng hoặc đổi ký tự khác. Đây là băm hiện tại thay cho số băm lịch sử của các tệp cùng tên. Test so mẫu và từ điển dùng cùng quy ước. NGUON.md tự mô tả nên không tự ghi băm chính nó.

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `e_mask/cong-cu/chuyen_danh_muc_demo.py` | `3ffb0fad8b709bde45371aee785b3d5a9d7da8540e328e8a21c83b2c0fd56db3` |
| `e_mask/docs/VIEC.md` | `785ff02e4203c088307c3a086621ea2e38f39da2fbbb570d015eda7564e7375c` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `abae2f86b71dcb1b452f067014e41e1895205994a1168cf4a5806d89e4f74d43` |
| `e_mask/goi/e_mask/KHAI-SDK-2.1.json` | `db2ca7378f08d4d5c9fd60d77d79b403c4c1f9b8ea80a5f26e796c5349306cb5` |
| `e_mask/goi/e_mask/README.md` | `2c5bd3abd44733826a15bba70b307dab7fd6906021cf8d4351d3caee78103683` |
| `e_mask/goi/e_mask/e_mask/chay.py` | `346ff1d95734f7d52c78cac53e209e726b75fdf682ec43f763279f4eab637959` |
| `e_mask/goi/e_mask/e_mask/kho_ngan.py` | `dd7f47f871a8b1bced793855a79a9a98b66a6c11d6559a8112d99f3b39d7f67b` |
| `e_mask/goi/e_mask/e_mask/kho_qua_core.py` | `ead192d13252dab309692c1f7e95ebbf3100930a73a1f2ed9ced051a03c292c3` |
| `e_mask/tests/chay_demo.py` | `edbfe964c6d628435a068ca2965189c617964cd913c69d7b3e8dbc16a06ef58c` |
| `e_mask/tests/test_mask_3b.py` | `96ef2c819123429b6e0e20f9d1a1d97ae48fc73249198843eca8912d9bf98c48` |
| `e_mask/tests/test_mask_4_6.py` | `cc4345889d8d7cc51d95d8c4a44d1ae5997e79fa269c18c9d41c6ed461de77b8` |

Hai mẫu chung được giữ nguyên, kiểm đối chiếu nguồn → bản gói sau chuẩn hóa LF:

| Nguồn | Bản gói | SHA-256 LF của cả hai |
|---|---|---|
| `_chung/mau-ma/ngan.py` | `e_mask/goi/e_mask/e_mask/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `e_mask/goi/e_mask/e_mask/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

Đã kiểm bằng Core giả (CoreGia): cổng thay thế trong tests đạt 2/2 DEMO; CLI SDK chuẩn chặn thiếu nguồn quyền. Pytest 280 passed, 190 subtests passed, 0 skipped; kiểm độc lập đạt. RAM không bền qua khởi động lại, quyền/ngăn thật vẫn chờ Core.

## Sửa an toàn theo kiểm độc lập — 15/11/2026

Mục này cập nhật trạng thái hiện tại; số băm ở bảng nguồn privacy phía trên được làm mới theo bản gói. Không sửa nguồn trong ma-nguon, mẫu chung hoặc hai bản ngan.py/cau_hinh.py trong gói. Chỉ thư viện chuẩn và SDK 2.0.0; không thêm dependency.

- `nguon/privacy/types.py`: dùng bảng Unicode của Python (category Cf) và các variation selector, tạo bộ quét một lần trong RAM. Bỏ ký tự vô hình trước NFC và giữ khoảng ký tự nguyên văn; không ánh xạ được thì từ chối. Không duy trì whitelist Cf thủ công.
- `che_van_ban.py`, `phong_bi.py`: dùng chung ánh xạ, dò bổ sung tên qua tab/xuống dòng; bỏ mọi ký tự vô hình trên đầu ra, kiểm chặn phong bì, giữ đối chiếu tiền/ngày. Mã Junsky đã duyệt giữ nguyên khi khớp tên.
- `kho_qua_core.py`, `kho_ngan.py`, `chay.py`: bí danh tạm riêng mỗi yêu cầu, không nhận tham chiếu chéo, giữ chính thức; gộp cụm chờ và đếm gặp đúng. Lỗi ngăn/port thành câu cố định, bỏ chuỗi ngoại lệ gốc; giữ hủy/ChuaRo/CAS. Chốt không nhận bản che không đạt.
- Ba hiện vật `kho_tam.py`, `cau_hinh_may.py`, `schemas/cau_hinh_may.schema.json` chuyển nguyên nội dung từ gói sang `e_mask/LUU-TRU/mask_truoc_ngan/` theo đúng cấu trúc con. Gói không còn mô-đun/schema này. Test lịch sử nạp qua `tests/ho_tro_luu_tru.py`, không đưa thư mục lưu trữ vào đường chạy engine. SHA LF đối chiếu với blob gốc của cả ba tệp.
- `git mv` bị sandbox chặn Git index ngoài worktree; dùng Move-Item để giữ nguyên tệp. Lead stage rename khi commit. Không commit/push. Kiểm độc lập đã thêm chặn mã đọc biến cấu hình máy và import mô-đun lưu trữ.

Các test hồi quy dùng đúng ví dụ định danh DEMO do lead cung cấp; kiểm Cf toàn bộ bảng Unicode, selector ngoài BMP, NFD/NBSP/tab/xuống dòng, MST/STK, quyền alias và stdout/stderr. Hai yêu cầu độc lập có alias tạm khác nhau là thay đổi có chủ ý theo lệnh sửa an toàn, thay kỳ vọng cũ dùng chung alias. Vector trong ma-nguon giữ nguyên; fixture bổ sung quyền sở hữu rõ ràng cho các ca tái dùng của chính yêu cầu đó.

SHA-256 hiện tại bên dưới tính sau chuẩn hóa CRLF thành LF, không băm chính NGUON.md. Kết quả chạy thật và giờ thực tế ở báo cáo sửa an toàn trong e_mask/docs; đã kiểm bằng Core giả (CoreGia).

<!-- SHA-SUA-AN-TOAN -->

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `.gitignore` | `ce73ac75f2132332709576302ce0e8b848d232780636db3da15bf4deb3dfe275` |
| `e_mask/LUU-TRU/mask_truoc_ngan/cau_hinh_may.py` | `282258c946f3d1dc9562f00a3c3d5aa89113372c670b62a2d43726b57adcb0b2` |
| `e_mask/LUU-TRU/mask_truoc_ngan/kho_tam.py` | `f59171f0094a6093a338a9894a0695f6ce8d2a2d66f4acd1769714c1555714f5` |
| `e_mask/LUU-TRU/mask_truoc_ngan/schemas/cau_hinh_may.schema.json` | `111673c65f54ad9b866e08b4f300871bbc3f6faf2cc2309a060aa3e9a2ae45d1` |
| `e_mask/docs/VIEC.md` | `785ff02e4203c088307c3a086621ea2e38f39da2fbbb570d015eda7564e7375c` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `abae2f86b71dcb1b452f067014e41e1895205994a1168cf4a5806d89e4f74d43` |
| `e_mask/goi/e_mask/README.md` | `2c5bd3abd44733826a15bba70b307dab7fd6906021cf8d4351d3caee78103683` |
| `e_mask/goi/e_mask/e_mask/chay.py` | `346ff1d95734f7d52c78cac53e209e726b75fdf682ec43f763279f4eab637959` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `55cdceed15cd9d0988abf1211f66b3290522860fa36621b8b1e440d15d227104` |
| `e_mask/goi/e_mask/e_mask/kho_ngan.py` | `dd7f47f871a8b1bced793855a79a9a98b66a6c11d6559a8112d99f3b39d7f67b` |
| `e_mask/goi/e_mask/e_mask/kho_qua_core.py` | `ead192d13252dab309692c1f7e95ebbf3100930a73a1f2ed9ced051a03c292c3` |
| `e_mask/goi/e_mask/e_mask/nguon/privacy/types.py` | `7f81a43ed1f61a8553c73da9499c5fab1c0bb69334f27b40eabfc202b9c3b3e1` |
| `e_mask/goi/e_mask/e_mask/phong_bi.py` | `8d1393bba2fbd278fcd22a469b9b76c55acb7c2627109b4998c4af1f45f97661` |
| `e_mask/tests/ho_tro_core_gia.py` | `98319448372a4269b43fdacd8b482febbbf6e4cacc11ca3b8a978906dd871cfe` |
| `e_mask/tests/ho_tro_luu_tru.py` | `54f9c2a6965da00325337e64d828b279646f39bd32dd3730b724a8a1f665d64a` |
| `e_mask/tests/kiem_doc_lap.py` | `8557adb5389495692f34d1d15b162a68968d4a54aa5b2ce53ce896f86b8045ab` |
| `e_mask/tests/test_kho_tam.py` | `dbf436f6312d2399b4be012f041ab53bdd24fea18ee0acb132a1412a9c5a843d` |
| `e_mask/tests/test_mask_0.py` | `700940273d7165f5cdd3e7021c2e5a15097013de22092f213bc8b829304c798c` |
| `e_mask/tests/test_mask_3.py` | `25049167381885f975a068b2c5c891098fa9d2da24733d9bff8ccdc3d3298c80` |
| `e_mask/tests/test_mask_3b.py` | `96ef2c819123429b6e0e20f9d1a1d97ae48fc73249198843eca8912d9bf98c48` |
| `e_mask/tests/test_mask_4_6.py` | `cc4345889d8d7cc51d95d8c4a44d1ae5997e79fa269c18c9d41c6ed461de77b8` |
| `e_mask/tests/test_sua_an_toan.py` | `c85beeb506055e65303ce302546300054792f588e9325f3174b02940d6cb4413` |
| `e_mask/docs/BAO-CAO-SUA-AN-TOAN-MASK-3b-6.md` | `b670eaf9a1199dfaff23dc20045e15219f88cf7f455189872f58347671b3cc7d` |
| `e_mask/docs/KET-QUA-KIEM-SUA-AN-TOAN-MASK-3b-6.txt` | `4b232e449470aeb2b5d91e27d7772a93b105d28e8ae6344d3700c37961c6c24d` |

## Bổ sung MASK-2b — 15/11/2026

Mã viết trong repo, chỉ dùng thư viện chuẩn và SDK 2.0.0; không chép nguồn ngoài hoặc thêm dependency. Đúng hai tệp runtime: thêm `e_mask/ten_nguoi.py`, sửa `e_mask/che_van_ban.py`. Bộ dò dùng lại bốn tài nguyên sạch đã cấp, không thay tệp/băm từ điển. Không sửa mẫu chung, ngăn/cấu hình, Core hoặc nguồn cũ.

Quy tắc mới: bỏ dấu/hoa thường nhưng giữ âm tiết và vị trí, họ + 1–3 âm tiết; danh xưng/tên chính thức tăng tin cậy để che, nghi vấn còn lại chặn phát hành. “và”/ngoặc chức danh không tự cho phép gửi. Cụm thông dụng trùng họ khai rõ tại `_CUM_THONG_DUNG`; không tải từ điển hay dùng dữ liệu thật. Tên dài, che prefix, trùng sau bỏ dấu và bí danh tạm chưa duyệt có ca hồi quy. Giữ bộ dò chữ hoa cũ, thêm lưới tên thường độc lập.

Đã kiểm bằng Core giả (CoreGia): pytest 545 passed, 190 subtests passed, 0 skipped; adapter DEMO 2/2, kiểm độc lập ĐẠT. CLI SDK chuẩn 0/2 do thiếu nguồn quyền. 14 mẫu có sẵn báo nhầm 1/14; 30 câu bổ sung 2/30, bằng bản nền; chi tiết/giới hạn và nguồn mẫu ở báo cáo MASK-2b. Không chứng nhận mọi tên hoặc đủ điều kiện bật Cloud.

Bảng này thay các băm lịch sử cùng tên ở trên cho bản MASK-2b. Quy ước SHA-256: `read_bytes().replace(b'\r\n', b'\n')`, không đổi ký tự khác; không tự băm NGUON.md.

<!-- SHA-MASK-2b -->

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `e_mask/goi/e_mask/e_mask/ten_nguoi.py` | `6b5b0a21fbbc7ce438f82725589391c234febc58fc1d4c239a9c5df075693886` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `766552691ca30d4fca2cde61d1c1b11423216823d5fa136218a757b732bc45d4` |
| `e_mask/tests/test_mask_2b.py` | `150ded0fb5848a62e3d09869343df6d35c8570fe76d7f981bc47c093b003fe56` |
| `e_mask/tests/do_mask_2b.py` | `9ce3d80e2845345ea34548c091d51568fa737f8996a968a7f81e38257870835e` |
| `e_mask/tests/test_mask_2.py` | `f5b012bcefac7196e62318de0afd4d402fc0c3420ba8375e997a0b23c27514bb` |
| `e_mask/tests/test_che_van_ban.py` | `e2023cc28afe67b91744bfff12a9d44e93ad579bee8c742b6b1b6a7ec2420264` |
| `e_mask/docs/VIEC.md` | `c10cc41ba3f2fc3eecf7d99025777e5c3b1d705ea8b49cd394dee6debcf91ed1` |
| `e_mask/goi/e_mask/README.md` | `1d412cbbb27311da170d67e4b0d2dc46fa849d91073044dbbb7373f49e3b8474` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `1f042768b20d89eb831eddadddc45665cab96a130e43de90cf96b04c6784cb29` |
| `e_mask/docs/BAO-CAO-MASK-2b.md` | `523778d62fe4294fda317e576f4fc2e77b55b6085296c7c87bb391a2dc400b6d` |
| `e_mask/docs/KET-QUA-KIEM-MASK-2b.txt` | `221b8669bd261ec15e49085832405beda14fcb91f1b69b4e143b02855c9c6aff` |
| `e_mask/docs/SO-DO-MASK-2b.json` | `94645b2b9baed0f86190eeedb20db0e3a866332ede8629fc115baf8e1c3162fe` |

## Sửa MASK-2b theo kiểm độc lập — 15/11/2026

Mục này thay mô tả hiện hành và các băm lịch sử cùng tên của MASK-2b ở trên. Chỉ sửa hai tệp runtime `e_mask/ten_nguoi.py`, `e_mask/che_van_ban.py`; không thêm thư viện, không sửa nguồn cũ, mẫu chung, ngăn/cấu hình hoặc bốn tệp từ điển đã duyệt. Đã kiểm bằng Core giả (CoreGia).

Nguồn danh sách bổ sung, không dùng dữ liệu hồ sơ thật:

- **Họ:** `_HO_BO_SUNG` lấy nguyên 15 họ từ lệnh giao sửa của Anh/lead ngày 15/11/2026 lúc 09:47: Ưng, Âu, Khúc, Lục, Thân, Ninh, Quan, Ông, Vi, Mẫn, Khổng, Bế, Nông, Lò, Hầu. Đây chỉ là họ, không phải danh sách người. Không suy họ từ từ thường hay từ tên/đệm. `vn_surnames.txt` sạch giữ nguyên; họ bổ sung nằm trong mã, không giả nhận là từ điển nguồn đã thay đổi.
- **Âm tiết tên/đệm:** `_AM_TEN`, `_AM_DEM` tự soạn trong repo theo phạm vi lead cho phép, chỉ gồm từ đơn thường dùng như văn, thị, đức, minh, thanh, hải, an, hoa, long, khoa; không lấy tổ hợp tên cụ thể của hồ sơ/người thật. Không tải bộ tên ngoài hoặc thêm dependency. Danh sách hữu hạn, không chứng nhận đủ mọi tên.
- **Từ ghép:** `_CUM_THONG_DUNG` tự soạn từ cụm 2–3 âm tiết của lệnh giao và thuật ngữ kế toán/hợp đồng/phổ thông. Áp dụng ở mọi vị trí của ứng viên; phân biệt danh xưng có dấu với từ thường và loại danh xưng không dấu khi nằm trong cụm thường. Không miễn cả họ Phan vì có phân bổ.
- **Quy tắc:** ≥8 che, 4–7 con_sot, <4 bỏ qua; mỗi điều chỉnh có mã căn cứ nội bộ. Tên dài/ranh giới hỏng/trùng nhiều tên chính thức/tên Latin bị giới hạn điểm tối đa 7; không lộ cụm gốc trong cảnh báo. Tên Latin có ngữ cảnh được chặn; nếu cả cụm đã che như công ty thì không còn nghi vấn tên để phát hành. Giữ số văn bản dạng số/năm sau số; mã có hậu tố chữ vẫn được kiểm.
- **Test của lead:** 32 ca t9 và 41 câu t10 là literal DEMO được chuyển bằng AST sang `tests/test_mask_2b_rv.py`, không import/thực thi script tham khảo. Hai bản `.py.txt` chuyển nguyên nội dung từ `tests/rv_mask_2b/` sang `LUU-TRU/rv_mask_2b/` ngoài gói. SHA LF từng tệp đã đối chiếu blob HEAD trước chuyển; test xác nhận đủ literal.

Kết quả thật: t9 từ 6/32 lọt xuống 0/32 (24 chặn, 8 che); t10 từ 28 chặn + 1 che thừa xuống 2 chặn, 0 che thừa, tức báo nhầm 29/41 → 2/41 (4,88%), gồm cả ca mập mờ. Còn câu mập mờ lê thị hoa đơn gốc và câu số sổ cái 331 bị lớp nhãn tài khoản cũ chặn. Pytest 717 passed, 190 subtests passed, 0 skipped; DEMO 2/2, kiểm độc lập đạt; CLI SDK chuẩn 0/2 do thiếu quyền. Báo cáo/số đo/lệnh thật ở e_mask/docs; chưa kiểm Core thật/Linux/Cloud. Nợ tên nước ngoài thiếu ngữ cảnh/N.V. An/ngoại lệ từ vựng ghi trong VIEC.

SHA-256 dưới đây tính đúng `read_bytes().replace(b'\r\n', b'\n')`; không tự băm NGUON.md. Nguồn trước sửa là blob HEAD của worktree (không sửa Git index).

| Tệp runtime (từ gốc repo) | SHA-256 LF trước | SHA-256 LF sau |
|---|---|---|
| `e_mask/goi/e_mask/e_mask/ten_nguoi.py` | `6b5b0a21fbbc7ce438f82725589391c234febc58fc1d4c239a9c5df075693886` | `e6bd9bd4c1c5027f23dfc6280d8602425b3380f2281e5456145f889e027423a4` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `766552691ca30d4fca2cde61d1c1b11423216823d5fa136218a757b732bc45d4` | `ce5a3965168768e6a3ec2a5661908a206441925bbce35b084ff9523cbe1186b0` |

<!-- SHA-MASK-2b-RV -->

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `e_mask/goi/e_mask/e_mask/ten_nguoi.py` | `e6bd9bd4c1c5027f23dfc6280d8602425b3380f2281e5456145f889e027423a4` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `ce5a3965168768e6a3ec2a5661908a206441925bbce35b084ff9523cbe1186b0` |
| `e_mask/tests/test_mask_2b_rv.py` | `0a0b2d494fb857fc4880d19692150d5f47359e45383ed94a38b388289f773b48` |
| `e_mask/LUU-TRU/rv_mask_2b/tan_cong_t9.py.txt` | `fbba30698bd4e0586e4a81dbb489b325318672d6ed4162816824f34f6092b9d9` |
| `e_mask/LUU-TRU/rv_mask_2b/bao_nham_t10.py.txt` | `f5481fa3e40c0dca77ac0052ed37054996738f7b11f50503cdd7fee6375da8a1` |
| `e_mask/docs/BAO-CAO-MASK-2b.md` | `8dd734b87caaa734e2f8702d0154d12844346c39f8ca3ee8d3fb9d7e1fa2b377` |
| `e_mask/docs/VIEC.md` | `e1506277ecc9c2352a18c76c9af4b273e9d7ba1b67fd1a4c8fd2682cd9e13f77` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `84dd68b4eb6bc9c32b4c02638157487d70249a17f6b26342882882070afe1af0` |
| `e_mask/docs/KET-QUA-KIEM-MASK-2b.txt` | `95b811a16861db299942da113849625b7cb7eaec4c99cdb5a4052de7388e8672` |
| `e_mask/docs/SO-DO-MASK-2b.json` | `f8929d3e65731da3476c39e27e93808e3dd1e6c44f3e1e28070941ebfc971dfc` |


## Ranh giới Cf và held-out MASK-2b — 15/11/2026

Không thêm từ điển hoặc dependency. Bản dò tên nhận diện ranh giới Cf bằng hình thức âm tiết và họ trong `vn_surnames`; ánh xạ về nguyên văn. Kết quả held-out do lead cung cấp: lọt 4/45, báo nhầm 15/75; nợ CAO vẫn mở, Cloud tắt cứng. Đã kiểm bằng Core giả (CoreGia). SHA-256 sau chuẩn hóa CRLF thành LF, thay cho băm lịch sử cùng tên; không tự băm NGUON.md.

| Tệp | SHA-256 LF |
|---|---|
| `e_mask/goi/e_mask/e_mask/ten_nguoi.py` | `39ce61691967aaf6866013725eaaa9ea21dbb4f83c0d0075ec083ebcc56fdca1` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `b2f96b6e009ae06de5be592dea893963640ba844bf2083ded9f07466476168b7` |
| `e_mask/tests/test_mask_2b.py` | `11a101ec37209cc97ba3a9428f05e079d17e3b0ed0909095aa4cb2f6f2600fa9` |
| `e_mask/docs/BAO-CAO-MASK-2b.md` | `b92ca176efbb9bbf90ec7e51c99b4f692be7bc891aae5533cee6d9cf54e8123a` |
| `e_mask/docs/VIEC.md` | `4278314ab831e5f4093a5dbc2ce9100321bba37c6e76ff0a60a1e2b02bb84d56` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `63455d7dd6a5f3a957521319e0f37f7d424fdcbb6a1a791f7c894c3487d1633b` |

## MASK-2c-1 — edit script và snapshot nội bộ, 15/11/2026

Mã tự viết trong repo, chỉ thư viện chuẩn và SDK 2.0.0; không thêm dependency hoặc nguồn ngoài. Đúng bốn tệp mã chạy theo phiếu. Giữ nguyên `ngan.py`, `cau_hinh.py`, nguồn cũ, manifest/API và schema chung. `types.py` chỉ thêm bộ liệt kê khoảng Cf/selector và kiểm biên dấu tổ hợp, không đổi phép dò hiện có.

`anh_xa_ai.py` ghi ba script bất biến: gốc → bỏ Cf/selector, bản sạch → NFC, gốc → bản che theo đúng khoảng thay thực tế. Chuyển bản dò ↔ bản che bằng hợp thành qua gốc, trả khoảng bao khi phép đổi không song ánh; không dùng chênh chiều dài toàn văn hoặc tìm tên lần đầu. Băm UTF-8 hai đầu, phiên bản map và bảng Unicode được ghim; kiểm lại phủ/ngữ nghĩa/script trước phát hành. Chỉ một khoảng thay alias bao trọn tên mới chứng minh đã che tên.

`ho_so_ai.py` chỉ xử lý RAM và port kho tệp Core có ACL. Snapshot có gốc/bản dò/bản che/map/kế hoạch đoạn, JSON chuẩn và băm bytes; Ngan chỉ lưu chỉ mục băm/tham chiếu, không toàn văn/map. Trần snapshot kỹ thuật 64 MiB, vượt từ chối; không thay trần công khai 500.000 code point. Port chưa có transport thật, adapter DEMO dùng CoreGia trong `tests/ho_tro_ho_so_ai.py`, ngoài gói. Đã kiểm bằng Core giả (CoreGia); chưa kiểm Core/Local thật, Cloud tắt.

Giữ kiểm hiệu năng 500.000 ký tự: bộ liệt kê Cf bỏ qua ASCII như bộ bỏ Cf cũ; nghi vấn số dài chỉ gồm chữ số ASCII/dấu cách và trùng toàn bộ văn bản sau strip được định vị đúng chữ trực tiếp. Kết quả vẫn chặn với cùng khoảng; không miễn detector, không đổi tiền/ngày, giới hạn thời gian hoặc test cũ. Các trường hợp khác giữ matcher hiện có; test đối chiếu với KnownText trên dữ liệu DEMO.

Băm hiện hành sau chuẩn hóa CRLF thành LF; thay băm lịch sử cùng tên ở các mục trước:

| Tệp | SHA-256 LF |
|---|---|
| `e_mask/goi/e_mask/e_mask/anh_xa_ai.py` | `3432016d943c4f2cbc271a04d1f9aa39ec142e352649468dbcf6f9ed5b989a72` |
| `e_mask/goi/e_mask/e_mask/ho_so_ai.py` | `578f204934e51cec4764cd58cd190983869da10351f0c5e55a3e952b08bc16e9` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `c6d2c76477c86af17981dc551494723d1d02fefaa17bd637641b0a4fd71a5610` |
| `e_mask/goi/e_mask/e_mask/nguon/privacy/types.py` | `962dccced2516f246db56ab84be07d3cb3d6fdd4dfcfe43c937c3795aa5a49d4` |

## MASK-B1 — cổng ZIP/XML nội bộ, 15/11/2026

Quyền tái dùng: lệnh giao MASK-B1 của Anh/lead cho phép **CHÉP chọn lọc nội repo**. Nguồn Python Hóa đơn theo `e_hoa_don/goi/e_hoa_don/NGUON.md` (HD-4/HD-6), chưa có căn cứ giấy phép riêng; không gán quyền CD-096 A1 của Node cho Python. DOCX Đối chiếu theo mục DC-2 trong `e_doi_chieu/goi/e_doi_chieu/NGUON.md`, chuyển từ nguồn nội bộ Trích xuất theo phiếu đã cho phép. Trích xuất ghi nguồn nội bộ tại `e_trich_xuat/goi/e_trich_xuat/NGUON.md`. Không suy thành quyền phân phối bên ngoài hoặc tự thêm giấy phép/dependency.

| Đường nguồn từ gốc repo | Symbol thực đọc/chuyển | Đích và thay đổi |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py` | `doc_zip`: callback hủy, đoạn `JSONEncoder.iterencode` đếm byte; `_canh_bao_zip_hong` chỉ đối chiếu | `e_mask/doc_tep.py::ma_hoa_json_noi_bo`: chép có sửa đoạn encoder, trần báo cáo 256 KiB/chuyển tiếp 64 KiB/khuôn 32 KiB. Không chép báo cáo giữ tên entry hoặc tiếp tục khi lỗi |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/hoa_don_xml.py` (**closure thực của wrapper**) | `doc_goi_hoa_don_zip`: khóa NFC/casefold, kiểm symlink, ZIP lồng, hàm lồng `dem_byte`, CRC và hủy | `e_mask/zip_an_toan.py::{_kiem_ten,_kiem_header,_giai_nen,doc_zip}`: chép/chuyển có sửa các kiểm; thay mọi số cũ bằng trần B1; không mang DTO hoặc đường đọc lỗi một phần |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `_kiem_danh_muc`, `_kiem_zip`, `_doc_xml`, `_BoDungCay`, `_quan_he`, `_kieu_noi_dung` | Ba tệp B1: chép có sửa tiền kiểm EOCD/header, DEFLATE bounded/EOF/CRC, ngân sách cây tổng, part/type/graph. Siết whitelist; Expat stdlib phân biệt XML declaration với PI |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/cau_truc.py` | `W`, `W_NS`, `_sai`, `_vuot` (closure import của DOCX) | Chỉ đối chiếu. Namespace và hai lỗi định nghĩa tại chỗ theo Mask; không chép `DanhSo`, `_DocNoiDung`, `_gan_vi_tri`, `_noi_khoi` hoặc reader nghiệp vụ |
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `_BoDungCay`, `_doc_xml`, `_kiem_zip`, nhánh Accept All | Chỉ đối chiếu trần/hủy và giới hạn reader thân. Không chép Accept All, bỏ vùng hoặc adapter tệp của mẫu |

Closure dừng tại các kiểm và hai lỗi/namespace tại chỗ, **đúng ba tệp mã**. Không nạp module engine nguồn; không sửa nguồn mẫu/Core/SDK/ngăn chung. B1 kiểm record bằng `struct`, giải nén bằng `zlib`; không dùng API riêng của `zipfile` hoặc hook cảnh báo toàn cục, không có cảnh báo mang tên entry từ `zipfile`.

**Băm nguồn trước và sau:** đo bytes checkout khi đọc và kiểm lại sau triển khai; nguồn không đổi nên băm trước = sau. Cột LF chỉ thay CRLF bằng LF, không đổi Unicode. LF wrapper/DOCX/Trích xuất khớp P2; closure Hóa đơn được lần và băm bổ sung thực tế.

| Đường nguồn | SHA-256 bytes (trước = sau) | SHA-256 LF (trước = sau) |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py` | `6212ab75f8f1e0cb8cc2103d11ce4a5d4ea08ab213d5191745c3721ecc215149` | `3be2a2156de2ba8f63c5a9679b8c4d344a6d7e5a8d12f838d5d440b2d4b3e733` |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/hoa_don_xml.py` | `fb201bbb723c4c739596dbbbe0270584a8ab2dbc368886428cde7ef0e3fbcab1` | `8b7cb17848a5861b7384aefa31b22d6cc39f28b2e3486a0c4bc938929d397f32` |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `5d261c682d130a7cc5fba80759d9a94512ba773e6d463af5b16a9a58592d476c` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/cau_truc.py` | `1acb9e949370b8f25efda2e9d491469af620226a762068f30d1dd58df5fab7ad` | `ddde14383f97bf5c1fa1a2161aed7db8f3ea1e36004c16350a2db52018c2d333` |
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `165e4da8a5f791aa49ee2f4c2525b2f32e25b17c3cc33eea0facfa01c83a6ef2` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |

**Băm bản gói sau sửa:** ba đích chưa tồn tại trước MASK-B1. Đây là bản chuyển có sửa, không nhận còn nguyên bytes mẫu; băm toàn tệp đích sau sửa, không phải băm phát hành toàn gói.

| Đích từ gốc gói e_mask | Trước MASK-B1 | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|---|
| `e_mask/doc_tep.py` | Chưa có | `9050f061dab051b69fd0ca7d383edf0850aeb74ee7bf560f95da00eef8186e1c` | `9050f061dab051b69fd0ca7d383edf0850aeb74ee7bf560f95da00eef8186e1c` |
| `e_mask/zip_an_toan.py` | Chưa có | `0628d86ff80985b365c0ac7fc1c25583b102254e8892a4de70b508d1f7d7d25e` | `0628d86ff80985b365c0ac7fc1c25583b102254e8892a4de70b508d1f7d7d25e` |
| `e_mask/xml_an_toan.py` | Chưa có | `b44819c30f722ce833329a945e97b6d72540fc2c83eb7c4444599570032d21be` | `b44819c30f722ce833329a945e97b6d72540fc2c83eb7c4444599570032d21be` |

Profile B1 chỉ dùng **nội bộ**: ZIP cổ điển một đĩa, STORED/DEFLATE; không ZIP64, prefix tự chạy, data descriptor, khoảng trống/overlap/đuôi, mã hóa, extra/comment hoặc header ngoài whitelist. Tên part cố định/số thứ tự 1–256; không nhận tên tệp máy. Giữ bytes gốc/local record/payload và offset cho B4, B1 chưa ghi ZIP mới.

XML chỉ UTF-8/UTF-16 và namespace/prefix đã liệt kê; DTD/entity/quan hệ ngoài/PI/comment XML đều từ chối. Part whitelist gồm thân/story Word, styles/numbering/settings/fontTable/webSettings, workbook/worksheet/sharedStrings/styles và core/app/custom properties; graph phải tới mọi part, đúng loại/gốc/quan hệ. Theme, phần mở rộng và các vùng bị cấm ở phiếu §7.2 bị từ chối, kể cả mồ côi. Whitelist node/attribute là cửa đầu vào, **chưa thay reader/map/kiểm ngữ nghĩa B2/B3 hoặc chứng minh đã che**.

Trần thử nghiệm: container vào/ra 1 MiB riêng mỗi chiều; 8 MiB giải nén tổng, 2 MiB/phần, 256 phần, ratio 200:1 kể cả nhỏ; depth 64, 100.000 node tổng, 50 sheet, 20.000 ô; vào 500.000 code point. B1 đếm bảo thủ mọi text/tail và giá trị attribute, cộng shared string ở từng ô dùng, không preview; có thể từ chối sớm hơn reader ngữ nghĩa. Reader sau vẫn kiểm ký tự logic/vùng thực đọc. Helper ra kiểm đồng thời 2.000.000 code point/8 MiB UTF-8 và JSON 256/64/32 KiB; B4/B7/B9 phải gọi khi có writer/phát hành, B1 chưa upload. Unicode hợp lệ: 2 triệu code point tối đa 8.000.000 byte, nhỏ hơn 8 MiB; test riêng cửa đếm byte 8 MiB/+1, không nâng trần ký tự để tạo biên giả.

Dữ liệu việc chỉ RAM, không thêm trạng thái bền hoặc bảng ngăn. Buffer/bảng tạm dọn `finally`; dữ liệu cần giữ ở lát sau dùng Ngan/kho tệp Core đúng mẫu. Lỗi parse/trần chỉ hai mã và câu Việt cố định, không tên/path/nội dung; hủy/mất lease/ChuaRo truyền nguyên. Từng lỗi DEMO kiểm không trả một phần, không ghi đĩa, không mạng hoặc in log. Không thêm dependency/PDF/Office automation. Gói hiện có đã kiểm bằng Core giả (CoreGia); cổng B1 kiểm trực tiếp RAM, **chưa nối năng lực tệp, Core thật, Word/Excel hay Local thật**, Cloud giữ tắt.


## MASK-B2 — reader Word nội bộ, 15/11/2026

Quyền tái dùng: lệnh giao MASK-B2 của Anh/lead cho phép CHÉP chọn lọc nội repo. Theo DC-2 trong `e_doi_chieu/goi/e_doi_chieu/NGUON.md` và TX-1 trong `e_trich_xuat/goi/e_trich_xuat/NGUON.md`: nguồn nội bộ, SDK 2.0.0 và thư viện chuẩn, không bổ sung giấy phép bên thứ ba hoặc suy quyền phân phối ngoài tổ chức. Không sửa hoặc import engine nguồn.

| Đường nguồn từ gốc repo | Symbol chép/chuyển có sửa | Đích và khác biệt |
|---|---|---|
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `doc_bytes`: vòng story/containers notes, kiểm ID/tham chiếu note, main/type/root/relationship; `_quet_chua_chot` làm căn cứ chặn sửa đổi | `doc_word.py::_DocWord.doc`, `xml_word.py::kiem_cay_word`: giữ mọi story/note đã nhận, không bỏ vùng/metadata/Accept All; B1 giữ cổng XML/graph, B2 siết cấu trúc/giá trị |
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `_val`, `_DocNoiDung._chu`, `khoi`, `_bang`: run/ký hiệu/bảng/gridSpan/vMerge | `doc_word.py::{_val,_DocWord._doan,_khoi,_bang}`: giữ mọi ô vật lý và chữ ở ô nối, không ghép qua ô/đoạn/story, không mang cảnh báo bỏ vùng, Accept All, Numbering/DTO của TX |
| B1 trong chính gói e_mask | `_kiem_danh_muc`, `_kiem_ten`, `doc_zip`, `GoiZip`, `PhanZip`, `doc_xml` | Khối MASK-B2 riêng cuối `doc_tep.py`; không sửa hai tệp ZIP/XML B1. Chỉ chiếu byte RAM sau kiểm header/descriptor gốc rồi để B1 kiểm lại payload/EOF/CRC/trần; trả nguyên bytes và offset ZIP gốc |

Closure dừng tại các symbol trên, không chép/import `.cau_truc` hoặc kéo thêm thư viện. Bộ profile/metadata/theme và lexical map là phần mới trong `xml_word.py`, chỉ đi trên cây đã được Expat B1 kiểm, đối chiếu từng giá trị với cây; không dùng regex thay parser. Hai nguồn trước = sau, kiểm lại với `e_mask/docs/SHA-NGUON-MASK-B2-TRUOC.json`. LF chỉ đổi CRLF thành LF:

| Nguồn | SHA-256 bytes trước = sau | SHA-256 LF trước = sau |
|---|---|---|
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `5d261c682d130a7cc5fba80759d9a94512ba773e6d463af5b16a9a58592d476c` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `165e4da8a5f791aa49ee2f4c2525b2f32e25b17c3cc33eea0facfa01c83a6ef2` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |

Băm toàn tệp đích, bản chuyển có sửa. doc_tep trước là checkout B1 có CRLF; hai đích mới chưa có:

| Đích từ gốc repo | SHA bytes trước | SHA LF trước | SHA bytes sau | SHA LF sau |
|---|---|---|---|---|
| `e_mask/goi/e_mask/e_mask/doc_tep.py` | `77e3b72b743e6c239f7b416eb017b8add2ecccd4e8ffdd45f1baeb95f31eb655` | `9050f061dab051b69fd0ca7d383edf0850aeb74ee7bf560f95da00eef8186e1c` | `fb58024cdb07b232a99cbd06c9c9e2e3caed40789f62c895db76d2246c915fdb` | `4aa66b7ca7429dbd59082775b29f2e11dd14e0bbc068a4adda40f9ff75275360` |
| `e_mask/goi/e_mask/e_mask/doc_word.py` | `chưa có` | `chưa có` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` |
| `e_mask/goi/e_mask/e_mask/xml_word.py` | `chưa có` | `chưa có` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` |

Profile: WordprocessingML transitional thân/bảng/run/đầu-chân/notes/chữ ẩn, core/app/custom scalar có kiểu, styles/numbering/settings/fontTable/webSettings và theme chuẩn trong phạm vi đã kiểm. Text metadata/custom property name, tên style/latent style/lvlText/theme/scheme đều có map, bắt buộc qua hai lớp sau này. **Mọi scalar custom**, kể cả số/bool/ngày, cũng có map và vào tổng quét: kiểu hợp lệ chưa chứng minh không chứa mã định danh. Writer sau phải từ chối nếu cần thay alias làm sai kiểu, không tự đổi kiểu property. Style ID chỉ tập builtin hữu hạn, typeface chỉ tập font hằng; giá trị cấu trúc số/hex/ngày/bool/enum phải qua kiểm profile trước coi bất biến. Giá trị chưa phân loại từ chối, không miễn vì không ở w:t.

Kết quả chỉ TaiLieuWord nội bộ, không cờ đã che/chuỗi nối mọi vùng. Từng VungWord có text gốc, SHA UTF-8 riêng, story/đoạn/ô vật lý/note; từng ManhWord có node path/run/style/cờ ẩn/attribute và khoảng Unicode code point nửa mở trong vùng. Mỗi code point có khoảng byte trong part XML giải nén NGUYÊN GỐC, không phải byte trong DEFLATE; ZIP gốc/local record/payload nén/offset vẫn giữ riêng. Entity/CR/CRLF/CDATA/UTF-8/BOM/UTF-16/surrogate pair có map; giữ nguyên NFD/Cf. Tab/br/note có manh ky_hieu; note đọc một lần mỗi part/note và giữ đủ tham chiếu lặp. Không ghép qua đoạn/ô/story.

Tổng text logic gồm metadata/style/theme và ký hiệu đếm khi dựng vùng, không quá 500.000. B1 vẫn đếm bảo thủ cả text/tail/attribute kỹ thuật nên có thể từ chối sớm hơn tổng logic; test biên ghi đúng tổng B1 và tổng logic riêng. Word thêm trần 20.000 ô vật lý kể cả trống/ô nối; các trần ZIP/XML khác giữ nguyên B1. Dữ liệu việc chỉ RAM, bảng/buffer tạm dọn finally; không thêm bảng/trạng thái Ngan. Snapshot ở lát B7/B9 qua Core ACL, chỉ mục qua Ngan mẫu hiện có.

Comments/revision/author markup, field/textbox/content control/extension, nhúng/media/macro/customXml/binary, part mồ côi/đánh tráo type/root/relationship đều từ chối cả gói. Không Accept All, không cảnh báo thay quét. ZIP bit 1–2 chỉ DEFLATE; bit 3 có descriptor 12/16 byte đúng CRC/size central và local header tương thích. le_cuoi bao cả descriptor; payload chỉ dài so_byte_nen. Hủy/ChuaRo truyền nguyên; không I/O/mạng/log/output một phần.

Giữ đúng ba tệp runtime. Nợ tên dài hơn 256 được chặn tại wrapper `_kiem_ten`/`doc_zip` trong doc_tep, không sửa tệp ZIP thứ tư; hàm độc lập trong zip_an_toan giữ nguyên B1. Khối ZIP chung dùng được XLSX tối thiểu; reader/theme/calcChain Excel thuộc B3, B2 không sửa doc_excel/xml_excel. Chưa writer/upload/năng lực tệp hoặc MASK-2b + Local trên tệp. Đã kiểm bằng Core giả (CoreGia) gói văn bản; reader B2 kiểm trực tiếp RAM, chưa Core/Office/Local thật hoặc Linux thực tế. Cloud tắt.
## MASK-B3 — reader Excel nội bộ, 15/11/2026

**Quyền tái dùng:** lệnh giao MASK-B3 của Anh/lead cho phép CHÉP chọn lọc `xlsx_toi_thieu.py` trong repo. `e_hoa_don/goi/e_hoa_don/NGUON.md` HD-7 ghi writer Python stdlib tự viết; bằng chứng CD-096 A1 ở đó dành cho nguồn Node nội bộ chỉ tham chiếu, không tự suy thành giấy phép Python hoặc quyền phân phối ngoài. Không thêm giấy phép/dependency. Mã mới B3 chỉ SDK 2.0.0 và thư viện chuẩn Python.

| Đường nguồn từ gốc repo | Symbol đọc/chép | Đích và khác biệt |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py` | `chu_xml`: escape literal ST_Xstring một lượt, control XML và CR | Chép chọn lọc vào `e_mask/xml_excel.py::chu_xml`; chỉ nhận chuỗi, từ chối surrogate lẻ, không ép số hoặc cắt độ dài. Helper escape text cho B4/B6, chưa dùng để ghi tệp trong B3. Không chép `tao_xlsx`, writer inline string hoặc bộ nén |
| `./e_mask/ma-nguon/nguon/privacy/excel.py` | `decode_string`, `encode_string`, `_read_cells`, `_read_metadata`, `_validate_relationships`, `_audit`; đối chiếu MASK-7 §3 | Chỉ tham chiếu để xác định vùng, ST_Xstring, shared index và rủi ro. Reader/map mới không normalize gốc về NFC; map đủ surrogate pair, entity, CR và từng run/attribute/byte. Chặn formula/link/sheet ẩn/phần chưa phân loại, không giữ bằng disclosures có tên |
| `./e_mask/ma-nguon/nguon/privacy/excel_values.py` | `clean_text`, `safe_sheet_name`, `_cell_xml`, `build_values_workbook` | Chỉ đọc tĩnh, không nạp runtime. Không dùng đường dựng workbook mới/cắt 32767/đổi tên sheet làm fallback giữ định dạng |
| `e_mask/goi/e_mask/e_mask/{doc_tep,zip_an_toan,xml_an_toan}.py` | Cổng B1, ngân sách XML, kiểm danh mục/header/DEFLATE EOF/CRC, content types/relationship graph | Dùng trực tiếp nội bộ cùng engine. Khối B3 riêng ở cuối `doc_tep.py` kiểm cờ nén 1–2 và descriptor bit 3; không sửa 37 định nghĩa/câu lệnh AST B1 trước đó, không thay parser Word hoặc sửa nguồn mẫu |

**Nguồn trước và sau:** băm lại bytes thực sau triển khai, cả ba nguồn không đổi nên trước = sau. LF chỉ thay CRLF bằng LF, không chuẩn hóa Unicode.

| Đường nguồn | SHA-256 bytes trước = sau | SHA-256 LF trước = sau |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py` | `06e185c00dc5762a4393a7223d47e234d6af39a3424dcf43263ae60933fbc304` | `ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d` |
| `./e_mask/ma-nguon/nguon/privacy/excel.py` | `464456eae2a71488ef57954af2265c1bba0656254a466e3b19d90200c7e873a5` | `b837f86a9accaea662357b485fb0d835a6deef4ba4e9f8ccffb0bb9a1243fdc7` |
| `./e_mask/ma-nguon/nguon/privacy/excel_values.py` | `12d3f14b74cba21de40ade2b5d707e8a604ea0ff72b00927c58d68c0f83c43aa` | `6bbcb1c0e19923d13923ca935970199626aca668ec3f23d903ef3e512c22e901` |

**Đích trước sửa:** `doc_excel.py` và `xml_excel.py` chưa có. `doc_tep.py` trước B3 có SHA bytes `77e3b72b743e6c239f7b416eb017b8add2ecccd4e8ffdd45f1baeb95f31eb655`, SHA LF `9050f061dab051b69fd0ca7d383edf0850aeb74ee7bf560f95da00eef8186e1c`. Băm B1 lịch sử ở trên giữ nguyên; bảng dưới là toàn tệp sau B3, không là băm phát hành cả gói.

| Đích từ gốc gói e_mask | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|
| `e_mask/doc_tep.py` | `8490326022023e2980ac666e1c5f7f917b33e4e94a61f15500a29c86c8c24526` | `24175ad56221e4d3b3403416f1c8e7dd1d9550ad6325f292f176df2967f8ad7e` |
| `e_mask/doc_excel.py` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` |
| `e_mask/xml_excel.py` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` |

Profile B3: XLSX transitional, đường part cố định/số thứ tự B1, đủ graph/types/root/namespace/node/attribute và ngữ nghĩa được hỗ trợ. Thêm `xl/theme/theme1.xml` với grammar màu/font/style có miền giá trị cố định; `xl/calcChain.xml` chỉ được rỗng. CalcChain có tham chiếu công thức luôn bị từ chối theo chính sách formula/cache, kể cả khi phần đó do Office lưu. Không nhận mọi OOXML hoặc mọi theme/font/numFmt thực tế.

Font name, tên style mặc định và mã định dạng chỉ được giữ trong allowlist đã kiểm; numFmt tùy ý có tên, codeName hoặc attribute chưa phân loại bị chặn. Properties core/app/custom: chuỗi thành vùng có map, số/boolean/ngày kiểm kiểu và giữ nguyên; custom tên/giá trị có map inverse, HeadingPairs chỉ nhãn Worksheets với số sheet đúng, TitlesOfParts phải khớp tên sheet theo thứ tự và không được tự đổi. Sheet name có vùng riêng `duoc_sua=False`: B6/B7 phải chạy cả hai lớp trên vùng đó và gọi `kiem_thay_the`; yêu cầu thay khác gốc thì từ chối cả tệp.

ST_Xstring chỉ giải mã tại shared/inline/rich text và tên sheet; text metadata theo kiểu chuỗi XML của properties. Không normalize NFD/Cf hoặc chuẩn hóa CR gốc tùy ý: map phản ánh đúng chuẩn hóa XML literal CR/CRLF thành LF, character reference và ST CR vẫn giữ CR. Chuỗi literal `_x005F_x0041_` chỉ thành literal `_x0041_`, surrogate pair thành một code point có span bao hai escape, surrogate lẻ bị chặn. Map UTF-8/UTF-16, BOM, attribute normalization và khoảng byte hai chiều; node tự đóng không có neo chèn text giả trong tail. CDATA trong part cần map bị từ chối: chưa có profile patch chứng minh cho kiểu escape khác và miền lexical không liền nhau, không giả khoảng bao delimiter là text an toàn để thay.

Mỗi shared string có vùng gốc kể cả chưa được dùng; mỗi ô dùng có vùng tham chiếu riêng và danh sách đầy đủ `(số sheet, địa chỉ ô)`. Ghép rich runs trong cùng đơn vị, không nối hai ô. Đếm cả shared dùng lặp và mọi metadata, không preview. Trần Excel 32767 UTF-16 code unit được kiểm, không cắt. Giữ raw value/type/style và XML ô số/boolean/serial ngày; ghi riêng style gốc và style hiệu lực từ ô/hàng/cột, giữ epoch, merge và bytes các part.

ZIP Office: B1 giải nén bounded/CRC/EOF thật sau kiểm descriptor CRC/size khớp central directory; hỗ trợ cờ nén 0x0006, bit UTF-8 và bit 3, descriptor cổ điển 12/16 bytes. Các cờ khác/extra/comment/overlap/gap/ZIP64/nhúng/part lạ vẫn chặn. `PhanZip.le_cuoi` kết thúc payload, `PhanZipExcel.le_cuoi_ban_ghi` bao descriptor; B4 phải dùng đúng hai mốc khi chép record nguyên trạng. Không sửa hoặc nén lại bytes trong B3.

Chỉ RAM, không bảng ngăn mới; giữ nguyên Ngan theo mẫu và không tạo tệp tạm. Bảng làm việc dọn `finally`. Chưa phát hành năng lực tệp, chưa nối writer hoặc hai lớp/Local cho tệp. Gói văn bản đã kiểm bằng Core giả (CoreGia); reader B3 kiểm trực tiếp RAM, chưa Excel/Core/Local thật. Cloud giữ tắt, không import engine khác, Core, nguồn cũ hoặc dependency mới. B2/B3 để lead gộp khối riêng, B3 không sửa mã Word.

## Gộp MASK-B2 + MASK-B3 — SHA hiện hành, 15/11/2026

Giữ nguyên mọi dòng provenance/băm lịch sử B1/B2/B3 ở trên. Bảng này thay băm hiện hành của các tệp cùng tên sau gộp; LF chỉ đổi CRLF thành LF, không chuẩn hóa Unicode. Không băm chính NGUON.md để tránh tự tham chiếu.

Giữ hai khối reader và cổng ZIP, không sửa `doc_word.py`, `xml_word.py`, `doc_excel.py`, `xml_excel.py`. Cổng chung B2 cũng nhận XLSX cờ 0x0006/descriptor có kiểm; cổng B3 gọi wrapper `_kiem_ten` chung tối đa 256. Quy ước offset mỗi reader giữ nguyên. Test gộp tự soạn theo fixture DEMO B1/B3 trong RAM, kiểm cả hai cổng; không thêm nguồn ngoài/dependency.

| Tệp từ gốc repo (bản hợp nhất) | SHA-256 LF hiện hành |
|---|---|
| `e_mask/cong-cu/THU-MASK-LOCAL-AI-THAT.cmd` | `7e41c1bf14a0a1a045ce4462ed55fa259fe795fa8f83cdd8676ddcef1382b723` |
| `e_mask/cong-cu/mask_2c_4_ung_vien_demo.json` | `b3569b357132a7f7e0a7202b6e3d3c0b5fec2228c6ebd09604e7d05092485dd8` |
| `e_mask/cong-cu/thu_mask_local_ai_that.py` | `27a2f63e05519ddb8ab227c107a829b3b615f8cd5ad423a341d5d70b9939ee05` |
| `e_mask/docs/BAO-CAO-MASK-2c-4.md` | `b4c41ca97fc61b1d8d0faa6e8aa24ed24d5b2ff86e11fe77769851a5a29deed4` |
| `e_mask/docs/BAO-CAO-MASK-B3.md` | `80ede4fbb44b9412d5bde46b28f4c41f89efb2b658caab088ca56c48d6f8ac46` |
| `e_mask/docs/KET-QUA-KIEM-MASK-2c-4.txt` | `4e55ac28e7b986cab7d88dc4bcbd1ab693b81431ccd81e6e9d3fa639776154c0` |
| `e_mask/docs/KET-QUA-KIEM-MASK-B3.txt` | `924dceabea41bba01ef31050eeda1cb8682427ce4b6c1207fe31198667ec3d8d` |
| `e_mask/docs/VIEC.md` | `5d85d30fd1e058ed74cd68ac0f7d2295ab60caaa7b5e52131a484f96b00b6506` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `482684dcb0d8a95f61d2e2b1fa7806f307f47d6763fc8c23aeb3189fd895b26b` |
| `e_mask/goi/e_mask/e_mask/doc_excel.py` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` |
| `e_mask/goi/e_mask/e_mask/doc_tep.py` | `7169ad765f8566479e9b88f4907be2d37e70fbaded112f2ced6dd75e18567646` |
| `e_mask/goi/e_mask/e_mask/doc_word.py` | `ca1dc23fcd0422a2b56458de1fe9872567ededcbdcc3344fb229e3c977be7c77` |
| `e_mask/goi/e_mask/e_mask/xml_excel.py` | `1105d3622ef84cee5a90c127987ca00d2683312998d68057cd67e80cf9b220b5` |
| `e_mask/goi/e_mask/e_mask/xml_word.py` | `b98963305b11a5ac216552ec091d7dbd3323c179e21b13db4e55adfba3116d08` |
| `e_mask/tests/ho_tro_mask_b3.py` | `c64ff8e1e27f8a8b34512adf81a79f41de69a91b6e5460c8fed513c179ed7f51` |
| `e_mask/tests/test_gop_mask_b2_b3.py` | `58976f10be12beb8d7a4b8001e7856d49017cd3784c2230888c30c9733c95d28` |
| `e_mask/tests/test_mask_2c_4.py` | `aaeb93c259f68e943d4ae212791e40c15909072f6d57afc1faef3cc214992510` |
| `e_mask/tests/test_mask_b3.py` | `4f5dc6876b1ffe359c13a8aa3cc5aa938245b153fd2c923ec95d93fad3e9cd68` |

## MASK-B4 — writer ZIP và patch XML nội bộ, 15/11/2026

**Quyền tái dùng:** Anh/lead cho phép CHÉP chọn lọc các mẫu nội repo trong lệnh MASK-B4. Hóa đơn HD-7 ghi `xlsx_toi_thieu.py` là writer Python stdlib nội bộ tự viết; HD-4/HD-6 là nguồn ZIP Python của B1. Đối chiếu DC-2 ghi nguồn DOCX nội bộ chuyển có sửa từ Trích xuất. Không suy quyền CD-096 A1 của Node sang Python hoặc quyền phân phối ngoài tổ chức. Không import engine nguồn, sửa nguồn mẫu, thêm dependency hoặc đổi SDK/API.

| Đường nguồn từ gốc repo | Symbol chép/chuyển có sửa | Đích và khác biệt |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py` | `_BoDem.write`, `chu_xml`: RAM, kiểm byte trước ghi, escape literal ST_Xstring/control/CR | `ghi_zip.py::_BoDem.ghi`, `va_xml.py::_ma_hoa`: tính cả central directory/EOCD, đếm trước từng mảnh encode; ST chỉ ô Excel, attribute giữ tab/LF/CR, CDATA đổi miền ngay trong span. Không chép `tao_xlsx`, `ten_cot`, writer inline string hoặc dựng workbook mới |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `_kiem_danh_muc`, `_kiem_zip`: EOCD, bounds/metadata, CRC/ratio/tên/loại tệp | `zip_an_toan.py::kiem_ban_ghi` tiếp tục kiểm của B1 và đối chiếu bytes record thực trước chép. Không dùng ZipInfo làm nguồn tin cậy hoặc mang policy bỏ qua vùng của reader mẫu |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py` → `hoa_don_xml.py` | Closure đã ghi B1: `doc_goi_hoa_don_zip`, `dem_byte`, NFC/casefold, CRC, symlink/ZIP lồng/hủy | Tái dùng các kiểm B1 qua `doc_word`/`doc_excel`, `_kiem_danh_muc`, `_kiem_header`, `_giai_nen`; không kéo wrapper/DTO, báo cáo tên raw hoặc policy tiếp tục khi entry lỗi. Runtime không dùng zipfile nên không có UserWarning mang tên entry |
| `e_mask/goi/e_mask/e_mask/{doc_tep,doc_word,xml_word,doc_excel,xml_excel}.py` | Reader/map B1/B2/B3 và hai kiểu mốc cuối descriptor | Dùng trực tiếp trong cùng engine, không sửa. Writer dựng lại reader từ bytes trước và sau, đối chiếu map/băm/metadata thay vì tin cây mutable của caller; `kiem_ban_ghi` phân biệt cuối payload với cuối local record |

Nguồn trước = sau, đã đối chiếu snapshot `e_mask/docs/SHA-NGUON-MASK-B4-TRUOC.json`. LF chỉ thay CRLF bằng LF, không chuẩn hóa Unicode. Closure dừng tại các kiểm/mẫu trên; không nạp `ma-nguon`, COM, PDF, engine khác hoặc mã Core.

| Đường nguồn | SHA-256 bytes trước = sau | SHA-256 LF trước = sau |
|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/xlsx_toi_thieu.py` | `06e185c00dc5762a4393a7223d47e234d6af39a3424dcf43263ae60933fbc304` | `ad6a6c8e89d73e5e994c4f21066c7ee76640b261eaf253dc82a69cf1337fa46d` |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py` | `6212ab75f8f1e0cb8cc2103d11ce4a5d4ea08ab213d5191745c3721ecc215149` | `3be2a2156de2ba8f63c5a9679b8c4d344a6d7e5a8d12f838d5d440b2d4b3e733` |
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/hoa_don_xml.py` | `fb201bbb723c4c739596dbbbe0270584a8ab2dbc368886428cde7ef0e3fbcab1` | `8b7cb17848a5861b7384aefa31b22d6cc39f28b2e3486a0c4bc938929d397f32` |
| `e_doi_chieu/goi/e_doi_chieu/e_doi_chieu/doc_docx.py` | `5d261c682d130a7cc5fba80759d9a94512ba773e6d463af5b16a9a58592d476c` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |

Đích trước/sau B4, băm toàn tệp chuyển có sửa, không là băm phát hành cả gói. Hai tệp mới chưa có trước; phần ZIP B1 trước B4 có SHA bytes `0b7112dc63c02c2b33893de1efa8f442090ed12ae1672aa72a1ccd3225644d8b`, LF `0628d86ff80985b365c0ac7fc1c25583b102254e8892a4de70b508d1f7d7d25e`. Băm hiện hành dưới đây thay băm ZIP cũ, không sửa provenance lịch sử.

| Đích từ gốc gói | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|
| `e_mask/ghi_zip.py` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` |
| `e_mask/va_xml.py` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` |
| `e_mask/zip_an_toan.py` | `d55a1555fd3fb05aed323b3fd9146d26e773c19bfcd57ac32d836905b53880db` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` |

API nội bộ: `lap_kich_ban(tai_lieu, ((vi_vung, dau_unicode, cuoi_unicode, chu_moi), ...), kiem_huy=...)` → `KichBanXML`; `ghi_goi(tai_lieu, kich_ban, kiem_huy=...)` → bytes. Chỉ nhận `TaiLieuWord`/`ExcelDaDoc` qua B1+B2/B3, không nhận raw/path/dict thay reader. Script phiên bản 1 ghim SHA bytes ZIP, SHA UTF-8 vùng, SHA part và SHA từng khoảng byte XML gốc. Writer đọc lại bytes/map, kiểm chồng Unicode/byte và mọi băm/CRC/size/offset; không dùng script như chứng cứ hai lớp hoặc quyền phát hành.

Một thay thế qua nhiều run/miền lexical ghi chữ mới ở mảnh đầu, xóa text đã chọn ở các mảnh sau; giữ toàn bộ markup/namespace/format ngoài khoảng. Không sửa tab/br/note như text. CDATA đóng/mở ngay trong span để escape đúng CR và chuỗi đóng CDATA. Không normalize NFD/Cf, không sửa byte ngoài span hoặc serialize XML. ST chỉ shared/inline/rich text Excel, metadata giữ nghĩa XML thường; surrogate lẻ, injection, ST ghép mã ngoài ý định ở biên bị chặn qua kiểm lại nghĩa mọi vùng.

Part bất biến chép nguyên local header/payload nén/descriptor; central chỉ đổi offset nếu cần. Part sửa giữ method/flags, DOS time/attribute/thứ tự/names; cập nhật CRC và hai size trong central, local đầy đủ hoặc descriptor đúng kiểu 12/16 byte. Mức DEFLATE theo cờ normal/max/fast/superfast, chỉ một lần nén, không đổi method hoặc thử lại để tránh ratio. Không edit/no-op thì toàn ZIP bằng đúng gốc. Extra/comment/cờ/descriptor chưa kiểm đều từ chối cả gói.

Giới hạn được kiểm trước/từng lần encode, thêm buffer, nén/ghi và đóng ZIP, gồm cả central+EOCD: output 1 MiB; giải nén tổng 8 MiB/phần 2 MiB; ratio 200. Các trần phần/node/depth/ô/sheet và tính hợp lệ XML/graph tiếp tục qua lại B1/readers. Nội dung dự kiến đếm cả shared dùng lặp, kiểm 2 triệu code point/8 MiB UTF-8 và 32767 UTF-16/ô; không thêm báo cáo JSON nên giữ helper 256/64/32 KiB của B1 nguyên trạng. **Giới hạn hiện hành:** B1/B2/B3 đọc lại output vẫn đếm bảo thủ 500.000 ký tự cả text/tail/attribute kỹ thuật, có thể từ chối sớm hơn trần ra 2 triệu; không nới reader bằng cờ hoặc monkey-patch. Điều chỉnh profile đọc chiều ra cần lát reader riêng trước khi cam kết hỗ trợ phần khuếch đại đó.

Không ghi Ngan/bền máy hoặc tạo tệp tạm; chỉ RAM và dọn buffer trong `finally`. Hủy/mất lease/ChuaRo truyền nguyên, không output dở, mạng/log/tên gốc. Chưa công bố năng lực tệp; B7/B9 mới nối hai lớp/quyền/chốt/upload. Đã kiểm bằng Core giả (CoreGia) gói văn bản hiện có; writer tệp kiểm trực tiếp RAM/fixture Office DEMO, **chưa Word/Excel/Core/Local thật hoặc Linux thực tế**. Cloud vẫn tắt.

## MASK-S22 — 15/11/2026, SDK 2.2.0

Mục này là hiện trạng mới nhất; các mục SDK 2.0/2.1 ở trên là lịch sử. Đã kiểm bằng Core giả (CoreGia). Runtime chỉ thư viện chuẩn và `kho_tri_thuc_sdk==2.2.0`, không thêm dependency chạy. Wheel từ `docs/goi-gui-engine/sdk-2.2.0/`, SHA-256 bytes `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`, khớp SHA256SUMS.txt. Venv mới `.venv`, SDK cài bằng `--no-index --no-deps`; môi trường cũ được giữ tại `.venv-truoc-mask-s22`. Bộ kiểm offline sao các tệp phân phối đã cài từ venv cũ theo đúng phiên bản ở `e_mask/tests/requirements.lock`: pytest 9.1.1, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0, iniconfig 2.3.0, colorama 0.4.6. Không cần mạng hoặc phụ thuộc khác của SDK dành cho module.

Không chép nguồn engine khác hoặc sửa SDK/mẫu chung. Bốn runtime được điều chỉnh từ chính HEAD trước lát; adapter công cụ ngoài gói đổi sang cấu hình/ngăn CoreGia của Hỏi AI AI-11/AI-12. Theo chỉ dẫn Lead riêng Mask, giữ cổng bí danh RAM và các ca hành vi hiện tại, không tự nối kho này với ngăn SDK; không có đường giải mã mới. Schema cấu hình rỗng theo hiện trạng; prompt/model Local do module/quy trình cấp qua port tin cậy, không là cấu hình engine. Không có đệm phụ thuộc cấu hình cần làm mới. Bản khai 2.1 và bộ đọc cấu hình tạm chuyển nguyên byte ra LUU-TRU; test bộ đọc cũ chỉ nạp hiện vật ngoài gói. Hai test so băm mẫu và phép so mẫu trong ca B3 đã bỏ, các kiểm hành vi còn giữ.

Băm LF dưới đây chuẩn hóa CRLF → LF, không đổi nội dung khác. Nguồn trước là Git HEAD của worktree bắt đầu lát, đích sau là tệp hiện tại. Tệp mới ghi “mới”.

| Tệp từ thư mục e_mask | SHA-256 trước (LF) | SHA-256 sau (LF) |
|---|---|---|
| `goi/e_mask/e_mask/chay.py` | `af5bfbdaf8bb2ea90aad75c84375b16be65a4ab2207b4e4c0ca675f26198fdb0` | `3afb29b2364a5dca5d35f6dc5a1ca12a447badf52f77a281aecb1f6bfbadc5ff` |
| `goi/e_mask/e_mask/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` | `a2304ef100f2650227d06f5ec0b64ea4026626de967b8d256d87e5a05f180f59` |
| `goi/e_mask/e_mask/kho_ngan.py` | `dd7f47f871a8b1bced793855a79a9a98b66a6c11d6559a8112d99f3b39d7f67b` | `e8ca52d6a8e81a512e11c4ef093e9c60a9a741f967dd19c92d5f1580825e4cd5` |
| `goi/e_mask/e_mask/kho_qua_core.py` | `ead192d13252dab309692c1f7e95ebbf3100930a73a1f2ed9ced051a03c292c3` | `eab5abe60566e0874a1f989cacf6813d84ab5c75de364a2b214e484054e9c24f` |
| `cong-cu/thu_mask_local_ai_that.py` | `27a2f63e05519ddb8ab227c107a829b3b615f8cd5ad423a341d5d70b9939ee05` | `a8e091d14e1c9992cfcf02d885ce977caf1231b166ba054346c1c33d29139eb2` |
| `goi/e_mask/engine.json` | `9edc5cdb2becd61e3ae880a59157691f1e9a0c2564b013d67c08c90bce5d9c82` | `cdf368cd4fa86a0f64271f33303d2717a131a7985046f66cee54e13f159b54c2` |
| `goi/e_mask/cau_hinh.schema.json` | `mới` | `3804ad4a504016a6a80a752c51d7ab05a3f5289b8bf7ac329b4512c570150175` |
| `goi/e_mask/requirements.lock` | `mới` | `2042fa331b34afc8df48dcfa2d46909276abd557f828865360618b07b64de5a9` |

Hiện vật được bảo toàn (SHA bytes trước = sau; SHA LF kiểm được ở mọi checkout):

| Nguồn trước trong gói | Đích từ thư mục e_mask | SHA bytes | SHA LF |
|---|---|---|---|
| `KHAI-SDK-2.1.json` | `LUU-TRU/sdk_truoc_2_2/KHAI-SDK-2.1.json` | `c9d215451c1c1d9f3857803a2526681daf6820f2a8a33ed9cdcb7029c1e70958` | `db2ca7378f08d4d5c9fd60d77d79b403c4c1f9b8ea80a5f26e796c5349306cb5` |
| `e_mask/cau_hinh.py` | `LUU-TRU/sdk_truoc_2_2/cau_hinh.py` | `fc36c496f3f7717b3f05512c21ef5dea84f34d3929cba3d2a8d5acefe453acbf` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

CLI chuẩn chưa có cửa cấp quyền/mã yêu cầu tin cậy cho hai ví dụ Mask; không đổi quyền hoặc thêm chế độ DEMO runtime để báo đạt. Cần Core và kết quả kiểm cuối ghi trong `e_mask/docs/BAO-CAO-MASK-S22.md`; màn duyệt chỉ giữ kiểm với KttCore giả, chưa nối ngăn Core mới.

Nguồn tham chiếu đã thay trên main trước MASK-S22 (không phải thay đổi do lát này):

| Nguồn | Commit đã gộp | SHA bytes hiện hành | SHA LF hiện hành |
|---|---|---|---|
| `e_hoa_don/goi/e_hoa_don/e_hoa_don/zip.py` | `55f0f761fed03460a0039cd791da0684303ede88` | `0d9abdf12d0a5767ab2f46b445f4baeda8e7e6e0ca264f971eec11ca6aa99567` | `5b60d342be6f9e109c75df7b266e779a0aa389c0937288f7e7ed77e992685e52` |

Giữ nguyên băm nguồn B1/B4 lịch sử và hiện vật `SHA-NGUON-MASK-B4-TRUOC.json`; test so với bằng chứng chuyển nguồn `SHA-NGUON-MASK-S22-DA-GOP.json` cho đúng tệp đã đổi trên main, các nguồn khác vẫn kiểm nguyên trạng. Mã B1/B4 đã chép không đổi.

Băm bản checkout MASK-B4 hiện tại, mã LF không đổi; bytes khác do checkout Windows dùng CRLF:

| Tệp trong gói Python | SHA bytes checkout | SHA LF |
|---|---|---|
| `ghi_zip.py` | `c98b6d8ad273ca9d6946c0362446f292cf40e8b871b01a3d4aa5054a7f44a470` | `f5dcebe3fe3eb81690929c18426fca20b947b977608584c57535b7bad6a5199c` |
| `va_xml.py` | `6b826f350c567b04587bd4f6e227af136037a28400fabd38a131fb37e7b48f17` | `b683b4d154919f37cc9708f7ee77b9a75731a32398a6570626d65e7fa373eb15` |
| `zip_an_toan.py` | `d55a1555fd3fb05aed323b3fd9146d26e773c19bfcd57ac32d836905b53880db` | `7d1b6b180f1a862dcff60d3c4ac6c526e132d93fa65f50394bb0f48f5898ba9e` |

## MASK-R2 — adapter ngăn bí mật, 15/11/2026

Viết tiếp mã nội bộ được phép tái dùng của dự án, không chép nguồn ngoài hoặc thêm dependency. Bốn runtime theo bảng P4; giữ các khối RAM lịch sử cho hồi quy, chặn chúng với NganEngine. Phần mới chỉ gọi SDK 2.2.0 từ wheel đã đối chiếu SHA phát hành; không import Core/engine khác. Không thay nguồn cũ hay các bằng chứng SHA lịch sử.

| Tệp | SHA-256 bytes hiện tại | SHA-256 LF hiện tại |
|---|---|---|
| `e_mask/kho_ngan.py` | `5c418ce07372449ec3c7a7948a4e3c1887e1cdb202671c8dd2d517d076a72583` | `83c6cce6a586ae2901f3e5a40161e917999d8eeb8951b501d580e3db6b262fde` |
| `e_mask/kho_dinh_danh.py` | `23f7a23450d80bfc11c004f2db210c14601b105be7374b2396b5109646bf821b` | `fd8633450de5ae85484d78d74a8583b3efd5078f19a27221f14326975b16ecb9` |
| `e_mask/kho_qua_core.py` | `01b0004bd18c5680b77dbc2c5d2369993f78a2a27a81bfacd859ab4401fa2299` | `1b7f9023d4e73b5ac45df98988ef2bea4085db1532c2a7361e9d0f799159129d` |
| `e_mask/khoi_tao_ngan.py` | `c23071dcf0b924f56ad794484b2338a71db9074cb670ce85d2c5aa28f20f3f91` | `4fcc71ef714b867eac854ada233d38fc2b22c29e39d1baedbe44131563569bad` |

## MASK-R5 — tiếp lát từ 23:50 ngày 15/11/2026

Chỉ sửa tiếp nguồn nội bộ đã có, không chép mã ngoài/thêm dependency. Ba runtime của R5 giữ kho R4; công cụ CoreGia ngoài gói chuyển fixture snapshot sang RAM, catalogue DEMO khai trước chuỗi độc lập gold/Local. SDK 2.2.0 từ wheel repo đã kiểm SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`, jsonschema/pytest đã có trong venv. Không sửa e_hoi_ai/Core/SDK/schema chung/nguồn cũ, không commit/push.

Các bản snapshot fixture và công cụ trước đổi được giữ nguyên ở `e_mask/LUU-TRU/mask_2c_snapshot_core/`, chỉ tham chiếu lịch sử; không nằm trong gói chạy. Metadata ho_so tương thích AI-9 chỉ là ram-… không có tệp, không mang map/gốc. Cần phối hợp AI-9: bỏ yêu cầu snapshot Core (AI-13).

| Tệp sửa | SHA-256 bytes | SHA-256 LF |
|---|---|---|
| `e_mask/goi/e_mask/e_mask/chuan_bi_ai.py` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` | `f09adcb15b45882572ce6355203c94b256cf913808b98f2e5c7b7d79d8d8f8d5` |
| `e_mask/goi/e_mask/e_mask/hau_kiem_ai.py` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` | `051f4eb324345cfe8a60b6146e0a26886ffe77348b877f28f2b75a19f10a4c46` |
| `e_mask/goi/e_mask/e_mask/phong_bi.py` | `f64f540e124da384bcbb166c5c68817fe15b67d1b693b8f75722f71cc826576e` | `f64f540e124da384bcbb166c5c68817fe15b67d1b693b8f75722f71cc826576e` |
| `e_mask/cong-cu/thu_mask_local_ai_that.py` | `4071dfeee80ac208c3c059b88885aa65e366ecc8810504d9bc8e11b3d4866c23` | `20453f2d4bbe77b592ac8f1df0ba698a648266c328b0e3d4dcbb8536208ec192` |

## MASK-R6b — sửa rà bảo mật R6, 16/11/2026

Viết tiếp bốn runtime nội bộ đã có; automaton trie/failure-link tự viết bằng thư viện chuẩn Python (collections.deque), không chép mã ngoài/thêm dependency. SDK 2.2.0 cài offline từ wheel repo; SHA-256 khớp 0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984. Không sửa nguồn cũ/Core/e_hoi_ai/API v1 hoặc lưu map ngoài RAM.

Chốt giới hạn thử nghiệm 1.000 alias, 10.000 chuỗi kể cả khóa và 200.000 nút bảng dò để chặn phình RAM lúc dựng biến thể. Tập alias được phép lấy từ bản che cuối bất biến sẵn có trong AnhXaAI; không mở cổng lưu trữ mới. Mọi tệp gói được kiểm kê theo bytes LF thực tế, trừ chính tệp kiểm kê. Kết quả kiểm bằng CoreGia và số đo tại VIEC.md; không là bằng chứng Core/Local/Linux thật.

| Tệp | SHA-256 LF |
|---|---|
| `e_mask/mo_che_ram.py` | `3894db53a087f2faf2244cf360f548c20c721744f15b45bfc982c1d336314799` |
| `e_mask/che_van_ban.py` | `fb20d043b46cddea2080b50904f88533c0990b7cf21cc434be8089beb72ead81` |
| `e_mask/kho_anh_xa_ram.py` | `9aec91add2c4ef86d287947fee53bf89eddbb226d7d0b4c68a1c9a0988192ae6` |
| `e_mask/phong_bi.py` | `83ccbdaba8d10a68b247068a9ce7fa72d6962e415ce46595538697b302541625` |

## MASK-B6c — hiệu năng Excel, 16/11/2026

Sửa tiếp hai runtime nội bộ đã được phép tái dùng; không chép mã ngoài hoặc thêm dependency. Profiler xác nhận đường quyền R4 theo callback, detector tên/kiểm số lặp và reader/map ZIP/XML là điểm nóng. Giữ detector/R2/R3/R4 và gate B1/B3/B4, không sửa nguồn cũ/Core/e_hoi_ai hoặc tệp B8. `_map_excel` tự viết bằng Expat thư viện chuẩn, chỉ lập map byte trên worksheet UTF-8 đơn giản đã qua gate; tag/attribute/leaf đối chiếu cây B1 độc lập, số nút và offset nguyên như map B3. UTF-16/entity/CR/LF/tab/CDATA/encoding khác đi nguyên `xml_excel.map_xml`; 32 oracle test so toàn map cho Unicode/rich run/encoding/fallback. Không nới profile/parser an toàn.

Cache reader khóa theo toàn bytes, tối đa hai bản riêng trong primitive; bản trả độc lập cây/map/ZIP, dọn trong finally. ST không có `_x` giữ nguyên ChuXML đã được parser kiểm; map alias bất biến dùng lại theo identity, không gộp nguyên văn khác nhau. SDK 2.2.0 cài offline từ wheel repo, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp bản phát hành. Không có nguồn/dependency mạng mới.

| Tệp / symbol sửa | SHA-256 LF trước (HEAD) | SHA-256 LF sau |
|---|---|---|
| `e_mask/tep_excel.py` — `_bao_ve, _BuocExcel, _kiem_so_bat_bien, _gop_alias, _luu_ram, che_excel` | `b22d1e60bacd13b7f10874b30d8d6d0b9685c88697e4c02fe27dfe5437758972` | `9eee85619ed5e03edc6e1873c8b65e1a289138a6c7ca376fc1fbfaef3e4e7c3c` |
| `e_mask/doc_excel.py` — `_map_excel, _DocExcel.map/vung_moi, _sao_ban_doc, doc_excel, _doc_excel` | `09d3700c527583e3a2191b9833a078ddd9c28c81982618208c6a5df58cecb382` | `230fa8bacd6152c98baa48d0aa8e39e5e8c0b2c5d076d2b655ebaf3e3cb71e42` |


## MASK-B6c lượt 2 — 16/11/2026, tương thích B7

Chỉ sửa `_sao_ban_doc` trong `e_mask/doc_excel.py` nội bộ đã được phép tái dùng. Không chép nguồn ngoài/thêm dependency, không sửa B7/B8/Core/SDK/engine.json. SDK 2.2.0 đã có trong venv, wheel repo khớp SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`.

Nguyên nhân: `ban_ghi.phan` nguồn là header-only (du_lieu rỗng), còn `zip.phan` có bytes giải nén. Bản sao cache trước đây tráo hai giá trị này, khiến `va_xml.doc_lai_nguon` từ chối khi B7 đọc lại ngoài cache với mã `MASK_TEP_CHUA_HO_TRO`. Sao riêng `replace(b.phan)` giữ đúng giá trị và cô lập vỏ dataclass, không đổi gate so sánh. Cache chỉ tồn tại trong primitive của `_BuocExcel`, dọn trong finally; B7 dùng primitive mới sau đổi quyền sở hữu/scope, không tái dùng cache trước.

| Tệp / symbol | SHA-256 bytes trước (blob HEAD) | SHA-256 LF trước | SHA-256 bytes sau | SHA-256 LF sau |
|---|---|---|---|---|
| `e_mask/doc_excel.py` / `_sao_ban_doc` | `230fa8bacd6152c98baa48d0aa8e39e5e8c0b2c5d076d2b655ebaf3e3cb71e42` | `230fa8bacd6152c98baa48d0aa8e39e5e8c0b2c5d076d2b655ebaf3e3cb71e42` | `4f246d0979791dfaf055bf84acd5b16d820845a2e83c295dca14b280961e9c26` | `4f246d0979791dfaf055bf84acd5b16d820845a2e83c295dca14b280961e9c26` |

Đã kiểm bằng Core giả (CoreGia); chưa Core/Office/Local/Linux thật. Cache header-only và bản đọc mới có cùng giá trị, writer vẫn chặn header giả; cache/handle dọn giữa chuẩn bị và hậu kiểm. Không có nơi lưu map mới. Kiểm kê tính bytes thật (không normalize LF), phiên bản bằng manifest 1.5.0. Kết quả và số đo thật tại VIEC.md.

## MASK-B9b — kiểm cuối trước phát hành, 16/11/2026

Chỉ sửa hai runtime nội bộ đã được phép tái dùng, không chép nguồn ngoài hoặc thêm dependency. `MoTepSDK._mo` kiểm sau tiêu thụ RAM nhưng trước ExitStack bàn giao; `CongHauKiemTepSDK.__exit__/_kiem_cuoi` giữ cửa cách ly qua xác minh cuối sau khi R4 nhường handle. Ngoại lệ đi vào cửa Core để hủy, không dùng close thoát thành công sau lỗi kiểm. API v1/engine.json giữ nguyên; ChuaRo tại chốt/bàn giao vẫn kết thúc, không lưu hoặc phục hồi map.

| Tệp / symbol | SHA-256 LF trước (HEAD) | SHA-256 LF sau |
|---|---|---|
| `e_mask/kho_dinh_danh.py` / `MoTepSDK._mo` | `a2190eb979714282022146df514d9c4585030755f6ec4a778d0e43af728c7921` | `11ab939a6c3feb5a59b80c332731c13ad609a36bf7e1de42ccc54e5688dfe0ae` |
| `e_mask/kho_qua_core.py` / `CongHauKiemTepSDK.__exit__, _kiem_cuoi` | `c3e08b11d81d0557aa06eee5fa50383cd7bf2c9b0def9b98f7fe936fa9167ed3` | `fc6501e0c1d33b30ea3866e092d8d332269187cc758fa5242528791f075a14b2` |

Adapter `tests/ho_tro_mask_b7.py` ngoài gói sửa đúng hợp đồng cách ly/commit/hủy. `tests/test_mask_b9b.py` chỉ DEMO; chèn sau R4, trước kiểm cuối và thoát cửa, không thay gate. SDK 2.2.0 cài offline từ wheel repo, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp phát hành. Kiểm kê bytes/SHA trên byte LF mọi tệp gói trừ chính kiểm kê, phiên bản theo manifest 1.6.0. Đã kiểm bằng Core giả (CoreGia), chưa Core/Office/Local/Linux thật. Không sửa Core/e_hoi_ai hoặc công cụ B10.


## MASK-B11 lượt 1 — 16/11/2026, giảm chặn nhầm trong lớp 1 (lịch sử)

Viết tiếp hai runtime nội bộ `tep_word.py`, `tep_excel.py`; các symbol mới `_MARKER_KY_THUAT`, `_TONG_HOP`, `_canh_bao_chu_chua_dat` và chốt `leaked_known` được tự viết bằng thư viện chuẩn `re`, `bisect`, dùng nguyên detector/kiểm số/tiền-ngày nội bộ. Không chép nguồn ngoài/thêm dependency, không sửa mã nguồn cũ/Core/SDK/e_hoi_ai/API v1. Quyền nguồn nội bộ giữ nguyên các mục trước. Manifest giữ 1.6.0; map/bytes không ra khỏi RAM. Bộ development mới chỉ dùng DEMO tự dựng, không nhập công cụ/recipe held-out B10. Chưa đạt phát hành toàn chuỗi vì biểu thức hậu kiểm B7 ngoài closure đang chờ duyệt; không coi kết quả lớp 1 là chứng cứ Local.

SHA trước lấy từ HEAD ban đầu của worktree, SHA sau từ bytes gói; LF là chuẩn hóa CRLF thành LF, không đổi các bộ gold. Không ghi băm hay nội dung của định danh vào bảng nguồn này.

| Tệp | Mốc | Bytes | SHA-256 bytes | SHA-256 LF |
|---|---|---:|---|---|
| `tep_word.py` | trước | 17635 | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` | `8d6be7b0b3fed771338ce0875b2f34cccfb6d1b00d2dce481f23d5c2014a9ce8` |
| `tep_word.py` | sau | 19977 | `b9ff69d747c277d1a3cc5f6b49e20db3635f781a6c48bdf5357e5cf90764898a` | `b9ff69d747c277d1a3cc5f6b49e20db3635f781a6c48bdf5357e5cf90764898a` |
| `tep_excel.py` | trước | 28020 | `9eee85619ed5e03edc6e1873c8b65e1a289138a6c7ca376fc1fbfaef3e4e7c3c` | `9eee85619ed5e03edc6e1873c8b65e1a289138a6c7ca376fc1fbfaef3e4e7c3c` |
| `tep_excel.py` | sau | 28145 | `069b83acd72c9e807290eefc6364b7335d480c436265f86a7f7dc12c20521982` | `069b83acd72c9e807290eefc6364b7335d480c436265f86a7f7dc12c20521982` |

## MASK-B11 lượt 2 — 16/11/2026, biểu thức hậu kiểm được lead duyệt

Áp đúng `.venv/b11-hau-kiem-de-nghi.patch` của lượt 1 vào duy nhất biểu thức trong `hau_kiem_tep.py::_kiem_cuoi`. Dùng bộ lọc `_canh_bao_chu_chua_dat` nội bộ đã có của Word/Excel; không thêm biểu thức nhận diện hoặc nới bộ lọc. Giữ `du`, kiểm nhãn/số/ngày, Local, metadata và vòng đời RAM. Hai runtime lớp 1 giữ nguyên bytes lượt 1. Không chép nguồn ngoài, không thêm dependency, API v1/manifest 1.6.0 không đổi. SDK 2.2.0 trong venv, wheel repo khớp SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`.

| Tệp / symbol | Mốc | Bytes | SHA-256 bytes = SHA-256 LF |
|---|---|---:|---|
| `e_mask/hau_kiem_tep.py::_kiem_cuoi` | trước (HEAD, LF) | 13350 | `57d3ad2495486da0cac22c2523207a958c8269c7ae3784eeb9f06720c2483ab2` |
| `e_mask/hau_kiem_tep.py::_kiem_cuoi` | sau (diff đã duyệt, LF) | 13402 | `497d592d4bd593b33ba8c177f67617f43d613bbdc536c0333b0d0a0c64044ac9` |

Fixture ngoài gói `tests/demo_mask_r3.json` được khôi phục từ bytes blob Git, SHA-256 `b200f74a29547965c637487ee0c6ded78cb6174028b5ce09236e06f5798d5181`; chỉ EOL, nội dung không đổi. Test hậu kiểm mới cô lập writer/lần kiểm map trước cửa để detector thật chạy trên ca độc hại; không thay detector hoặc bộ lọc. Test phát hành hai lớp và các bộ B5/B6/B6b/B8 vẫn chạy nguyên runtime qua CoreGia. Không đổi held-out/gold/công cụ B10, MASK-2c, Core hoặc e_hoi_ai. Kiểm kê dùng bytes thật mọi tệp gói trừ chính nó, LF, phiên bản lấy từ engine.json. Kết quả thật ghi VIEC.md; đã kiểm bằng Core giả (CoreGia), chưa Core/Office/Local/Linux thật, Cloud tắt.


## MASK-B11 lượt 3 — 16/11/2026, bịt hai ngoại lệ lọt bản rõ

Chỉ sửa `tep_word.py::_MARKER_KY_THUAT`, `_TONG_HOP`, `_canh_bao_chu_chua_dat` và thêm `_duoi_tong_hop_hop_le`. Regex lấy đủ đuôi đến hết đơn vị (biên CR/LF, chấm phẩy hoặc | như trước); marker chỉ miễn khi không có chữ cái khác. Đuôi tổng hợp chỉ cho chữ nằm trọn trong tiền/ngày đã được `che_van_ban._cac_tien_ngay` hiện có nhận diện; chữ tự do khác giữ nguyên cảnh báo. Không thêm tên, mã tệp hoặc câu từ held-out vào runtime; không nới ngoại lệ khác. Excel/hậu kiểm B7 dùng chung hàm nên không cần sửa `tep_excel.py` hoặc `hau_kiem_tep.py` ở lượt này.

Tự viết tiếp nguồn nội bộ, chỉ thư viện chuẩn, không nguồn ngoài/dependency. API v1, SDK 2.2.0, manifest 1.6.0, nguồn/quyền, detector chung, nhãn, kiểm số/tiền/ngày và vòng đời RAM giữ nguyên. Test development dùng các chuỗi phản ví dụ DEMO lead giao, không sửa gold/held-out hoặc fixture R3 đã khôi phục LF. Đã kiểm bằng Core giả (CoreGia), Local giả; chưa Core/Office/Local/Linux thật. PR: chờ lead mở.

| Tệp | Mốc | Bytes | SHA-256 bytes = SHA-256 LF |
|---|---|---:|---|
| `e_mask/tep_word.py` | trước lượt 3 (lượt 2) | 19977 | `b9ff69d747c277d1a3cc5f6b49e20db3635f781a6c48bdf5357e5cf90764898a` |
| `e_mask/tep_word.py` | sau lượt 3 | 20684 | `7ecfef3d145d9d4fe1eea76ca2db4056832c6ed300b3c030d3009e4cc6e901ab` |

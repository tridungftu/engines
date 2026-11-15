# TX-4b — E6 theo giá trị và dẫn chứng trên bộ DEMO chuẩn

15/11/2026 · PR: **chờ lead mở** · Ước tính phiếu TX-4: **4 giờ công**.

**Kết luận: phép đo đạt trên 2/2 ca, 74/74 mã khớp giá trị và bản vàng;
74/74 giá trị mới có dẫn chứng hợp lệ. E6 nghiệm thu chưa kiểm vì bộ DEMO
và bản vàng còn chờ lead duyệt.** CLI SDK chuẩn vẫn vướng C-TX-04.

Tiêu chí trong tài liệu này thay thế tiêu chí byte câu hỏi/bảng/phản hồi của
TX-4 trước đó theo `_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` §2.
Không làm lại luồng nhiều lượt; luồng mới vẫn một lượt đủ 37 mã.
Artifact chẩn đoán TX-4 cũ được giữ làm lịch sử, không dùng chấm theo tiêu chí mới.

## Tiêu chí và chuẩn hóa cố định trước khi đo

- **Bắt buộc trùng byte:** bộ E1 đủ 10 tiêu đề/370 ô/37 mã đúng thứ tự,
  tham số pipeline và toàn văn đọc DOCX. Giữ codec UTF-8 JSON của TX-2:
  `ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")`, không NaN.
  So bytes trực tiếp, không dựa vào hash để kết luận bằng nhau.
- **Bắt buộc từng mã:** lấy `gia_tri` cuối luồng cũ và `gia_tri` sau hậu kiểm
  TX-3 của luồng mới; chỉ dùng `str.strip()` loại khoảng trắng đầu/cuối.
  Không NFC, gộp khoảng trắng bên trong, đổi chữ hoa/thường, số, tiền hoặc ngày.
  `1.000.000 VND` khác `1000000 VND`; `2026-10-30` khác `30/10/2026`.
- Adapter cũ biểu diễn vắng mặt bằng `null` cho đúng ba dấu: `None`, chuỗi
  rỗng `""`, thông báo pipeline `"Không tìm thấy trong HĐ"`. Đây là ánh xạ
  giao thức thiếu dữ liệu; `"Không quy định"`, `"Không áp dụng"` vẫn là giá trị,
  không quy về null. Chuỗi chỉ có khoảng trắng không được tự quy về null.
- Giá trị mới khác null phải có dẫn chứng: danh sách không rỗng, **mọi câu**
  khớp nguyên văn tại offset Unicode `[bat_dau:ket_thuc]`, số nguyên không
  nhận bool, không vượt văn bản; dẫn chứng phải hỗ trợ trọn token giá trị.
  Không tin cờ AI. So giá trị sau hậu kiểm, không lấy `nguyen_van`/`phan_hoi_ai`
  thay cho giá trị đã được TX-3 giữ lại hoặc chuyển null.
- Báo cáo từng mã có `khớp / khác / cũ có-mới null / cũ null-mới có`, giá trị
  hai bên, lý do, tình trạng dẫn chứng và đối chiếu riêng cả hai bên với vàng.
  Giá trị hai luồng cùng sai vàng vẫn không đạt. Mã thiếu/trùng/đảo đều bị chặn.
- Câu hỏi, toàn bảng và phản hồi thô vẫn có offset byte đầu, độ dài, SHA-256
  trong `tham_khao_khong_cham`; sai khác của chúng không quyết định đạt.

## Bộ nguồn DEMO và bản vàng độc lập

[Manifest](../tham-chieu/e6/chap-nhan.json) phiên bản **2** ghim SHA-256 từng
DOCX, băng AI, tham số module và bản vàng; `chap_nhan_lead: "chờ lead"`.
Mỗi ca có bốn tệp, đường tương đối không symlink/đi ra ngoài thư mục nguồn:

| Ca | Nội dung | Module | Số giá trị vàng |
|---|---|---|---:|
| DEMO-thuong | Hợp đồng thi công nhà kho hư cấu, số DEMO-XD-001, giá 1.100.000 VND | DEMO-crm | 37 |
| DEMO-track-changes | Hợp đồng DEMO-XD-002, giá mới 2.200.000 VND; một cặp xóa/chèn giá cũ/mới | DEMO-m3 | 37 |

Hợp đồng ghi nhãn DEMO, mọi tổ chức/địa điểm/số liệu là hư cấu. Ngày dùng ISO;
giá trị tiền nguyên văn luôn có VND. TT-21 được **ghi trực tiếp 10%**, không
suy ra theo công thức chưa duyệt. Bản Track Changes cập nhật cả bảo lãnh
tạm ứng và thực hiện hợp đồng để nhất quán với giá mới. Sau Accept All có
đúng **2** thay đổi được nhận, câu giá cũ không còn trong văn bản.

`tests/tao_demo_e6.py` chứa bảng tác giả tự soạn 37 giá trị và câu hợp đồng;
bản vàng được viết từ bảng này trước phép đo, **không lấy đầu ra engine**.
Mỗi `*.vang.json` có `gia_tri` và `can_cu` để lead so với chính DOCX.
Băng `*.ai.json` cố định cho hai giao thức nhưng cùng câu trả lời nghiệp vụ:
nguồn cũ 9 lượt nhóm, nguồn mới 1 phản hồi 37 mã với offset tác giả tính từ
văn bản dự kiến. Không có AI thật hoặc sinh đáp án trong lúc chạy E6.

Bộ này đủ vị trí/giá trị nên nguồn cũ không cần lượt dò/rà lại; wrapper vẫn
giữ thuật toán dò/nhóm/rà lại nguyên trạng, regression kỹ thuật riêng có
chạy các nhánh đó. Công cụ soạn chỉ tái lập nguồn; từ chối ghi đè tệp tồn
tại khác bytes, kể cả bản vàng/manifest đã duyệt. E6 không gọi công cụ soạn.
Mọi sai khác phải được ghi nhận; không sửa vàng theo kết quả.

Nguồn XLSX gốc không đổi:
`05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd`.
Nội dung E1:
`6b8190a73e73ced8784fb22e3339a42d72785826ae15b1a499955facb4d65812`.
Băm snapshot/phần byte và nguồn cũ sau CRLF→LF có trong artifact kết quả.

## Cách chạy và kết quả thật

Dùng `.venv/Scripts/python -B`; Linux dùng `.venv/bin/python -B`.

```text
python -B e_trich_xuat/tests/kiem_e6.py
python -B e_trich_xuat/tests/kiem_e6.py --manifest e_trich_xuat/tham-chieu/e6/chap-nhan.json
```

[Artifact kết quả đầy đủ](TX-4b-ket-qua.json) ghi băm manifest/nguồn và đủ
74 dòng kết quả từng mã. **đã kiểm bằng Core giả (CoreGia)**, NganBoNho có
cấu hình; hậu kiểm TX-3 được đăng ký trong phiếu RAM kiểm thử, không sửa gói.

| Ca | E1/tham số/văn bản trùng byte | Cũ = mới = vàng | Dẫn chứng mới hợp lệ | Câu hỏi cũ / mới |
|---|---|---:|---:|---:|
| Thường | Có / Có / Có | 37/37 | 37/37 | 9 / 1 |
| Track Changes | Có / Có / Có | 37/37 | 37/37 | 9 / 1 |

Không có mã khác/cũ có-mới null/cũ null-mới có ở bộ chuẩn; regression test
kiểm đủ bốn trạng thái và trường hợp hai bên cùng sai vàng. Câu hỏi/bảng/
phản hồi thô đều khác byte ở cả hai ca và chỉ được ghi tham khảo.

CLI E6 **exit 2**, `ket_qua_do="dat"`, `trang_thai="chua_kiem"`, lý do bộ
nguồn chờ lead duyệt. Không tự đổi dấu duyệt. Sau review, lead dùng
`chap_nhan_lead="đã duyệt"` và `bien_ban_lead` có tham chiếu biên bản/PR;
đó chỉ là dấu quy trình, không phải cơ chế xác thực chữ ký/quyền Core.
Mã thoát: **0** phép đo đạt và đã duyệt; **1** sai tiêu chí/runtime chưa
hoàn tất (kể cả đang chờ lead); **2** chờ duyệt/thiếu nguồn/băng/khuôn;
**3** sai SHA-256; **4** lỗi kiểm bất ngờ. `--chan-doan` luôn exit 2.

## Kiểm chung và giới hạn

Windows, Python **3.13.14**, `.venv --system-site-packages`; SDK **2.0.0**
cài offline `--no-index --no-deps`, wheel SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`; pytest **9.1.1** có sẵn. `PYTHONUTF8=1`,
`PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

| Lệnh qua Python venv -B | Kết quả thật |
|---|---|
| `-m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/3 ĐẠT, exit 1**; bước chuẩn bị `CHUA_CAU_HINH`, CLI SDK thiếu ngăn, giữ C-TX-04 |
| `-m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp` | **412 passed in 16.26s, 0 skipped, exit 0** |
| `e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0** |
| `e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **5/5 ĐẠT, exit 0** |
| `e_trich_xuat/tests/kiem_e6.py` | **74/74 giá trị và dẫn chứng đạt; exit 2, chờ lead** |

Test bao gồm strip/NFC/khoảng trắng trong chuỗi/số-tiền-ngày không được
đổi; thiếu/sai offset/bool/vượt biên/câu không hỗ trợ giá trị; mã thiếu,
trùng, đảo; sai một byte E1/tham số/văn bản; vàng sai dù đã cập nhật hash;
nguồn thiếu/sai hash, băng AI thiếu/dư; hai module và dữ liệu không bị ghi
đè. Có kiểm E6 không ghi nguồn và soạn lại DOCX trong RAM trùng bytes.

**Chưa kiểm bố cục bằng PNG:** đã gọi renderer của skill documents nhưng
lệnh dừng ở `ModuleNotFoundError: No module named 'pdf2image'`. Không tải
thêm dependency/mạng để sửa môi trường. Đã kiểm ZIP/XML/quan hệ styles,
Accept All và toàn văn hai reader; chưa thay thế cho kiểm thị giác trong
Word/renderer. Lead cần review trực quan cùng giá trị vàng trước duyệt.

Linux/Core thật/ACL/TTL/vòng đời tệp, T3/N1/model thật chưa kiểm. **0 Cloud,
0 mạng/AI thật**, không sửa `goi/**`, nguồn cũ/Core/SDK hoặc ghim XLSX.
CHANGELOG cho lát này đặt ở `docs/CHANGELOG.md` vì phạm vi cấm sửa `goi/**`.
Không commit/push, không chuyển bộ mặc định/lưu trữ hoặc mở luồng nhiều lượt.

Thời gian thực tế 15/11/2026 (UTC+07): bắt đầu **12:36** theo lead;
kết thúc **12:52:14**, **0.27 giờ**. Phiếu TX-4 **4 giờ công ước tính**,
không có dự toán TX-4b riêng. Giữ C-TX-01/02/04/A-TX-01; không phát sinh
API cần Core mới. Phần đăng ký năng lực là TX-3b song song, ngoài lát này.
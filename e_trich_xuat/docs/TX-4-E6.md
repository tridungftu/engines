# TX-4 — công cụ E6 và biên bản sai khác byte

15/11/2026 · PR: **chờ lead mở** · Ước tính phiếu: **4 giờ công**.

**Kết luận: Chưa đạt điều kiện bàn giao E6. E6 nghiệm thu chưa kiểm vì thiếu
fixture/bản vàng DEMO được lead chấp nhận; chẩn đoán kỹ thuật đã thấy khác
byte câu hỏi, bảng và phản hồi.** Không chuyển bộ mặc định sang module/lưu trữ.
Đây không phải phép đo AI thật, T3 hoặc N1.

## Nguồn đã xác minh

Đọc duy nhất XLSX tham chiếu trong worktree, không sửa tệp hoặc ghim nguồn.
SHA-256 bytes thật khớp `tham-chieu/NGUON.md` và băm trong nguồn cũ:

| Đối tượng | SHA-256 |
|---|---|
| XLSX thực | `05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd` |
| Nội dung E1 (`ma_bam_noi_dung`) | `6b8190a73e73ced8784fb22e3339a42d72785826ae15b1a499955facb4d65812` |
| Snapshot JSON DEMO-crm dựng từ E1 để kiểm cơ chế | `36ede31d53aab2af694e3856f84dc0851c1d51d4a2e2ece9a212a6475b3ff67a` |

Snapshot cuối bảng là dữ liệu kiểm cơ chế, **không phải snapshot module đã
được nghiệm thu**. Snapshot chứa metadata, toàn bộ dòng/quy tắc và hai băm
nguồn. Bộ module thật phải được cấp độc lập trong fixture, không lấy snapshot
này để thay đầu vào thiếu/sai.

E1 SDK 2.0.0 đọc bytes đã xác minh: **37 mã đúng thứ tự, 10 tiêu đề và 370 ô**.
Đã chuyển kiểu bool/int của E1 ngược về biểu diễn ô rồi so nguyên văn với
sheet đọc bằng bộ đọc SDK; không dùng khả năng strip/NFC của E1 để miễn sai
khác. Đồng thời đối chiếu dòng và tham số với parser nguồn cũ. `MAC_DINH` chỉ
kiểm danh sách/thứ tự mã; không dùng để tạo XLSX hoặc làm dữ liệu thay thế.

## Công cụ và ranh giới phép so

Chạy bằng `.venv/Scripts/python -B` trên Windows; Linux dùng `.venv/bin/python -B`:

```text
e_trich_xuat/tests/kiem_e6.py
e_trich_xuat/tests/kiem_e6.py --manifest e_trich_xuat/tham-chieu/e6/chap-nhan.json
e_trich_xuat/tests/kiem_e6.py --chan-doan
```

Không có manifest được chấp nhận trong worktree lúc bàn giao. Lệnh mặc định
thực tế **exit 2**, `trang_thai=chua_kiem`, “Thiếu nguồn đối chiếu E6.”
`--chan-doan` dùng hai DEMO kỹ thuật/rỗng-null cố định và **luôn exit 2**, kể
cả nếu sau này các byte trùng. Nó không tạo bản vàng hoặc nhận chứng nhận E6.

Các mã thoát: **0** chỉ khi đủ ca được chấp nhận và tất cả byte trùng; **1**
có sai khác/đường module không hoàn tất; **2** thiếu fixture/duyệt/băng AI;
**3** nguồn không khớp băm (“Nguồn đối chiếu không khớp mã kiểm tra.”);
**4** công cụ gặp lỗi kiểm bất ngờ, thông điệp chung an toàn. Trường hợp nguồn
thiếu/sai không biến thành kết quả runtime XONG. Lỗi runtime giữ nguyên
`SAI_BAM_BO_THAM_SO`/`BO_THAM_SO_KHONG_HOP_LE`, không fallback XD.

Wrapper `tests/doi_chieu_cu_e6.py` chỉ dùng trong kiểm thử. Nó đọc AST của mã
cũ cố định trong worktree, không import Core/kênh socket/client AI. Giữ thân
hàm dựng nhóm/dò/rà lại, prompt DTO, kiểm tra/logic và toàn bộ dòng bảng.
Các seam: đọc DOCX XML qua BytesIO và Accept All theo namespace như wrapper
`ma-nguon/docx.py`; AI là hàng đợi trả lời cố định; bỏ ghi cấu trúc/xuất tệp
cũ và tự tìm đáp án. Không sửa thuật toán nguồn hoặc đường runtime mới.
Mã nguồn tham chiếu có SHA-256 sau CRLF→LF trong artifact để tái lập Linux.

Đường module đi thật qua **CoreGia + NganBoNho đã có cấu hình**:
DOCX → chuẩn bị → AI giả cố định → lõi hậu kiểm TX-3 (đăng ký trong RAM test).
Hậu kiểm/xuất vẫn chưa đăng ký runtime, chờ duyệt TX-3. Metadata module,
loại, phiên bản, hash snapshot/nội dung được kiểm riêng và không miễn sai
khác nội dung.

Sáu artifact cố định trước khi đo:

| Khóa | Nội dung so |
|---|---|
| `bo_10_cot` | Tiêu đề và mọi ô theo đúng thứ tự E1 |
| `tham_so` | Toàn bộ tham số pipeline sau parser, giữ thứ tự |
| `van_ban` | UTF-8 nguyên văn đầu vào câu hỏi sau đọc DOCX |
| `cau_hoi` | Mọi DTO câu hỏi theo thứ tự gọi: prompt/tài liệu/danh sách trường; khuôn nếu có |
| `bang` | Toàn bộ trường của mọi dòng bảng, không chỉ giá trị/37 mã |
| `phan_hoi` | Mọi phản hồi AI giả ở seam tương ứng, giữ thứ tự gọi và payload |

Vật liệu JSON dùng codec đã định từ TX-2: UTF-8, `ensure_ascii=False`,
`sort_keys=True`, `separators=(",", ":")`, không NaN. Chỉ sắp khóa object;
không sắp dòng/mã/mảng. Chuỗi và bytes bản vàng so đúng bytes, không parse
rồi serialize lại. Không strip/NFC/bỏ cột/đổi nhãn/round hoặc loại sai khác
sau khi thấy kết quả. Các artifact không chứa thời gian; không có thêm
ngoại lệ thời gian nào. DTO nghiệp vụ là ranh giới so, không phải request
HTTP tới provider hoặc số đo model.

Mỗi phép so dùng trực tiếp `bytes == bytes`, ghi byte khác đầu (từ 0), độ
dài hai bên và hai băm. Không in byte/nội dung sai khác hoặc đường máy.
Test ép hai hash giả bằng nhau vẫn phát hiện bytes khác.

## Kết quả chẩn đoán kỹ thuật — không phải bản vàng

Artifact đầy đủ: [TX-4-E6-CHAN-DOAN.json](TX-4-E6-CHAN-DOAN.json).
Hai đầu vào là DEMO kỹ thuật do test tạo, **chưa được lead chấp nhận**;
câu trả lời giả rỗng/null chỉ để kiểm cơ chế, không đánh giá độ chính xác.
Không có bản vàng nghiệm thu được tạo từ chính kết quả mới.

| Phần | DEMO thường: byte cũ / mới; byte khác đầu | DEMO Track Changes: byte cũ / mới; byte khác đầu |
|---|---|---|
| Bộ 10 cột | 8.661 / 8.661; trùng | 8.661 / 8.661; trùng |
| Tham số pipeline | 13.243 / 13.243; trùng | 13.243 / 13.243; trùng |
| Văn bản | 116 / 116; trùng | 100 / 100; trùng |
| Câu hỏi | 16.111 / 8.035; **3** | 15.418 / 8.018; **3** |
| Bảng | 24.581 / 14.642; **3** | 24.836 / 14.642; **3** |
| Phản hồi | 308 / 2.587; **13** | 274 / 2.587; **13** |

Nguồn cũ: DEMO thường **9** câu hỏi (1 dò, 3 nhóm, 5 lượt rà lại);
Track Changes **8** câu hỏi (1 dò, 2 nhóm, 5 lượt rà lại).
TX-2: **1** câu hỏi đủ 37 trường ở mỗi ca. Track Changes nhận đúng **2**
thay đổi, không giữ chữ xóa; văn bản hai bên trùng ở mẫu này.
Mọi khác biệt giữ nguyên. Kết quả chẩn đoán: **chưa đạt**; trạng thái
nghiệm thu tổng thể: **chưa kiểm** do thiếu nguồn được chấp nhận.

## Nguồn còn thiếu để nghiệm thu

Lead cần đặt bộ nguồn DEMO đã review ở `tham-chieu/e6/` và ghi biên bản
chấp nhận (PR/biên bản, phạm vi ca, người duyệt):

- DOCX hợp đồng thường và DOCX Track Changes được chấp nhận, kèm SHA-256.
- Snapshot module và tham số/prompt đã ghim độc lập cho từng việc; ít nhất
  hai module có bản riêng, kể cả cùng loại XD.
- Băng AI giả cố định cho cả hai giao thức; lead xác nhận chúng biểu diễn
  cùng câu trả lời nghiệp vụ. Phải đủ chính xác mọi lượt dò/nhóm/rà lại;
  thiếu hoặc dư lượt đều bị chặn, không tự sinh đáp án.
- Bản vàng DEMO được lead chấp nhận: bytes của cả sáu artifact nguồn, cùng
  quy tắc biểu diễn đã review. Công cụ kiểm lại bản vàng với wrapper nguồn
  trước khi so nguồn với module. Bản vàng không được thiếu bất kỳ artifact.

Manifest JSON phiên bản 1 có `nhan="DEMO"`, `chap_nhan_lead` là tham chiếu
biên bản chấp nhận, `cac_ca` có mã duy nhất, đủ `loai="thuong"` và
`loai="track_changes"`. Mỗi ca có bốn nguồn `docx`, `tham_so`, `ai`, `vang`;
mỗi nguồn dạng `{"tep":"DEMO-ten-tep.json","bam":"sha256:<64 hex>"}`,
đường tương đối bên trong thư mục manifest, không symlink/đường ngoài.

`tham_so` là dict tham số bước TX-2, gồm chuỗi snapshot/hash/prompt/phiên bản
và ngân sách. `ai` là `{"cu":{"tim_vi_tri":[...],"hoi_trich":[...]},
"moi":{...}}`: từng lượt dò trả dict mã→danh sách ID; từng lượt trích trả
danh sách item nguồn; `moi` là `du_lieu` đủ thứ tự mã và ô TX-3. `vang` là
object đủ sáu khóa artifact, giá trị là **chuỗi chứa đúng bytes UTF-8 đã
chấp nhận**, không phải object để công cụ tự chuẩn hóa. Không có chế độ
tạo/kích hoạt bản vàng. `chap_nhan_lead` là dấu dẫn tới review bên ngoài,
không phải cơ chế xác thực quyền hoặc chữ ký số.

Các manifest/bản vàng tự tạo trong `test_e6.py` chỉ nằm vùng tạm pytest, có
nhãn UNIT TEST, kiểm cổng **thất bại**; không được đưa vào nguồn nghiệm thu.

## Phương án làm lại riêng — chưa triển khai

Giữ E6 nguyên trạng. Khác biệt không chỉ là số lượt: dạng DTO/khuôn và cấu
trúc dòng bảng hiện tại cũng khác nguồn. Cần thiết kế lớp kết quả tương thích
bảo toàn nội dung bảng/phản hồi nguồn, đồng thời giữ hậu kiểm nghiêm; không
bỏ cột khỏi phép so hoặc hạ cổng trích dẫn để làm xanh.

| Phương án trình lead | Ưu / nhược / điều kiện | Giờ engine ước tính riêng |
|---|---|---:|
| **A — batch có contract mới, Core điều phối** (đề xuất) | Biểu diễn rõ dò/nhóm/rà lại và hợp nhất, dễ ghim/replay; cần review loại AI mới/cửa Core, tương thích bảng phải thiết kế riêng | **12–18 giờ** |
| B — nhiều bước v1 lặp có trạng thái do Core điều phối | Có thể tái dùng phong bì AI hiện tại; phức tạp hơn về CAS/hủy/lease/lượt chưa rõ và kết thúc chuỗi, vẫn cần cửa lặp Core và lớp bảng tương thích | **18–24 giờ** |

Hai dự toán là sơ bộ, cần chốt kiến trúc/contract sau khi lead cấp nền E6;
chưa gồm công Core/module/AI, chờ máy, phê duyệt hoặc N1/T3 thật. **Không
tính giờ làm lại này vào TX-4 4 giờ.** Chỉ mở code sau khi được giao riêng.
Không chọn giữ một lượt rồi bỏ phần câu hỏi/bảng khỏi E6.

## Kiểm đã chạy

Môi trường Windows, `.venv` trong worktree với `--system-site-packages`;
Python **3.13.14**, SDK **2.0.0** cài offline `--no-index --no-deps` từ
wheel trong repo; SHA-256 wheel `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp `SHA256SUMS.txt`. pytest **9.1.1** có sẵn; không thêm dependency.
Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, tắt plugin pytest tự nạp.

| Lệnh bằng `.venv/Scripts/python -B` | Kết quả thật |
|---|---|
| `-m kho_tri_thuc_sdk.thu e_trich_xuat/goi/e_trich_xuat` | **2/3 ĐẠT, exit 1**; TX-2 `CHUA_CAU_HINH`, CLI 2.0 thiếu ngăn, giữ **C-TX-04** |
| `-m pytest e_trich_xuat/tests -q --basetemp=.pytest-tmp` | **375 passed in 11.68s, 0 skipped, exit 0** |
| `e_trich_xuat/tests/kiem_doc_lap.py` | **[ĐẠT], exit 0** |
| `e_trich_xuat/tests/chay_demo_voi_ngan_gia.py` | **5/5 ĐẠT, exit 0**, hai DEMO TX-3 chỉ đăng ký trong RAM |
| `e_trich_xuat/tests/kiem_e6.py` | **exit 2**, “Thiếu nguồn đối chiếu E6.”, không có ca được chấp nhận |
| `e_trich_xuat/tests/kiem_e6.py --chan-doan` | Hàm/CLI trả **2**, phát hiện sai khác trên cả hai DEMO kỹ thuật; artifact ở trên |

**đã kiểm bằng Core giả (CoreGia)**. Test mới kiểm sai một byte/đảo thứ tự/
cột/câu hỏi/bảng/phản hồi, băm giả bằng nhau, hai module chung app/ngăn có
bộ riêng, runtime sai hash không tải tệp, nguồn thiếu/sai băm, thiếu duyệt/
Track Changes/bản vàng/lượt AI và sai bản vàng dù đã băm lại. Chặn network
và ghi đĩa khi chạy đối chiếu. Hai mẫu `ngan.py`/`cau_hinh.py` giữ nguyên,
test SHA sau CRLF→LF đã chạy bắt buộc. Không có tệp tạm trong wrapper;
BytesIO đóng theo context manager; dữ liệu engine/CoreGia chỉ ở RAM.
JSON biên bản là artifact phát triển theo yêu cầu TX-4, không phải dữ liệu
runtime engine tự lưu.

Linux chưa chạy thực tế trong worktree Windows; không chứng nhận Linux,
Core thật/ACL/TTL/lưu-đóng hoặc N1/T3 thật. **0 mạng/AI thật, 0 Cloud**.
Không sửa Core/SDK/schema/manifest/mã runtime hoặc nguồn chỉ đọc, không
xóa tệp, không commit/push. Cổng có ngăn chờ lead xác nhận như TX-2.

Thời gian thực tế (UTC+07), **15/11/2026**: bắt đầu **09:54:00** theo lead,
kết thúc/chốt kiểm **10:12:54**, khoảng **0,32 giờ** so với **4 giờ công
ước tính**. Chưa gồm làm lại T3/batch hoặc thời gian cấp/duyệt nền E6.
Rà cuối AST/UTF-8/NFC/artifact tái lập và `git diff --check`: đạt.

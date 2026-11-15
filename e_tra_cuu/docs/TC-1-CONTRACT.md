# TC-1 — Contract hồ sơ và chỗ nối dữ liệu

Ngày 15/11/2026 · PR: **chờ lead mở** · Ước tính phiếu: **3 giờ**.

TC-Q13 và lựa chọn TC-Q14 đã được Anh duyệt theo quyết định chiều 15/11.
Mục §7 tài liệu loại chung còn đoạn lịch sử “chưa duyệt”; quyết định chiều thắng.
TC-Q06 tiếp tục **không tự xóa**. Không sửa tài liệu loại chung hoặc schema đã khóa.
TC-0 có khung; cổng CLI 0 demo của SDK vẫn trả 1, không coi là nghiệm thu nghiệp vụ.

## 1. Phạm vi và metadata đăng ký

TC-1 tạo đúng 5 tệp schema nguồn/bản chép: nguồn mới
`_chung/contract/ho_so_tra_cuu.schema.json` và 4 bản chép trong
`goi/e_tra_cuu/contract/`. Ba schema chung `van_ban_tai_lieu`, `yeu_cau_ai`,
`tra_loi_ai` chép nguyên bytes; cả bốn cặp kiểm SHA-256 sau **chỉ đổi CRLF→LF**.
Không đăng ký năm DTO `.v1` lịch sử, không thêm dependency.

Metadata loại đã duyệt (thiết kế để TC-2 chép vào manifest):

```json
[
  {"ma":"van_ban_tai_lieu","ten":"Văn bản tài liệu có vị trí"},
  {"ma":"yeu_cau_ai","ten":"Yêu cầu hỏi AI"},
  {"ma":"tra_loi_ai","ten":"Trả lời AI có trích dẫn"},
  {"ma":"ho_so_tra_cuu","ten":"Hồ sơ tính toán tra cứu"}
]
```

Producer/consumer `ho_so_tra_cuu` chỉ là `e_tra_cuu`. Module đọc JSON xuất cuối;
không mặc nhiên cho engine khác nhận. Khung manifest giữ SDK 2.0/API v1,
`0.1.0`, cục bộ, 1 việc đồng thời, readiness 30 giây, không bí mật/webhook.
**TC-1 giữ nguyên engine.json/chay.py TC-0**, stub `tra_cuu.kiem_khung@1`
luôn `CHUA_LAM`, `chay_thu_demo=[]`. TC-2 thay đồng thời manifest và stub,
đăng ký handler đích hoặc stub lỗi rõ cho phần chưa làm trước phát hành.
Chỉ có schema trong gói không có nghĩa loại/năng lực đã kích hoạt.

| Năng lực (tiền tố `tra_cuu.`) | Nhận | Trả | Handler/lát | Thời hạn giây |
|---|---|---|---|---:|
| `nhan_yeu_cau@1` | `tep` JSON | `ho_so_tra_cuu` | TC-2 | 120 |
| `cat_doan@1` | `ho_so_tra_cuu` | `ho_so_tra_cuu` | TC-3 | 120 |
| `chuan_bi_ai@1` | `ho_so_tra_cuu` | `yeu_cau_ai` | TC-4 | 180 |
| `phan_loai_tai_lieu@1` | `tra_loi_ai` | `ho_so_tra_cuu` | TC-5 | 180 |
| `phan_tich_cau_hoi@1` | `tra_loi_ai` | `ho_so_tra_cuu` | TC-6 | 180 |
| `xep_hang_lai@1` | `tra_loi_ai` | `ho_so_tra_cuu` | TC-6 | 180 |
| `soan_tra_loi@1` | `tra_loi_ai` hoặc `ho_so_tra_cuu` | `ho_so_tra_cuu` | TC-7 | 180 |
| `xuat_ket_qua@1` | `ho_so_tra_cuu` | `truong` tĩnh | TC-8 | 120 |

Mọi năng lực hủy được, `tep_toi_da_mib=20` cho việc đọc snapshot/tệp con;
bước nhận MIME `application/json`; các bước còn lại `ky_tu_toi_da=500000`.
Tham số theo phiếu §2.3: nhận có `bam_yeu_cau` bắt buộc (71 ký tự);
cắt có `do_dai_muc_tieu` nguyên 200…8000, mặc định 2000; chuẩn bị AI có
`tac_vu`, `ma_prompt` ≤200, `phien_ban_prompt` ≤100, `prompt` ≤16000 bắt buộc,
`model_uu_tien` ≤200 tùy chọn. Hậu kiểm/xuất không nhận tham số thay nguồn/ngưỡng.

Xuất luôn đủ trường: `tac_vu,trang_thai,tra_loi,nhan,nhom_de_xuat,loai_de_xuat`
kiểu `van_ban`; `tang,so_doan,so_ung_vien` kiểu `so`;
`co_can_cu,co_mau_thuan,can_duyet` kiểu `co_khong`; `tep_json` kiểu `tep`.
Không áp dụng/chưa xác định là null. JSON đầy đủ ở Core, không nhét vào ô chữ.

## 2. Phong bì phiên bản 1

Chỉ một phong bì `{"loai":"ho_so_tra_cuu","ho_so_tra_cuu":{...}}`,
không có `nhan_2`. Schema Draft 2020-12 kiểm hình dạng; cho thêm trường tùy chọn
tương thích, đổi nghĩa/required không tương thích phải tạo mã `ho_so_tra_cuu_2`.
Từ chối trường mở chứa nội dung lớn/không hợp miền ở biên Python, không lách trần.

| Payload (mọi trường đều required) | Kiểu / giới hạn |
|---|---|
| `phien_ban` | Integer đúng 1; bool không phải integer |
| `ma_yeu_cau` | Chuỗi opaque không trắng do Core cấp/ghim; không chứa câu hỏi/quyền |
| `tac_vu` | `phan_loai,cat_doan,phan_tich_cau_hoi,xep_hang_lai,soan_tra_loi` |
| `giai_doan` | Enum tám giá trị theo bảng trạng thái dưới |
| `ho_so` | Tệp Core với `tep_id,ten,mime,kich_thuoc` required; MIME `application/json`, bytes 1…20971520; tên kỹ thuật an toàn |
| `bam_ho_so` | `sha256:<64 hex>` trên **bytes snapshot đã tải** trước parse |
| `bam_cau_hinh` | SHA-256 canonical JSON của giá trị cấu hình đã ghim |
| `bam_danh_muc` | SHA-256 canonical JSON danh mục nếu dùng, ngược lại null |
| `phien_ban_engine` | `e_tra_cuu <major>.<minor>.<patch>`, khớp bản chạy tính kết quả |
| `tom_tat` | Object required đủ tám trường theo bảng kế tiếp |
| `canh_bao` | Mảng câu Việt cố định do mã tạo; không nguyên văn/tên riêng/path/khóa |

| `tom_tat` (required từng trường) | Miền |
|---|---|
| `trang_thai` | null hoặc `da_cat_doan,cho_phan_loai,da_phan_loai,da_phan_tich,da_xep_hang,co_can_cu,khong_thay_can_cu` |
| `so_doan` | Integer 0…5000 hoặc null; chỉ 0 khi thực sự tính ra tập rỗng |
| `so_ung_vien` | Integer 0…50 hoặc null |
| `tang` | 1, 2, 3 hoặc null; không nhận bool |
| `co_can_cu,co_mau_thuan,can_duyet` | Boolean hoặc null; không suy false khi chưa chạy |
| `nhan` | `xanh,vang,null` |

Trần **toàn phong bì ≤65536 bytes UTF-8**, không dùng `maxLength` thay byte count.
Các chuỗi/mảng chưa có trần riêng chịu trần toàn phong bì; không tự thêm trần mã
opaque/cảnh báo ngoài quyết định. Không toàn văn/danh mục/ứng viên/ảnh base64 trong
phong bì. Schema không thể kiểm băm thật/kích thước thật/tệp đã tải/quyền.

| Tác vụ | Giai đoạn hợp lệ trong hồ sơ | Kết quả và `tom_tat.trang_thai` |
|---|---|---|
| `phan_loai` | `da_nhan → cho_ai → da_phan_loai` hoặc `cho_phan_loai` | `da_phan_loai` hoặc `cho_phan_loai` tương ứng |
| `cat_doan` | `da_nhan → da_cat_doan` | `da_cat_doan`; không AI |
| `phan_tich_cau_hoi` | `da_nhan → cho_ai → da_phan_tich` | `da_phan_tich` |
| `xep_hang_lai` | `da_nhan → cho_ai → da_xep_hang` | `da_xep_hang` |
| `soan_tra_loi` | `da_nhan → cho_ai → da_soan`; Python `da_nhan → da_soan` | `co_can_cu` hoặc `khong_thay_can_cu` |

`da_nhan/cho_ai`: trạng thái kết quả null; tóm tắt số đếm chỉ có khi tập đã xác lập.
`cho_ai` là giai đoạn snapshot ghim trong yêu cầu AI; phong bì ngoài bước chuẩn bị
vẫn là `yeu_cau_ai`. Hậu kiểm không nhận hồ sơ `cho_ai` trực tiếp thay phản hồi.
Xuất từ chối `da_nhan/cho_ai`, sai tác vụ hoặc chuyển trạng thái trái bảng.
Python không AI chỉ trả tầng 1 bằng mẫu đã duyệt đủ bằng chứng, hoặc từ chối thiếu
căn cứ. TC-Q14 đã chốt: Xanh chỉ Python tầng 1 đã duyệt/còn hiệu lực/đủ tin cậy,
không cờ chờ; có LLM soạn tối đa Vàng. `khong_thay_can_cu`: không số đoán,
`co_can_cu=false`, nhãn null. Mâu thuẫn giữ bằng chứng hai bên, tối đa Vàng,
`co_mau_thuan=true,can_duyet=true`; cờ là đề nghị, không xác nhận đã tạo K5.

## 3. JSON yêu cầu và snapshot tại Core

JSON yêu cầu là bytes UTF-8 ≤1 MiB nằm trong kho Core; đầu vào SDK là `tep`,
`tham_so.bam_yeu_cau` băm bytes chính xác. Cấu trúc bắt buộc:
`phien_ban=1,ma_yeu_cau,tac_vu,ngu_canh_core,du_lieu`.
`du_lieu` gồm tham chiếu+băm các tài nguyên cần tác vụ ở bảng dưới. Mọi tham chiếu
JSON dùng `{tep:{tep_id,ten,mime,kich_thuoc},bam}`; nguồn gốc thêm
`ma_nguon,phien_ban_nguon`. Không có đường máy, URL, SQL, mã thực thi hoặc base64.

Snapshot sau nhận bắt buộc `phien_ban,ma_yeu_cau,tac_vu,giai_doan,ngu_canh_core,
cau_hinh,nguon,du_lieu,ket_qua`.
`cau_hinh={gia_tri,row_version}` từ một bản đọc ngăn nhất quán, dùng giá trị sau
điền mặc định trên bản sao; băm chỉ `gia_tri`, không gồm row_version/băm chính nó.
`nguon` là tập nguồn/tham chiếu/phiên bản/băm đã kiểm; `ket_qua=null` trước xử lý.
Danh mục ghim ở `du_lieu.danh_muc`; băm đúng object này, không tự chứa băm của nó.
Không dùng `doc_cau_hinh` rồi đọc row_version ở thời điểm khác để ghép hai bản.

`ngu_canh_core={phap_nhan_id,module,nhom,nguoi_hoi_id,thoi_diem,ma_pham_vi}`
do cửa tin cậy Core cấp (thời điểm ISO có múi giờ). SDK 2.0 chỉ có
`viec_id,buoc,phap_nhan_id`: JSON tự khai ngữ cảnh hoặc `da_loc_quyen=true`
không là chứng nhận. Core phải đối chiếu ngữ cảnh đã xác thực, phạm vi từng nguồn,
request/task và quyền xuyên bước. Băm/tep_id/opaque id không thay quyền Core.
Thiếu cửa tin cậy C-TC-02/03 trả `TC_CHUA_CO_CUA_CORE`, không fallback runtime.
Thiếu pháp nhân ngữ cảnh SDK trả `TC_THIEU_NGU_CANH`; pháp nhân giả khác ngữ cảnh
là `TC_SAI_NGUON`. Chưa rõ pháp nhân nghiệp vụ trong văn bản phân loại thì đưa
hàng chờ, không đổi ngữ cảnh SDK theo model.

| Tác vụ | `du_lieu` bắt buộc, bổ sung cho snapshot chung | `ket_qua` sau xử lý |
|---|---|---|
| `phan_loai` | `tai_lieu` gồm nguồn gốc/băm bytes/phiên bản, nguyên phong bì `van_ban_tai_lieu` hoặc ref+băm; `danh_muc` 8 nhóm/loại/trạng thái/loại hình CP–TNHH/đối tượng; `phan_loai_cu,quan_he_phu_luc` null nếu không có | `nhom_de_xuat,loai_de_xuat,doi_tuong,diem,can_cu,ly_do_cho,de_nghi_chuyen_bo`; enum từ danh mục Core, không tự duyệt/đổi nhóm/kích hoạt nhựa–điện |
| `cat_doan` | `tai_lieu` cùng nguồn/cấu trúc bảng; `metadata_core` nhóm/loại/hiệu lực/duyệt; danh mục nếu thực sự cần, nếu không băm null | `doan[]` với mã ổn định, nguyên văn, nguồn/băm/phiên bản, offset, cấu trúc/ô/vị trí/map; phủ đủ nguồn, ≤5000 |
| `phan_tich_cau_hoi` | `cau_hoi`, phạm vi/thời điểm Core; `ham[]` tên/phiên bản/mô tả/schema tham số/schema đầu ra/giới hạn/quyền đã lọc | `y_dinh,thuc_the[],ham_de_xuat[],phu_thuoc_thoi_diem`; thực thể có loại/mã/giá trị chính xác, hàm+tham số đúng allowlist; engine không thực thi hàm |
| `xep_hang_lai` | `cau_hoi,thuc_the,ung_vien[]` Core đã lọc quyền/hiệu lực; từng mã duy nhất gắn một nguồn/phiên bản/băm/nội dung/vị trí/điểm tìm kiếm; thang điểm ghim | `xep_hang[]` hoán vị đủ đúng tập mã ứng viên, điểm hữu hạn đúng thang; không thêm/bớt/trùng/đổi nguồn |
| `soan_tra_loi` | `cau_hoi,thuc_the,tang,bang_chung[],co_van_ban_moi_cho_duyet,phu_thuoc_cache[]`; tầng 1 có trường/giá trị/đơn vị/duyệt/hiệu lực/độ tin cậy/mốc công bố và nguồn; tầng 2–3 có đoạn/kết quả trích có vị trí | `trang_thai,tra_loi,khang_dinh[],co_can_cu,co_mau_thuan,can_duyet,nhan`; mỗi khẳng định nối thực thể/trường/giá trị/đơn vị → dẫn chứng → nguồn; thiếu căn cứ trả từ chối |

Mảng chưa xử lý không thay bằng tập rỗng: `ket_qua=null`; sau xử lý rỗng mới là
`[]`. Tập phụ thuộc cache gồm nguồn/phiên bản/duyệt/mốc công bố/thực thể/phạm vi/
cờ thời điểm; Core kiểm lại quyền mọi nguồn và hết hạn theo sự kiện. Không cache
câu phụ thuộc thời điểm ở bản đầu. Không đối chiếu ngược mọi tệp tầng 1 trái QĐ-4.
Không mặc định DTO TX đã có: bằng chứng TX qua adapter Core tin cậy đã duyệt.

## 4. Băm, nguồn, offset và Local AI

Canonical JSON: `json.dumps(obj,ensure_ascii=False,sort_keys=True,
separators=(",",":"),allow_nan=False).encode("utf-8")`. Từ chối khóa trùng,
NaN/Infinity, UTF-8/surrogate hỏng, bool trong trường số; không đổi Unicode NFC/NFD.
SHA xuất chữ thường `sha256:<64 hex>`; đọc chấp nhận hex hoa/thường như schema.
Băm tệp = bytes chính xác trước parse (không tự canonical hóa để “chữa” sai băm).
Băm toàn văn = UTF-8 chuỗi, khác băm bytes tệp gốc và băm phong bì OCR.
Tải snapshot bằng `viec.tai_tep_ra`, chỉ dựng metadata sau Core xác nhận; khi đọc
bằng `viec.mo_tep`, đối chiếu MIME/tên/kích thước với metadata Core, kiểm băm trước
parse. Không giả id hoặc xác nhận tải/lưu thành công; mất ACK/hủy không ra XONG giả.

Offset dùng **Unicode code point**, khoảng nửa mở `[bat_dau,ket_thuc)`, 0-based;
phải `nguyen_van == van_ban[bat_dau:ket_thuc]`, không dùng byte/UTF-16 của JS.
Nguồn gồm `ma_nguon,tep_id,phien_ban_nguon,bam_goc,bam_van_ban`.
Đoạn/mapping có `bat_dau,ket_thuc,loai_khoi,dieu,khoan,trang,hop,hang,cot,
gop_hang,gop_cot` (không áp dụng là null). Bảng giữ ô rỗng/gộp/tiêu đề và nguồn ô;
đoạn tổng hợp có `map_nguon[]` từng span, không giả một lát liên tục.
Map ngữ cảnh AI có `ai_bat_dau,ai_ket_thuc,ma_nguon,nguon_bat_dau,
nguon_ket_thuc,vai_tro` (`noi_dung`/`ngu_canh_lap`); nhãn kỹ thuật không là chứng cứ.
Mỗi span trích phải nằm trong vùng map và khớp nguyên văn nguồn. Giữ vùng nguồn
để tái dựng đủ toàn văn, phần tiêu đề lặp không đếm hai lần. DOCX chưa phân trang:
nguyên phong bì `so_trang=0,trang=[]`, vị trí đoạn `trang=null,hop=null`, không bịa.

Chuẩn bị ghim thêm snapshot `ai={ma_prompt,phien_ban_prompt,prompt,khuon_tra_loi,
tai_lieu,map_nguon,bam_ngu_canh_ai}`; băm ngữ cảnh trên UTF-8 `tai_lieu` chính xác.
`yeu_cau_ai.chuyen_tiep.tra_cuu` gồm đúng `phien_ban=1,ma_yeu_cau,tac_vu,ho_so,
bam_ho_so,bam_cau_hinh,bam_ngu_canh_ai`, mục tiêu ≤4 KiB, trần chuyển tiếp ≤64 KiB.
Không chứa toàn văn/danh mục/prompt. Hỏi AI giữ nguyên, không cho model tái tạo.
Hậu kiểm so prompt/version/khuôn/request hash/chuyển tiếp/snapshot/task; phản hồi
phải `nha_cung_cap=local`. Không tin riêng `kiem_trich_dan.dat`, tự kiểm quote/map/
đúng thực thể–trường–đơn vị. `bam_dau_vao` phản hồi theo Hỏi AI trên toàn yêu cầu
canonical, không thay bằng băm toàn văn. Core điều phối AI, **0 Cloud**, M9/07 Local.

## 5. Trần, lỗi và ranh giới kiểm

| Trần engine tự kiểm trước parse/xử lý | Giá trị |
|---|---:|
| JSON yêu cầu chính | 1 MiB |
| Mỗi tệp con/snapshot/kết quả | 20 MiB |
| Tổng bytes tệp con thực đọc/việc | 64 MiB |
| Phong bì hồ sơ / chuyển tiếp AI | 64 KiB mỗi loại |
| Văn bản / trang nếu có / đoạn | 500000 ký tự / 60 / 5000 |
| Đơn vị cấu trúc không chia an toàn | 8000 ký tự |
| Câu hỏi / hàm / mục danh mục / ứng viên | 4000 ký tự / 100 / 1000 / 50 |
| `tai_lieu` AI / khuôn | 100000 ký tự / 32 KiB |

Vượt từ chối, không cắt đuôi/top-k/batch tự động/chuyển Cloud. Ký tự không là
phép đo context model. SDK `mo_tep` dùng trần 20 MiB chung của bước, không sửa SDK.

Ba schema chung có `$ref`, `oneOf`, `type` mảng. Bộ đọc `cau_hinh.py` NGAN-0
**KHÔNG là validator chung**, từ chối từ khóa ngoài tập hỗ trợ; không đưa những
schema này vào đó và không báo chúng đã được runtime validate đầy đủ.
TC-2…7 phải viết kiểm miền rõ bằng Python: JSON nghiêm/trần, quan hệ nguồn/quyền,
task/stage/summary, allowlist danh mục/hàm, đủ ứng viên, quote/offset/map, kiểu
tiền `{so,tien_te}`/ngày `YYYY-MM-DD`, đúng thực thể, nhãn và các trạng thái trên.
Schema không tự chứng minh các quan hệ này. TC-1 không thêm validator/dependency.

| Lỗi `LoiNghiepVu` | Khi nào / câu cố định |
|---|---|
| `TC_SAI_NGUON` | Ref/băm/metadata/phiên bản/summary lệch snapshot, giả pháp nhân: “Chưa kiểm chứng được nguồn tra cứu. Anh gửi lại yêu cầu từ hồ sơ được cấp quyền.” |
| `TC_SAI_GIAI_DOAN` | Sai cặp tác vụ–giai đoạn/chuyển bước/xuất trung gian: “Hồ sơ chưa ở đúng bước xử lý. Anh chạy lại từ bước nhận yêu cầu.” |
| `TC_THIEU_NGU_CANH` | Thiếu ngữ cảnh bắt buộc: “Chưa đủ ngữ cảnh tra cứu. Anh gửi lại yêu cầu từ hồ sơ.” |
| `TC_QUA_GIOI_HAN` | Quá trần dữ liệu: “Yêu cầu vượt giới hạn xử lý. Anh chia lại hồ sơ trước khi gửi.” |

Thiếu cửa tin cậy: `TC_CHUA_CO_CUA_CORE`; hình dạng/JSON sai:
`TC_DAU_VAO_KHONG_HOP_LE`; ngân sách AI: `TC_QUA_NGAN_SACH_AI`; Cloud:
`TC_CHI_LOCAL`; thiếu cấu hình: `CHUA_CAU_HINH`. Không log nguyên văn/path/khóa.
Không rõ phân loại/thiếu căn cứ là trạng thái nghiệp vụ, không lỗi kỹ thuật.
Nguồn ngoài đã nhận chưa trả do tầng sở hữu báo `ChuaRo(ma_tuong_quan)`.

## 6. Kiểm TC-1 và phụ thuộc

Test contract chỉ là mô hình thực thi đặc tả trong `tests/`, dùng CoreGia thật
của SDK để giữ bytes DEMO; adapter mở tệp con/quyền giả chỉ trong tests.
Các ca sai cặp task/stage, ref hỏng, băm/size sai, số đếm lệch, pháp nhân giả,
thiếu ngữ cảnh/quá trần không chứng nhận handler chưa có. Test schema dùng bộ
đánh giá giới hạn trong tests **chỉ cho schema mới**, fail khi gặp từ khóa lạ;
không quảng bá nó là validator Draft 2020-12 hoặc dùng cho ba schema chung.
Khung/lỗi SDK hiện có **đã kiểm bằng Core giả (CoreGia)** khi chạy pytest;
chưa chạy Core thật, AI thật, Linux hay kiểm RLS thật. Kết quả thật ở `VIEC.md`.

- **C-TC-02:** Core ghép JSON và cấp quyền/vòng đời tệp con xuyên bước/ACK;
  không có fan-in tự động SDK 2.0; runtime phải từ chối khi thiếu cửa.
- **C-TC-03:** ngữ cảnh, danh mục/hàm/bằng chứng/duyệt/hiệu lực/quyền tin cậy,
  RLS trước nguồn tới AI; cờ JSON/băm không chứng minh điều này.
- **C-TC-05:** log an toàn, lỗi trần/lease và kiểm loại riêng ở SDK; engine tự
  kiểm sâu, không sửa SDK. C-TC-01 giữ ghi nhận CLI 0 demo trả 1/ngăn thật chưa có.

Mọi cấu hình/bài đo cần giữ qua `Ngan`; khóa/lọc bảng pháp nhân luôn có
`phap_nhan_id` từng lệnh, đúng `khai_bao`, `KetQuaLenh`, CAS/lô mẫu NGAN-0.
Snapshot/tệp ở Core; chỉ mục/vector/cache/nhật ký hỏi đáp/danh mục do Core giữ.
Không kho thứ hai hoặc tệp bền trên máy engine; tệp tạm của việc dọn trong finally.

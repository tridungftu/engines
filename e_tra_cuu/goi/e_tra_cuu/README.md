# Tra cứu tài liệu — SDK 2.2.0

## UI-TC — 21/11/2026

Màn `ui/cau_hinh.js` chia **Cơ bản** (ngưỡng phân loại chỉ đọc, độ dài mục
tiêu mỗi đoạn) và **Nâng cao** thu gọn (bộ quy tắc và toàn bộ trần hiện có).
Ngưỡng chưa đo hiện “Chưa đo”, không tự điền số hoặc kích hoạt ngưỡng.
Mỗi ô có nhãn, hướng dẫn, mẫu và lỗi cạnh ô; mở Nâng cao khi lưu sai.
Lưu dùng CAS, tranh chấp đọc lại bản mới để kiểm tra trước khi lưu lại.

Schema có `title`, `description`, `examples` đủ từng cấp; mô tả gốc liệt kê
cấu trúc, điều kiện bắt buộc, giá trị cho phép, mặc định và mẫu DEMO đầy đủ
cho ô JSON chung khi Core chưa nạp màn. Không thay đổi ràng buộc hoặc xử lý
việc. Theo schema thực tế có **13 trần ngân sách + 2 trần cắt đoạn**; tất cả
đặt trong Nâng cao, không bỏ trường để khớp con số 14 trong phiếu UI.

`KHAI-SDK-2.1.json` chỉ khai dự kiến hai màn/quyền; SDK 2.2.0 chưa nhận khóa
màn trong manifest. Hai màn chỉ gọi `KttCore.engine("e_tra_cuu")`; không
có thao tác kiểm máy/dịch vụ, không có API key hoặc cổng bí mật ở UI-TC.
Đã kiểm bằng Core giả (CoreGia)/KttCore giả; chưa nạp trong Core thật.
Ảnh và cách dựng DEMO: `../../docs/ui-tc/README.md`.

Kiểm UI không mạng: `node --test e_tra_cuu/tests/ui/*.test.js` tại gốc repo.

## TC-10 — DEMO toàn tuyến, 15/11/2026

**Chưa đạt cổng nghiệm thu chung:** CLI chuẩn **0/12, mã 1**: năm ca nhận
trả `CHUA_CAU_HINH`, bảy ca có tệp con trả `TC_CHUA_CO_CUA_CORE`. Giữ nguyên
năm ca nhận, bổ sung bảy ví dụ bao phủ đủ tám năng lực đã làm. Không có default
DEMO hoặc cấu hình tự tạo trong runtime. Các số 0/5 của TC-S22 bên dưới là
lịch sử trước khi bổ sung ví dụ TC-10.

Đã kiểm bằng Core giả (CoreGia): harness **55/55** hồi quy, bộ đáp án
**38/38** ca (31 lượt Local giả qua consumer Hỏi AI AI-12, 0 Cloud). Đơn vị
chấm là **một ca**, khẳng định/trích dẫn phải đúng toàn bộ mới tính đạt.
Pytest **1330 passed, 0 skipped**; kiểm độc lập mã **0**, kiểm kê **141/141**
tệp (trừ chính kiểm kê) khớp bytes/SHA-256. Đây là số ca kiểm cơ chế:

| Chỉ số DEMO | Tất cả nhóm | Riêng nhóm 02 |
|---|---:|---:|
| Trả lời đúng giá trị/thực thể/tiền/ngày/nhãn | 12/12 | 11/11 |
| Trích dẫn đúng nguồn/phiên bản/băm/offset | 12/12 | 11/11 |
| Từ chối đúng khi không đủ căn cứ hoặc AI sai | 6/6 | 6/6 |
| Phân loại đúng nhóm/loại hoặc hàng chờ có lý do | 20/20 | 2/2 |

Không gộp trung bình. Mỗi chỉ số có `tu_so`, `mau_so`, `so_ca_du_kien`,
`chua_do`, `skip`, `loi_chay`; lỗi chạy tính không đạt, skip/chưa đo tách riêng,
mẫu số 0 cho `ty_le=null`. Không biến số ca hồi quy thành chỉ số chất lượng.
Bộ DEMO **chưa được nghiệp vụ duyệt**; `accuracy_model_that=null`, chưa có
ngưỡng tin cậy thật, không kích hoạt nhóm. TC-Q15 đã duyệt nguyên tắc duyệt
bộ câu hỏi/ngưỡng trước áp dụng, nhóm 02 trước; chưa duyệt bộ fixture này.

`demo/tc-10/bo-ca-DEMO.json` giữ ca đầu vào/Local giả, `dap-an-DEMO.json` giữ
đáp án độc lập. Băm bytes chính xác ở `bam-DEMO.json`; không chuẩn hóa dữ liệu
lúc kiểm. Bộ có đủ tám nhóm, 03/04, CP/TNHH, nhựa/điện chờ kích hoạt,
VAY-A/B, đổi bản/hết hiệu lực, nhân sự 07, mâu thuẫn, thời điểm và từ chối
tiền/ngày/quote/offset bịa. `tao_bo_demo_tc_10.py` chỉ tạo dữ liệu từ các
giá trị đặt trước, không lấy đáp án từ runtime; không chạy generator lúc chấm.

`demo/tc-10/cong-chuan/` chứa snapshot, tệp con, phản hồi AI Local và giấy
cấp giả đã đóng băng từ CoreGia, cùng băm thật cho bảy ví dụ mới. Loader trong
tests nạp bytes qua `them_tep`, kiểm metadata/băm và cấp quyền ngoài payload.
Các vị trí mã việc xen giữa mã tệp được tái lập bằng tệp DEMO không tham chiếu;
không có ID được coi là có thật khi chưa tải bytes. CLI chưa có cửa nạp những
fixture này; harness là cổng bổ sung để lead review C-TC-01/02/05.

SDK 2.2.0 đã thay `NganBoNho` tạm: harness dùng `dat_cau_hinh` và `viec.ngan`
thật trên CoreGia. Bài `DEMO-TC10` ghi đúng bốn cặp số đo và tham chiếu báo cáo
vào `dot_kiem`, gửi lại không nhân số đếm. Hai mẫu NGAN-0 giữ nguyên trong
`LUU-TRU/TC-S22`, so băm LF với nguồn; không đưa trở lại runtime.

Adapter `tests/core_hop_dong_tc_10.py` chỉ kiểm hợp đồng điều phối ba tầng và
cache/quyền: thiếu/chưa duyệt/hết hiệu lực/thấp ngưỡng/ngoài trường mới xuống
tầng 2, tầng 3 chờ 202 rồi chạy nền; kiểm quyền mọi nguồn và làm hết hiệu lực
theo phiên bản/nhóm/duyệt/công bố/thu quyền; `bo_qua_cache` và thực thể/pháp nhân
phải khớp. M9/07 mọi nhánh Local, nguồn không quyền bị loại trước dựng AI.
Đây **không phải** triển khai/chứng nhận cache, RLS, runner hoặc HTTP nghiệp vụ
trên Core thật. Hai test MayChuGia chạy bootstrap stdin/HTTP loopback thật,
kiểm lỗi thiếu cấu hình/cửa nguồn đúng và không nộp XONG giả.

Chạy tại gốc repo (Windows dùng Python venv, Linux đổi `Scripts` thành `bin`):

```powershell
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py --bao-cao e_tra_cuu/docs/TC-10-KET-QUA-DEMO.json
node --test e_tra_cuu/tests/ui/*.test.js
e_tra_cuu/tests/KIEM-MAY-SACH.cmd --bao-cao e_tra_cuu/docs/TC-10-MAY-SACH-WINDOWS.json
```

`KIEM-MAY-SACH.cmd` / `kiem_may_sach.sh` là ASCII, dùng cùng công cụ Python:
tạo venv tạm tách biệt, chỉ cài SDK wheel repo offline theo lock/băm, import
gói chép riêng bằng `-I -B`, chạy CLI chuẩn và kiểm không có bytecode. Tạm dọn
trong `finally`; công cụ giữ mã 1 khi CLI chưa đạt. Windows đã chạy import/cài
SDK/không bytecode đạt, CLI vẫn 0/12; venv máy sạch không cài dependency test
nên harness/pytest chạy riêng. `.sh` mới kiểm cú pháp qua Git Bash; **Linux
chưa kiểm** vì không có WSL/Linux. Node **30/30**, chỉ KttCore giả; chưa kiểm
trình duyệt Core thật, RLS, lưu bền, tải 20/150 người hoặc model thật.

Biên bản và Cần Core hiện hành ở `e_tra_cuu/docs/TC-10-KIEM-CHUNG.md` và
`VIEC.md`. `requirements.lock` tiếp tục chỉ SDK 2.2.0 + thư viện chuẩn;
không thêm/cài thư viện mới. Phần TC-S22 dưới đây giữ để tra lịch sử.

Phiên bản **0.2.0**, lát **TC-S22**, ngày **15/11/2026**. Engine chỉ tính toán;
Core cất tệp, ngăn dữ liệu, cấu hình và điều phối các engine. Chỉ DEMO trong gói.
**Chưa đạt cổng nghiệm thu chung:** CLI chuẩn vẫn 0/5 `CHUA_CAU_HINH` vì wheel
2.2.0 chưa có cách nạp cấu hình/quyền nguồn cho `chay_thu_demo`. Không có ngăn
RAM thay thế, cấu hình môi trường hoặc nhánh giả lập trong runtime.

## Năng lực và ranh giới

| Năng lực `tra_cuu.*@1` | Nhận → trả | Xử lý |
|---|---|---|
| `nhan_yeu_cau` | `tep` JSON → `ho_so_tra_cuu` | Kiểm bytes/băm/quyền/nguồn, ghim snapshot |
| `cat_doan` | `ho_so_tra_cuu` → cùng loại | Cắt Điều/Khoản/bảng, giữ Unicode/nguồn/vị trí |
| `chuan_bi_ai` | `ho_so_tra_cuu` → `yeu_cau_ai` | Bốn tác vụ Local; không gọi model |
| `phan_loai_tai_lieu` | `tra_loi_ai` → `ho_so_tra_cuu` | Hậu kiểm phân loại/ranh giới nhóm |
| `phan_tich_cau_hoi` | `tra_loi_ai` → `ho_so_tra_cuu` | Hậu kiểm ý định/thực thể/hàm allowlist |
| `xep_hang_lai` | `tra_loi_ai` → `ho_so_tra_cuu` | Đủ tập mã, không đổi nguồn/cắt ứng viên |
| `soan_tra_loi` | `tra_loi_ai` hoặc `ho_so_tra_cuu` → `ho_so_tra_cuu` | Python tầng 1 hoặc hậu kiểm Local |
| `xuat_ket_qua` | `ho_so_tra_cuu` → `truong` | JSON đầy đủ tại Core + trường tĩnh ghép cột |

Bốn loại chung trong `contract/` giữ nguyên nội dung, chỉ chuẩn hóa LF. Engine
không import/gọi engine khác, CSDL hoặc SQL lúc chạy. Core sở hữu Kho tài liệu,
RLS, chỉ mục/vector, cache, nhật ký hỏi đáp, dừng ba tầng và K5. Bản đầu không
Cloud; M9/nhóm 07 luôn Local. Chưa kiểm Core thật/RLS/Linux/model thật.

## Môi trường và khởi động

Python ≥3.11. Tạo `.venv` mới trong worktree, cài wheel nội bộ `--no-index
--no-deps`; gói chỉ cần SDK và thư viện chuẩn Python. SHA wheel nguyên bytes:

```text
0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984
```

SHA đã đối chiếu `docs/goi-gui-engine/sdk-2.2.0/SHA256SUMS.txt`.
`requirements.lock` ghim `kho_tri_thuc_sdk==2.2.0`; manifest yêu cầu
`>=2.2.0 <3.0.0`. Phụ thuộc test riêng ghim tại `e_tra_cuu/tests/requirements.lock`,
không gửi trong gói. Phiên này cài chúng offline từ các distribution sẵn trên
máy, không dùng `--system-site-packages`; có `jsonschema` để CoreGia kiểm cấu
hình đầy đủ như Core, không dùng đường kiểm schema tối giản của SDK.

Core chạy trong thư mục gói bằng `{python} -m e_tra_cuu.chay`, truyền bootstrap
SDK theo API v1. Đặt `PYTHONDONTWRITEBYTECODE=1` hoặc dùng `-B` để không tạo
bytecode trong gói. Không đọc tệp cấu hình hoặc biến môi trường cấu hình riêng.

## Cấu hình của Core

`engine.json.cau_hinh.schema` trỏ `cau_hinh.schema.json`. Màn cấu hình giữ
`KttCore.engine("e_tra_cuu").cau_hinh.doc/luu` và CAS; không đọc/ghi bảng
`cau_hinh` trong ngăn. SDK cấp **bản chụp `viec.cau_hinh`** lúc nhận việc.
Không giữ đệm cấu hình riêng nên không cần callback làm mới đệm.

- Khởi động chưa có cấu hình được phép; thiếu `phien_ban` hoặc `quy_tac_nhom`
  khi nhận việc trả `LoiNghiepVu("CHUA_CAU_HINH", ...)` với hướng dẫn Admin.
- `phien_ban=1`; `quy_tac_nhom={tep_id,bam}` trỏ tài nguyên Core, SHA-256 đúng
  định dạng. Mã/băm không chứng minh quyền; Core vẫn phải cấp quyền nguồn.
- `phan_loai.trang_thai=chua_do` không sinh ngưỡng. `da_do` phải có `nguong`
  và `bam_bo_do`; engine kiểm quan hệ nghiệp vụ, kiểu/trần và UTF-8 an toàn.
- Mặc định cắt đoạn: mục tiêu 2000 ký tự, đơn vị ≤8000, ≤5000 đoạn. `ngan_sach`
  chỉ cho giảm trần. Default điền trên bản sao, không ghi ngược Core.
- Snapshot ghim giá trị cùng `bam_cau_hinh`; hậu kiểm không thay bằng cấu hình
  mới. SDK chưa công khai phiên bản CAS cấu hình trên `Viec`: `row_version`
  trong **snapshot nội bộ** để `null`, không bịa số phiên bản. Phiên bản CAS
  bài đo ở ngăn vẫn là số thật do SDK/Core trả.

Trong test dùng `core.nap_engine(app)` và `core.dat_cau_hinh(app.ma, gia_tri)`.
Không khởi tạo DEMO tự động trong runtime.

## Ngăn và migration

Phiếu khai duy nhất `dot_kiem`, phạm vi `phap_nhan`, khóa `ma_dot`, duy nhất
`(phap_nhan_id, ma_dot)`. Không khai lại cột hệ thống trong `truong`. Mọi truy
cập Python đi qua **`viec.ngan`**, không fallback sang ngăn app và không truyền
`phap_nhan_id` trong khóa/lọc/giá trị. Core lấy pháp nhân và mã việc tin cậy.

Bài đo chỉ có metadata/băm, bốn cặp tử số/mẫu số và tham chiếu báo cáo tại Core;
không lưu câu hỏi/nguyên văn/nguồn. SDK 2.2.0 chưa nhận kiểu ngăn `json`/`tep`:
`chi_so` và `bao_cao` dùng `van_ban` chứa JSON đã kiểm, cột SQL `text`. UI giải
mã JSON có trần 64 KiB và dùng `textContent`. `bao_cao=null` nghĩa là chưa có.
Không đổi tiền/ngày nghiệp vụ thành số thực hoặc văn bản mất mã tiền tệ.

`lay_hoac_tao_dot` trả `KetQuaLenh` thật của SDK (`id,row_version,da_tao`),
không nhân số đếm khi gửi lại. CAS dùng một lô ≤100 lệnh; lệch phiên bản rollback
cả lô và trả lỗi yêu cầu đọc lại. Không tự retry/ghi đè. SDK chỉ trả kết quả
lệnh sau khi ra khỏi `with`; đọc giá trị bằng `viec.ngan.doc` nếu cần.

Không có lệnh xóa trong runtime. TC-Q06 chưa chốt thời hạn nên `dot_kiem`
**không đặt `giu_toi_da_ngay`**, không tự xóa dữ liệu hoặc nhật ký.
`sql/001_tao_dot_kiem.sql` chỉ `CREATE TABLE eng_e_tra_cuu.dot_kiem`, đủ bảy
cột hệ thống như mẫu. Core chạy migration khi cài, engine không chạy SQL.
`sql/kiem_ke.json` liệt kê bytes/SHA-256 **mọi tệp gói, trừ chính kiểm kê**.
`.gitattributes` giữ toàn gói LF; kiểm kê băm bytes thật, không chuẩn hóa lúc kiểm.

Ba tệp cổng tạm `KHAI-SDK-2.1.json`, `ngan.py`, `cau_hinh.py` đã chuyển vào
`e_tra_cuu/LUU-TRU/TC-S22/`, không xóa. Test không còn so băm hai mẫu NGAN-0.
README trước chuyển cũng được giữ tại đó để tra chi tiết seam lịch sử.

## Local AI và kiểm chứng

Bốn khuôn `phan_loai`, `phan_tich_cau_hoi`, `xep_hang_lai`, `soan_tra_loi`
gắn `$comment` theo `_chung/docs/LOAI-DU-LIEU-RIENG.md` §8:

- `ktt:ai12:metadata`: mã/nhãn/điểm/cờ/thời điểm Core; vẫn kiểm type/enum/const.
- `ktt:ai12:trich_xuat`: thực thể, tham số hàm, giá trị/đơn vị/tiền; vẫn cần căn cứ.
- `ktt:ai12:trich_dan`: object câu trích và offset Unicode nửa mở chính xác.
- `ktt:ai12:tong_hop`: câu trả lời tổng hợp; token số phải có căn cứ xác minh.

Annotation do engine tạo; không nhận quyền hạ chuẩn từ module/model. Tham số
hàm luôn trích xuất kể cả `$ref` nội bộ; không sửa schema nguồn của module.
Map từ ngữ cảnh AI về tệp gốc và từng offset được TC kiểm lại độc lập. `XONG`
ở Hỏi AI không chứng nhận đúng thực thể/trường/đơn vị hoặc quyền nguồn.
Xanh chỉ Python tầng 1 đủ điều kiện; LLM tối đa Vàng. Thiếu căn cứ trả câu
không số, `nhan=null`; mâu thuẫn giữ hai bên và chỉ đề nghị K5.

Trần: JSON chính 1 MiB, mỗi tệp/snapshot 20 MiB, tổng đọc 64 MiB; văn bản
500000 ký tự/60 trang; câu hỏi 4000; 100 hàm/1000 mục danh mục/50 ứng viên;
ngữ cảnh AI 100000 ký tự, khuôn 32 KiB, chuyển tiếp/hồ sơ 64 KiB. Vượt từ chối,
không cắt ngầm/batch/chuyển Cloud. Số token/context thật chưa đo.

## Cửa nguồn và màn hình còn cần Core

SDK 2.2.0 đã có ngăn/cấu hình; các cửa nguồn C-TC-02/03 vẫn chưa phải API SDK:
`app.cua_nguon.doc_quyen(viec_id)` chỉ là seam được tiêm từ phía chủ Core.
Nó phải xác thực request/task/pháp nhân/ngữ cảnh, map `tep` theo ID kèm metadata
và băm, map `nguon`, phong bì `dau_vao` xuyên bước, danh mục/hàm/hiệu lực/duyệt
và profile binding/ngưỡng trả lời. Runtime thiếu cửa trả `TC_CHUA_CO_CUA_CORE`;
không nhận cờ caller như chứng nhận Core. Test dùng adapter tệp con/quyền giả.

Hai ES module ở `ui/` giữ `KttCore.engine("e_tra_cuu")`; trạng thái chỉ đọc
`dot_kiem`, không gửi pháp nhân tự khai trong khóa/lọc, kiểm pháp nhân trả về.
Host Core phải gắn phạm vi/quyền mỗi truy vấn. Không cấp user quyền Admin toàn
engine. `giao_dien_quan_tri` vẫn bị bộ kiểm manifest SDK 2.2.0 từ chối; không
đưa vào `engine.json`. Khai UI dự kiến giữ trong bản lưu trữ; chưa kiểm nạp
màn, CAS cấu hình và phân quyền bằng KttCore/trình duyệt thật.

CoreGia 2.2.0 dùng cursor dạng offset, chưa ràng buộc cursor với bộ lọc/pháp nhân;
truy vấn vẫn lọc theo việc nên không đọc chéo pháp nhân. Test giữ kiểm cô lập,
không giả SDK đã từ chối cursor tái dùng. Cần Core xác nhận hành vi host thật.

## Kiểm tra

PowerShell, tại gốc worktree:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
.venv/Scripts/python -m pytest e_tra_cuu/tests -q --basetemp=.pytest-tmp
.venv/Scripts/python e_tra_cuu/tests/kiem_doc_lap.py
node --test e_tra_cuu/tests/ui/*.test.js
```

Linux đổi `.venv/Scripts/python` thành `.venv/bin/python`. Test không cần mạng,
Core thật hoặc thông tin máy thật. Ngăn dùng CoreGia 2.2.0 và `dat_cau_hinh`,
`gay_xung_dot_ngan`, `xem_ngan`, không `NganBoNho` riêng. Test tích hợp nạp
consumer Hỏi AI trong repo, lấy phiên bản từ manifest; Local giả, không Cloud.

CLI chuẩn giữ nguyên năm ví dụ và báo đúng **0/5, mã 1**; không hạ điều kiện
hoặc thay bằng harness. `tests/chay_demo_voi_core_gia.py` chỉ là hồi quy bổ sung
của nguồn/tệp con giả, không thay nghiệm thu. Kết quả lệnh thật và thời gian
TC-S22 ở `e_tra_cuu/docs/VIEC.md`. **Đã kiểm bằng Core giả (CoreGia)**;
chưa kiểm Core thật, Linux, RLS, trình duyệt thật hoặc chất lượng model.

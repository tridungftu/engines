> SDK25 (22/11/2026): công cụ dùng SDK 2.5.0 và `CoreGia.dat_cau_hinh`.
> Hai `.cmd` cài wheel SDK nội bộ và thư viện từ `goi/e_trich_xuat/wheels/`
> theo lock có SHA-256, hoàn toàn offline. Không tải hoặc đổi phiên bản thư viện.
> Các biên bản TX-6 cũ bên dưới là lịch sử; không chứng nhận máy/model thật.

# Công cụ TX-6 — T3 và N1, ngoài runtime engine

Mặc định **CHẠY KHÔ, Local giả, không mạng, 0 Cloud**. Chỉ người chạy cấp
`--that` **cùng** `--url` và đủ cấu hình mới được gọi Local thật. Codex không chạy
`--that`. Công cụ dùng discovery và transport của Hỏi AI (`chon_model`,
`ai_cuc_bo._gui_post`), giữ chặn proxy/redirect/nguồn Cloud và `ChuaRo`;
không sửa Hỏi AI hoặc để runtime Trích xuất gọi engine/nhà cung cấp.

## Chạy khô

Từ gốc repo, trên Windows:

```bat
e_trich_xuat\cong-cu\DO-SUC-CHUA-MODEL.cmd
e_trich_xuat\cong-cu\CHAY-N1-MOT-LAN.cmd
```

Hai `.cmd` ASCII tự tạo `.venv` nếu thiếu, cài wheel SDK 2.5.0 offline bằng
`--no-index --no-deps`. Nếu venv đã có nhưng thiếu SDK thì cài wheel theo
hướng dẫn SDK25 trước. Thư viện ngoài cài từ wheel và lock của gói, có `--require-hashes --only-binary :all: --no-deps`.
Trên Linux gọi cùng hai tệp `.py` bằng Python trong venv, với `-B`.

Thêm `--dau-ra <artifact.json>` để xuất biên bản; không ghi đè tệp đã có.
Nếu chỉ truyền `--url` thì vẫn chạy khô. Chạy khô thành công trả exit 0,
`trang_thai=chay_kho`, **không có kết luận T3/N1 đạt**. Mọi token/thời gian
runtime để `null`; context và ID có nhãn DEMO là cấu hình mô phỏng.
Số chấm từ Local giả không được dùng làm nền N1 thật.

N1 mặc định đọc bộ DEMO E6 đã được lead duyệt ở `tham-chieu/e6/chap-nhan.json`.
`--bo-demo <manifest.json>` cho phép chỉ rõ bộ DEMO đã ghim khác; mỗi nguồn
DOCX/đáp án/tham số phải nằm cùng thư mục, tên `DEMO-*`, đúng SHA bytes.
Không dò hồ sơ, đọc tệp cấu hình engine hoặc biến môi trường cấu hình.

**Lỗi checkout Windows:** Git `core.autocrlf=true` có thể đổi JSON LF thành
CRLF, khiến SHA bytes không khớp. Công cụ từ chối, không tự chuẩn hóa nguồn
để đạt. Lead khôi phục đúng blob LF/đóng gói đúng bytes trước kiểm mặc định.
Test TX-6 có staging riêng khôi phục đúng bytes LF đã ghim và kiểm lại SHA;
không sửa tham chiếu gốc, không thay kết quả kiểm E6 trên checkout thật.

## Cấu hình máy thật chỉ qua dòng lệnh

Mỗi `--model-spec` có tám mục ASCII, cách nhau bằng dấu phẩy:

```text
vai_tro,ID,context_hieu_dung,token_ra_toi_da,du_phong_boc,runtime,quantization,bam_bien_ban_runtime
```

`vai_tro` là `qwen3_8b`, `gpt_oss_20b`, `gemma`. T3 yêu cầu đúng ba ID riêng;
N1 chỉ chọn một ID khớp nền đã duyệt. ID phải trùng discovery và đúng họ/kích
thước được giao. **Không đoán thế hệ/kích thước/context Gemma.** Context là
context hiệu dụng đã nạp, lấy từ biên bản do lead/Anh xác minh, không phải
model card. Runtime cần ghi phiên bản, quantization ghi đúng cấu hình nạp;
thiếu số/băm biên bản thì từ chối. Không đưa URL/IP/path vào model-spec.

Chạy thật còn cần `--ngan-sach-trich <trần đã ghim>` (1.024–100.000), giống
cấu hình Trích xuất của nền. Không tự dùng giá trị mô phỏng 100.000 của
chạy khô làm cấu hình thật. Ngân sách bước trong fixture cũng phải nằm
trong trần này; khác nền hoặc vượt trần thì từ chối, không tự hạ ngầm.

Khung lệnh để **lead điền đầy đủ trước buổi Anh bấm**, không phải lệnh đã chạy:

```bat
e_trich_xuat\cong-cu\DO-SUC-CHUA-MODEL.cmd --that --url URL_ANH_CAP --ngan-sach-trich TRAN_DA_GHIM --model-spec "qwen3_8b,ID_QWEN,CONTEXT,RA,BOC,RUNTIME,QUANT,sha256:BAM_BIEN_BAN" --model-spec "gpt_oss_20b,ID_GPT_OSS,CONTEXT,RA,BOC,RUNTIME,QUANT,sha256:BAM_BIEN_BAN" --model-spec "gemma,ID_GEMMA,CONTEXT,RA,BOC,RUNTIME,QUANT,sha256:BAM_BIEN_BAN" --bien-ban-e6 E6.json --bien-ban-n1 N1.json --dau-ra T3.json
e_trich_xuat\cong-cu\CHAY-N1-MOT-LAN.cmd --that --url URL_ANH_CAP --ngan-sach-trich TRAN_DA_GHIM --model-spec "VAI_TRO,ID,CONTEXT,RA,BOC,RUNTIME,QUANT,sha256:BAM_BIEN_BAN" --nen NEN_N1.json --bam-nen sha256:BAM_NEN --dau-ra N1.json
```

`--model-json` là cách tương đương, dùng JSON trên dòng lệnh với các khóa
`vai_tro,id,context_hieu_dung,token_ra_toi_da,du_phong_boc,runtime,quantization,
bam_bien_ban_runtime`. Không đọc JSON cấu hình engine từ đĩa.

Discovery chỉ chứng minh ID đang khả dụng; công cụ không coi nó đã chứng minh
context. Trước mỗi POST, kiểm lại ID, đóng gói đúng system prompt/phần bọc
AI-2/khuôn, kiểm ngân sách context. Mặc định dùng **trần bảo thủ bytes UTF-8
toàn request + dự phòng phần bọc + ngân sách đầu ra**. Đây không phải token
đã đo. Trần này có thể từ chối tải mà tokenizer thực vẫn chứa được; không
được diễn giải thành model chắc chắn không chứa được DEMO-20/60.

Nếu có bộ đếm tokenizer đáng tin đã tính **sau chat template/phần bọc**, thêm
`token_vao_da_kiem` vào `--model-json`, ánh xạ **băm toàn body gửi** →
`{"so": <token thực>, "bam_bien_ban": "sha256:..."}`. Công cụ chỉ dùng số khi
băm body khớp; vẫn cộng dự phòng phần bọc và đầu ra. Chạy khô với cấu hình
người chạy để lấy `bam_than_gui`, cung cấp số đã kiểm qua dòng lệnh; không
dùng ký tự/4 thay tokenizer. Thay model/API/phần bọc/khuôn thì băm khác và
quay lại cổng bảo thủ. Thiếu context đã xác minh không được gửi.

## T3: chín tải/model, không mở batch trong engine

- Đúng toàn văn Phụ lục A TX-0: DEMO-1/20/60 lần lượt 2.227/78.246/238.286
  ký tự, khuôn đủ 37 mã. Khối phụ lục tổng hợp không phải số trang thật.
- Dùng `trich.chuan_bi@1` thật trên CoreGia có ngăn DEMO, rồi transport Local
  ngoài runtime, hậu kiểm TX-3 thật. Prompt/khuôn thực của TX-2 có thêm giao
  thức so với khối đếm lịch sử: báo **riêng** băm prompt/khuôn Phụ lục A và
  băm prompt/khuôn/body thực, không gán băm cũ cho nội dung mới.
- Báo băm bộ/prompt/tài liệu/khuôn/cấu hình; runtime/quantization/context do
  người chạy xác minh; token vào/ra/reasoning nguyên số runtime; giây thực;
  ô trả/37, ô có dẫn chứng hợp lệ/37, ô cần soát, từ chối/tràn/cắt.
  `completion_tokens`/`eval_count` được giữ nguyên; không tự trừ reasoning
  hoặc điền 0 khi API không tách reasoning. Thiếu số giữ `null`, chưa kiểm.
- Vượt ngân sách từ chối trước POST; không cắt toàn văn, giảm mã hay đổi
  Cloud. Một phản hồi/lượt, không tự sửa JSON/hỏi lại/batch. `ChuaRo` dừng
  toàn phép đo, giữ mã tương quan, không gửi lượt sau hoặc gửi lại mù.
- Mỗi tải chỉ đủ điều kiện khi đủ số runtime, 37 ô/37 căn cứ hợp lệ, không
  cần soát/cắt/tràn/từ chối, qua hậu kiểm và có E6/N1 thật khớp cấu hình.
  `pham_vi_du_dieu_kien` chỉ liệt kê tải/model đáp ứng; một N1 của model A
  không chứng minh model B. Biên bản E6 phải khớp băm manifest DEMO hiện tại.
  Không có biên bản thì T3 chưa đo/chưa đủ điều kiện; exit khác 0.
- Thất bại chỉ trình T3(b) batch **12–18 giờ** hoặc T3(c) nhiều bước
  **18–24 giờ công ước tính riêng**, chưa bao gồm Core/module/AI hay chờ máy;
  không tự mở các phương án đó.

## N1: một lần, không lựa kết quả đẹp

Nền phải có `chap_nhan_lead="đã duyệt"`, biên bản, đúng model/băm cấu hình,
băm bộ DEMO, từng DOCX/đáp án/tham số, prompt/tài liệu/khuôn/bộ và băm giá
trị cấu hình Trích xuất đã ghim trong hồ sơ. Mẫu
[`MAU-NEN-N1.json`](MAU-NEN-N1.json) **chưa có số**, luôn bị từ chối khi dùng
làm nền thật. Lead chuyển số nền đã được chấp nhận vào mẫu; không dùng đầu
ra mới hoặc số giả để tạo lại nền cho khớp.

Toàn bộ tập nguồn/ghim/ngân sách được kiểm trước POST đầu tiên. Trước gửi,
công cụ tạo độc quyền `N1-<băm nền>.da-nhan.json` cạnh nền, độc lập tên
`--dau-ra`. Giữ dấu cả khi lỗi/chưa rõ; không xóa/đổi thư mục nền để chạy lại.
Đây là dấu tại bộ artifact của người chạy, không là bảo đảm chống chạy lại
toàn hệ thống hoặc ngăn Core. Lead giữ một bản nền và dấu chuẩn cho đợt đo.

Giữ nguyên `compare` từ nguồn chấm `review-2026-10-15a/compare-gia-tri-v1`
và mẫu số `da_do`: thiếu đáp án hoặc giá trị → chưa đo, `dat/ty_le=null`.
Không đổi phép chứa chuỗi rộng của cách chấm cũ. Báo từng mã chỉ có số/cờ;
không xuất nội dung đáp án/hồ sơ. So đúng tập mã đã đo/mẫu số nền; giảm mẫu
số không được dùng để nâng tỷ lệ. Chưa đủ 37 mã đo, chưa qua hậu kiểm,
thiếu số runtime hoặc thấp hơn nền thì không đạt. N1 tách khỏi chín tải T3;
không lặp N1. Chưa có nền/biên bản thật: **N1 chưa kiểm**.

Artifact `--dau-ra` và dấu một lần là **artifact nghiệm thu của công cụ Anh
chạy**, không phải engine lưu cấu hình/sổ/đệm/kết quả trên máy. Engine không
thay đổi, vẫn chỉ dùng ngăn và kho tệp Core. **đã kiểm bằng Core giả (CoreGia)**
chỉ chứng minh đường ống giả, không chứng nhận quyền/lưu giữ/ACK Core thật.

## Kiểm môi trường

`tests/kiem_may_sach.cmd` hoặc `sh tests/kiem_may_sach.sh` tạo venv mới,
không `--system-site-packages`, cài SDK 2.5.0 đã kiểm SHA vào venv. Thư viện
được cài bằng lệnh offline của Core vào khu `.thu-vien` riêng qua lock có hash,
không có SDK trong lock. Tiến trình kiểm dùng `-I` để loại PYTHONPATH/user-site;
kiểm độc lập, hai công cụ khô và CLI chuẩn. CLI thiếu hồ sơ phụ vẫn trả
exit 1 (C-TX-06); cấu hình mặc định đã có từ SDK. Không cài pytest vào venv runtime. Bộ pytest/UI chạy riêng
trong venv kiểm theo `tests/requirements.lock`. Kiểm venv mới không đồng
nghĩa máy Windows OS sạch. Linux/CI dùng `TX25_KHO_WHEEL` hoặc `--kho-wheel` với kho wheel Linux và hash tương ứng trong lock; chỉ ghi đã kiểm sau lần chạy thật.

Exit: 0 cho chạy khô hoàn tất hoặc phạm vi thật đủ điều kiện; 1 cho đo/kiểm
không đạt; 2 cho thiếu số/nguồn/cấu hình/biên bản/chưa rõ. Artifact giữ trạng
thái riêng để không nhầm exit 0 chạy khô với nghiệm thu máy thật.

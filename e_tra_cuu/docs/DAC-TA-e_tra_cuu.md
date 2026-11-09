# 56 · Đặc tả engine Tra cứu tài liệu (`e_tra_cuu`) và Kho tài liệu của Core

*Bản chép ngày 08/11/2026 từ tài liệu Project `claude/56-dac-ta-engine-tra-cuu-tai-lieu.md` (lập 31/10/2026), dùng cho project engine riêng. Nếu hai bản khác nhau, bản trong Project là bản gốc.*

**Trạng thái:** bản nháp đặc tả để Anh duyệt, thuộc bộ chuẩn Core (cổng C, TL 55 §3). **Không lập trình trước khi Anh duyệt** (TL 54 §14 #2).

**Căn cứ:**
- Anh chốt trong phiên claude.ai ngày 31/10/2026, 13:02–13:51 (mục 1).
- TL 54 (Core · CSDL · API), TL 55 (chuẩn hóa Core, 5 engine, cổng, contract, cách gắn module), TL 53 (E-RAG, vùng dữ liệu module), TL 48 (cổng AI), TL 51 (M9 — kho hợp đồng vay và hỏi đáp), TL 37 (màn duyệt chung K5).

**Quy ước:**
- Mọi tên schema, bảng, route, capability là **đề xuất**, tiếng Việt không dấu, snake_case. Lead chốt sau G0.
- Chỗ chưa có căn cứ ghi **[CẦN ANH XÁC NHẬN]**. Câu hỏi gom ở mục 15.

**Bảo mật:** tài liệu không chứa dữ liệu thật. Số dung lượng ở mục 13 là ước tính theo giả định, chưa đo.

**Lưu ý khi đọc ở project engine (08/11):**
- Phần Kho tài liệu, `loi_tra_cuu`, các quy trình và route là **dịch vụ của Core**, phải đi qua cửa chung theo `..\..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.
- Project engine chỉ làm phần tính toán ở mục 9.

---

## 0. Kết luận

- **`e_tra_cuu` là engine thứ 6 của Core**, cùng chuẩn với 5 engine ở TL 55 §12.
  - Thay cho E-RAG (TL 53 §3) và phần M9-2 "cắt đoạn + chỉ mục + hỏi đáp" (TL 51 §7).
  - Mọi module dùng chung engine này. Không module nào tự làm RAG riêng.
- **Hỏi đáp theo 3 tầng, dừng ở tầng đủ căn cứ:**
  - Tầng 1: dữ liệu có cấu trúc đã duyệt (chủ yếu từ `e_trich_xuat`).
  - Tầng 2: tìm trong chỉ mục đoạn văn.
  - Tầng 3: trích xuất lại trên đúng tệp.
  - Câu trả lời luôn có trích dẫn và nhãn nguồn: Xanh = dữ liệu đã duyệt; Vàng = trích từ tệp, chưa duyệt.
- **Kho tài liệu do Core quản lý hoàn toàn.** Cây thư mục: pháp nhân → 8 nhóm nghiệp vụ → đối tượng → loại tài liệu. Người dùng chỉ nộp tệp vào hộp nhận, không sắp xếp.
- **Cache hỏi đáp:** mỗi lượt hỏi được lưu để dùng lại và tự hết hiệu lực khi dữ liệu nguồn thay đổi.
- **Đúng ranh giới Core:**
  - Engine không giữ dữ liệu, không có mật khẩu CSDL.
  - Kho, chỉ mục và cache do Core lưu (`loi_tai_lieu` mở rộng + schema mới `loi_tra_cuu`).
  - Chuỗi xử lý do Workflow Runner điều phối.
  - AI chỉ gọi qua `e_hoi_ai`; Cloud chỉ đi qua `e_mask`.
- **Dùng lại, không làm mới:**
  - Engine: `e_ocr`, `e_trich_xuat`, `e_hoi_ai`, `e_mask`.
  - Bảng: `tai_lieu`, `tep`, `ket_qua_xu_ly`.
  - Contract: `van_ban_tai_lieu.v1`, `tham_so.v1`, `tra_loi_ai.v1`…
  - Màn duyệt chung K5.

## 1. Anh đã chốt (31/10/2026)

| # | Giờ | Quyết định |
|---|---|---|
| 1 | 13:10 | Làm RAG thành **engine trong Core**, không gắn riêng một module |
| 2 | 13:10 | Khi hỏi, Local AI **ưu tiên dữ liệu từ engine trích xuất**; không thấy mới trích từ tệp để kiểm tra |
| 3 | 13:15 | **Mỗi lượt hỏi đáp được lưu kiểu cache** để các lần sau dùng lại |
| 4 | 13:15–13:16 | Dữ liệu phục vụ RAG tổ chức theo cấu trúc; **cấu trúc thư mục do hệ thống tạo trước, con người không sắp xếp** |
| 5 | 13:40–13:41 | Danh mục chia **trước hết theo pháp nhân, sau đó theo 8 nhóm nghiệp vụ**: 01 Pháp lý dự án · 02 Vay · 03 Mua hàng (không gồm xây dựng) · 04 Hợp đồng xây dựng · 05 Bán hàng · 06 Pháp lý công ty · 07 Nhân sự · 08 Quy chế khác |
| 6 | 13:44, 13:49 | 05 gồm cả bán nhựa và bán điện, ở trạng thái **chờ kích hoạt**: đã khai báo trong danh mục; tệp nộp vào trước khi kích hoạt nằm ở hàng chờ |
| 7 | 13:44 | Ranh giới 03/04 nằm chủ yếu ở **BOQ**: nhóm 03 không có BOQ hoặc BOQ đơn giản; nhóm 04 có BOQ và bản vẽ để xác định khối lượng |
| 8 | 13:47 | **Thiết bị kèm lắp đặt, sửa chữa bảo trì, vật tư chủ đầu tư tự mua → 04; thuê máy móc thiết bị → 03** |
| 9 | 13:47 | Hợp đồng đổi bản chất giữa chừng → **chuyển cả bộ sang nhóm mới, ghi nhật ký**. Trường hợp này ít |
| 10 | 13:44 | Quy chế liên quan **người lao động, phúc lợi, thưởng phạt người lao động → 07**; còn lại → 08 |
| 11 | 13:49–13:51 | 06 gồm hồ sơ đăng ký mở công ty, thay đổi ĐKKD, hồ sơ ĐHĐCĐ…; **có pháp nhân là công ty TNHH**; đồng ý các mục bổ sung (điều lệ, HĐQT, ban kiểm soát, cổ đông/vốn góp, giấy phép con, ủy quyền) |
| 12 | 13:50 | 08 là **phần còn lại**; không định sẵn thư mục con, bổ sung trong quá trình vận hành |
| 13 | 13:51 | Đặc tả phải dùng **SDK, API, CSDL chuẩn của Core** |
| 14 | bảng chọn sau khi nhận TL 56 | **QĐ-1** chỉ mục và cache do Core lưu · **QĐ-2** dữ liệu mới từ tầng 2–3 vào hàng chờ duyệt K5 · **QĐ-3** hộp nhận gồm web + thư mục trên máy chủ · **QĐ-4** không đối chiếu ngược tầng 1 với tệp |

## 2. Vị trí trong kiến trúc Core

| Thành phần | Trách nhiệm trong tính năng tra cứu |
|---|---|
| **Core — Kho tài liệu/tệp** (Document/File Store, TL 54 §9) | Hộp nhận, cây kho, đặt tên, phiên bản, hiệu lực, liên kết, quyền. Lưu tệp tại `D:\DU-LIEU-KE-TOAN\kho-file\` (TL 53 §8) |
| **Core — Database Manager** | Lưu đoạn văn, vector, chỉ mục từ khóa, cache trong `loi_tra_cuu`. **Truy vấn tìm kiếm chạy trong PostgreSQL với ngữ cảnh RLS của người hỏi**, nên quyền được lọc trước khi đoạn văn tới AI |
| **Core — Workflow Runner + Job Worker** | Chạy hai quy trình `nap_tai_lieu` (mục 3.4) và `hoi_dap` (mục 5) |
| **Core — Contract registry** | Đăng ký các **hàm tra cứu** mà module công bố cho tầng 1 (mục 12) |
| **Core — màn duyệt chung K5** (TL 37) | Thêm hai loại việc: *phân loại tài liệu* và *dữ liệu mới từ tra cứu chờ duyệt*; số đỏ trên icon |
| **`e_tra_cuu`** (engine mới) | Tính toán: phân loại tài liệu, cắt đoạn, phân tích câu hỏi, xếp hạng lại, soạn câu trả lời có trích dẫn. **Không đọc/ghi CSDL** |
| `e_ocr` | Tệp scan → `van_ban_tai_lieu.v1` |
| `e_trich_xuat` | Trích tham số theo mẫu của từng loại tài liệu (tầng 1 lúc nạp; tầng 3 lúc hỏi) |
| `e_hoi_ai` | Mọi lượt gọi model, kể cả tạo vector (mục 9.2); Local luôn có |
| `e_mask` | Che trước khi ra Cloud, mở che kết quả |
| **Module** (M9, M4, CRM, M2…) | Nhúng ô hỏi đáp của SDK JS, giới hạn phạm vi theo nhóm nghiệp vụ; khai báo hàm tra cứu trong `contract/` |

**Giao diện (đề xuất):**
- Core có icon **"Kho tài liệu"** ở cấp hệ thống, gồm: cây kho, hộp nhận, hàng chờ phân loại, hỏi đáp toàn kho theo quyền, quản trị danh mục (chỉ Admin).
- Module nhúng ô hỏi đáp với phạm vi riêng. Ví dụ: M9 nhúng với phạm vi nhóm 02-Vay và khóa chỉ Local.

**Anh chốt QĐ-1:** chỉ mục và cache do **Core lưu** (`loi_tra_cuu`); engine không giữ dữ liệu (TL 54 §2, TL 53 §7).

## 3. Kho tài liệu do hệ thống quản lý

### 3.1 Nguyên tắc
1. **Cấu trúc sinh từ danh mục trong CSDL:** pháp nhân, nhóm, loại, đối tượng, quy tắc đặt tên. Core tự tạo thư mục, kể cả khi có pháp nhân, dự án, hợp đồng mới.
2. **Người dùng chỉ có quyền đọc** kho. Chỉ Core được ghi, chuyển, đổi tên. Người dùng xem cây kho trên giao diện web; thư mục trên máy chủ là bản phản chiếu của cùng cây đó.
3. **Danh tính tệp là `tep_id` + mã băm, không phải đường dẫn.** Đổi cấu trúc, đổi tên, chuyển nhóm không làm hỏng trích dẫn và cache.
4. **Tên thư mục đối tượng dùng mã, không dùng tên:** mã pháp nhân, mã dự án, mã đối tượng Junsky (nhà cung cấp, khách hàng, ngân hàng), số hợp đồng, mã nhân viên. Như vậy ổn định và không lộ tên trên đường dẫn (Junsky cấp mã — TL 00).
5. **Mỗi tệp chỉ nằm một nơi** (nhóm nghiệp vụ chính). Liên quan nhóm khác thì dùng liên kết, không sao chép. Ví dụ: giấy chứng nhận quyền sử dụng đất nằm ở 01, liên kết sang 02 với vai trò tài sản đảm bảo.
6. **Muốn đổi cấu trúc thì sửa danh mục** (Admin). Core di chuyển tệp theo cấu trúc mới và ghi nhật ký.

### 3.2 Cây kho

Tên trong ngoặc nhọn là thư mục đối tượng sinh theo danh mục. Các loại chi tiết là đề xuất, chờ Anh duyệt.

```
D:\DU-LIEU-KE-TOAN\kho-file\kho-tai-lieu\
  <ma-phap-nhan>\
    01-phap-ly-du-an\<ma-du-an>\
        quy-hoach | chu-truong-dau-tu | dat-dai | thiet-ke-co-so
        | moi-truong | pccc | giay-phep-xay-dung | thoa-thuan-dau-noi
    02-vay\<ma-ngan-hang>\<ma-khoan-vay>\
        hop-dong-tin-dung | khe-uoc-nhan-no | the-chap-cam-co
        | tai-san-dam-bao | bao-lanh | phu-luc-sua-doi | thong-bao-lai-suat
    03-mua-hang\<ma-nha-cung-cap>\<so-hop-dong>\        (phân loại: tai-san | vat-tu | dich-vu | thue-may-moc)
        bao-gia-chon-ncc | hop-dong | phu-luc | ban-giao-nghiem-thu | thanh-ly
    04-hop-dong-xay-dung\<ma-du-an>\<so-hop-dong>\      (phân loại: thi-cong | tu-van | thiet-bi-lap-dat
                                                          | sua-chua-bao-tri | vat-tu-cdt-cap)
        hop-dong | phu-luc | boq-ban-ve | bao-lanh | nghiem-thu | thanh-toan | quyet-toan
    05-ban-hang\
        nha-o\<ma-du-an>\<so-hop-dong>\
        kcn\<ma-du-an>\<so-hop-dong>\
        ban-nhua\                                       [chờ kích hoạt]
        ban-dien\                                       [chờ kích hoạt]
            (mỗi hợp đồng: hop-dong | phu-luc | dat-coc | bien-ban-ban-giao | thanh-ly)
    06-phap-ly-cong-ty\
        dang-ky-thanh-lap | thay-doi-dkkd\<lan-thay-doi> | dieu-le
        | dai-hoi-dong-co-dong\<nam>\<thuong-nien|bat-thuong>   (công ty cổ phần)
        | hoi-dong-quan-tri\<nam> | ban-kiem-soat\<nam>          (công ty cổ phần)
        | hoi-dong-thanh-vien-chu-so-huu\<nam>                  (công ty TNHH)
        | co-dong-von-gop | giay-phep-con | uy-quyen-dai-dien
    07-nhan-su\
        quy-che | hop-dong-lao-dong\<ma-nhan-vien> | quyet-dinh
    08-quy-che-khac\        (không định sẵn thư mục con — mục 3.6)
```

- Nhóm 06 hiển thị nhánh theo **loại hình của pháp nhân** (cổ phần / TNHH), lấy từ hồ sơ pháp nhân trong `loi.phap_nhan`.

### 3.3 Quy tắc phân loại (engine kiểm theo thứ tự)

| Bước | Điều kiện | Kết quả |
|---|---|---|
| 1 | Xác định pháp nhân (bên ký, MST, con dấu…) | Không xác định được → hàng chờ |
| 2 | Tài liệu **phục vụ công trình**: thi công có BOQ/bản vẽ; tư vấn công trình (thiết kế, giám sát, khảo sát, thẩm tra, QLDA); thiết bị kèm lắp đặt; sửa chữa, bảo trì (không có ngưỡng giá trị); vật tư chủ đầu tư tự mua cấp cho công trình | Nhóm 04 |
| 3 | Mua tài sản, vật tư, dịch vụ không gắn công trình; **thuê máy móc thiết bị** (kể cả thiết bị thi công) | Nhóm 03 |
| 4 | Quy chế liên quan người lao động, phúc lợi, thưởng phạt người lao động | Nhóm 07; quy chế khác → 08 |
| 5 | Nhóm 01, 02, 05, 06 theo loại tài liệu nhận diện được | Nhóm tương ứng |
| 6 | Loại thuộc nhánh **chờ kích hoạt** (bán nhựa, bán điện) | Hàng chờ; khi Anh kích hoạt, Core tự xếp các tệp đang chờ |
| 7 | Không xác định được, hỗn hợp, hoặc độ tin cậy dưới ngưỡng | Hàng chờ phân loại |

- **Vật tư tự mua và sửa chữa, bảo trì thường không có BOQ.** Engine nhận diện chúng vào nhóm 04 dựa trên **thông tin công trình** trong tài liệu (tên dự án, hạng mục, địa điểm). Thiếu thông tin này thì vào hàng chờ, không đoán.
- **Đổi bản chất giữa chừng** (ví dụ hợp đồng nhóm 03 nhận phụ lục bổ sung BOQ và bản vẽ):
  - Engine gắn cờ và đưa vào hàng chờ.
  - Người duyệt xác nhận thì Core chuyển cả bộ hồ sơ (hợp đồng, phụ lục, chứng từ liên quan) sang nhóm mới, ghi nhật ký.
  - Không tự động hóa sâu hơn vì trường hợp này ít.
- **Nhóm 04 có hai mẫu trích xuất:**
  - Mẫu đầy đủ: BOQ, khối lượng thiết kế so với nghiệm thu, nối sang M4.
  - Mẫu rút gọn: hàng, đơn giá, số lượng, mã dự án; dùng cho vật tư tự mua và sửa chữa nhỏ.

### 3.4 Luồng nạp — quy trình `nap_tai_lieu`
1. **Hộp nhận là cửa vào duy nhất:**
   - tải lên qua giao diện web (`POST /api/v1/tai-lieu/hop-nhan`), và/hoặc
   - thư mục hộp nhận trên máy chủ, dùng để nạp hàng loạt.
   - **Anh chốt QĐ-3:** dùng cả hai cửa. Người dùng không có quyền ghi vào thư mục nào khác của kho.
2. **Tính mã băm.** Trùng tệp đã có thì báo trùng, không nạp lại.
3. **OCR nếu là bản scan:** gọi `e_ocr`, nhận `van_ban_tai_lieu.v1`, lưu thành biến thể `ocr` trong `ket_qua_xu_ly`.
4. **Phân loại:** gọi `tra_cuu.phan_loai_tai_lieu@1`, nhận `phan_loai_tai_lieu.v1` (pháp nhân, nhóm, loại, đối tượng, phiên bản/hiệu lực, độ tin cậy, trích dẫn căn cứ).
5. **Xếp kho:**
   - Đủ tin cậy: Core đặt tên, xếp vào cây, ghi `nhat_ky_xep_kho`, phát `tai_lieu.da_xep`.
   - Không đủ: đưa vào hàng chờ phân loại (K5). Người duyệt **chỉ chọn từ danh mục**, không gõ tự do.
6. **Cắt đoạn và lập chỉ mục:**
   - Gọi `tra_cuu.cat_doan@1`: cắt theo điều/khoản/bảng/trang, không cắt cố định theo số ký tự.
   - Gọi `ai.nhung_vector@1` qua `e_hoi_ai` (chỉ Local).
   - Core lưu vào `loi_tra_cuu.doan_van` và `vector_doan`.
7. **Trích xuất tham số** theo mẫu gắn với loại tài liệu (`e_trich_xuat`). Kết quả `tham_so.v1` ở trạng thái `needs_review` tới khi được duyệt.
8. **Phiên bản/hiệu lực:**
   - Phụ lục hoặc văn bản sửa đổi được đánh dấu **thay thế** điều khoản/tham số tương ứng của bản trước.
   - Bản cũ vẫn giữ để truy vết, nhưng tầng 1–2 mặc định chỉ dùng bản đang hiệu lực.

### 3.5 Đặt tên tệp
- Mẫu đề xuất: `<loai>_<so-hieu>_<ngay-ky yyyymmdd>_v<phien-ban>`, ví dụ `hop-dong-tin-dung_<so-hd>_20260115_v1`.
- Có thêm mã pháp nhân vào tên tệp không? Mã pháp nhân đã có ở cấp thư mục. [CẦN ANH XÁC NHẬN — trả lời sau]

### 3.6 Danh mục và quản trị
- **Trạng thái mỗi loại:** hoạt động / chờ kích hoạt / ngừng nhận mới. Ngừng thì không xóa và không chuyển tệp cũ.
- **Nhóm 08:**
  - Ban đầu tệp nằm thẳng trong `08-quy-che-khac\`.
  - Admin thêm loại mới trên giao diện. Core tạo thư mục con, chuyển tệp liên quan vào, ghi nhật ký.
  - Engine **gợi ý** loại mới khi thấy nhiều tệp cùng loại tích lũy; Admin duyệt mới tạo. Ngưỡng gợi ý: [CẦN ANH XÁC NHẬN — trả lời sau].
- Ai được sửa danh mục: chỉ Admin hệ thống, hay cả trưởng bộ phận với nhóm của mình? [CẦN ANH XÁC NHẬN — trả lời sau]

### 3.7 Phân quyền
- Quyền xét **theo pháp nhân trước, rồi theo nhóm nghiệp vụ**, qua ma trận thẩm quyền của Core. RLS áp trên `phap_nhan_id` + `ma_nhom` ở mọi bảng của kho và chỉ mục.
- **Nhóm 07 – Nhân sự** mặc định chỉ bộ phận nhân sự và người được chỉ định xem. Tra cứu và cache chịu cùng giới hạn.
- Đoạn văn người hỏi không có quyền **không bao giờ vào ngữ cảnh AI**, vì lọc ngay trong truy vấn PostgreSQL.

## 4. Bốn lớp dữ liệu và bảng Core tương ứng (dùng lại, không tạo kho thứ hai)

| Lớp | Nội dung | Nơi lưu |
|---|---|---|
| Gốc | Tệp nguyên bản, chỉ đọc | `loi_tai_lieu.tep` (biến thể `goc`) + kho tệp |
| Chuyển đổi | Văn bản sau OCR/chuyển đổi, theo trang | `loi_tai_lieu.ket_qua_xu_ly` (biến thể `ocr`, contract `van_ban_tai_lieu.v1`) |
| Chỉ mục | Đoạn văn + metadata + vector + chỉ mục từ khóa | `loi_tra_cuu.doan_van`, `loi_tra_cuu.vector_doan` (mới) |
| Trích xuất | Tham số có cấu trúc, trích dẫn, trạng thái duyệt | `loi_tai_lieu.ket_qua_xu_ly` (contract `tham_so.v1`) + dữ liệu module công bố (`cong_bo_<module>`) |

## 5. Hỏi đáp 3 tầng — quy trình `hoi_dap`

| Bước | Việc | Ai làm |
|---|---|---|
| 0 | **Tra cache** (mục 6). Trúng và còn hiệu lực → trả ngay, ghi "trả lời từ lần hỏi ngày…" | Core |
| 1 | **Phân tích câu hỏi:** ý định; thực thể (số hợp đồng, khoản vay, dự án, pháp nhân); có phụ thuộc thời điểm không; chọn hàm tra cứu tầng 1 và tham số | `tra_cuu.phan_tich_cau_hoi@1` (qua `e_hoi_ai`) |
| 2 | **Tầng 1 — dữ liệu có cấu trúc:** (a) hàm tra cứu module công bố, ví dụ lãi suất hiện hành từ snapshot Sheet của M9; (b) tham số `tham_so.v1` **đã duyệt** do `e_trich_xuat` tạo. Core chạy truy vấn chỉ đọc với RLS của người hỏi; **AI không viết SQL** | Core |
| 3 | **Tầng 2 — tìm trong chỉ mục:** tìm lai (vector + từ khóa), lọc quyền và hiệu lực ngay trong truy vấn; xếp hạng lại | Core + `tra_cuu.xep_hang_lai@1` |
| 4 | **Tầng 3 — trích lại trên tệp cụ thể:** chỉ chạy khi tầng 2 vẫn không chắc. Gọi `e_trich_xuat` với đúng trường cần tìm trên đúng tệp; trả **202 + `viec_id`** vì chậm hơn | Core → `e_trich_xuat` |
| 5 | **Soạn câu trả lời từ bằng chứng:** mỗi khẳng định gắn trích dẫn (tệp · trang · điều khoản · câu nguyên văn); tiền luôn kèm đơn vị | `tra_cuu.soan_tra_loi@1` |
| 6 | **Python kiểm:** trích dẫn có đúng nguyên văn trong nguồn; số trong câu trả lời có trong bằng chứng. Không đạt → hạ nhãn hoặc trả "không thấy căn cứ" | Core |
| 7 | **Lưu:** nhật ký lượt hỏi, cache; nếu có dữ liệu mới từ tầng 2–3 thì xử lý theo QĐ-2 | Core |

**"Không thấy thông tin" ở tầng 1** (chuyển xuống tầng 2) gồm:
- không có giá trị;
- có giá trị nhưng **chưa duyệt**;
- **độ tin cậy dưới ngưỡng**;
- giá trị thuộc **phiên bản hết hiệu lực**;
- câu hỏi nằm ngoài các trường đã trích (ví dụ hỏi về điều khoản phạt trả nợ trước hạn).

**Nhãn nguồn** (giữ quy tắc "kết quả có LLM tối đa Vàng", TL 48 §1.7):
- **Xanh:** trả lời hoàn toàn từ dữ liệu tầng 1 đã duyệt.
- **Vàng:** có dùng tầng 2–3, hoặc dữ liệu chưa duyệt.
- **"Không thấy căn cứ":** không trả lời bằng số, không đoán.

**Mâu thuẫn:** dữ liệu tầng 1 khác nội dung tệp đang hiệu lực (ví dụ phụ lục mới đổi lãi suất nhưng dữ liệu chưa cập nhật) → trả cả hai kèm cờ **"có mâu thuẫn"**, không tự chọn bên nào, và tạo việc chờ trong K5.

**Anh chốt QĐ-4: không đối chiếu ngược tầng 1 với tệp ở từng câu hỏi.**
- Câu trả lời tầng 1 dựa vào dữ liệu đã duyệt, vẫn kèm trích dẫn để người dùng tự mở kiểm.
- Biện pháp bù, chạy theo sự kiện lúc nạp tài liệu nên không tốn tài nguyên mỗi lượt hỏi:
  - Khi nạp văn bản **thay thế/sửa đổi** (phụ lục, văn bản điều chỉnh), Core gắn cờ **"có văn bản mới chờ duyệt"** cho tham số tầng 1 của bản cũ.
  - Câu trả lời dùng tham số đó hiện cảnh báo và hạ xuống **Vàng** tới khi tham số mới được duyệt.

**Anh chốt QĐ-2: dữ liệu mới tìm được ở tầng 2–3 vào hàng chờ duyệt K5.**
- Duyệt rồi mới thành dữ liệu tầng 1.
- Bị loại thì chỉ giữ dấu vết ngắn để truy vết.

## 6. Cache hỏi đáp

- **Khóa so khớp:** pháp nhân + câu hỏi chuẩn hóa + vector câu hỏi + **tập thực thể** (số hợp đồng, khoản vay, dự án…). Chỉ coi là trùng khi **thực thể khớp**, không chỉ giống nghĩa. Mục đích: "lãi suất khoản vay A" không nhận đáp án của khoản vay B.
- **Quyền:** chỉ dùng lại khi quyền của người hỏi **bao trùm toàn bộ nguồn** của câu trả lời đã cache.
- **Phụ thuộc nguồn:**
  - Mỗi câu trả lời lưu danh sách nguồn: `tep_id` + phiên bản, id `ket_qua_xu_ly`, hàm tra cứu + mốc dữ liệu.
  - Khi có sự kiện `tai_lieu.phien_ban_moi`, `tai_lieu.doi_nhom`, `ket_qua.da_duyet` hoặc `cong_bo.<module>.cap_nhat`, các câu trả lời phụ thuộc bị đánh dấu **hết hạn**.
- **Câu hỏi phụ thuộc thời điểm** ("hiện nay", "tháng này", "sắp đáo hạn"): không cache, hoặc cache ngắn hạn. Thời hạn: [CẦN ANH XÁC NHẬN — trả lời sau].
- **Minh bạch:** hiện "trả lời từ lần hỏi ngày…"; nút **"Tra lại từ đầu"** bỏ qua cache.
- **Chỉ lưu tham chiếu, không sao chép nội dung tài liệu:**
  - Lưu: câu hỏi, câu trả lời, tầng đã dùng, Local/Cloud, trích dẫn dạng mã.
  - Không lưu: bản sao đoạn văn, toàn bộ prompt.
- **Bộ câu hỏi mẫu:** cặp hỏi đáp người dùng xác nhận đúng có thể đưa vào bộ câu hỏi mẫu để đo chất lượng (mục 13). Việc đưa vào cần người duyệt.

## 7. Cổng AI và bảo mật

- Mọi lượt gọi model (phân tích câu hỏi, xếp hạng, soạn trả lời, phân loại, tạo vector) **chỉ qua `e_hoi_ai`**, có nhật ký (TL 48 §1.1).
- **Tạo vector luôn chạy Local** (`ai.nhung_vector@1`). Nội dung tài liệu không ra ngoài ở bước lập chỉ mục.
- **Cloud** chỉ dùng khi Local không chạy, Local không chắc, hoặc khi kiểm xác suất (TL 48 §1.5). **Bắt buộc qua `e_mask`** (không che số tiền và ngày).
- **Khóa theo module:**
  - M9 khóa **chỉ Local** (TL 51).
  - Mặc định cho các module khác: [CẦN ANH XÁC NHẬN — trả lời sau]. Đề xuất theo chính sách chung TL 48; riêng nhóm 07-Nhân sự chỉ Local.
- **Đo độ chính xác Local** theo hai loại việc mới `tra_cuu.phan_loai` và `tra_cuu.tra_loi`. Lịch giảm tỷ lệ kiểm theo TL 48 §1.6 (ngưỡng > 90%).
- **Nhật ký:** ai hỏi, lúc nào, pháp nhân, tầng, Local/Cloud, nguồn. Không ghi toàn văn tài liệu vào log (TL 54 §9).

## 8. CSDL (chuẩn TL 55 §1)

Quy ước cho mọi bảng:
- ID dạng UUID; mỗi bảng có `phap_nhan_id`; RLS theo ngữ cảnh đặt cho từng transaction.
- Thời điểm dùng `timestamptz`; bảng sửa đồng thời có `row_version`.
- Bảng nhật ký chỉ ghi thêm.
- Role chạy không phải chủ bảng, không có BYPASSRLS.
- Migration có phiên bản + checksum, nằm trong `loi*` (Core sở hữu).

**8.1 `loi_tai_lieu` — bổ sung**

| Bảng | Nội dung chính |
|---|---|
| `danh_muc_nhom_tai_lieu` | 8 nhóm: mã (01–08), tên, thứ tự, quyền mặc định |
| `danh_muc_loai_tai_lieu` | Loại chi tiết: nhóm, mã thư mục, trạng thái (hoat_dong / cho_kich_hoat / ngung_nhan_moi), mẫu trích xuất gắn kèm, quy tắc đặt tên, áp dụng cho loại hình pháp nhân (cổ phần/TNHH) |
| `cay_kho` | Nút thư mục sinh từ danh mục: pháp nhân, nhóm, đối tượng (mã), loại; đường dẫn tương đối |
| `vi_tri_tep` | `tep_id` ↔ nút `cay_kho`, tên chuẩn, hiệu lực từ–đến (đổi chỗ không đổi `tep_id`) |
| `quan_he_tai_lieu` | Thay thế / sửa đổi / phụ lục của / liên kết nhóm khác (một tệp nhiều vai trò) |
| `hop_nhan` | Lượt nộp: người nộp, kênh (web/thư mục), mã băm, trạng thái |
| `cho_phan_loai` | Đề xuất phân loại + độ tin cậy + lý do vào hàng chờ; quyết định của người duyệt |
| `nhat_ky_xep_kho` | Chỉ ghi thêm: xếp, chuyển, đổi tên, đổi nhóm, kích hoạt loại; trước/sau, người/engine, căn cứ |

**8.2 `loi_tra_cuu` — schema mới** (dựng lại được từ lớp Gốc + Chuyển đổi)

| Bảng | Nội dung chính |
|---|---|
| `doan_van` | `tep_id` + phiên bản, trang, vị trí, điều/khoản, loại khối (văn bản/bảng), nội dung, `ma_nhom`, hiệu lực |
| `vector_doan` | Vector của đoạn (pgvector), model + phiên bản model tạo vector |
| `chi_muc_tu_khoa` | Văn bản đã bỏ dấu + tsvector; pg_trgm để tìm số hiệu/mã. PostgreSQL không có sẵn bộ xử lý tiếng Việt |
| `luot_hoi` | Nhật ký lượt hỏi: người, pháp nhân, module gọi, phạm vi, tầng đã dùng, Local/Cloud, thời gian, nhãn, đánh giá của người dùng |
| `cache_tra_loi` | Câu hỏi chuẩn hóa, vector câu hỏi, thực thể, câu trả lời (`tra_loi_tra_cuu.v1`), hạn dùng, trạng thái hiệu lực |
| `cache_phu_thuoc` | Câu trả lời ↔ nguồn (để làm hết hạn theo sự kiện) |
| `bo_cau_hoi_mau` | Câu hỏi, đáp án, nguồn đúng, nhóm/loại; dùng đo chất lượng |

- **[Kiểm ở G0]:** PostgreSQL tại `D:\DU-LIEU-KE-TOAN` (Windows) có cài được **pgvector** và **unaccent/pg_trgm** không.
- Nếu không cài được pgvector: lead đề xuất phương án thay thế để Anh chọn. Không tự chuyển vector sang kho ngoài CSDL.

## 9. Engine `e_tra_cuu`

### 9.1 Capability

| Capability | Vào | Ra |
|---|---|---|
| `tra_cuu.phan_loai_tai_lieu@1` | `van_ban_tai_lieu.v1` + danh mục đang hoạt động (từ Core) | `phan_loai_tai_lieu.v1` |
| `tra_cuu.cat_doan@1` | `van_ban_tai_lieu.v1` (+ `du_lieu_bang.v1`) | danh sách `doan_van.v1` |
| `tra_cuu.phan_tich_cau_hoi@1` | `cau_hoi_tra_cuu.v1` + danh sách hàm tra cứu được phép | ý định, thực thể, hàm + tham số, cờ phụ thuộc thời điểm |
| `tra_cuu.xep_hang_lai@1` | câu hỏi + đoạn ứng viên | điểm xếp hạng |
| `tra_cuu.soan_tra_loi@1` | câu hỏi + bằng chứng (kết quả tầng 1 / đoạn) | `tra_loi_tra_cuu.v1` |

### 9.2 Bổ sung cho engine khác
- **`e_hoi_ai` thêm `ai.nhung_vector@1`, chỉ Local.** Model tạo vector phải hỗ trợ tốt tiếng Việt. Lead chọn ứng viên và **đo trên bộ câu hỏi mẫu trước khi chốt**. Tài liệu này không đưa con số so sánh khi chưa đo.
- **`e_trich_xuat` nhận thêm tham số "danh sách trường cần trích"** để phục vụ tầng 3 (trích có mục tiêu trên một tệp).

### 9.3 Vòng đời (chuẩn TL 55 §10, §12)
- Tiến trình riêng. Core giữ và nhả cổng. Tự kích hoạt khi cần, tự đóng khi rảnh. Ghi số đo khởi động.
- Chạy dưới tài khoản hạn chế. **Không giữ mật khẩu CSDL hay khóa.**
- Mọi đầu vào/đầu ra có contract JSON Schema; có adapter.
- Bộ test mẫu dùng dữ liệu giả, chạy độc lập.
- Trạng thái: stopped / starting / ready / busy / failed.

## 10. API (chuẩn TL 55 §2)

| Route | Việc |
|---|---|
| `POST /api/v1/tra-cuu/hoi` | Hỏi. Trả **200** nếu xong ngay (cache / tầng 1 / tầng 2), **202 + `viec_id`** nếu cần tầng 3. Đầu vào: câu hỏi, `phap_nhan_id`, phạm vi (nhóm/đối tượng, tùy chọn), module gọi, `bo_qua_cache` |
| `GET /api/v1/tra-cuu/luot/{id}` | Xem lượt hỏi và câu trả lời |
| `POST /api/v1/tra-cuu/luot/{id}/danh-gia` | Người dùng đánh giá đúng/sai (nguồn cho bộ câu hỏi mẫu) |
| `POST /api/v1/tai-lieu/hop-nhan` | Nộp tệp (multipart, khóa chống trùng) → 202 + `viec_id` |
| `GET /api/v1/tai-lieu/cay` | Cây kho theo quyền |
| `GET /api/v1/tai-lieu/cho-phan-loai` · `POST …/{id}/xep` | Hàng chờ; xếp bằng lựa chọn từ danh mục (`row_version` → 409 khi xung đột) |
| `GET/POST /api/v1/quan-tri/danh-muc-tai-lieu` | Thêm loại; kích hoạt / chờ kích hoạt / ngừng (Admin) |
| `POST /api/v1/quan-tri/tra-cuu/lap-lai-chi-muc` | Dựng lại chỉ mục (khi đổi model vector) → 202 |

- Lỗi theo chuẩn chung `{ma, thong_diep, request_id, thu_lai_duoc}`; có phân trang; JSON Schema cho mọi đầu vào/đầu ra.
- Các route được đưa vào **OpenAPI** của Core.

## 11. SDK, contract, sự kiện

- **SDK Python:**
  - Thêm nhóm `tra_cuu`: `hoi()`, `xem_luot()`.
  - Nhóm `tai_lieu` thêm `nop()`, `vi_tri()`, `quan_he()`.
  - Engine adapter dùng nhóm `engine` như mọi engine khác.
- **SDK JS:**
  - `KhungHoiDap`: ô hỏi, câu trả lời, nhãn Xanh/Vàng, trích dẫn bấm mở đúng trang, nút "Tra lại từ đầu", nút đánh giá; nhận tham số phạm vi và chế độ chỉ Local.
  - `CayKhoTaiLieu`, `HangChoPhanLoai`.
- **Contract** (TL 55 §11.3: dùng lại trước, chỉ mở rộng khi thiếu):
  - Dùng lại: `tham_chieu_tep.v1`, `van_ban_tai_lieu.v1`, `du_lieu_bang.v1`, `tham_so.v1`, `noi_dung_da_che.v1`, `tra_loi_ai.v1`.
  - Mới: `phan_loai_tai_lieu.v1`, `doan_van.v1`, `cau_hoi_tra_cuu.v1`, `tra_loi_tra_cuu.v1` (mở rộng `tra_loi_ai.v1` thêm: tầng, nhãn, cờ mâu thuẫn, từ cache, danh sách nguồn), `ham_tra_cuu.v1`.
  - Tất cả qua Anh duyệt trước khi kích hoạt (TL 55 §11.4).
- **Sự kiện (bus `su_kien`):**
  - Phát: `tai_lieu.da_nhan`, `tai_lieu.da_xep`, `tai_lieu.phien_ban_moi`, `tai_lieu.doi_nhom`, `tra_cuu.du_lieu_moi_cho_duyet`.
  - Nhận: `ket_qua.da_duyet`, `cong_bo.<module>.cap_nhat` (để làm hết hạn cache).

## 12. Module dùng engine thế nào

- **Khai báo hàm tra cứu:**
  - Module muốn dữ liệu của mình trả lời được ở tầng 1 thì khai báo hàm tra cứu (`ham_tra_cuu.v1`) trong thư mục `contract/` của gói.
  - Mỗi hàm gồm: tên, mô tả cho AI chọn hàm, tham số, contract đầu ra, quyền.
  - Core đăng ký hàm khi cài module. Hàm chỉ đọc khung nhìn `cong_bo_<module>`.
- **M9:**
  - Lát M9-1 (kho, tải lên, OCR) và M9-2 (chỉ mục, hỏi đáp) **chuyển sang dùng Kho tài liệu (nhóm 02) + `e_tra_cuu`**.
  - M9 giữ: snapshot Sheet, báo cáo lãi suất, màn riêng, khóa chỉ Local.
  - Các quyết định ở TL 51 §8 giữ nguyên.
- **M4:** hồ sơ nhóm 04 vào kho chung. Tham số BOQ/nghiệm thu qua `e_trich_xuat` (mẫu đầy đủ / rút gọn); M4 đọc kết quả đã duyệt.
- **CRM:** hợp đồng nhóm 05 vào kho chung; CRM công bố hàm tra cứu lịch thu và trạng thái hợp đồng.
- **M2:** hợp đồng nhóm 03 vào kho chung, dùng 5 danh mục tham số mua theo loại (TL 44).
- **Module chưa chạy:** kho và hỏi đáp tầng 2 vẫn hoạt động. Tầng 1 của module đó hiện "chờ" kèm lý do (TL 55 §13 #4).

## 13. Chất lượng, tải, dung lượng

- **Trước khi bật cho một nhóm tài liệu** phải có **bộ câu hỏi mẫu** kèm đáp án và nguồn đúng (giữ quy tắc "có đáp án mẫu trước khi bật").
- **Chỉ số đo** (gắn với ngưỡng > 90% của TL 48):
  - tỷ lệ trả lời đúng;
  - tỷ lệ trích dẫn đúng;
  - tỷ lệ "không thấy căn cứ" đúng (không bịa);
  - tỷ lệ phân loại đúng.
- **Tải:** thiết kế cho khoảng 150 người dùng, đỉnh khoảng 20 người đồng thời. Tầng 3 chạy qua hàng việc nền, không giữ yêu cầu trình duyệt.
- **Máy Local AI:** cấu hình (có GPU hay không) quyết định model tạo vector và model trả lời [CẦN ANH XÁC NHẬN — trả lời sau]. *Cập nhật 07/11: máy AI có GPU; model gpt-oss 20B, Qwen3 8B, Gemma.*
- **Dung lượng nhật ký và cache — ước tính theo giả định, chưa đo:**
  - Giả định khoảng 5 KB mỗi lượt (chỉ văn bản và tham chiếu).
  - Với 1.000 lượt/ngày: khoảng 5 MB/ngày, khoảng 1,8 GB/năm.
  - Đo thực tế sau khi chạy để thay giả định.
  - Thời hạn giữ nhật ký: [CẦN ANH XÁC NHẬN — trả lời sau]. Hết hạn thì chuyển lưu trữ, không xóa ngay.
- **Sao lưu:**
  - Tệp gốc và `loi_tai_lieu` bắt buộc sao lưu.
  - `loi_tra_cuu` dựng lại được nên có thể sao lưu thưa hơn [CẦN ANH XÁC NHẬN — trả lời sau].

## 14. Lát công việc (sau khi Anh duyệt cổng C; chưa ghi thời lượng vì chưa đo)

| Mã | Việc | Phụ thuộc |
|---|---|---|
| TC-0 | Khảo sát: pgvector/unaccent/pg_trgm trên PostgreSQL hiện có; cấu hình máy Local AI; chọn và đo model tạo vector | G0 |
| TC-1 | Danh mục 8 nhóm + loại, cây kho, hộp nhận, đặt tên, chống trùng, nhật ký xếp kho, hàng chờ phân loại trong K5 | Core G2 (Kho tài liệu) |
| TC-2 | `e_tra_cuu`: phân loại + cắt đoạn; `ai.nhung_vector@1`; quy trình `nap_tai_lieu` | TC-0, TC-1, `e_ocr`, `e_hoi_ai` |
| TC-3 | Hỏi đáp tầng 1–2: phân tích câu hỏi, hàm tra cứu, tìm lai, xếp hạng, soạn và kiểm trích dẫn | TC-2 |
| TC-4 | Tầng 3 + hàng chờ dữ liệu mới + cờ mâu thuẫn | TC-3, `e_trich_xuat` |
| TC-5 | Cache + làm hết hạn theo sự kiện | TC-3 |
| TC-6 | SDK JS (`KhungHoiDap`, `CayKhoTaiLieu`, `HangChoPhanLoai`), icon Kho tài liệu, nhúng vào M9; bộ câu hỏi mẫu nhóm 02 và đo chất lượng | TC-3 |
| TC-7 | Nạp hàng loạt tệp hiện có qua hộp nhận (nếu Anh chọn) | TC-2 |

Mỗi lát có test bằng dữ liệu giả. Dữ liệu thật chỉ dùng trong CSDL thật.

## 15. Cần Anh chốt

**Đã chốt qua bảng chọn ngày 31/10/2026:**

| Mã | Câu hỏi | Anh chốt |
|---|---|---|
| QĐ-1 | Chỉ mục và cache đặt ở đâu | **Core lưu** (`loi_tra_cuu`); engine không giữ dữ liệu |
| QĐ-2 | Dữ liệu mới tìm được ở tầng 2–3 | **Hàng chờ duyệt K5** |
| QĐ-3 | Cách đưa tệp vào hộp nhận | **Web + thư mục hộp nhận trên máy chủ** |
| QĐ-4 | Đối chiếu ngược tầng 1 với tệp | **Không đối chiếu** ở từng câu; bù bằng cờ "có văn bản mới chờ duyệt" khi nạp văn bản thay thế (mục 5) |

**Trả lời sau:**
1. Tên tệp có thêm mã pháp nhân không (mục 3.5).
2. Ai được sửa danh mục; ngưỡng để engine gợi ý loại mới ở nhóm 08 (mục 3.6).
3. Chính sách Cloud mặc định cho các module ngoài M9 (mục 7).
4. Thời hạn cache ngắn hạn cho câu hỏi phụ thuộc thời điểm; thời hạn giữ nhật ký hỏi đáp; tần suất sao lưu `loi_tra_cuu` (mục 6, 13).
5. Cấu hình máy Local AI (mục 13).
6. Danh sách loại chi tiết nhóm 01–07 ở mục 3.2 có cần thêm hay bớt.
7. "Bán điện" (chờ kích hoạt) có khác "điện năng" trong 4 loại hình doanh thu KCN của PLHN không, hay điện năng KCN xếp vào `05-ban-hang\kcn`.
8. Sửa chữa, bảo trì không gắn dự án đầu tư (ví dụ nhà xưởng đang vận hành) xếp dưới mã nào trong nhóm 04.
9. Tệp hiện đang để rải rác: có nạp hàng loạt qua hộp nhận không (TC-7); bản cũ chuyển vào lưu trữ, không xóa ngay.

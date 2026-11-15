# TC-11 — thử tra cứu DEMO ngoài runtime

**Phép đo thật CHỜ ANH TỰ CHẠY.** Bản này đã kiểm bằng Core giả (CoreGia) và
adapter giả; chưa có accuracy, model/ngưỡng được chốt hoặc bằng chứng tải thật.

Anh chạy từ workspace, không cần mạng ở chế độ mặc định:

```bat
e_tra_cuu\cong-cu\THU-TRA-CUU-THAT.cmd
```

Mặc định chỉ đọc đúng bộ TC-10 đã ghim SHA-256: câu hỏi/nguồn/đáp án DEMO,
không gọi provider, không dò máy, không đọc biến khóa/cấu hình máy và không
ghi tệp. Cấu hình engine vẫn ở `viec.cau_hinh`/ngăn Core. Bộ TC-10 chưa được
nghiệp vụ duyệt; phản hồi `local` giả và đáp án không được chuyển cho adapter.

Chỉ khi Anh muốn một artifact DEMO ngoài thư mục gói:

```bat
e_tra_cuu\cong-cu\THU-TRA-CUU-THAT.cmd --bao-cao e_tra_cuu\docs\TC11-DEMO.json --workspace .
```

Không ghi đè, không tạo thư mục, không ghi trong `goi/`, ngoài workspace hoặc
theo symlink ra ngoài. Artifact chỉ metadata/băm/số đo, không nguồn/câu hỏi/
đáp án/khóa/địa chỉ/đường máy. RAM là mặc định; seam gửi báo cáo cho Core khi
có adapter. Công cụ không tạo tệp tạm nên không có tệp cần dọn trong `finally`.

**Cửa `--that` hiện khóa:** SDK/API được giao chưa công bố hợp đồng discovery,
tokenizer trước gửi, ghép chuỗi và đọc đầy đủ kết quả đo qua cửa chung. Khi
Anh cấp đủ `--that --core <Core> --bo-demo <thu_muc> --bam-bo <SHA256>
--ghim <manifest_DEMO> --bam-ghim <SHA256>`, công cụ vẫn trả
`TC_CHUA_CO_MOI_TRUONG_THU` với câu Việt đúng phiếu, trước nhập khóa/gọi mạng.
Không có tùy chọn bỏ chốt hoặc nạp adapter Python từ CLI. Thiếu cửa này là
**C-TC-06**, không phải đã nối Core thật. Lead cần hoàn thiện adapter theo
[TC-11-ADAPTER.md](../docs/TC-11-ADAPTER.md) sau khi Core công bố hợp đồng;
không sửa Core/Hỏi AI trong lát này.

`--bo-demo` là bộ được lead/Anh cấp, cùng định dạng TC-10. `--bam-bo` ghim
bytes `bam-DEMO.json` từ kênh lead; mọi nguồn/đáp án phải khớp băm. `--ghim`
chỉ là biên bản **phiên bản + băm trên Core** của engine/danh mục/cấu hình/
bốn prompt; không chứa giá trị cấu hình, URL hoặc khóa. Trường và seam ghi ở
tài liệu adapter. Khóa không được nhận qua CLI/env/tệp/log. Bản này không cần
khóa vì chưa mở cửa thật; adapter tương lai nếu cần phải dùng nhập ẩn/handle
không lưu, không phản chiếu lỗi từ Core.

Báo cáo tách bốn tỷ lệ từng model (tử số/mẫu số/chưa đo), không cộng ba model
thành accuracy chung. Có bộ chấm bổ sung cắt đoạn/vị trí, câu hỏi/hàm và xếp
hạng; chưa có đáp án tương ứng trong bộ đầu vào thì để chưa đo. Tiền/ngày so
đúng thực thể/trường/đơn vị; số runtime thiếu là `null` kèm lý do. Thời gian
công cụ tính bằng giây riêng, không thay thời gian inference. Ký tự/4 không
phải token runtime. Context thiếu đếm đủ khung thì không gửi; quá trần từ chối.

Core/lead tự kiểm RLS/cache/ba tầng/K5/trích dẫn/UI, PostgreSQL và extension.
20 người đồng thời/150 người chỉ nhận biên bản bài tải riêng của Core. Không
kết nối CSDL, cài extension, chuyển Cloud, cắt ngầm hoặc tự mở batch. HTTP 202,
mất ACK hoặc nguồn đã nhận chưa trả dừng bằng `ChuaRo`; Core đối soát mã lượt
đang giữ trước khi Anh thử tiếp, công cụ không gửi lại mù. Ctrl+C dừng nộp mới;
không khẳng định đã hủy việc phía Core.

Exit: **0** chạy khô hợp lệ; **1** kết quả đo không đạt; **2** thiếu cửa/số đo/
đáp án/bằng chứng hoặc chưa rõ; **130** hủy. Exit 0 của chạy khô không chứng
nhận môi trường thật. Mọi kết quả thật cần lead review trước nghiệm thu.

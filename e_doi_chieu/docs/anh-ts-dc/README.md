# Ảnh TS-DC — DEMO, 21/11/2026

Đã kiểm bằng Core giả (CoreGia). Các ảnh chụp từ **màn JavaScript thật của
gói**, chạy trên Edge headless với cửa D2/KttCore giả trong RAM. Không
phải ảnh trong khung Core thật. Dữ liệu chỉ DEMO; băm `a…a` minh họa vị
trí chưa chứng minh khớp nguồn, không dùng cho việc nghiệp vụ thật.

| Tệp | Trạng thái để lead so với mẫu |
|---|---|
| `TS-DC-desktop.png` | Màn rộng 1.200 px, ô hai cột; có vùng bảo vệ DEMO |
| `TS-DC-mobile.png` | Màn hẹp 520 px, ô một cột, nút tự xuống dòng |
| `TS-DC-loi.png` | Nguyên văn rỗng, lỗi ngay cạnh ô và thông báo phía dưới |
| `TS-DC-cas.png` | Giả lập 409, giữ nội dung và khóa áp dụng tới khi tải lại |

HTML tự chứa theo từng trạng thái: `DEMO-rong.html`, `DEMO-vung.html`,
`DEMO-loi.html`, `DEMO-cas.html`. Dựng lại từ thư mục gốc repo:

```powershell
node e_doi_chieu/tests/ui/dung_anh_ts_dc.mjs
```

Có thể mở HTML bằng browser để xem và chụp lại. Trên môi trường kiểm này,
Chrome headless lỗi khởi động; cửa browser tương tác timeout hai lần.
Edge headless với profile DEMO riêng trong worktree chạy được khi dùng
renderer/GPU trong cùng tiến trình và tắt sandbox của **tiến trình kiểm
tạm**; không sửa Windows/browser security settings của người dùng.
Màn không gọi mạng; harness cũng thay các API mạng bằng hàm từ chối.

Ví dụ chụp trên máy dev đã được cấu hình cho browser headless (thay các
placeholder bằng đường tuyệt đối thuộc worktree, không dùng profile thật):

```text
msedge.exe --headless --disable-gpu --no-first-run --disable-background-networking --disable-component-update --disable-sync --user-data-dir=<profile-DEMO-tam> --window-size=1200,1850 --virtual-time-budget=4000 --screenshot=<anh-PNG> file:///<HTML-DEMO>
```

Chỉ ảnh/harness thuộc hồ sơ bàn giao; profile browser thử được giữ trong
vùng tạm bị git bỏ qua, không đưa vào gói hay PR. Không có bí mật, máy
AI hoặc thao tác kết nối trong lát này. Danh sách quy tắc cứng/cặp đổi
nghĩa là chỉ đọc vì lõi hiện tại cố định chúng trong Python; cần lead xác
nhận điểm lệch này so với diễn đạt của phiếu TS-DC.

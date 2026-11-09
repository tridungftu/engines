# CHANGELOG — e_hoa_don

## Chưa phát hành — G3-GOI-26, 06/11/2026

- Cập nhật README theo nguồn Node nội bộ đã gộp, bộ đọc/ánh xạ trong gói và
  helper SDK từ các lát 22–25; giữ capability XML và các phiên bản hiện có.
- Bổ sung SHA nguồn hiện tại (LF/CRLF), môi trường kiểm, hướng dẫn regression
  thuần và quay về bản ghim qua drain/ACK. Giữ nguyên quyền dùng CD-096 A1,
  SHA vendor và Node lock/integrity của lát 25.
- Thêm `requirements.lock` ở trạng thái CHUA_KIEM, chỉ ghi điều kiện chờ SDK
  cuối G3-GOI-34; chưa có dòng cài đặt hoặc pin SDK 1.4.1 candidate. Ghim Python
  và mã băm toàn gói phát hành còn chờ lead, không tăng version SDK/engine.
- Ghi rõ hai import ngoài SDK, packaging Python chưa hoàn tất và kiểm Windows/
  Chromium thật còn thiếu; test trong repo chưa chứng minh wheel độc lập.

## Các mốc đã gộp — G3-GOI-22 đến 25, 06/11/2026

- G3-GOI-22: đưa reader XML/ZIP vào `lib/hoa_don_xml.py`, hai import qua SDK;
  giữ bridge legacy cùng object, `Issue` và `__module__` để hash không đổi.
- G3-GOI-23: tách ánh xạ trạng thái vào `lib/trang_thai.py`; adapter cũ tái xuất
  cùng object, `doc.py`/`tai.py` dùng thư viện nội bộ.
- G3-GOI-24: `chay.py`/`phien.py` dùng helper SDK; giữ ngoại lệ `env_con` và
  `kiem_tra_tien_trinh`; thiếu kiểm môi trường thật vẫn CHUA_KIEM.
- G3-GOI-25: đóng gói `vendor/build.js`, `vendor/config.js`, `package.json`,
  `package-lock.json`; nạp tương đối, kiểm SHA trước require, test closure trong
  RAM. Không đổi thuật toán, chưa đưa job/portal thật vào gói.

## 0.1.0-demo.1 (G3-GOI-21, 05/11/2026)
- Chuyển nguyên trạng `bang_ke.cjs`, `chay.py`, `doc.py`, `phien.py`, `portal.cjs`, `tai.py`, `engine.json` từ `src/kho_tri_thuc/engines/e_hoa_don/` sang `engines/e_hoa_don/` (git mv, không đổi nội dung).
- Thêm shim namespace tại đường cũ, `__init__.py` marker, `contract/schemas.json`, `contract/vi_du.json`, tài liệu và test độc lập.
- Không giữ CJS wrapper tại đường cũ; test Node trỏ thẳng `engines/e_hoa_don/`.

"""Máy Local AI DEMO trên loopback; dùng chung cho pytest và lệnh SDK thu."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

TAI_LIEU = (
    "DEMO — Hợp đồng DEMO-001 của Công ty DEMO Ánh Dương. "
    "Số tiền thanh toán là 1.000.000 VND. Ngày thanh toán là 30/10/2026."
)
TRICH_TIEN = "Số tiền thanh toán là 1.000.000 VND."
TRICH_NGAY = "Ngày thanh toán là 30/10/2026."
TRA_LOI = {"truong": [
    {"ten": "so_tien", "gia_tri": "1.000.000 VND", "trich_dan": TRICH_TIEN},
    {"ten": "ngay", "gia_tri": "30/10/2026", "trich_dan": TRICH_NGAY},
]}


class LocalGia:
    def __init__(self, tra_loi=None):
        self.tra_loi = TRA_LOI if tra_loi is None else tra_loi
        self.tra_loi_tung_luot = []
        self.models = [{"id": "model-demo", "owned_by": "local-demo"}]
        self.tags = None
        self.yeu_cau = []
        self.luot = []
        self.khi_nhan = lambda phuong_thuc, duong: None
        self.ma_http = 200
        self.phan_hoi_tho = None
        self.chuyen_huong = None
        self.may_chu = None

    @property
    def url(self):
        return f"http://127.0.0.1:{self.may_chu.server_address[1]}"

    @property
    def so_luot_hoi(self):
        return len(self.yeu_cau)

    def __enter__(self):
        chu = self

        class XuLy(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def tra(self, ma, du_lieu):
                raw = json.dumps(du_lieu, ensure_ascii=False).encode("utf-8")
                self.tra_tho(ma, raw)

            def tra_tho(self, ma, raw):
                self.send_response(ma)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    pass

            def chuyen(self):
                if chu.chuyen_huong and self.path == chu.chuyen_huong[0]:
                    self.send_response(chu.chuyen_huong[1])
                    self.send_header("Location", "http://cloud.demo.invalid:12345/khong-duoc-goi")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return True
                return False

            def do_GET(self):
                chu.luot.append(("GET", self.path))
                chu.khi_nhan("GET", self.path)
                if self.chuyen():
                    return
                if self.path == "/v1/models":
                    self.tra(200, {"data": chu.models})
                elif self.path == "/api/tags" and chu.tags is not None:
                    self.tra(200, {"models": chu.tags})
                else:
                    self.tra(404, {"error": "Đường dẫn DEMO không có."})

            def do_POST(self):
                chu.luot.append(("POST", self.path))
                than = self.rfile.read(int(self.headers["Content-Length"]))
                chu.yeu_cau.append(json.loads(than))
                chu.khi_nhan("POST", self.path)
                if self.chuyen():
                    return
                if chu.phan_hoi_tho is not None:
                    self.tra_tho(chu.ma_http, chu.phan_hoi_tho)
                    return
                tra_loi = chu.tra_loi_tung_luot.pop(0) if chu.tra_loi_tung_luot else chu.tra_loi
                noi_dung = tra_loi if isinstance(tra_loi, str) else json.dumps(tra_loi, ensure_ascii=False)
                self.tra(chu.ma_http, {"message": {"content": noi_dung}} if self.path == "/api/chat"
                         else {"choices": [{"message": {"content": noi_dung}}]})

        self.may_chu = ThreadingHTTPServer(("127.0.0.1", 0), XuLy)
        self.luong = threading.Thread(target=self.may_chu.serve_forever,
                                      kwargs={"poll_interval": 0.01}, daemon=True)
        self.luong.start()
        return self

    def __exit__(self, *args):
        self.may_chu.shutdown()
        self.may_chu.server_close()
        self.luong.join(timeout=5)


def ghi_cau_hinh(thu_muc, url, *, thoi_han=2, quy_tac=None):
    tep = Path(thu_muc) / "cau_hinh_DEMO.json"
    tep.write_text(json.dumps({
        "local_ai": {"url": url, "timeout_giay": thoi_han},
        "quy_tac_model": quy_tac if quy_tac is not None else [
            {"mau_ma_prompt": "demo.*", "uu_tien": "model-demo", "du_phong": []}
        ],
    }), encoding="utf-8")
    return tep

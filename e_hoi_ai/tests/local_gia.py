"""Máy Local AI DEMO trên loopback; dùng chung cho pytest và lệnh SDK thu."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import socket

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
        self.models = [{"id": "model-demo", "owned_by": "local-demo", "context_length": 65536}]
        self.tags = None
        self.dang_chay = [{"name": "model-demo", "context_length": 65536}]
        self.native_v1 = None
        self.native_v0 = None
        self.phan_hoi_get = {}
        self.yeu_cau = []
        self.luot = []
        self.khi_nhan = lambda phuong_thuc, duong: None
        self.ma_http = 200
        self.phan_hoi_tho = None
        self.sua_phong_bi = {}
        self.cat_sau_post = False
        self.cat_than_sau_post = False
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
                if chu.cat_than_sau_post and self.command == "POST":
                    raw = raw[:len(raw) // 2]
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
                if self.path in chu.phan_hoi_get:
                    ma, raw = chu.phan_hoi_get[self.path]
                    self.tra_tho(ma, raw)
                elif self.path == "/api/v1/models" and chu.native_v1 is not None:
                    self.tra(200, {"models": chu.native_v1})
                elif self.path == "/api/v0/models" and chu.native_v0 is not None:
                    self.tra(200, {"data": chu.native_v0})
                elif self.path == "/v1/models":
                    self.tra(200, {"data": chu.models})
                elif self.path == "/api/tags" and chu.tags is not None:
                    self.tra(200, {"models": chu.tags})
                elif self.path == "/api/ps":
                    self.tra(200, {"models": chu.dang_chay})
                else:
                    self.tra(404, {"error": "Đường dẫn DEMO không có."})

            def do_POST(self):
                chu.luot.append(("POST", self.path))
                than = self.rfile.read(int(self.headers["Content-Length"]))
                chu.yeu_cau.append(json.loads(than))
                chu.khi_nhan("POST", self.path)
                if chu.cat_sau_post:
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                if self.chuyen():
                    return
                if chu.phan_hoi_tho is not None:
                    self.tra_tho(chu.ma_http, chu.phan_hoi_tho)
                    return
                tra_loi = chu.tra_loi_tung_luot.pop(0) if chu.tra_loi_tung_luot else chu.tra_loi
                noi_dung = tra_loi if isinstance(tra_loi, str) else json.dumps(tra_loi, ensure_ascii=False)
                phong_bi = ({"message": {"content": noi_dung}, "done": True, "done_reason": "stop"}
                           if self.path == "/api/chat" else
                           {"choices": [{"message": {"content": noi_dung}, "finish_reason": "stop"}]})
                self.tra(chu.ma_http, {**phong_bi, **chu.sua_phong_bi})

        self.may_chu = ThreadingHTTPServer(("127.0.0.1", 0), XuLy)
        self.luong = threading.Thread(target=self.may_chu.serve_forever,
                                      kwargs={"poll_interval": 0.01}, daemon=True)
        self.luong.start()
        return self

    def __exit__(self, *args):
        self.may_chu.shutdown()
        self.may_chu.server_close()
        self.luong.join(timeout=5)


_CORE_DEMO = None


def core_demo():
    """CoreGia chính thức dùng chung trong một ca; fixture tạo mới giữa các ca."""
    global _CORE_DEMO
    if _CORE_DEMO is None:
        from kho_tri_thuc_sdk.thu import CoreGia
        from e_hoi_ai.chay import app
        _CORE_DEMO = CoreGia(app)
    return _CORE_DEMO


def nap_cau_hinh(url, *, thoi_han=2, quy_tac=None, core=None):
    """Nạp DEMO qua cấu hình chính thức của SDK, không tạo tệp hay bảng cấu hình."""
    from e_hoi_ai.chay import app
    gia_tri = {
        "local_ai": {"url": url, "timeout_giay": thoi_han},
        "quy_tac_model": quy_tac if quy_tac is not None else [
            {"mau_ma_prompt": "demo.*", "uu_tien": "model-demo", "du_phong": []}
        ],
    }
    (core or core_demo()).dat_cau_hinh(app.ma, gia_tri)
    return gia_tri

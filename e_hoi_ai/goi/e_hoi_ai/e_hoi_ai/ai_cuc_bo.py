"""Lõi HTTP từ ma-nguon/lib/ai_cuc_bo.py, chỉ gọi máy Local bằng IP.

Giữ kiểm mạng, nguồn Tailscale, socket IP trực tiếp, chặn proxy/redirect và
kiểm metadata model trước khi gửi nội dung. Không dùng kênh engine cũ.
"""
import http.client
import ipaddress
import json
import socket
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from .dto import MA_MODEL

MANG_TAILSCALE = tuple(ipaddress.ip_network(n) for n in (
    "100.64.0.0/10", "fd7a:115c:a1e0::/48",
))
MANG_CHO_PHEP = tuple(ipaddress.ip_network(n) for n in (
    "127.0.0.0/8", "::1/128", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
)) + MANG_TAILSCALE
GIOI_HAN_PHAN_HOI = 2_000_000


class LocalAIKhongSanSang(ValueError):
    """Lỗi an toàn, không chứa địa chỉ, nội dung phản hồi hoặc cấu hình."""


def kiem_url(url):
    """Nhận địa chỉ gốc, /v1 hoặc endpoint đầy đủ; không phân giải tên miền."""
    try:
        if not isinstance(url, str) or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
            raise ValueError
        parsed = urlsplit(url)
        if (parsed.scheme != "http" or not parsed.port or parsed.username is not None
                or parsed.password is not None or parsed.query or parsed.fragment
                or parsed.path not in ("", "/", "/v1", "/v1/", "/v1/chat/completions")
                or "%" in (parsed.hostname or "")):
            raise ValueError
        if parsed.hostname == "localhost":
            parsed = parsed._replace(netloc=f"127.0.0.1:{parsed.port}")
        dia_chi = ipaddress.ip_address(parsed.hostname or "")
        if not any(dia_chi in mang for mang in MANG_CHO_PHEP):
            raise ValueError
        return parsed._replace(path="/v1/chat/completions")
    except ValueError:
        raise LocalAIKhongSanSang("Địa chỉ Local AI không hợp lệ hoặc không thuộc mạng cho phép.") from None


def la_tailscale(host):
    return any(ipaddress.ip_address(host) in mang for mang in MANG_TAILSCALE)


def ip_nguon(host, port):
    """UDP connect chỉ hỏi đường đi của hệ điều hành, không gửi dữ liệu."""
    loai = socket.AF_INET6 if ":" in host else socket.AF_INET
    with socket.socket(loai, socket.SOCK_DGRAM) as thu:
        thu.connect((host, port))
        return thu.getsockname()[0]


def nguon_tailscale(host, port):
    if not la_tailscale(host):
        return None
    nguon = ip_nguon(host, port)
    if not la_tailscale(nguon):
        raise LocalAIKhongSanSang("Kết nối tới máy AI chưa đi qua Tailscale.")
    return nguon


def model_tu_xa(muc):
    return bool(muc.get("remote_host") or muc.get("remote_model") or any(
        "cloud" in str(muc.get(k) or "").casefold() for k in ("id", "name", "model")
    ))


class _KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _KetNoiIP(http.client.HTTPConnection):
    def __init__(self, host, *, nguon=None, **kwargs):
        super().__init__(host, **kwargs)
        self._nguon = nguon

    def connect(self):
        loai = socket.AF_INET6 if ":" in self.host else socket.AF_INET
        ket_noi = socket.socket(loai, socket.SOCK_STREAM)
        try:
            ket_noi.settimeout(self.timeout)
            if self._nguon:
                ket_noi.bind((self._nguon, 0))
            ket_noi.connect((self.host, self.port))
        except Exception:
            ket_noi.close()
            raise
        self.sock = ket_noi


class _MoHTTPBangIP(urllib.request.HTTPHandler):
    def __init__(self, nguon):
        super().__init__()
        self._nguon = nguon

    def http_open(self, req):
        return self.do_open(lambda host, **kw: _KetNoiIP(host, nguon=self._nguon, **kw), req)


def _doc_json(bo_mo, url, thoi_han, than=None):
    yeu_cau = urllib.request.Request(url, data=than, headers={"Content-Type": "application/json"})
    with bo_mo.open(yeu_cau, timeout=thoi_han) as phan_hoi:
        raw = phan_hoi.read(GIOI_HAN_PHAN_HOI + 1)
    if len(raw) > GIOI_HAN_PHAN_HOI:
        raise LocalAIKhongSanSang("Phản hồi Local AI vượt giới hạn cho phép.")
    text = raw.decode("utf-8")
    # Giữ trần độ sâu JSON của lõi cũ trước khi đưa vào json.loads.
    do_sau = 0
    trong_chuoi = thoat = False
    for ky_tu in text:
        if trong_chuoi:
            if thoat:
                thoat = False
            elif ky_tu == "\\":
                thoat = True
            elif ky_tu == '"':
                trong_chuoi = False
        elif ky_tu == '"':
            trong_chuoi = True
        elif ky_tu in "[{":
            do_sau += 1
            if do_sau > 64:
                raise LocalAIKhongSanSang("Phản hồi Local AI không hợp lệ.")
        elif ky_tu in "]}":
            do_sau -= 1
    return json.loads(text)


def _kiem_model(bo_mo, goc, model, thoi_han, kiem_huy):
    metadata = _doc_json(bo_mo, goc + "/v1/models", thoi_han)
    cac_model = metadata.get("data") if isinstance(metadata, dict) else None
    if not isinstance(cac_model, list):
        raise LocalAIKhongSanSang("Chưa đọc được danh sách model Local AI.")
    muc = next((m for m in cac_model if isinstance(m, dict)
                and str(m.get("id") or "").removesuffix(":latest") == model.removesuffix(":latest")), None)
    if (muc is None or model_tu_xa(muc) or muc.get("state") == "not-loaded"
            or ("loaded_instances" in muc and not muc["loaded_instances"])):
        raise LocalAIKhongSanSang("Model đã chọn chưa sẵn sàng trên máy Local AI.")
    kiem_huy()
    # Ollama có thể giấu remote_host ở /v1/models; kiểm thêm /api/tags như mã cũ.
    try:
        tags = _doc_json(bo_mo, goc + "/api/tags", thoi_han)
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code in (404, 405):
            return
        raise
    cac_model = tags.get("models") if isinstance(tags, dict) else None
    if not isinstance(cac_model, list):
        return
    muc = next((m for m in cac_model if isinstance(m, dict) and any(
        str(m.get(k) or "").removesuffix(":latest") == model.removesuffix(":latest")
        for k in ("name", "model"))), None)
    if muc is None or model_tu_xa(muc):
        raise LocalAIKhongSanSang("Không xác minh được model chạy cục bộ trên máy AI.")


def hoi_local(cau_hinh, model, prompt, *, kiem_huy=lambda: None):
    """Một lượt OpenAI-compatible; không thử lại POST hay chuyển nhà cung cấp."""
    try:
        parsed = kiem_url(cau_hinh["url"])
        if not MA_MODEL.fullmatch(model) or model_tu_xa({"model": model}):
            raise LocalAIKhongSanSang("Tên model Local AI không hợp lệ.")
        nguon = nguon_tailscale(parsed.hostname, parsed.port)
        bo_mo = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), _KhongChuyenHuong(), _MoHTTPBangIP(nguon)
        )
        goc = parsed._replace(path="").geturl()
        thoi_han = cau_hinh["timeout_giay"]
        kiem_huy()
        _kiem_model(bo_mo, goc, model, thoi_han, kiem_huy)
        kiem_huy()  # Hủy trong lúc đọc metadata thì không gửi prompt/tài liệu.
        than = json.dumps({"model": model, "temperature": 0, "stream": False, "messages": [
            {"role": "system", "content": "Bạn là trợ lý kế toán. Chỉ trả lời đúng định dạng được yêu cầu."},
            {"role": "user", "content": prompt},
        ]}, ensure_ascii=False).encode("utf-8")
        phan_hoi = _doc_json(bo_mo, parsed.geturl(), thoi_han, than)
        noi_dung = phan_hoi["choices"][0]["message"]["content"]
        if not isinstance(noi_dung, str) or not noi_dung.strip():
            raise LocalAIKhongSanSang("Máy Local AI chưa trả được câu trả lời.")
        return noi_dung
    except urllib.error.HTTPError as exc:
        exc.close()
        raise LocalAIKhongSanSang("Máy Local AI chưa sẵn sàng. Hãy thử lại.") from None
    except (ValueError, OSError, http.client.HTTPException, KeyError, IndexError, TypeError,
            RecursionError, OverflowError):
        raise LocalAIKhongSanSang("Máy Local AI chưa sẵn sàng. Hãy thử lại.") from None

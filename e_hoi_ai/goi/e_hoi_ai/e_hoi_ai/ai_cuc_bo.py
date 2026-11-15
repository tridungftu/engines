"""Lõi HTTP từ ma-nguon/lib/ai_cuc_bo.py, chỉ gọi máy Local bằng IP.

Giữ kiểm mạng, nguồn Tailscale, socket IP trực tiếp, chặn proxy/redirect và
kiểm metadata model trước khi gửi nội dung. Không dùng kênh engine cũ.
"""
import http.client
import ipaddress
import socket
import urllib.error
import urllib.request
import uuid
from urllib.parse import urlsplit

from kho_tri_thuc_sdk.engine import ChuaRo, LoiNghiepVu

from .dto import MA_MODEL
from .khuon_json import doc_json, json_chuan

MANG_TAILSCALE = tuple(ipaddress.ip_network(n) for n in (
    "100.64.0.0/10", "fd7a:115c:a1e0::/48",
))
MANG_CHO_PHEP = tuple(ipaddress.ip_network(n) for n in (
    "127.0.0.0/8", "::1/128", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
)) + MANG_TAILSCALE
GIOI_HAN_PHAN_HOI = 2_000_000
TRAN_DAU_VAO_MASK = 64 * 1024
TOKEN_DAU_RA_MASK = 8192


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
    return bool(muc.get("remote_host") or muc.get("remote_model")
                or muc.get("is_remote") or muc.get("is_cloud") or muc.get("remote") or muc.get("cloud")
                or muc.get("local") is False
                or any("cloud" in str(muc.get(k) or "").casefold()
                       for k in ("id", "name", "model", "provider", "nha_cung_cap", "owned_by"))
                or any(str(muc.get(k) or "").casefold() in
                       {"remote", "openai", "anthropic", "azure", "google"}
                       for k in ("provider", "nha_cung_cap", "location", "owned_by")))


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
    # Chỉ dùng cho GET metadata. POST sinh nội dung có trạng thái gửi riêng.
    if than is not None:
        raise ValueError("POST cần transport theo dõi trạng thái gửi.")
    yeu_cau = urllib.request.Request(url, data=than, headers={"Content-Type": "application/json"})
    with bo_mo.open(yeu_cau, timeout=thoi_han) as phan_hoi:
        raw = phan_hoi.read(GIOI_HAN_PHAN_HOI + 1)
    return _giai_json(raw)


def _giai_json(raw):
    """Cùng trần byte/độ sâu và JSON nghiêm cho metadata lẫn phản hồi POST."""
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
    return doc_json(text)


def _gui_post(url, nguon, thoi_han, than, kiem_huy):
    """Không retry/redirect/proxy. Chỉ lỗi connect chắc chắn chưa gửi mới cho thử lại."""
    parsed = urlsplit(url)
    ket_noi = _KetNoiIP(parsed.netloc, nguon=nguon, timeout=thoi_han)
    ket_noi.auto_open = 0
    try:
        kiem_huy()
        try:
            ket_noi.connect()
        except (OSError, http.client.HTTPException):
            raise LocalAIKhongSanSang("Chưa kết nối được máy Local AI.") from None
        kiem_huy()
        try:
            # Từ đây nguồn có thể đã nhận: kể cả request() chỉ gửi được một phần.
            ket_noi.request("POST", parsed.path, body=than,
                            headers={"Content-Type": "application/json"})
            phan_hoi = ket_noi.getresponse()
            if phan_hoi.status != 200:
                raise ChuaRo("local-" + uuid.uuid4().hex)
            raw = phan_hoi.read(GIOI_HAN_PHAN_HOI + 1)
            if len(raw) > GIOI_HAN_PHAN_HOI:
                raise ChuaRo("local-" + uuid.uuid4().hex)
            kich_thuoc = phan_hoi.getheader("Content-Length")
            if kich_thuoc is not None and len(raw) < int(kich_thuoc):
                raise ChuaRo("local-" + uuid.uuid4().hex)
            ket_qua = _giai_json(raw)
        except (OSError, http.client.HTTPException, ValueError, TypeError, RecursionError, OverflowError):
            raise ChuaRo("local-" + uuid.uuid4().hex) from None
        kiem_huy()
        return ket_qua
    finally:
        try:
            ket_noi.close()
        except (OSError, http.client.HTTPException):
            pass  # Lỗi dọn socket không được che mất trạng thái ChuaRo đã xác định.


def _kiem_budget_mask(bo_mo, goc, model, thoi_han, than, loai_api, kiem_huy):
    """Byte UTF-8 là dự trù bảo thủ, không phải phép đếm token của model.

    Chỉ chấp nhận context đang tải được server khai rõ; không dùng max_context_length
    của kiến trúc làm sức chứa thực. Thiếu metadata thì chặn, chờ đo model thật.
    """
    from .chon_model import bo_phat_hien, _chuan_hoa

    if len(than) > TRAN_DAU_VAO_MASK:
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Đầu vào Local AI vượt ngân sách byte cho phép.")
    catalog = bo_phat_hien.phat_hien({"url": goc, "timeout_giay": thoi_han}, kiem_huy=kiem_huy)
    if catalog is None:
        raise LocalAIKhongSanSang("Chưa kiểm được sức chứa model Local AI.")
    # Ollama công bố context đang chạy ở /api/ps; tags không chứng minh sức chứa.
    api, truong, khoa = (("/api/ps", "models", "name") if loai_api == "ollama"
                        else catalog.api[1:])
    kiem_huy()
    data = _doc_json(bo_mo, goc + api, thoi_han)
    kiem_huy()
    moi = _chuan_hoa(data, (catalog.loai, api, truong, khoa))
    if not any(m.ma == model and m.kha_dung for m in moi.models):
        raise LocalAIKhongSanSang("Model Local AI không còn khả dụng trước gửi.")
    ds = data.get(truong) if isinstance(data, dict) else None
    if not isinstance(ds, list):
        raise LocalAIKhongSanSang("Chưa kiểm được sức chứa model Local AI.")
    muc = [m for m in ds if isinstance(m, dict)
           and m.get(khoa, m.get("model") if loai_api == "ollama" else None) == model]
    if not muc or any(model_tu_xa(m) for m in muc):
        raise LocalAIKhongSanSang("Chưa kiểm được nguồn model Local AI.")
    suc_chua = []
    for m in muc:
        n = m.get("loaded_context_length", m.get("context_length"))
        if type(n) is not int or n <= 0:
            raise LocalAIKhongSanSang("Model Local AI chưa khai sức chứa context đang dùng.")
        suc_chua.append(n)
    # Gồm cả JSON, schema, system prompt, phần bọc và dự trù 256 token giao thức.
    if len(than) + 256 + TOKEN_DAU_RA_MASK > min(suc_chua):
        raise LoiNghiepVu("VUOT_GIOI_HAN", "Prompt, khuôn và đầu ra dự kiến vượt sức chứa model Local AI.")


def _noi_dung_hoan_tat(phan_hoi, *, ollama, model):
    if (not isinstance(phan_hoi, dict) or "error" in phan_hoi or model_tu_xa(phan_hoi)
            or phan_hoi.get("nha_cung_cap", "local") != "local"
            or phan_hoi.get("model", model) != model):
        raise LocalAIKhongSanSang("Phản hồi Local AI không đúng nguồn đã chọn.")
    if ollama:
        if phan_hoi.get("done") is not True or phan_hoi.get("done_reason") != "stop":
            raise LocalAIKhongSanSang("Local AI chưa trả phản hồi hoàn tất.")
        noi_dung = phan_hoi["message"]["content"]
    else:
        choices = phan_hoi["choices"]
        if not isinstance(choices, list) or len(choices) != 1 or choices[0].get("finish_reason") != "stop":
            raise LocalAIKhongSanSang("Local AI chưa trả phản hồi hoàn tất.")
        noi_dung = choices[0]["message"]["content"]
    if not isinstance(noi_dung, str) or not noi_dung.strip():
        raise LocalAIKhongSanSang("Máy Local AI chưa trả được câu trả lời.")
    return noi_dung


def _kiem_model(goc, model, thoi_han, kiem_huy):
    # Dùng API đã nhận diện, không bắt Ollama/LM Studio có /v1/models.
    from .chon_model import bo_phat_hien

    catalog = bo_phat_hien.kha_dung_hien_tai(
        {"url": goc, "timeout_giay": thoi_han}, kiem_huy=kiem_huy
    )
    if catalog is None or not any(m.ma == model and m.kha_dung for m in catalog.models):
        raise LocalAIKhongSanSang("Model đã chọn chưa sẵn sàng trên máy Local AI.")
    # Dùng cùng kết quả kiểm khả dụng để chọn cách gửi khuôn, không dò API thêm.
    return catalog.loai


def hoi_local(cau_hinh, model, prompt, *, kiem_huy=lambda: None, khuon=None, ngan_sach_mask=False):
    """Một lượt Local; có khuôn thì dùng API cấu trúc đúng loại máy đã xác minh."""
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
        loai_api = _kiem_model(goc, model, thoi_han, kiem_huy)
        kiem_huy()  # Hủy trong lúc đọc metadata thì không gửi prompt/tài liệu.
        du_lieu = {"model": model, "temperature": 0, "stream": False, "messages": [
            {"role": "system", "content": "Bạn là trợ lý kế toán. Chỉ trả lời đúng định dạng được yêu cầu."},
            {"role": "user", "content": prompt},
        ]}
        url = parsed.geturl()
        if khuon is not None:
            if loai_api == "ollama":
                url = goc + "/api/chat"
                du_lieu.pop("temperature")
                du_lieu.update(format=khuon, options={"temperature": 0})
            else:
                du_lieu["response_format"] = {"type": "json_schema", "json_schema": {
                    "name": "tra_loi_ai", "schema": khuon,
                }}
        if ngan_sach_mask:
            if loai_api == "ollama":
                du_lieu["options"]["num_predict"] = TOKEN_DAU_RA_MASK
            else:
                du_lieu["max_tokens"] = TOKEN_DAU_RA_MASK
        than = json_chuan(du_lieu)
        if ngan_sach_mask:
            _kiem_budget_mask(bo_mo, goc, model, thoi_han, than, loai_api, kiem_huy)
        phan_hoi = _gui_post(url, nguon, thoi_han, than, kiem_huy)
        try:
            return _noi_dung_hoan_tat(phan_hoi, ollama=khuon is not None and loai_api == "ollama", model=model)
        except (ValueError, KeyError, IndexError, TypeError, AttributeError, RecursionError, OverflowError):
            raise ChuaRo("local-" + uuid.uuid4().hex) from None
    except urllib.error.HTTPError as exc:
        exc.close()
        raise LocalAIKhongSanSang("Máy Local AI chưa sẵn sàng. Hãy thử lại.") from None
    except (ValueError, OSError, http.client.HTTPException, KeyError, IndexError, TypeError, AttributeError,
            RecursionError, OverflowError):
        raise LocalAIKhongSanSang("Máy Local AI chưa sẵn sàng. Hãy thử lại.") from None

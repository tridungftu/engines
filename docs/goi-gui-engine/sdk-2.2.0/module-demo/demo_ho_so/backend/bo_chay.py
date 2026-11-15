"""Bộ chạy theo khai báo, TẠM đặt trong gói DEMO cho tới khi SDK 2.0 phía module có điểm vào chung (a.10 điểm 6).

Dựng ModuleRuntime của SDK hiện hành từ chính module.json: mỗi `hanh_dong` thành một route (cùng cách Core dựng
route bản 2), hàm xử lý lấy ở bảng `{hanh_dong.ma: hàm}`. Hàm nhận `sdk` (chỉ `ngan(ma).doc` trên ngăn của chính
module) và `yeu_cau` {duong_dan, truy_van, than, ngu_canh}; lỗi nghiệp vụ trả theo `ma_loi` của phiếu.
Không import Core, không tự bind cổng, không nhận cấu hình từ request. Chỉ dữ liệu của pháp nhân trong phiên.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import socket
import threading
from types import SimpleNamespace
from uuid import UUID

from kho_tri_thuc_sdk.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL, gui_thong_diep
from kho_tri_thuc_sdk.giao_dich import CuaGiaoDich
from kho_tri_thuc_sdk.module_runtime import ModuleRuntime, PhanHoi
from kho_tri_thuc_sdk.ngu_canh import _xoa_loi

ROOT = Path(__file__).resolve().parents[1]
LOI_HTTP = (400, 403, 404, 409, 410, 413, 415, 422, 429, 500, 502, 503, 504)
COT_CHUAN = (("id", "uuid"), ("phap_nhan_id", "uuid"), ("nguoi_tao", "uuid"), ("tao_luc", "timestamptz"),
             ("sua_luc", "timestamptz"), ("ban_ghi_goc_id", "uuid"), ("da_luu_tru", "boolean"))
KIEU_PG = {"van_ban": "text", "so": "numeric", "so_tien": "numeric", "ngay": "date",
           "co_khong": "boolean", "tep": "uuid", "khoa_noi": "uuid"}
TOI_DA_TRANG = 500


def _json_doc(path):
    return json.loads((ROOT / path).read_bytes())


class _KiemSchema:
    """Registry offline: schema kỹ thuật Core cấp + schema trong gói; không tải qua mạng."""

    def __init__(self, schemas):
        from jsonschema import Draft202012Validator, FormatChecker
        from referencing import Registry, Resource
        self._V, self._fc = Draft202012Validator, FormatChecker()
        tat_ca = deepcopy(schemas)
        for path in sorted((ROOT / "schema").glob("*.json")) + sorted((ROOT / "contract").glob("*.schema.json")):
            schema = json.loads(path.read_bytes())
            tat_ca[path.relative_to(ROOT).as_posix()] = schema
            if "$id" in schema:
                tat_ca[schema["$id"]] = schema
        for schema in tat_ca.values():
            Draft202012Validator.check_schema(schema)
        self.registry = Registry().with_resources((uri, Resource.from_contents(s)) for uri, s in tat_ca.items())
        self.schemas = tat_ca

    def kiem(self, schema, value):
        try:
            if isinstance(schema, str):
                schema = {"$ref": schema}
            return self._V(schema, registry=self.registry, format_checker=self._fc).is_valid(value)
        except Exception as exc:  # schema/ref lỗi: coi như không khớp, không lộ chi tiết
            _xoa_loi(exc)
        return False


class _Registry:
    """Đường dẫn cố định thắng đường dẫn có tham số; sai method -> 405."""

    def __init__(self, routes):
        self.routes = tuple(sorted(routes, key=lambda r: "{" in r.duong_dan))

    def tra(self, method, path):
        from kho_tri_thuc_sdk import kenh_khung as k
        found = []
        for route in self.routes:
            pattern = re.sub(r"\\\{([a-z][a-z0-9_]*)\\\}", r"(?P<\1>[^/]+)", re.escape(route.duong_dan))
            match = re.fullmatch(pattern, path)
            if match:
                found.append((route, match.groupdict()))
        if not found:
            raise k.LoiKenh("KHONG_TIM_THAY")
        for route, params in found:
            if route.method == method:
                return route, params
        raise k.LoiKenh("KHONG_TIM_THAY")


def _gia_tri(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class _Ngan:
    """Chỉ đọc một ngăn của chính module, lọc theo pháp nhân của phiên (RLS vẫn áp ở CSDL)."""

    def __init__(self, tx, ma_module, ngan, phap_nhan_id):
        self._tx, self._pn = tx, str(phap_nhan_id)
        self._bang = f'"mod_{ma_module}"."{ngan["ma"]}"'
        self._cot = list(COT_CHUAN) + [(c["ma"], KIEU_PG[c["kieu"]]) for c in ngan["cot"]]

    def doc(self, loc=None, gioi_han=100, con_tro=None):
        kieu = dict(self._cot)
        if (type(loc or {}) is not dict or any(k not in kieu for k in (loc or {}))
                or type(gioi_han) is not int or not 1 <= gioi_han <= TOI_DA_TRANG):
            raise ValueError("NGAN_LOC_KHONG_HOP_LE")
        dau = int(con_tro or 0)
        dieu_kien, tham_so = ['"phap_nhan_id" = %s::uuid'], [self._pn]
        for ten, gia_tri in (loc or {}).items():
            dieu_kien.append(f'"{ten}" = %s::{kieu[ten]}')
            tham_so.append(gia_tri if not isinstance(gia_tri, bool) else gia_tri)
        cot = ", ".join(f'"{t}"' for t, _ in self._cot)
        sql = (f"SELECT {cot} FROM {self._bang} WHERE {' AND '.join(dieu_kien)} "
               f'ORDER BY "tao_luc", "id" LIMIT {gioi_han + 1} OFFSET {dau}')
        rows = self._tx.execute(sql, tham_so).fetchall()
        dong = [{t: _gia_tri(v) for (t, _), v in zip(self._cot, r)} for r in rows[:gioi_han]]
        return {"danh_sach": dong, "con_tro_tiep": str(dau + gioi_han) if len(rows) > gioi_han else None}


class _SdkModule:
    def __init__(self, tx, manifest, context):
        self._tx, self._m, self._ctx = tx, manifest, context

    def ngan(self, ma):
        for ngan in (self._m.get("du_lieu") or {}).get("ngan", []):
            if ngan["ma"] == ma:
                return _Ngan(self._tx, self._m["ma"], ngan, self._ctx.phap_nhan_id)
        raise ValueError("NGAN_KHONG_THUOC_MODULE")


def _hanh_dong_mtq(ma_module, ma_quyen):
    tai_nguyen, _, dong_tu = ma_quyen.partition(".")
    return ":".join((ma_module.upper(), tai_nguyen.upper(), dong_tu.upper()))


def _routes(manifest, kiem, ma_bam_goi, xu_ly, loi_nghiep_vu):
    ma, phien_ban = manifest["ma"], manifest["phien_ban"]
    cong_bo = (manifest.get("contract") or {}).get("cong_bo", [])
    loi = {e["ma"]: e for e in manifest["ma_loi"]}
    routes = []
    for op in manifest["hanh_dong"]:
        ham = xu_ly[op["ma"]]
        target, tai_nguyen = op.get("doi_tuong"), op["quyen"].partition(".")[0]
        version = next((c["phien_ban"] for c in cong_bo if c["ma"] == op.get("contract")),
                       cong_bo[0]["phien_ban"] if len(cong_bo) == 1 else "1")
        params = re.findall(r"\{([a-z][a-z0-9_]*)\}", op["duong_dan"])
        ident = (target["id_tu"].partition(".")[2]
                 if target is not None and target["id_tu"].startswith("duong_dan.") else None)

        def doi_tuong(p, body, target=target, tai_nguyen=tai_nguyen):
            if target is None:
                return {"bang": tai_nguyen}
            nguon, _, ten = target["id_tu"].partition(".")
            value = p.get(ten) if nguon == "duong_dan" else (body or {}).get(ten)
            return {"bang": target["ngan"], "id": str(UUID(value))}

        def handler(tx, context, ham=ham):
            sdk = _SdkModule(tx, manifest, context)
            yeu_cau = dict(duong_dan=dict(context.path or {}), truy_van=dict(context.query or {}),
                           than=context.body, ngu_canh=dict(nguoi_dung_id=str(context.nguoi_dung_id),
                                                           phap_nhan_id=str(context.phap_nhan_id)))
            try:
                return PhanHoi(200, ham(sdk, yeu_cau))
            except loi_nghiep_vu as exc:
                muc = loi.get(exc.ma)
                if muc is None:
                    raise
                return PhanHoi(muc["http"], dict(ma=exc.ma, thong_diep=muc["thong_diep"],
                                                 request_id=context.request_id, thu_lai_duoc=False))

        dau_ra = {200: kiem.schemas[op["dau_ra"]] if "dau_ra" in op else {}}
        dau_ra.update({s: {"$ref": "urn:ktt:contract:loi_chuan.v1"} for s in LOI_HTTP})
        ghi = op["phuong_thuc"] != "GET"
        routes.append(SimpleNamespace(
            method=op["phuong_thuc"], duong_dan=f"/api/v1/module/{ma}" + op["duong_dan"], module=ma,
            operation=op["ma"], hanh_dong=_hanh_dong_mtq(ma, op["quyen"]),
            dau_vao=kiem.schemas[op["dau_vao"]] if "dau_vao" in op else {}, dau_ra=dau_ra,
            ma_loi={(e["http"], e["ma"]): e["thong_diep"] for e in manifest["ma_loi"]},
            doi_tuong=doi_tuong, chu_so_huu="module", viec_lau=op["kieu"] == "nen",
            phien_ban_contract=version, truong_cas=(), loai="doi_tuong", thu_tu=None,
            query_schema={"type": "object", "maxProperties": 20,
                          "propertyNames": {"pattern": "^[a-z][a-z0-9_]{0,62}$"},
                          "additionalProperties": {"type": "string", "maxLength": 200}},
            path_schema={"type": "object", "additionalProperties": False, "required": params,
                         "properties": {n: {"type": "string", "format": "uuid"} if n == ident else
                                        {"type": "string", "minLength": 1, "maxLength": 200,
                                         "pattern": "^[A-Za-z0-9_.:-]+$"} for n in params}},
            handler=handler, ghi=ghi, chong_trung=op["chong_trung"], pham_vi="phap_nhan", phien="bat_buoc",
            phien_ban_goi=phien_ban, ma_bam_goi=ma_bam_goi,
            quyen_doc=lambda ctx, body: dict(hanh_dong=ctx.hanh_dong, doi_tuong=ctx.doi_tuong)))
    return routes


def _kiem_csdl(ket_noi, login):
    """Readiness: kết nối được bằng đúng login module, không đổi vai, không ghi."""
    with ket_noi() as conn:
        with conn.transaction():
            conn.execute("SET TRANSACTION READ ONLY")
            row = conn.execute("SELECT session_user, current_user").fetchone()
            if row is None or tuple(row) != (login, login):
                raise LoiBootstrap("MODULE_READINESS_LOGIN")


class _VongNhan:
    def __init__(self, runtime):
        self.runtime = runtime
        self.worker = threading.Thread(target=self._chay, name="module-runtime", daemon=True)

    def bat_dau(self):
        self.worker.start()

    def _chay(self):
        try:
            self.runtime.chay()
        except Exception as exc:
            _xoa_loi(exc)
            self.ngung_accept()

    def ngung_accept(self):
        self.runtime.ngung_accept()

    def drain(self):
        if not self.runtime.drain(timeout=0.1):
            return False
        if self.worker.ident is not None:
            self.worker.join(0.3)
        return not self.worker.is_alive()


def chay(xu_ly, *, loi_nghiep_vu, kiem_chu_ky, tao_ket_noi, cau_hinh_runtime, stdin=None, stdout=None, **_):
    manifest = _json_doc("module.json")
    ma, phien_ban = manifest["ma"], manifest["phien_ban"]
    contracts = [c["ma"] for c in (manifest.get("contract") or {}).get("cong_bo", [])]
    if set(xu_ly) != {h["ma"] for h in manifest["hanh_dong"]}:
        raise LoiBootstrap("MODULE_BANG_XU_LY_KHONG_KHOP")
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky, stdin=stdin, stdout=stdout)
    vong, da_dong, ma_loi = None, False, "MODULE_RUNTIME_LOI"
    try:
        if bootstrap.bo_doc.module != ma:
            raise LoiBootstrap("MODULE_SAI_MA")
        login = bootstrap.tham_so["dang_nhap_csdl"]
        ket_noi = tao_ket_noi(dang_nhap_csdl=login, cau_hinh=bootstrap.tham_so["csdl"])
        cua = CuaGiaoDich(module=ma, dang_nhap_csdl=login, ket_noi=ket_noi)
        if bootstrap.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN) != 1:
            raise LoiBootstrap("MODULE_LISTENER_CHUA_NGHE")

        def san_sang():
            nonlocal vong, ma_loi
            ma_loi = "MODULE_READINESS_CSDL"
            _kiem_csdl(ket_noi, login)
            ma_loi = "MODULE_READINESS_BINDING"
            cfg = cau_hinh_runtime
            pins = deepcopy(cfg["binding"])
            kiem = _KiemSchema(cfg["schemas"])
            routes = _routes(manifest, kiem, cfg["ma_bam_goi"], xu_ly, loi_nghiep_vu)
            if set(pins) != {r.operation for r in routes}:
                raise LoiBootstrap("MODULE_BINDING_KHONG_KHOP")
            runtime = ModuleRuntime(bootstrap=bootstrap, khoa_cong_khai=cfg["khoa_cong_khai"],
                core_epoch=cfg["core_epoch"], registry=_Registry(routes), kiem=kiem, cua_giao_dich=cua,
                binding=lambda route: (pins[route.operation]["contract_id"], pins[route.operation]["ma_bam_schema"]),
                binding_core=cfg["binding_core"])
            vong = _VongNhan(runtime)
            return True

        bootstrap.bao_san_sang(phien_ban=phien_ban, contracts=contracts, kiem_san_sang=san_sang)
        ma_loi = "MODULE_RUNTIME_LOI"
        vong.bat_dau()
        try:
            bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=vong.drain)
            da_dong = True
        except LoiBootstrap as exc:
            if exc.ma != "DRAIN_CHUA_XONG":
                raise
            _xoa_loi(exc)
            gui_thong_diep(bootstrap._ra, {"protocol": PROTOCOL, "kieu": "drain_chua_xong"})
            while not vong.drain():
                threading.Event().wait(0.05)
            bootstrap.socket.close()
            da_dong = True
            gui_thong_diep(bootstrap._ra, {"protocol": PROTOCOL, "kieu": "da_thu_hoi"})
    except Exception as exc:
        if isinstance(exc, LoiBootstrap) and exc.ma.startswith("MODULE_"):
            ma_loi = exc.ma
        _xoa_loi(exc)
        raise LoiBootstrap(ma_loi) from None
    finally:
        if vong is not None:
            vong.ngung_accept()
            while not vong.drain():
                threading.Event().wait(0.05)
        if not da_dong:
            bootstrap.socket.close()
        bootstrap.bi_mat.thu_hoi()

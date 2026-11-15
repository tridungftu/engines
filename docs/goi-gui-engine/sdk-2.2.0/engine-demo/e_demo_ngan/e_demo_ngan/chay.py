"""Đếm theo ngày Việt Nam và pháp nhân, chỉ gọi ngăn bằng SDK."""
from datetime import datetime, timedelta, timezone

try:
    from kho_tri_thuc_sdk.engine import Engine, NganXungDot
except ImportError:  # chạy trong mã nguồn có SDK 2.2.0
    from kho_tri_thuc.sdk_core.engine import Engine, NganXungDot


app = Engine.tu_khai_bao("engine.json")
GIO_VIET_NAM = timezone(timedelta(hours=7))
SO_LAN_THU_LAI = 5


@app.nang_luc("dem.goi@1")
def dem_goi(viec):
    khoa = {"ngay": datetime.now(GIO_VIET_NAM).date().isoformat()}
    van_ban = viec.dau_vao["van_ban"]
    for lan in range(SO_LAN_THU_LAI + 1):
        viec.kiem_huy()
        try:
            # Core điền pháp nhân từ việc. Tạo bộ đếm 0 nếu chưa có.
            with viec.ngan.lo() as lo:
                lo.lay_hoac_tao("dem_goi", khoa, {"so_lan": 0})
            ban_ghi = viec.ngan.doc("dem_goi", khoa)
            so_lan = int(ban_ghi.gia_tri["so_lan"]) + 1
            # CAS và định danh cùng một lô: xung đột không ghi định danh dở dang.
            with viec.ngan.lo() as lo:
                lo.sua("dem_goi", khoa, {"so_lan": so_lan},
                       row_version=ban_ghi.row_version)
                if van_ban.startswith("DD:"):
                    lo.them("dinh_danh", {
                        "gia_tri": van_ban[3:].strip(),
                        "bi_danh": f'{viec.cau_hinh.get("tien_to", "DEMO")}-{viec.id}',
                    })
            return {"loai": "truong", "truong": {"so_lan": so_lan}}
        except NganXungDot:
            if lan == SO_LAN_THU_LAI:
                raise


if __name__ == "__main__":
    app.chay()

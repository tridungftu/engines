"""Vòng đời trên TienTrinhCore, quét hàng việc/inbox bền vững mỗi giây.

Mọi đường dispatch/worker phải giữ su_dung() đến hết bàn giao. Bộ đếm và
quyết định drain dùng cùng khóa với controller; chờ drain ở ngoài khóa.
Không polling hàng việc bằng quyền owner, không ACK hoặc chạy lại việc ở đây.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import math
from threading import Event, Thread
import time
from types import SimpleNamespace

from . import so_cong, so_do
from .tien_trinh import LoiTienTrinh


class _KetNoiCoHan:
    """Giới hạn tổng thời gian SQL trên cùng transaction bằng SET LOCAL."""

    def __init__(self, conn, *, han=None, controller=None, tran=2, giu_lease=False):
        self._conn, self._han = conn, han
        self._controller, self._tran = controller, tran
        self._giu_lease = giu_lease

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def execute(self, *args, **kwargs):
        now = time.monotonic()
        if self._han is None:
            self._han = now + self._tran
        c = self._controller
        if c is not None:
            binding, den = getattr(c, '_p1_giu_den', (None, None))
            if self._giu_lease and binding != (str(c.instance_id), c.the_he):
                # Chưa biết hạn: cấp lease trong tx riêng trước SQL có thể
                # chờ dưới khóa. Không để lease mới chờ commit cùng SQL đó.
                binding = str(c.instance_id), c.the_he
                with c._giao_dich() as conn:
                    while isinstance(conn, _KetNoiCoHan):
                        conn = conn._conn
                    bounded = _KetNoiCoHan(conn, han=self._han, tran=self._tran)
                    row = so_cong.gia_han(bounded, c.id, c.instance_id, c.the_he)
                den = datetime.fromisoformat(str(row['giu_den']))
                c._p1_giu_den, c._p1_lease = (binding, den), (binding, 120)
        con = min(self._tran, self._han - time.monotonic())
        if c is not None:
            if binding == (str(c.instance_id), c.the_he):
                con = min(con, (den - datetime.now(timezone.utc)).total_seconds() / 2)
        # Không làm tròn lên thành SQL vượt phần lease/deadline còn lại.
        ms = int(con * 1000)
        if ms < 1:
            raise TimeoutError('KENH_DRAIN_HET_HAN')
        self._conn.execute(f'SET LOCAL statement_timeout = {ms}')
        if time.monotonic() >= self._han:
            raise TimeoutError('KENH_DRAIN_HET_HAN')
        return self._conn.execute(*args, **kwargs)


class VongDoiCore:
    CAC_LUOT = ('request', 'viec', 'lease', 'download', 'mask', 'inbox')

    def __init__(self, tien_trinh, *, giao_dich, dong_ho=time.monotonic, nhip_quet=1,
                 drain_inbox=None):
        if nhip_quet is not None and (isinstance(nhip_quet, bool)
                or not isinstance(nhip_quet, (int, float)) or not math.isfinite(nhip_quet)
                or not 0 < nhip_quet <= 5):
            raise ValueError('Nhịp quét phải trong (0, 5] giây')
        if drain_inbox is not None and not callable(drain_inbox):
            raise ValueError('Cần callback drain consumer module')
        self._drain_inbox = drain_inbox
        self._gia_han_inbox = None
        self.tien_trinh = tien_trinh
        self._giao_dich, self._gio = giao_dich, dong_ho
        # Các adapter cùng controller chia sẻ bộ đếm và cờ drain.
        with tien_trinh.khoa:
            if not hasattr(tien_trinh, '_vong_doi'):
                tien_trinh._vong_doi = SimpleNamespace(
                    luot=dict.fromkeys(self.CAC_LUOT, 0), lan_cuoi=self._gio(), dang_dung=False)
            self._s = tien_trinh._vong_doi
        self._dung_quet, self._luong_quet = Event(), None
        self.loi_quet = None
        if nhip_quet is not None:
            self._luong_quet = Thread(target=self._quet_lap, args=(nhip_quet,), daemon=True)
            self._luong_quet.start()

    def _quet_lap(self, nhip):
        while not self._dung_quet.wait(nhip):
            try:
                self.quet_hang_cho()
                self.kiem_ranh()
                self.loi_quet = None
            except (so_do.LoiSoDo, LoiTienTrinh) as exc:
                self.loi_quet = exc.ma
            except Exception:
                # Không để DSN/lỗi driver thoát luồng; lần sau đọc lại CSDL.
                self.loi_quet = 'CHE_DO_THAT_BAI'

    def dong(self, *, timeout=5):
        """Core dừng vòng quét trước khi đóng controller/kết nối CSDL."""
        self._dung_quet.set()
        if self._luong_quet is not None:
            self._luong_quet.join(timeout)
            return not self._luong_quet.is_alive()
        return True

    def quet_hang_cho(self):
        """Bật một instance khi có việc/inbox đã commit ở pháp nhân không TAT.

        Công tắc theo từng pháp nhân, không theo instance. SQL bỏ pháp nhân
        TAT; _danh_thuc kiểm lại dưới khóa để chặn đổi TAT giữa quét và bật.
        """
        c = self.tien_trinh
        with c.khoa:
            # failed sau cleanup vẫn được thử lại. Controller đọc hạn 2/4
            # giây và khóa LOI từ sổ bền vững, không suy từ trạng thái local.
            if self._s.dang_dung or c.trang_thai not in ('stopped', 'failed'):
                return None
            with self._giao_dich() as conn:
                cac_hang = so_do.hang_cho(conn, c.id)
            for hang in cac_hang:
                if not (hang['so_viec'] or hang['so_inbox']):
                    continue
                try:
                    return self._danh_thuc(hang['phap_nhan_id'])
                except so_do.LoiSoDo as exc:
                    if exc.ma != 'MODULE_TAT':
                        raise
            return None

    def _kiem_drain(self):
        if self._s.dang_dung or self.tien_trinh.trang_thai == 'dang_dung':
            raise LoiTienTrinh('TIEN_TRINH_DANG_DUNG')

    def _danh_thuc(self, phap_nhan_id):
        self._kiem_drain()
        # Khóa công tắc PG tương thích module_doi_che_do; TAT không thể commit
        # xen giữa kiểm và spawn. Transaction này không bao gồm drain/request.
        with self._giao_dich() as conn:
            if self.tien_trinh.trang_thai == 'ready':
                conn = _KetNoiCoHan(conn, controller=self.tien_trinh, giu_lease=True)
            so_do.cho_bat(conn, self.tien_trinh.id, phap_nhan_id)
            loi = None
            try:
                instance = self.tien_trinh.khoi_dong()
            except LoiTienTrinh as exc:
                # Cùng connection có thể dùng nested transaction; phải commit
                # bộ đếm lỗi/retry 022 trước khi trả 503 ra ngoài transaction.
                loi = exc
        if loi is not None:
            raise loi
        self._s.lan_cuoi = self._gio()
        return instance

    def danh_thuc(self, *, phap_nhan_id, nguon='request'):
        """Dùng cho request, việc đã commit hoặc inbox; cùng một instance."""
        if nguon not in ('request', 'viec', 'inbox'):
            raise ValueError('Nguồn đánh thức không hợp lệ')
        with self.tien_trinh.khoa:
            return self._danh_thuc(phap_nhan_id)

    @contextmanager
    def su_dung(self, *, phap_nhan_id, loai='request'):
        if loai not in self.CAC_LUOT:
            raise ValueError('Loại lượt giữ không hợp lệ')
        with self.tien_trinh.khoa:
            instance = self._danh_thuc(phap_nhan_id)
            self._s.luot[loai] += 1
        try:
            yield instance
        finally:
            with self.tien_trinh.khoa:
                self._s.luot[loai] -= 1
                self._s.lan_cuoi = self._gio()

    def xu_ly_inbox(self, *, phap_nhan_id, xu_ly):
        """Giữ instance tới khi consumer module commit/rollback và trả về.

        Composition root cấp callback qua kênh module đã xác thực; callback
        phải chờ transaction module đóng. Không chuyển handler vào login Core.
        Không ACK tại đây; TAT/drain vẫn được kiểm dưới khóa trước khi gọi.
        """
        if not callable(xu_ly):
            raise ValueError('Cần callback consumer module')
        with self.su_dung(phap_nhan_id=phap_nhan_id, loai='inbox') as instance:
            return xu_ly(instance)

    def drain_inbox(self, *, timeout=300, gia_han=True, han=None):
        """Một nhịp chờ consumer; False để vòng ngoài gia hạn rồi gọi lại.

        Ghim đúng instance/thế hệ; không giữ khóa controller trong khi chờ.
        Thiếu provider thì không có consumer để drain. Không đóng kênh ở đây.
        Manager truyền gia_han=False khi đã có luồng giữ lease toàn drain.
        """
        if (type(timeout) not in (int, float) or not math.isfinite(timeout)
                or not 0 <= timeout <= 300):
            raise ValueError('Hạn drain không hợp lệ')
        c = self.tien_trinh
        if not c.khoa.acquire(timeout=-1 if han is None else max(0, han - time.monotonic())):
            return False
        try:
            self._s.dang_dung = True
            if c.trang_thai == 'stopped':
                return True
            instance, the_he = c.instance_id, c.the_he
            now = time.monotonic()
            old = self._gia_han_inbox
            lan_dau = old is None or old[:2] != (instance, the_he)
            if gia_han and c.trang_thai == 'ready':
                if lan_dau and self._drain_inbox is None:
                    # Không có consumer để chờ ngay nhịp đầu. Thu hồi tức thì
                    # giữ đường P1; nếu manager còn chờ, gia hạn từ nhịp sau.
                    self._gia_han_inbox = instance, the_he, now
                elif lan_dau or now - old[2] >= 1:
                    # Cờ drain chặn lượt mới, chưa phải đã thu hồi controller.
                    # Giữ lease cả khi không callback hoặc consumer đã xong.
                    c.gia_han()
                    self._gia_han_inbox = instance, the_he, now
            if self._drain_inbox is None:
                return True
        finally:
            c.khoa.release()
        return self._drain_inbox(instance, the_he, timeout=min(1, timeout)) is True

    def kiem_ranh(self, *, timeout=300):
        if isinstance(timeout, bool) or not 0 < timeout <= 300:
            raise ValueError('Hạn drain không hợp lệ')
        c = self.tien_trinh
        with c.khoa:
            if self._s.dang_dung or c.trang_thai != 'ready' or any(self._s.luot.values()):
                return False
            with self._giao_dich() as conn:
                # Tổng các truy vấn dưới khóa cũng phải nằm trong lease.
                conn = _KetNoiCoHan(conn, controller=c, giu_lease=True)
                cfg = so_do.cau_hinh(conn, c.id)
                if cfg['che_do'] == 'luon_chay' or self._gio() - self._s.lan_cuoi < cfg['ranh_giay']:
                    return False
                if any(h['so_viec'] or h['so_inbox'] for h in so_do.hang_cho(conn, c.id)):
                    return False
                so_do.ghi_drain(conn, c.id, c.instance_id, c.the_he)
            self._s.dang_dung = True
        try:
            if self._drain_inbox is None:
                # Giữ đường P1-SUA: thu_hoi tự cấp lease cho toàn bộ timeout.
                return c.thu_hoi(timeout=timeout)
            han = time.monotonic() + timeout
            while not self.drain_inbox(timeout=max(0, han - time.monotonic())):
                con = han - time.monotonic()
                if con <= 0:
                    return False
                self._dung_quet.wait(min(.01, con))
            con = han - time.monotonic()
            return con > 0 and c.thu_hoi(timeout=con)
        finally:
            with c.khoa:
                # Quá hạn/không rõ kết quả giữ chặn đến khi kiem_con xác nhận.
                if c.trang_thai == 'stopped':
                    self._s.dang_dung = False
                    self._s.lan_cuoi = self._gio()

    def kiem_con(self):
        ket_qua = self.tien_trinh.kiem_con()
        with self.tien_trinh.khoa:
            if self.tien_trinh.trang_thai == 'stopped':
                self._s.dang_dung = False
        return ket_qua

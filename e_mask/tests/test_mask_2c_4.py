"""Tool ngoài gói, chỉ Local HTTP giả + CoreGia; không đo chất lượng model."""
from copy import deepcopy
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
import unicodedata

import pytest

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / 'e_hoi_ai/tests'))
spec = importlib.util.spec_from_file_location('thu_mask_local_ai_that', GOC / 'e_mask/cong-cu/thu_mask_local_ai_that.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
from local_gia import LocalGia
from e_hoi_ai import chay as ai, chon_model
from e_hoi_ai.nha_cung_cap import NhaCungCapCloud
from ho_tro_hau_kiem_ai import bo, giao, chay, tap_phan_hoi, thuc_the


@pytest.fixture(autouse=True)
def chi_loopback_khong_cloud(monkeypatch):
    goc = socket.socket.connect
    def connect(s, address):
        assert ipaddress.ip_address(address[0]).is_loopback
        return goc(s, address)
    def cam(*a, **kw):
        raise AssertionError('Không được DNS/Cloud trong bộ giả.')
    monkeypatch.setattr(socket.socket, 'connect', connect)
    monkeypatch.setattr(socket, 'getaddrinfo', cam)
    monkeypatch.setattr(NhaCungCapCloud, 'hoi', cam)
    monkeypatch.setattr(chon_model, 'bo_phat_hien', chon_model.BoPhatHienModel())


def ca_demo(ten='orvella linero', *, chu=None, nhom='nguoi'):
    chu = 'DEMO; ' + ten + '; nội dung.' if chu is None else chu
    gold = []
    start = 0
    while ten:
        a = chu.find(ten, start)
        if a < 0:
            break
        gold.append(dict(loai='nguoi', nguyen_van=ten, bat_dau=a, ket_thuc=a + len(ten)))
        start = a + len(ten)
    return dict(ma='D-test', nhom=nhom, van_ban=chu, gold=gold)


def bo_demo(*cac):
    return dict(noi_dung={'ung_vien': list(cac)}, tinh_trang_gold='DEMO test, không held-out',
                sha256_noi_dung=tool.bam(list(cac)))


def tra_gold(may, gold):
    """Oracle CHỈ cho development/hồi quy/mock; không chạy trên ứng viên mới."""
    def khi_nhan(method, path):
        if method != 'POST':
            return
        req = may.yeu_cau[-1]
        prompt = req['messages'][1]['content']
        text = json.loads(prompt[prompt.find('{'):])['tai_lieu']
        ts = []
        for ten in gold:
            start = 0
            while True:
                a = text.find(ten, start)
                if a < 0:
                    break
                ts.append(dict(loai='nguoi', nguyen_van=ten, bat_dau=a, ket_thuc=a+len(ten), muc='chac'))
                start = a + len(ten)
        may.tra_loi = dict(da_quet_het=True, thuc_the=ts)
    may.khi_nhan = khi_nhan


def do_gia(may, ca, **kw):
    return tool.do(bo_demo(ca), that=True, url=may.url, model='model-demo', **kw)


def test_bo_ung_vien_gold_bam_du_so_luong_tach_ca_cu():
    v = tool.doc_bo()
    ds = [c for c in v['noi_dung']['ung_vien'] if not c['ma'].startswith('BS')]
    assert len([c for c in ds if c['nhom'] == 'nguoi']) == 45
    assert len([c for c in ds if c['nhom'] == 'thuong']) >= 75
    assert len([c for c in ds if c['nhom'] == 'to_chuc']) == 15
    assert len([c for c in ds if c['nhom'] == 'dia_chi']) == 15
    assert len([c for c in ds if c['nhom'] == 'bien_the']) == 12
    assert len({c['gold'][0]['nguyen_van'] for c in ds if c['nhom'] == 'nguoi'}) == 45
    assert all(c['gold'][0]['nguyen_van'].islower() for c in ds if c['nhom'] == 'nguoi')
    assert len(v['noi_dung']['hoi_quy_lead_cu']) == 4
    assert set(c['van_ban'] for c in ds).isdisjoint(c['van_ban'] for c in v['noi_dung']['development'])
    assert 'CHƯA lead' in v['tinh_trang_gold']
    cu = '\n'.join(p.read_text('utf-8') for p in (GOC/'e_mask/tests').glob('test_*.py')
                   if p.name != Path(__file__).name)
    assert all(c['gold'][0]['nguyen_van'] not in cu for c in ds if c['nhom'] == 'nguoi')


def test_mac_dinh_kho_khong_mang_khong_so_gia(monkeypatch, capsys):
    def cam(*a, **kw):
        raise AssertionError('Khô không được mở socket.')
    monkeypatch.setattr(socket.socket, 'connect', cam)
    monkeypatch.setattr(socket.socket, 'sendto', cam)
    assert tool.main([]) == 0
    v = json.loads(capsys.readouterr().out)
    assert v['trang_thai_local'] == 'CHƯA ĐO Local thật'
    assert v['ket_qua'] is None and v['so_luot_local'] == v['so_luot_cloud'] == 0
    assert 'muc_tieu_0_lot' not in v and v['held_out_doc_lap'] is True
    assert v['tinh_trang_gold'].startswith('ĐÃ ĐÓNG BĂNG')


@pytest.mark.parametrize('args', [['--that'], ['--that', '--url', 'http://127.0.0.1:1'], ['--that', '--model', 'model-demo']])
def test_can_du_ba_tham_so(args):
    with pytest.raises(SystemExit) as exc:
        tool.main(args)
    assert exc.value.code == 2


@pytest.mark.parametrize('ollama', [False, True])
def test_toan_chuoi_model_va_network_checks_nguyen_ban(ollama):
    ca = ca_demo()
    with LocalGia() as may:
        if ollama:
            may.tags = [{'name': 'model-demo'}]
        tra_gold(may, ['orvella linero'])
        k = do_gia(may, ca)
    hai = k['ket_qua']['hai_lop']
    assert hai['trang_thai']['phat_hanh_che_du'] == 1, k
    assert hai['so_span_che_du'] == 1 and hai['so_span_lot'] == 0
    assert hai['so_doan_ke_hoach'] == hai['so_doan_ai_xong'] == k['so_luot_local'] == 1
    assert k['so_luot_cloud'] == 0 and may.so_luot_hoi == 1
    wire = json.dumps(may.yeu_cau, ensure_ascii=False)
    assert 'chuyen_tiep' not in wire and 'bam_ho_so' not in wire
    assert any(method == 'GET' for method, _ in may.luot)
    assert k['ket_qua']['quy_tac']['so_span_lot'] == 1


@pytest.mark.parametrize('ten', ['orvella linero', unicodedata.normalize('NFD', 'ánh veloria'),
                                'orvella\u200b linero', 'orvella\u200f linero', 'orvella linero\ufe0f'])
def test_nfd_cf_selector_lap(ten):
    ca = ca_demo(ten, chu=ten+'; '+ten+'; nội dung DEMO.')
    with LocalGia() as may:
        tra_gold(may, [ten])
        k = do_gia(may, ca)
    hai = k['ket_qua']['hai_lop']
    assert hai['trang_thai']['phat_hanh_che_du'] == 1, k
    assert hai['so_span_gold'] == hai['so_span_che_du'] == 2


def test_nhieu_doan_overlap_du_va_khong_gui_gold():
    ten = 'orvella linero'
    chu = 'nội dung tổng hợp. ' * 380 + ten + '; ' + 'nội dung tổng hợp. ' * 480 + ten
    with LocalGia() as may:
        tra_gold(may, [ten])
        k = do_gia(may, ca_demo(ten, chu=chu))
    hai = k['ket_qua']['hai_lop']
    assert hai['so_doan_ke_hoach'] >= 2
    assert hai['so_doan_ke_hoach'] == hai['so_doan_ai_xong'] == may.so_luot_hoi
    assert hai['so_span_che_du'] == 2, k
    assert k['tung_ca'][-1]['du_doan'] is True


@pytest.mark.parametrize('ten,chu', [('mạc đĩnh chi','mạc đĩnh chi'), ('lương thế vinh','lương thế vinh'),
    ('từ minh tâm','từ minh tâm'), ('văn tiến dũng','phụ trách hạng mục: văn tiến dũng')])
def test_hai_lop_bon_ca_lead_cu_ai_bao_du(ten, chu):
    b = bo(chu + '; nội dung DEMO.')
    a = b.chu.index(ten)
    giao(b, tap_phan_hoi(b, [thuc_the(b, a, a + len(ten))]))
    k = chay(b)
    assert k['trang_thai'] == 'XONG', k
    assert ten not in k['ket_qua']['van_ban_da_che']['van_ban']


def test_ai_bao_thieu_mot_phan_ten_van_lot_khong_duoc_tuyen_bo_cuu_het():
    ca = ca_demo('mạc đĩnh chi', chu='mạc đĩnh chi; nội dung DEMO.')
    with LocalGia() as may:
        tra_gold(may, ['mạc đĩnh'])
        k = do_gia(may, ca)
    hai = k['ket_qua']['hai_lop']
    assert hai['so_ca_lot'] == hai['so_span_lot'] == 1, k
    assert hai['trang_thai']['phat_hanh_con_lot'] == 1
    assert k['muc_tieu_0_lot'] == 'KHÔNG ĐẠT'


def test_da_thay_lot_van_khong_dat_khi_ca_khac_loi_ky_thuat():
    c1 = ca_demo('mạc đĩnh chi',chu='mạc đĩnh chi; nội dung DEMO.')
    c2 = ca_demo()
    with LocalGia() as may:
        tra_gold(may,['mạc đĩnh'])
        nhan = may.khi_nhan
        def khi_nhan(method,path):
            nhan(method,path)
            if method == 'POST' and 'orvella' in may.yeu_cau[-1]['messages'][1]['content']:
                may.tra_loi = 'JSON không hợp lệ'
        may.khi_nhan = khi_nhan
        k = tool.do(bo_demo(c1,c2),that=True,url=may.url,model='model-demo')
    assert k['muc_tieu_0_lot'] == 'KHÔNG ĐẠT'
    assert k['ket_qua']['hai_lop']['so_ca_lot'] == 1
    assert k['ket_qua']['hai_lop']['trang_thai']['loi_ky_thuat'] == 1


@pytest.mark.parametrize('dang', ['json', 'khong_model', 'model_khac', 'cat', '202', 'timeout', 'context', 'remote'])
def test_loi_ky_thuat_va_chua_ro_khong_thanh_0_dat(dang):
    with LocalGia() as may:
        may.tra_loi = 'JSON không hợp lệ' if dang == 'json' else {'da_quet_het': True, 'thuc_the': []}
        if dang == 'khong_model': may.models = []
        if dang == 'model_khac': may.models = [{'id': 'model-khac', 'owned_by': 'local', 'context_length': 65536}]
        if dang == 'remote': may.models[0]['is_remote'] = True
        if dang == 'context': may.models[0]['context_length'] = 100
        if dang == 'cat': may.cat_sau_post = True
        if dang == '202': may.ma_http = 202
        if dang == 'timeout':
            may.khi_nhan = lambda method, path: time.sleep(.8) if method == 'POST' else None
        k = do_gia(may, ca_demo(), timeout=.3 if dang == 'timeout' else 120)
    hai = k['ket_qua']['hai_lop']
    assert hai['trang_thai']['loi_ky_thuat'] + hai['trang_thai']['chua_ro'] == 1, k
    assert hai['trang_thai']['chan_nghiep_vu'] == 0
    assert hai['ca_hop_le'] == 0 and hai['so_span_lot'] == 0
    assert k['muc_tieu_0_lot'] == 'CHƯA ĐO ĐỦ' and k['so_luot_cloud'] == 0
    if dang in {'cat','202','timeout'}:
        assert hai['trang_thai']['chua_ro'] == 1
        assert k['so_timeout_xac_dinh'] is None
    if dang in {'khong_model','model_khac','remote','context'}:
        assert not may.so_luot_hoi


def test_thieu_doan_hau_kiem_chan_ky_thuat():
    b = bo('nội dung tổng hợp. ' * 900)
    bundle = tap_phan_hoi(b)
    assert len(bundle['phan_hoi']) > 1
    bundle['phan_hoi'].pop(0)
    giao(b, bundle)
    k = chay(b)
    r = tool.cham(ca_demo('', chu=b.chu, nhom='thuong'), k, b.n)
    assert r['trang_thai'] == 'loi_ky_thuat' and k['ket_qua'] is None


def test_bao_nham_hop_hai_nhom_va_mau_so_khong_giau_loi():
    rows = []
    for trang, thua in [('phat_hanh_che_du',True),('chan_nghiep_vu',True),('loi_ky_thuat',None),('chua_ro',None),('phat_hanh_che_du',False)]:
        rows.append(dict(che_do='hai_lop', nhom='thuong', trang_thai=trang, che_thua=thua,
                         so_span_gold=0, so_span_lot=None, so_doan_ke_hoach=0,
                         so_doan_ai_xong=0, thoi_gian_ms=1, ma_loi=None))
    thuong = tool.tong_hop(rows)['hai_lop']['cau_thuong']
    assert thuong == dict(tu_so=2, mau_so=5, so_ca_hop_le=3, ti_le=.4,
                         ti_le_tren_ca_hop_le=2/3, nguyen_ven=1)


def test_bao_nham_dem_tu_ca_thuong_chay_thuc_bang_mock():
    cac = [ca_demo('',chu='nội dung tổng hợp.',nhom='thuong'),
           ca_demo('',chu='nội dung DEMO.',nhom='thuong'),
           ca_demo('',chu='Mai sau khi nhận hóa đơn sẽ hạch toán vào tài khoản 331.',nhom='thuong')]
    with LocalGia(tra_loi={'da_quet_het': True, 'thuc_the': []}) as may:
        k = tool.do(bo_demo(*cac),that=True,url=may.url,model='model-demo')
    for che_do in ('quy_tac','hai_lop'):
        v = k['ket_qua'][che_do]['cau_thuong']
        assert (v['tu_so'],v['mau_so'],v['so_ca_hop_le'],v['nguyen_ven']) == (2,3,3,1), k
        assert v['ti_le'] == 2/3


def test_bao_cao_khong_ro_goc_url_path_ma_yeu_cau(capsys, tmp_path, monkeypatch):
    ca = ca_demo()
    with LocalGia() as may:
        tra_gold(may, ['orvella linero'])
        monkeypatch.setattr(tool, 'doc_bo', lambda: bo_demo(ca))
        tep = tmp_path / 'bao cao DEMO.json'
        assert tool.main(['--that','--url',may.url,'--model','model-demo','--bao-cao',str(tep),
                          '--thu-muc-bao-cao',str(tmp_path)]) == 0
    log = capsys.readouterr()
    raw = tep.read_text('utf-8')
    for bi_mat in (ca['van_ban'], 'orvella linero', may.url, str(tep), 'yeu-cau-demo-', 'luot-demo-'):
        assert bi_mat not in log.out + log.err + raw
    assert json.loads(raw)['held_out_doc_lap'] is False


def test_cam_bao_cao_trong_engine_va_khong_ghi_de(tmp_path):
    for ma in ('e_mask','e_hoi_ai','e_ocr'):
        assert tool.main(['--bao-cao',str(GOC/ma/'khong-duoc-tao.json')]) == 2
    tep = tmp_path/'da co.json'
    tep.write_text('DEMO nguyên bản',encoding='utf-8')
    assert tool.main(['--bao-cao',str(tep)]) == 2
    assert tep.read_text('utf-8') == 'DEMO nguyên bản'


@pytest.mark.skipif(os.name != 'nt', reason='Chỉ Windows chạy cmd.exe; Linux vẫn kiểm ASCII/quote ở test khác.')
def test_cmd_chay_kho_duong_dan_va_thu_muc_co_khoang_trang(tmp_path):
    root = tmp_path/'ban DEMO co khoang trang'
    for rel in ('e_mask/cong-cu','e_mask/goi','e_hoi_ai/goi','e_mask/tests','.venv'):
        shutil.copytree(GOC/rel,root/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    script = root/'e_mask/cong-cu/THU-MASK-LOCAL-AI-THAT.cmd'
    report = tmp_path/'bao cao co khoang trang.json'
    command = f'cmd.exe /d /s /c ""{script}" --bao-cao "{report}""'
    k = subprocess.run(command,cwd=tmp_path, capture_output=True,
                       encoding='utf-8',timeout=30)
    assert k.returncode == 0, k.stdout+k.stderr
    assert json.loads(k.stdout)['trang_thai_local'] == 'CHƯA ĐO Local thật'
    assert json.loads(report.read_text('utf-8'))['so_luot_local'] == 0


def test_cmd_ascii_quote_va_B():
    raw = (GOC/'e_mask/cong-cu/THU-MASK-LOCAL-AI-THAT.cmd').read_bytes()
    raw.decode('ascii')
    assert b'"%MASK_PY%" -B "%~dp0thu_mask_local_ai_that.py" %*' in raw
    assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b'')


def test_28_ca_bo_sung_du_nhan_gold_khung_va_ke_hoach_thuc():
    ds = [c for c in tool.doc_bo()['noi_dung']['ung_vien'] if c['ma'].startswith('BS')]
    assert len(ds) == 28
    assert len({c['van_ban'] for c in ds}) == 28
    assert all(c['nhan'] == 'DEMO' and 'DEMO' in c['van_ban'] for c in ds)
    assert len({c['gold'][0]['nguyen_van'].casefold() for c in ds}) == 28
    nguoi = [c for c in ds if c['nhom'] == 'nguoi']
    assert {c.get('danh_xung') for c in nguoi} >= {'ông','bà','anh','chị','TS.','ThS.','Mr.'}
    assert {c['so_am_tiet'] for c in nguoi} == {2,4}
    for c in nguoi:
        ten = c['gold'][0]['nguyen_van']
        assert ten.isascii() and (ten.istitle() or ten.isupper())
    assert {c['gold'][0]['nguyen_van'].split()[0].lower() for c in nguoi} == {
        'ha','ho','luong','van','phan','mai'}
    for nhom in ('to_chuc','dia_chi'):
        cac = [c for c in ds if c['nhom'] == nhom]
        assert len(cac) == 5
        assert {c['khung_cau'] for c in cac} == {'hop_dong','email','bien_ban','bang_ke','chu_ky'}
        assert all('demo' not in t['nguyen_van'].casefold() for c in cac for t in c['gold'])
    bien = [c for c in nguoi if c.get('vi_tri_doan')]
    assert len(bien) == 6
    for c in bien:
        ke = tool.cb.lap_ke_hoach(c['van_ban'])
        a, b = c['gold'][0]['bat_dau'], c['gold'][0]['ket_thuc']
        assert len(ke) >= 2
        kieu = c['vi_tri_doan']
        if kieu == 'dau_van_ban': assert a == ke[0].bat_dau == 0
        if kieu == 'cuoi_van_ban': assert b == ke[-1].ket_thuc == len(c['van_ban'])
        if kieu == 'dau_doan_noi': assert any(a == d.bat_dau for d in ke[1:])
        if kieu == 'cuoi_doan_noi': assert any(b == d.ket_thuc for d in ke[:-1])
        if kieu == 'vung_chong':
            assert sum(d.bat_dau <= a < b <= d.ket_thuc for d in ke) >= 2
        if kieu == 'bien_chinh': assert any(a < d.ket_thuc_chinh < b for d in ke[:-1])


def test_tach_chan_truoc_ai_khoi_ai_do_va_mau_so_bao_nham():
    cac = [ca_demo('',chu='Mai sau khi nhận hóa đơn sẽ hạch toán vào tài khoản 331.',nhom='thuong'),
           ca_demo(), ca_demo('',chu='nội dung tổng hợp.',nhom='thuong')]
    with LocalGia() as may:
        tra_gold(may, ['orvella linero', 'nội dung'])
        k = tool.do(bo_demo(*cac),that=True,url=may.url,model='model-demo')
    tong = k['ket_qua']['hai_lop']
    tach = tong['phan_tach']
    assert tong['tong_ca'] == 3
    assert tach['chan_truoc_ai']['tong_ca'] == 1
    assert tach['chan_truoc_ai']['so_doan_ai_xong'] == 0
    assert tach['chan_truoc_ai']['so_ca_lot'] == 0
    assert tach['ai_thuc_su_do']['tong_ca'] == 2
    assert tach['ai_thuc_su_do']['cau_thuong']['mau_so'] == 1
    assert tong['cau_thuong']['mau_so'] == 2
    assert '0 lọt trên ca bị chặn trước AI là hiển nhiên' in tong['ghi_chu']


@pytest.mark.parametrize('loai', ['nguoi','to_chuc','dia_chi'])
def test_che_vuot_gold_cua_ca_dinh_danh_do_doc_lap(loai, monkeypatch):
    ca = ca_demo('vùng cần che', chu='DEMO vùng cần che ngoài vàng', nhom=loai)
    ca['gold'][0]['loai'] = loai
    a, b = ca['gold'][0]['bat_dau'], ca['gold'][0]['ket_thuc']
    monkeypatch.setattr(tool, 'map_doc_lap', lambda *args: [(a,b+5)])
    kq = {'trang_thai':'XONG','ket_qua':{'van_ban_da_che':{'van_ban':'DEMO [[MASKTAM-0001]] vàng'}}}
    r = tool.cham(ca,kq,None)
    assert r['so_span_lot'] == 0
    assert r['che_thua'] is True and r['so_span_che_thua'] == 1 and r['so_ky_tu_che_thua'] == 5
    r.update(ca='D-test', che_do='hai_lop', nhom=loai, so_span_gold=1,
             so_doan_ke_hoach=1, so_doan_ai_xong=1, thoi_gian_ms=1)
    t = tool.tong_hop([r])['hai_lop']['che_thua_dinh_danh']
    assert t == dict(so_ca=1,so_ca_da_cham=1,tong_ca_co_gold=1,so_span=1,so_ky_tu=5)


def test_han_mac_dinh_theo_doan_va_tran_cau_hinh():
    ca = ca_demo('', chu='DEMO; '+ 'nội dung tổng hợp; '*900,nhom='thuong')
    n = len(tool.cb.lap_ke_hoach(ca['van_ban']))
    assert n > 1
    assert tool.han_ca(ca) == (120*n,n)
    assert tool.han_ca(ca,timeout_toi_da=200) == (200,n)
    assert tool.han_ca(ca,timeout=40,timeout_toi_da=200) == (40,n)
    assert tool.han_ca(ca,timeout=300,timeout_toi_da=200) == (200,n)


@pytest.mark.parametrize('gia_tri', ['0','-1','nan','inf'])
def test_timeout_khong_hop_le_khong_tao_bao_cao(gia_tri, tmp_path):
    tep = tmp_path/'timeout.json'
    assert tool.main(['--timeout',gia_tri,'--bao-cao',str(tep)]) == 2
    assert not tep.exists()


def test_ngoai_le_giua_chung_giu_ca_xong_va_danh_dau_ca_chua_do(monkeypatch):
    c1, c2 = ca_demo(), ca_demo('norella finero')
    c2['ma'] = 'D-test-2'
    goc = tool.tao_bo
    def tao(ca,*a,**kw):
        if ca['ma'] == 'D-test-2': raise RuntimeError('DEMO không được phản chiếu')
        return goc(ca,*a,**kw)
    monkeypatch.setattr(tool,'tao_bo',tao)
    with LocalGia() as may:
        tra_gold(may,['orvella linero'])
        k = tool.do(bo_demo(c1,c2),that=True,url=may.url,model='model-demo')
    assert len(k['tung_ca']) == 4
    assert k['tung_ca'][1]['trang_thai'] == 'phat_hanh_che_du'
    assert all(r['tinh_trang_do'] == 'chưa đo đủ' and r['so_span_lot'] is None for r in k['tung_ca'][2:])
    assert k['loi_giua_chung'] == 'NGOAI_LE_KHI_DO' and k['muc_tieu_0_lot'] == 'CHƯA ĐO ĐỦ'
    assert 'không được phản chiếu' not in json.dumps(k,ensure_ascii=False)


def gia_deadline_child(monkeypatch, *, so_doan_ai_xong):
    """Chạy chuỗi thật tới checkpoint, tiêm hết hạn tại biên subprocess.

    subprocess.run bảo đảm kill/wait trước TimeoutExpired. Test phía cha
    kiểm hợp đồng đó bằng tín hiệu xác định, không dùng sleep hay đo tải máy.
    Các ca LocalGia khác vẫn kiểm timeout HTTP và child CLI thật.
    """
    cac_luot = []
    # Đồng hồ logic chỉ của tool; không sửa time của SDK/HTTP server.
    # Chuẩn bị snapshot chậm do tải máy không được hết hạn trước checkpoint.
    monkeypatch.setattr(tool, 'time', SimpleNamespace(
        monotonic=lambda: 100.0, perf_counter=time.perf_counter))

    class DungTaiCheckpoint(BaseException):
        pass

    def run(cmd, *, input, stdout, stderr, timeout):
        assert cmd[-1] == '--_ca-con'
        assert stdout == stderr == subprocess.PIPE
        tham_so = json.loads(input)
        bo_con = tham_so.pop('bo')
        checkpoint = None

        def nhan(k):
            nonlocal checkpoint
            r = k['tung_ca'][1]
            if (r['so_doan_ai_xong'] == so_doan_ai_xong
                    and r.get('so_luot_local', 0) > 0):
                checkpoint = deepcopy(k)
                raise DungTaiCheckpoint()

        try:
            tool.do(bo_con, that=True, cap_nhat=nhan, **tham_so)
        except DungTaiCheckpoint:
            pass
        assert checkpoint is not None, 'Chuỗi chưa tới checkpoint cần kiểm.'
        cac_luot.append(timeout)
        raw = json.dumps({'bao_cao': checkpoint}, ensure_ascii=False).encode('utf-8') + b'\n'
        raise subprocess.TimeoutExpired(cmd, timeout, output=raw)

    monkeypatch.setattr(tool.subprocess, 'run', run)
    return cac_luot


def test_timeout_cung_cli_dung_child_va_ghi_bao_cao_tung_phan(tmp_path, monkeypatch, capsys):
    ca = ca_demo()
    monkeypatch.setattr(tool,'doc_bo',lambda: bo_demo(ca))
    tep = tmp_path/'timeout-cung.json'
    cac_luot = gia_deadline_child(monkeypatch, so_doan_ai_xong=0)
    with LocalGia() as may:
        code = tool.main(['--that','--url',may.url,'--model','model-demo',
                          '--timeout','2','--bao-cao',str(tep),'--thu-muc-bao-cao',str(tmp_path)])
    k = json.loads(tep.read_text('utf-8'))
    assert code == 1 and cac_luot == [2]
    assert k['so_ca_het_han_cung'] == 1
    assert k['tung_ca'][0]['tinh_trang_do'] == 'đã đo'
    assert k['tung_ca'][1]['tinh_trang_do'] == 'chưa đo đủ'
    assert k['tung_ca'][1]['ma_loi'] == 'HET_HAN_CHUOI'
    assert k['muc_tieu_0_lot'] == 'CHƯA ĐO ĐỦ'
    assert 'orvella' not in tep.read_text('utf-8') + capsys.readouterr().out


def test_bao_cao_trong_repo_can_thu_muc_chi_dinh(tmp_path, monkeypatch):
    monkeypatch.setattr(tool,'GOC',tmp_path)
    thu = tmp_path/'bao-cao-duoc-chi-dinh'
    thu.mkdir()
    tep = thu/'dem.json'
    assert tool.main(['--bao-cao',str(tep)]) == 2
    assert not tep.exists()
    assert tool.main(['--bao-cao',str(tep),'--thu-muc-bao-cao',str(thu)]) == 0
    assert json.loads(tep.read_text('utf-8'))['ket_qua'] is None


def test_che_thua_dinh_danh_qua_toan_chuoi_local_gia():
    ca = ca_demo('linero',chu='DEMO; orvella linero; nội dung.')
    with LocalGia() as may:
        tra_gold(may,['orvella linero'])
        k = do_gia(may,ca)
    r = k['tung_ca'][1]
    assert r['trang_thai'] == 'phat_hanh_che_du'
    # Lớp quy tắc cũng che nhãn DEMO (4 ký tự) ngoài gold. Không bỏ qua
    # phần che thừa này để làm đẹp số đo ca có định danh.
    assert r['so_ky_tu_che_thua'] == len('orvella ') + 4 and r['so_span_che_thua'] == 2
    assert k['ket_qua']['hai_lop']['che_thua_dinh_danh']['so_ca'] == 1


def test_ngoai_le_tien_trinh_cli_van_ghi_ca_truoc(tmp_path,monkeypatch,capsys):
    c1, c2 = ca_demo(), ca_demo('norella finero')
    c2['ma'] = 'D-test-2'
    monkeypatch.setattr(tool,'doc_bo',lambda: bo_demo(c1,c2))
    chay_goc = tool.subprocess.run
    so_lan = 0
    def chay_con(*a,**kw):
        nonlocal so_lan
        so_lan += 1
        if so_lan == 2: raise OSError('DEMO chi tiết bí mật không được in')
        return chay_goc(*a,**kw)
    monkeypatch.setattr(tool.subprocess,'run',chay_con)
    tep = tmp_path/'ngoai-le.json'
    with LocalGia() as may:
        tra_gold(may,['orvella linero'])
        code = tool.main(['--that','--url',may.url,'--model','model-demo','--bao-cao',str(tep),
                          '--thu-muc-bao-cao',str(tmp_path)])
    k = json.loads(tep.read_text('utf-8'))
    assert code == 1 and len(k['tung_ca']) == 4
    assert k['tung_ca'][1]['trang_thai'] == 'phat_hanh_che_du'
    assert k['tung_ca'][3]['tinh_trang_do'] == 'chưa đo đủ'
    assert k['loi_giua_chung'] == 'NGOAI_LE_KHI_DO'
    assert 'chi tiết bí mật' not in tep.read_text('utf-8') + capsys.readouterr().out


def test_timeout_cung_giu_dem_doan_ai_da_xong(tmp_path,monkeypatch):
    ca = ca_demo(chu='DEMO; '+ 'nội dung tổng hợp; '*900+' orvella linero')
    monkeypatch.setattr(tool,'doc_bo',lambda: bo_demo(ca))
    tep = tmp_path/'mot-phan-doan.json'
    cac_luot = gia_deadline_child(monkeypatch, so_doan_ai_xong=1)
    with LocalGia(tra_loi={'da_quet_het':True,'thuc_the':[]}) as may:
        code = tool.main(['--that','--url',may.url,'--model','model-demo','--timeout','5',
                          '--bao-cao',str(tep),'--thu-muc-bao-cao',str(tmp_path)])
        assert may.so_luot_hoi == 1
    k = json.loads(tep.read_text('utf-8'))
    r = k['tung_ca'][1]
    assert code == 1 and cac_luot == [5] and r['so_doan_ai_xong'] == 1
    assert r['so_doan_ke_hoach'] > 1 and r['du_doan'] is False
    assert r['so_span_lot'] is None and r['tinh_trang_do'] == 'chưa đo đủ'
    assert k['ket_qua']['hai_lop']['phan_tach']['ai_thuc_su_do']['tong_ca'] == 1

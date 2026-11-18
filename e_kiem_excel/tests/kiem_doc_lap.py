"""Kiểm AST/import, cây gói và CoreGia trong tiến trình Python cô lập."""

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

GOI = Path(__file__).resolve().parents[1] / 'goi' / 'e_kiem_excel'
CHO_PHEP = {'e_kiem_excel','kho_tri_thuc_sdk','openpyxl','et_xmlfile','defusedxml'}
TEN_CAM = {'SDKEngine','Bootstrap','kenh_engine','__import__','eval','exec','compile','import_module'}
MODULE_CAM = {'importlib','pickle','subprocess','socket','sqlite3','urllib','sys','builtins','runpy','site'}


def kiem_doc_lap(goi=GOI):
    loi=[]
    for tep in Path(goi).rglob('*'):
        ten=tep.relative_to(goi).as_posix()
        if tep.is_symlink() or (hasattr(tep,'is_junction') and tep.is_junction()):
            loi.append(f'{ten}: liên kết không hợp lệ.')
        if tep.name=='__pycache__' or tep.suffix.lower() in {'.pyc','.pyo'}:
            loi.append(f'{ten}: có bytecode.')
        if not tep.is_file():
            continue
        if tep.stat().st_size>20*1048576:
            loi.append(f'{ten}: tệp quá lớn.')
        if tep.suffix!='.py':
            continue
        try:
            cay=ast.parse(tep.read_text(encoding='utf-8'))
        except (SyntaxError,UnicodeError):
            loi.append(f'{ten}: mã Python không hợp lệ.'); continue
        for nut in ast.walk(cay):
            modules=[]
            if isinstance(nut,ast.Import):
                modules=[x.name for x in nut.names]
            elif isinstance(nut,ast.ImportFrom) and not nut.level:
                modules=[nut.module or '']
            for module in modules:
                goc=module.split('.')[0]
                if goc in MODULE_CAM or goc not in sys.stdlib_module_names|CHO_PHEP:
                    loi.append(f'{ten}:{nut.lineno}: import bị cấm hoặc chưa ghim.')
            if isinstance(nut,ast.Name) and nut.id in TEN_CAM or isinstance(nut,ast.Attribute) and nut.attr in TEN_CAM:
                loi.append(f'{ten}:{nut.lineno}: cơ chế động/kênh cũ bị cấm.')
            if isinstance(nut,ast.Constant) and isinstance(nut.value,str):
                if any(x in nut.value for x in ('kho_tri_thuc.', 'ma-nguon', 'shim-kho_tri_thuc', 'tu-core-cu')):
                    loi.append(f'{ten}:{nut.lineno}: phụ thuộc Core/mã tham chiếu.')
    return loi


def kiem_tien_trinh_sach(goi=GOI):
    modules=['kho_tri_thuc_sdk','openpyxl','et_xmlfile','defusedxml']
    origins=[]
    for ten in modules:
        spec=importlib.util.find_spec(ten)
        if not spec or not spec.origin:
            return ['Thiếu thư viện đã ghim để kiểm độc lập.']
        origins.append(str(Path(spec.origin).parent.parent))
    code=r'''
import sys
sys.dont_write_bytecode=True
sys.path[:0]=sys.argv[1:]
allowed=sys.stdlib_module_names|{'e_kiem_excel','kho_tri_thuc_sdk','openpyxl','et_xmlfile','defusedxml'}
def audit(event,args):
    if event=='import' and args[0].split('.')[0] not in allowed:
        raise ModuleNotFoundError('Import ngoài danh sách cho phép.',name=args[0])
    if event in {'socket.connect','socket.bind','subprocess.Popen','os.system'}:
        raise RuntimeError('Cấm mạng/tiến trình ngoài trong engine.')
sys.addaudithook(audit)
import kho_tri_thuc_sdk, openpyxl, defusedxml, et_xmlfile
assert kho_tri_thuc_sdk.__version__=='2.2.0'
assert openpyxl.__version__=='3.1.5'
assert defusedxml.__version__=='0.7.1'
from openpyxl.xml import DEFUSEDXML
assert DEFUSEDXML
from e_kiem_excel.chay import app
from kho_tri_thuc_sdk.thu import CoreGia
kq=CoreGia().chay_thu_demo(app)
assert len(kq)==3
assert all(k['trang_thai']=='LOI' and k['loi']['ma']=='CHUA_LAM' and k['ket_qua'] is None for k in kq[:2])
assert kq[2]['trang_thai']=='XONG' and kq[2]['ket_qua']['truong']['so_dong']==30
assert not any(n=='kho_tri_thuc' or n.startswith('kho_tri_thuc.') for n in sys.modules)
print('EX_DOC_LAP_DAT')
'''
    try:
        run=subprocess.run([sys.executable,'-I','-B','-S','-c',code,str(Path(goi).resolve()),*sorted(set(origins))],
                           capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30,cwd=goi)
    except (OSError,subprocess.TimeoutExpired):
        return ['Không chạy được tiến trình kiểm độc lập.']
    if run.returncode or 'EX_DOC_LAP_DAT' not in run.stdout:
        return [f'Tiến trình cô lập chưa đạt (mã thoát {run.returncode}); không dùng Core/shim để bù.']
    return []


def main():
    loi=kiem_doc_lap()
    if not loi:
        loi+=kiem_tien_trinh_sach()
    for cau in loi:
        print('[LỖI] '+cau)
    if not loi:
        print('[ĐẠT] AST, cây gói, import cô lập; đã kiểm bằng Core giả (CoreGia), EX-4 đọc bảng thành công; 2 DEMO toàn vẹn CHUA_LAM.')
    return int(bool(loi))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())

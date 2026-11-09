"""AI-5a: BoGhiNhatKy qua SDKEngine, không có kết nối/kho riêng.

Core cấp qua doc_dau_vao()['nhat_ky_ai'] một snapshot có thứ tự tep_ids
(toàn bộ lịch sử được phép đọc), du_lieu_ket_qua và revision_tep_truoc.
Snapshot rỗng phải được Core khai rõ; thiếu/lỗi không có nghĩa chưa có lượt.
Đây là seam tiêm của Core như AI-4a, không là operation/contract công bố mới.
Với bước Hỏi AI v2, cùng đầu vào SDK phải có nguon_core do Core dựng lại
sau đối chiếu provider gói đã cài; không lấy mã prompt từ yeu_cau engine.

Mỗi tệp kết quả chứa đúng một BanGhiCongAI, không chứa prompt/câu trả lời.
Core chịu trách nhiệm quyền, provenance, chống trùng khi phát lại cùng lần
bàn giao, commit và ACK da_ban_giao=True (G2-10/20). Core cấp lịch sử theo
phạm vi thống kê đã xác minh, không lấy phạm vi từ nội dung tệp của engine.
BoGhiBoNho chỉ dùng tính thống kê tạm từ snapshot Core, không làm kho lưu.
Nối vào launcher/drain thật thuộc lát tích hợp; drain phải chờ da_ban_giao().
"""

from collections import deque
from copy import deepcopy
from dataclasses import fields
from datetime import datetime
import io
import json
import math
import re
import threading
from uuid import UUID

from ...sdk_core.engine import SDKEngine
from .lib.cong_ai import BanGhiCongAI, BanGhiHoiAI, BoGhiBoNho, LOAI_VIEC, THONG_BAO, TRUONG_PROVENANCE


class LoiNhatKy(RuntimeError):
    """Core chưa xác nhận hoặc metadata không đọc được; không trả số 0 giả."""


_TRUONG = {f.name for f in fields(BanGhiHoiAI)}
_MA = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}')
_CHON = re.compile(r'(?:uu_tien|co_dinh|du_phong:[1-9][0-9]*)')
_NGUON = ('ma_module', 'ma_function', 'ma_prompt', 'phien_ban_prompt',
          'phap_nhan_id', 'viec_id')


def _kiem_provenance(data, *, day_du):
    """Chỉ mã và số đo; không cho nhét nội dung vào trường metadata sẵn có."""
    if not set(data) & TRUONG_PROVENANCE:
        return
    bat_buoc = TRUONG_PROVENANCE - {'ly_do_chon_model'}
    if not day_du:
        bat_buoc -= {'ma_prompt', 'phien_ban_prompt'}
    if not bat_buoc <= set(data):
        raise LoiNhatKy('NHAT_KY_THIEU_PROVENANCE')
    for key in ('ma_module', 'ma_function', 'ma_prompt'):
        if key in data and (not isinstance(data[key], str) or not _MA.fullmatch(data[key])):
            raise LoiNhatKy('NHAT_KY_DU_LIEU')
    if 'phien_ban_prompt' in data and (not isinstance(data['phien_ban_prompt'], str)
            or not re.fullmatch(r'[1-9][0-9]*', data['phien_ban_prompt'])):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')
    try:
        dau, cuoi = (datetime.fromisoformat(data[k]) for k in ('luc_bat_dau', 'luc_ket_thuc'))
        if (dau.utcoffset() is None or cuoi.utcoffset() is None or cuoi < dau
                or data['luc'] != data['luc_bat_dau']):
            raise ValueError
    except (ValueError, TypeError):
        raise LoiNhatKy('NHAT_KY_DU_LIEU') from None
    for key in ('so_ky_tu_gui', 'so_ky_tu_nhan', 'thoi_gian_ms', 'so_truong_bi_loai',
                'token_vao', 'token_ra'):
        value = data[key]
        if value is None and key in ('token_vao', 'token_ra'):
            continue
        if type(value) is not int or value < 0:
            raise LoiNhatKy('NHAT_KY_DU_LIEU')
    gia = data['chi_phi_uoc_usd']
    if (gia is not None and (type(gia) not in (int, float) or not math.isfinite(gia) or gia < 0)
            or data['trich_dan_hop_le'] is not None and type(data['trich_dan_hop_le']) is not bool):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')
    try:
        UUID(data['ma_yeu_cau'])
        for key in ('phap_nhan_id', 'viec_id', 'de_xuat_id'):
            if data[key] is not None:
                UUID(data[key])
    except (ValueError, TypeError, AttributeError):
        raise LoiNhatKy('NHAT_KY_DU_LIEU') from None
    chon = data.get('ly_do_chon_model')
    model = data['model']
    if any(not isinstance(data[k], str) for k in (
            'ket_qua', 'ket_qua_kiem', 'ma_ly_do_kiem', 'loai_viec')):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')
    if (data['duong'] != 'LOCAL' or data['nha_cung_cap'] != 'local'
            or data['loai_viec'] not in LOAI_VIEC
            or not isinstance(model, str)
            or (model and (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./:+-]{0,199}', model)
                           or '://' in model or re.search(r'\d+\.\d+\.\d+\.\d+', model)))
            or (model and (not isinstance(chon, str) or not _CHON.fullmatch(chon)))
            or (not model and chon is not None)
            or data['ket_qua'] not in ('DAT', 'KHONG_CHAC', 'KHONG_DUNG_DUOC', 'LOI', 'KHONG_GUI')
            or data['ket_qua_kiem'] != ('dat' if data['ket_qua'] == 'DAT' else 'tu_choi')
            or data['ma_ly_do_kiem'] not in {'DAT', *THONG_BAO}
            or any(v not in THONG_BAO and v != chon for v in data['ly_do'])
            or data['ly_do_chuyen_cloud'] or data['ma_luot_mask'] is not None
            or any(data[k] is not None and (not isinstance(data[k], str) or data[k] not in THONG_BAO)
                   for k in ('loi', 'ly_do_khong_gui'))):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')


def _ban_ghi(data, *, day_du=True):
    if (not isinstance(data, dict) or not set(data) <= _TRUONG
            or not _TRUONG - TRUONG_PROVENANCE <= set(data)):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')
    data = dict(data)
    for ten in ('ly_do', 'ly_do_chuyen_cloud'):
        if (not isinstance(data[ten], (list, tuple))
                or any(not isinstance(v, str) for v in data[ten])):
            raise LoiNhatKy('NHAT_KY_DU_LIEU')
        data[ten] = tuple(data[ten])
    if (data['duong'] not in ('LOCAL', 'CLOUD')
            or type(data['da_gui']) is not bool
            or any(not isinstance(data[k], str) or not data[k]
                   for k in ('ma_yeu_cau', 'luc', 'loai_viec'))):
        raise LoiNhatKy('NHAT_KY_DU_LIEU')
    _kiem_provenance(data, day_du=day_du)
    return (BanGhiHoiAI if set(data) & TRUONG_PROVENANCE else BanGhiCongAI)(**data)


def _them_nguon(data, snapshot):
    if not set(data) & TRUONG_PROVENANCE:
        return data
    if snapshot['_legacy'] and not {'ma_prompt', 'phien_ban_prompt'} & set(data):
        # Snapshot cổng dùng chung cũ chỉ có nhat_ky_ai, không phải đầu vào
        # bước Hỏi AI v2. Không áp đặt provenance v2 lên đường tương thích.
        return {k: v for k, v in data.items() if k not in TRUONG_PROVENANCE}
    # doc_dau_vao do Core xác minh bằng provider của gói đã cài. Không đọc
    # yeu_cau/chi_dan hoặc metadata do engine gửi để dựng provenance.
    nguon = snapshot.get('nguon_core')
    if not isinstance(nguon, dict) or not set(_NGUON) <= set(nguon):
        raise LoiNhatKy('NHAT_KY_THIEU_PROVENANCE')
    if any(data.get(k) != nguon[k] for k in ('ma_module', 'ma_function', 'phap_nhan_id', 'viec_id')):
        raise LoiNhatKy('NHAT_KY_NGUON_KHONG_KHOP')
    if any(k in data and data[k] != nguon[k] for k in ('ma_prompt', 'phien_ban_prompt')):
        raise LoiNhatKy('NHAT_KY_NGUON_KHONG_KHOP')
    return _ban_ghi({**data, **{k: nguon[k] for k in _NGUON}}).thanh_dict()


class BoGhiQuaCore:
    """Hiện thực BoGhiNhatKy để tiêm vào CongAI(bo_ghi=...).

    Mọi lần thong_ke đều đọc lại Core; không cache số đo qua các request.
    ghi xếp hàng bytes trước mọi lời gọi Core và chỉ thành công sau ACK.
    Khi lỗi, giữ cả các bản ghi tiếp theo; thu_lai bàn giao tuần tự trước
    khi cho phép engine tự đóng. Metadata/revision đã cấp được giữ khi retry.
    """

    __slots__ = ('__sdk', '__cho', '__khoa')

    def __init__(self, sdk):
        if not isinstance(sdk, SDKEngine):
            raise TypeError('Cần SDKEngine do Core cấp')
        self.__sdk = sdk
        self.__cho = deque()
        self.__khoa = threading.RLock()

    def __repr__(self):
        return 'BoGhiQuaCore(<an>)'

    def __reduce__(self):
        raise TypeError('Không serialize BoGhiQuaCore')

    def _snapshot(self):
        dau_vao = self.__sdk.doc_dau_vao()
        data = dau_vao.get('nhat_ky_ai') if isinstance(dau_vao, dict) else None
        if (not isinstance(data, dict) or 'tep_ids' not in data
                or not isinstance(data['tep_ids'], list)
                or any(not isinstance(v, str) or not v for v in data['tep_ids'])
                or len(set(data['tep_ids'])) != len(data['tep_ids'])):
            raise LoiNhatKy('NHAT_KY_THIEU_SNAPSHOT')
        snapshot = deepcopy(data)
        snapshot['_legacy'] = set(dau_vao) == {'nhat_ky_ai'}
        # Không giữ prompt/tài liệu từ payload trong hàng đợi retry.
        nguon = dau_vao.get('nguon_core')
        snapshot['nguon_core'] = ({k: deepcopy(nguon[k]) for k in _NGUON if k in nguon}
                                 if isinstance(nguon, dict) else None)
        return snapshot

    def ghi(self, ban_ghi):
        if type(ban_ghi) not in (BanGhiCongAI, BanGhiHoiAI):
            raise TypeError('Cần BanGhiCongAI')
        data = _ban_ghi(ban_ghi.thanh_dict(), day_du=False).thanh_dict()
        raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
        with self.__khoa:
            self.__cho.append((raw, None))
            self.thu_lai()

    def _doc_ban_ghi(self, tep_id):
        with self.__sdk.mo_doc(tep_id) as luong:
            try:
                data = json.load(luong)
            except (ValueError, UnicodeError):
                raise LoiNhatKy('NHAT_KY_DU_LIEU') from None
        return _ban_ghi(data)

    def _da_ghi(self, data, snapshot):
        """Cùng mã tương quan đã ACK vẫn chống trùng sau restart bộ ghi."""
        for tep_id in snapshot['tep_ids']:
            cu = self._doc_ban_ghi(tep_id).thanh_dict()
            if (cu['ma_yeu_cau'], cu['duong']) != (data['ma_yeu_cau'], data['duong']):
                continue
            if cu != data:
                raise LoiNhatKy('NHAT_KY_TRUNG_MA_KHAC_NOI_DUNG')
            return True
        return False

    def thu_lai(self):
        """Phát lại cùng bytes/revision; không gọi lại Local/Cloud/provider."""
        with self.__khoa:
            while self.__cho:
                raw, metadata = self.__cho[0]
                if metadata is None:
                    snapshot = self._snapshot()
                    if ('du_lieu_ket_qua' not in snapshot
                            or type(snapshot.get('revision_tep_truoc')) is not int
                            or snapshot['revision_tep_truoc'] < 0):
                        raise LoiNhatKy('NHAT_KY_THIEU_METADATA')
                    metadata = (snapshot['du_lieu_ket_qua'], snapshot['revision_tep_truoc'])
                    data = _them_nguon(json.loads(raw), snapshot)
                    if set(data) & TRUONG_PROVENANCE and self._da_ghi(data, snapshot):
                        self.__cho.popleft()
                        continue
                    raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
                    self.__cho[0] = (raw, metadata)
                data, revision = metadata
                with io.BytesIO(raw) as luong:
                    ack = self.__sdk.ghi_ket_qua(luong=luong, ten='nhat-ky-ai.json',
                        du_lieu=deepcopy(data), revision_tep_truoc=revision)
                if not isinstance(ack, dict) or ack.get('da_ban_giao') is not True:
                    raise LoiNhatKy('NHAT_KY_CHO_ACK')
                self.__cho.popleft()

    def da_ban_giao(self):
        """Seam drain: False khi vẫn còn metadata chưa được Core ACK."""
        with self.__khoa:
            return not self.__cho

    def thong_ke(self, cua_so):
        if type(cua_so) is not int or cua_so < 1:
            raise ValueError('Cửa sổ phải là số nguyên dương')
        with self.__khoa:
            if self.__cho:
                raise LoiNhatKy('NHAT_KY_CHO_ACK')
            snapshot = self._snapshot()
            bo_tinh = BoGhiBoNho()
            for tep_id in snapshot['tep_ids']:
                bo_tinh.ghi(self._doc_ban_ghi(tep_id))
            return bo_tinh.thong_ke(cua_so)

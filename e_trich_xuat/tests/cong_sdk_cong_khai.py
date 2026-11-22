"""Điểm gắn mô phỏng của test qua DuongTruyen công khai, không đổi SDK/runtime."""


def duong_truyen_thu(core, monkeypatch, ma="e_trich_xuat"):
    tao = core.duong_truyen
    dt = tao(ma)
    monkeypatch.setattr(core, "duong_truyen",
                        lambda ma_engine, instance=None: dt if ma_engine == ma else tao(ma_engine, instance))
    return dt

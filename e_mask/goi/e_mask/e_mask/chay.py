"""Cổng SDK: nghiệp vụ chưa triển khai."""
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")

@app.nang_luc("mask.che_van_ban@1")
def che_van_ban(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất.")

@app.nang_luc("mask.mo_che_van_ban@1")
def mo_che_van_ban(viec):
    raise LoiNghiepVu("CHUA_LAM", "Chức năng này chưa được hoàn tất.")

if __name__ == "__main__":
    app.chay()

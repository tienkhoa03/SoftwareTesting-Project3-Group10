# Duy Automation Tests (Level 1 & Level 2)

## Cấu trúc thư mục (đã gộp theo Level)
```
Duy/
  common/
    chromedriver.exe
  requirements.txt
  level1/
    bva/
      bva_login_datadriven.py
      data/BVA_LOGIN.csv
      static/TC00410*.py
    ecp/
      ecp_login_datadriven.py
      data/ECP_LOGIN.csv
      static/TC00400*.py
    register_dt/
      RegisterDTDataDriven.py
      data/REGISTER_DT.csv
    uc_register/
      UCRegisterDataDriven.py
      data/UC_REGISTER.csv
  level2/
    bva/
      level2_bva_login.py
      data/BVA_LOGIN.csv
      locators.csv
    ecp/
      level2_ecp_login.py
      data/ECP_LOGIN.csv
      locators.csv
    register_dt/
      level2_register_dt.py
      data/REGISTER_DT.csv
      locators.csv
    uc_register/
      level2_uc_register.py
      data/UC_REGISTER.csv
      locators.csv
```
> Các thư mục cũ (BVA/, ECP/, register_DT/, UCREGISTERSuite/) vẫn giữ làm backup nhưng đã gộp logic chính vào `level1/` và `level2/` như trên.

## Chuẩn bị
1) (Tùy chọn) kích hoạt venv sẵn có:
```
cd f:\HK251\Testing\btl3\Duy\KR-exported-python-unitest-project
\.venv\Scripts\Activate.ps1
```
2) Cài dependencies (dùng file mới ở root `requirements.txt`):
```
cd f:\HK251\Testing\btl3\Duy
pip install -r requirements.txt
```
3) Đảm bảo `chromedriver.exe` ở `Duy/common`. Nếu đổi vị trí, cập nhật hằng `CHROMEDRIVER_PATH` trong các file.

## Cách chạy Level 1
- BVA:
```
cd f:\HK251\Testing\btl3\Duy\level1\bva
python -m unittest bva_login_datadriven.BVALoginDataDriven
```
- ECP:
```
cd f:\HK251\Testing\btl3\Duy\level1\ecp
python -m unittest ecp_login_datadriven.ECPLoginDataDriven
```
- Register_DT:
```
cd f:\HK251\Testing\btl3\Duy\level1\register_dt
python RegisterDTDataDriven.py
```
- UC Register:
```
cd f:\HK251\Testing\btl3\Duy\level1\uc_register
python UCRegisterDataDriven.py
```

## Cách chạy Level 2 (locator CSV tách riêng)
- BVA:
```
cd f:\HK251\Testing\btl3\Duy\level2\bva
python level2_bva_login.py
```
- ECP:
```
cd f:\HK251\Testing\btl3\Duy\level2\ecp
python level2_ecp_login.py
```
- Register_DT:
```
cd f:\HK251\Testing\btl3\Duy\level2\register_dt
python level2_register_dt.py
```
- UC Register:
```
cd f:\HK251\Testing\btl3\Duy\level2\uc_register
python level2_uc_register.py
```

## Lưu ý flakiness / rate-limit
- Login site có thể trả về thông báo lockout (“exceeded allowed number of login attempts”); các script đã chấp nhận thông báo này như PASS cho case alert.
- Giữa mỗi test case, script đã xóa cookies + session/localStorage và mở tab trắng để giảm lỗi.
- Nếu vẫn bị lockout, tăng `time.sleep(0.8)` lên 1–2s, hoặc dùng email khác nhau cho các case alert/success.

## Dữ liệu
- Tất cả data CSV nằm ở `level1/*/data/` và `level2/*/data/`. Muốn thêm case, thêm dòng cùng format cột.
- Với case success, dùng email mới để tránh “already registered”.

## Push Git (repo chính TESTING-ASS3)
```
cd f:\HK251\Testing\btl3\TESTING-ASS3
git remote add origin https://github.com/ABsievil/TESTING-ASS3.git   # nếu chưa có
git add .
git commit -m "Restructure level1/level2 folders"
git push origin master
```

## Nộp bài gợi ý
- Tạo `submission/Level1` chứa script + CSV level1.
- Tạo `submission/Level2` chứa script + CSV + locators level2.
- Viết báo cáo PDF: mô tả tool, cấu trúc, cách chạy, phân công.
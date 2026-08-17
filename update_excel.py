import openpyxl
import os

# 載入剛剛建立的 xlsx
file_path = os.path.join(os.path.dirname(__file__), 'data.xlsx')
wb = openpyxl.load_workbook(file_path)
sheet = wb.active

# 將第二格（B欄）的前 20 行填入"這是一個好的測試"
for i in range(1, 21):
    sheet.cell(row=i, column=2, value='這是一個好的測試')

# 儲存檔案
wb.save(file_path)

print(f"成功更新 Excel 檔案：{file_path}")

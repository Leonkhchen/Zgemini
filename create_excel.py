import openpyxl
import os

wb = openpyxl.Workbook()
sheet = wb.active

# 迴圈 10 次，將前 10 行的第一格填入 'abcde'
for i in range(1, 11):
    sheet.cell(row=i, column=1, value='abcde')

# 儲存檔案
file_path = os.path.join(os.path.dirname(__file__), 'data.xlsx')
wb.save(file_path)

print(f"成功建立 Excel 檔案：{file_path}")

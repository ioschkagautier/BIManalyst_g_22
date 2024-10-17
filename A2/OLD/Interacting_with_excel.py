import xlwings as xw

# Open the workbook with xlwings
wb = xw.Book('C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/A2/Excel_empty.xlsx')

# Select the sheet
sheet = wb.sheets['Ark1']

# Insert data
data = [
    ['New', 'Data', 'Row', 3],
    ['Another', 'Data', 'Row', 2]
]

# Write data to the top-left corner of the sheet
start_row = 1
start_col = 1

for i, row in enumerate(data):
    sheet.range((start_row + i, start_col)).value = row

# Force recalculation of all formulas in the workbook
wb.api.Application.CalculateFull()

# Retrieve data from column 6 (F) and rows 6, 7, and 8
retrieved_data = sheet.range('F6:F8').value

# Print the retrieved data
print(retrieved_data)

# Save and close the workbook
wb.save()
wb.close()

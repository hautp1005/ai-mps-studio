
import pandas as pd
import openpyxl
from time import sleep

# Open the Excel file
workbook = openpyxl.load_workbook('sz_tc.xlsx')

# Select the worksheet by name
worksheet = workbook['Checklist_']

# Create a new workbook to write the output
output_workbook = openpyxl.Workbook()

# Select the first sheet of the output workbook
output_sheet = output_workbook.active

# Iterate over each row in the original worksheet
for row in worksheet.iter_rows():
    # Create a new row in the output worksheet
    output_row = []
    for cell in row:
        # Check if the cell is within a merged cell range
        if cell.coordinate in [cell_range.coord for cell_range in worksheet.merged_cells.ranges]:
            # Get the merged cell value and add it to the output row
            merged_cell = worksheet.cell(*worksheet.merged_cells(cell.row, cell.column)[0].coord)
            output_row.append(merged_cell.value)
        else:
            # Add the cell value to the output row
            output_row.append(cell.value)

    # Write the output row to the output worksheet
    output_sheet.append(output_row)

# Save the output workbook
output_workbook.save('output.xlsx')
print("Output workbook was succeed")
sleep(1)
print("Starting to read file excel")
# Read file excel
df = pd.read_excel('output.xlsx')

col1 = df['Testcase description']
col2 = df['Test to perform']

# List the required formats
count = 0
na_arr = []
for i in range(len(col1)):
    if pd.isnull(col1[i]) is False:
        na_arr += [i]
        count += 1

print(na_arr)

# Create an objects Series from na_arr
na_series = pd.Series(na_arr)
count = 0
na_series_i = 0
start_na_series = 0
msg = ""

# Export message file
for c_desc_i in range(len(col1)):
    if pd.isnull(col1[c_desc_i]) is False:
        count += 1
        desc = f"Testcase description {count}:"
        print(desc)
        print(col1[c_desc_i])
        for na_series_i in range(start_na_series, len(na_series)):
            test = f"Test to perform {na_series_i + 1}:"
            print(test)
            try:
                print(f"{na_arr[na_series_i]} >> {na_arr[na_series_i + 1]}")
                for k in range(na_arr[na_series_i], na_arr[na_series_i + 1]):
                    if pd.isnull(col2[k]) is False:
                        print(col2[k])
                start_na_series += 1
            except BaseException:
                try:
                    for j in range(max(na_arr), max(na_arr) * 10):
                        if pd.isnull(col2[j]) is False:
                            print(col2[j])
                except BaseException:
                    print("")

            print()
            break

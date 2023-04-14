# import openpyxl
#
# # Open the Excel file
# workbook = openpyxl.load_workbook('sz_tc.xlsx')
#
# # Select the worksheet by name
# worksheet = workbook['Checklist_']
#
# # Create a new workbook to write the output
# output_workbook = openpyxl.Workbook()
#
# # Select the first sheet of the output workbook
# output_sheet = output_workbook.active
#
# # Iterate over each row in the original worksheet
# for row in worksheet.iter_rows():
#     # Create a new row in the output worksheet
#     output_row = []
#     for cell in row:
#         # Check if the cell is within a merged cell range
#         if cell.coordinate in [cell_range.coord for cell_range in worksheet.merged_cells.ranges]:
#             # Get the merged cell value and add it to the output row
#             merged_cell = worksheet.cell(*worksheet.merged_cells(cell.row, cell.column)[0].coord)
#             output_row.append(merged_cell.value)
#         else:
#             # Add the cell value to the output row
#             output_row.append(cell.value)
#
#     # Write the output row to the output worksheet
#     output_sheet.append(output_row)
#
# # Save the output workbook
# output_workbook.save('output.xlsx')

import pandas as pd

# Read the Excel file
df = pd.read_excel('output.xlsx')

# Set display options to show merged cells
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Print the table with merged rows
print(df)

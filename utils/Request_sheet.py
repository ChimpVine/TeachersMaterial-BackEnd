import gspread
import os
def update_google_sheet(full_name, email, description, sheet_id):
    try:
        file_path = os.path.join('credentials.json')
        # Authenticate and open the Google Sheet
        gc = gspread.service_account(filename=file_path)  # Your service account JSON file
        workbook = gc.open_by_key(sheet_id)
        sheet = workbook.sheet1  # Use the first sheet in the workbook

        # Find the next available row
        next_row = len(sheet.get_all_values()) + 1

        # Batch update to improve performance
        cell_list = sheet.range(f'A{next_row}:G{next_row}')
        values = [full_name, email, description]

        for cell, value in zip(cell_list, values):
            cell.value = value
        
        sheet.update_cells(cell_list)

        print(f"Data successfully written to row {next_row}")

        return {"success": True, "message": "Data written to Google Sheet"}

    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return {"success": False, "error": str(e)}

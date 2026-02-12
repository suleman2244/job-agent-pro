import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from config import OUTPUT_FILENAME

def export_to_excel(jobs_list):
    """
    Exports a list of job dictionaries to a professional, formatted Excel file using openpyxl directly.
    This replaces pandas to reduce the deployment size for Vercel.
    """
    if not jobs_list:
        print("No jobs to export.")
        return None

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Job Leads"

        columns = ['title', 'company', 'location', 'link', 'emails', 'source']
        ws.append([col.capitalize() for col in columns])

        # --- PROFESSIONAL STYLING ---
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        left_wrap = Alignment(horizontal='left', vertical='top', wrap_text=True)
        link_font = Font(color="0563C1", underline="single")

        # Style header row
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align

        # Add data
        for job in jobs_list:
            row_data = []
            for col in columns:
                val = job.get(col, "")
                if isinstance(val, list):
                    val = "\n".join(val)
                # Clean strings for Excel
                if isinstance(val, str):
                    val = "".join(c for c in val if c.isprintable() or c in "\n\r\t")
                row_data.append(val)
            ws.append(row_data)

        # Style data rows and add hyperlinks
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
            for cell in row:
                cell.alignment = left_wrap
                
                # Check for link column (Column 4 corresponds to index 3 in 0-based, but 4 in 1-based)
                if cell.column == 4:
                    raw_url = cell.value
                    if raw_url and str(raw_url).startswith("http"):
                        cell.value = f'=HYPERLINK("{raw_url}", "OPEN JOB POSTING")'
                        cell.font = link_font

        # --- AUTO-ADJUST COLUMN WIDTHS ---
        column_widths = {
            1: 40, # Title
            2: 25, # Company
            3: 20, # Location
            4: 25, # Link
            5: 35, # Emails
            6: 15  # Source
        }
        for col_idx, width in column_widths.items():
            col_letter = ws.cell(row=1, column=col_idx).column_letter
            ws.column_dimensions[col_letter].width = width

        # Freeze panes
        ws.freeze_panes = 'A2'

        wb.save(OUTPUT_FILENAME)
        print(f"Successfully exported {len(jobs_list)} jobs to {OUTPUT_FILENAME}")
        return os.path.abspath(OUTPUT_FILENAME)
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None

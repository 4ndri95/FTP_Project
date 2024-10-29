import os
import pandas as pd
from datetime import datetime
import re  

def collect_pdfs(directories):
    pdf_files = []
    for directory in directories:
        try:
            for file in os.listdir(directory):
                if file.endswith('.pdf'):
                    cleaned_uc = re.sub(r'\D', '', file) 
                    pdf_files.append(cleaned_uc)
        except FileNotFoundError:
            print(f"Directory not found: {directory}")
    return pdf_files

directories = [
    '/path/to/directory1',
    '/path/to/directory2',
    '/path/to/directory3',
    '/path/to/directory4'
]

pdf_files = collect_pdfs(directories)

df = pd.DataFrame(pdf_files, columns=['UC'])

current_date = datetime.now().strftime("%d.%m.%Y")

spreadsheet_name = f"Processes retrieved from FTP on {current_date}.xlsx"

df.to_excel(spreadsheet_name, index=False)

print(f"Spreadsheet created: {spreadsheet_name}")
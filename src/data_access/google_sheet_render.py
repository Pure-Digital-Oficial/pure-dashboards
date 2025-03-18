import os
import gspread
import pandas as pd
from dotenv import load_dotenv
import json
import base64

class GoogleSheetsReader:
    def __init__(self):
        load_dotenv(dotenv_path=".env")
        self.spreadsheet_url = os.getenv("GOOGLE_SHEETS_URL")
        self.worksheet_name = os.getenv('GOOGLE_SHEETS_TIME_NOTES_WORKSHEET')
        service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")
        
        self.service_account_info = json.loads(base64.b64decode(service_account_info).decode())
        self.credentials = gspread.service_account_from_dict(self.service_account_info)

    def formalize_data(self):
        self.data['Nome'] = self.data['Nome'].str.strip()
        self.data['Nome'] = self.data['Nome'].str.upper()
        self.data['Modalidade'] = self.data['Modalidade'].str.strip()
        self.data['Modalidade'] = self.data['Modalidade'].str.upper()
        self.data['Horas'] = self.data['Horas'].str.replace(',', '.')
        self.data['Horas'] = pd.to_numeric(self.data['Horas'])
        self.data['Data'] = self.data['Data'].str.strip()
        self.data['Data'] = pd.to_datetime(self.data['Data'], format='%d/%m/%Y')
        self.data['AnoMes'] = self.data['Data'].dt.to_period('M')
        self.data['Projeto'] = self.data['Projeto'].str.upper()

    def get_dataframe(self):
        spreadsheet = self.credentials.open_by_url(self.spreadsheet_url)
        worksheet = spreadsheet.worksheet(self.worksheet_name)

        data = worksheet.get_all_values()

        columns = data.pop(0)

        self.data = pd.DataFrame(data=data, columns=columns)
        self.formalize_data()

        return self.data
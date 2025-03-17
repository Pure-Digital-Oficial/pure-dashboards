import os
import gspread
import pandas as pd
from dotenv import load_dotenv

class GoogleSheetsReader:
    def __init__(self, service_account_file="service-account.json"):
        load_dotenv(dotenv_path="../.env")
        self.spreadsheet_url = os.getenv("GOOGLE_SHEETS_URL")
        self.worksheet_name = os.getenv('GOOGLE_SHEETS_TIMEKEPPING_WORKSHEET')
        self.credentials = gspread.service_account(filename=service_account_file)

    def get_dataframe(self):
        spreadsheet = self.credentials.open_by_url(self.spreadsheet_url)
        worksheet = spreadsheet.worksheet(self.worksheet_name)

        data = worksheet.get_all_values()

        columns = data.pop(0)

        data = pd.DataFrame(data=data, columns=columns)
        data['Nome'] = data['Nome'].str.strip()
        data['Nome'] = data['Nome'].str.upper()
        data['Modalidade'] = data['Modalidade'].str.strip()
        data['Modalidade'] = data['Modalidade'].str.upper()
        data['Horas'] = data['Horas'].str.replace(',', '.')
        data['Horas'] = pd.to_numeric(data['Horas'])
        data['Data'] = data['Data'].str.strip()
        data['Data'] = pd.to_datetime(data['Data'], format='%d/%m/%Y')
        data['AnoMes'] = data['Data'].dt.to_period('M')

        return data
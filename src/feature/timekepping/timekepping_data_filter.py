import pandas as pd

class TimekeppingDataFilter:
    def __init__(self, data):
        self.data = data

    def filter_by_name(self, selected_name):
        if selected_name != 'Todos':
            self.data = self.data[self.data['Nome'].str.upper() == selected_name]
        return self

    def filter_by_modality(self, selected_modality):
        if selected_modality != 'Todos':
            self.data = self.data[self.data['Modalidade'].str.upper() == selected_modality]
        return self

    def filter_by_year(self, selected_year, date_column):
        if selected_year != 'Todos':
            self.data = self.data[pd.to_datetime(date_column, format='%d/%m/%Y').dt.year == selected_year]
        return self

    def filter_by_month(self, selected_month, date_column, month_mapping):
        if selected_month != 'Todos':
            month_number = list(month_mapping.keys())[list(month_mapping.values()).index(selected_month)]
            self.data = self.data[pd.to_datetime(date_column, format='%d/%m/%Y').dt.month == month_number]
        return self
    
    def filter_by_project(self, selected_project):
        if selected_project != 'Todos':
            self.data = self.data[self.data['Projeto'].str.upper() == selected_project]
        return self


    def get_filtered_data(self):
        return self.data
import streamlit as st
import pandas as pd
from data_access.google_sheet_render import GoogleSheetsReader

class TimekeppingDashboard:
    def __init__(self):
        pass
    
    def renderPage(self):
        readerGoogle = GoogleSheetsReader()
        data = readerGoogle.get_dataframe()

        monthPtBr = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }

        st.set_page_config(layout='wide')
        names = data['Nome'].str.strip()
        names = names.str.upper().unique().tolist()

        modalities = data['Modalidade'].str.strip()
        modalities = modalities.str.upper().unique().tolist()

        filterData = data['Data'].str.strip()
        months = pd.to_datetime(filterData, format='%d/%m/%Y').dt.month.sort_values(ascending=True).unique().tolist()
        months = [monthPtBr[months] for months in months]
        years = pd.to_datetime(filterData, format='%d/%m/%Y').dt.year.sort_values(ascending=True).unique().tolist()

        st.title('DASHBOARD PURE DIGITAL :shopping_trolley:')

        st.sidebar.title('Filtros')
        selected_name = st.sidebar.selectbox('Equipe', ['Todos'] + names)
        selected_modality = st.sidebar.selectbox('Modalidades', ['Todos'] + modalities)
        selected_year = st.sidebar.selectbox('Ano', ['Todos'] + years)
        selected_month = st.sidebar.selectbox('Mês', ['Todos'] + months)

        filtered_data = data.copy()

        if selected_name != 'Todos':
            filtered_data = filtered_data[filtered_data['Nome'].str.upper() == selected_name]

        if selected_modality != 'Todos':
            filtered_data = filtered_data[filtered_data['Modalidade'].str.upper() == selected_modality]

        if selected_year != 'Todos':
            filtered_data = filtered_data[pd.to_datetime(filterData, format='%d/%m/%Y').dt.year == selected_year]

        if selected_month != 'Todos':
            month_number = list(monthPtBr.keys())[list(monthPtBr.values()).index(selected_month)]
            filtered_data = filtered_data[pd.to_datetime(filterData, format='%d/%m/%Y').dt.month == month_number]
        
        st.dataframe(filtered_data)
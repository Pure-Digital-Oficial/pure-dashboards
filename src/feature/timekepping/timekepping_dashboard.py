# main.py
import streamlit as st
import pandas as pd
from data_access.google_sheet_render import GoogleSheetsReader
from feature.timekepping.timekepping_data_filter import TimekeppingDataFilter

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
        months = [monthPtBr[month] for month in months]
        years = pd.to_datetime(filterData, format='%d/%m/%Y').dt.year.sort_values(ascending=True).unique().tolist()

        st.title('DASHBOARD PURE DIGITAL :shopping_trolley:')

        st.sidebar.title('Filtros')
        selected_name = st.sidebar.selectbox('Equipe', ['Todos'] + names)
        selected_modality = st.sidebar.selectbox('Modalidades', ['Todos'] + modalities)
        selected_year = st.sidebar.selectbox('Ano', ['Todos'] + years)
        selected_month = st.sidebar.selectbox('Mês', ['Todos'] + months)

        data_filter = TimekeppingDataFilter(data)
        filtered_data = data_filter \
            .filter_by_name(selected_name) \
            .filter_by_modality(selected_modality) \
            .filter_by_year(selected_year, filterData) \
            .filter_by_month(selected_month, filterData, monthPtBr) \
            .get_filtered_data()

        tabQuantity = st.tabs(['Apontamentos'])[0]

        with tabQuantity:
            columnLeft, columnRight = st.columns(2)
            with columnLeft:
                st.metric('Qtd Horas Apontadas', pd.to_numeric(filtered_data['Horas'].str.replace(',', '.')).sum())
            with columnRight:
                st.metric('Qtd de Apontamentos', filtered_data['Horas'].count())
        
        st.dataframe(filtered_data)
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
        name = data['Nome'].str.strip()
        name = name.str.upper().unique().tolist()

        modality = data['Modalidade'].str.strip()
        modality = modality.str.upper().unique().tolist()

        filterData = data['Data'].str.strip()
        mes = pd.to_datetime(filterData, format='%d/%m/%Y').dt.month.sort_values(ascending=True).unique().tolist()
        mes = [monthPtBr[mes] for mes in mes]
        ano = pd.to_datetime(filterData, format='%d/%m/%Y').dt.year.sort_values(ascending=True).unique().tolist()

        st.title('DASHBOARD PURE DIGITAL :shopping_trolley:')

        st.sidebar.title('Filtros')
        st.sidebar.selectbox('Equipe', ['Todos'] + name)
        st.sidebar.selectbox('Modalidades', ['Todos'] + modality)
        st.sidebar.selectbox('Ano', ['Todos'] + ano)
        st.sidebar.selectbox('Mês',  ['Todos'] + mes)

        st.dataframe(data)
# main.py
import streamlit as st
import pandas as pd
import plotly.express as px
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
        data['Nome'] = data['Nome'].str.strip()
        data['Nome'] = data['Nome'].str.upper()
        data['Modalidade'] = data['Modalidade'].str.strip()
        data['Modalidade'] = data['Modalidade'].str.upper()
        data['Horas'] = data['Horas'].str.replace(',', '.')
        data['Horas'] = pd.to_numeric(data['Horas'])

        names = data['Nome'].unique().tolist()
        modalities = data['Modalidade'].unique().tolist()

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

        # Tables
        sumHoursFromTeamMember = filtered_data.groupby('Nome')[['Horas']].sum()
        
        quantityHoursFromTeamMember = filtered_data.groupby('Nome')[['Horas']].count()

        # Graphs
        fig_sum_hours_team = px.bar(
            sumHoursFromTeamMember,
            text_auto = True,
            title = 'Horas apontadas por Membro'
        )

        fig_quantity_hours_team = px.bar(
            quantityHoursFromTeamMember,
            text_auto = True,
            orientation = 'h',
            title = 'Quantidade de Horas apontadas por Membro'
        )

        
        # Views
        tabQuantity = st.tabs(['Apontamentos'])[0]

        with tabQuantity:
            columnLeft, columnRight = st.columns(2)
            with columnLeft:
                st.metric('Qtd Horas Apontadas', pd.to_numeric(filtered_data['Horas']).sum())
                st.plotly_chart(fig_sum_hours_team, use_container_width = True)
            
            with columnRight:
                st.metric('Qtd de Apontamentos', filtered_data['Horas'].count())
                st.plotly_chart(fig_quantity_hours_team, use_container_width = True)
        
        st.dataframe(filtered_data)
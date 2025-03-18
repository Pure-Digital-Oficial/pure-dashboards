import streamlit as st
import pandas as pd
import plotly.express as px
from data_access.google_sheet_render import GoogleSheetsReader
from feature.data.time_notes_data_filter import TimeNotesDataFilter
from feature.data.time_notes_generate_charts import TimeNotesGenerateCharts

class TimeNotesDashboard:
    def __init__(self):
        self.readerGoogle = GoogleSheetsReader()
        self.data = self.readerGoogle.get_dataframe()
        self.monthPtBr = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro',
            10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
    
    def setup_filters(self):
        st.sidebar.title('Filtros')
        self.filterData = self.data['Data']
        names = self.data['Nome'].unique().tolist()
        modalities = self.data['Modalidade'].unique().tolist()
        projects = self.data['Projeto'].str.upper().unique().tolist()        
        months = self.filterData.dt.month.sort_values(ascending=True).unique().tolist()
        months = [self.monthPtBr[month] for month in months]
        years = self.filterData.dt.year.sort_values(ascending=True).unique().tolist()
        
        self.selected_name = st.sidebar.selectbox('Equipe', ['Todos'] + names)
        self.selected_modality = st.sidebar.selectbox('Modalidades', ['Todos'] + modalities)
        self.selected_year = st.sidebar.selectbox('Ano', ['Todos'] + years)
        self.selected_month = st.sidebar.selectbox('Mês', ['Todos'] + months)
        self.selected_project = st.sidebar.selectbox('Projetos', ['Todos'] + projects)
        
    def apply_filters(self):
        data_filter = TimeNotesDataFilter(self.data)
        self.filtered_data = data_filter \
            .filter_by_name(self.selected_name) \
            .filter_by_modality(self.selected_modality) \
            .filter_by_year(self.selected_year, self.filterData) \
            .filter_by_month(self.selected_month, self.filterData, self.monthPtBr) \
            .filter_by_project(self.selected_project) \
            .get_filtered_data()

    def render_layout(self):
        charts = TimeNotesGenerateCharts(self.filtered_data, self.monthPtBr).generate_charts()
        tabHours, tabQuantity = st.tabs(['Horas', 'Quantidade'])

        with tabHours:
            columnLeft, columnRight = st.columns(2)
            with columnLeft:
                st.metric('Soma Horas Apontadas', pd.to_numeric(self.filtered_data['Horas']).sum())
                st.plotly_chart(charts['fig_sum_hours_team'], use_container_width = True)
                st.plotly_chart(charts['fig_sum_hours_feature'], use_container_width = True)
            
            with columnRight:
                st.metric('Qtd de Apontamentos', self.filtered_data['Horas'].count())
                st.plotly_chart(charts['fig_sum_hours_month'], use_container_width = True)
                st.plotly_chart(charts['fig_sum_hours_project'], use_container_width = True)

        with tabQuantity:
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    st.metric('Soma Horas Apontadas', pd.to_numeric(self.filtered_data['Horas']).sum())
                    st.plotly_chart(charts['fig_quantity_hours_team'], use_container_width = True)
                    st.plotly_chart(charts['fig_quantity_hours_feature'], use_container_width = True)

                with columnRight:
                    st.metric('Qtd de Apontamentos', self.filtered_data['Horas'].count())
                    st.plotly_chart(charts['fig_quantity_hours_month'], use_container_width = True)
                    st.plotly_chart(charts['fig_quantity_hours_project'], use_container_width = True)
        
        st.dataframe(charts['details'], use_container_width = True)
    
    def render_page(self):
        st.title('APONTAMENTOS HORAS TRABALHADAS')
        self.setup_filters()
        self.apply_filters()
        self.render_layout()

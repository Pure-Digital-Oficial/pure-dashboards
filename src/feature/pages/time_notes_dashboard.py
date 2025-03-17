import streamlit as st
import pandas as pd
import plotly.express as px
from data_access.google_sheet_render import GoogleSheetsReader
from feature.data.time_notes_data_filter import TimeNotesDataFilter

class TimeNotesDashboard:
    def __init__(self):
        self.readerGoogle = GoogleSheetsReader()
        self.data = self.readerGoogle.get_dataframe()
        self.monthPtBr = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro',
            10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        self.featuresMap = {
            'DEVOPS': '#0a53a8', 'BACKEND': '#b10202', 'FRONTEND': '#5ed3f3',
            'UI/UX': '#cca1e9', 'VENDAS': '#0da543', 'ESTUDOS': '#ff8f00',
            'MANUTENÇÃO': '#753800', 'NOSSA EMPRESA': '#e8eaed',
            'REUNIÃO': '#0066fe', 'ANALISE': '#dd11a3'
        }
    
    def ajustTitle(self, text, module):
        if module.lower() == "s":
            return f'{text} (SOMA)'
        elif module.lower() == "q":
            return f'{text} (QUANTIDADE)'
        else:
            return "Entrada inválida"

    def setupFilters(self):
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
        
    def applyFilters(self):
        data_filter = TimeNotesDataFilter(self.data)
        self.filtered_data = data_filter \
            .filter_by_name(self.selected_name) \
            .filter_by_modality(self.selected_modality) \
            .filter_by_year(self.selected_year, self.filterData) \
            .filter_by_month(self.selected_month, self.filterData, self.monthPtBr) \
            .filter_by_project(self.selected_project) \
            .get_filtered_data()
    
    def generateCharts(self):
        # Combined aggregations to avoid redundant calculations
        team_member_agg = self.filtered_data.groupby('Nome')['Horas'].agg(['sum', 'count']).reset_index()
        feature_agg = self.filtered_data.groupby('Modalidade')['Horas'].agg(['sum', 'count']).reset_index()
        project_agg = self.filtered_data.groupby('Projeto')['Horas'].agg(['sum', 'count']).reset_index()
        
        # Month Agregation
        month_agg = self.filtered_data.groupby('AnoMes')['Horas'].agg(['sum', 'count']).reset_index()
        month_agg['Ano'] = month_agg['AnoMes'].dt.year
        month_agg['Mes'] = month_agg['AnoMes'].dt.month.map(self.monthPtBr)
        month_agg.drop(columns=['AnoMes'], inplace=True)

        # Details
        details = self.filtered_data[['Nome', 'Modalidade', 'Feature', 'Observacao', 'Problemas', 'Duvidas']].set_index("Nome")

        # Create bar graphs
        def create_bar_chart(data, x, y, title, yaxis_title='Horas'):
            return px.bar(data, x=x, y=y, text_auto=True, title=title).update_layout(yaxis_title=yaxis_title)

        # Create line graphs
        def create_line_chart(data, x, y, color, title, yaxis_title='Horas'):
            return px.line(data, x=x, y=y, markers=True, range_y=(0, data[y].max()), color=color, line_dash=color, title=title).update_layout(yaxis_title=yaxis_title)

        # Create pizza graphs
        def create_pie_chart(data, names, values, title, color_map=None):
            return px.pie(data, names=names, values=values, hole=.3, color=names, color_discrete_map=color_map, title=title)

        return {
            "fig_sum_hours_team": create_bar_chart(team_member_agg, x='Nome', y='sum', title=self.ajustTitle('Horas apontadas por Membro ', 's')),
            "fig_quantity_hours_team": create_bar_chart(team_member_agg, x='Nome', y='count', title=self.ajustTitle('Horas apontadas por Membro ', 'q')),
            "fig_sum_hours_month": create_line_chart(month_agg, x='Mes', y='sum', color='Ano', title=self.ajustTitle('Apontamentos Mensais', 's')),
            "fig_quantity_hours_month": create_line_chart(month_agg, x='Mes', y='count', color='Ano', title=self.ajustTitle('Apontamentos Mensais', 'q')),
            "fig_sum_hours_feature": create_pie_chart(feature_agg, names='Modalidade', values='sum', title=self.ajustTitle('Horas apontadas por Modalidade', 's'), color_map=self.featuresMap),
            "fig_quantity_hours_feature": create_pie_chart(feature_agg, names='Modalidade', values='count', title=self.ajustTitle('Horas apontadas por Modalidade', 'q'), color_map=self.featuresMap),
            "fig_sum_hours_project": create_pie_chart(project_agg, names='Projeto', values='sum', title=self.ajustTitle('Horas apontadas por Projeto', 's')),
            "fig_quantity_hours_project": create_pie_chart(project_agg, names='Projeto', values='count', title=self.ajustTitle('Horas apontadas por Projeto', 'q')),
            "details": details
        }

    def renderLayout(self):
        charts = self.generateCharts()
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
    
    def renderPage(self):
        st.title('APONTAMENTOS HORAS TRABALHADAS')
        self.setupFilters()
        self.applyFilters()
        self.renderLayout()

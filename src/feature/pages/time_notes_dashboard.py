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
    
    def normalizeData(self):
        self.data['Nome'] = self.data['Nome'].str.strip()
        self.data['Nome'] = self.data['Nome'].str.upper()
        self.data['Modalidade'] = self.data['Modalidade'].str.strip()
        self.data['Modalidade'] = self.data['Modalidade'].str.upper()
        self.data['Horas'] = self.data['Horas'].str.replace(',', '.')
        self.data['Horas'] = pd.to_numeric(self.data['Horas'])
        self.data['Data'] = self.data['Data'].str.strip()
        self.data['Data'] = pd.to_datetime(self.data['Data'], format='%d/%m/%Y')
        self.data['AnoMes'] = self.data['Data'].dt.to_period('M')

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

    def renderPage(self):
        st.title('APONTAMENTOS HORAS TRABALHADAS')
        self.normalizeData()
        self.setupFilters()
        self.applyFilters()
        
        # Tables
        sumHoursFromTeamMember = self.filtered_data.groupby('Nome')[['Horas']].sum()
        sumHoursFromFeature = self.filtered_data.groupby('Modalidade', as_index=False)[['Horas']].sum()
        sumHoursFromProject = self.filtered_data.groupby('Projeto', as_index=False)[['Horas']].sum()
        
        quantityHoursFromTeamMember = self.filtered_data.groupby('Nome')[['Horas']].count()
        quantityHoursFromFeature = self.filtered_data.groupby('Modalidade', as_index=False)[['Horas']].count()
        quantityHoursFromProject = self.filtered_data.groupby('Projeto', as_index=False)[['Horas']].count()

        sumHoursFromMonth = self.filtered_data.groupby('AnoMes', as_index=False)[['Horas']].sum()
        sumHoursFromMonth['Ano'] = sumHoursFromMonth['AnoMes'].dt.year
        sumHoursFromMonth['Mes'] = sumHoursFromMonth['AnoMes'].dt.month
        sumHoursFromMonth['Mes'] = sumHoursFromMonth['Mes'].map(self.monthPtBr)
        sumHoursFromMonth = sumHoursFromMonth.drop(columns=['AnoMes'])

        quantityHoursFromMonth = self.filtered_data.groupby('AnoMes', as_index=False)[['Horas']].count()
        quantityHoursFromMonth['Ano'] = quantityHoursFromMonth['AnoMes'].dt.year
        quantityHoursFromMonth['Mes'] = quantityHoursFromMonth['AnoMes'].dt.month
        quantityHoursFromMonth['Mes'] = quantityHoursFromMonth['Mes'].map(self.monthPtBr)
        quantityHoursFromMonth = quantityHoursFromMonth.drop(columns=['AnoMes'])

        details = self.filtered_data[['Nome', 'Modalidade', 'Feature', 'Observacao', 'Problemas', 'Duvidas']]
        details.set_index("Nome", inplace=True)

        # Graphs
        fig_sum_hours_team = px.bar(
            sumHoursFromTeamMember,
            text_auto = True,
            title = self.ajustTitle('Horas apontadas por Membro ', 's')
        )
        fig_sum_hours_team.update_layout(yaxis_title = 'Horas')

        fig_quantity_hours_team = px.bar(
            quantityHoursFromTeamMember,
            text_auto = True,
            title = self.ajustTitle('Horas apontadas por Membro ', 'q')
        )
        fig_quantity_hours_team.update_layout(yaxis_title = 'Horas')

        fig_sum_hours_month = px.line(sumHoursFromMonth,
                             x= 'Mes',
                             y= 'Horas',
                             markers=True,
                             range_y= (0, sumHoursFromMonth.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= self.ajustTitle('Apontamentos Mensais', 's'))
        fig_sum_hours_month.update_layout(yaxis_title = 'Horas')

        fig_quantity_hours_month = px.line(quantityHoursFromMonth,
                             x= 'Mes',
                             y= 'Horas',
                             markers=True,
                             range_y= (0, quantityHoursFromMonth.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= self.ajustTitle('Apontamentos Mensais', 'q'))
        fig_quantity_hours_month.update_layout(yaxis_title = 'Horas')
        
        fig_sum_hours_feature = px.pie(sumHoursFromFeature, 
                                       names='Modalidade', 
                                       values='Horas',
                                       hole=.3,
                                       color='Modalidade',
                                       color_discrete_map=self.featuresMap,
                                       title= self.ajustTitle('Horas apontadas por Modalidade', 's'))
        
        fig_quantity_hours_feature = px.pie(quantityHoursFromFeature, 
                                       names='Modalidade', 
                                       values='Horas',
                                       hole=.3,
                                       color='Modalidade',
                                       color_discrete_map=self.featuresMap,
                                       title= self.ajustTitle('Horas apontadas por Modalidade', 'q'))
        
        fig_sum_hours_project = px.pie(sumHoursFromProject, 
                                       names='Projeto', 
                                       values='Horas',
                                       hole=.3,
                                       color='Projeto',
                                       title= self.ajustTitle('Horas apontadas por Projeto', 's'))
        
        fig_quantity_hours_project = px.pie(quantityHoursFromProject, 
                                       names='Projeto', 
                                       values='Horas',
                                       hole=.3,
                                       color='Projeto',
                                       title= self.ajustTitle('Horas apontadas por Projeto', 'q'))

        # Views
        tabHours, tabQuantity = st.tabs(['Horas', 'Quantidade'])

        with tabHours:
            columnLeft, columnRight = st.columns(2)
            with columnLeft:
                st.metric('Soma Horas Apontadas', pd.to_numeric(self.filtered_data['Horas']).sum())
                st.plotly_chart(fig_sum_hours_team, use_container_width = True)
                st.plotly_chart(fig_sum_hours_feature, use_container_width = True)
            
            with columnRight:
                st.metric('Qtd de Apontamentos', self.filtered_data['Horas'].count())
                st.plotly_chart(fig_sum_hours_month, use_container_width = True)
                st.plotly_chart(fig_sum_hours_project, use_container_width = True)

        with tabQuantity:
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    st.metric('Soma Horas Apontadas', pd.to_numeric(self.filtered_data['Horas']).sum())
                    st.plotly_chart(fig_quantity_hours_team, use_container_width = True)
                    st.plotly_chart(fig_quantity_hours_feature, use_container_width = True)

                with columnRight:
                    st.metric('Qtd de Apontamentos', self.filtered_data['Horas'].count())
                    st.plotly_chart(fig_quantity_hours_month, use_container_width = True)
                    st.plotly_chart(fig_quantity_hours_project, use_container_width = True)
        
        st.dataframe(details, use_container_width = True)
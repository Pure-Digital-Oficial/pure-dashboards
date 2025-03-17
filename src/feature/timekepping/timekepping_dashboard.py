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

        featuresMap = {
            'DEVOPS':'#0a53a8',
            'BACKEND':'#b10202',
            'FRONTEND':'#5ed3f3',
            'UI/UX':'#cca1e9',
            'VENDAS':'#0da543',
            'ESTUDOS':'#ff8f00',
            'MANUTENÇÃO':'#753800',
            'NOSSA EMPRESA':'#e8eaed',
            'REUNIÃO':'#0066fe',
            'ANALISE':'#dd11a3'
        }

        st.set_page_config(layout='wide')
        st.title('DASHBOARD PURE DIGITAL :rocket:')

        # Normalize Data
        data['Nome'] = data['Nome'].str.strip()
        data['Nome'] = data['Nome'].str.upper()
        data['Modalidade'] = data['Modalidade'].str.strip()
        data['Modalidade'] = data['Modalidade'].str.upper()
        data['Horas'] = data['Horas'].str.replace(',', '.')
        data['Horas'] = pd.to_numeric(data['Horas'])
        data['Data'] = data['Data'].str.strip()
        data['Data'] = pd.to_datetime(data['Data'], format='%d/%m/%Y')
        data['AnoMes'] = data['Data'].dt.to_period('M')

        filterData = data['Data']
        
        # Filters Data
        names = data['Nome'].unique().tolist()
        modalities = data['Modalidade'].unique().tolist()
        projects = data['Projeto'].str.upper().unique().tolist()        
        months = filterData.dt.month.sort_values(ascending=True).unique().tolist()
        months = [monthPtBr[month] for month in months]
        years = filterData.dt.year.sort_values(ascending=True).unique().tolist()

        # Filters
        st.sidebar.title('Filtros')
        selected_name = st.sidebar.selectbox('Equipe', ['Todos'] + names)
        selected_modality = st.sidebar.selectbox('Modalidades', ['Todos'] + modalities)
        selected_year = st.sidebar.selectbox('Ano', ['Todos'] + years)
        selected_month = st.sidebar.selectbox('Mês', ['Todos'] + months)
        selected_project = st.sidebar.selectbox('Projetos', ['Todos'] + projects)
            
        data_filter = TimekeppingDataFilter(data)
        filtered_data = data_filter \
            .filter_by_name(selected_name) \
            .filter_by_modality(selected_modality) \
            .filter_by_year(selected_year, filterData) \
            .filter_by_month(selected_month, filterData, monthPtBr) \
            .filter_by_project(selected_project) \
            .get_filtered_data()

        # Tables
        sumHoursFromTeamMember = filtered_data.groupby('Nome')[['Horas']].sum()
        sumHoursFromFeature = filtered_data.groupby('Modalidade', as_index=False)[['Horas']].sum()
        sumHoursFromProject = filtered_data.groupby('Projeto', as_index=False)[['Horas']].sum()
        
        quantityHoursFromTeamMember = filtered_data.groupby('Nome')[['Horas']].count()
        quantityHoursFromFeature = filtered_data.groupby('Modalidade', as_index=False)[['Horas']].count()
        quantityHoursFromProject = filtered_data.groupby('Projeto', as_index=False)[['Horas']].count()

        sumHoursFromMonth = filtered_data.groupby('AnoMes', as_index=False)[['Horas']].sum()
        sumHoursFromMonth['Ano'] = sumHoursFromMonth['AnoMes'].dt.year
        sumHoursFromMonth['Mes'] = sumHoursFromMonth['AnoMes'].dt.month
        sumHoursFromMonth['Mes'] = sumHoursFromMonth['Mes'].map(monthPtBr)
        sumHoursFromMonth = sumHoursFromMonth.drop(columns=['AnoMes'])

        quantityHoursFromMonth = filtered_data.groupby('AnoMes', as_index=False)[['Horas']].count()
        quantityHoursFromMonth['Ano'] = quantityHoursFromMonth['AnoMes'].dt.year
        quantityHoursFromMonth['Mes'] = quantityHoursFromMonth['AnoMes'].dt.month
        quantityHoursFromMonth['Mes'] = quantityHoursFromMonth['Mes'].map(monthPtBr)
        quantityHoursFromMonth = quantityHoursFromMonth.drop(columns=['AnoMes'])

        details = filtered_data[['Nome', 'Modalidade', 'Feature', 'Observacao', 'Problemas', 'Duvidas']]
        details.set_index("Nome", inplace=True)

        # Graphs
        fig_sum_hours_team = px.bar(
            sumHoursFromTeamMember,
            text_auto = True,
            title = 'Horas apontadas por Membro (SOMA)'
        )

        fig_quantity_hours_team = px.bar(
            quantityHoursFromTeamMember,
            text_auto = True,
            title = 'Horas apontadas por Membro (QUANTIDADE)'
        )

        fig_sum_hours_month = px.line(sumHoursFromMonth,
                             x= 'Mes',
                             y= 'Horas',
                             markers=True,
                             range_y= (0, sumHoursFromMonth.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Apontamentos Mensais (SOMA)')
        fig_sum_hours_month.update_layout(yaxis_title = 'Horas')

        fig_quantity_hours_month = px.line(quantityHoursFromMonth,
                             x= 'Mes',
                             y= 'Horas',
                             markers=True,
                             range_y= (0, quantityHoursFromMonth.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Apontamentos Mensais (QUANTIDADE)')
        fig_quantity_hours_month.update_layout(yaxis_title = 'Horas')
        
        fig_sum_hours_feature = px.pie(sumHoursFromFeature, 
                                       names='Modalidade', 
                                       values='Horas',
                                       hole=.3,
                                       color='Modalidade',
                                       color_discrete_map=featuresMap,
                                       title='Horas apontadas por Modalidade (SOMA)')
        
        fig_quantity_hours_feature = px.pie(quantityHoursFromFeature, 
                                       names='Modalidade', 
                                       values='Horas',
                                       hole=.3,
                                       color='Modalidade',
                                       color_discrete_map=featuresMap,
                                       title='Horas apontadas por Modalidade (QUANTIDADE)')
        
        fig_sum_hours_project = px.pie(sumHoursFromProject, 
                                       names='Projeto', 
                                       values='Horas',
                                       hole=.3,
                                       color='Projeto',
                                       title='Horas apontadas por Projeto (SOMA)')
        
        fig_quantity_hours_project = px.pie(quantityHoursFromProject, 
                                       names='Projeto', 
                                       values='Horas',
                                       hole=.3,
                                       color='Projeto',
                                       title='Horas apontadas por Projeto (QUANTIDADE)')

        # Views
        tabHours, tabQuantity = st.tabs(['Horas', 'Quantidade'])

        with tabHours:
            columnLeft, columnRight = st.columns(2)
            with columnLeft:
                st.metric('Soma Horas Apontadas', pd.to_numeric(filtered_data['Horas']).sum())
                st.plotly_chart(fig_sum_hours_team, use_container_width = True)
                st.plotly_chart(fig_sum_hours_feature, use_container_width = True)
            
            with columnRight:
                st.metric('Qtd de Apontamentos', filtered_data['Horas'].count())
                st.plotly_chart(fig_sum_hours_month, use_container_width = True)
                st.plotly_chart(fig_sum_hours_project, use_container_width = True)

        with tabQuantity:
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    st.metric('Soma Horas Apontadas', pd.to_numeric(filtered_data['Horas']).sum())
                    st.plotly_chart(fig_quantity_hours_team, use_container_width = True)
                    st.plotly_chart(fig_quantity_hours_feature, use_container_width = True)

                with columnRight:
                    st.metric('Qtd de Apontamentos', filtered_data['Horas'].count())
                    st.plotly_chart(fig_quantity_hours_month, use_container_width = True)
                    st.plotly_chart(fig_quantity_hours_project, use_container_width = True)
        
        st.dataframe(details, use_container_width = True)
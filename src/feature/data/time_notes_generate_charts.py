import plotly.express as px
class TimeNotesGenerateCharts:
    def __init__(self, data, monthPtBr):
        self.filtered_data = data
        self.monthPtBr = monthPtBr
        self.featuresMap = {
            'DEVOPS': '#0a53a8', 'BACKEND': '#b10202', 'FRONTEND': '#5ed3f3',
            'UI/UX': '#cca1e9', 'VENDAS': '#0da543', 'ESTUDOS': '#ff8f00',
            'MANUTENÇÃO': '#753800', 'NOSSA EMPRESA': '#e8eaed',
            'REUNIÃO': '#0066fe', 'ANALISE': '#dd11a3'
        }

    def ajust_title(self, text, module):
        if module.lower() == "s":
            return f'{text} (SOMA)'
        elif module.lower() == "q":
            return f'{text} (QUANTIDADE)'
        else:
            return "Entrada inválida"

    def generate_charts(self):
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
            "fig_sum_hours_team": create_bar_chart(team_member_agg, x='Nome', y='sum', title=self.ajust_title('Horas apontadas por Membro ', 's')),
            "fig_quantity_hours_team": create_bar_chart(team_member_agg, x='Nome', y='count', title=self.ajust_title('Horas apontadas por Membro ', 'q')),
            "fig_sum_hours_month": create_line_chart(month_agg, x='Mes', y='sum', color='Ano', title=self.ajust_title('Apontamentos Mensais', 's')),
            "fig_quantity_hours_month": create_line_chart(month_agg, x='Mes', y='count', color='Ano', title=self.ajust_title('Apontamentos Mensais', 'q')),
            "fig_sum_hours_feature": create_pie_chart(feature_agg, names='Modalidade', values='sum', title=self.ajust_title('Horas apontadas por Modalidade', 's'), color_map=self.featuresMap),
            "fig_quantity_hours_feature": create_pie_chart(feature_agg, names='Modalidade', values='count', title=self.ajust_title('Horas apontadas por Modalidade', 'q'), color_map=self.featuresMap),
            "fig_sum_hours_project": create_pie_chart(project_agg, names='Projeto', values='sum', title=self.ajust_title('Horas apontadas por Projeto', 's')),
            "fig_quantity_hours_project": create_pie_chart(project_agg, names='Projeto', values='count', title=self.ajust_title('Horas apontadas por Projeto', 'q')),
            "details": details
        }
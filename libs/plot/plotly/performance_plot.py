import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from libs.plot.plotly._plot import _Plot


class PerformancePlot(_Plot):

    _fig: subplots

    @classmethod
    def _run(cls):
        cls._create_fig()

    @classmethod
    def _create_fig(cls):
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          vertical_spacing=0.15,
                                          subplot_titles=['Отн. отклонение суммарной суточной добычи от факта, %',
                                                          'Отн. отклонение добычи за месяц от факта, %',
                                                          'Отн. отклонение дебита от факта, %',
                                                          'Отн. отклонение накопленной добычи от факта, %'],
                                          specs=[[{'secondary_y': True}, {}],
                                                 [{'secondary_y': True}, {}]],
                                          column_widths=[0.7, 0.3])

        cls._fig.layout.template = 'seaborn'
        cls._fig.update_layout(width=1450,
                               title=dict(text=f'<b>Статистика прогнозов добычи по 20 скважинам<b>',
                                          font=dict(size=20),
                                          x=0.05,
                                          xanchor='left'),
                               font=dict(family='Jost', size=10),
                               hovermode='x',
                               barmode='group',
                               bargap=0.2,
                               bargroupgap=0.05)
        cls._add_11()
        cls._add_12()
        cls._add_21()
        cls._add_22()
        file = str(cls._settings.path / 'performance')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        df = cls._project.df_result
        x = [i for i in range(1, cls._settings.forecast_days_number + 1)]
        devs_sum_prod_liq = df['dev_sum_prod_liq_model'].to_list()
        devs_sum_prod_oil_model = df['dev_sum_prod_oil_model'].to_list()
        devs_sum_prod_oil_ksg = df['dev_sum_prod_oil_ksg'].to_list()
        trace_1 = cls._create_trace('неф_ftor', x, devs_sum_prod_oil_model, color='#EF553B', mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('неф_ксг', x, devs_sum_prod_oil_ksg, color='#636EFA', mode='lines+markers', marker_size=5)
        trace_3 = cls._create_trace('жид_ftor', x, devs_sum_prod_liq, color='#00CC96', mode='lines+markers', marker_size=5, visible='legendonly')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='номер дня', **pos)
        cls._fig.update_yaxes(title_text='нефть', **pos)
        cls._fig.update_yaxes(title_text='жидкость', secondary_y=True, **pos)

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df_test_month = cls._project.df_result_month
        x_month = [1, 2, 3]
        devs_prod_liq_model = df_test_month['dev_prod_liq_model'].to_list()
        devs_prod_oil_model = df_test_month['dev_prod_oil_model'].to_list()
        devs_prod_oil_ksg = df_test_month['dev_prod_oil_ksg'].to_list()
        trace_1 = go.Bar(name='неф_ftor', x=x_month, y=devs_prod_oil_model, marker=dict(color='#EF553B'), opacity=0.5)
        trace_2 = go.Bar(name='неф_ксг', x=x_month, y=devs_prod_oil_ksg, marker=dict(color='#636EFA'), opacity=0.5)
        trace_3 = go.Bar(name='жид_ftor', x=x_month, y=devs_prod_liq_model, marker=dict(color='#00CC96'), visible='legendonly', opacity=0.5)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.update_xaxes(title_text='номер месяца', **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df = cls._project.df_result
        x = [i for i in range(1, cls._settings.forecast_days_number + 1)]
        devs_rate_liq = df['dev_prod_liq_model'].to_list()
        devs_rate_oil_model = df['dev_prod_oil_model'].to_list()
        devs_rate_oil_ksg = df['dev_prod_oil_ksg'].to_list()
        trace_1 = cls._create_trace('неф_ftor', x, devs_rate_oil_model, color='#EF553B', mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('неф_ксг', x, devs_rate_oil_ksg, color='#636EFA', mode='lines+markers', marker_size=5)
        trace_3 = cls._create_trace('жид_ftor', x, devs_rate_liq, color='#00CC96', mode='lines+markers', marker_size=5, visible='legendonly')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='номер дня', **pos)
        cls._fig.update_yaxes(title_text='нефть', **pos)
        cls._fig.update_yaxes(title_text='жидкость', secondary_y=True, **pos)

    @classmethod
    def _add_22(cls):
        pos = dict(row=2, col=2)
        df = cls._project.df_result
        x = [i for i in range(1, cls._settings.forecast_days_number + 1)]
        devs_cum_liq = df['dev_cum_liq_model'].to_list()
        devs_cum_oil_model = df['dev_cum_oil_model'].to_list()
        devs_cum_oil_ksg = df['dev_cum_oil_ksg'].to_list()
        trace_1 = cls._create_trace('накоп_неф_ftor', x, devs_cum_oil_model, color='#EF553B', mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('накоп_неф_ксг', x, devs_cum_oil_ksg, color='#636EFA', mode='lines+markers', marker_size=5)
        trace_3 = cls._create_trace('накоп_жид_ftor', x, devs_cum_liq, color='#00CC96', mode='lines+markers', marker_size=5, visible='legendonly')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.update_xaxes(title_text='номер дня', **pos)
        cls._fig.update_yaxes(title_text='накопленная добыча', **pos)

import plotly as pl
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
                                          cols=1,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          subplot_titles=['Отн. отклонение дебита от факта, %',
                                                          'Отн. отклонение добычи от факта, %'],
                                          specs=[[{'secondary_y': True}],
                                                 [{}]])
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
        cls._add_21()
        file = str(cls._settings.path / 'performance')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        df = cls._project.df_result
        x = [i for i in range(1, cls._settings.forecast_days_number + 1)]
        devs_rel_rate_liq = df['dev_rel_rate_liq_model'].to_list()
        devs_rel_rate_oil_model = df['dev_rel_rate_oil_model'].to_list()
        devs_rel_rate_oil_ksg = df['dev_rel_rate_oil_ksg'].to_list()
        trace_1 = cls._create_trace('жид_ftor', x, devs_rel_rate_liq, mode='lines+markers', marker_size=5, visible='legendonly')
        trace_2 = cls._create_trace('неф_ftor', x, devs_rel_rate_oil_model, mode='lines+markers', marker_size=5)
        trace_3 = cls._create_trace('неф_ксг', x, devs_rel_rate_oil_ksg, mode='lines+markers', marker_size=5)
        cls._fig.add_trace(trace_1, secondary_y=True, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.update_yaxes(title_text='нефть', **pos)
        cls._fig.update_yaxes(title_text='жидкость', secondary_y=True, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df = cls._project.df_result
        x = [i for i in range(1, cls._settings.forecast_days_number + 1)]
        devs_rel_cum_liq = df['dev_rel_cum_liq_model'].to_list()
        devs_rel_cum_oil_model = df['dev_rel_cum_oil_model'].to_list()
        devs_rel_cum_oil_ksg = df['dev_rel_cum_oil_ksg'].to_list()
        trace_1 = cls._create_trace('накоп_жид_ftor', x, devs_rel_cum_liq, mode='lines+markers', marker_size=5, visible='legendonly')
        trace_2 = cls._create_trace('накоп_неф_ftor', x, devs_rel_cum_oil_model, mode='lines+markers', marker_size=5)
        trace_3 = cls._create_trace('накоп_неф_ксг', x, devs_rel_cum_oil_ksg, mode='lines+markers', marker_size=5)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.update_xaxes(title_text='номер дня', **pos)
        cls._fig.update_yaxes(title_text='накопленная добыча', **pos)

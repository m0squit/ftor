import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from domain.entities.well import Well
from libs.plot.plotly._plot import _Plot


class RatesPlot(_Plot):

    _fig: subplots
    _well: Well

    @classmethod
    def _run(cls):
        for well in cls._project.wells:
            cls._well = well
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        well_name = f'{cls._well.name}'
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          vertical_spacing=0.1,
                                          subplot_titles=['Дебит, м3/д',
                                                          'Добыча, м3',
                                                          'Отн. отклонение дебита от факта, %',
                                                          'Отн. отклонение добычи от факта, %'],
                                          specs=[[{'secondary_y': True}, {}],
                                                 [{'secondary_y': True}, {'secondary_y': True}]],
                                          column_widths=[0.7, 0.3])

        cls._fig.layout.template = 'seaborn'
        cls._fig.update_layout(width=1450,
                               title=dict(text=f'<b>Прогноз добычи по скважине {well_name}<b>',
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
        file = str(cls._settings.path / f'prod_{well_name}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        df = cls._well.report.df_test
        x = df.index.to_list()
        rates_oil_fact = df['prod_oil'].to_list()
        rates_oil_ksg = df['prod_oil_ksg'].to_list()
        rates_oil_model = df['prod_oil_model'].to_list()
        rates_liq_fact = df['prod_liq'].to_list()
        rates_liq_model = df['prod_liq_model'].to_list()
        trace_1 = cls._create_trace('неф_факт', x, rates_oil_fact, mode='lines+markers', marker_size=3)
        trace_2 = cls._create_trace('неф_ftor', x, rates_oil_model, mode='lines+markers', marker_size=3)
        trace_3 = cls._create_trace('неф_ксг', x, rates_oil_ksg, mode='lines+markers', marker_size=3)
        trace_4 = cls._create_trace('жид_факт', x, rates_liq_fact, mode='lines+markers', marker_size=3, visible='legendonly')
        trace_5 = cls._create_trace('жид_ftor', x, rates_liq_model, mode='lines+markers', marker_size=3, visible='legendonly')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.add_trace(trace_4, secondary_y=True, **pos)
        cls._fig.add_trace(trace_5, secondary_y=True, **pos)
        cls._fig.update_yaxes(title_text='нефть', **pos)
        cls._fig.update_yaxes(title_text='жидкость', secondary_y=True, **pos)

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df = cls._well.report.df_test_month
        x = df.index.to_list()
        prod_oil_fact = df['prod_oil'].to_list()
        prod_oil_ksg = df['prod_oil_ksg'].to_list()
        prod_oil_model = df['prod_oil_model'].to_list()
        prod_liq_fact = df['prod_liq'].to_list()
        prod_liq_model = df['prod_liq_model'].to_list()
        trace_1 = go.Bar(name='неф_факт', x=x, y=prod_oil_fact, marker=dict(color='#636EFA'), opacity=0.4)
        trace_2 = go.Bar(name='неф_ftor', x=x, y=prod_oil_model, marker=dict(color='#EF553B'), opacity=0.4)
        trace_3 = go.Bar(name='неф_ксг', x=x, y=prod_oil_ksg, marker=dict(color='#00CC96'), opacity=0.4)
        trace_4 = go.Bar(name='жид_факт', x=x, y=prod_liq_fact, visible='legendonly', opacity=0.4)
        trace_5 = go.Bar(name='жид_ftor', x=x, y=prod_liq_model, visible='legendonly', opacity=0.4)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.add_trace(trace_4, **pos)
        cls._fig.add_trace(trace_5, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df = cls._well.report.df_test
        x = df.index.to_list()
        devs_rel_rate_liq = df['dev_rel_rate_liq_model'].to_list()
        devs_rel_rate_oil_model = df['dev_rel_rate_oil_model'].to_list()
        devs_rel_rate_oil_ksg = df['dev_rel_rate_oil_ksg'].to_list()
        trace_1 = cls._create_trace('жид_ftor', x, devs_rel_rate_liq, mode='lines+markers', marker_size=3, visible='legendonly')
        trace_2 = cls._create_trace('неф_ftor', x, devs_rel_rate_oil_model, mode='lines+markers', marker_size=3)
        trace_3 = cls._create_trace('неф_ксг', x, devs_rel_rate_oil_ksg, mode='lines+markers', marker_size=3)
        cls._fig.add_trace(trace_1, secondary_y=True, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.update_xaxes(title_text='дата', **pos)
        cls._fig.update_yaxes(title_text='нефть', **pos)
        cls._fig.update_yaxes(title_text='жидкость', secondary_y=True, **pos)

    @classmethod
    def _add_22(cls):
        pos = dict(row=2, col=2)
        df_test_month = cls._well.report.df_test_month
        df_test_day = cls._well.report.df_test
        x_month = df_test_month.index.to_list()
        x_day = df_test_day.index.to_list()
        devs_prod_liq_model = df_test_month['dev_rel_prod_liq_model'].to_list()
        devs_prod_oil_model = df_test_month['dev_rel_prod_oil_model'].to_list()
        devs_prod_oil_ksg = df_test_month['dev_rel_prod_oil_ksg'].to_list()
        devs_rel_cum_liq = df_test_day['dev_rel_cum_liq_model'].to_list()
        devs_rel_cum_oil_model = df_test_day['dev_rel_cum_oil_model'].to_list()
        devs_rel_cum_oil_ksg = df_test_day['dev_rel_cum_oil_ksg'].to_list()

        trace_1 = go.Bar(name='мес_неф_ftor', x=x_month, y=devs_prod_oil_model, marker=dict(color='#EF553B'), opacity=0.4)
        trace_2 = go.Bar(name='мес_неф_ксг', x=x_month, y=devs_prod_oil_ksg, marker=dict(color='#00CC96'), opacity=0.4)
        trace_3 = go.Bar(name='мес_жид_ftor', x=x_month, y=devs_prod_liq_model, visible='legendonly', opacity=0.4)
        trace_4 = cls._create_trace('накоп_жид_ftor', x_day, devs_rel_cum_liq, mode='lines+markers', marker_size=3, visible='legendonly')
        trace_5 = cls._create_trace('накоп_неф_ftor', x_day, devs_rel_cum_oil_model, mode='lines+markers', marker_size=3)
        trace_6 = cls._create_trace('накоп_неф_ксг', x_day, devs_rel_cum_oil_ksg, mode='lines+markers', marker_size=3)

        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.add_trace(trace_4, secondary_y=True, **pos)
        cls._fig.add_trace(trace_5, secondary_y=True, **pos)
        cls._fig.add_trace(trace_6, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='дата', **pos)
        cls._fig.update_yaxes(title_text='добыча за месяц', **pos)
        cls._fig.update_yaxes(title_text='накопленная добыча', secondary_y=True, **pos)

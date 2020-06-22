import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from domain.entities.well import Well
from libs.plot.plotly._plot import _Plot


class UnitsPlot(_Plot):

    _train_mode: str
    _fig: subplots
    _well: Well

    @classmethod
    def _run(cls):
        for well in cls._project.wells:
            cls._well = well
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        name_well = f'{cls._well.name}'
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          vertical_spacing=0.1,
                                          subplot_titles=['Corey model performance',
                                                          'Relative deviations',
                                                          'Watercut. Plot is divided: 1-train, 3-test',
                                                          'Rates'],
                                          specs=[[{'type': 'table'}, {'secondary_y': True}],
                                                 [{}, {'secondary_y': True}]],
                                          column_widths=[0.5, 0.5],
                                          row_heights=[0.4, 0.6])
        cls._fig.layout.template = 'plotly'
        cls._fig.update_layout(width=1400,
                               title=dict(text=f'<b>Well {name_well}<b>',
                                          font=dict(size=20)),
                               font=dict(family='Jost',
                                         size=12),
                               hovermode='x')
        cls._add_11()
        cls._add_12()
        cls._add_21()
        cls._add_22()
        file = str(cls._settings.path / f'{name_well}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        data = cls._group_data_to_table()
        trace = go.Table(header=dict(values=['name', 'unit', 'value'],
                                     font=dict(size=12),
                                     align='left'),
                         cells=dict(values=data,
                                    font=dict(size=12),
                                    align='left'))
        cls._fig.add_trace(trace, **pos)

    @classmethod
    def _group_data_to_table(cls):
        params = cls._well.flood_model.params
        names = list(params.usable_params.keys())
        names.append('cum_prod_oil')
        names.append('mae_train')
        names.append('mae_test')
        units = list(params.get_units().values())
        units.append('mn_m3')
        units.append('fr')
        units.append('fr')
        values = [x for x in params.get_values()]
        cum_prod_oil = cls._well.report.df_train['cum_prod_oil'].iloc[-1] / 1e6
        values.append(cum_prod_oil)
        values.append(cls._well.flood_model.mae_train)
        values.append(cls._well.flood_model.mae_test)
        values = [round(x, 4) for x in values]
        data = [names, units, values]
        return data

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df = cls._well.report.df_test
        x = df.index.to_list()
        devs_rel_rate_oil = df['dev_rel_rate_oil'].to_list()
        devs_rel_cum_oil = df['dev_rel_cum_oil'].to_list()
        devs_rel_rate_liq = df['dev_rel_rate_liq'].to_list()
        devs_rel_cum_liq = df['dev_rel_cum_liq'].to_list()
        trace_1 = cls._create_trace('rel_rate_oil', x, devs_rel_rate_oil, mode='lines+markers', marker_size=3)
        trace_2 = cls._create_trace('rel_cum_oil', x, devs_rel_cum_oil, mode='lines+markers', marker_size=3)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)

        trace_3 = cls._create_trace('rel_rate_liq', x, devs_rel_rate_liq, mode='lines+markers', marker_size=3)
        trace_4 = cls._create_trace('rel_cum_liq', x, devs_rel_cum_liq, mode='lines+markers', marker_size=3)
        cls._fig.add_trace(trace_3, **pos)
        cls._fig.add_trace(trace_4, secondary_y=True, **pos)

        cls._fig.update_yaxes(title_text='deviation_rate, %', **pos)
        cls._fig.update_yaxes(title_text='deviation_cum, %', secondary_y=True, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df_train = cls._well.report.df_train
        df_test = cls._well.report.df_test
        x = df_train.index.to_list() + df_test.index.to_list()
        watercuts_fact = cls._well.flood_model.watercuts_fact + df_test['watercut'].to_list()
        watercuts_model = cls._well.flood_model.watercuts_model + df_test['watercut_model'].to_list()
        trace_1 = cls._create_trace('watercut_fact', x, watercuts_fact, mode='markers', marker_size=5)
        trace_2 = cls._create_trace('watercut_model', x, watercuts_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._draw_train_test_delimiter(df_train, pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='watercut, fr', **pos)

    @classmethod
    def _draw_train_test_delimiter(cls, df, pos):
        x_del_tt = df.index.to_list()[-1]
        line = cls._create_line_shape(x0=x_del_tt, x1=x_del_tt, y0=0, y1=1)
        cls._fig.add_shape(line, **pos)

    @classmethod
    def _add_22(cls):
        pos = dict(row=2, col=2)
        df_test = cls._well.report.df_test
        x = df_test.index.to_list()
        rates_liq_fact = df_test['prod_liq'].to_list()
        rates_liq_model = df_test['prod_liq_model'].to_list()
        rates_oil_fact = df_test['prod_oil'].to_list()
        rates_oil_model = df_test['prod_oil_model'].to_list()
        trace_1 = cls._create_trace('rate_liq_fact', x, rates_liq_fact, mode='lines+markers', marker_size=3)
        trace_2 = cls._create_trace('rate_liq_model', x, rates_liq_model, mode='lines+markers', marker_size=3)
        trace_3 = cls._create_trace('rate_oil_fact', x, rates_oil_fact, mode='lines+markers', marker_size=3)
        trace_4 = cls._create_trace('rate_oil_model', x, rates_oil_model, mode='lines+markers', marker_size=3)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_trace(trace_3, secondary_y=True, **pos)
        cls._fig.add_trace(trace_4, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='rate_liq, m3/d', **pos)
        cls._fig.update_yaxes(title_text='rate_oil, m3/d', secondary_y=True, **pos)

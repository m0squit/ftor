import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from domain.aggregates.zone import Zone
from libs.plot.plotly._plot import _Plot


class UnitsPlot(_Plot):

    _zone: Zone

    @classmethod
    def _run(cls):
        for zone in cls._project.zones:
            cls._zone = zone
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        name_well = f'{cls._zone.well.name}'
        name_formation = f'{cls._zone.formation.name}'
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          vertical_spacing=0.1,
                                          subplot_titles=['Corey model performance',
                                                          'Abs dev cum is calculated: cum model - cum fact',
                                                          'Plot is divided: 1-monthly, 2-daily, 3-test',
                                                          ''],
                                          specs=[[{'type': 'table'}, {'secondary_y': True}],
                                                 [{}, {'secondary_y': True}]],
                                          column_widths=[0.5, 0.5],
                                          row_heights=[0.4, 0.6])
        cls._add_11()
        cls._add_12()
        cls._add_21()
        cls._add_22()
        cls._fig.update_layout(width=1400,
                               title=dict(text=f'<b>Case {name_well} {name_formation}<b>',
                                          font=dict(size=20)),
                               font=dict(size=11),
                               hovermode='x')
        file = str(cls._path / f'{name_well}')
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
        params = cls._zone.flood_model.params
        names = list(params.usable_params.keys())
        names.append('cum_prod_oil')
        names.append('mae_train')
        names.append('mae_test')
        units = list(params.get_units().values())
        units.append('mn_m3')
        units.append('fr')
        units.append('fr')
        values = [x for x in params.get_values()]
        cum_prod_oil = cls._zone.report.df_result['cum_prod_oil'].iloc[-1] / 1e6
        values.append(cum_prod_oil)
        values.append(cls._zone.report.mae_train)
        values.append(cls._zone.report.mae_test)
        values = [round(x, 4) for x in values]
        data = [names, units, values]
        return data

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df = cls._zone.report.df_result
        x = df.index.to_list()
        devs_rel_rate_oil = df['dev_rel_rate_oil'].to_list()
        devs_abs_cum_oil = df['dev_abs_cum_oil'].to_list()
        trace_1 = cls._create_trace('rel_dev_rate', x, devs_rel_rate_oil, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('abs_dev_cum', x, devs_abs_cum_oil, fill='tozeroy')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)
        cls._fig.update_yaxes(title_text='relative_deviation_rate, fr', **pos)
        cls._fig.update_yaxes(title_text='absolute_deviation_cum, m3', secondary_y=True, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df = cls._zone.report.df_flood
        x = df.index.get_level_values('date').to_list()
        watercuts_fact = df['watercut'].to_list()
        watercuts_model = cls._zone.flood_model.watercuts_model + cls._zone.report.df_result['watercut_model'].to_list()
        trace_1 = cls._create_trace('watercut_fact', x, watercuts_fact, mode='markers')
        trace_2 = cls._create_trace('watercut_model', x, watercuts_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._draw_lines(df, pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='watercut, fr', **pos)

    @classmethod
    def _draw_lines(cls, df, pos):
        x_del_md = df.index.get_loc_level(key='month')[1][-1]  # X coordinate for add line month-day delimiter.
        x_del_tt = df.index.get_loc_level(key='day')[1][-1]  # X coordinate for add line train-test delimiter.
        line_1 = cls._create_line_shape(x0=x_del_md, x1=x_del_md, y0=0, y1=1)
        line_2 = cls._create_line_shape(x0=x_del_tt, x1=x_del_tt, y0=0, y1=1)
        cls._fig.add_shape(line_1, **pos)
        cls._fig.add_shape(line_2, **pos)

    @classmethod
    def _add_22(cls):
        pos = dict(row=2, col=2)
        df = cls._zone.report.df_result
        x = df.index.to_list()
        rates_liq_fact = df['prod_liq'].to_list()
        rates_oil_fact = df['prod_oil'].to_list()
        rates_oil_model = df['prod_oil_model'].to_list()
        trace_1 = cls._create_trace('rate_liq_fact', x, rates_liq_fact, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('rate_oil_fact', x, rates_oil_fact)
        trace_3 = cls._create_trace('rate_oil_model', x, rates_oil_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)
        cls._fig.add_trace(trace_3, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='rate_liquid_fact, m3/d', **pos)
        cls._fig.update_yaxes(title_text='rate_oil, m3/d', secondary_y=True, **pos)

import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots
from pathlib import Path

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone


class SinglePlotly(object):

    _path: Path
    _zone: Zone
    _fig: subplots

    @classmethod
    def create_figures(cls, path: Path, project: Project):
        cls._path = path
        cls._wells = []
        for zone in project.zones:
            cls._zone = zone
            cls._create_zone_fig()

    @classmethod
    def _create_zone_fig(cls):
        name_well = f'{cls._zone.well.name}'
        name_formation = f'{cls._zone.formation.name}'
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          vertical_spacing=0.1,
                                          subplot_titles=['', '', 'Plot is divided: 1-monthly, 2-daily, 3-test', ''],
                                          specs=[[{'type': 'table'}, {'secondary_y': True}],
                                                 [{}, {'secondary_y': True}]],
                                          column_widths=[0.5, 0.5],
                                          row_heights=[0.4, 0.6])
        cls._add_11()
        cls._add_12()
        cls._add_21()
        cls._add_22()
        cls._fig.update_layout(width=1400,
                               title=dict(text=f'<b>case_{name_well}_{name_formation}<b>',
                                          font=dict(size=20)),
                               font=dict(size=11),
                               hovermode='x')
        file = str(cls._path / f'{name_well}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=True)

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
        names, units, values = [], [], []
        params = cls._zone.flood_model.params
        names.extend(list(params.usable_params.keys()))
        names.append('mae_train')
        names.append('mae_test')
        units.extend((params.get_units().values()))
        units.append('fr')
        units.append('fr')
        values.extend([round(x, 3) for x in params.get_values()])
        values.append(cls._zone.report.mae_train)
        values.append(cls._zone.report.mae_test)
        data = [names, units, values]
        return data

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df = cls._zone.report.df_result
        x = df.index.to_list()
        devs_rel_rate_oil = df['dev_rel_rate_oil'].to_list()
        devs_abs_cum_oil = df['dev_abs_cum_oil'].to_list()
        trace_1 = cls._create_trace('dev_rel_rate', x, devs_rel_rate_oil, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('dev_abs_cum', x, devs_abs_cum_oil, fill='tozeroy')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)
        cls._fig.update_yaxes(title_text='relative_deviation_rate, fr', **pos)
        cls._fig.update_yaxes(title_text='absolute_deviation_cum, m3', secondary_y=True, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        df = cls._zone.report.df_flood
        x = df.index.get_level_values('date').to_list()
        x_del_md = df.index.get_loc_level(key='month')[1][-1]  # X coordinate for add line month-day delimiter.
        x_del_tt = df.index.get_loc_level(key='day')[1][-1]  # X coordinate for add line train-test delimiter.
        watercuts_fact = df['watercut'].to_list()
        watercuts_model = cls._zone.flood_model.watercuts_model + cls._zone.report.df_result['watercut_model'].to_list()
        trace_1 = cls._create_trace('watercut_fact', x, watercuts_fact, mode='markers')
        trace_2 = cls._create_trace('watercut_model', x, watercuts_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._fig.add_shape(type='line', opacity=0.4, x0=x_del_md, x1=x_del_md, y0=0, y1=1, **pos)
        cls._fig.add_shape(type='line', opacity=0.4, x0=x_del_tt, x1=x_del_tt, y0=0, y1=1, **pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='watercut, fr', **pos)

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

    @staticmethod
    def _create_trace(name_trace, x, y, mode='lines', marker_size=3, fill=None):
        trace = go.Scattergl(name=name_trace,
                             visible=True,
                             showlegend=True,
                             mode=mode,
                             x=x,
                             y=y,
                             marker=dict(size=marker_size,
                                         symbol='circle'),
                             fill=fill)
        return trace

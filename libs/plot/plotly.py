import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots
from pathlib import Path

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone


class Plotly(object):

    _path: Path
    _zone: Zone
    _fig: subplots

    @classmethod
    def create_figures(cls, path: Path, project: Project, statistics: bool = False):
        cls._path = path
        cls._wells = []
        for zone in project.zones:
            cls._zone = zone
            cls._create_zone_fig()
        if statistics is True:
            cls._create_statistics()

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
        df = cls._zone.report.df_flood.loc['test']
        x = df.index.to_list()
        diffs_cum_prod_oil = df['diff_cum_prod_oil'].to_list()
        diffs_rel_prod_oil = df['diff_rel_prod_oil'].to_list()
        trace_1 = cls._create_trace('dev_rel_rate', x, diffs_rel_prod_oil, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('dev_abs_cum', x, diffs_cum_prod_oil, fill='tozeroy')
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
        watercuts_model = df['watercut_model'].to_list()
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
        df = cls._zone.report.df_flood.loc['test']
        x = df.index.to_list()
        rates_liq_fact = df['prod_liq'].to_list()
        rates_oil_model = df['prod_oil_model'].to_list()
        trace_1 = cls._create_trace('rate_liq_fact', x, rates_liq_fact, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('rate_oil_model', x, rates_oil_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='date', **pos)
        cls._fig.update_yaxes(title_text='rate_liquid_fact, m3/d', **pos)
        cls._fig.update_yaxes(title_text='rate_oil_model, m3/d', secondary_y=True, **pos)

    @classmethod
    def _create_statistics(cls):
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=1,
                                          print_grid=True,
                                          specs=[[{'type': 'xy'}],
                                                 [{'type': 'xy'}]])
        cls._add_diff_rel_prod_oil_well()
        cls._add_diff_prod_oil_well()
        cls._fig.update_layout(width=1500,
                               title=dict(text=f'<b>Statistics on 30 days<b>',
                                          font=dict(size=20)))
        file = str(cls._path / f'statistics')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_mape(cls):
        trace = go.Bar(x=cls._wells, y=cls._mapes)
        cls._fig.add_trace(trace, row=1, col=1)
        cls._fig.update_xaxes(title_text='well', row=1, col=1)
        cls._fig.update_yaxes(title_text='MAPE, fr', row=1, col=1)

    @classmethod
    def _add_diff_rel_prod_oil_well(cls):
        diff_rel_prod_oil_well = []
        for i in range(30):
            diff_rel_prod_oil = 0
            for j in range(cls._n_zone):
                diff_rel_prod_oil += cls._diffs_rel_rate_oil[j][i]
            diff_rel_prod_oil_well.append(diff_rel_prod_oil / cls._n_zone)

        x = [x for x in range(1, 31)]
        y = diff_rel_prod_oil_well
        trace = go.Bar(x=x, y=y)
        cls._fig.add_trace(trace, row=1, col=1)
        cls._fig.update_xaxes(title_text='day', row=1, col=1)
        cls._fig.update_yaxes(title_text='deviation_rate_oil, fr', row=1, col=1)

    @classmethod
    def _add_diff_prod_oil_well(cls):
        diff_prod_oil_well = []
        for i in range(30):
            diff_prod_oil = 0
            for j in range(cls._n_zone):
                diff_prod_oil += cls._diffs_rate_oil[j][i]
            diff_prod_oil_well.append(diff_prod_oil / cls._n_zone)

        x = [x for x in range(1, 31)]
        y = diff_prod_oil_well
        trace = go.Bar(x=x, y=y)
        cls._fig.add_trace(trace, row=2, col=1)
        cls._fig.update_xaxes(title_text='day', row=2, col=1)
        cls._fig.update_yaxes(title_text='deviation_rate_oil, m3/day', row=2, col=1)

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

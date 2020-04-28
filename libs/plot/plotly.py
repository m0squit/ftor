from typing import List

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
        zone_name = f'{cls._zone.well.name}_{cls._zone.formation.name}'
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          specs=[[{'type': 'table'}, {'secondary_y': True}],
                                                 [{}, {'secondary_y': True}]],
                                          column_widths=[0.5, 0.5])
        cls._add_11()
        cls._add_12()
        cls._add_21()
        cls._add_22()
        cls._fig.update_layout(width=1400,
                               title=dict(text=f'<b>{zone_name}<b>',
                                          font=dict(size=20)))
        file = str(cls._path / f'{zone_name}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=True)

    @classmethod
    def _add_11(cls):
        params = cls._zone.flood_model.params
        names = list(params.usable_params.keys())
        units = list(params.get_units().values())
        values = [round(x, 3) for x in params.get_values()]
        trace = go.Table(header=dict(values=['name', 'unit', 'value'],
                                     font=dict(size=12),
                                     align='left'),
                         cells=dict(values=[names, units, values],
                                    font=dict(size=12),
                                    align='left'))
        cls._fig.add_trace(trace, row=1, col=1)

    @classmethod
    def _add_12(cls):
        df = cls._zone.report.df_flood.loc['test']
        x = df.index.to_list()
        rates_liq = df['prod_liq'].to_list()
        rates_oil_model = df['prod_oil_model'].to_list()
        trace_1 = cls._create_trace('rate_liq_fact', x, rates_liq)
        trace_2 = cls._create_trace('rate_oil_model', x, rates_oil_model)
        cls._fig.add_trace(trace_1, row=1, col=2)
        cls._fig.add_trace(trace_2, row=1, col=2, secondary_y=True)
        cls._fig.update_yaxes(title_text='rate_liq, m3/day', row=1, col=2)
        cls._fig.update_yaxes(title_text='rate_oil, m3/day', row=1, col=2, secondary_y=True)

    @classmethod
    def _add_21(cls):
        df = cls._zone.report.df_flood
        x = df.index.get_level_values('date').to_list()
        watercuts_fact = df['watercut'].to_list()
        watercuts_model = df['watercut_model'].to_list()
        trace_1 = cls._create_trace('watercut_fact', x, watercuts_fact, mode='markers')
        trace_2 = cls._create_trace('watercut_model', x, watercuts_model)
        cls._fig.add_trace(trace_1, row=2, col=1)
        cls._fig.add_trace(trace_2, row=2, col=1)
        cls._fig.update_yaxes(title_text='watercut, fr', row=2, col=1)

    @classmethod
    def _add_22(cls):
        df = cls._zone.report.df_flood.loc['test']
        x = df.index.to_list()
        diffs_cum_prod_oil = df['diff_cum_prod_oil'].to_list()
        diffs_rel_prod_oil = df['diff_rel_prod_oil'].to_list()
        trace_1 = go.Bar(name='dev_rate_oil', x=x, y=diffs_rel_prod_oil, opacity=0.5)
        trace_2 = cls._create_trace('dev_cum_oil', x, diffs_cum_prod_oil, fill='tozeroy')
        cls._fig.add_trace(trace_1, row=2, col=2)
        cls._fig.add_trace(trace_2, row=2, col=2, secondary_y=True)
        cls._fig.update_xaxes(title_text='date', row=2, col=2)
        cls._fig.update_yaxes(title_text='rel_dev_rate, fr', row=2, col=2)
        cls._fig.update_yaxes(title_text='abs_dev_cum, m3', row=2, col=2, secondary_y=True)

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
    def _create_trace(name_trace, x, y, mode='lines', fill=None):
        trace = go.Scattergl(name=name_trace,
                             visible=True,
                             showlegend=True,
                             mode=mode,
                             x=x,
                             y=y,
                             marker=dict(size=3,
                                         symbol='circle'),
                             fill=fill)
        return trace

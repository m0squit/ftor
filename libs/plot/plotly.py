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
    _wells: List[str]
    _mapes: List[float]

    @classmethod
    def create(cls, path: Path, project: Project):
        cls._path = path
        cls._wells = []
        cls._mapes = []
        for zone in project.zones:
            cls._zone = zone
            cls._create_zone_plot()
            cls._wells.append(f'well_{zone.well.name}')
            cls._mapes.append(zone.mape)
        cls._create_mape()

    @classmethod
    def _create_zone_plot(cls):
        name_zone = cls._zone.well.name
        cls._fig = subplots.make_subplots(rows=3,
                                          cols=1,
                                          specs=[[{'type': 'xy'}],
                                                 [{'type': 'xy', 'secondary_y': True}],
                                                 [{'type': 'xy'}]])
        cls._add_top()
        cls._add_middle()
        cls._add_bottom()
        cls._fig.update_layout(width=1500,
                               title=dict(text=f'<b>well_{name_zone}<b>',
                                          font=dict(size=20)))
        file = str(cls._path / f'{name_zone}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_top(cls):
        df = cls._zone.report.df_flood_result
        x = df.index.get_level_values('date').to_list()
        watercuts_fact = df['watercut'].to_list()
        watercuts_model = cls._zone.flood_model.watercuts_model
        w = cls._zone.flood_model.watercuts
        watercuts_model.extend(w)

        cls._fig.add_trace(go.Scatter(name='watercut_fact', x=x, y=watercuts_fact, mode='markers'), row=1, col=1)
        cls._fig.add_trace(go.Scatter(name='watercut_model', x=x, y=watercuts_model, mode='lines'), row=1, col=1)

        cls._fig.update_yaxes(title_text='<b>watercut, fr<b>', row=1, col=1)

    @classmethod
    def _add_middle(cls):
        df = cls._zone.report.df_flood.loc['test']
        df_r = cls._zone.report.df_flood_result.loc['test']
        x = df_r.index.get_level_values('date').to_list()

        cls._fig.add_trace(go.Scatter(name='rate_oil_fact', x=x, y=df['prod_oil'], mode='markers'), row=2, col=1)
        cls._fig.add_trace(go.Scatter(name='rate_oil_model', x=x, y=df_r['prod_oil'], mode='markers'), row=2, col=1)
        cls._fig.add_trace(go.Bar(name='deviation_rate_oil',
                                  x=x,
                                  y=cls._zone.diffs_relative_rate,
                                  opacity=0.5),
                           row=2, col=1,
                           secondary_y=True)

        cls._fig.update_yaxes(title_text='<b>rate_oil, m3/day<b>', row=2, col=1)
        cls._fig.update_yaxes(title_text='<b>deviation, fr<b>', row=2, col=1, secondary_y=True)

    @classmethod
    def _add_bottom(cls):
        df_r = cls._zone.report.df_flood_result.loc['test']
        x = df_r.index.get_level_values('date').to_list()
        cls._fig.add_trace(go.Bar(name='deviation_cum_oil', x=x, y=cls._zone.diffs_relative_cp), row=3, col=1)

        cls._fig.update_xaxes(title_text='<b>date<b>', row=3, col=1)
        cls._fig.update_yaxes(title_text='<b>deviation, fr<b>', row=3, col=1)

    @classmethod
    def _create_mape(cls):
        fig = go.Figure([go.Bar(x=cls._wells, y=cls._mapes)])
        fig.update_layout(width=1500,
                          title=dict(text=f'<b>MAPE (mean absolute persentage error) for each well on 30 days<b>',
                                     font=dict(size=20)))
        fig.update_xaxes(title_text='<b>well<b>')
        fig.update_yaxes(title_text='<b>mape, fr<b>')
        file = str(cls._path / f'mapes')
        pl.io.write_html(fig, f'{file}.html', auto_open=False)

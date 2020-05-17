from typing import List

import pandas as pd
import plotly as pl
from plotly.graph_objects import Figure

from domain.aggregates.zone import Zone
from libs.plot.plotly._plot import _Plot


class FloodPlot(_Plot):

    _fig: Figure
    _zone: Zone
    _df_month: pd.DataFrame()
    _df_flood: pd.DataFrame()
    _y_month: List[float]
    _y_day: List[float]
    _y_model: List[float]

    @classmethod
    def _run(cls):
        for zone in cls._project.zones:
            cls._zone = zone
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        name_well = f'{cls._zone.well.name}'
        cls._fig = Figure()
        cls._customize_fig()
        cls._prepare()
        cls._add_month()
        cls._add_day_and_model()
        cls._draw_lines()
        file = str(cls._settings.path / f'{name_well}')
        pl.io.write_image(cls._fig, f'{file}.png', format='png', scale=1.2)

    @classmethod
    def _customize_fig(cls):
        cls._fig.layout.template = 'plotly_white'
        name_well = f'{cls._zone.well.name}'
        name_formation = f'{cls._zone.formation.name}'
        cls._fig.update_layout(title=dict(text=f'<b>Case {name_well} {name_formation}<b>',
                                          font=dict(size=20)),
                               font=dict(family='Jost',
                                         size=12))
        cls._fig.update_xaxes(title_text='date')
        cls._fig.update_yaxes(title_text='watercut, fr')

    @classmethod
    def _prepare(cls):
        df = cls._zone.report.df_flood
        x = df.loc[:'test'].index.get_level_values('date').to_list()[-10]
        cls._df_month = cls._zone.report.df_month.loc[x:]
        cls._df_flood = df.loc[['day', 'test']]

    @classmethod
    def _add_month(cls):
        x = cls._df_month.index.to_list()
        cls._y_month = cls._df_month['watercut'].to_list()
        trace = cls._create_trace('month', x, cls._y_month, mode='markers+lines', marker_size=5)
        cls._fig.add_trace(trace)

    @classmethod
    def _add_day_and_model(cls):
        x = cls._df_flood.index.get_level_values('date').to_list()
        cls._y_day = cls._df_flood['watercut'].to_list()

        y_test = cls._zone.report.df_result['watercut_model'].to_list()
        n = len(cls._y_day) - len(y_test)
        cls._y_model = cls._zone.flood_model.watercuts_model[-n:] + y_test

        trace_1 = cls._create_trace('day', x, cls._y_day, mode='markers+lines', marker_size=5)
        trace_2 = cls._create_trace('model', x, cls._y_model)
        cls._fig.add_trace(trace_1)
        cls._fig.add_trace(trace_2)

    @classmethod
    def _draw_lines(cls):
        df = cls._zone.report.df_flood
        x = df.index.get_loc_level(key='test')[1][0]  # X coordinate of train-test delimiter.
        y = cls._y_month + cls._y_day + cls._y_model
        y_min = min(y)
        y_max = max(y)
        line = cls._create_line_shape(x0=x, x1=x, y0=y_min, y1=y_max)
        cls._fig.add_shape(line)

import plotly as pl
from pandas import DataFrame
from plotly.graph_objects import Figure

from domain.entities.well import Well
from libs.plot.plotly._plot import _Plot


class FloodPlot(_Plot):

    _fig: Figure
    _well: Well
    _df_month: DataFrame
    _df_day: DataFrame

    @classmethod
    def _run(cls):
        for well in cls._project.wells:
            cls._well = well
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        name_well = f'{cls._well.name}'
        cls._fig = Figure()

        cls._customize_fig()
        cls._prepare()
        cls._add_trace(cls._df_month, 'month')
        cls._add_trace(cls._df_day, 'day')

        file = str(cls._settings.path / f'{name_well}')
        pl.io.write_image(cls._fig, f'{file}.png', format='png', scale=1.2)

    @classmethod
    def _customize_fig(cls):
        cls._fig.layout.template = 'plotly_white'
        name_well = f'{cls._well.name}'
        cls._fig.update_layout(title=dict(text=f'<b>Case {name_well}<b>',
                                          font=dict(size=20)),
                               font=dict(family='Jost',
                                         size=12))
        cls._fig.update_xaxes(title_text='date')
        cls._fig.update_yaxes(title_text='watercut, fr')

    @classmethod
    def _prepare(cls):
        report = cls._well.report
        x = report.df_result.index.to_list()[0]
        cls._df_month = report._df_month.loc[x:]
        cls._df_day = report._df_day.loc[x:]

    @classmethod
    def _add_trace(cls, df, name):
        x = df.index.to_list()
        y = df['watercut'].to_list()
        trace = cls._create_trace(name, x, y, mode='markers+lines', marker_size=5)
        cls._fig.add_trace(trace)

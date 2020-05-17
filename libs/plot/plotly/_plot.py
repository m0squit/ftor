import plotly.graph_objects as go

from abc import ABC, abstractmethod

from data.settings import Settings
from domain.aggregates.project import Project


class _Plot(ABC):

    _settings: Settings
    _project: Project

    @classmethod
    def create(cls, settings: Settings, project: Project):
        cls._settings = settings
        cls._project = project
        cls._run()

    @classmethod
    @abstractmethod
    def _run(cls):
        pass

    @classmethod
    @abstractmethod
    def _create_fig(cls):
        pass

    @staticmethod
    def _create_trace(name_trace, x, y, mode='lines', marker_size=3, fill=None):
        trace = go.Scatter(name=name_trace,
                           visible=True,
                           showlegend=True,
                           mode=mode,
                           x=x,
                           y=y,
                           marker=dict(size=marker_size,
                                       symbol='circle'),
                           fill=fill)
        return trace

    @staticmethod
    def _create_line_shape(x0, x1, y0, y1):
        params_line = dict(type='line',
                           x0=x0,
                           x1=x1,
                           y0=y0,
                           y1=y1,
                           line=dict(width=2),
                           opacity=0.4)
        return params_line

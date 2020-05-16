from statistics import mean

import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from libs.plot.plotly._plot import _Plot


class PerformancePlot(_Plot):

    _fig: subplots

    @classmethod
    def _run(cls):
        cls._create_fig()

    @classmethod
    def _create_fig(cls):
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=1,
                                          print_grid=True,
                                          subplot_titles=['Average deviations for wells per day',
                                                          'Mean absolute errors per well'],
                                          specs=[[{'secondary_y': True}],
                                                 [{}]],
                                          row_heights=[0.4, 0.6])
        cls._add_11()
        cls._add_21()
        cls._fig.update_layout(width=1400,
                               title=dict(text=f'<b>Total performance on 90 days<b>',
                                          font=dict(size=20)),
                               font=dict(size=11),
                               hovermode='x',
                               barmode='group',
                               bargap=0.2,
                               bargroupgap=0.05)
        file = str(cls._path / f'performance')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        df = cls._project.df_result
        x = [i for i in range(1, 91)]
        devs_rel_rate_oil = df['dev_rel_rate_oil'].to_list()
        devs_abs_cum_oil = df['dev_abs_cum_oil'].to_list()
        trace_1 = cls._create_trace('dev_rel_rate', x, devs_rel_rate_oil, mode='lines+markers', marker_size=5)
        trace_2 = cls._create_trace('dev_abs_cum', x, devs_abs_cum_oil, fill='tozeroy')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, secondary_y=True, **pos)
        cls._fig.update_xaxes(title_text='day', **pos)
        cls._fig.update_yaxes(title_text='relative_deviation_rate, fr', **pos)
        cls._fig.update_yaxes(title_text='absolute_deviation_cum, m3', secondary_y=True, **pos)

    @classmethod
    def _add_21(cls):
        pos = dict(row=2, col=1)
        x = [f'well_{well.name}' for well in cls._project.wells]
        maes_train = cls._project.maes_train
        maes_test = cls._project.maes_test
        trace_1 = go.Bar(x=x, y=maes_train, name='mae_train')
        trace_2 = go.Bar(x=x, y=maes_test, name='mae_test')
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._draw_lines(x, pos)
        cls._fig.update_yaxes(title_text='mae, fr', **pos)

    @classmethod
    def _draw_lines(cls, x, pos):
        mean_mae_train = mean(cls._project.maes_train)
        mean_mae_test = mean(cls._project.maes_test)
        line_1 = cls._create_line_shape(x0=x[0], x1=x[-1], y0=mean_mae_train, y1=mean_mae_train)
        line_2 = cls._create_line_shape(x0=x[0], x1=x[-1], y0=mean_mae_test, y1=mean_mae_test)
        cls._fig.add_shape(line_1, **pos)
        cls._fig.add_shape(line_2, **pos)

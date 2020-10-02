import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots

from domain.entities.well import Well
from libs.plot.plotly._plot import _Plot


class WatercutsPlot(_Plot):

    _fig: subplots
    _well: Well

    @classmethod
    def _run(cls):
        for well in cls._project.wells:
            cls._well = well
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        well_name = f'{cls._well.name}'
        cls._fig = subplots.make_subplots(rows=1,
                                          cols=2,
                                          shared_xaxes=True,
                                          print_grid=True,
                                          horizontal_spacing=0.1,
                                          subplot_titles=['Параметры модели ftor',
                                                          'Обводненность, д. ед.: обучение и прогноз'],
                                          specs=[[{'type': 'table'}, {}]],
                                          column_widths=[0.3, 0.7])
        cls._fig.layout.template = 'seaborn'
        cls._fig.update_layout(width=1450,
                               title=dict(text=f'<b>Прогноз обводненности по скважине {well_name}<b>',
                                          font=dict(size=20),
                                          x=0.05,
                                          xanchor='left'),
                               font=dict(family='Jost', size=10),
                               hovermode='x')
        cls._add_11()
        cls._add_12()
        file = str(cls._settings.path / f'wc_{well_name}')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_11(cls):
        pos = dict(row=1, col=1)
        data = cls._group_data_to_table()
        trace = go.Table(header=dict(values=['название', 'ед. изм.', 'значение'], font=dict(size=12), align='left'),
                         cells=dict(values=data, font=dict(size=12), align='left'))
        cls._fig.add_trace(trace, **pos)

    @classmethod
    def _group_data_to_table(cls):
        names = ['watecut_initial', 'mobility_ratio', 'n_o', 'n_w', 'ooip', 'cum_oil', 'mae_train', 'mae_test']
        units = ['fr', 'non-dim', 'non-dim', 'non-dim', 'Mm3', 'Mm3', 'fr', 'fr']
        fm = cls._well.flood_model
        values = [fm.watercut_initial, fm.mobility_ratio, fm.n_o, fm.n_w, fm.ooip]
        cum_oil = cls._well.report.df_train['cum_oil'].iloc[-1] / 1e6
        values.append(cum_oil)
        values.append(cls._well.flood_model.mae_train)
        values.append(cls._well.flood_model.mae_test)
        values = [round(x, 4) for x in values]
        data = [names, units, values]
        return data

    @classmethod
    def _add_12(cls):
        pos = dict(row=1, col=2)
        df_train = cls._well.report.df_train
        df_test = cls._well.report.df_test
        x = df_train.index.to_list() + df_test.index.to_list()
        watercuts_fact = cls._well.flood_model.watercuts_fact + df_test['watercut'].to_list()
        watercuts_model = cls._well.flood_model.watercuts_model.tolist() + df_test['watercut_model'].to_list()
        trace_1 = cls._create_trace('факт', x, watercuts_fact, mode='markers', marker_size=5)
        trace_2 = cls._create_trace('ftor', x, watercuts_model)
        cls._fig.add_trace(trace_1, **pos)
        cls._fig.add_trace(trace_2, **pos)
        cls._draw_train_test_delimiter(df_train, pos)
        cls._fig.update_xaxes(title_text='дата', **pos)
        cls._fig.update_yaxes(title_text='обводненность', **pos)

    @classmethod
    def _draw_train_test_delimiter(cls, df, pos):
        x_del_tt = df.index.to_list()[-1]
        line = cls._create_line_shape(x0=x_del_tt, x1=x_del_tt, y0=0, y1=1)
        cls._fig.add_shape(line, **pos)

from typing import List

import pandas as pd

from bokeh import layouts
from bokeh.layouts import row, column
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, ColumnDataSource, output_file, save
from pathlib import Path

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone


class ResearchPlot(object):

    _fig: figure
    _source: ColumnDataSource
    _sliders: List[Slider]
    _layout: layouts
    _path: Path
    _project: Project
    _zone: Zone
    _df: pd.DataFrame

    @classmethod
    def create(cls, path: Path, project: Project):
        cls._path = path
        cls._project = project
        cls._run()

    @classmethod
    def _run(cls):
        for zone in cls._project.zones:
            cls._zone = zone
            cls._create_fig()

    @classmethod
    def _create_fig(cls):
        name_well = f'{cls._zone.well.name}'
        name_formation = f'{cls._zone.formation.name}'
        cls._fig = figure(title=f'Case {name_well} {name_formation}',
                          plot_width=800,
                          plot_height=500)
        cls._fig.xaxis.axis_label = 'cumulative oil production, m3'
        cls._fig.yaxis.axis_label = 'watercut, fr'
        cls._df = cls._zone.report.df_flood.loc[slice('month', 'day')].copy()
        cls._add_fact_trace()
        cls._add_model_trace()
        cls._add_actions()
        file = str(cls._path / f'bokeh_{name_well}')
        output_file(f'{file}.html')
        save(cls._layout)

    @classmethod
    def _add_fact_trace(cls):
        cum_oil = cls._df['cum_prod_oil'].to_list()
        watercuts = cls._df['watercut'].to_list()
        cls._fig.circle(x=cum_oil, y=watercuts, size=2)

    @classmethod
    def _add_model_trace(cls):
        cum_oil = cls._df['cum_prod_oil'].to_list()
        watercuts = cls._zone.flood_model.watercuts_model
        cls._source = ColumnDataSource(data=dict(x=cum_oil, y=watercuts))
        cls._fig.line('x', 'y', source=cls._source, line_color='red', line_width=2, line_alpha=0.6)

    @classmethod
    def _add_actions(cls):
        cls._create_sliders()
        callback = CustomJS(args=dict(source=cls._source,
                                      watercut_initial=cls._sliders[0],
                                      mobility_ratio=cls._sliders[1],
                                      parameter_alpha=cls._sliders[2],
                                      parameter_beta=cls._sliders[3],
                                      parameter_stoiip=cls._sliders[4]),
                            code="""
                const wc_initial = watercut_initial.value;
                const m_ratio = mobility_ratio.value;
                const alpha = parameter_alpha.value;
                const beta = parameter_beta.value;
                const stoiip = parameter_stoiip.value;
                const x = source.data['x'];
                const y = source.data['y'];
                for (var i = 0; i < x.length; i++)
                {
                    recovery_factor = x[i] / (stoiip * Math.pow(10, 6));
                    term_1 = Math.pow(1 - recovery_factor, alpha);
                    term_2 = m_ratio * Math.pow(recovery_factor, beta);
                    y[i] = wc_initial + 1 / (1 + term_1 / term_2);
                }
                source.change.emit();
                """)
        for slider in cls._sliders:
            slider.js_on_change('value', callback)
        cls._layout = row(cls._fig, column(cls._sliders))

    @classmethod
    def _create_sliders(cls):
        params = cls._zone.flood_model.params
        cls._sliders = [cls._create_slider('watercut_initial', params.watercut_initial, step=0.01),
                        cls._create_slider('mobility_ratio', params.mobility_ratio, step=0.01),
                        cls._create_slider('alpha', params.alpha, step=0.01),
                        cls._create_slider('beta', params.beta, step=0.01),
                        cls._create_slider('stoiip', params.stoiip, step=0.001)]

    @classmethod
    def _create_slider(cls, param_name, value, step):
        bounds_params = cls._zone.flood_model.params.usable_params
        bounds = bounds_params[param_name]
        start = bounds['min']
        end = bounds['max']
        slider = Slider(start=start, end=end, value=value, step=step, title=param_name)
        return slider

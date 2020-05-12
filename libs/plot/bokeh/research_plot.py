import pandas as pd

from bokeh import plotting, models, layouts
from pathlib import Path

from domain.aggregates.project import Project
from domain.aggregates.zone import Zone


class ResearchPlot(object):

    _fig: plotting.figure
    _source: plotting.ColumnDataSource
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
        cls._fig = plotting.figure(title=f'Case {name_well} {name_formation}',
                                   plot_width=800,
                                   plot_height=500)
        cls._fig.xaxis.axis_label = 'recovery_factor, fr'
        cls._fig.yaxis.axis_label = 'watercut, fr'
        cls._df = cls._zone.report.df_flood.loc[slice('month', 'day')].copy()
        cls._add_fact_trace()
        cls._add_model_trace()
        cls._add_actions()
        file = str(cls._path / f'bokeh_{name_well}')
        plotting.output_file(f'{file}.html')
        plotting.save(cls._layout)

    @classmethod
    def _add_fact_trace(cls):
        cum_oil = cls._df['cum_prod_oil'].to_list()
        watercuts = cls._df['watercut'].to_list()
        cls._fig.circle(x=cum_oil, y=watercuts, size=1)

    @classmethod
    def _add_model_trace(cls):
        cum_oil = cls._df['cum_prod_oil'].to_list()
        watercuts = cls._zone.flood_model.watercuts_model
        cls._source = plotting.ColumnDataSource(data=dict(x=cum_oil, y=watercuts))
        cls._fig.line('x', 'y', source=cls._source, line_color='red', line_width=2, line_alpha=0.6)

    @classmethod
    def _add_actions(cls):
        params = cls._zone.flood_model.params
        watercut_initial_slider = cls._create_slider('watercut_initial', value=params.watercut_initial, step=0.01)
        mobility_ratio_slider = cls._create_slider('mobility_ratio', value=params.mobility_ratio, step=0.01)
        alpha_slider = cls._create_slider('alpha', value=params.alpha, step=0.01)
        beta_slider = cls._create_slider('beta', value=params.beta, step=0.01)
        stoiip_slider = cls._create_slider('stoiip', value=params.stoiip, step=1e2)
        callback = models.CustomJS(args=dict(source=cls._source,
                                             watercut_initial=watercut_initial_slider,
                                             mobility_ratio=mobility_ratio_slider,
                                             alpha=alpha_slider,
                                             beta=beta_slider,
                                             stoiip=stoiip_slider),
                                   code="""
                const data = source.data;
                const wc_initial = watercut_initial.value;
                const m_ratio = mobility_ratio.value;
                const alpha = alpha.value;
                const beta = beta.value;
                const stoiip = stoiip.value;
                const x = data['x'];
                const y = data['y'];
                for (var i = 0; i < x.length; i++)
                {
                    recovery_factor = x[i] / (stoiip * Math.Pow(10, 6));
                    term_1 = Math.pow(1 - recovery_factor, alpha);
                    term_2 = m_ratio * Math.pow(recovery_factor, beta);
                    y[i] = wc_initial + (1 - wc_initial) / (1 + term_1 / term_2);
                    data.y[i] = y[i];
                }
                source.change.emit();
                """)
        watercut_initial_slider.js_on_change('value', callback)
        mobility_ratio_slider.js_on_change('value', callback)
        alpha_slider.js_on_change('value', callback)
        beta_slider.js_on_change('value', callback)
        stoiip_slider.js_on_change('value', callback)
        cls._layout = layouts.row(cls._fig, layouts.column(watercut_initial_slider,
                                                           mobility_ratio_slider,
                                                           alpha_slider,
                                                           beta_slider,
                                                           stoiip_slider))

    @classmethod
    def _create_slider(cls, param_name, value, step):
        bounds_params = cls._zone.flood_model.params.usable_params
        bounds = bounds_params[param_name]
        start = bounds['min']
        end = bounds['max']
        slider = models.Slider(start=start, end=end, value=value, step=step, title=param_name)
        return slider

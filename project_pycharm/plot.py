import pathlib
import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots
import bokeh.plotting as plotting
import bokeh.models as models
import bokeh.layouts as layouts
import project_pycharm.watercut_model_optimizer as watercut_model_optimizer


class Plot(object):

    _versions_train = {0.3: 'train_0.3', 0.7: 'train_0.7', 1: 'train_1'}
    _directory_data_artifical = pathlib.Path.cwd().parent / 'data' / 'artificial'
    _directory_plot = None
    _data = None
    _model = None

    @classmethod
    def create_plots(cls, data, model):
        cls._directory_plot = cls._directory_data_artifical / cls._versions_train[model.mult_indexes_train]
        cls._data = data
        cls._model = model
        cls._create_plot_plotly()
        cls._create_plot_bokeh()

    @classmethod
    def _create_plot_plotly(cls):
        params_watercut = cls._model.params_watercut
        title_text = f'watercut_initial={round(params_watercut[0], 2)},' + \
                     f'mobility_ratio={round(params_watercut[1], 2)},' + \
                     f'parameter_alpha={round(params_watercut[2], 2)},' + \
                     f'parameter_beta={round(params_watercut[3], 2)}'
        title_dict = dict(text=f'{title_text}',
                          font=dict(size=12))
        cls._create_plot_plotly_watercut(title_dict)
        cls._create_plot_plotly_rate_oil(title_dict)

    @classmethod
    def _create_plot_plotly_watercut(cls, title_dict):
        # Создание data trace
        recovery_factors_data = cls._data.recovery_factors
        watercuts_data = cls._data.watercuts
        trace_watercuts_data = cls._create_trace(name_trace='data',
                                                 x=recovery_factors_data,
                                                 y=watercuts_data,
                                                 mode='markers')
        # Создание model trace
        recovery_factors_model = cls._model.recovery_factors
        watercuts_model = cls._model.watercuts
        trace_watercuts_model = cls._create_trace(name_trace='model',
                                                  x=recovery_factors_model,
                                                  y=watercuts_model)
        fig_watercut = go.Figure()
        fig_watercut.add_trace(trace_watercuts_data)
        fig_watercut.add_trace(trace_watercuts_model)
        fig_watercut.update_layout(title=title_dict)
        fig_watercut.update_xaxes(title_text='recovery_factor, fr')
        fig_watercut.update_yaxes(title_text='watercut, fr')
        file = str(cls._directory_plot / f'{cls._data.file_excel_name}_watercut_plotly.html')
        pl.io.write_html(fig=fig_watercut, file=file, auto_open=False)

    @classmethod
    def _create_plot_plotly_rate_oil(cls, title_dict):
        times = cls._data.times
        # Создание data trace
        rates_oil_data = cls._data.rates_oil
        trace_rates_oil_data = cls._create_trace(name_trace='data',
                                                 x=times,
                                                 y=rates_oil_data)
        # Создание model trace
        rates_oil_model = cls._model.rates_oil
        trace_rates_oil_model = cls._create_trace(name_trace='model',
                                                  x=times,
                                                  y=rates_oil_model)
        # Создание deviation trace
        deviations_rates_oil = cls._calc_deviations(rates_oil_data, rates_oil_model)
        trace_deviation_rates_oil = cls._create_trace(name_trace='deviation',
                                                      x=times,
                                                      y=deviations_rates_oil)
        fig_rate = subplots.make_subplots(specs=[[{'secondary_y': True}]])
        fig_rate.add_trace(trace_rates_oil_data)
        fig_rate.add_trace(trace_rates_oil_model)
        fig_rate.add_trace(trace_deviation_rates_oil, secondary_y=True)
        fig_rate.update_layout(title=title_dict)
        fig_rate.update_xaxes(title_text='time, hr')
        fig_rate.update_yaxes(title_text='rate_oil, m3/day', secondary_y=False)
        fig_rate.update_yaxes(title_text='deviation, fr', secondary_y=True)
        file = str(cls._directory_plot / f'{cls._data.file_excel_name}_rate_oil.html')
        pl.io.write_html(fig=fig_rate, file=file, auto_open=False)

    @classmethod
    def _create_plot_bokeh(cls):
        # Создание data данных
        recovery_factors_data = cls._data.recovery_factors
        watercuts_data = cls._data.watercuts
        # Создание model данных
        rate_oil_model = cls._model
        index_start_train = rate_oil_model.index_start_train
        index_start_prediction = rate_oil_model.index_start_prediction
        recovery_factors_model = rate_oil_model.recovery_factors[index_start_train:index_start_prediction]
        watercuts_model = rate_oil_model.watercuts[index_start_train:index_start_prediction]
        source = plotting.ColumnDataSource(data=dict(x=recovery_factors_model, y=watercuts_model))

        plot = plotting.figure(y_range=(0, 1), plot_width=1000, plot_height=800)
        plot.circle(x=recovery_factors_data, y=watercuts_data, size=1)
        plot.line('x', 'y', source=source, line_color='red', line_width=2, line_alpha=0.6)

        params_watercut = rate_oil_model.params_watercut
        watercut_initial_slider = cls._create_slider(parameter_name='watercut_initial', value=params_watercut[0])
        mobility_ratio_slider = cls._create_slider(parameter_name='mobility_ratio', value=params_watercut[1])
        parameter_alpha_slider = cls._create_slider(parameter_name='parameter_alpha', value=params_watercut[2])
        parameter_beta_slider = cls._create_slider(parameter_name='parameter_beta', value=params_watercut[3])

        callback = models.CustomJS(args=dict(source=source,
                                             watercut_initial=watercut_initial_slider,
                                             mobility_ratio=mobility_ratio_slider,
                                             parameter_alpha=parameter_alpha_slider,
                                             parameter_beta=parameter_beta_slider),
                                   code="""
        const data = source.data;
        const wc_initial = watercut_initial.value;
        const m_ratio = mobility_ratio.value;
        const alpha = parameter_alpha.value;
        const beta = parameter_beta.value;
        const x = data['x'];
        const y = data['y'];
        for (var i = 0; i < x.length; i++)
        {
            term_1 = Math.pow(1 - x[i], alpha);
            term_2 = m_ratio * Math.pow(x[i], beta);
            y[i] = wc_initial + (1 - wc_initial) / (1 + term_1 / term_2);
            data.y[i] = y[i];
        }
        source.change.emit();
        """)
        watercut_initial_slider.js_on_change('value', callback)
        mobility_ratio_slider.js_on_change('value', callback)
        parameter_alpha_slider.js_on_change('value', callback)
        parameter_beta_slider.js_on_change('value', callback)
        layout = layouts.row(plot, layouts.column(watercut_initial_slider,
                                                  mobility_ratio_slider,
                                                  parameter_alpha_slider,
                                                  parameter_beta_slider))
        file = str(cls._directory_plot / f'{cls._data.file_excel_name}_watercut_bokeh.html')
        plotting.output_file(filename=file)
        plotting.save(layout)

    @staticmethod
    def _calc_deviations(parameters_data, parameters_model):
        deviations = []
        for i in range(len(parameters_data)):
            deviation = abs(parameters_data[i] - parameters_model[i]) / parameters_data[i]
            deviations.append(deviation)
        return deviations

    @staticmethod
    def _create_trace(name_trace, x, y, mode='lines'):
        trace = go.Scattergl(name=name_trace,
                             visible=True,
                             showlegend=True,
                             mode=mode,
                             x=x,
                             y=y,
                             marker=dict(size=3,
                                         symbol='circle'))
        return trace

    @staticmethod
    def _create_slider(parameter_name, value):
        bounds_params_watercut = watercut_model_optimizer.WatercutsModelOptimizer.params_bounds
        bounds = bounds_params_watercut[parameter_name]
        start = bounds['min']
        end = bounds['max']
        step = 0.01
        slider = models.Slider(start=start, end=end, value=value, step=step, title=parameter_name)
        return slider

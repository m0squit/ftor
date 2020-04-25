import pathlib
import plotly as pl
import plotly.graph_objects as go
import plotly.subplots as subplots
import bokeh.plotting as plotting
import bokeh.models as models
import bokeh.layouts as layouts
import libs.numeric_tools.optimizer as watercut_model_optimizer


class Plot(object):

    _directory_data_artifical = pathlib.Path.cwd().parent / 'data' / 'artificial'
    _directory_data_fact = pathlib.Path.cwd().parent / 'data' / 'real' / 'kholmogorskoe'

    _versions_train = {0.3: 'train_0.3', 0.7: 'train_0.7', 1: 'train_1'}
    _directory_plot = None
    _data = None
    _model = None

    @classmethod
    def create_plots(cls, data, model, save_png=False):
        cls._directory_plot = cls._directory_data_fact  # cls._directory_data_artifical / cls._versions_train[model.mult_indexes_train]
        cls._data = data
        cls._model = model
        cls._create_plotly_plot(save_png)
        # cls._create_bokeh_plot()

    @classmethod
    def _create_plotly_plot(cls, save_png):
        # Создание fig
        fig = subplots.make_subplots(rows=2,
                                     cols=1,
                                     shared_xaxes=True,
                                     print_grid=True,
                                     vertical_spacing=0.02,
                                     specs=[[{'type': 'xy'}],
                                            [{'type': 'xy', 'secondary_y': True}]],
                                     x_title='<b>date<b>')
        x = cls._data.times
        fig = cls._create_plotly_plot_top(fig, x)
        fig = cls._create_plotly_plot_bottom(fig, x)
        fig.update_layout(width=1500,
                          title=dict(text=f'<b>case_{cls._data.file_excel_name}<b>',
                                     font=dict(size=20)))
        # Запись в файл
        file = str(cls._directory_plot / f'plotly_{cls._data.file_excel_name}')
        # if save_png is True:
        #     fig.write_image(f'{file}.png')
        pl.io.write_html(fig, f'{file}.html', auto_open=False)

    @classmethod
    def _create_plotly_plot_top(cls, fig, x):
        # Добавление вертикальных линий для разделения временного диапазона на train и prediction
        x_start_train = x[cls._model.index_start_train]
        x_start_prediction = x[cls._model.index_start_prediction]
        fig.add_shape(type='line', opacity=0.4, x0=x_start_train, x1=x_start_train, y0=0, y1=1)
        fig.add_shape(type='line', opacity=0.4, x0=x_start_prediction, x1=x_start_prediction, y0=0, y1=1)
        # Добавление аннотации
        # x_annotation = (x_start_train + x_start_prediction) / 2
        # fig.add_annotation(text='train_range',
        #                    font=dict(size=20),
        #                    x=x_annotation,
        #                    y=0.9,
        #                    showarrow=False)

        trace_watercuts_data = cls._create_trace(name_trace='watercut_data', x=x, y=cls._data.watercuts_fact, mode='markers')
        trace_watercuts_model = cls._create_trace(name_trace='watercut_model', x=x, y=cls._model.watercuts_fact)
        fig.add_trace(trace_watercuts_data, row=1, col=1)
        fig.add_trace(trace_watercuts_model, row=1, col=1)

        df_telemetry = cls._data.df_day_watercut_telemetry
        trace_watercuts_telemetry = cls._create_trace(name_trace='wc_telemetry',
                                                      x=df_telemetry['Дата'].to_list(),
                                                      y=[y / 100 for y in df_telemetry['Обводненность (ТМ)'].to_list()],
                                                      mode='markers')
        df_lab = cls._data.df_day_watercut_lab
        trace_watercuts_lab = cls._create_trace(name_trace='wc_lab',
                                                x=df_lab['Дата'].to_list(),
                                                y=[y / 100 for y in df_lab['Обводненность (ХАЛ)'].to_list()],
                                                mode='markers')

        fig.add_trace(trace_watercuts_telemetry, row=1, col=1)
        fig.add_trace(trace_watercuts_lab, row=1, col=1)

        fig.update_yaxes(title_text='<b>watercut, fr<b>', row=1, col=1)  # range=[0, 1])
        return fig

    @classmethod
    def _create_plotly_plot_bottom(cls, fig, x):
        i = cls._data.month_end
        x = x[i:]
        rates_oil_data = cls._data.rates_oil[i:]
        rates_oil_model = cls._model.rates_oil[i:]
        deviations_rates_oil = cls._calc_deviations(rates_oil_data, rates_oil_model)

        trace_rates_oil_data = cls._create_trace(name_trace='rate_oil_data', x=x, y=rates_oil_data)
        trace_rates_oil_model = cls._create_trace(name_trace='rate_oil_model', x=x, y=rates_oil_model)
        trace_deviation_rates_oil = cls._create_trace(name_trace='deviation', x=x, y=deviations_rates_oil)

        df_liquid = cls._data.df_liquid
        x1 = [x[1].date() for x in df_liquid.index.to_list()[i:]]
        y1 = df_liquid['production_liquid'].to_list()[i:]
        trace_rates_liquid_data = cls._create_trace(name_trace='rate_liquid_data',
                                                    x=x1,
                                                    y=y1)
        fig.add_trace(trace_rates_liquid_data, row=2, col=1)

        fig.add_trace(trace_rates_oil_data, row=2, col=1)
        fig.add_trace(trace_rates_oil_model, row=2, col=1)
        fig.add_trace(trace_deviation_rates_oil, row=2, col=1, secondary_y=True)
        fig.update_yaxes(title_text='<b>rate_oil, m3/day<b>', row=2, col=1)
        fig.update_yaxes(title_text='<b>deviation, fr<b>', row=2, col=1, secondary_y=True)
        return fig

    @classmethod
    def _create_bokeh_plot(cls):
        # Создание plot
        plot = plotting.figure(title=f'case_{cls._data.file_excel_name}',
                               plot_width=1000,
                               plot_height=800)
        plot.xaxis.axis_label = 'recovery_factor, fr'
        plot.yaxis.axis_label = 'watercut, fr'
        # Создание data данных
        recovery_factors_data = cls._data.recovery_factors
        watercuts_data = cls._data.watercuts_fact
        plot.circle(x=recovery_factors_data, y=watercuts_data, size=1)
        # Создание model данных
        rate_oil_model = cls._model
        index_start_train = rate_oil_model.index_start_train
        index_start_prediction = rate_oil_model.index_start_prediction
        recovery_factors_model = rate_oil_model.recovery_factors[index_start_train:index_start_prediction]
        watercuts_model = rate_oil_model.watercuts_fact[index_start_train:index_start_prediction]
        source = plotting.ColumnDataSource(data=dict(x=recovery_factors_model, y=watercuts_model))
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
        # Запись в файл
        file = str(cls._directory_plot / f'bokeh_{cls._data.file_excel_name}')
        plotting.output_file(f'{file}.html')
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
        bounds_params_watercut = watercut_model_optimizer.Optimizer.params_bounds
        bounds = bounds_params_watercut[parameter_name]
        start = bounds['min']
        end = bounds['max']
        step = 0.01
        slider = models.Slider(start=start, end=end, value=value, step=step, title=parameter_name)
        return slider

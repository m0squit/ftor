import time
import project_pycharm.data_artificial as data_artificial
import project_pycharm.rate_oil_model as rate_oil_model
import project_pycharm.plot as plot
import project_pycharm.data_fact as data_fact


class Calculator(object):

    @classmethod
    def run(cls, type_data):
        start_time = time.time()

        if type_data == 'artificial':
            cls._run_artificial()
        if type_data == 'fact':
            cls._run_fact()

        print(f'--- {time.time() - start_time} seconds ---')

    @staticmethod
    def _run_artificial():
        # 'circle_500_1_injector',
        # 'circle_500_1_injector_aquifer',
        # 'circle_500_aquifer_bhp_200',
        # 'circle_500_aquifer_bhp_250',
        # 'square_500_1_injector',
        # 'square_500_2_injector',
        # 'square_500_2_injector_variable',
        # 'square_500_4_injector',
        # 'square_500_4_injector_diagonal',
        # 'square_500_aquifer'
        names_file_excel = ['circle_500_1_injector',
                            'circle_500_1_injector_aquifer',
                            'circle_500_aquifer_bhp_200',
                            'circle_500_aquifer_bhp_250',
                            'square_500_1_injector',
                            'square_500_2_injector',
                            'square_500_2_injector_variable',
                            'square_500_4_injector',
                            'square_500_4_injector_diagonal',
                            'square_500_aquifer']
        mults_indexes_train = [0.3, 0.7, 1]

        data_dict = dict.fromkeys(names_file_excel)
        mult_dict = dict.fromkeys(mults_indexes_train)
        file_dict = dict.fromkeys(['data', 'model'])

        for name_file_excel in names_file_excel:
            data_dict[name_file_excel] = mult_dict
            data = data_artificial.DataArtificial(name_file_excel)
            for mult_indexes_train in mults_indexes_train:
                model = rate_oil_model.RateOilModel(data,
                                                    mult_watercuts_train=1.1,
                                                    mult_indexes_train=mult_indexes_train)
                plot.Plot.create_plots(data,
                                       model,
                                       save_png=False)
                data_dict[name_file_excel][mult_indexes_train] = file_dict
                data_dict[name_file_excel][mult_indexes_train]['data'] = data
                data_dict[name_file_excel][mult_indexes_train]['model'] = model
            print(f'{name_file_excel}')

    @staticmethod
    def _run_fact():
        wells = [#'1_502',
                 '18_163',
                 #'36_368',
                 #'82_1102',
                 #'100_1248',
                 '112_2190',
                 '116_2276',]
                 #'132_2165']

        for well in wells:
            data = data_fact.DataFact('kholmogorskoe', f'{well}', 0.5)
            data.file_excel_name = well

            df = data.df
            df.columns = ['production_oil', 'production_liquid', 'recovery_factor', 'cumprod_liquid', 'watercut']

            data.times = [x[1].date() for x in df.index.to_list()]
            data.times_count = len(data.times)
            data.rates_oil = df['production_oil'].to_list()
            data.rates_liquid = df['production_liquid'].to_list()
            data.watercuts = df['watercut'].to_list()
            data.stoiip = 1e6
            data.cumulative_productions_liquid = df['cumprod_liquid'].to_list()
            data.recovery_factors = df['recovery_factor'].apply(lambda x: x / data.stoiip)

            model = rate_oil_model.RateOilModel(data, mult_indexes_train=0.7)
            plot.Plot.create_plots(data, model)

            # watercut_model.WatercutModel.mult_watercuts_train = 1
            # watercut_model.WatercutModel.mult_indexes_train = 0.7
            # settings = watercut_model.WatercutModel.get_settings(data, None, 'differential_evolution')
            # params = settings['params']
            #
            # fun = watercut_model.WatercutModel.calc_watercut
            # data.watercuts_model = [fun(x, params) for x in data.recovery_factors]
            #
            # fig = go.Figure()
            # x = data.recovery_factors
            # y1 = data.watercuts
            # y2 = data.watercuts_model
            # fig.add_trace(go.Scatter(x=x, y=y1, mode='markers'))
            # fig.add_trace(go.Scatter(x=x, y=y2, mode='lines'))
            # pl.io.write_html(fig, f'{well}.html', auto_open=False)


Calculator.run('fact')

import time
import project_pycharm.data_artificial as data_artificial
import project_pycharm.rate_oil_model as rate_oil_model
import project_pycharm.plot as plot

# class Calculator(object):
# 
#     type_data = None
# 
#     @classmethod
#     def _run(cls):
#         if cls.type_data is None:
#             pass
#         if cls.type_data == 'artificial':



start_time = time.time()

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

print(f'--- {time.time() - start_time} seconds ---')

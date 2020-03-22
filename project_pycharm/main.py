import time
import project_pycharm.data_artificial as data_artificial
import project_pycharm.rate_oil_model as rate_oil_model
import project_pycharm.plot as plot

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
file_excel_names = ['circle_500_1_injector',
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

data_dict = dict.fromkeys(file_excel_names)
mult_dict = dict.fromkeys(mults_indexes_train)
file_dict = dict.fromkeys(['data', 'model'])

for file_excel_name in file_excel_names:
    data_dict[file_excel_name] = mult_dict
    data = data_artificial.DataArtificial(file_excel_name)
    for mult_indexes_train in mults_indexes_train:
        model = rate_oil_model.RateOilModel(data,
                                            mult_watercuts_train=1.1,
                                            mult_indexes_train=mult_indexes_train)
        plot.Plot.create_plots(data, model)
        data_dict[file_excel_name][mult_indexes_train] = file_dict
        data_dict[file_excel_name][mult_indexes_train]['data'] = data
        data_dict[file_excel_name][mult_indexes_train]['model'] = model
    print(f'{file_excel_name}')

print(f'--- {time.time() - start_time} seconds ---')

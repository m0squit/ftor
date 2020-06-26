import pandas as pd
from domain.aggregates.project import Project


class Calculator(object):
    """Domain objects calculation manager."""

    _project: Project

    @classmethod
    def run(cls, project: Project) -> Project:
        cls._project = project
        cls._calc_wells()
        cls._project.calc_metric()
        return cls._project

    @classmethod
    def _calc_wells(cls):
        cls._add_prod_oil_ksg_to_df_test()
        data = cls._read_model_liq_rates()
        for well in cls._project.wells:
            print(well.name)
            rates_liq_model = data[well.name].to_list()
            well.calc(rates_liq_model)

    @classmethod
    def _add_prod_oil_ksg_to_df_test(cls):
        # Add new df_test column for prod_oil_ksg in each well
        for well in cls._project.wells:
            well.report.df_test['prod_oil_ksg'] = None

        dates = cls._project.wells[0].report.df_test.index

        # Define prod_oil ratios in prod_oil_total for each well by first forecast day
        ratios = {}
        first_forecast_date = dates[0]
        prod_oil_total = 0
        for well in cls._project.wells:
            prod_oil_total += well.report.df_test['prod_oil'].loc[first_forecast_date]
        for well in cls._project.wells:
            prod_oil_fact = well.report.df_test['prod_oil'].loc[first_forecast_date]
            ratio = prod_oil_fact / prod_oil_total
            ratios[well.name] = ratio

        prods_oil_ksg = cls._read_ksg_oil_prods()
        for i in range(len(prods_oil_ksg)):
            prod_oil_ksg = prods_oil_ksg[i]
            date = dates[i]
            for well in cls._project.wells:
                well.report.df_test['prod_oil_ksg'].loc[date] = prod_oil_ksg * ratios[well.name]

    @classmethod
    def _read_ksg_oil_prods(cls):
        read_params = {'02': {'col': 'K', 'skiprows': 10, 'nrows': 86},
                       '03': {'col': 'E', 'skiprows': 10, 'nrows': 92},
                       '04': {'col': 'F', 'skiprows': 10, 'nrows': 89}}
        prods_oil_ksg = []
        for sheet in read_params.keys():
            s = pd.read_excel(io=cls._project.settings.path / 'ksg_oil_prods.xlsx',
                              sheet_name=sheet,
                              header=None,
                              usecols=read_params[sheet]['col'],
                              squeeze=True,
                              skiprows=read_params[sheet]['skiprows'],
                              nrows=read_params[sheet]['nrows'])
            s.dropna(inplace=True)
            s = s.apply(lambda x: x / 0.849)
            s = s.to_list()
            prods_oil_ksg.extend(s)
        return prods_oil_ksg

    @classmethod
    def _read_model_liq_rates(cls):
        data = pd.read_excel(io=cls._project.settings.path / 'model_liq_rates.xlsx',
                             sheet_name='Q_liq - модель',
                             header=0,
                             index_col=0,
                             usecols='A:CM',
                             nrows=22,
                             na_values=0)
        data.dropna(axis='index', how='all', inplace=True)
        data = data.transpose()
        return data

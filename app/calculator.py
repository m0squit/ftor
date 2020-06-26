import pandas as pd
from domain.aggregates.project import Project


class Calculator(object):
    """Domain objects calculation manager."""

    @classmethod
    def run(cls, project: Project) -> Project:
        project = cls._calc_wells(project)
        project.calc_metric()
        return project

    @staticmethod
    def _calc_wells(project: Project) -> Project:
        data = pd.read_excel(io=project.settings.path / 'Отдельное.xlsx',
                             sheet_name='Q_liq - модель',
                             header=0,
                             index_col=0,
                             usecols='A:CM',
                             nrows=22,
                             na_values=0)

        data.dropna(axis='index', how='all', inplace=True)
        data = data.transpose()

        for well in project.wells:
            well.report.df_test['prod_oil_ksg'] = None

        read_params = {'02': {'col': 'K', 'skiprows': 10, 'nrows': 86},
                       '03': {'col': 'E', 'skiprows': 10, 'nrows': 92},
                       '04': {'col': 'F', 'skiprows': 10, 'nrows': 89}}
        prods_oil_ksg = []
        for sheet in read_params.keys():
            s = pd.read_excel(io=project.settings.path / 'КСГ.xlsx',
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

        dates = project.wells[0].report.df_test.index
        for i in range(len(prods_oil_ksg)):
            prod_oil_ksg = prods_oil_ksg[i]
            date = dates[i]
            prod_oil = 0
            for well in project.wells:
                prod_oil += well.report.df_test['prod_oil'].loc[date]
            for well in project.wells:
                prod_oil_fact = well.report.df_test['prod_oil'].loc[date]
                ratio = prod_oil_fact / prod_oil
                well.report.df_test['prod_oil_ksg'].loc[date] = prod_oil_ksg * ratio

        for well in project.wells:
            print(well.name)
            rates_liq_model = data[well.name].to_list()
            well.calc(rates_liq_model)

        return project

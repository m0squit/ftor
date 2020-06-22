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
            print(well.name)
            rates_liq_model = data[well.name].to_list()
            well.calc(rates_liq_model)
        return project

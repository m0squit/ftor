import datetime
from typing import List
from pandas import DataFrame, concat

from data.settings import Settings
from domain.aggregates.project import Project
from domain.entities.well import Well
from domain.factories.input_data import InputData
from domain.value_objects.report import Report


class ProjectCreator(object):

    _settings: Settings
    _project: Project
    _wells: List[Well]

    _df_month: DataFrame
    _df_day: DataFrame
    _df_test: DataFrame
    _df_train: DataFrame
    _df_fact: DataFrame

    @classmethod
    def run(cls, input_data: InputData, settings: Settings) -> Project:
        cls._settings = settings
        cls._create_wells(input_data)
        cls._create_project()
        return cls._project

    @classmethod
    def _create_wells(cls, input_data: InputData):
        cls._wells = []
        for name, data in input_data.wells.items():
            cls._df_month = data['df_month']
            cls._df_day = data['df_day']
            report = cls._create_report()
            well = Well(name, report)
            cls._wells.append(well)

    @classmethod
    def _create_project(cls):
        cls._project = Project(cls._settings, cls._wells)

    @classmethod
    def _create_report(cls) -> Report:
        report = Report()
        report.df_month = cls._df_month
        report.df_day = cls._df_day
        cls._create_df_test()
        cls._create_df_train()
        report.df_train = cls._df_train
        report.df_test = cls._df_test
        return report

    @classmethod
    def _create_df_test(cls):
        cls._df_test = cls._df_day.tail(cls._settings.forecast_days_number)
        cls._modify_df_month_df_day()

    @classmethod
    def _modify_df_month_df_day(cls):
        last_train_date = cls._df_test.index[0] - datetime.timedelta(days=1)
        cls._df_month = cls._df_month.loc[:last_train_date]
        cls._df_day = cls._df_day.loc[:last_train_date]

    @classmethod
    def _create_df_train(cls):
        cls._create_mix_month_day()
        cls._df_train = cls._calc_cumulative_productions(cls._df_train)

    @classmethod
    def _create_mix_month_day(cls):
        cls._divide_month_day()
        cls._df_train = concat(objs=[cls._df_month, cls._df_day],
                               axis='index',
                               verify_integrity=True)

    @classmethod
    def _divide_month_day(cls):
        dates_month = cls._df_month.index
        dates_day = cls._df_day.index
        ratios = []
        for i in range(len(dates_day)):
            date_day = dates_day[i]
            number_points_month = len(dates_month[dates_month < date_day])
            number_points_day = len(dates_day[dates_day >= date_day])
            ratio = number_points_month / number_points_day
            ratios.append(ratio)
        ratio_points_month_day = min(ratios, key=lambda x: abs(x - cls._settings.ratio_points_month_day))
        i = ratios.index(ratio_points_month_day)
        number_points_month = len(dates_month[dates_month < dates_day[i]])
        number_points_day = len(dates_day[dates_day >= dates_day[i]])
        cls._df_month = cls._df_month.head(number_points_month)
        cls._df_day = cls._df_day.tail(number_points_day)

    @classmethod
    def _calc_cumulative_productions(cls, df: DataFrame) -> DataFrame:
        df = cls._calc_cumulative_productions_phase(df, 'oil')
        df = cls._calc_cumulative_productions_phase(df, 'liq')
        return df

    @staticmethod
    def _calc_cumulative_productions_phase(df: DataFrame, phase: str) -> DataFrame:
        df[f'cum_{phase}'] = df[f'prod_{phase}'].cumsum()
        return df

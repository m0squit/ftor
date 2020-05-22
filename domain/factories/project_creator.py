import datetime
from typing import List
from numpy import cumsum
from pandas import DataFrame, concat

from data.settings import Settings
from domain.aggregates.project import Project
from domain.entities.formation import Formation
from domain.entities.well import Well
from domain.factories.input_data import InputData
from domain.value_objects.fluid import Fluid
from domain.value_objects.report import Report


class ProjectCreator(object):

    _settings: Settings
    _project: Project
    _wells: List[Well]

    _df_month: DataFrame
    _df_day: DataFrame
    _df_train: DataFrame
    _df_test: DataFrame
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
            # radius = data['radius']
            #
            # fluid = Fluid(data['density'],
            #               data['viscosity'],
            #               data['volume_factor'])
            #
            # formation = Formation(data['formations_names'],
            #                       data['thickness'],
            #                       data['porosity'],
            #                       fluid,
            #                       data['compressibility'],
            #                       data['type_completion'],
            #                       data['type_boundaries'])

            cls._df_month = data['df_month']
            cls._df_day = data['df_day']
            report = cls._create_report()

            well = Well(name,
                        # radius,
                        # formation,
                        report)

            cls._wells.append(well)

    @classmethod
    def _create_report(cls) -> Report:
        cls._create_df_train()
        cls._create_df_fact()
        report = Report(cls._df_train, cls._df_fact)
        return report

    @classmethod
    def _create_df_train(cls):
        prediction_mode = cls._settings.prediction_mode
        train_mode = cls._settings.train_mode

        if prediction_mode == 'test':
            cls._df_test = cls._df_day.tail(cls._settings.forecast_days_number)
            cls._calc_cum_prods_df_test()
            cls._modify_df_month_df_day()

        if train_mode == 'month':
            cls._df_train = cls._calc_cum_prods(cls._df_month)
        if train_mode == 'day':
            cls._df_train = cls._df_day
            cls._calc_cum_prods_df_day()
        if train_mode == 'mix':
            cls._create_mix_month_day()
            cls._df_train = cls._calc_cum_prods(cls._df_train)

    @classmethod
    def _calc_cum_prods_df_test(cls):
        cls._df_test = cls._calc_cum_prods(cls._df_test)
        cls._add_cum_prod_before_df_test(phase='oil')
        cls._add_cum_prod_before_df_test(phase='liq')

    @classmethod
    def _add_cum_prod_before_df_test(cls, phase: str):
        cum_prod = cls._calc_cum_prod_before_df_test(phase)
        cls._df_test[f'prod_{phase}'] = cls._df_test[f'prod_{phase}'].apply(lambda x: x + cum_prod)

    @classmethod
    def _calc_cum_prod_before_df_test(cls, phase: str) -> float:
        day_date = cls._df_month.index[-1] + datetime.timedelta(days=1)
        first_test_date = cls._df_test.index[0]
        s_month = cls._df_month[f'prod_{phase}']
        s_day = cls._df_day[f'prod_{phase}'][day_date:first_test_date]
        s = s_month.append(s_day)
        cum_prod = s.sum()
        return cum_prod

    @classmethod
    def _modify_df_month_df_day(cls):
        first_test_date = cls._df_test.index[0]
        train_days_number = len(cls._df_day.index) - cls._settings.forecast_days_number
        cls._df_month = cls._df_month.loc[:first_test_date]
        cls._df_day = cls._df_day.head(train_days_number)

    @classmethod
    def _calc_cum_prods_df_day(cls):
        cls._df_day = cls._calc_cum_prods(cls._df_day)
        cls._add_cum_prod_before_df_day(phase='oil')
        cls._add_cum_prod_before_df_day(phase='liq')

    @classmethod
    def _add_cum_prod_before_df_day(cls, phase: str):
        cum_prod = cls._calc_cum_prod_before_df_day(phase)
        cls._df_day[f'prod_{phase}'] = cls._df_day[f'prod_{phase}'].apply(lambda x: x + cum_prod)

    @classmethod
    def _calc_cum_prod_before_df_day(cls, phase: str) -> float:
        dates_month = cls._df_month.index
        first_day_date = cls._df_day.index[0]
        for date in dates_month:
            if date == first_day_date:
                date += datetime.timedelta(days=1)
                s_month = cls._df_month[f'prod_{phase}'][:date]
                cum_prod = s_month.sum()
                return cum_prod
            if date > first_day_date:
                date += datetime.timedelta(days=1)
                s_month = cls._df_month[f'prod_{phase}'][:date]
                cum_prod = s_month.sum()
                for i in cls._df_day.index[:date]:
                    cum_prod -= cls._df_day[f'prod_{phase}'].loc[i]
                return cum_prod

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
    def _create_df_fact(cls):
        cls._df_fact = concat(objs=[cls._df_train, cls._df_test],
                              axis='index',
                              verify_integrity=True)

    @classmethod
    def _create_project(cls):
        cls._project = Project(cls._wells, cls._settings)

    @classmethod
    def _calc_cum_prods(cls, df: DataFrame) -> DataFrame:
        df = cls._calc_cum_prod(df, 'oil')
        df = cls._calc_cum_prod(df, 'liq')
        return df

    @staticmethod
    def _calc_cum_prod(df: DataFrame, phase: str) -> DataFrame:
        new_df = df.copy()
        new_df[f'cum_prod_{phase}'] = cumsum(df[f'prod_{phase}'].to_list())
        return new_df

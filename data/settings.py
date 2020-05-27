from pathlib import Path


class Settings(object):

    def __init__(self,
                 project_name: str,
                 forecast_days_number: int,
                 ratio_points_month_day: int,
                 path: Path):

        self.project_name = project_name
        self.forecast_days_number = forecast_days_number
        self.ratio_points_month_day = ratio_points_month_day
        self.path = path

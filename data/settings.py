from pathlib import Path


class Settings(object):

    def __init__(self,
                 forecast_days_number: int,
                 train_mode: str,
                 ratio_points_month_day: int,
                 path: Path):

        self.forecast_days_number = forecast_days_number
        self.train_mode = train_mode
        self.ratio_points_month_day = ratio_points_month_day
        self.path = path

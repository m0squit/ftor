from pathlib import Path


class Settings(object):

    def __init__(self,
                 project_name: str,
                 forecast_days_number: int,
                 prediction_mode: str,
                 train_mode: str,
                 ratio_points_month_day: int,
                 path: Path):

        self.project_name = project_name
        self.forecast_days_number = forecast_days_number
        self.prediction_mode = prediction_mode
        self.train_mode = train_mode
        self.ratio_points_month_day = ratio_points_month_day
        self.path = path

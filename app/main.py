import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository
from data.settings import Settings
from libs.plot.bokeh.research_plot import ResearchPlot
from libs.plot.plotly.flood_plot import FloodPlot
from libs.plot.plotly.units_plot import UnitsPlot
from libs.plot.plotly.performance_plot import PerformancePlot

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
forecast_days_number = 90
settings = Settings(forecast_days_number=forecast_days_number,
                    train_mode='mix',
                    ratio_points_month_day=1,
                    path=path)

repository = ExcelRepository(settings)
project = repository.create_project()
project = Calculator.run(project, forecast_days_number)

FloodPlot.create(settings, project)
# UnitsPlot.create(settings, project)
# PerformancePlot.create(settings, project)
# ResearchPlot.create(path, project)

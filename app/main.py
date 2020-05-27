import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository
from data.settings import Settings
from libs.plot.bokeh.research_plot import ResearchPlot
from libs.plot.plotly.units_plot import UnitsPlot
from libs.plot.plotly.performance_plot import PerformancePlot

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
repository = ExcelRepository(path)

settings = Settings(project_name='',
                    forecast_days_number=90,
                    ratio_points_month_day=10,
                    path=path)
project = repository.create_project(settings)
project = Calculator.run(project)

UnitsPlot.create(settings, project)
PerformancePlot.create(settings, project)
ResearchPlot.create(path, project)

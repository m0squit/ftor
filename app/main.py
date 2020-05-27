import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository
from data.settings import Settings
from libs.plot.bokeh.research_plot import ResearchPlot
from libs.plot.plotly.units_plot import UnitsPlot
from libs.plot.plotly.performance_plot import PerformancePlot


path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'


def run_app(settings: Settings):
    repository = ExcelRepository(path)
    project = repository.create_project(settings)
    project = Calculator.run(project)
    UnitsPlot.create(settings, project)
    # ResearchPlot.create(path, project)
    PerformancePlot.create(settings, project)


ratios = [5]
for ratio in ratios:
    _settings = Settings(project_name='',
                         forecast_days_number=90,
                         ratio_points_month_day=ratio,
                         path=path)
    run_app(_settings)

import pathlib
import xlwings as xw

from app.calculator import Calculator
from data.excel import ExcelRepository
from data.settings import Settings
from libs.plot.bokeh.research_plot import ResearchPlot
from libs.plot.plotly.rates_plot import RatesPlot
from libs.plot.plotly.watercuts_plot import WatercutsPlot
from libs.plot.plotly.performance_plot import PerformancePlot

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'otdelnoe'


def run_app(settings: Settings):
    repository = ExcelRepository(path)
    project = repository.create_project(settings)
    project = Calculator.run(project)
    RatesPlot.create(settings, project)
    WatercutsPlot.create(settings, project)
    # ResearchPlot.create(path, project)
    PerformancePlot.create(settings, project)

    # wb = xw.Book()
    # sht = wb.sheets['Лист1']
    # col = 1
    # for well in project.wells:
    #     sht.range((1, col)).value = well.name
    #     df = well.report.df_test_month[['prod_oil', 'prod_oil_model', 'prod_oil_ksg']]
    #     sht.range((2, col)).value = df
    #     col += 4
    # wb.save(path=path / 'oil_prod_values.xlsx')
    # wb.close()


ratios = [0.5]
for ratio in ratios:
    _settings = Settings(project_name='',
                         forecast_days_number=90,
                         ratio_points_month_day=ratio,
                         path=path)
    run_app(_settings)

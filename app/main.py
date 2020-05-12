import pathlib
import xlwings as xw

from app.calculator import Calculator
from data.excel import ExcelRepository
from libs.plot.bokeh.research_plot import ResearchPlot
from libs.plot.plotly.units_plot import UnitsPlot
from libs.plot.plotly.performance_plot import PerformancePlot

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
repository = ExcelRepository(path)
project = repository.create_project()
project = Calculator.run(project)
UnitsPlot.create(path, project)
PerformancePlot.create(path, project)
# ResearchPlot.create(path, project)

# wb = xw.Book()
# for zone in project.zones:
#     well_name = zone.well.name
#     sht = wb.sheets.add(name=f'{well_name}')
#     df = zone.report.df_result[['prod_oil',
#                                 'prod_oil_model',
#                                 'dev_rel_rate_oil',
#                                 'dev_abs_cum_oil']]
#     sht.range('A1').value = df
# wb.sheets['Лист1'].delete()
# wb.save(path=path / 'results')
# wb.close()

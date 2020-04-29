import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository
from libs.plot.plotly.units_plot import UnitsPlot
from libs.plot.plotly.performance_plot import PerformancePlot

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
repository = ExcelRepository(path)
project = repository.create_project()
project = Calculator.run(project)
UnitsPlot.create(path, project)
PerformancePlot.create(path, project)

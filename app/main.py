import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository
from libs.plot.plotly import Plotly

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
repository = ExcelRepository(path)
project = repository.create_project()
project = Calculator.run(project)
Plotly.create_figures(path, project)

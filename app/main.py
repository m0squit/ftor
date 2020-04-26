import pathlib

from app.calculator import Calculator
from data.excel import ExcelRepository

path = pathlib.Path.cwd().parent / 'tests' / 'data' / 'real' / 'nng' / 'kholmogorskoe'
repository = ExcelRepository(path)
project = repository.create_project()
project = Calculator.run(project)

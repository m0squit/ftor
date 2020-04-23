from app.calculator import Calculator
from data.excel import ExcelRepository

path = 'str'
repository = ExcelRepository(path)
project = repository.create_project()
project = Calculator.run(project)

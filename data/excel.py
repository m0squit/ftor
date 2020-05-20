from pathlib import Path

from data._repository import _Repository
from domain.factories.parser.parser import Parser


class ExcelRepository(_Repository):

    def __init__(self,
                 path: Path):

        self.path = path
        self._get_data()

    def _get_data(self):
        self.data = Parser().run(self.path)

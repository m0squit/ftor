from data._repository import _Repository
from data.settings import Settings
from libs.parser.parser import Parser


class ExcelRepository(_Repository):

    def __init__(self,
                 settings: Settings):

        super().__init__(settings)
        self._get_data()

    def _get_data(self):
        self.data = Parser().run(self.settings)

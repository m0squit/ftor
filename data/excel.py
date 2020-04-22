from data.repository import Repository
from libs.parser.reader import Reader


class ExcelRepository(Repository):

    def __init__(self,
                 path):
        super().__init__()
        self.path = path
        self._get_data()

    def _get_data(self):
        self.data = Reader().run(self.path)

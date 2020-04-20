from data.repository import Repository
from libs.reader import Reader


class ExcelRepository(Repository):

    def __init__(self,
                 path):
        super().__init__()
        self.path = path

    def get_data(self):
        self.data = Reader().run(self.path)

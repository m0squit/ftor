class InputData(object):
    """Class for data in ObjectCreator to create project."""
    def __init__(self):
        self.wells = {}

    def add_well(self, name: str, data: dict):
        self.wells[name] = data

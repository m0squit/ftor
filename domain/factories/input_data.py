class InputData(object):
    """Class for data in ObjectCreator to create project."""
    def __init__(self):
        self.wells = {}

    def add_well(self, well_name: str, well_data: dict):
        self.wells[well_name] = well_data

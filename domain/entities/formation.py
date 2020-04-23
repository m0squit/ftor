class Formation(object):

    def __init__(self,
                 name: str,
                 porosity: float,
                 compressibility_total: float):

        self.name = name
        self.porosity = porosity
        self.compressibility_total = compressibility_total
        self.zones = []

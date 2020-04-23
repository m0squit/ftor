class Formation(object):

    def __init__(self,
                 name,
                 porosity,
                 compressibility_total):

        self.name = name
        self.porosity = porosity
        self.compressibility_total = compressibility_total
        self.zones = []

class Formation(object):

    def __init__(self,
                 name,
                 reservoir,
                 fluid,
                 compressibility_total):

        self.name = name
        self.reservoir = reservoir
        self.fluid = fluid
        self.compressibility_total = compressibility_total
        self.zones = []

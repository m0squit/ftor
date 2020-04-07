class Fluid(object):

    def __init__(self,
                 viscosity,
                 compressibility,
                 volume_expansion):
        self.viscosity = viscosity
        self.compressibility = compressibility
        self.volume_expansion = volume_expansion

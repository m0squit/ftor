class Fluid(object):

    def __init__(self,
                 density,
                 viscosity,
                 volume_factor):

        self.density = density
        self.viscosity = viscosity
        self.volume_factor = volume_factor

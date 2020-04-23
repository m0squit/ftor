class Fluid(object):

    def __init__(self,
                 density: float,
                 viscosity: float,
                 volume_factor: float):

        self.density = density
        self.viscosity = viscosity
        self.volume_factor = volume_factor

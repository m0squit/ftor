from domain.value_objects.fluid import Fluid


class Formation(object):

    def __init__(self,
                 name: str,
                 thickness: float,
                 porosity: float,
                 fluid: Fluid,
                 compressibility: float,
                 type_completion: str,
                 type_boundaries: str,):

        self.name = name
        self.thickness = thickness
        self.porosity = porosity
        self.fluid = fluid
        self.compressibility = compressibility
        self.type_completion = type_completion
        self.type_boundaries = type_boundaries

class Reservoir(object):

    def __init__(self,
                 thickness,
                 porosity,
                 permability,
                 compressibility,
                 pressure_initial):
        self.thickness = thickness
        self.porosity = porosity
        self.permability = permability
        self.compressibility = compressibility
        self.pressure_initial = pressure_initial

    def calc_deliverability(self, fluid):
        deliverability = self.permability * self.thickness / fluid.viscosity
        return deliverability

    def calc_conductivity(self, fluid):
        compressibility_total = self.compressibility + fluid.compressibility
        conductivity = self.permability / (self.porosity * fluid.viscosity * compressibility_total)
        return conductivity

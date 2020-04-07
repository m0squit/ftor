class Well(object):

    def __init__(self,
                 radius,
                 wellbore_storage,
                 skin,
                 pressure_bottomhole):
        self.radius = radius
        self.wellbore_storage = wellbore_storage
        self.skin = skin
        self.pressure_bottomhole = pressure_bottomhole

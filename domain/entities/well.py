class Well(object):

    def __init__(self,
                 name: str,
                 radius: float):

        self.name = name
        self.radius = radius
        self.zones = []

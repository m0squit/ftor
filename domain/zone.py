class Zone(object):

    def __init__(self,
                 well,
                 formation,
                 data):

        self.well = well
        self.formation = formation
        self.data = data

    def _create_model_rate_liquid(self):
        pass

    def _create_model_watercut(self):
        pass

    def _predict(self):
        pass

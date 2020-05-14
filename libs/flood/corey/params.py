class CoreyModelParams(object):

    usable_params = {'watercut_initial': {'min': 0, 'max': 1},
                     'mobility_ratio': {'min': 0.0025, 'max': 50},
                     'alpha': {'min': 1, 'max': 6},
                     'beta': {'min': 1, 'max': 6}}

    def __init__(self):
        self.watercut_initial = None
        self.mobility_ratio = None
        self.alpha = None
        self.beta = None
        self.stoiip = None

    def set_values(self, params):
        self.watercut_initial = params[0]
        self.mobility_ratio = params[1]
        self.alpha = params[2]
        self.beta = params[3]
        if 'stoiip' in self.usable_params:
            self.stoiip = params[4]

    def get_values(self):
        values = [self.watercut_initial,
                  self.mobility_ratio,
                  self.alpha,
                  self.beta]
        if self.stoiip is not None:
            values.append(self.stoiip)
        return values

    def get_units(self):
        units = {'watercut_initial': 'fr',
                 'mobility_ratio': 'dim',
                 'alpha': 'dim',
                 'beta': 'dim'}
        if self.stoiip is not None:
            units['stoiip'] = 'mn_m3'
        return units

class CoreyModelParams(object):

    usable_params = {'watercut_initial': {'min': 0,
                                          'max': 1,
                                          'init': 0.05},

                     'mobility_ratio': {'min': 0.01,
                                        'max': 5,
                                        'init': 1.66},

                     'alpha': {'min': 0.5,
                               'max': 20,
                               'init': 3.50},

                     'beta': {'min': 0.1,
                              'max': 20,
                              'init': 3.77}}

    def __init__(self):
        self.watercut_initial = None
        self.mobility_ratio = None
        self.alpha = None
        self.beta = None
        self.stoiip = None

    def set_values(self, *params):
        self.watercut_initial = params[0]
        self.mobility_ratio = params[1]
        self.alpha = params[2]
        self.beta = params[3]
        if 'stoiip' in self.usable_params:
            self.stoiip = params[4]

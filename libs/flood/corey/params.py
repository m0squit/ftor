from typing import List, Dict


class CoreyModelParams(object):

    usable_params = {'watercut_initial': {'min': -0.5, 'max': 1},
                     'mobility_ratio': {'min': 0.0025, 'max': 50},
                     'alpha': {'min': 1, 'max': 6},
                     'beta': {'min': 1, 'max': 6},
                     'stoiip': {'min': None, 'max': None}}

    def __init__(self):
        self.watercut_initial = None
        self.mobility_ratio = None
        self.alpha = None
        self.beta = None
        self.stoiip = None

    def get_values(self) -> List[float]:
        values = [self.watercut_initial,
                  self.mobility_ratio,
                  self.alpha,
                  self.beta,
                  self.stoiip]
        return values

    def set_values(self, params: List[float]):
        self.watercut_initial = params[0]
        self.mobility_ratio = params[1]
        self.alpha = params[2]
        self.beta = params[3]
        self.stoiip = params[4]

    @staticmethod
    def get_units() -> Dict[str, str]:
        units = {'watercut_initial': 'fr',
                 'mobility_ratio': 'dim',
                 'alpha': 'dim',
                 'beta': 'dim',
                 'stoiip': 'mn_m3'}
        return units

class WatercutModel(object):

    def __init__(self,
                 wc_initial,
                 mobility_ratio,
                 alpha,
                 beta,
                 stoiip):

        self.wc_initial = wc_initial
        self.mobility_ratio = mobility_ratio
        self.alpha = alpha
        self.beta = beta
        self.stoiip = stoiip

    def calc(self, cum_prod):
        recovery_factor = cum_prod / self.stoiip
        term_1 = (1 - recovery_factor) ** self.alpha
        term_2 = self.mobility_ratio * recovery_factor ** self.beta
        watercut = self.wc_initial + (1 - self.wc_initial) / (1 + term_1 / term_2)
        return watercut

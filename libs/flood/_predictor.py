from libs.numeric_tools.solver import solve_ode


class _Predictor(object):

    _flood_model = None
    _cum_prods_oil = None

    @classmethod
    def run(cls, cum_prod_oil_start, cum_prods_liq, model):
        cls._flood_model = model
        cls._calc_cum_prods_oil(cum_prod_oil_start, cum_prods_liq)
        return cls._cum_prods_oil

    @classmethod
    def _calc_cum_prods_oil(cls, cum_prod_oil_start, cum_prods_liq):
        cls._cum_prods_oil = solve_ode(fun=cls._calc_right_hand_side_ode,
                                       y0=[cum_prod_oil_start],
                                       t_span=(cum_prods_liq[0], cum_prods_liq[-1]),
                                       t_eval=cum_prods_liq[1:])

    @classmethod
    def _calc_right_hand_side_ode(cls, cum_prod_liq, cum_prod_oil):
        stoiip = cls._flood_model.params.stoiip
        recovery_factor = cum_prod_oil / stoiip
        term = (1 - cls._flood_model.calc_watercut(recovery_factor)) * 1 / stoiip
        return term

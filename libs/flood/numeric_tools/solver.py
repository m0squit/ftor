from scipy import integrate


def solve_ode(fun, t_span, y0, t_eval):
    solution = integrate.solve_ivp(fun=fun,
                                   t_span=t_span,
                                   y0=y0,
                                   method='RK45',
                                   t_eval=t_eval)
    return list(solution.y[0])

def rk4_step(func, y_n, t_n, h):
    '''returns t_n+1, y_n+1'''
    k1 = func(t_n, y_n)
    k2 = func(t_n + h / 2, y_n + h * k1 / 2)
    k3 = func(t_n + h / 2, y_n + h * k2 / 2)
    k4 = func(t_n + h, y_n + h * k3)
    return t_n + h, y_n + h / 6 * ( k1 + 2 * k2 + 2 * k3 + k4 )

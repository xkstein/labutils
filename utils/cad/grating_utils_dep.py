import gdspy
import numpy as np

def make_grating_path(path: gdspy.Path, N: int, period: float, duty_cycle: float, high_width: float, low_width: float, transition=0.001, front_taper_n=0, back_taper_n=0):
    ''' Makes square bragg gratings for path objects and adds linearly interpolating tapers

    **This is depricated because it uses more polygons than `make_grating_low_poly`**

    path: gdspy.Path to make grating on (also copies the layer and direction data from the last segment)
    N: number of period in grating (including tapers)
    duty_cycle: high vs low expressed as a decimal. i.e. 80% high is 0.8
    high_width: width of high parts of the grating
    low_width: width of low parts of the grating
    direction: vector expressed as 2d np array of the grating's direction
    transition: the length to transition between high and low
    front_taper_n: number of periods to taper in for (the nth will be at `high_width`)
    back_taper_n: number of periods to taper out for (everything after the N-nth will be less than `high_width`)
    '''
    direction = path.direction
    layer = path.layers[-1]
    datatype = path.datatypes[-1]

    high_dist = duty_cycle * period - transition
    low_dist = ( 1 - duty_cycle ) * period - transition

    assert N >= (front_taper_n + back_taper_n), 'need meat between tapers dumbo'

    def _high_func(n):
        if n < front_taper_n - 1:
            return ( n + 1 ) * (high_width - low_width) / front_taper_n + low_width
        elif (N - n) < back_taper_n:
            return (N - n) * (high_width - low_width) / back_taper_n + low_width
        return high_width

    for n in range(N):
        path.segment(transition, direction=direction, final_width=_high_func(n), layer=layer, datatype=datatype)
        path.segment(high_dist, direction=direction, layer=layer, datatype=datatype)
        path.segment(transition, direction=direction, final_width=low_width, layer=layer, datatype=datatype)
        path.segment(low_dist, direction=direction, layer=layer, datatype=datatype)
    return path

def make_grating_robust_path(path: gdspy.RobustPath, N: int, period: float, duty_cycle: float, high_width: float, low_width: float, transition=0.001, front_taper_n=0, back_taper_n=0):
    ''' Makes square bragg gratings and adds linearly interpolating tapers

    **This is depricated bc RobustPath is slow asf**

    path: gdspy.RobustPath to make grating on
    N: number of period in grating (including tapers)
    duty_cycle: high vs low expressed as a decimal. i.e. 80% high is 0.8
    high_width: width of high parts of the grating
    low_width: width of low parts of the grating
    direction: vector expressed as 2d np array of the grating's direction
    transition: the length to transition between high and low
    front_taper_n: number of periods to taper in for (the nth will be at `high_width`)
    back_taper_n: number of periods to taper out for (everything after the N-nth will be less than `high_width`)
    '''
    direction = path.grad(len(path))[0]
    direction = direction / np.sqrt(np.sum( direction @ direction ))

    high_dist = duty_cycle * period - transition
    low_dist = ( 1 - duty_cycle ) * period - transition

    assert N > (front_taper_n + back_taper_n), 'need meat between tapers dumbo'

    def _high_func(n):
        if n < front_taper_n - 1:
            return ( n + 1 ) * (high_width - low_width) / front_taper_n + low_width
        elif (N - n) < back_taper_n:
            return (N - n) * (high_width - low_width) / back_taper_n + low_width
        return high_width

    for n in range(N):
        path.segment(transition * direction, width=_high_func(n), relative=True)
        path.segment(high_dist * direction, relative=True)
        path.segment(transition * direction, width=low_width, relative=True)
        path.segment(low_dist * direction, relative=True)
    return path

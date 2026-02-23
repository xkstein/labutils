import gdspy
from typing import Callable, Iterable
import numpy as np

def add_arbitrary_grating(path: gdspy.Path, length: np.ndarray | float, width: np.ndarray | Callable, max_points=8190) -> gdspy.Path:
    '''
    Adds arbitrarily varying width segment to a path

    Arguments:
        path: `gdapy.Path` object to append segment to
        length: Array stepping from 0 to L (where L is the total length of the new 
            segment) that used to calculate segment width and determines the number 
            of points in the polygon. If float it's just 
            `np.linspace(0, length, max_points // 2)`
        width: func or array that describes waveguide width as a function of length
    '''
    if isinstance(length, float):
        length = np.linspace(0, length, max_points // 2)
    direction_lut = {
        '+x': 0,
        '-x': np.pi,
        '+y': np.pi / 2,
        '-y': 3 * np.pi / 2,
    }
    if isinstance(path.direction, str):
        angle = direction_lut[path.direction]
    else:
        angle = path.direction

    x = np.cos(angle) * length + path.x
    y = np.sin(angle) * length + path.y

    if isinstance(width, np.ndarray | list):
        assert len(width) == len(length), 'if width is prescribed, it must have the same length as length'
        w = width
    else:
        w = width(length)

    top = np.vstack((x - np.sin(angle) * w / 2, y + np.cos(angle) * w / 2)).T
    bottom = np.vstack(((x + np.sin(angle) * w / 2), (y - np.cos(angle) * w / 2))).T

    n_sections = np.ceil(len(length) / 4094).astype(int)
    for ind in range(n_sections):
        if len(length) < (ind + 1) * 4094:
            _top = top[ind * 4094:]
            _bot = bottom[ind * 4094:]
        else:
            _top = top[ind * 4094:(ind + 1) * 4094 + 1]
            _bot = bottom[ind * 4094:(ind + 1) * 4094 + 1]
        pts = np.concat((_top, _bot[::-1]))
        path.polygons.append(pts)
        path.layers.extend(path.layers[-1] for _ in range(path.n))
        path.datatypes.extend(path.datatypes[-1] for _ in range(path.n))
    path.x = x[-1]
    path.y = y[-1]
    path.w = w[-1] * 0.5
    path.length += max(length)
    return path

def make_grating_low_poly(path: gdspy.Path, N: int, period: float, 
          duty_cycle: float, high_width: float, low_width: float, 
          transition=0.001, front_taper_n=0, back_taper_n=0, 
          front_taper_cuts_n=0, back_taper_cuts_n=0):
    ''' Makes square bragg gratings for path objects and adds linearly interpolating tapers

    Arguments:
        path: gdspy.RobustPath to make grating on (also copies the layer and direction data from the last segment)
        N: number of period in grating (including tapers)
        duty_cycle: high vs low expressed as a decimal. i.e. 80% high is 0.8
        high_width: width of high parts of the grating
        low_width: width of low parts of the grating
        transition: the length to transition between high and low
        front_taper_n: number of periods to taper in for (the nth will be at `high_width`)
        back_taper_n: number of periods to taper out for (everything after the N-nth will be less than `high_width`)
        front_taper_cuts_n: tapering in by cutting into the high width
        back_taper_cuts_n: tapering out by cutting into the high width
    '''
    low_dist = ( 1 - duty_cycle ) * period

    assert N >= (front_taper_n + back_taper_n), 'need meat between tapers dumbo'

    def _high_func(n):
        if n < front_taper_n - 1:
            return ( n + 1 ) * (high_width - low_width) / front_taper_n + low_width
        elif (N - n) < back_taper_n:
            return (N - n) * (high_width - low_width) / back_taper_n + low_width
        return high_width

    def _low_func(n):
        if n < front_taper_cuts_n - 1:
            return high_width - ( n + 1 ) * (high_width - low_width) / front_taper_cuts_n
        elif (N - n) < back_taper_cuts_n:
            return high_width - (N - n) * (high_width - low_width) / back_taper_cuts_n
        return low_width

    length = np.array([])
    width = np.array([])
    for n in range(N):
        length = np.concat((
            length, 
            n * period + np.array([0, low_dist - transition, low_dist, period - transition])
        ))
        width = np.concat((
            width,
            [_low_func(n), _low_func(n), _high_func(n), _high_func(n)]
        ))
    length = np.concat((length, [N * period, N * period + low_dist]))
    width = np.concat((width, [_low_func(N), _low_func(N)]))
    return add_arbitrary_grating(path, length, width)

if __name__ == '__main__':
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell('grating')

    path = gdspy.Path(1.5, (0,0))
    path.segment(10, np.pi / 4)
    path = make_grating_low_poly(path, N=100, period=1, duty_cycle=0.8, 
                                 high_width=2.5, low_width=1.5, 
                                 front_taper_n=10, back_taper_cuts_n=10)
    path.segment(10)
    cell.add(gdspy.Text('Square grating with tapers\n(notice how it tapers to high width at the top and the low width at the bottom)', 10, (0, -10)))
    cell.add(path)

    x = np.linspace(0, 10, 120, endpoint=False)
    width = np.cos(2 * np.pi * x - np.pi) / 2 + 2

    path = gdspy.Path(1.5, (0,500))
    path.segment(10, np.pi / 2)
    path = add_arbitrary_grating(path, x, width)
    path.segment(10)
    cell.add(path)
    cell.add(gdspy.Text('Sinusoidal grating', 10, (0, 490)))

    gdspy.LayoutViewer(lib)
    lib.write_gds('grating_test.gds')
    # reload('util_test.gds')


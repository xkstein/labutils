import gdspy
import numpy as np

def assign_layer(path: gdspy.Path, layer: int, datatype: int = 0):
    '''Sets the layer/datatype of a path'''
    path.layers = len(path.layers) * [layer]
    path.datatypes = len(path.datatypes) * [datatype]
    return path

def remove_path_link(path, n: int=1, direction='x'):
    if direction == 'x':
        pos = np.mean(path.polygons[-n][:2], axis=0)
    elif direction == 'y':
        pos = np.mean(path.polygons[-n][1:-1], axis=0)
    path.x = pos[0]
    path.y = pos[1]
    path.polygons = path.polygons[:-n]
    path.layers = path.layers[:-n]
    path.datatypes = path.datatypes[:-n]
    return path

def find_length(obj: gdspy.Path | gdspy.Cell):
    if isinstance(obj, gdspy.Rectangle):
        return 4
    elif isinstance(obj, gdspy.Polygon | np.ndarray):
        return len(obj)

    length = 0
    for polygon in obj.polygons:
        length += find_length(polygon)
    return length

def angle_to_unit(angle):
    if isinstance(angle, gdspy.Path):
        angle = angle.direction
    return np.array([np.cos(angle), np.sin(angle)])

def tangent_tangent_radius(path, pos_out, vec_out, radius):
    '''Connects two tangent vectors to create a rounded corner
    Requires the path and the vector to be CONVERGING

    Arguments:
        path: gdapy.Path (will be used to find pos_in and vec_in)
        pos_out: target position to reach
        vec_out: direction of the path at the target position, pointing in
        radius: desired bend radius

    Uses Cramer\'s Rule for line intercepts
    '''
    length = lambda a: np.sqrt(a @ a)
    norm = lambda a: a / length(a)

    vec_in = norm(angle_to_unit(path))
    vec_out = norm(vec_out)
    pos_in = np.array([path.x, path.y])

    if np.isclose(norm(vec_in) @ norm(vec_out), -1):
        path.segment(length(pos_out - pos_in))
        return path
    
    A = np.array([[-vec_in[1], vec_in[0]],
                  [-vec_out[1], vec_out[0]]])
    b = np.array([(A @ pos_in)[0], (A @ pos_out)[1]])

    cramer = np.linalg.det(A)
    assert cramer != 0, 'vectors are parallel'
    intersection = np.array([b[0] * A[1,1] - b[1] * A[0,1], 
                             b[1] * A[0,0] - b[0] * A[1,0]]) / cramer

    alpha = np.arccos( (vec_in @ vec_out) / (np.sqrt(vec_in @ vec_in) * np.sqrt(vec_out @ vec_out)) )
    center_dist = radius / np.sin(alpha / 2)

    bend_pt1 = intersection - np.sqrt(center_dist ** 2 - radius ** 2) * vec_in / np.sqrt(vec_in @ vec_in)
    bend_pt2 = intersection - np.sqrt(center_dist ** 2 - radius ** 2) * vec_out / np.sqrt(vec_out @ vec_out)

    assert (intersection - pos_in) @ vec_in > 0, 'Paths are diverging'
    assert (intersection - pos_out) @ vec_out > 0, 'Paths are diverging'

    orth_vec_in = np.array([-vec_in[1], vec_in[0]])
    sign = -np.sign( (intersection - pos_out) @ orth_vec_in )

    path.segment(length(bend_pt1 - pos_in))
    path.turn(radius, sign * (np.pi - alpha))
    path.segment(length(bend_pt2 - pos_out))
    return path


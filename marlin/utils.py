import numpy as np

from simple_pid import PID


def clip(x, xmin, xmax):
    return min(max(x, xmin), xmax)


def closestPointOnLine(a, b, p, offset=0):
    ap = p - a
    ab = b - a

    # project point onto line
    result = a + np.dot(ap, ab) / np.dot(ab, ab) * ab

    # add offset
    result = result + (ab / np.linalg.norm(ab) * offset)

    # check if point outside line
    scale = np.dot(result - a, ab) / np.dot(ab, ab)

    return result, scale

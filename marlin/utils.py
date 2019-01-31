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


def directionError(position, goal, direction):
    d1 = goal - position
    d1 = d1/np.linalg.norm(d1)
    err = np.arccos(np.dot(d1, direction))*2/np.pi
    err *= np.sign(np.cross(d1, direction))
    return err


def headingToVector(heading):
    rad = heading*np.pi/180
    return np.array([np.cos(rad), np.sin(rad)])

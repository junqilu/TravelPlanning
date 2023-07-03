from scipy.spatial import ConvexHull
from scipy import interpolate

import numpy as np


def generate_convex_hull(points):
    hull = ConvexHull(points)  # Get convex hull

    # get x and y coordinates
    # repeat last point to close the polygon
    x_hull = np.append(
        points[hull.vertices, 0],
        points[hull.vertices, 0][0]
    )
    y_hull = np.append(
        points[hull.vertices, 1],
        points[hull.vertices, 1][0]
    )

    return x_hull, y_hull


def generate_interpolation(x_hull, y_hull):
    # Make interpolation from convex hull
    dist = np.sqrt(
        (x_hull[:-1] - x_hull[1:]) ** 2 + (y_hull[:-1] - y_hull[1:]) ** 2)
    dist_along = np.concatenate(([0], dist.cumsum()))
    spline, u = interpolate.splprep(
        [x_hull, y_hull],
        u=dist_along,
        s=0,
        per=1
    )
    interp_d = np.linspace(dist_along[0], dist_along[-1], 50)
    interp_x, interp_y = interpolate.splev(interp_d, spline)

    return interp_x, interp_y






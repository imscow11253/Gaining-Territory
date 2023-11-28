from scipy.spatial import ConvexHull
import numpy as np

def ConvexHull2(points):
    upper = []
    lower = []
    for p in sorted(points):
        while len(upper) > 1 and ccw(upper[-2], upper[-1], p) > 0:
            upper.pop()
        while len(lower) > 1 and ccw(lower[-2], lower[-1], p) < 0:
            lower.pop()
        upper.append(p)
        lower.append(p)
 
    convex_points = upper + lower
    result = []
    [result.append(x) for x in convex_points if x not in result]
    return result

def ccw(a,b,c):
    return a[0]*b[1] + b[0]*c[1] + c[0]*a[1] - (b[0]*a[1] + c[0]*b[1] + a[0]*c[1])


point_list = [[0,0], [2,1], [3,2], [2,3], [0,6],[3,6],[4,3],[4,6],[6,1],[6,6]]
print(ConvexHull2(point_list))

from numpy import floor

def Coords2Indices(point, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    x = int(floor((point[0] - xllcorner) / cellsize))
    y = int(floor((point[1] - yllcorner) / cellsize))
    return (y, x)

def Coords2IndicesAr(points, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    xs = []
    ys = []
    for point in points:
        x, y = Coords2Indices(point, cellsize, xllcorner, yllcorner)
        xs.append(x)
        ys.append(y)
    return xs, ys

def upsampleGeoJSON(coords_ar, rate):
    if rate == 1: raise ValueError('Upsample rate cannot be 1')
    if rate != int(rate): raise ValueError('Upsample rate must be integer')

    upcoords_ar = [coords_ar[-1]]
    for curr in coords_ar:
        prev = upcoords_ar[-1]
        for i in range(1, rate):
            x = prev[0] + i * (curr[0] - prev[0]) / (rate-1)
            y = prev[1] + i * (curr[1] - prev[1]) / (rate-1)
            upcoords_ar.append((x,y))

    return upcoords_ar

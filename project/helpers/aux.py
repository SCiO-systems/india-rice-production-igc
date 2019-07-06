import numpy as np
from matplotlib.path import Path

def Coords2Indices(point, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    x = int(np.floor((point[0] - xllcorner) / cellsize))
    y = int(np.floor((point[1] - yllcorner) / cellsize))
    return (y, x)

def Coords2IndicesAr(points, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    coords = []
    for point in points:
        coords.append(Coords2Indices(point, cellsize, xllcorner, yllcorner))
    return coords

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

def ascRead(filename):
    with open(filename, 'r') as f:
        line = f.readline()
        data = []
        while line:
            if line.startswith('ncols'):
                ncols = int(line.split()[1])
            elif line.startswith('nrows'):
                nrows = int(line.split()[1])
            elif line.startswith('xllcorner'):
                xllcorner = int(line.split()[1])
            elif line.startswith('yllcorner'):
                yllcorner = int(line.split()[1])
            elif line.startswith('cellsize'):
                cellsize = float(line.split()[1])
            elif line.startswith('NODATA'):
                nodataval = int(line.split()[1])
            else:
                data.append([int(d) for d in line.split()])
            line = f.readline()

    return nrows, ncols, xllcorner, yllcorner, cellsize, nodataval, np.array(data)

def fillPolygon4Raster(perimeter, rows=900, cols=2160):
    x, y = np.meshgrid(np.arange(rows), np.arange(cols))
    x, y = x.flatten(), y.flatten()
    geo_points = np.vstack((x,y)).T

    p = Path(perimeter)
    grid = p.contains_points(geo_points)
    return np.flip(grid.reshape(cols, rows).T, 0)

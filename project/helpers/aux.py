import numpy as np
from matplotlib.path import Path

def Coords2Indices(point, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    # point in (>, Λ) => (x,y) reversed for matrix conventions (V, >)
    x = int(np.floor((point[0] - xllcorner) / cellsize))
    y = int(np.floor((point[1] - yllcorner) / cellsize))
    return (y, x)

def Coords2IndicesAr(points, cellsize=0.16666666667, xllcorner=-180, yllcorner=-60):
    coords = []
    for point in points:
        # NOTE: duplicates because of upsampling (replace with (ordered) set?)
        coords.append(Coords2Indices(point, cellsize, xllcorner, yllcorner))
    return coords

def upsampleGeoJSON(coords_ar, rate):
    '''
    Upsamples coordinates parsed from a GEOJSON file
    by addind coordinates on the line between consecutive
    coordinates
    '''
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
                # .asc format provides data from top left point in rows
                data.append([int(d) for d in line.split()])
            line = f.readline()

    return nrows, ncols, xllcorner, yllcorner, cellsize, nodataval, np.array(data)

def fillPolygon4Raster(perimeter, rows=900, cols=2160):
    '''
    Given the indices of the perimeter, returns the filled polygon
    (inclusive) 
    '''
    x, y = np.meshgrid(np.arange(rows), np.arange(cols))
    x, y = x.flatten(), y.flatten()
    geo_points = np.vstack((x,y)).T

    p = Path(perimeter)
    grid = p.contains_points(geo_points)
    # np.flip(axis=0) to get [0,0] as top left point of raster
    return np.flip(grid.reshape(cols, rows).T, 0)

def boundingBoxAr(coords, nodataval=-9999):
    def boundOneDimension(a):
        n, m = a.shape
        foundmin = False
        foundmax = True
        for i in range(n):
            for j in range(m):
                if not foundmin and a[i,j] != nodataval:
                    foundmin = True
                    tl = i
                if a[i,j] != nodataval:
                    foundmax = False
            if foundmin and foundmax:
                lr = i
                break
            else:
                foundmax = True
        return tl, lr

    # 1 connected component
    coords = np.array(coords)
    in_itl, in_ilr = boundOneDimension(coords)
    in_jtl, in_jlr = boundOneDimension(coords.T)
    return in_itl, in_jtl, in_ilr, in_jlr

def boundingBoxPer(perimeter, rows):
    in_itl = min([i for i,_ in perimeter])
    in_jtl = min([j for _,j in perimeter])
    in_ilr = max([i for i,_ in perimeter])
    in_jlr = max([j for _,j in perimeter])
    # because of np.flip in fillPolygon4Raster, xs must be reversed (rows - _)
    return rows - in_ilr - 1, in_jtl, rows - in_itl - 1, in_jlr

def padding(bb, rows, cols, pad=3):
    return max(bb[0] - pad, 0), max(bb[1] - pad, 0), \
        min(bb[2] + pad, rows-1), min(bb[3] + pad, cols-1)
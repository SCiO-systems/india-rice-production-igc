'''This file coontains helper function for .asc parsing and coordinate cropping'''

import numpy as np
from matplotlib.path import Path
from scipy.ndimage.morphology import binary_closing


def coords2indices(point, xcellsize=0.16666666667, ycellsize=0.166666667,
                   xllcorner=-180, yllcorner=-60):
    '''Returns array indices of geographical point'''
    # point in (>, Λ) => (x,y) reversed for matrix conventions (V, >)
    j_ar = int(np.floor((point[0] - xllcorner) / xcellsize))
    i_ar = int(np.floor((point[1] - yllcorner) / ycellsize))
    return (i_ar, j_ar)

def coords2indices_ar(points, xcellsize=0.16666666667, ycellsize=0.166666667,
                      xllcorner=-180, yllcorner=-60):
    '''Returns array indices of multiple geographical points'''
    coords = []
    for point in points:
        # NOTE: duplicates because of upsampling (replace with (ordered) set?)
        coords.append(coords2indices(point, xcellsize, ycellsize, xllcorner, yllcorner))
    return coords

def upsample_geojson(coords_ar, rate):
    '''
    Upsamples coordinates parsed from a GEOJSON file
    by addind coordinates on the line between consecutive
    coordinates
    '''
    if rate == 1:
        raise ValueError('Upsample rate cannot be 1')
    if rate != int(rate):
        raise ValueError('Upsample rate must be integer')

    upcoords_ar = [coords_ar[-1]]
    for curr in coords_ar:
        prev = upcoords_ar[-1]
        for i in range(1, rate):
            lng = prev[0] + i * (curr[0] - prev[0]) / (rate-1)
            lat = prev[1] + i * (curr[1] - prev[1]) / (rate-1)
            upcoords_ar.append((lng, lat))

    return upcoords_ar

def asc_read(filename):
    '''Read asc file. Returns (ordered)
    `nrows`, `ncols`, `xllcorner`, `yllcorner`,
    `cellsize`, `data_array` (numpy array)'''
    with open(filename, 'r') as fdc:
        line = fdc.readline()
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
            line = fdc.readline()

    return nrows, ncols, xllcorner, yllcorner, cellsize, nodataval, np.array(data)

def fill_polygon_for_raster(perimeter, rows=900, cols=2160,
                            flip=True, closing={'close': False, 'struct': np.ones((4, 4))}):
    '''Given the indices of the perimeter,
    returns the filled polygon (inclusive)

    Arguments:

    `perimeter`: points on perimeter (inorder preferable)

    `rows`: #rows

    `cols`: #columns

    `flip`: bool, flip final result

    `closing`: dict, required keys `'close'` (bool) & `'struct'` (2d iterable),
    perform binary closing on result
    '''
    xs_2d, ys_2d = np.meshgrid(np.arange(rows), np.arange(cols))
    xs_2d, ys_2d = xs_2d.flatten(), ys_2d.flatten()
    geo_points = np.vstack((xs_2d, ys_2d)).T

    grid = Path(perimeter).contains_points(geo_points)
    # np.flip(axis=0) to get [0,0] as top left point of raster
    grid = grid.reshape(cols, rows).T
    grid[([x for x, _  in perimeter], [y for _, y in perimeter])] = True
    if closing['close']:
        grid = binary_closing(grid, structure=closing['struct'])
    if flip:
        grid = np.flip(grid, 0)
    return  grid

# def bounding_box_ar(coords, nodataval=-9999):
#     def boundOneDimension(a):
#         n, m = a.shape
#         foundmin = False
#         foundmax = True
#         for i in range(n):
#             for j in range(m):
#                 if not foundmin and a[i, j] != nodataval:
#                     foundmin = True
#                     tl = i
#                 if a[i, j] != nodataval:
#                     foundmax = False
#             if foundmin and foundmax:
#                 lr = i
#                 break
#             else:
#                 foundmax = True
#         return tl, lr

#     # 1 connected component
#     coords = np.array(coords)
#     in_itl, in_ilr = boundOneDimension(coords)
#     in_jtl, in_jlr = boundOneDimension(coords.T)
#     return in_itl, in_jtl, in_ilr, in_jlr

def bounding_box_per(perimeter, rows):
    '''Returns the bounding box around the perimeter

    Arguments:

    * `perimeter`: List of perimeter points, needn't be in order

    * `rows`: number of rows in geographical array, needed because array contains
    top left spot at [0,0]'''
    in_itl = min([i for i, _ in perimeter])
    in_jtl = min([j for _, j in perimeter])
    in_ilr = max([i for i, _ in perimeter])
    in_jlr = max([j for _, j in perimeter])
    # because of np.flip in fillPolygon4Raster, xs must be reversed (rows - _)
    return rows - in_ilr - 1, in_jtl, rows - in_itl - 1, in_jlr

def bounding_box_pers(per_dict, rows):
    '''Returns the bounding box around the "actual" perimeter

    Arguments:

    * `perimeter`: Dict of lists of perimeter points, needn't be in order

    * `rows`: number of rows in geographical array, needed because array contains
    top left spot at [0,0]'''
    itl, jtl = np.Inf, np.Inf
    ilr, jlr = 0, 0
    for key in per_dict.keys():
        for per in per_dict[key]:
            for lat, lng in per:
                if lat < itl:
                    itl = lat
                if lat > ilr:
                    ilr = lat
                if lng < jtl:
                    jtl = lng
                if lng > jlr:
                    jlr = lng
    return rows - ilr - 1, jtl, rows - itl - 1, jlr

def padding(bbp, rows, cols, pad=3):
    '''Add padding to bounding box'''
    return max(bbp[0] - pad, 0), max(bbp[1] - pad, 0), \
        min(bbp[2] + pad, rows-1), min(bbp[3] + pad, cols-1)

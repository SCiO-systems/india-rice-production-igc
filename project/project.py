import osgeo, gdal
import helpers.aux as aux
import numpy as np
import matplotlib.pyplot as plt

geojson_fn = './data/IND.geo.json'
geojson = ''
with open(geojson_fn, 'r') as f:
    line = f.readline()
    while line:
        geojson += line[:-1] # remove trailing '\n'
        line = f.readline()

perimeter = osgeo.ogr.CreateGeometryFromJson(geojson)

rows, cols = 900, 2130
india = np.zeros((rows, cols))

indian_coords = osgeo.ogr.Geometry.GetPoints(
    osgeo.ogr.Geometry.GetGeometryRef(perimeter, 0)
)
indian_coords = aux.upsampleGeoJSON(indian_coords, 15)
india[aux.Coords2IndicesAr(indian_coords)] = 1



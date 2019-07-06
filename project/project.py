import osgeo, gdal
import helpers.aux as aux
import numpy as np
import matplotlib.pyplot as plt

geojson_fn = './data/IND.geo.json'
bio_fn = './data/bio_1.asc'

geojson = ''
with open(geojson_fn, 'r') as f:
    line = f.readline()
    while line:
        geojson += line[:-1] # remove trailing '\n'
        line = f.readline()

perimeter = osgeo.ogr.CreateGeometryFromJson(geojson)

rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(bio_fn)

indian_coords = osgeo.ogr.Geometry.GetPoints(
    osgeo.ogr.Geometry.GetGeometryRef(perimeter, 0)
)
indian_coords = aux.upsampleGeoJSON(indian_coords, 15)

perimeter = aux.Coords2IndicesAr(
    indian_coords, xllcorner=xllcorner, yllcorner=yllcorner, cellsize=cellsize
)

india = aux.fillPolygon4Raster(perimeter, rows, cols)

plt.imshow(india)
plt.show()


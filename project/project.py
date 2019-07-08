import osgeo, gdal, osr
import helpers.aux as aux
import numpy as np

geojson_fn = './data/IND.geo.json'
bio_fn = './data/tmax_1.asc'

geojson = ''
with open(geojson_fn, 'r') as f:
    line = f.readline()
    while line:
        geojson += line[:-1] # remove trailing '\n'
        line = f.readline()

perimeter = osgeo.ogr.CreateGeometryFromJson(geojson)

indian_coords = osgeo.ogr.Geometry.GetPoints(
    osgeo.ogr.Geometry.GetGeometryRef(perimeter, 0)
)
# upsample with heuristic rate 15 to fill gaps in array indices
indian_coords = aux.upsampleGeoJSON(indian_coords, rate=15)

# data array holds at [0,0] the top left point of the actual data
rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(bio_fn)

perimeter = aux.Coords2IndicesAr(
    indian_coords, xllcorner=xllcorner, yllcorner=yllcorner, cellsize=cellsize
)

# get "rough" polygon of india and set values outside of it to NODATA_value
india = aux.fillPolygon4Raster(perimeter, rows, cols)
data[np.invert(india)] = nodataval

# get bounding box of india for geotiff purposes
in_itl, in_jtl, in_ilr, in_jlr = aux.padding(
    aux.boundingBoxPer(perimeter, rows), rows, cols, pad=3
)


drv = gdal.GetDriverByName('GTiff')
ds = drv.Create('./results/test.tiff', in_jlr - in_jtl, in_ilr - in_itl, 1, gdal.GDT_Byte)
ds.SetGeoTransform((
    xllcorner + in_itl * cellsize, cellsize, 0, yllcorner + (rows - in_itl) * cellsize, 0, -cellsize
))

dst_srs = osr.SpatialReference()
# NOTE: attempt at setting crs to wgs84 (epsg 3857), to be verified
dst_srs.ImportFromEPSG(3857)
ds.SetProjection(dst_srs.ExportToWkt())
ds.GetRasterBand(1).WriteArray(data[in_itl:in_ilr, in_jtl:in_jlr])
ds.GetRasterBand(1).SetNoDataValue(nodataval)
ds.GetRasterBand(1).FlushCache()
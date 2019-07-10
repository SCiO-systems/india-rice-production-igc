import osgeo, gdal, osr
import helpers.aux as aux
import helpers.bands as bands
import numpy as np

geojson_fn = './data/IND.geo.json'


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

# dummy read to initialize other structures
rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(
    bands.BANDS[0]['path'].replace(bands.TEMPLATE, str(bands.BANDS[0]['range'][0]))
)

# get perimeter and cropping params
perimeterIndices = aux.Coords2IndicesAr(
    indian_coords, xllcorner=xllcorner, yllcorner=yllcorner, cellsize=cellsize
)
in_itl, in_jtl, in_ilr, in_jlr = aux.padding(
    aux.boundingBoxPer(perimeterIndices, rows), rows, cols, pad=3
)

# create empty tiff
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create('./results/india_cmip5_multiband.tiff', in_jlr - in_jtl, in_ilr - in_itl, bands.getNumberOfBands(), gdal.GDT_Byte)
ds.SetGeoTransform((
    xllcorner + in_itl * cellsize, cellsize, 0, yllcorner + (rows - in_itl) * cellsize, 0, -cellsize
))

bandcnt = 1
for band in bands.BANDS:
    for i in band['range']:
        print(bandcnt)
        # data array holds at [0,0] the top left point of the actual data
        rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(
            # if band['path'] does not contain TEMPLATE, nothing is replaced
            # and only one iteration is made
            band['path'].replace(bands.TEMPLATE, str(i))
        )

        perimeterIndices = aux.Coords2IndicesAr(
            indian_coords, xllcorner=xllcorner, yllcorner=yllcorner, cellsize=cellsize
        )

        # get "rough" polygon of india and set values outside of it to NODATA_value
        india = aux.fillPolygon4Raster(perimeterIndices, rows, cols)
        data[np.invert(india)] = nodataval

        ds.GetRasterBand(bandcnt).WriteArray(data[in_itl:in_ilr, in_jtl:in_jlr])
        ds.GetRasterBand(bandcnt).SetNoDataValue(nodataval)

        bandcnt += 1

dst_srs = osr.SpatialReference()
# setting crs to wgs84 (epsg 3857)
dst_srs.ImportFromEPSG(3857)
ds.SetProjection(dst_srs.ExportToWkt())
ds.GetRasterBand(bandcnt-1).FlushCache()

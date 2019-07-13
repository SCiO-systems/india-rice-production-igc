import osgeo, gdal, osr
import helpers.aux as aux
import numpy as np

class GeotiffBands:
    def __init__(self, band_desc, desc_template):
        try:
            band_desc[0]['path']
            for i in band_desc[0]['range']:
                band_desc[0]['path'].replace(desc_template, i)
            cnt = 0
            for band in band_desc:
                cnt += len(band['range'])
        except Exception:
            raise ValueError('Check project/helpers/bands.py for correct parameters example')

        self.bands = band_desc
        self.template = desc_template
        self.band_cnt = cnt
    
    def expand(self, band):
        # if band['path'] does not contain template, nothing is replaced
        # and only one iteration is made
        return [band['path'].replace(self.template, i) for i in band['range']]


    def createTiff(self, geojson_f, res_f, rate=15, pad=3, epsg=3857):
        geojson = ''
        with open(geojson_f, 'r') as f:
            line = f.readline()
            while line:
                geojson += line[:-1] # remove trailing '\n'
                line = f.readline()

        perimeter = osgeo.ogr.CreateGeometryFromJson(geojson)

        indian_coords = osgeo.ogr.Geometry.GetPoints(
            osgeo.ogr.Geometry.GetGeometryRef(perimeter, 0)
        )
        # upsample with heuristic rate 15 to fill gaps in array indices
        indian_coords = aux.upsampleGeoJSON(indian_coords, rate=rate)

        # dummy read to initialize other structures
        rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(
            self.expand(self.bands[0])[0]
        )

        # get perimeter and cropping params
        perimeterIndices = aux.Coords2IndicesAr(
            indian_coords, xllcorner=xllcorner, yllcorner=yllcorner, cellsize=cellsize
        )
        in_itl, in_jtl, in_ilr, in_jlr = aux.padding(
            aux.boundingBoxPer(perimeterIndices, rows), rows, cols, pad=pad
        )

        # create empty tiff
        drv = gdal.GetDriverByName('GTiff')
        ds = drv.Create(res_f, in_jlr - in_jtl, in_ilr - in_itl, self.band_cnt, gdal.GDT_Byte)
        ds.SetGeoTransform((
            xllcorner + in_jtl * cellsize, cellsize, 0, yllcorner + (rows - in_itl) * cellsize, 0, -cellsize
        ))

        bandcnt = 1
        for band in self.bands:
            ascfiles = self.expand(band)
            for ascfile in ascfiles:
                print(bandcnt)
                # data array holds at [0,0] the top left point of the actual data
                rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.ascRead(ascfile)

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
        dst_srs.ImportFromEPSG(epsg)
        ds.SetProjection(dst_srs.ExportToWkt())
        ds.GetRasterBand(bandcnt-1).FlushCache()

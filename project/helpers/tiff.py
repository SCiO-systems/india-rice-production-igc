'''Contains auxiliary class for asc files to GeoTIFF and edit GeoTIFF function'''

import osgeo
import gdal
import osr
import pyproj
import numpy as np

from project.helpers import aux

def epsg_trans(points, epsg_in=4326, epsg_out=4326):
    '''Coord transform from `epsg_in` to `epsg_out`.

    Arguments:

    `points`: list of iterables where [0]=lng, [1]=lat

    `epsg_in`: epsg of input points

    `epsg_out`: epsg of output points'''
    pin = pyproj.Proj(init=f'epsg:{epsg_in}')
    pout = pyproj.Proj(init=f'epsg:{epsg_out}')

    return [pyproj.transform(pin, pout, lng, lat) for lng, lat in points]

class GeotiffBands:
    '''GeotiffBands is an auxiliary class, created for convenience.
    It holds a list of specially structured dictionaries (see project/preliminary/helpers/bands.py),
    `bands`, and its template, `template`, and utilizes it to create a multiband GeoTIFF.
    '''
    def __init__(self, band_desc, desc_template):
        '''Arguments:

        * `band_desc`: List of specially structured dictionaries, holds concentrated information
        for .asc to be parsed
        * `desc_template`: Template that `band_desc` uses to condense information
        '''
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
        '''Expands a dictionary/band to all its real .asc files

        Arguments:

        * `band`: Specially structured dictionary
        '''

        # if band['path'] does not contain template, nothing is replaced
        # and only one iteration is made
        return [band['path'].replace(self.template, i) for i in band['range']]


    def create_tiff(self, geojson_f, tiff_f, rate=15, pad=3, epsg=4326):
        '''Creates (multiband) GeoTIFF based on its atttributes' information

        Arguments:

        * `geojson_f`: Filename of geojson file that defines areas (rough) perimeter

        * `tiff_f`: Resulting TIFF's filename

        * `rate`: Rate at which to upsample geojson as to create a closed polygon

        * `pad`: Padding in pixels around the region of interest, for display purposes.

        * `epsg`: Coordinates system to be used by the resulting GeoTIFF
        '''
        geojson = ''
        with open(geojson_f, 'r') as fdc:
            line = fdc.readline()
            while line:
                geojson += line[:-1] # remove trailing '\n'
                line = fdc.readline()

        perimeter = osgeo.ogr.CreateGeometryFromJson(geojson)

        indian_coords = osgeo.ogr.Geometry.GetPoints(
            osgeo.ogr.Geometry.GetGeometryRef(perimeter, 0)
        )
        # upsample with heuristic rate 15 to fill gaps in array indices
        indian_coords = aux.upsample_geojson(indian_coords, rate=rate)

        # dummy read to initialize other structures
        rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.asc_read(
            self.expand(self.bands[0])[0]
        )

        # get perimeter and cropping params
        perimeter_indices = aux.coords2indices_ar(
            indian_coords, xllcorner=xllcorner, yllcorner=yllcorner,
            xcellsize=cellsize, ycellsize=cellsize
        )
        in_itl, in_jtl, in_ilr, in_jlr = aux.padding(
            aux.bounding_box_per(perimeter_indices, rows), rows, cols, pad=pad
        )

        # create empty tiff
        drv = gdal.GetDriverByName('GTiff')
        dst = drv.Create(tiff_f, in_jlr - in_jtl + 1, in_ilr - in_itl + 1, self.band_cnt, gdal.GDT_Int16)

        # get proper epsg 3857 coords and cells
        xtlcorner = xllcorner + in_jtl * cellsize
        ytlcorner = yllcorner + (rows - in_itl) * cellsize

        [(xlrcorner, ylrcorner)] = epsg_trans([
            (xtlcorner + (in_jlr - in_jtl) * cellsize, ytlcorner - (in_ilr - in_itl) * cellsize)
        ])

        [(xtlcorner, ytlcorner)] = epsg_trans([(xtlcorner, ytlcorner)])

        xcellsize = abs(xtlcorner - xlrcorner) / (in_jlr - in_jtl)
        ycellsize = abs(ytlcorner - ylrcorner) / (in_ilr - in_itl)

        dst.SetGeoTransform((
            xtlcorner, xcellsize, 0,
            ytlcorner, 0, -ycellsize
        ))

        bandcnt = 1
        for band in self.bands:
            ascfiles = self.expand(band)
            for ascfile in ascfiles:
                print(bandcnt)
                # data array holds at [0,0] the top left point of the actual data
                rows, cols, xllcorner, yllcorner, cellsize, nodataval, data = aux.asc_read(ascfile)

                perimeter_indices = aux.coords2indices_ar(
                    indian_coords, xllcorner=xllcorner, yllcorner=yllcorner,
                    xcellsize=cellsize, ycellsize=cellsize
                )

                # get "rough" polygon of india and set values outside of it to NODATA_value
                india = aux.fill_polygon_for_raster(perimeter_indices, rows, cols)

                # crop
                india = india[in_itl:in_ilr+1, in_jtl:in_jlr+1]
                data = data[in_itl:in_ilr+1, in_jtl:in_jlr+1]
                data[np.invert(india)] = nodataval

                dst.GetRasterBand(bandcnt).WriteArray(data)
                dst.GetRasterBand(bandcnt).SetNoDataValue(nodataval)

                bandcnt += 1

        dst_srs = osr.SpatialReference()
        # setting crs to wgs84 (epsg 3857)
        dst_srs.ImportFromEPSG(epsg)
        dst.SetProjection(dst_srs.ExportToWkt())
        dst.FlushCache()


def edit_tiff(tiff_f, man_fun=(lambda x, y, z, w, v, u: x)):
    '''Appends bands to GeoTIFF.

    Arguments:

    * `tiff_f`: GeoTIFF filename

    * `man_fun`: Manipulating function. Has 6 (non-keyword) ordered arguments:

    `data_array`: the bands of the GeoTIFF as read, in the form of numpy array,

    `xtl`: top left x coordinate / longitude, `xcellsize`: cell resolution - longitude,

    `ytl`: top left y coordinate / latitude, `ycellsize`: cell resolution - latitude,

    `nodataval`: no data value, should be the same for every band.
    Should return the resulting bands in numpy array form
    (semantically, it should append new bands)
    '''
    dataset = gdal.Open(tiff_f, gdal.GA_ReadOnly)
    nrows, ncols = np.shape(dataset.GetRasterBand(1).ReadAsArray())
    data = np.zeros((nrows, ncols, dataset.RasterCount), dtype=float)
    nodataval = None

    for band in range(dataset.RasterCount):
        data[..., band] = dataset.GetRasterBand(band+1).ReadAsArray()
        if nodataval and \
             dataset.GetRasterBand(band+1).GetNoDataValue() != nodataval:
            raise ValueError('NODATA_value not equal between bands')
        nodataval = dataset.GetRasterBand(band+1).GetNoDataValue()

    xtl, xcellsize, dummy_xskew, ytl, dummy_yskew, ycellsize = dataset.GetGeoTransform()
    man_data = man_fun(data, xtl, xcellsize, ytl, -ycellsize, nodataval)

    ncols, nrows, bands = man_data.shape

    driver = gdal.GetDriverByName('GTiff')
    outdata = driver.Create(tiff_f, nrows, ncols, bands, gdal.GDT_Int16)
    outdata.SetGeoTransform(dataset.GetGeoTransform())
    outdata.SetProjection(dataset.GetProjection())
    for band in range(bands):
        print(band+1)
        outdata.GetRasterBand(band+1).WriteArray(man_data[..., band])
        outdata.GetRasterBand(band+1).SetNoDataValue(nodataval)
    outdata.FlushCache()

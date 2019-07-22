'''Create GeoTIFF with every data point our machine learning
model will need'''

import gdal
import numpy as np
import matplotlib.pyplot as plt

import project.helpers.aux as aux
import project.helpers.read_gov_in as gov_in
import project.helpers.read_nc as nc
from project.helpers.state_correspondence import GOV2GEO

def main():
    '''Main'''
    lai_f = './data/Copernicus/c_gls_LAI300_201405100000_GLOBE_PROBAV_V1.0.1.nc'
    ndvi_f = './data/Copernicus/c_gls_NDVI300_201401010000_GLOBE_PROBAV_V1.0.1.nc'
    rice_tifs = [
        './data/RiceGeotiffs/31360_spam2000v3r7_global_p_ta_rice_a.tif',
        './data/RiceGeotiffs/31360_spam2005v3r2_global_p_ta_rice_a.tif',
        './data/RiceGeotiffs/31360_spam2010v1r0_global_p_ta_rice_a.tif',
    ]
    geojson_f = './data/states.in.geo.json'
    temp_fs = [
        './data/data.gov.in/annual-seasonal-max-temp.in.json',
        './data/data.gov.in/annual-seasonal-mean-temp.in.json',
        './data/data.gov.in/annual-seasonal-min-temp.in.json',
    ]
    storms_f = './data/data.gov.in/annual-seasonal-monthly-cyclonic-storms.in.json'
    rain_f = './data/data.gov.in/monthly-rainfall.in.json'

    # model: last crop and weather thereafter, crops in 2000, 2005, 2010
    years = [i for i in range(2001, 2011)]
    data_label = 'ANNUAL'
    nodataval = -9999


    perimeters_coords = gov_in.get_perimeters_from_geojson(geojson_f) # X
    temp_measur = [
        gov_in.get_temporal_measurement(f, years, data_labels=[data_label]) for f in temp_fs
    ]
    storm_measur = gov_in.get_temporal_measurement(
        storms_f, years, data_labels=[data_label], nodataval=nodataval
    )
    rain_measur = gov_in.get_state_rainfall(
        rain_f, years, data_labels=[data_label], nodataval=nodataval
    )
    lai_ds = nc.NetCDFDataset(lai_f, 'LAI')
    ndvi_ds = nc.NetCDFDataset(ndvi_f, 'NDVI')

    # read to initialize array
    # 2005 tif has fewer longitude samples, same cellsize
    # -> points correspond to same map point
    struct_tif = gdal.Open(rice_tifs[1], gdal.GA_ReadOnly)
    nrows, ncols = np.shape(struct_tif.GetRasterBand(1).ReadAsArray())
    nbands = 1 + 1 + 3 + 3 * len(years) + 1 * len(years) + 1 * len(years)

    xtl, xcellsize, dummy_xskew, ytl, dummy_yskew, ycellsize = struct_tif.GetGeoTransform()

    states = {}
    for state in perimeters_coords:
        for per in perimeters_coords[state]:
            states.setdefault(state, []).append(
                list(set(aux.coords2indices_ar(
                    per, xcellsize=xcellsize, ycellsize=-ycellsize,
                    xllcorner=xtl, yllcorner=ytl+ycellsize*nrows
                )))
            )


    itl, jtl, ilr, jlr = aux.bounding_box_pers(states, nrows)

    for state in states:
        for per in range(len(states[state])):
            states[state][per] = [((nrows - i - 1) - itl, j - jtl) for i, j in states[state][per]]

    # for state in states.keys():
    #     all_per = []
    #     for per in states[state]:
    #         all_per.extend(per)

    #     a = np.zeros((ilr-itl+1, jlr-jtl+1))
    #     a[([x for x,_ in all_per], [y for _,y in all_per])] = 1
    #     plt.imshow(a)
    #     plt.show()

    filled_states = {}
    india = np.zeros((ilr-itl+1, jlr-jtl+1)).astype(bool)
    # india = np.zeros((nrows, ncols))

    for state in states:
        print(state)
        for per in states[state]:
            filled_states.setdefault(state, []).append(
                aux.fill_polygon_for_raster(
                    # per, rows=nrows, cols=ncols
                    per, rows=ilr-itl+1, cols=jlr-jtl+1,
                    flip=False, closing={'close': True, 'struct': np.ones((4, 4))}
                )
            )
            plt.show()
            india[filled_states[state][-1]] = 1

    # print(india)
    # plt.imshow(india)
    # plt.show()

    feature_dataset = np.zeros((ilr-itl+1, jlr-jtl+1, nbands), dtype=float)

    last_band = 0 # keep record of bands filled

    # inorder commit

    for band in range(last_band, len(rice_tifs)):
        tif = gdal.Open(rice_tifs[band], gdal.GA_ReadOnly)
        feature_dataset[..., band] = tif.GetRasterBand(1).ReadAsArray()[itl:ilr+1, jtl:jlr+1]
        # no data value of geotiffs was -1, change cause of probable conflict with temp
        prev_nodataval = tif.GetRasterBand(1).GetNoDataValue()
        feature_dataset[feature_dataset[..., band] == prev_nodataval, band] = nodataval
        last_band += 1


    for nc_ds in [lai_ds, ndvi_ds]:
        print(nc_ds.feature)
        for lat_ind in range(ilr-itl+1):
            print(lat_ind)
            for lng_ind in range(jlr-jtl+1):
                lat = ytl + (itl + lat_ind) * ycellsize
                lng = xtl + (jtl + lng_ind) * xcellsize
                feature_dataset[lat_ind, lng_ind, last_band] = \
                    nc_ds.get(lng, lat, nodataval=nodataval)
        last_band += 1

    for year in years:
        for temp in temp_measur:
            feature_dataset[india, last_band] = temp[year][data_label]
            last_band += 1

        feature_dataset[india, last_band] = storm_measur[year][data_label]
        last_band += 1

        for state in rain_measur:
            for geo_state in GOV2GEO[state]:
                for in_comp in filled_states[geo_state]:
                    feature_dataset[in_comp, last_band] = rain_measur[state][year][data_label]
        last_band += 1

    # # Dataset Structure
    #
    # Inorder:
    # * 2000, 2005, 2010 crop production
    # * LAI, NDVI (year 2014)
    # * By year (ascending, from 2000 to 2010):
    #   * max temperature
    #   * mean temperature
    #   * min temperature
    #   * storms
    #   * rainfall by state
    #
    # Total number of bands: 60
    if last_band != nbands:
        raise ValueError('Variable `last_band` not equal to number of bands')

    # NODATA val to unnecessary or unknown values
    feature_dataset[np.invert(india)] = nodataval

    driver = gdal.GetDriverByName('GTiff')
    feature_tiff = driver.Create(
        './results/rice_feature_dataset.tiff', jlr-jtl+1, ilr-itl+1, nbands, gdal.GDT_Int16
    )
    feature_tiff.SetGeoTransform((
        xtl + jtl * xcellsize, xcellsize, 0,
        ytl + itl * ycellsize, 0, ycellsize
    ))
    feature_tiff.SetProjection(struct_tif.GetProjection())
    for band in range(1, nbands+1):
        print(band)
        feature_tiff.GetRasterBand(band).WriteArray(feature_dataset[..., band-1])
        feature_tiff.GetRasterBand(band).SetNoDataValue(nodataval)
    feature_tiff.FlushCache()

if __name__ == '__main__':
    main()

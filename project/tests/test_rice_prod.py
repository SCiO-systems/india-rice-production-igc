'''Test rice goetiffs'''

import gdal

def main():
    '''Main'''
    rice_tifs = [
        './data/RiceGeotiffs/31360_spam2000v3r7_global_p_ta_rice_a.tif',
        './data/RiceGeotiffs/31360_spam2005v3r2_global_p_ta_rice_a.tif',
        './data/RiceGeotiffs/31360_spam2010v1r0_global_p_ta_rice_a.tif',
    ]

    for tif in rice_tifs:
        tif = gdal.Open(tif)
        xtl, xres, _, ytl, _, yres = tif.GetGeoTransform()
        print(xtl, xres, ytl, yres)
        print(xtl + xres * 4330, ytl + yres * 2150)

if __name__ == '__main__':
    main()


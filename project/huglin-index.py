import helpers.tiff as tiff
from helpers.bands import dirname
import numpy as np

template = '#'
bands = [
    {'path': f'{dirname("tmax")}/tmax_{template}.asc', 'range': [str(i) for i in range(4,10)], 'desc': 'monthly_maximum_temperature'},
    {'path': f'{dirname("tmean")}/tmean_{template}.asc', 'range': [str(i) for i in range(4,10)], 'desc': 'monthly_maximum_temperature'},    
]

my_bands = tiff.GeotiffBands(bands, template)
my_bands.createTiff('./data/IND.geo.json', './results/india_cmip5_huglin.tiff')

def huglin_index(data, xtl, ytl, cellsize, nodataval):
    def lat2index(lat):
        if lat % 2 == 0:
            lat -= 1
        return int(lat/2)-1

    # inferred values of K based on values presented at
    # https://steemit.com/gdd/@fruitionsciences/bioclimatic-indices-of-the-ripening-period-1-the-huglin-index
    k = [0.83 + i * 0.01 for i in range(45)]

    # days per month from Apr to Sep
    days_per_month = [30, 31, 30, 31, 31, 30]
    months = 6

    n, m, bands = data.shape

    HI_band = np.zeros((n,m))
    for y in range(n):
        lat = ytl - y * cellsize
        ki = lat2index(lat)
        for x in range(m):
            if data[y,x,0] != nodataval:
                for mth in range(bands):
                    HI_band[y,x] += data[y,x,mth] * days_per_month[mth % months] / 2 - 10 * days_per_month[mth % months]
                HI_band[y,x] *= k[ki]
            else:
                HI_band[y,x] = nodataval

    return np.dstack((data, HI_band))



tiff.editGeotiff('./results/india_cmip5_huglin.tiff', man_fun=huglin_index)
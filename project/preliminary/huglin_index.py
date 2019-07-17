'''Produces GeoTIFF with necessary temperature bands and a Huglin Index one'''

import numpy as np

from project.helpers import tiff
from project.helpers import bands

# include only from april to september
TEMPLATE = '#'
BANDS = [
    {
        'path': f'{bands.dirname("tmax")}/tmax_{TEMPLATE}.asc',
        'range': [str(i) for i in range(4, 10)],
        'desc': 'monthly_maximum_temperature'
    },
    {
        'path': f'{bands.dirname("tmean")}/tmean_{TEMPLATE}.asc',
        'range': [str(i) for i in range(4, 10)],
        'desc': 'monthly_maximum_temperature'
    },
]

HUGLIN_BANDS = tiff.GeotiffBands(BANDS, TEMPLATE)
HUGLIN_BANDS.create_tiff('./data/IND.geo.json', './results/india_cmip5_huglin.tiff')

def huglin_index(data, dummy_xtl, ytl, cellsize, nodataval):
    '''Computes Huglin Index and append it to `data`'''
    def lat2index(lat):
        '''Latitude to Huglin Index's K index'''
        if lat % 2 == 0:
            lat -= 1
        return int(lat/2)-1

    # inferred values of K based on values presented at
    # https://steemit.com/gdd/@fruitionsciences/bioclimatic-indices-of-the-ripening-period-1-the-huglin-index
    k = [0.83 + i * 0.01 for i in range(45)]

    # days per month from Apr to Sep
    days_per_month = [30, 31, 30, 31, 31, 30]
    months = 6

    huglin_band = np.zeros(data.shape[:2])
    for lat_ind in range(data.shape[0]):
        lat = ytl - lat_ind * cellsize
        k_ar_ind = lat2index(lat)
        for lng_ind in range(data.shape[1]):
            if data[lat_ind, lng_ind, 0] != nodataval:
                for mth in range(data.shape[2]):
                    huglin_band[lat_ind, lng_ind] += \
                        data[lat_ind, lng_ind, mth] * days_per_month[mth % months] / 2 - \
                        10 * days_per_month[mth % months]
                huglin_band[lat_ind, lng_ind] *= k[k_ar_ind]
            else:
                huglin_band[lat_ind, lng_ind] = nodataval

    return np.dstack((data, huglin_band))



tiff.edit_tiff('./india_cmip5_huglin.tiff', man_fun=huglin_index)

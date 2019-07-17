'''Creates multiband GeoTIFF from CMIP5 dataset'''

from project.helpers import bands
from project.helpers import tiff

MY_BANDS = tiff.GeotiffBands(bands.BANDS, bands.TEMPLATE)

MY_BANDS.create_tiff('./data/IND.geo.json', './results/india_cmip5_multiband.tiff')

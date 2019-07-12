import helpers.bands as bands
import helpers.tiff as tiff

my_bands = tiff.GeotiffBands(bands.BANDS, bands.TEMPLATE)

my_bands.createTiff('./data/IND.geo.json', './results/india_cmip5_multiband.tiff')
'''Creates multiband GeoTIFF from CMIP5 dataset'''

from project.helpers import bands
from project.helpers import tiff

def main():
    '''Main'''
    my_bands = tiff.GeotiffBands(bands.BANDS, bands.TEMPLATE)

    my_bands.create_tiff('./data/IND.geo.json', './results/india_cmip5_multiband.tiff')

if __name__ == '__main__':
    main()

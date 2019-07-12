import helpers.tiff as tiff
from helpers.bands import dirname

template = '#'
bands = [
    {'path': f'{dirname("tmax")}/tmax_{template}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'monthly_maximum_temperature'},
    {'path': f'{dirname("tmean")}/tmean_{template}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'monthly_maximum_temperature'},    
]

my_bands = tiff.GeotiffBands(bands, template)
my_bands.createTiff('./data/IND.geo.json', './results/india_cmip5_huglin.tiff')
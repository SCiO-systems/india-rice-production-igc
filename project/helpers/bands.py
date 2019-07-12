def dirname(measurement):
    _dirname_prefix = 'bcc_csm1_1_m_rcp8_5_2080s'
    _dirname_postfix = '10min_r1i1p1_no_tile_asc'
    _dirname_global = './data/CMIP5'

    return f'{_dirname_global}/{_dirname_prefix}_{measurement}_{_dirname_postfix}'

def getNumberOfBands():
    cnt = 0
    for band in BANDS:
        cnt += len(band['range'])
    return cnt

TEMPLATE = '#'

BANDS = [
    # `range`: parameters to substitute template with
    # len(`range`) == 1 if no template was required, dummy str
    {'path': f'{dirname("cons")}/cons_mths.asc', 'range': ['-999'], 'desc': 'consecutive_dry_months'},
    {'path': f'{dirname("prec")}/prec_{TEMPLATE}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'precipitation'},
    {'path': f'{dirname("tmax")}/tmax_{TEMPLATE}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'maximum_monthly_temperature'},
    {'path': f'{dirname("tmean")}/tmean_{TEMPLATE}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'mean_monthly_temperature'},
    {'path': f'{dirname("tmin")}/tmin_{TEMPLATE}.asc', 'range': [str(i) for i in range(1,13)], 'desc': 'min_monthly_temperature'}
]
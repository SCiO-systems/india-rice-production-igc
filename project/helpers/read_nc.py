'''Read from .nc files and their returning structures'''
# NOTE: netCDF4.Dataset is immutable -> No significant delay
#       when used as function parameter

# >>> ds = nc.Dataset('data/Copernicus/c_gls_LAI300_201405100000_GLOBE_PROBAV_V1.0.1.nc')
# >>> ds.dimensions.keys()
# odict_keys(['lon', 'lat'])
# >>> ds.dimensions['lon']
# <class 'netCDF4._netCDF4.Dimension'>: name = 'lon', size = 120960
#
# >>> ds.dimensions['lat']
# <class 'netCDF4._netCDF4.Dimension'>: name = 'lat', size = 47040
#
# >>> ds.variables.keys()
# odict_keys(['lon', 'lat', 'crs', 'LAI', 'LENGTH_AFTER', 'LENGTH_BEFORE', 'NOBS', 'QFLAG', 'RMSE'])
# >>> ds.variables['lon'][2]
# masked_array(data=-179.99404762,
#              mask=False,
#        fill_value=1e+20)
# >>> type(ds.variables['lat'][ds.dimensions['lat'].size-1].data)
# <class 'numpy.ndarray'>
# >>> ds.variables['lat'][0]
# masked_array(data=80.,
#              mask=False,
#        fill_value=1e+20)
# >>> ds.variables['lat'][0].data.item(0)
# 80.0
# >>> ds.variables['LAI'][0,0]
# masked
# >>> type(ds.variables['LAI'][0,0])
# <class 'numpy.ma.core.MaskedConstant'>
# >>> ds.variables['LAI'][3000,70000]
# 1.399986

import netCDF4

class NetCDFDataset:
    '''Proxy to properly parse data from netCFD4 Dataset
    without using netCDF4 syntax'''
    def __init__(self, filename, _feature):
        self.dataset = netCDF4.Dataset(filename)
        self.feature = _feature

    def get_index(self, geo_var, geo_val):
        '''Return index where 'geo_var' ~= geo_val.
        Assumes equal spacing (verified for small sample)'''
        # #samples of geographical coordinate
        size = self.dataset.dimensions[geo_var].size
        # find range
        first_val = self.dataset.variables[geo_var][0].data.item(0)
        last_val = self.dataset.variables[geo_var][size-1].data.item(0)
        # return index as percentage times size (-1 for index)
        return round((first_val - geo_val) / (first_val - last_val) * (size-1))

    def item(self, lng_index, lat_index, nodataval=None):
        '''Get data point at indices `lng_index`,`lat_index`'''
        val = self.dataset.variables[self.feature][lat_index, lng_index]
        # val could be numpy.ma.core.MaskedConstant, return nodataval for convenience
        return val if val else nodataval

    def get(self, lng, lat, nodataval=None):
        '''Get data point closest to (lng, lat) coords'''
        return self.item(
            self.get_index('lon', lng), self.get_index('lat', lat),
            nodataval=nodataval
        )

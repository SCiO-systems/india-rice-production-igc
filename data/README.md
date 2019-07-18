# Data Sources / Acknowledgements

* `CMIP5/` : [WDC Climate](https://cera-www.dkrz.de/WDCC/ui/cerasearch/q?hierarchy_steps_ss=CCAFS-CMIP5_Downscales&page=0&query=%2A%3A%2A)
* `data.gov.in/` : [India's Ministry Department of Earth Sciences](https://data.gov.in/catalogs/ministry_department/ministry-earth-sciences#path=asset_jurisdiction/all-india-2866/ministry_department/ministry-earth-sciences)
* `RiceGeotiffs/` : [MapSpam](http://mapspam.info/)
* `state.in.geo.json` : [Subhash9325](https://github.com/Subhash9325/GeoJson-Data-of-Indian-States)
* `Copernicus/` (not commited due to size): [Copernicus Global Land Service](https://land.copernicus.eu/global/products/lai). To properly execute certain files, you wills need to download 1. [c_gls_LAI300_201405100000_GLOBE_PROBAV_V1.0.1.nc](https://land.copernicus.vgt.vito.be/PDF/portal/Application.html#Browse;Root=512260;Collection=1000062;DoSearch=true;Time=NORMAL,NORMAL,1,JANUARY,2014,18,JULY,2019;ROI=61.05307547099,2.05323433762,96.82455984599,39.23096871262) and 2. [c_gls_NDVI300_201401010000_GLOBE_PROBAV_V1.0.1.nc](https://land.copernicus.vgt.vito.be/PDF/portal/Application.html#Browse;Root=513186;Collection=1000063;DoSearch=true;Time=NORMAL,NORMAL,1,JANUARY,2014,18,JULY,2019;ROI=61.05307547099,2.05323433762,96.82455984599,39.23096871262). These must be stored in `./Copernicus` or else the source code must to be modified.

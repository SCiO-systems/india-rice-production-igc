'''Test parsing geojson and then parsing to simple (not multi) polygons'''

# import gdal
# import osr
import osgeo.ogr

def main():
    '''Parses geojsons, created dict with keys = 'NAME_1'
    and creates perimeters'''

    geojson = {}
    with open('./data/states.in.geo.json', 'r') as fdc:
        line = fdc.readline()
        while line:
            # get only
            # ... "geometry": { ... } ...
            #                 |<--->|
            roi_ind = line.find('geometry')
            if roi_ind != -1:
                roi_bgn = line.find(':', roi_ind) + 1
                roi_end = line.rfind('}')

                key_ind = line.find('NAME_1')
                key_bgn = line.find('"', key_ind + len('NAME_1":')) + 1
                key_end = line.find('"', key_bgn)

                geojson[line[key_bgn:key_end]] = line[roi_bgn:roi_end].strip()
            line = fdc.readline()

    perimeters = {key: osgeo.ogr.CreateGeometryFromJson(geo) for key, geo in geojson.items()}
    # for p in perimeters:
    #     print(p.GetGeometryName())

    perimeters_coords = {}
    for key in perimeters.keys():
        if perimeters[key].GetGeometryName() == 'MULTIPOLYGON':
            for polygon in perimeters[key]:
                print(polygon.GetGeometryName())
                perimeters_coords.setdefault(key, []).append(
                    osgeo.ogr.Geometry.GetPoints(
                        osgeo.ogr.Geometry.GetGeometryRef(polygon, 0)
                    )
                )
        else: ## POLYGON itself
            print(perimeters[key].GetGeometryName())
            perimeters_coords[key] = [osgeo.ogr.Geometry.GetPoints(
                osgeo.ogr.Geometry.GetGeometryRef(perimeters[key], 0)
            )]

    for key in perimeters_coords:
        print(key+':')
        for per in perimeters_coords[key]:
            for pol in per:
                print(pol)

if __name__ == '__main__':
    main()

'''Parse data from data.gov.in dataset'''

import json
import osgeo.ogr

def get_columns(fields, data_labels, date_label='YEAR',
                subdivision=False, state_label='SUBDIVISION'):
    '''Get index of date_label, data_labels
    and optionally subdivision's name'''
    def to_col(col_id):
        '''json id to python list "column" index'''
        return ord(col_id) - ord('a')

    # keep keys from data_labels to distinguish
    # between different measurements
    data_cols = {}
    date_col = None
    state_col = None
    for lbldict in fields:
        if lbldict['label'] == date_label:
            date_col = to_col(lbldict['id'])
        elif lbldict['label'] in data_labels:
            data_cols[lbldict['label']] = to_col(lbldict['id'])
        elif subdivision and lbldict['label'] == state_label:
            state_col = to_col(lbldict['id'])

    if subdivision:
        return data_cols, date_col, state_col
    else:
        return data_cols, date_col

def get_temporal_measurement(filename, years, data_labels=['ANNUAL'], nodataval=None):
    '''Returns temperature or number of storms from dataset 
    in a dicitonary of dictionaries with key, value pairs s.t.
    key: year(int), value: dictionary with key, pair values s.t.
    key: data_label from `data_labels`, value: measurement(float)

    Arguments:

    * `filename`: filename from data.gov.in dataset, must be full path
    from root of project.

    * `years`: int list, years of measurements.

    * `data_labels`: labels of data to be returned from dataset.
    Non-existent labels are ignored.'''
    # if len(set(data_labels)) != len(data_labels):
    #     raise ValueError
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        # temporal -> label = 'YEAR'

        data_cols, date_col = get_columns(data['fields'], data_labels)

        # get measurements in a list of dictionaries
        temporal_measurement = {}
        for data_row in data['data']:
            year = int(data_row[date_col])
            if year in years:
                for key, data_col in data_cols.items():
                    try:
                        temporal_measurement.setdefault(year, {})[key] = float(data_row[data_col])
                    except ValueError: # NA
                        temporal_measurement.setdefault(year, {})[key] = nodataval
    return temporal_measurement

def get_state_rainfall(filename, years, data_labels=['ANNUAL'], nodataval=None):
    '''Returns rainfall (default: annual) for every state in India
    in the form of dictionary of dictionaries of dictionaries.
    Dictionary structure:

    {
        state1 (str) : {
            year1 (int) : {
                data_label1 (str): measurement (float) | None,
                data_label2 (str): ...
            },
            year2 (int) : {...}
        },
        state2 (str) : {...}
    }

    Arguments:

    * `filename`: full path from root of project to (rainfall) dataset.

    * `years`: int list, years of measurements.

    * `data_labels`: labels of data to be returned from dataset.
    Non-existent labels are ignored.'''

    with open(filename, 'r') as json_file:
        data = json.load(json_file)

        data_cols, date_col, state_col = get_columns(data['fields'], data_labels, subdivision=True)

        state_measurements = {}
        for data_row in data['data']:
            if data_row[date_col] in years or data_row[date_col] in map(str, years):
                year = int(data_row[date_col])
                for key, data_col in data_cols.items():
                    try:
                        state_measurements.setdefault(data_row[state_col], {})\
                            .setdefault(year, {})[key] = float(data_row[data_col])
                    except ValueError: # 'NA'
                        state_measurements.setdefault(data_row[state_col], {})\
                            .setdefault(year, {})[key] = nodataval

        return state_measurements

def get_perimeters_from_geojson(filename):
    '''Returns a dictionary of key: value pairs s.t.
    key: NAME_1 of state, value: list of perimeters,
    i.e. (longitude, latitude) lists (one or more)

    Arguments:

    * `filename`: Path from root of project to geojson
    '''
    # dictionary to preserve NAME_1 attribute (state)
    geojson = {}
    with open(filename, 'r') as fdc:
        line = fdc.readline()
        while line:
            # get only
            # ... "geometry": { ... } ...
            #                 |<--->|
            roi_ind = line.find('geometry')

            # file holds whole geometry in one line
            # the uses one "empty" line to seperate geometries
            if roi_ind != -1:
                roi_bgn = line.find(':', roi_ind) + 1
                roi_end = line.rfind('}')

                key_ind = line.find('NAME_1')
                key_bgn = line.find('"', key_ind + len('NAME_1":')) + 1
                key_end = line.find('"', key_bgn)

                geojson[line[key_bgn:key_end]] = line[roi_bgn:roi_end].strip()
            line = fdc.readline()

    # get POLYGONs and MULTIPOLYGONs of each state
    perimeters = {key: osgeo.ogr.CreateGeometryFromJson(geo) for key, geo in geojson.items()}

    perimeters_coords = {}
    for key in perimeters.keys():
        # if MULTIPOLYGON -> iterable of POLYGONs
        if perimeters[key].GetGeometryName() == 'MULTIPOLYGON':
            for polygon in perimeters[key]:
                perimeters_coords.setdefault(key, []).append(
                    osgeo.ogr.Geometry.GetPoints(
                        osgeo.ogr.Geometry.GetGeometryRef(polygon, 0)
                    )
                )
        else: # POLYGON itself
            perimeters_coords[key] = [osgeo.ogr.Geometry.GetPoints(
                osgeo.ogr.Geometry.GetGeometryRef(perimeters[key], 0)
            )]

    return perimeters_coords

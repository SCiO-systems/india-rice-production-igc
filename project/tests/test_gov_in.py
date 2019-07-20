'''Test parsing of annual temperatures/storms
from data.gon.in datasets'''

import json
from pprint import pprint
from project.helpers.read_gov_in import get_state_rainfall

def main():
    '''Main'''
    with open('./data/data.gov.in/annual-seasonal-min-temp.in.json', 'r') as json_file:
        data = json.load(json_file)
        years = [i for i in range(2000, 2011)]
        date_label = 'YEAR'
        data_label = ['SUBDIVISION', 'ANNUAL', 'balderdash']
        data_cols = {}
        for lbld in data['fields']:
            if lbld['label'] == date_label:
                date_col = ord(lbld['id']) - ord('a')
            elif lbld['label'] in data_label:
                data_cols[lbld['label']] = (ord(lbld['id']) - ord('a'))

        temporal_measurement = {}
        for data_row in data['data']:
            if data_row[date_col] in years or data_row[date_col] in map(str, years):
                year = int(data_row[date_col])
                for lbl, data_col in data_cols.items():
                    temporal_measurement.setdefault(year, {})[lbl] = float(data_row[data_col])

    return temporal_measurement


if __name__ == '__main__':

    RAIN = get_state_rainfall(
        './data/data.gov.in/monthly-rainfall.in.json', [i for i in range(2000, 2011)]
    )
    for key in RAIN:
        print(RAIN[key].keys())
    pprint(main())

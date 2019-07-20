'''Test parsing of rainfall data'''

import json
from pprint import pprint

from project.helpers.read_gov_in import get_columns

def main():
    '''Main'''
    with open('./data/data.gov.in/monthly-rainfall.in.json') as json_file:
        data = json.load(json_file)

        data_labels = ['ANNUAL',]
        years = [year for year in range(2000, 2011)]

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
                            .setdefault(year, {})[key] = None

        return state_measurements

if __name__ == '__main__':
    pprint(main())

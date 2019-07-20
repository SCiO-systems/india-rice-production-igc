'''This file holds, for every subdivision of data.gov.in dataset,
the corresponding NAME_1 values from the geojson, in a dictionary of lists
and vice versa'''

GOV2GEO = {
    'Andaman & Nicobar Islands': ['Andaman and Nicobar'],
    'Arunachal Pradesh': ['Arunachal Pradesh'],
    'Assam & Meghalaya': ['Assam', 'Meghalaya'],
    'Bihar': ['Bihar'],
    'Chhattisgarh': ['Chhattisgarh'],
    'Coastal Andhra Pradesh': ['Andhra Pradesh'],
    'Coastal Karnataka': ['Karnataka'],
    'East Madhya Pradesh': ['Madhya Pradesh'],
    'East Rajasthan': ['Rajasthan'],
    'East Uttar Pradesh': ['Uttar Pradesh'],
    'Gangetic West Bengal': ['West Bengal'],
    'Gujarat Region': ['Gujarat', 'Dadra and Nagar Haveli', 'Daman and Diu'],
    'Haryana Delhi & Chandigarh': ['Haryana', 'Delhi', 'Chandigarh'],
    'Himachal Pradesh': ['Himachal Pradesh'],
    'Jammu & Kashmir': ['Jammu and Kashmir'],
    'Jharkhand': ['Jharkhand'],
    'Kerala': ['Kerala'],
    'Konkan & Goa': ['Goa'],
    'Lakshadweep': ['Lakshadweep'],
    'Madhya Maharashtra': ['Maharashtra'],
    'Matathwada': ['Maharashtra'],
    'Naga Mani Mizo Tripura': ['Nagaland', 'Manipur', 'Mizoram', 'Tripura'],
    'North Interior Karnataka': ['Karnataka'],
    'Orissa': ['Orissa'],
    'Punjab': ['Punjab'],
    'Rayalseema': ['Andhra Pradesh'],
    'Saurashtra & Kutch': ['Gujarat'],
    'South Interior Karnataka': ['Karnataka'],
    'Sub Himalayan West Bengal & Sikkim': ['West Bengal', 'Sikkim'],
    'Tamil Nadu': ['Tamil Nadu', 'Puducherry'],
    'Telangana': ['Andhra Pradesh'],
    'Uttarakhand': ['Uttaranchal'],
    'Vidarbha': ['Maharashtra'],
    'West Madhya Pradesh': ['Madhya Pradesh'],
    'West Rajasthan': ['Rajasthan'],
    'West Uttar Pradesh': ['Uttar Pradesh'],
}

GEO2GOV = {}
for key, regs in GOV2GEO.items():
    for reg in regs:
        GEO2GOV.setdefault(reg, []).append(key)

## 'Dadra and Nagar Haveli', 'Daman and Diu', 'Puducherry' added after manual map inspection

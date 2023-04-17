# py39

# Application to append ASUD database information from the
#   ASUD web service
# Break into blocks of 100 requests
# Requires openpyxl

import os
import sys
import requests
import csv
import io
import pandas as pd
import numpy as np
import xlsxwriter

strat_units_wfs_url = "https://services.ga.gov.au/gis/stratunits/stratunit/wfs"
MAX_QUERIES = 100
naf_folder = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes'
naf_dataset = 'NationalAquiferFramework_with_NAF_IDs.xlsx'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_WITH_ASUD_Units_from_web_service.xlsx'

#stratno = 20758
#
# strat_unit_id = "StratigraphicUnit." + str(stratno)


# strat_units_get_url = "https://services.ga.gov.au/gis/stratunits/stratunit/wfs?request=GetFeature&version=1.1.0" \
#                     "&typeName" \
#                   "=stratunit:StratigraphicUnit&featureId=StratigraphicUnit.{0}&outputFormat=application/json"
#
# strat_units_get = strat_units_get_url.format(stratno)
#
#
# get_response = requests.get(strat_units_get)
#
# print(get_response.text)

## To do advanced filtering via POST

get_feature = """<?xml version="1.0" encoding="UTF-8"?>
                    <wfs:GetFeature version="1.1.0" 
                    xmlns:wfs="http://www.opengis.net/wfs"
                    xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.opengis.net/wfs 
                    http://schemas.opengis.net/wfs/1.1.0/wfs.xsd" maxFeatures="200" 
                    outputFormat="application/json">
                        <wfs:Query typeName="stratunit:StratigraphicUnit">
                        <ogc:Filter>
                            <ogc:PropertyIsLike wildCard="%" singleChar="#" escapeChar="!">
                            <ogc:PropertyName>NAME</ogc:PropertyName>
                            <ogc:Literal>%Birrindudu%</ogc:Literal>
                            </ogc:PropertyIsLike>
                        </ogc:Filter>
                        </wfs:Query>
                    </wfs:GetFeature>"""

get_feature_list = """<?xml version="1.0" encoding="UTF-8"?>
            <wfs:GetFeature version="1.1.0" 
                            xmlns:wfs="http://www.opengis.net/wfs"
                            xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xsi:schemaLocation="http://www.opengis.net/wfs 
                            http://schemas.opengis.net/wfs/1.1.0/wfs.xsd" maxFeatures="200" 
                            outputFormat="text/csv">
                <wfs:Query typeName="stratunit:StratigraphicUnit">
                <ogc:Filter>
              <ogc:Or>
              {0}
              </ogc:Or>
                </ogc:Filter>
                </wfs:Query>
            </wfs:GetFeature>"""

stratnos = [20758,23998,13847]

property_filters = []

for stratno in stratnos:
    property_filters.append ("""
        <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>STRATNO</ogc:PropertyName>
        <ogc:Literal>{0}</ogc:Literal>
        </ogc:PropertyIsEqualTo>
    """.format(stratno))

get_all_stratnos = get_feature_list.format("".join(property_filters))

response_post = requests.post(strat_units_wfs_url, data=get_all_stratnos)

df = pd.read_csv(io.StringIO(response_post.text), sep=',', quoting=csv.QUOTE_ALL)
print(df.head())


### FUNCTIONS ######################

def get_strat_from_asud_stratno(stratno):
    # Search on stratno column
    query = """
            SELECT  s.stratno, s.stratname
            FROM    geodx.stratnames s
            WHERE   stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_wms_strat(stratnos: list):
    get_feature_list = """<?xml version="1.0" encoding="UTF-8"?>
                <wfs:GetFeature version="1.1.0" 
                                xmlns:wfs="http://www.opengis.net/wfs"
                                xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                xsi:schemaLocation="http://www.opengis.net/wfs 
                                http://schemas.opengis.net/wfs/1.1.0/wfs.xsd" maxFeatures="200" 
                                outputFormat="text/csv">
                    <wfs:Query typeName="stratunit:StratigraphicUnit">
                    <ogc:Filter>
                <ogc:Or>
                {0}
                </ogc:Or>
                    </ogc:Filter>
                    </wfs:Query>
                </wfs:GetFeature>"""

    stratnos = [20758,23998,13847]

    property_filters = []

    for stratno in stratnos:
        property_filters.append ("""
            <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>STRATNO</ogc:PropertyName>
            <ogc:Literal>{0}</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        """.format(stratno))

    get_all_stratnos = get_feature_list.format("".join(property_filters))

    response_post = requests.post(strat_units_wfs_url, data=get_all_stratnos)

    df = pd.read_csv(io.StringIO(response_post.text), sep=',', quoting=csv.QUOTE_ALL)
    print(df.head())


###   MAIN    ######################

# Read first few columns of Full_NAF worksheet into Pandas
naf_path = os.path.join(naf_folder, naf_dataset)
#df = pd.read_excel(naf_path, sheet_name='Full_NAF', usecols='A:L', header=2)
df = pd.read_excel(naf_path, sheet_name='Full_NAF', header=2)
# remove row of bad data
df = df.drop([0])
# Three columns are imported as Float, so convert back to Integer.
#   Note that empty excel cells are now zeros
for i in ('NAFID', 'NafGAStratNumber', 'NafHGUNumber', 'NafHGCNumber'):
    df[i] = df[i].fillna(0)
df = df.astype({'NAFID': int,'NafGAStratNumber': int, 'NafHGUNumber': int, 'NafHGCNumber': int})
print(df.head())
print(df.dtypes)
df_headings = list(df.columns.values)


workbook = xlsxwriter.Workbook(output_file)
worksheet = workbook.add_worksheet()
worksheet.freeze_panes(1,0)
heading_format = workbook.add_format({'bold': True, 'italic': True})
ws_row = 0
ws_col = 0
# Insert column headings
for idx, val in enumerate(df_headings):
    worksheet.write(ws_row, idx, str(val), heading_format)
    ws_col += 1

asud_heading_format = workbook.add_format({'bold': True, 'italic': True, 'color': '#fc7703'})

asud_headings = [
    'STRATNO',
    'UNITNAME',
]

for idx, val in enumerate(asud_headings):
    worksheet.write(ws_row, ws_col+idx, val, asud_heading_format)

# Get ASUD information for each STRATNO and write to worksheet
ws_row += 1
for _, row in df.iterrows():
    ws_col = 0
    # Limit rows for testing
    # if ws_row > 50:
    #    break
    naf_gastratno = row['NafGAStratNumber']
    asud_details = ''
    if naf_gastratno is not np.nan:
        asud_details = get_strat_from_asud_stratno(naf_gastratno)

    for value in row:
        if type(value) is float:
            value = ''
        worksheet.write(ws_row, ws_col, str(value))
        ws_col += 1
    #ws_col += 1
    asud_col = ws_col
    if asud_details:
        for _, asud_tuple in enumerate(asud_details):
            tuple_stratno = asud_tuple[0]
            for item in asud_tuple:
                worksheet.write(ws_row, asud_col, item)
                asud_col += 1
            
            asud_col = ws_col
            ws_row += 1
    else:
        worksheet.write(ws_row, asud_col, 'STRATNO not found in ASUD')
        ws_row += 1

workbook.close()

# Developed using Python 3.9.13 (py39 env)

"""
An application to demonstrate the use of Geoscience Australia's
web services to check internal consistency of data stored in the
National Aquifer Framework (NAF). Creates a new worksheet with
stratigraphic unit names (UNITNAME) appended to the (NAF).

The version of the NAF used in this exercise only contains the "Full_NAF"
worksheet, which was  modified so that column A, labelled NAFID, has been
inserted; it contains a numeric unique identifier.

In this application, XML data is retrieved from Geoscience Australia's
Australian Stratigraphic Units Database, which is published via the
Web Feature Service (WFS) accessible from the URL in the strat_units_wfs_url
variable.

The get_wms_strat function generates a HTTP POST request as a query to the
WFS from a list of stratigraphic unit numbers derived by reading a limited
chunk of NafGAStratNumber cells in the input worksheet. The WMS returns each
hit in one line, giving us numerous lines in each chunk. Results are not
returned in the same order as the list used to generate the request.

The write_chunk_to_worksheet function reads the input NAF spreadsheet
line-by-line and finds the relevant line in the WMS response by matching
against the NafGAStratNumber. It writes the NAF row, extracts the unit name
(NAME field) using an equivalence of STRATNO to NafGAStratNumber, and appends
the NAME to the workbook in the UNITNAME field.

Chunked into blocks of 100 requests to avoid overwhelming servers.

Requires openpyxl
"""

import csv
import io
import os
import requests
import pandas as pd
import xlsxwriter

strat_units_wfs_url = "https://services.ga.gov.au/gis/stratunits/stratunit/wfs"
naf_folder = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes'
naf_dataset = 'NationalAquiferFramework_with_NAF_IDs.xlsx'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_WITH_ASUD_Units_from_web_service.xlsx'

MAX_QUERIES = 100       # Chunk size

### FUNCTIONS ######################

def get_processed_naf(chunk: pd.DataFrame):
    naf_chunk_stratnos = []
    for _, row in chunk.iterrows():
        naf_chunk_stratnos.append(row['NafGAStratNumber'])
    wmsstrat = get_wms_strat(naf_chunk_stratnos)
    return(wmsstrat)

def get_wms_strat(stratnos: list) -> pd.DataFrame:
    if not stratnos:
        # use test set
        stratnos = [20758,23998,13847]
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
    wfsdf = pd.read_csv(io.StringIO(response_post.text), sep=',', quoting=csv.QUOTE_ALL)
    #print(wfsdf.head())
    return(wfsdf)

def write_chunk_to_worksheet(worksheet, ws_start_row, naf_df, asud_chunk):
    ws_row = ws_start_row
    for _, row in naf_df.iterrows():
        ws_col = 0
        this_row_stratno = row['NafGAStratNumber']
        try:
            asud_unitname = asud_chunk.loc[asud_chunk['STRATNO'] == this_row_stratno, 'NAME'].iloc[0]
        except:
            asud_unitname = 'Unit not found using ASUD web service'
        for value in row:
            if type(value) is float:
                value = ''
            worksheet.write(ws_row, ws_col, str(value))
            ws_col += 1
            
        worksheet.write(ws_row, ws_col, asud_unitname)
        ws_row += 1
    return worksheet, ws_row

###   MAIN    ######################
# Read Full_NAF worksheet into Pandas
naf_path = os.path.join(naf_folder, naf_dataset)
df = pd.read_excel(naf_path, sheet_name='Full_NAF', header=2)
# remove row of bad data
df = df.drop([0])
# Three columns are imported as Float, so convert back to Integer.
#   Note that empty excel cells are now zeros
for i in ('NAFID', 'NafGAStratNumber', 'NafHGUNumber', 'NafHGCNumber'):
    df[i] = df[i].fillna(0)
df = df.astype({'NAFID': int,'NafGAStratNumber': int, 'NafHGUNumber': int, 'NafHGCNumber': int})
df_headings = list(df.columns.values)
max_naf_rows = df.shape[0]

# Create Excel workbook to write output
#workbook = xlsxwriter.Workbook(output_file)
with xlsxwriter.Workbook(output_file) as workbook:
    worksheet = workbook.add_worksheet()
    worksheet.freeze_panes(1,0)
    heading_format = workbook.add_format({'bold': True, 'italic': True})

    # Set counters for (reading and) writing workbooks
    ws_row = 0
    ws_col = 0

    # Insert column headings from NAF spreadsheet
    for idx, val in enumerate(df_headings):
        worksheet.write(ws_row, idx, str(val), heading_format)
        ws_col += 1

    # Add additional column headings from ASUD, in orange
    asud_heading_format = workbook.add_format({'bold': True, 'italic': True, 'color': '#fc7703'})
    asud_headings = [
        'UNITNAME',
    ]
    for idx, val in enumerate(asud_headings):
        worksheet.write(ws_row, ws_col+idx, val, asud_heading_format)

    # Finished writing header, so move down one row to write data
    ws_row += 1

    # Process NAF into new workbook
    print("Start processing workbook.\nChunk size: {} rows.".format(MAX_QUERIES))
    while ws_row <= max_naf_rows:
        print("No processing NAF row number: {}".format(ws_row))
        # Read a chunk of NAF and get ASUD info for that chunk
        naf_chunk = df.iloc[(ws_row-1):(ws_row+MAX_QUERIES-1)]
        processed_chunk = get_processed_naf(naf_chunk)

        # Write NAF and ASUD chunks to worksheet
        worksheet, ws_row = write_chunk_to_worksheet(worksheet, ws_row, naf_chunk, processed_chunk)
        
# Developed using Python 3.9.13
# Requires openpyxl

# Application to append ASUD database information from the
#   geodx.flatstrat_current and provinces tables to the end
#   of each row of the Full_NAF worksheet of the NAF.
# The flatstrat_current table holds a small set of information
#   for each *current* stratigraphic unit in the Australian
#   Stratigraphic Units Database (ASUD).
# Data from the provinces table is checked 

import os
import sys
import numpy as np
import pandas as pd
import xlsxwriter
import csv

#naf_folder = r'\\prod.lan\active\data\sdl\Hydrogeology\NationalAquiferFramework_2016'
#naf_dataset = 'NationalAquiferFramework.xlsx'
naf_folder = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes'
naf_dataset_with_ids = 'NationalAquiferFramework_with_NAF_IDs.xlsx'
OneMGeol_folder = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF\1M_geodatabase_10_3_geology_tables'
geol_line_file = 'GeologicUnitLines1M_TableToText.txt'
geol_poly_file = 'GeologicUnitPolygons1M_TableToText.txt'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_matched_with_1MGeol.xlsx'

### FUNCTIONS ######################

def read_1M_line_data(line_geology):
    with open(line_geology, newline='') as csvfile:
        linereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        lineDict = {}
        # We want objectid,  mapSymbol, plotSymbol, stratno, name, geologicHistory, lithology
        # ie, indexes 0, 1, 2, 3, 4,  8, 12
        lineindexes = [0, 1, 2, 3, 4,  8, 12]
        for row in linereader:
            line = []
            for i in lineindexes:
                line.append(row[i])
            if not line[4] in lineDict:
                lineDict[line[4]] = line
        return lineDict

def read_1M_poly_data(poly_geology):
    with open(poly_geology, newline='') as csvfile:
        polyreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        polyDict = {}
        # We want objectid,  mapSymbol, plotSymbol, stratno, name, geologicHistory, lithology
        # ie, indexes 0, 1, 2, 3, 4,  8, 12
        polyindexes = [0, 1, 2, 3, 4,  8, 12]
        for row in polyreader:
            line = []
            for i in polyindexes:
                line.append(row[i])
            if not line[4] in polyDict:
                polyDict[line[4]] = line
        return polyDict

def get_1M_details(NafGUName, poly_dict, line_dict):
    geol_details = []
    dataset = ''
    if NafGUName in poly_dict:
        dataset = 'poly'
        geol_details = poly_dict[NafGUName]
    elif NafGUName in line_dict:
        dataset = 'line'
        geol_details = line_dict[NafGUName]
    print(geol_details)
    return dataset, geol_details


### # MAIN #########################

# Prepare data from GA's 1:1M Surface Geology dataset for comparison with NAF
geol_line_file = os.path.join(OneMGeol_folder, geol_line_file)
geol_line_dict = read_1M_line_data(geol_line_file)
geol_poly_file = os.path.join(OneMGeol_folder, geol_poly_file)
geol_poly_dict = read_1M_poly_data(geol_poly_file)

# Read Full_NAF (with IDs) worksheet into Pandas
naf_path = os.path.join(naf_folder, naf_dataset_with_ids)
naf_df = pd.read_excel(naf_path, sheet_name='Full_NAF', header=2)
# remove row of bad data
naf_df = naf_df.drop([0])
# Three columns are imported as Float, so convert back to Integer.
#   Note that empty excel cells are now zeros
for i in ('NAFID', 'NafGAStratNumber', 'NafHGUNumber', 'NafHGCNumber'):
    naf_df[i] = naf_df[i].fillna(0)
naf_df = naf_df.astype({'NAFID': int,'NafGAStratNumber': int, 'NafHGUNumber': int, 'NafHGCNumber': int})
print(naf_df.head())
print(naf_df.dtypes)
naf_df_headings = list(naf_df.columns.values)

# Create workbook to write results
workbook = xlsxwriter.Workbook(output_file)
worksheet = workbook.add_worksheet()
worksheet.freeze_panes(1,0)
heading_format = workbook.add_format({'bold': True, 'italic': True})
ws_row = 0
ws_col = 0
# Insert column headings
for idx, val in enumerate(naf_df_headings):
    worksheet.write(ws_row, idx, str(val), heading_format)
    ws_col += 1

GAgeol_heading_format = workbook.add_format({'bold': True, 'italic': True, 'color': '#fc7703'})
geol_headings = [
    'rpt_NafGUName',
    '1M_geol_layer',
    '1M_geol_Objectid-forQCOnly',
    'mapSymbol',
    'plotSymbol',
    'stratno',
    'name',
    'geologicHistory',
    'lithology',
]

for idx, val in enumerate(geol_headings):
    worksheet.write(ws_row, ws_col+idx, val, GAgeol_heading_format)

ws_row += 1
for _, row in naf_df.iterrows():
    ws_col = 0
    # Limit rows for testing
    # if ws_row > 50:
    #    break
    naf_gu_name = row['NafGUName']
    #line_details = ''
    """if naf_gu_name is not np.nan:
        print('NAF GU: {}'.format(naf_gu_name))
        geol_info = get_1M_details(naf_gu_name, geol_poly_dict, geol_line_dict)
        print(geol_info)"""

    spatial_type, geol_info = get_1M_details(naf_gu_name, geol_poly_dict, geol_line_dict)
    
    # Write the data to the Excel spreadsheet
    # Starting by reproducing the first bit of the BoM's NAF spreadsheet
    for value in row:
        if type(value) is float:
            value = ''
        worksheet.write(ws_row, ws_col, str(value))
        ws_col += 1
    worksheet.write(ws_row, ws_col, naf_gu_name)
    ws_col += 1
    geol_col = ws_col
    #if line_details:
    if geol_info:
        #for _, line_tuple in enumerate(line_details):
        worksheet.write(ws_row, geol_col, spatial_type)
        geol_col += 1
        for _, item in enumerate(geol_info):
            #tuple_stratno = line_tuple[0]
            #for item in line_tuple:
            worksheet.write(ws_row, geol_col, item)
            geol_col += 1
        geol_col = ws_col
        ws_row += 1
    else:
        worksheet.write(ws_row, geol_col, 'Unit not found in 1M Surface Geology dataset')
        ws_row += 1

workbook.close()
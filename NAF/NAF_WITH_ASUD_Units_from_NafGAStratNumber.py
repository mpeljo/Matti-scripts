# Developed using Python 3.7.3
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

naf_folder = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes'
naf_dataset = 'NationalAquiferFramework_with_NAF_IDs.xlsx'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_WITH_ASUD_Units_from_Lookup_to_NafGAStratNumber.xlsx'

sys.path.append(r'H:\Python\Oracle')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

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


###   MAIN    ######################
# Read first few columns of Full_NAF worksheet into Pandas
naf_path = os.path.join(naf_folder, naf_dataset)
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
cur.close()
oracon.close()
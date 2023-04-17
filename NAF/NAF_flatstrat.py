# Developed using Python 3.7.3

# Requires openpyxl

import os
import sys
import numpy as np
import pandas as pd
import xlsxwriter

naf_folder = r'\\prod.lan\active\data\sdl\Hydrogeology\NationalAquiferFramework_2016'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_FLATSTRAT.xlsx'

asud_url_base = r'https://asud.ga.gov.au/search-stratigraphic-units/results/'

sys.path.append(r'H:\Python\Oracle')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

def get_stratno_flatstrat_current(stratno):
    # Search on stratno column
    query = """
            select  f.*
            from    geodx.flatstrat_current f
            where   f.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_flatstrat_current(NafGUName):
    # Search on stratname column
    query = """
            select  f.*
            from    geodx.flatstrat_current f
            WHERE   f.unitname = '{}'""".format(NafGUName)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_stratno_flatstrat_current_provs(stratno):
    # Search on stratno column
    query = """
            select  f.*, p.provname
            from    geodx.flatstrat_current f
            join    provs.prov_strats ps on ps.stratno = f.stratno
            join    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            where   f.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_flatstrat_current_provs(NafGUName):
    # Search on stratname column
    query = """
            select  f.*, p.provname
            from    geodx.flatstrat_current f
            join    provs.prov_strats ps on ps.stratno = f.stratno
            join    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            WHERE   f.unitname like '{}'""".format(NafGUName)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_stratno_asud(stratno):
    # Search on stratno column
    query = """
            SELECT  s.stratno, s.stratname, stat.statusname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
            FROM    geodx.stratnames s
            JOIN    geodx.stratstatus stat on s.status = stat.status
            WHERE   stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_asud(strat):
    # Search on stratname column
    query = """
            SELECT  s.stratno, s.stratname, stat.statusname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
            FROM    geodx.stratnames s
            JOIN    geodx.stratstatus stat on s.status = stat.status
            WHERE   stratname like '%{} %'""".format(strat)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_asud_details(token):
    # This approach might be good to try to get working...
    if type(token) is int:
        clause = 'stratno = \{\}'
    else:
        clause = 'stratname like \'%\{\} %\''
    query = """
            SELECT  stratno, stratname, parent, topminage, basemaxage, description, comments
            FROM    geodx.stratnames
            WHERE   {}""".format(clause, token)
    cur.execute(query)
    result = cur.fetchall()
    return result
    
# Read first few columns of Full_NAF worksheet into Pandas
naf_path = os.path.join(naf_folder, 'NationalAquiferFramework.xlsx')
df = pd.read_excel(naf_path, sheet_name='Full_NAF', usecols='A:L', header=2)
df = df.drop([0])
# Three columns are imported as Float, so convert back to Integer.
#   Note that empty excel cells are now zeros
for i in ('NafGAStratNumber', 'NafHGUNumber', 'NafHGCNumber'):
    df[i] = df[i].fillna(0)
df = df.astype({'NafGAStratNumber': int, 'NafHGUNumber': int, 'NafHGCNumber': int})
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
"""asud_headings = [
    'NafGUName_repeat',
    'Stratno',
    'Stratname',
    'Status',
    'Parent',
    'topMinAgeName',
    'botMaxAgeName',
    'Description',
    'Comments'
]"""

asud_headings = [
    'NafGUName_repeat',
    'STRATNO',
    'UNITNAME',
    'SUPERGROUP',
    'GROUP',
    'SUBGROUP',
    'FORMATION',
    'MEMBER',
    'BED',
    'STATE',
    'DESCRIPTION',
    'BASEMAXAGENAME',
    'TOPMINAGENAME',
    'ISCURRENT',
    'USAGE',
    'SUPERSUITE',
    'SUITE',
    'ASUD_URL',
    #'PROVINCE',
]

for idx, val in enumerate(asud_headings):
    worksheet.write(ws_row, ws_col+idx, val, asud_heading_format)

uninteresting_prefixes = [
    'Mount',
    'Cape',
    'Upper',
    'Lower',
    'North',
    'South',
    'East',
    'West',
]
# Get ASUD information for each NafGUName and write to worksheet
"""
Tokenise each NafGUName. If the final token is a number then look up that number,
otherwise take the first token and look that up.

Report back stratno and name and parent stratno and name of matching ASUD rows containing
the first token.

"""

ws_row += 1
for _, row in df.iterrows():
    ws_col = 0
    # Limit rows for testing
    # if ws_row > 50:
    #    break
    naf_gu_name = row['NafGUName']
    asud_details = ''
    if naf_gu_name is not np.nan:
        # Tokenise the NAF GU Name words
        tokens = str(naf_gu_name).split()
        print('NAF GU: {}'.format(naf_gu_name))
        last_token = tokens[len(tokens) - 1]
        # Check whether the final token is a number, in which case query on stratno
        if last_token.isnumeric():
            stratno = int(last_token)
            asud_details = get_stratno_flatstrat_current(stratno)
        # Otherwise query on stratname using the first token
        else:
            asud_details = get_named_flatstrat_current(naf_gu_name)
            # Don't use uninteresting prefixes
            #if uninteresting_prefixes.count(tokens[0]) == 0:
            #    asud_details = get_named_flatstrat_current(tokens[0])
            #else:
            #    asud_details = get_named_flatstrat_current(tokens[1])
        # Write the data to the Excel spreadsheet
        # Starting by reproducing the first bit of the BoM's NAF spreadsheet
        for value in row:
            if type(value) is float:
                value = ''
            worksheet.write(ws_row, ws_col, str(value))
            ws_col += 1
        worksheet.write(ws_row, ws_col, naf_gu_name)
        ws_col += 1
        asud_col = ws_col
        for _, asud_tuple in enumerate(asud_details):
            tuple_stratno = asud_tuple[0]
            for item in asud_tuple:
                worksheet.write(ws_row, asud_col, item)
                asud_col += 1
            asud_url = asud_url_base + str(tuple_stratno)
            worksheet.write(ws_row, asud_col, asud_url)
            asud_col = ws_col
            ws_row += 1
        #worksheet.write(ws_row, ws_col, str(asud_details))
    ws_row += 1

workbook.close()
cur.close()
oracon.close()
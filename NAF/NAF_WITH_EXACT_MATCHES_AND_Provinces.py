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
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_WITH_EXACT_MATCHES_AND_Provinces.xlsx'

asud_url_base = r'https://asud.ga.gov.au/search-stratigraphic-units/results/'

# Connect to Oracle without exposing credentials
sys.path.append(r'H:\Python\Oracle')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

### FUNCTIONS ######################
def get_provinces(stratno):
    # Find provinces by searching on ASUD stratno
    query = """
        select  p.provname
        from    provs.prov_strats ps
        join    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
        where   ps.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_stratno_flatstrat_current_provs(stratno):
    # Find provinces and flatstrat data by search on ASUD stratno
    # Flatstrat contains columns with stratno, unit name, supergroup,
    #   group, subgroup, formation, member, bed, and the state(s) the
    #   unit occurs in.
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
    # Find provinces and flatstrat data by search on stratname column
    # Flatstrat contains columns with stratno, unit name, supergroup,
    #   group, subgroup, formation, member, bed, and the state(s) the
    #   unit occurs in.
    query = """
            select  f.*, p.provname
            from    geodx.flatstrat_current f
            join    provs.prov_strats ps on ps.stratno = f.stratno
            join    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            WHERE   f.unitname like '{}'""".format(NafGUName)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_geodx_stratname(NafGUName):
    # Search all stratigraphic units on stratname column
    query = """
            select sn.stratno, sn.stratname, r.rank_name as rank, s.value as status, sn.iscurrent, sn.minagename, sn.maxagename
            from geodx.stratnames sn
            join geodx.lu_strat_rank r on sn.rank = r.strat_rankno
            join geodx.lu_status_category s on sn.status = s.status_category_no
            where sn.stratname like '{}'""".format(NafGUName)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_stratno_geodx_stratname(stratno):
    # Search all stratigraphic units on stratno column
    query = """
            select sn.stratno, sn.stratname, r.rank_name as rank, s.value as status, sn.iscurrent, sn.minagename, sn.maxagename
            from geodx.stratnames sn
            join geodx.lu_strat_rank r on sn.rank = r.strat_rankno
            join geodx.lu_status_category s on sn.status = s.status_category_no
            where sn.stratno like {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_stratno_flatstrat_current(stratno):
    # Search the FLATSTRAT table on stratno column.
    # The FLATSTRAT table contains a limited number of
    #   columns from the STRATNAMES table
    query = """
            select  f.*
            from    geodx.flatstrat_current f
            where   f.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_flatstrat_current(NafGUName):
    # Search the FLATSTRAT table on stratname column
    # The FLATSTRAT table contains a limited number of
    #   columns from the STRATNAMES table
    query = """
            select  f.*
            from    geodx.flatstrat_current f
            WHERE   f.unitname = '{}'""".format(NafGUName)
    cur.execute(query)
    result = cur.fetchall()
    return result


##############  MAIN  ######################
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

# Create output workbook
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
    'PROVINCES',
]

for idx, val in enumerate(asud_headings):
    worksheet.write(ws_row, ws_col+idx, val, asud_heading_format)

# The list of words at the beginning of many stratigraphic unit names
#   that aren't sufficiently diagnostic by themselves and so will be
#   ignored in the analysis 
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
        if asud_details:
            for _, asud_tuple in enumerate(asud_details):
                tuple_stratno = asud_tuple[0]
                for item in asud_tuple:
                    worksheet.write(ws_row, asud_col, item)
                    asud_col += 1
                asud_url = asud_url_base + str(tuple_stratno)
                worksheet.write(ws_row, asud_col, asud_url)
                asud_col += 1
                province = ''
                provinces = get_provinces(tuple_stratno)
                if not provinces:
                    province = 'No province information available'
                else:
                    for item in provinces:
                        province = item[0] + ', ' + province
                worksheet.write(ws_row, asud_col, province)
                asud_col = ws_col
                ws_row += 1
        else:
            worksheet.write(ws_row, asud_col, 'Unit not found or not current in ASUD')
            ws_row += 1

workbook.close()
cur.close()
oracon.close()
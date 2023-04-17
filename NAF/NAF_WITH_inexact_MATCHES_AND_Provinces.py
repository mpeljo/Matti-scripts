# Developed using Python 3.9
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
naf_dataset = 'NAF_WITH_inexact_MATCHES_AND_Provinces_step01.xlsx'
output_file = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\NAF fixes\NAF_WITH_inexact_MATCHES_AND_Provinces-output.xlsx'

asud_url_base = r'https://asud.ga.gov.au/search-stratigraphic-units/results/'

sys.path.append(r'H:\Python\Oracle')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

### FUNCTIONS ######################
def get_provinces(stratno):
    query = """
        select p.provname
        from provs.prov_strats ps
        join provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
        where ps.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_named_geodx_stratname(NafGUName):
    # Search on stratname column
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
    # Search on stratno column
    query = """
            select sn.stratno, sn.stratname, r.rank_name as rank, s.value as status, sn.iscurrent, sn.minagename, sn.maxagename
            from geodx.stratnames sn
            join geodx.lu_strat_rank r on sn.rank = r.strat_rankno
            join geodx.lu_status_category s on sn.status = s.status_category_no
            where sn.stratno like {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result


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

def get_named_asud(word):
    # Search on stratname column
    query = """
            SELECT  s.stratno, s.stratname, stat.statusname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
            FROM    geodx.stratnames s
            JOIN    geodx.stratstatus stat on s.status = stat.status
            WHERE   stratname like '%{} %'""".format(word)
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


################    MAIN    ################
# Read first few columns of NAF_WITH_inexact_MATCHES_AND_Provinces_step01 worksheet into Pandas
naf_path = os.path.join(naf_folder, naf_dataset)
df = pd.read_excel(naf_path, sheet_name='Data')


print(df.head())
print(df.dtypes)
#df_headings = list(df.columns.values)

workbook = xlsxwriter.Workbook(output_file)
worksheet = workbook.add_worksheet()
worksheet.freeze_panes(1,0)
heading_format = workbook.add_format({'bold': True, 'italic': True})
ws_row = 0
ws_col = 0
# Insert column headings
for idx, val in enumerate(list(df.columns.values)):
    worksheet.write(ws_row, idx, str(val), heading_format)
    ws_col += 1

asud_heading_format = workbook.add_format({'bold': True, 'italic': True, 'color': '#fc7703'})

asud_headings = [
    'NafGUName_repeat',

    'STRATNO',
    'Unit_name',
    'Status',
    'Parent_stratno',
    'TopMinAgeName',
    'BaseMaxAgeName',
    'Description',
    'Comments',
    'ASUD_URL',
    'Province(s)',
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
            asud_details = get_stratno_geodx_stratname(stratno)
        # Otherwise query on stratname using the first token
        else:
            # Don't use uninteresting prefixes
            if uninteresting_prefixes.count(tokens[0]) == 0:
                asud_details = get_named_asud(tokens[0])
            else:
                asud_details = get_named_asud(tokens[1])
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
            worksheet.write(ws_row, asud_col, 'No matches found in ASUD')
            ws_row += 1

workbook.close()
cur.close()
oracon.close()
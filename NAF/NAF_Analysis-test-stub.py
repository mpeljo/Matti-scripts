# Developed using Python 3.7.3

import os
import sys
import numpy as np
import pandas as pd
import xlsxwriter

naf_folder = r'\\prod.lan\active\data\sdl\Hydrogeology\NationalAquiferFramework_2016'
output_file = r'C:\Users\u25834\Desktop\NAF_ASUD.xlsx'

sys.path.append(r'H:\Python\Oracle')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

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

def get_tidy_named_asud(fullstratname):
     # Search on stratname column
    query = """
            SELECT  s.stratno, s.stratname, stat.statusname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
            FROM    geodx.stratnames s
            JOIN    geodx.stratstatus stat on s.status = stat.status
            WHERE   stratname like '{}'""".format(fullstratname)
    cur.execute(query)
    while True:
        row = cur.fetchone()
        if row is None:
            break
        print(row)
        stratno = row[0]
        prov_query = """
            select p.eno, p.provname from provs.prov_strats ps
            join provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            where ps.stratno = {}""".format(stratno)
        while True:
            provrow = print(cur.execute(prov_query))

def get_strat_provs_from_stratno(stratno):
    # Search on stratno column
    query = """
        SELECT DISTINCT s.stratno, s.stratname, stat.statusname, p.provname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
        FROM        geodx.stratnames s
        LEFT JOIN   geodx.stratstatus stat on s.status = stat.status
        LEFT JOIN   provs.prov_strats ps on ps.stratno = s.stratno
        LEFT JOIN   provs.provinces p on p.eno = ps.eno and p.pref = 'Y' and p.provtype <> 'georegion'
        WHERE       s.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_strat_provs_from_stratword(stratword):
    # Search on stratname column
    query = """
        SELECT DISTINCT s.stratno, s.stratname, stat.statusname, p.provname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
        FROM        geodx.stratnames s
        LEFT JOIN   geodx.stratstatus stat on s.status = stat.status
        LEFT JOIN   provs.prov_strats ps on ps.stratno = s.stratno
        LEFT JOIN   provs.provinces p on p.eno = ps.eno and p.pref = 'Y' and p.provtype <> 'georegion'
        WHERE       s.stratname like '%{} %'""".format(stratword)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_strat_provs_from_fullstratname(fullstratname):
    # Search on stratname column
    query = """
        SELECT DISTINCT s.stratno, s.stratname, stat.statusname, p.provname, s.parent, s.topminagename, s.basemaxagename, s.description, s.comments
        FROM        geodx.stratnames s
        LEFT JOIN   geodx.stratstatus stat on s.status = stat.status
        LEFT JOIN   provs.prov_strats ps on ps.stratno = s.stratno
        LEFT JOIN   provs.provinces p on p.eno = ps.eno and p.pref = 'Y' and p.provtype <> 'georegion'
        WHERE       s.stratname like '{}'""".format(fullstratname)
    cur.execute(query)
    result = cur.fetchall()
    return result

def get_provs(strat):
    # Search on stratname column
    query = """
            SELECT  p.eno, p.provname
            FROM    provs.prov_strats ps
            JOIN    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            WHERE   ps.stratno = {}""".format(strat)
    cur.execute(query)
    result = cur.fetchall()
    return result

"""
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
asud_headings = [
    'NafGUName_repeat',
    'Stratno',
    'Stratname',
    'Status',
    'Province',
    'Parent',
    'topMinAgeName',
    'botMaxAgeName',
    'Description',
    'Comments'
]

for idx, val in enumerate(asud_headings):
    worksheet.write(ws_row, ws_col+idx, val, asud_heading_format)
"""
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
test_NAF_units = [
    'Allaru Mudstone',
    'Pirramimma Sandstone',]
"""
    'Ngaltinga Formation',
    'Christies Beach Formation',
    'Ochre Cove Formation',
    'Undifferentiated Quaternary sediments',
    'Bakara Calcrete',
    'Molineaux-Lowan Sands',
    'Semaphore Sand Member',
    'Lowan Sand',
    'Loveday Soil',
    'Simpson Sand',
    'Wintrena Formation',
    'Bunyip Sand',
    'Molineaux Sand',
    'Woorinen Formation',
    'Ripon Calcrete',
    'Yamba Formation',
    'Undifferentiated Quaternary aeolian sediments',
    'coastal dunes 38488',
    'dunes 38496',
    'lunette dunes 72955',
    'sand plain 38499',
    'alluvium 38485',
    'Telford Gravel',
    'Arrowie Formation',
    'spring deposits 38500',
    'Talus, vegetated and active',
    'Tyrrell beds',
    'Curtis Island alluvium',
    'Yardinna Claystone',
    'Coleman River alluvium',
    'sedimentary rocks 72357 - SA',
    'Millyera Formation',
    'Condamine River alluvium',
    'Callabonna Clay',
    'limestone 72694',
    'colluvium 74366',
    'Coomera and Nerang Rivers alluvium',
    'Pooraka Formation',
]"""


ws_row = 0
ws_row += 1

for _, naf_gu_name in enumerate(test_NAF_units):

#for _, row in df.iterrows():
    ws_col = 0

    #naf_gu_name = row['NafGUName']
    asud_details = ''
    if naf_gu_name is not np.nan:
        # Tokenise the NAF GU Name words
        tokens = str(naf_gu_name).split()
        print('\nNAF GU: {}'.format(naf_gu_name))
        last_token = tokens[len(tokens) - 1]
        # Check whether the final token is a number, in which case query on stratno
        if last_token.isnumeric():
            stratno = int(last_token)
            #asud_details = get_stratno_asud(stratno)
            asud_details = get_strat_provs_from_stratno(stratno)
        # Otherwise query on stratname using the first token
        else:
            # Don't use uninteresting prefixes
            #if uninteresting_prefixes.count(tokens[0]) == 0:
                #asud_details = get_named_asud(tokens[0])
                #asud_details = get_strat_provs_from_stratword(tokens[0])
            #else:
                #asud_details = get_named_asud(tokens[1])
                #asud_details = get_strat_provs_from_stratword(tokens[1])
            #asud_details = get_strat_provs_from_fullstratname(naf_gu_name)
            get_tidy_named_asud(naf_gu_name)
        # Write the data to the Excel spreadsheet
        # Starting by reproducing the first bit of the BoM's NAF spreadsheet
        #print(asud_details)

        for _, row in enumerate(asud_details):
            print(row)
        
        #print(asud_details)

        """print(row)
        for value in row:
            if type(value) is float:
                value = ''
            print(ws_row, ws_col, str(value))
            ws_col += 1
        print(ws_row, ws_col, naf_gu_name)
        ws_col += 1
        asud_col = ws_col
        for idx, asud_tuple in enumerate(asud_details):
            for item in asud_tuple:
                print(ws_row, asud_col, item)
                asud_col += 1
            asud_col = ws_col
            ws_row += 1"""

        """for value in row:
            if type(value) is float:
                value = ''
            worksheet.write(ws_row, ws_col, str(value))
            ws_col += 1
        worksheet.write(ws_row, ws_col, naf_gu_name)
        ws_col += 1
        asud_col = ws_col
        for idx, asud_tuple in enumerate(asud_details):
            for item in asud_tuple:
                worksheet.write(ws_row, asud_col, item)
                asud_col += 1
            asud_col = ws_col
            ws_row += 1
        #worksheet.write(ws_row, ws_col, str(asud_details))"""
    ws_row += 1

#workbook.close()
cur.close()
oracon.close()
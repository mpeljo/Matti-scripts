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

def get_provinces(stratno):
    # Uses the query behind the Geological Provinces component of the
    #   ASUD Stratigraphic Unit Details web page (eg unit 291)
    #   https://asud.ga.gov.au/search-stratigraphic-units/results/291
    query = """
            SELECT  p.eno, p.provname
            FROM    provs.prov_strats ps
            JOIN    provs.provinces p on (ps.eno = p.eno and p.pref = 'Y' and p.provtype <> 'georegion')
            WHERE   ps.stratno = {}""".format(stratno)
    cur.execute(query)
    result = cur.fetchall()
    return result

list_of_stratnos = [
    291,
    19267
]

for stratno in list_of_stratnos:
    print(get_provinces(stratno))

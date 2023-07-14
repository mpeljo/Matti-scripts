import os, shutil
import pandas as pd
import numpy as np
from openpyxl import Workbook, load_workbook

pd.set_option('display.max_columns', 50)

input_wb = r'C:\Users\u25834\OneDrive - Geoscience Australia\Desktop\Remediate_GW036853.3.3.jav.xlsx'
resultsfile = r'\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036853.3\Results\GW03685.3_350_09-Mar-2023\GW03685.3_350_09-Mar-2023_1Dvectors_uniform.txt'

ora_loaded_data = pd.read_excel(input_wb)
print(ora_loaded_data.head())

#ora_loaded_wb = load_workbook(filename=input_wb)
#ws = ora_loaded_wb.active

jav_results = pd.read_csv(resultsfile, delim_whitespace=True)
#print(jav_results.head())

counter = 0

for index, row in jav_results.iterrows():
    Ksdr = row['Ksdr']
    #print(Ksdr)     # numpy.float64
    #ora_row = ora_loaded_data[np.isclose(ora_loaded_data['VALUE'], Ksdr, 0.0000000001)]
    #ora_row = ora_loaded_data[ora_loaded_data['VALUE'] == np.float64(Ksdr)]
    #print(ora_row)
    ora_loaded_data.KEEPER = np.where(ora_loaded_data.VALUE.eq(Ksdr), 'Y', '')
print(ora_loaded_data.head(n=20))




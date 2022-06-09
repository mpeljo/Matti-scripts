# Developed using Python 3.7.3

import os
import numpy as np
import pandas as pd
from pandas.core.indexes import multi
import xlsxwriter

naf_file = r'\\prod.lan\active\data\sdl\Hydrogeology\NationalAquiferFramework_2016\NationalAquiferFramework.xlsx'
geol_1M_folder = r'C:\Users\u25834\Desktop\1M SurfGeol\Excel'
geometries = ['Line', 'Poly']
output_excel_file = r'C:\Users\u25834\Desktop\NAF_1Mgeol_check.xlsx'

# Read 1:1M geology attribute table
def get_geol_attr_df(filename, feature_type='Line', show_head=True):
    if not os.path.isfile(filename):
        print('Problem encountered with file: {}'.format(filename))
        print('Quitting...')
        quit()
    if feature_type not in geometries:
        print('Can\'t process features of type {}'.format(feature_type))
        print('Usable feature types are: ')
        for ftype in geometries:
            print('    {}'.format(ftype))
        quit()
    print('Reading 1:1M geology {} attributes...'.format(feature_type))
    print('from file {}'.format(filename))
    df = pd.read_excel(filename, usecols='A:F')
    print('Dropping {} rows with duplicate NAME...'.format(feature_type))
    df_dedup = df.drop_duplicates(subset='NAME')
    if show_head == True:
        print('First few rows of the geology dataframe:')
        print(df_dedup.head(), '\n')
    return df_dedup

def get_NAF_df(filename):
    if not os.path.isfile(filename):
        print('Problem encountered with file: ')
        print(filename)
        print('Quitting...')
        quit()
    # Read first few columns of Full_NAF worksheet into Pandas
    df = pd.read_excel(filename, sheet_name='Full_NAF', usecols='A:L', header=2)
    # First row contains duds so drop it
    df = df.drop([0])
    df.reset_index(inplace=True, drop=True)
    # Three columns are imported as Float, so convert back to Integer.
    #   Note that empty excel cells are now zeros
    for i in ('NafGAStratNumber', 'NafHGUNumber', 'NafHGCNumber'):
        df[i] = df[i].fillna(0)
    df = df.astype({'NafGAStratNumber': int, 'NafHGUNumber': int, 'NafHGCNumber': int})
    return df

def merge_dfs(NAF_df, geol_df):
    count = 0
    joined_df = NAF_df.merge(geol_df, how='left', left_on='NafGUName', right_on='NAME')
    joined_df.insert(0, 'NAF_Orig_RowNum', joined_df.index + 5)
    for idx, row in joined_df.iterrows():
        name = row['NAME']
        if name is not np.nan:
            count += 1
        else:
            joined_df = joined_df.drop(idx)
    
    return joined_df, count

def write_xlsx(outfile, df):
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    xl_sheet = 'NAF matches against 1M geol'
    df.to_excel(writer, sheet_name=xl_sheet)
    writer.save()


#-------------MAIN-------------------
multi_geom_df = pd.DataFrame(None)
naf_df = get_NAF_df(naf_file)

for geom in geometries:
    geol_1M_file = os.path.join(geol_1M_folder, '1MGeology{}s.xlsx'.format(geom))
    geol_df = get_geol_attr_df(geol_1M_file, geom, False)
    merged_df, nr_rows = merge_dfs(naf_df, geol_df)
    print('Number of matching rows from {} data: {}'.format(geom, nr_rows))
    print('Number of matching rows from {} data: {}'.format(geom, len(merged_df.index)))
    multi_geom_df = multi_geom_df.append(merged_df)
    multi_geom_df = multi_geom_df.drop_duplicates(subset='NAF_Orig_RowNum', keep='first')
    print(multi_geom_df.head())
    print('Number of rows remaining after merging line/poly datasets and dropping duplicates: {}'.format(len(multi_geom_df.index)))

# Prepare NAF dataframe to insert non-matching rows into output dataset
for idx, _ in multi_geom_df.iterrows():
    naf_df.drop(idx, axis=0, inplace=True)
naf_df.insert(0, 'NAF_Orig_RowNum', naf_df.index + 5)

multi_geom_df = multi_geom_df.append(naf_df, sort=False)
multi_geom_df.sort_values('NAF_Orig_RowNum', inplace=True)

print('Final size of dataframe, rows x cols: {}'.format(multi_geom_df.shape))

write_xlsx(output_excel_file, multi_geom_df)

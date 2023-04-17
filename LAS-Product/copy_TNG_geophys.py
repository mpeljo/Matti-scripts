import os
import lasio
from shutil import copyfile

data_folder = r'\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\neils-final\final'
tng_folder = r'\\prod.lan\active\proj\futurex\Common\Data\Products\ClientDataPackages\TNG_packageNov2021'

themes = ['gamma', 'induction']

for theme in themes:
    file_path = os.path.join(data_folder, theme)
    outfolder = os.path.join(tng_folder, theme)
    for root, _, files in os.walk(file_path):
        for name in files:
            inputfile = os.path.join(root, name)
            lasfile = lasio.read(inputfile)
            lat = lasfile.well.LATI.value
            lon = lasfile.well.LONGI.value
            if 131 < lon < 136 and -25 < lat < -19:
                outfile = os.path.join(outfolder, name)
                copyfile(inputfile, outfile)
                print ('Copied {}'.format(name))
    
    
    
    #print(file_path)

"""
# Add all ~Well information to dataframe
for root, _, files in os.walk(file_path):
    for name in files:
        inputfile = os.path.join(root, name)
        lasfile = lasio.read(inputfile)
        new_row = {'File': name}
        for header_item in lasfile.well.values():
            new_row[header_item.mnemonic] = header_item.value
        df = df.append(new_row, ignore_index=True)
        
print(df.head())

df.to_csv(csv_file)
"""
# Small script to create one zipfile per borehole,
# from multiple input files in a defined root folder.
#
# Requires all data files be named with the borehole name as the prefix. Example:
#   <boreholeName>_otherFileNameInfo 
#
# Python 3.7.3

import os
from zipfile import ZipFile
from os.path import basename

data_folder = r"\\prod.lan\active\proj\futurex\Common\Working\Neil\cleaned_las\final"
product_folder = r"\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\final_plus_extras\\"
extras_folder = r"\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\extras_for_zipfiles"

# Make list of "extra" files to incorporate into zipfile
extras = []
for root, dirs, files in os.walk(extras_folder):
    for name in files:
        if name not in extras:
            extras.append(os.path.join(root, name))

# Make dict with list of las files per bore
bores = {}
for root, dirs, files in os.walk(data_folder):
    for name in files:
        bore = name.split("_")[0]
        if bore not in bores:
            bores[bore] = [os.path.join(root, name)]
        else:
            bores[bore].append(os.path.join(root, name))

# Create zipfiles
for bore in bores:
    zipfilepath = product_folder + bore + '.zip'
    with ZipFile(zipfilepath, 'w') as myzip:
        for file in bores[bore]:
            myzip.write(file, basename(file))
        for file in extras:
            myzip.write(file, basename(file))

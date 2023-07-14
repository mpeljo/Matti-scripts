import os
import json
import requests

#from pprint import pprint
from api_client import GroundwaterDataLibraryAPI
import settings

api = GroundwaterDataLibraryAPI(
    'https://api.nonprod.groundwaterdatalibrary.ga.gov.au/gdl',
    'G55IXmb3qR5SlYDSgmm5n103wlil1vEN3q6aDqFa',
    '6b8tn1jodcb71nkfpqmuc3gbl1',
    '1jfflhsl87i5imbnupgqsg7oiqe7k7gtqbkuhqjle8vkhdac24c2',
)

def get_unique_datasets(list_of_gdl_datasets):
    dataset_hashes = []
    unique_datasets = []
    for dataset in list_of_gdl_datasets:
        hash_value = dataset['hash']
        if hash_value not in dataset_hashes:
            dataset_hashes.append(hash_value)
            unique_datasets.append(dataset)
        else:
            print('Duplicate dataset found: {}\t{}'.format(dataset['theme'], dataset['name']))

    return unique_datasets

# Make top level GDL root directory
if not os.path.exists(settings.SHADOW_ROOT_DIR):
    os.makedirs(settings.SHADOW_ROOT_DIR)

# Make top level OPS directory
if not os.path.exists(settings.SHADOW_OPS_DIR):
    os.makedirs(settings.SHADOW_OPS_DIR)

# First check which datasets exist in the GDL shadow copy
#gdl_shadowindex = functions.generate_shadow_index_file(settings.SHADOW_ROOT_DIR)


# Get datastore index and write to file
datastore_index_file = 'datastore_index.json'
datastore_index_path = os.path.join(settings.SHADOW_OPS_DIR, datastore_index_file)
datastore_index = api.get_datastore_index()

# Delete all but the first occurrence of each dataset (check the hashes)
datastore_index = get_unique_datasets(datastore_index)
with open(datastore_index_path, 'w') as f:
    json.dump(datastore_index, f, indent=4)

count = 0


#print(full_index)
for dataset in datastore_index:
    theme = dataset['theme']
    name = dataset['name'] + '.zip'
    url = dataset['url']

    themepath = os.path.join(settings.SHADOW_ROOT_DIR, theme)
    if not os.path.exists(themepath):
        print('Creating folder: {}'.format(themepath))
        os.makedirs(themepath)

    filepath = os.path.join(themepath, name)
    print(filepath)
    if os.path.exists(filepath):
        print('File exists: {}'.format(filepath))
    else:
        r = requests.get(url, stream=True)
        print('Retrieving dataset: {}'.format(filepath))
        with open(filepath, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    count += 1
    if count >= 10:
        break


import os
import json
import hashlib
import zipfile
import subprocess

def get_dataset_hash(dataset_path):
    pass

def unzip_to_toplevel_folder(zipped_file, theme, shadow_root_path):
    with zipfile.ZipFile(zipped_file) as zf:
        for member in zf.infolist():
            # get the subdir & file name parts
            subdirs = member.filename.replace(shadow_data_path.split('/')[-2] + '/', '').split('/')
            if len(subdirs) < 2:
                subdirs = member.filename.replace(shadow_data_path.split('/')[-2] + '\\', '').split('\\')

            #create subdirs, ignore last part as that's the file
            for subdir_part in subdirs[:-1]:
                if not os.path.exists(shadow_data_path + subdir_part):
                    os.makedirs(shadow_data_path + subdir_part)

            #extract all the members
            zf.extract(member, shadow_data_path)

            #move each member to its right place
            print shadow_data_path + '/'.join(subdirs)
            os.rename(shadow_data_path + member.filename, shadow_data_path + '/'.join(subdirs))        #
        pass

def download_and_unzip_dataset_to_shadow(session, datastore_dataset_register_uri, missing_dataset_id, datastore_index_file, shadow_root_dir):
    """
    Downloads and unzips a given zip file to its location within a Shadow Copy

    :param session: a session with a Data Store instance
    :param datastore_dataset_register_uri: the URI of the Data Store's dataset register
    :param missing_dataset_id: the URI of the dataset to download and unzip
    :param datastore_index_file: the simplified JSON index file for the Data Store
    :param shadow_root_dir: root directory of the Shadow copy
    :return: a string of the dataset_id
    """
    # get the dataset details
    dataset_details = ''
    for dataset in json.load(open(datastore_index_file))['datasets']:
        if dataset.get('id') == missing_dataset_id:
            dataset_details = {
                'id': missing_dataset_id,
                'data_path': dataset.get('data_path'),
                'folder_name': dataset.get('folder_name')
            }

    #create the path for this dataset, removing trailing slash from shadow_root_dir
    shadow_data_path =  os.path.join( shadow_root_dir, dataset_details.get('data_path') )
    if not os.path.exists(shadow_data_path):
        os.makedirs(shadow_data_path)

    #download the zip file to the data_path
    r = session.get(datastore_dataset_register_uri + missing_dataset_id + '?_view=download', stream=True, verify=False, )
    zip_file_and_path = os.path.join(shadow_data_path, dataset_details.get('id')) + '.zip'
    with open(zip_file_and_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            #filter out keep-alive new chunks
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()
    #unzip the zip
    subprocess.call([
        'unzip',
        zip_file_and_path,
        '-d',
        shadow_data_path
    ])

    # subprocess.call([
    #     '7z',
    #     'x',
    #     zip_file_and_path,
    #     '-o'+shadow_data_path
    # ])

    #move the zip file into the folder_name
    print "moving to: " + shadow_data_path + '/' + dataset_details.get('folder_name') + '/' + dataset_details.get('id') + '.zip'
    os.rename(zip_file_and_path,
              shadow_data_path + '/' + dataset_details.get('folder_name') + '/' +dataset_details.get('id') + '.zip')
    #unzip_to_toplevel_folder(zip_file_and_path, shadow_data_path)

    return missing_dataset_id

def calculate_zipfile_hash(zipped_file_path, blocksize=65536):
    hash = hashlib.sha1()
    if os.path.exists(zipped_file_path):
        with open(zipped_file_path, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()
    else:
        return ''

def generate_shadow_index_file(shadow_root_dir):

    pass



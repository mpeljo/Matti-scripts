import os
import json
import hashlib
import zipfile
import subprocess

import settings, functions

def unzip_to_toplevel_folder(zip_file_and_path, shadow_data_path):
    """
    Unzips a given zip file to its location within a Shadow copy

    Helper for download_and_unzip_dataset_to_shadow()

    :param zip_file_and_path: path to a dataset zip file within the Repository
    :param shadow_data_path: location for the unzipped files within the Shadow
    :return:  None (files will have been unzipped)
    """
    with zipfile.ZipFile(zip_file_and_path) as zf:
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
            print(shadow_data_path + '/'.join(subdirs))
            os.rename(shadow_data_path + member.filename, shadow_data_path + '/'.join(subdirs))

def overwritezipfile(zipfilepathfolder, hash):
    #overwrite the existing .zip file with a text file of the same name containing the dataset hash
    try:
        file = open(zipfilepathfolder,'w+')
        file.write(hash)
        file.close()
    except:
        print('Couldnt overwight existing .zip file - Skipping')
        return False
    return True

def check_zip_file(zip_file_path):
    # Extract the directory name from the zip file path
    zip_dirname = os.path.splitext(os.path.basename(zip_file_path))[0]
    
    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_info = {
            'file_list':  [],
            'folder_count':   0,
            'zipped_folder_name': '',
        }
        # Get the list of all files and folders in the zip file
        file_list = zip_ref.namelist()
        zip_info['file_list'] = file_list
        
        # Check if there is only one folder in the zip file
        folder_count = sum(1 for file in file_list if file.endswith('/'))
        zip_info['folder_count'] = folder_count
        if folder_count != 1:
            pass
            #return False, zip_info
        
        # Get the name of the zipped folder
        #zipped_folder = os.path.commonprefix(file_list)
        zipped_folder = os.path.commonpath(file_list)
        print('Common path: {}'.format(zipped_folder))
        zipped_folder = zipped_folder.rstrip('/')
        zip_info['zipped_folder_name'] = zipped_folder
        
        # Check if the zipped folder has the same name as the zip file
        if zipped_folder != zip_dirname:
            return False, zip_info
        
    return True, zip_info

test_zipfile = 'Sweet chilli chicken and lime stir.docx.zip'
#test_zipfile = 'test_text_doc.txt'
test_theme = r'Climate'
gdl_folder = settings.SHADOW_ROOT_DIR
dataset_info = {
    'Dataset_Name': 'Sweet chilli chicken and lime stir.docx',
    'Identifier': '85a437e3-698b-4b49-a304-825dab204f2f',
    'Dataset_Hash': '63aa2586f0a982f5d0ad34ae1ab909c62173e684',
}

"""
test_theme = r'BoreHoles\Geothermal'
gdl_folder = settings.SHADOW_ROOT_DIR
test_zipfile = 'loop_creator_v0.1.5.zip'
"""
"""
test_theme = r'BoreHoles\CSG'
gdl_folder = settings.SHADOW_ROOT_DIR
test_zipfile = '__coverage__.zip'
"""
themepath = os.path.join(gdl_folder, test_theme)
full_testzip_path = os.path.join(themepath, test_zipfile)

line = ''
if os.path.exists(full_testzip_path):
    print('Path exists: {}'.format(full_testzip_path))
    with open(full_testzip_path) as f:
        try:
            print(f.readable())
        except:
            print('Could not open and read new .zip file - manually check and fix!')
    
    result, zipfile_info = check_zip_file(full_testzip_path)
    if result:
        print("The zip file meets the requirements.")
    else:
        print("The zip file does not meet the requirements.")

    """with zipfile.ZipFile(full_testzip_path, 'r') as zf:
        info = zf.infolist()
        top = {item.split('/')[0] for item in zf.namelist()}    # Get set of all items in the zip's top level
        print(len(top), top)"""
        #candidate_folder = ''
        #for zip in info:
            #print(zip.filename)
            #filename_parts = zip.filename.split('/')
            #print(filename_parts[0])
            #print(zip)
            
    #zfi = zipfile.ZipInfo.from_file(full_testzip_path)
    #print(zfi.is_dir())
    """with zipfile.ZipFile(full_testzip_path, 'r') as zf:
        print(zf.printdir())
        zf.extractall(path=themepath)"""
        
        

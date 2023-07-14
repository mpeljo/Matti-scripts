import os, hashlib

sync_path = r'\\prod.lan\active\data\sdl\gdl_test\sync'

files = [
    'GA Strategy 2028 Update_FA2.zip',
    'groundwater-data-library-api.zip',
    'loop_creator_v0.1.5.zip',
]

def sha1sum(filename, blocksize=65536):
    hash = hashlib.sha1()
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(blocksize)
                if not data:
                    break
                hash.update(data)
        return hash.hexdigest()
    else:
        return ''

for file in files:
    data_file = os.path.join(sync_path, file)
    print(file)
    hash_value = sha1sum(data_file)
    print(file, hash_value)
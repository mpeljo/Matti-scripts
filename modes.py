#!/usr/bin/env python
#title           :modes.py
#description     :Counts the number of occurrences of each Unix file mode in a
#                   folder. Recursively descends into all directories.
#author          :Matti Peljo
#date            :20160817
#version         :0.1
#usage           :python modes.py <directory location>
#notes           :Imports "collections" to use Counter, which is not available
#                   in Python 2.6.6 on rhe-gatr-prod01. Here, collections.py
#                   is kept in a directory next to modes.py called py27.
#python_version  :2.6.6  
#==============================================================================

import os
import stat
import sys
from py27.collections import Counter

excludes = (".snapshot", "test")    # .snapshot for Linux filesystem

walk_dir = sys.argv[1]

print('walk_dir = ' + walk_dir)
print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

c = Counter()

for root, subdirs, files in os.walk(walk_dir):
    subdirs[:] = [d for d in subdirs if d not in excludes]
    #print('--\nroot = ' + root)
    list_file_path = os.path.join(root, 'my-directory-list.txt')
    #print('list_file_path = ' + list_file_path)

    #with open(list_file_path, 'wb') as list_file:
    #for subdir in subdirs:
    #    print('\t- subdirectory ' + subdir)

    for filename in files:
        file_path = os.path.join(root, filename)
        filemode = oct(stat.S_IMODE(os.stat(file_path).st_mode))
        
        c[filemode] += 1
        
print c

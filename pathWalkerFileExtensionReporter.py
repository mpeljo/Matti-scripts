# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 15:42:49 2015

@author: u70587     Duncan Moore
"""
import os, time
startTime = time.time()
userList = []
tailList = []

ws = r"\\nas\gemd\georisk\HaRIA_C_Coastal\Projects\BNHCRC"
extension = r"\\nas\gemd\georisk\HaRIA_C_Coastal\Projects\BNHCRC\Data_Management\extension.csv"
#
try:
    os.remove(extension)
    print "\nCSV exists and has been deleted: " + extension
    print "\tCreating new mxdsProcessedCSV file"
    fh = open(extension,"w")
    fh.write("Extension, Enter into data log?\n")
    fh.close()
    print "\tExtensions CSV file created: " + extension + "\n"

except:
    print "\nCreating new CSV file"
    fh = open(extension,"w")
    fh.write("Extension, Enter into data log?\n")
    fh.close()
    print "\tExtensions CSV file created: " + extension + "\n"

count = 0
if not os.path.exists(ws):
    print ws + ' does not exist'

for folder, subs, files in os.walk(ws):
    for f in files:
        print f
        tail = os.path.splitext(f)[1]
        print '\tTail: ' + tail.lower()
        if tail.lower() not in tailList:
            tailList.append(tail.lower())
            fh = open(extension,"a")
            fh.write(tail.lower() + '\n')
            fh.close()
        count += 1
        print '\t' + str(count)

#    if os.path.isdir(folder):
#        print folder
#        statinfo = os.stat(folder)
##        fh = open(extension,"a")
##        fh.write(folder + ',' + str(os.stat(folder).st_uid) + '\n')
##        fh.close()
#        print statinfo
#        if os.stat(folder).st_uid not in userList:
#            userList.append(os.stat(folder).st_uid)
#        count += 1
#        print '\t' + str(count)


print '\nTotal folders:' + str(count)
#        os.stat(folder)
#        print stat.ST_UID
for tail in tailList:
    print tail

#for user in userList:
#    print user
print "\n"
# figure out how long the script took to run
stopTime = time.time()
sec = stopTime - startTime
days = int(sec / 86400)
sec -= 86400*days
hrs = int(sec / 3600)
sec -= 3600*hrs
mins = int(sec / 60)
sec -= 60*mins
print 'The script took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'

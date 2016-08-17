# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 15:42:49 2015

@author: u70587     Duncan Moore
"""
import os, time, string
startTime = time.time()
userList = []
tailList = []

ws = r"/nas/gemd/georisk/HaRIA_C_Coastal/Projects/BNHCRC"
extensionList = ['.shp','.xlsx','.las','.xls','.mxd','.docx','.pdf','.doc','.pptx,','.xls', '.msg', '.txt', '.lyr', '.csv', '.7z', '.kml', '.nc', '.tgz',
                 '.kmz', 'ecw', '.dxf', '.xyz', '.las', '.dwg', '.asc', '.jpg', '.tif', '.ovr', '.tif', '.xml', '.fl', '.sgy' ,'.vm', '.bmp', '.ai', '.enl'
                 '.zip', '.html', '.mrk', '.rad', '.rd3', '.add', '.em', '.cor', '.aux', '.rrd']
dataLog = r"/nas/gemd/georisk/HaRIA_C_Coastal/Projects/BNHCRC/Data_Management/dataLog.csv"
gridFileMemory = []
users = {0:'Unknown',30485:'Jane Sexton', 30223:'Duncan Moore', 7613:'Scott Nichol', 7162:'Andrew McPhersion', 8663:'Floyd Howard', 8676:'Wenping Jiang', 8824:'Kathryn Owen', 8347:'Gareth Davies', 7343:'Craig Arthur'}

try:
    os.remove(dataLog)
    print "\nCSV exists and has been deleted: " + dataLog
    print "\tCreating new dataLog file"
    fh = open(dataLog,"w")
    fh.write("Date received, File, Location, Data received by, Organisation received from, Person received from, Data Licence (rules for use and distribution)\n")
    fh.close()
    print "\tdataLog CSV file created: " + dataLog + "\n"

except:
    print "\nCreating new CSV file"
    fh = open(dataLog,"w")
    fh.write("Date received, File, Location, Data received by, Organisation received from, Person received from, Data Licence (rules for use and distribution)\n")
    fh.close()
    print "\tdataLog CSV file created: " + dataLog + "\n"

count = 0
if not os.path.exists(ws):
    print ws + ' does not exist'

for folder, subs, files in os.walk(ws):
    if os.path.isdir(folder) and folder.endswith('.gdb'):
        print folder
        cTime = os.path.getctime(folder)
        print cTime
        isoTime = time.strftime("%d-%m-%Y", time.localtime(cTime))
        print isoTime
        fh = open(dataLog,"a")
        winPath = string.replace(folder,os.path.sep,'\\\\',1)
        print winPath
##        winPath = string.replace(winPath, '~','\\\\',1)
##        print string.replace(winPath, '~','\\')
        fh.write(isoTime + ',' + string.replace(winPath, os.path.sep,'\\') + ',' + users[os.stat(folder).st_uid] + ',,,' + '\n')
        fh.close()
#        if os.stat(folder).st_uid not in userList:
#            userList.append(os.stat(folder).st_uid)
        count += 1
    for f in files:
        print f
        tail = os.path.splitext(f)[1]
        print '\tTail: ' + tail.lower()
        if tail.lower() in extensionList:
            cTime = os.path.getctime(os.path.join(folder,f))
            isoTime = time.strftime("%d-%m-%Y", time.localtime(cTime))
            fh = open(dataLog,"a")
            winPath = string.replace(folder,os.path.sep,'\\\\',1)
##            print winPath
##            winPath = string.replace(winPath, '~','\\\\',1)
##            print string.replace(winPath, '~','\\')
            fh.write(isoTime + ',' + f + ',' + string.replace(winPath, os.path.sep,'\\') + ',' + users[os.stat(os.path.join(folder,f)).st_uid] + ',,,' + '\n')
            fh.close()
        if tail.lower().endswith('adf') and folder.lower() not in gridFileMemory:
            cTime = os.path.getctime(folder)
            isoTime = time.strftime("%d-%m-%Y", time.localtime(cTime))
            fh = open(dataLog,"a")
##            winPath = string.replace(folder,os.path.sep,'~')
##            print winPath
            winPath = string.replace(folder, os.path.sep,'\\\\',1)
##            print string.replace(winPath, '~','\\')
            fh.write(isoTime + ',' + string.replace(winPath, os.path.sep,'\\') + ',,' + users[os.stat(folder).st_uid] + ',,,' + '\n')
            fh.close()
            gridFileMemory.append(folder.lower())
        if tail.lower().endswith('dbf') and not os.path.exists(os.path.join(folder,f.split('.')[0] + '.shp')):
            cTime = os.path.getctime(os.path.join(folder,f))
            isoTime = time.strftime("%d-%m-%Y", time.localtime(cTime))
            fh = open(dataLog,"a")
            winPath = string.replace(folder, os.path.sep,'\\\\',1)
            fh.write(isoTime + ',' + f + ','  + string.replace(winPath, os.path.sep,'\\') + ',,' + users[os.stat(folder).st_uid] + ',,,' + '\n')
            fh.close()


        count += 1
        print '\tFiles processd: ' + str(count)

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

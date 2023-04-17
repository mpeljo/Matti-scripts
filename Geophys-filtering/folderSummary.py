#!/bin/sh python
#===============================================================================
# Author: Duncan Moore
# Date: 5 November 2014
# Purpose: To summarise the files in the inputFolder by their last access or modified time.  
#                    
#          The time of access/modification is determined from the current time, i.e. if the 
#          difference between the current time and the file's access/modify time is less
#          than 24 hours it is classed into the 'Files accessed in the last 24 
#          hours' class. 
#          This does not align with the files accessed today as the date change at
#          midnight is not considered in this script. 
#          
#          There is a list produced of all the folder paths not included in the summary
#          as the user specifies the folder names to be excluded and this name
#          could potentially be embedded in the folder tree elsewhere to the user's  
#          knowledge. 
#          
#          User to specify the folders to be excluded in the top folder 'inputFolder' 
#          (line 41), the 'exclude' list (line 47), the 'destinationFolder' to store 
#          the outputs (line 49 - csv file of the results - also printed to screen, 
#          metadata file and the script used) and the time type (line 53 -last access  
#          or modification). A date stamped, and sequentially numbered if the date exists, 
#          named folder is created for the outputs in the 'destinationFolder'.
#          
#          The metadata file contains a record of the script inputs and the output 
#          messages (excluded paths and errors).
#
#                       
#===============================================================================

import sys, os, time, shutil, getpass, csv
import numpy as np
import matplotlib.pyplot as plt

import win32com.client as com
from decimal import *
from Tkinter import Tk
from tkFileDialog import askdirectory
getcontext().prec = 6

fig, ax = plt.subplots()

# Define some constants
KiB = 1024
MiB = KiB * KiB
GiB = MiB * KiB

labels = ('Today', 'Yesterday', '1 - 7 days', '8 - 30 days',
            '31 - 90 days', '91 - 180 days', '181 - 365 days',
            '1 - 2 years', '2 - 3 years', '3 - 5 years',
            '6 - 10 years', 'Over 10 years')


# Functions -----------------------------------------------------------

def getUserInputs(askForInput):
    if askForInput == 'n':         # Use hard-coded inputs
        inputFolder = 'C:\Users\u25834\Desktop'
        exclude = ''
        destinationFolder = '.'
        timeType = 'A'
        showResults = True
        return inputFolder, exclude, destinationFolder, timeType, showResults
    else:
        ###############################################
        ## User to specify the inputFolder for the highest level folder to be considered.
        dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = True
        options['title'] = 'Select the folder to analyse'
        Tk().withdraw()
        inputFolder = askdirectory(**dir_opt)
            
        ## Exclude: folders (folders to be identified by the user in single or double quotes separated by commas, 
        ## e.g. exclude = ['newFolder', 'data']'''. This input is sought at the command line or from the Python Shell
        #exclude = raw_input("Enter folders (name only, not full path) to be excluded separated by a comma (enter for no exclusions): ")
        exclude = '~snapshot'
        
        ## Outputs
        options['title'] = 'Select the folder to write results to:'
        destinationFolder = askdirectory(**dir_opt)
        #destinationFolder = raw_input('Enter the output folder (date labelled sub-folder will be created): ')
        #while not destinationFolder:                            # Test to make sure an input was provided
         #   print 'No output folder provided...'
         #   destinationFolder = raw_input('\tEnter the output folder (date labelled sub-folder will be created): ')
        
        ## Accessed or Modified timestamps to be analysed
        timeType = 'A'                                          # Hard-coded for now
        #timeType = raw_input('Accessed or Modified time? (A/M): ')
        while timeType not in ('a', 'A', 'm', 'M'):             # Test to make sure a correct input was provided
            print '\tAccessed or Modified time incorrectly entered...'    
            timeType = raw_input('\tAccessed or Modified time? (A/M): ')
            
        ## Display the results in the python window?
        showResults = False
        displayResultsYN = raw_input('Show the data in the python window? (Y/N): ')
        while displayResultsYN not in('y', 'Y', 'n', 'N'):
            print '\tYour response must be Y or N'
            displayResultsYN = raw_input('Show the data in the python window? (Y/N): ')
        if displayResultsYN in ('y', 'Y'):
            showResults = True
        
        return inputFolder, exclude, destinationFolder, timeType, showResults

def showRunTime(appStartTime):
    '''Print out how long the script took to run'''
    stopTime = time.time()
    sec = stopTime - appStartTime
    days = int(sec / 86400)
    sec -= 86400*days
    hrs = int(sec / 3600)
    sec -= 3600*hrs
    mins = int(sec / 60)
    sec -= 60*mins
    print 'The script took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'
                
def autolabel(rects, units):
    # attach some text labels
    for rect in rects:
        width = rect.get_width()
        ax.text(width/2, rect.get_y() + rect.get_height()/2., '%d'%int(width) + ' ' + units,
                ha='left', va='center')
    
def createChart(sizeList, countList):
    maxSize = max(sizeList)     # Size of largest list item, in bytes
    
    # Set size unit range
    if (maxSize  < KiB):
        units = 'Bytes'
        factor = 1
    elif (maxSize < MiB):
        units = 'KB'
        factor = KiB
    elif (maxSize < GiB):
        units = 'MB'
        factor = MiB
    else:
        units = 'GB'
        factor = GiB
    
    # Create new list that is normalised against the maximum size
    normList = sizeList
    for i, val in enumerate(normList):
        normList[i] = normList[i] / factor
    
    '''
    # Create the chart
    y_pos = np.arange(len(sizeList))
    rects1 = plt.barh(y_pos, normList, align='center', alpha=0.2)
    plt.yticks(y_pos, labels)
    
    autolabel(rects1, units)'''
    
    # Create the chart
    y_pos = np.arange(len(countList))
    rects1 = plt.barh(y_pos, countList, align='center', alpha=0.2)
    plt.yticks(y_pos, labels)
    plt.title('File count') 
    
    autolabel(rects1, 'files')

    plt.show()

def readData(fName):
    with open(fName, 'r') as f:
        reader = csv.reader(f)
        csvSizeList = []
        csvCountList = []
        i = 0
        try:
            iterRows = iter(reader)
            next(iterRows)              # Skip header row
            for row in iterRows:
                csvSizeList.append(int(row[1]))
                csvCountList.append(int(row[3]))
            return csvSizeList, csvCountList
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

def writeData(fName, sizeList, countList, labels, folder):
    ''' Create the destination folder
    os.makedirs(destinationFolder) 
    print "Dated destination folder:\n\t" + destinationFolder 
    
    #Copy the python file being run to the destination folder to keep a copy of the script with the outputs
#    shutil.copy2(sys.argv[0], destinationFolder)
#    print "\t\t" + os.path.split(sys.argv[0])[-1] + " created"
    
    #Create the metadata file and populate it
    pf = open(processedFile,"w")
    pf.write("Automated metadata report\n")    
    pf.write("Script run at: " + iso_time + "\n")
    pf.write("Script run by: " + getpass.getuser() + "\n")
    pf.write("Python script: ") 
    pf.write(os.path.split(sys.argv[0])[-1])
    pf.write(" run from: \n\t" + sys.argv[0])
    pf.write("\n\tOpen the .py file (Python IDE or text editor) and review the comments for lineage details")
    pf.write("\n\nOutputs created in: " + destinationFolder + "\n")
    pf.write("\t" + os.path.split(sys.argv[0])[-1] + " saved\n")
    pf.write('\t\tInputs:\n')
    pf.write('\t\t\tinputFolder: ' + inputFolder + '\n')
    pf.write('\t\t\texcludedFolders: ' + exclude + '\n')
    pf.write('\t\t\tdestinationFolder: ' + destinationFolder + '\n')
    pf.write('\t\t\touputCSV: ' + outputCSV + '\n')
    if timeType == 'a' or timeType == 'A':    
        pf.write('\t\t\ttimeType: ' + timeType + ' (Accessed time)\n')
    else:
        pf.write('\t\t\ttimeType: ' + timeType + ' (Modified time)\n')
    pf.close()
    print "\t\tMetadata file created"
    
    print 'Inputs provided...'
    # Create the output CSV named as a function of the CSV's purpose
    if timeType == 'A' or timeType == 'a':
        outputCSV = 'accessed.csv'
    elif timeType == 'M' or timeType == 'm':
        outputCSV = 'modified.csv'
    
    print '\t' + outputCSV + ' will be created in ' + destinationFolder + '\n'
    '''
    
    writeFile = folder + '//' + fName
    with open(writeFile, 'wb') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["Accessed","size (bytes)","Proportion by size (%)","file count"]) # Headers. To do: accessed vs modified
        totalSize = sum(sizeList)
        for label, size, count in zip(labels, sizeList, countList):
            percentSize = str(("%.2f" % (Decimal(size)/Decimal(totalSize)*100)))
            csvwriter.writerow([str(label), str(size), percentSize, str(count)])
            
        '''
        

    # Identify tuple time and reformat to iso time
    tuple_time = time.localtime()
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", tuple_time)
        
    # Create a non-existent, numbered date file name to capture multiple processing runs on the same day
    ext = 0
    while os.path.exists(destinationFolder + os.sep + time.strftime("%Y-%m-%d", tuple_time) + "_v" + str(ext)):
        ext = ext + 1

    # Set the path to the destinationFolder and the processedFile
    destinationFolder = os.path.join(destinationFolder, time.strftime("%Y-%m-%d", tuple_time) + "_v" + str(ext))
    processedFile = os.path.join(destinationFolder,'metadata.txt')
    
    # Write the output messages to the processedFile (metadata file)
    pf = open(processedFile,"a")
    pf.write("\nOuput messages:\n")    
    print '\nFolders excluded from the summary:'
    if len(excludePaths) == 0:
        print '\tNo folders excluded'
        pf.write("\tExcluded paths: \n\t\tno paths excluded\n")
    else:
        pf.write("\tExcluded paths:\n")  
        for path in excludePaths:
            pf.write("\t\t" + path + '\n')  
            print '\t' + path
    # Write the error messages to the processedFile (metadata file)           
    print '\nError report (file size not counted and file not counted into date classes):'
    if len(errors) == 0:
        pf.write("\tErrors: \n\t\tno errors recorded\n")
        print '\tNo errors recorded'
    else:
        pf.write("\tErrors:\n") 
        for keys, values in errors.items():
            # Print is switched as files had to be the dict key otherwise multiple errors in a single folder 
            # with the folder being the key, would not store all the errors.
            pf.write("\t\t" + values + '\\' + keys + '\n')             
            print '\t' + values + '\\' + keys
    pf.close()
    '''

def printResults(sizeList, countList, labels):
    print "       Accessed,  size (bytes)  ,  Proportion by size (%), file count" # Headers. To do: accessed vs modified
    totalSize = sum(sizeList)
    for label, size, count in zip(labels, sizeList, countList):
        percentSize = ("%.2f" % (Decimal(size)/Decimal(totalSize)*100))
        print '%15s, %15s, %5s, %s' % (label, size, percentSize, count)
            
def analyseFolder(inputFolder, excludeList, timeType):

    #    sizeList = [sizeToday 0, sizeYesterday 1, size3_7 2, size8_30 3, size31_90 4, size91_180 5, size181_365 6,
    #                size366_730 7, size731_1095 8, size1096_1825 9, size1826_3650 10, sizeGT3649 11]
    #    countList = [countToday, countYesterday, count3_7, count8_30, count31_90, count91_180,
    #                count181_365, count366_730, count731_1095, count1096_1825, count1826_3650, countGT3649]
    
    # Calculate the size of the top folder, prepare progress counter
    progressCountDisplay = True                 # Initialise
    try:
        print inputFolder
        fso = com.Dispatch("Scripting.FileSystemObject")
        folder = fso.GetFolder(inputFolder)
        folderSize = folder.size
        if folderSize < MiB:
            print '\tInput folder size: ' + ''"%i KB"%(folderSize/KiB/1.0)
        elif folderSize < GiB:
            print '\tInput folder size: ' + ''"%i MB"%(folderSize/MiB)
        else:
            print  '\tInput folder size: ' + ''"%i GB"%(folderSize/GiB)
    except:
        '\t*****' + inputFolder + ' folder size was not returned*****'
        print '\t*****Script progress will not be reported*****'
        progressCountDisplay = False
    

    sizeList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    countList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    runningCount    = 0
    totalSize       = 0
    #theTime     = time.time()   # Get the current time to compare with file stats
    progressCountDisplay        = True
    errorCount      = 0
    
    # Create list used to report progress concisely, i.e. at the listed intervals
    progressPoint = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100)

    # Set each of the lists as variables and their value to False
    for p in progressPoint:
        globals()[p] = False
    
    # Topdown needs to remain True for the subs[:] slice to work
    print '\nIterating through folders and files...'    
    for folder, subs, files in os.walk(inputFolder, topdown=True):
        for sub in subs:
            if sub in exclude:
                excludePaths.append(os.path.join(folder,sub))

        subs[:] = [d for d in subs if d not in exclude]
        
        for f in files:
            try:
                fullpath = os.path.join(folder,f)
                size = os.path.getsize(fullpath)
                #print fullpath
                runningCount += 1
                totalSize += size
                
                if timeType == 'a' or timeType == 'A':                
                    deltaTime = theTime - os.path.getatime(fullpath)
                    timeString = 'accessed'
                elif timeType == 'm' or timeType == 'M':
                    deltaTime = theTime - os.path.getmtime(fullpath)
                    timeString = 'modified'
                     
                if deltaTime/86400 < 1:         # Today
                    sizeList[0] += size
                    countList[0] += 1
                elif deltaTime/86400<2:         # Yesterday
                    sizeList[1] += size
                    countList[1] += 1
                elif deltaTime/86400<7:         # 3 - 7 days
                    sizeList[2] += size
                    countList[2] += 1
                elif deltaTime/86400<30:        # 8 - 30 days
                    sizeList[3] += size
                    countList[3] += 1
                elif deltaTime/86400<90:        # 31 - 90 days
                    sizeList[4] += size
                    countList[4] += 1
                elif deltaTime/86400<180:       # 91 - 180 days
                    sizeList[5] += size
                    countList[5] += 1
                elif deltaTime/86400<365:       # 181 - 365 days
                    sizeList[6] += size
                    countList[6] += 1
                elif deltaTime/86400<730:       # 1 - 2 years
                    sizeList[7] += size
                    countList[7] += 1
                elif deltaTime/86400<1095:      # 2 - 3 years
                    sizeList[8] += size
                    countList[8] += 1
                elif deltaTime/86400<1825:      # 3 - 5 years
                    sizeList[9] += size
                    countList[9] += 1
                elif deltaTime/86400<3650:      # 5 - 10 years
                    sizeList[10] += size
                    countList[10] += 1
                elif deltaTime/86400>3649:      # Over 10 years
                    sizeList[11] += size
                    countList[11] += 1
                else:
                    print fullPath + ' not captured in time classes, script requires revision'
                '''
                # Progress reporting, try win32.com comparison else do a modulo, i.e. count / 1000000000
                # with no remainder, reporting                                
                if progressCountDisplay == True:
                    print  totalSize, ' ', folderSize
                    try:
                        percentProgress = "%.2f" % (Decimal(totalSize)/Decimal(folderSize)*100)
                        for point in progressPoint:
                            if percentProgress > point and globals()[point] == False:
                                print '\t' + str(point) + '% processed'
                                globals()[point] = True

                    except Exception:
                        continue 
                elif progressCountDisplay == False and 100000000%runningCount == 0 and runningCount > 100:'''
                print '\t' + str(runningCount) + ' files processed'
                
            except:
                errors[f] = folder
                errorCount += 1
                
            totalCount = sum(countList)
            totalSize = sum(sizeList)
    print '\t\t\t\t\t\tSum size: ' + str("%.2f" % (Decimal(totalSize)/Decimal(MiB))) + ' MB\t\tSum file count: ' + str(totalCount + errorCount) + ' (' + str(errorCount) + ' errors included)'
                

    return sizeList, countList, errorCount



# Mainline -----------------------------------------------------------

# Initialise some variables
excludePaths    = []                # List of paths to exclude from analysis 
errors          = {}                # Errors dictionary

# Get input and output details
inputFolder, exclude, destinationFolder, timeType, showResults = getUserInputs('y')

theTime         = time.time()       # Get the current time to compare with file stats
                                    # and to calculate run time.

# Read existing data file
#sizeList, countList = readData('accessed.csv')

# Or... analyse folder and create a new data file
sizeList, countList, errs = analyseFolder(inputFolder, exclude, timeType)

# Write new file
writeData("testFile.csv", sizeList, countList, labels, destinationFolder)

# Print data
if showResults == True:
    printResults(sizeList, countList, labels)

showRunTime(theTime)

createChart(sizeList, countList)

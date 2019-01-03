# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 13:09:24 2018

@author: Joseph Bell
Converts a large RINEX file into daily RINEX files for processing in AUSPOS

AUSPOS has a limit of 7 days but it was recommented that the input files only be 1 day long.
May have errors but seemed to be working as planned.
Check all your outputs make sense.

"""

import shutil   # for copy of files to another folder

import os   # operating system tools 

# blank list to hole the list of RINEX files
rinexFiles = list()


# saved working folders
startfolder = r'\\xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\DGPS\DGPS_data\2016 DGPS Ord data RINEX'


# this is the extension the script will look for - it will look for these files in all subfolders below the startfolder
default_ext = '.17o'  # change to suit the year data you have

# make a folder for the output
outFld = startfolder + '/all_daily/'

# check if the output folder exists - if not then make it
if not os.path.exists(outFld):
    os.makedirs(outFld)


'''
Below are the functions the script can call (not all are used at the moment)
def means function
'''

#convert 01 numbers into just 1 (for search RINEX dates)
def singleDigitConvert(myNum):
    if myNum[0] == '0':
        myNum = ' ' + myNum[1]
    return myNum

def collect_dates(rinex):
    theseDates = list()
    for line in rinex:
        if '0.000000' in line:
            if not line.startswith('  '):
                theseDates.append(line)
    return theseDates

def is_line_a_date(line):
    is_dateLine = False
    if '0.000000' in line:
        if not line.startswith('  '):
            is_dateLine = True 
    return is_dateLine


def write_list_to_file(theseDayFile, filename):
    """Write the list to csv file."""

    with open(filename, "w") as outfile:
        for entries in theseDayFile:
            outfile.write(entries)
            #outfile.write("\n")
            
def toHead_Date(line):
    ''' 
    Converts a line date into head date format
    '''
    # gather year , month, day, Hour and second
    myYear = line[1:4]
    myYear = (myYear.strip())
    
    myMonth = line[3:6]
    myMonth = myMonth.strip()
    # justify to the right 
    myMonth = myMonth.rjust(6, " ")

    myDay = line[6:9]
    myDay = myDay.strip()
    myDay = myDay.rjust(6, " ")
    
    myHour = line[9:12]
    myHour = myHour.strip()
    myHour = myHour.rjust(6, " ")
    
    myMins = line[12:15]
    myMins = myMins.strip()
    myMins = myMins.rjust(6, " ")
    
    mySecs = line[15:26]
    mySecs = mySecs.strip()
    mySecsFloat = float(mySecs)
    if mySecsFloat < 5:
        myPad = "    "
    else:
        myPad = "   "


    myYear = '  20' + myYear + myMonth + myDay  + myHour + myMins +  myPad + mySecs
    

    #print myDate
    return myYear

   
    
    
def get_the_day(line):
    ''' 
    Finds the day from a time (out of a line that refers to a date/time)
    '''

    # read the line and extract the 'day' portion
    myDay = line[6:9] 
    myDay = myDay.strip()  # repove and empty spaces
    
    # send the answer back
    return myDay   
    
# this id the starting numer for the output file prefix
fileNo = 0

# look through the startfolder and subfolders and make a list of all files in there
for folder, subs, files in os.walk(startfolder):

    for fl in files:
        # only consider files that have the correct extension - see default_ext variable
        if fl.endswith(default_ext):
            # make a full path by prefixing the folder name
            fullPath = folder + '/' + fl
            # print fullPath
            
            # exclude the all_daily folder because that is output files
            if 'all_daily' not in fullPath:
                # only  files bigger than a day in size
                # print fullPath
                # find size of this file - 2 steps
                statinfo = os.stat(fullPath)
                size = statinfo.st_size
                #print size
                if  size  > 8000000:  # only include files > 8000 kb = 8MB ie more than one day
                    # print fullPath
                    rinexFiles.append(fullPath)
                else:
                # if less than 8MB then simply copy to the outfolder with the file number prefixed
                    # try:
                    #copy the file to the all_daily folder
                    shutil.copy(fullPath, (outFld + str(fileNo) + '_'+ fl))
                    fileNo += 1
#                    except:
#                        # when the file is already in the folder (don't know why)
#                        pass


# print the number of files found
print 'Number of files > 8MB found= ' + str(len(rinexFiles))


# make a couple of lists to use further down
minDates = list()
maxDates = list()


# go through the list of RINEX files we have identified and process them
# at this stage they will be simply saved into an other list without updating their dates.
# updating header dates is in the next stage
for f in rinexFiles:
    # delete any old header files
    headerFile = list()
    thisFile = ''
    # find file name
    thisFile = os.path.basename(f)
#     remove the extension from the file
#    thisFile = thisFile[:-4]
    #lines = tuple(open(rin, 'r'))
    lines = tuple(open(f, 'r'))
    
    #make a list with the header file
    # some times the header is shorter or longer - look for 'END OF HEADER' 
         
    # read one by one, up to 120 lines and save the header
    for y in range(120):
        #print lines[y],
        headerFile.append(lines[y])
        # stop when the line with END OF HEADER comes up
        if "END OF HEADER" in lines[y]:
            break
        
    # now header is saved
  
    # this is a list for all the days
    theseDays = list()
    
    # this is a list for one day
    thisDay_data = list()
    
    
    lastDay = -9999 
 
    for item in lines:

        # if line is a date - many in each day
        if is_line_a_date(item):
            # get the day
            thisDay = get_the_day(item)
            
            # compare to see if new day
            if lastDay != thisDay:
                print 'New Day ' + str(lastDay) + '   ' + str(thisDay)
                # save the previous days data as an item in the thesedays list
                theseDays.append(thisDay_data)
                
                # and clear the data to start a new day
                thisDay_data = list() 
                
                # in the new day the first thing is to add the header
                for aline in headerFile:
                    thisDay_data.append(aline)
                    
                # we still have a single line in memory that belongs to the new day
                # we add it on after the header
                thisDay_data.append(item)
            
            # else (if not a new day) just append the data
            else:
                thisDay_data.append(item)
                
               
            # and remember the day for the next cycle
            lastDay = thisDay
        
        # if not a date line - just append the line to that day
        else:
            
            # append
            thisDay_data.append(item)
            # add to existing file
    
    
    
    # print out the length of these days - which = the number of days
    print (str(len(theseDays)) + ' days' )
    
    # remove the first "day" because it is only a copy of the header
    theseDays.pop(0)
    
    # initialise a list to hold some dates
    someDates = list()


    # go through the list with seperate daily data in it
    # for each daty of data
    for item in theseDays:
        
        print
        print
        #print item[11], item[12]
        # move though the rows in the data one by one
        for rows in item:
            # check to see if this row is a date time info
            if is_line_a_date(rows):
                # if it is a date/time add it to my list of somedates
                someDates.append(rows)
       
        # now somedates has a list of all the date/times for that day

    #    print min(someDates)  # this is the starting day/time
    #    print max(someDates)  # this is the finishing day/time
    
        #convert the earilest data date to a headerdate and put in place
        item[11] = toHead_Date(min(someDates)) + '     GPS         TIME OF FIRST OBS\n'
        item[12] = toHead_Date(max(someDates)) + '     GPS         TIME OF LAST OBS\n'
        
        # see if it worked by printing out
        print item[11]
        print item[12]
        
        # reinitialise someDates ready for a new day
        someDates = list()
        
        # add 1 to the file name
        fileNo += 1
        # make up a file name for this daya of data
        thisOutfile = outFld + str(fileNo) + '_' + thisFile
        
        # use the function to write the file out to the output folder
        write_list_to_file(item, thisOutfile)
        
 
    
 
# print ourselves a list of files we have processed into daily files in this run
for item in rinexFiles:
    print item
    print


   
print ('finished')





















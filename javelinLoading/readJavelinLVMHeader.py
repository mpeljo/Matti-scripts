# 
# readJavelinLVMHeader.py
#
# Uses: Python 3.6.9 64-bit
# Program to inspect the first 24 entries of a
# Vista Clara .lvm raw data file
#
# The raw Javelin data for each logged depth interval (with “.lvm” extension) are saved as
# binary files. Each file contains four data channels written with big-endian format and
# 64-bit double precision.
#
# The first 50 entries of each binary raw data file contain header information and are the
# same for all four columns. The header information is copied from the 2001 manual and
# reproduced in the javHeaderVariables{} dictionary.

import os
import sys
import struct

javHeaderVariables = {
    1: "Excitation pulse length",           # Seconds
    2: "Echo Time",                         # Seconds
    3: "Number of Echoes",                  # Integer
    4: "Measurement Frequency",             # Hz
    5: "Number of Averages",                # Integer
    6: "Preprocessed Sampling Frequency",   # Hz
    7: "Quality Factor",                    # Float
    8: "Preamplifier Gain",                 # Float
    9: "Measurement Depth",                 # Meters
    10: "Acquisition Version",              # #.#
    11: "Probe ID",                         # eg 175.2001 is 175B-001
    12: "Cable ID",                         # Meters
    13: "Operation Mode",                   # Integer (0, 1, 2)
    14: "Tr",                               # Seconds relaxation time
    15: "Wellhead height above ground",     # Meters
    16: "Start Depth",                      # Meters
    17: "Stop Depth",                       # Meters
    18: "Depth Increment",                  # Meters
    19: "Sensor Offset from Logging Head",  # Meters
    20: "(245kHz) 100% H2O Cal Scaling",    # Float
    21: "(245kHz) Echo Time Shift",         # Microseconds
    22: "(245kHz) Echo Phase Shift",        # Degrees
    23: "(245kHz) Echo Frequency Shift",    # Hz
    24: "(245kHz) Q Factor During Calibration",    # Float
    25: "(290kHz) 100% H2O Cal Scaling",    # Float
    26: "(290kHz) Echo Time Shift",         # Microseconds
    27: "(290kHz) Echo Phase Shift",        # Degrees
    28: "(290kHz) Echo Frequency Shift",    # Hz
    29: "(290kHz) Q Factor During Calibration",
    30: "unknown",      # Float
    31: "unknown",      # Float
    32: "unknown",      # Float
    33: "unknown",      # Float
    34: "unknown",      # Float
    35: "unknown",      # Float
    36: "unknown",      # Float
    37: "unknown",      # Float
    38: "unknown",      # Float
    39: "unknown",      # Float
    40: "unknown",      # Float
    41: "unknown",      # Float
    42: "unknown",      # Float
    43: "unknown",      # Float
    44: "unknown",      # Float
    45: "unknown",      # Float
    46: "unknown",      # Float
    47: "unknown",      # Float
    48: "unknown",      # Float
    49: "unknown",      # Float
    50: "unknown",      # Float
}

old_dataFolders = {
    'KR08': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR08',
    'KR21': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\18BP13-D\JP350\18BP13-D_110-60',
    'KR22': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR22',
    'KR23': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR23',
    'KR30': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR30',
    'KR31a': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR31a',
    'KR33': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR33',
    'KR36': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR36\KR36_144p0_110p5m',
    'KR38': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR38',
    'KR40': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR40',
    'KR45': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR45',
    'KR46': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR46',
    'KR49': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR49',
    'KR50a': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR50a',
    'KR50B': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR50B\KR50b_136p5_60p0m',
    'KR51a': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR51a',
    'KR51B': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR51B\KR51b_94-45p5m',
    'KR21B': 	r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\KR21B\KR21B_142p0_70m',
}

dataFolders = {
    'GW036806.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036806.2\GW036806.2-350-74p5m-to-10p0m",
    'GW036842.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036842.2\GW036842.2-350-59p0m-to-30p0m",
    'GW036852.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036852.2\GW036852.2-350-38p0m-to-7p0m",
    'GW036853.3.3': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036853.3\350",
    'GW036883.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036883.1\GW036883.1-350-24p0m-to-5p0m",
    'GW036884.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036884\GW036884 - 350 - 24p0mto 6p0m",
    'GW036885.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036885\GW036885 - 350 - 23p0m to 9p0m",
    'GW036941.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036941.2\GW036941 - 350 - 32p0m to 12p0m",
    'GW036942.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036942.2\GW036942.2-350-50p0m-to-10p0m",
    'GW040872.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW040872.2\GW040872.2-238-19p5m-to-5p0m",
    'GW040873.3.3': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW040873.3\GW040873.3-238-102p0m-to-90p0m",
    'GW098195.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098195\GW098195 - 350- 31p5m to 8p0m",
    'GW098196.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098196.1\GW098196.1-46p0m-to-20p0m",
    'GW098197.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098197.2\GW098197.2-350-64p0m-to-30p0m",
    'GW098199.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098199.2\GW098199-350-104.0m-7.5m",
    'GW098201.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098201\350",
    'GW098203.1.1': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW098203\GW098203-350-97.0m_to_7.5m",
}

def read_javelin_header(file):
    f = open(file, 'rb')
    for i in range(len(javHeaderVariables)):
        headerValue = struct.unpack('>d', f.read(8))
        if i == 14:
            print ("{0:38} {1}".format(javHeaderVariables[i+1], headerValue[0]))
            print(headerValue[0])

for borehole, datapath in dataFolders.items():
    print('\'' + borehole + '\',', end='')
    files = os.listdir(datapath)
    found = False
    for f in files:
        parts = f.split('.')
        while not found:
            if len(parts) > 1 and parts[1] == 'lvm':
                print(f + ', ', end='')
                lvm_file = datapath + '\\' + f
                read_javelin_header(lvm_file)
                found = True
            else:
                break
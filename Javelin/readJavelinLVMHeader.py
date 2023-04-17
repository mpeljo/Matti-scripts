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

dataFolders = {
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

def read_javelin_header(file):
    # fileName = '\\\\prod.lan\\active\\proj\\futurex\\StuartCorridor\\Working\\Matti\\Javelin\\KR48_38p5-8m_freq1_Tr1000_1.lvm'
    #for file in fileNames:
    f = open(file, 'rb')
    for i in range(len(javHeaderVariables)):
        headerValue = struct.unpack('>d', f.read(8))
        if i == 14:
            #print ("{0:38} {1}".format(javHeaderVariables[i+1], headerValue[0]))
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

#if __name__ == "__main__":
#    if sys.argv[1:]:
#        read_javelin_header(sys.argv[1:])
#    else:
#        print("Usage: %s <path\\file.lvm> [<path\\file.lvm>...]" % sys.argv[0])
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

def read_javelin_header(fileNames):
    # fileName = '\\\\prod.lan\\active\\proj\\futurex\\StuartCorridor\\Working\\Matti\\Javelin\\KR48_38p5-8m_freq1_Tr1000_1.lvm'
    for file in fileNames:
        print(file)
        f = open(file, 'rb')
        for i in range(len(javHeaderVariables)):
            headerValue = struct.unpack('>d', f.read(8))
            print ("{0:38} {1}".format(javHeaderVariables[i+1], headerValue[0]))

if __name__ == "__main__":
    if sys.argv[1:]:
        read_javelin_header(sys.argv[1:])
    else:
        print("Usage: %s <path\\file.lvm> [<path\\file.lvm>...]" % sys.argv[0])

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

testdataFolders = {
    'GW036806.2.2': r"\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR\GW036806.2\GW036806.2-350-74p5m-to-10p0m",
}

def read_javelin_header(file):
    f = open(file, 'rb')
    for i in range(1, len(javHeaderVariables)+1):
        headerValue = struct.unpack('>d', f.read(8))
        if i == 11:
            print ("{0:15} {1}".format(javHeaderVariables[i+1], headerValue[0]))

for borehole, datapath in dataFolders.items():
    print(borehole + ':\t', end='')
    files = os.listdir(datapath)
    found = False
    for f in files:
        while not found:
            if f.endswith('lvm'):
                #print(f + ', ', end='')
                lvm_file = datapath + '\\' + f
                read_javelin_header(lvm_file)
                found = True
            else:
                break

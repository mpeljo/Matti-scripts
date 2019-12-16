# read_boot_sector.py - Inspect the first 512 bytes of a file

import struct

javHeader = {
    1: "Excitation pulse length",
    2: "Echo Time",
    3: "Number of Echoes",
    4: "Measurement Frequency",
    5: "Number of Averages",
    6: "Preprocessed Sampling Frequency",
    7: "Quality Factor",
    8: "Preamplifier Gain",
    9: "Measurement Depth",
    10: "Acquisition Version",
    11: "Probe ID",
    12: "Cable ID",
    13: "Operation Mode",
    14: "Tr",
    15: "Wellhead height above ground",
    16: "Start Depth",
    17: "Stop Depth",
    18: "Depth Increment",
    19: "Sensor Offset from Logging Head"
}

file = open('\\\\prod.lan\\active\\proj\\futurex\\StuartCorridor\\Working\\Matti\\Javelin\\KR48_38p5-8m_freq1_Tr1000_1.lvm', 'rb')
for i in range(20):
    f = struct.unpack('>d', file.read(8))       # first value probably 0.00007 (7e-05)
    print(i+1, f)


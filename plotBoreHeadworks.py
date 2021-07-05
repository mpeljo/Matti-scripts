'''
Python 3.7.2 code to draw groundwater borehole headworks.
Requires formatted Excel spreadsheet with headworks measurements.
The location of the Excel spreadsheet on a user's computer is
    hard-coded in the "borefile" variable and must be updated
    in order to run this program.
Connects to ORAPROD for non-essential details.

No error handling.
'''

import sys
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
import matplotlib.lines as lines

# Constants
CASING_ID = 0.100
CASING_PROTECTOR_ID = 0.300
SCALE = 2
CENTRE_X = 10

# File containing bore headworks measurements
# borefile = 'C:\\Users\\u25834\\Desktop\\KeepRiverBores\\latestKeepBores.xlsx'
borefile = (r"\\prod.lan\active\proj\futurex\Common\Working\Matti\BoreHeadworksVisualiser\latestKeepBores.xlsx")

# Connect to Oracle database, get bore construction details
sys.path.append(r'H:\\Python\\Oracle\\\\')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cursor = oracon.cursor()
#cursor = connect_to_oracle()

# Open Excel spreadsheet containing borehole info
xl_file = pd.ExcelFile(borefile)
df = xl_file.parse('Survey data')

for borefileRow in range(21):

    print(df.columns)
    print(df.index)

    # Get borehole measurements
    # Expected excel file sheet 1 headings:
    # Index([0:'Bore ID', 1:'RN', 2:'Date-time', 3:'Easting', 4:'Northing',
    #      5:'Horizontal precision (m)', 6:'Trimble datum (m AHD),
    #      7:'SWL RP elevation (m AHD)', 8:'Cement elevation (m AHD)',
    #      9:'Ground elevation (m AHD)', 10:'Vertical precision (m)',
    #      11:'SWL (m bRP)', 12:'SWL (m AHD)', 13:'Casing protector (m agl)',
    #      14:'PVC (m agl)', 15:'Cement (m agl)', 16:'RP', 17:'Notes'],
    #     dtype='object')

    inf_bname       = df.iloc[borefileRow, 0]
    bname           = str(df.iloc[borefileRow, 1])
    h_precision     = df.iloc[borefileRow, 5]
    RP_elevation    = df.iloc[borefileRow, 6]                   # Trimble datum
    gndAHD          = df.iloc[borefileRow, 9]
    v_precision     = df.iloc[borefileRow, 10]
    SWL_AHD         = df.iloc[borefileRow, 12]
    tocp_agl        = df.iloc[borefileRow, 13]
    toc_agl         = df.iloc[borefileRow, 14]
    plinth_agl      = df.iloc[borefileRow, 15]
    RP              = df.iloc[borefileRow, 16]                  # TOCP or TOC

    # Calculate some details for drawing purposes
    cp_l_offset     = CENTRE_X - (CASING_PROTECTOR_ID * SCALE)
    cp_r_offset     = CENTRE_X + (CASING_PROTECTOR_ID * SCALE)
    casing_l_offset = CENTRE_X - (CASING_ID * SCALE)
    casing_r_offset = CENTRE_X + (CASING_ID * SCALE)

    gnd_length = 5

    plot_title = 'Bore ' + bname + '  (' + inf_bname + ')'

    plt.title(plot_title, fontsize=10)

    # Start drawing headworks

    # Plinth
    plt.plot([cp_l_offset - 2, cp_l_offset - 2, cp_l_offset], [0, plinth_agl, plinth_agl], color = 'orange')
    plt.plot([cp_r_offset, cp_r_offset + 2, cp_r_offset + 2], [plinth_agl, plinth_agl, 0], color = 'orange')
    plt.plot([cp_r_offset + 2.3, cp_r_offset + gnd_length + 4], [plinth_agl, plinth_agl], 'r--')
    plinthLabel = str(round(gndAHD + plinth_agl, 3)) + ' m AHD'
    plt.text(cp_r_offset + gnd_length + 4.7, plinth_agl, plinthLabel)
    plinthHeightText = str(round(plinth_agl, 3)) + ' m agl'
    plt.text(4, plinth_agl, plinthHeightText)

    # Ground elevation
    plt.plot([cp_l_offset - gnd_length, cp_l_offset], [0,0], color = 'orange')
    plt.plot([cp_r_offset, cp_r_offset + gnd_length], [0,0], color = 'orange')
    plt.plot([cp_r_offset + gnd_length + 0.3, cp_r_offset + gnd_length + 4], [0, 0], 'r--')
    gndLabel = str(round(gndAHD, 3)) + ' m AHD'
    plt.text(cp_r_offset + gnd_length + 4.7, -0.05, gndLabel)
    plt.plot([cp_r_offset + gnd_length + 8, cp_r_offset + gnd_length + 8], [0,0])

    # Casing protector
    plt.plot([cp_l_offset, cp_l_offset], [-0.5, tocp_agl], color='green')
    plt.plot([cp_r_offset, cp_r_offset], [-0.5, tocp_agl], color='green')
    plt.plot([cp_r_offset + 0.3, cp_r_offset + gnd_length + 4], [tocp_agl, tocp_agl], 'r--')
    tocp = str(round(tocp_agl + gndAHD, 3)) + ' m AHD'
    plt.text(cp_r_offset + gnd_length + 4.7, tocp_agl - 0.05, tocp)
    cpHeightText = str(round(tocp_agl, 3)) + ' m agl'
    plt.text(4, tocp_agl, cpHeightText)

    # Casing
    plt.plot([casing_l_offset, casing_l_offset], [-1.0, toc_agl], color='green')
    plt.plot([casing_r_offset, casing_r_offset], [-1.0, toc_agl], color='green')
    plt.plot([casing_r_offset + 0.3, casing_r_offset + gnd_length + 4], [toc_agl, toc_agl], 'r--')
    toc = str(round(toc_agl + gndAHD, 3)) + ' m AHD'
    plt.text(cp_r_offset + gnd_length + 4.7, toc_agl - 0.05, toc)
    cHeightText = str(round(toc_agl, 3)) + ' m agl'
    plt.text(4, toc_agl, cHeightText)

    # Standing Water Level
    plt.plot([casing_l_offset - (gnd_length / 2), casing_r_offset + (gnd_length / 2)], [-0.4, -0.4], color='blue', marker = 'o', linestyle='dashed')
    swlText = str(round(SWL_AHD, 3)) + ' m AHD'
    plt.text(casing_r_offset + (gnd_length / 2) + 0.2, -0.41, swlText)

    # Get borehole details from database and print them
    query = 'select b.location.sdo_point.x, b.location.sdo_point.y from BOREHOLE.BOREHOLES b where b.BOREHOLE_NAME = \'' + bname + '\''

    cursor.execute(query)
    for row in cursor:
        lon = row[0]
        lat = row[1]
        lon = 'Longitude:   ' + str(lon)            # Must be a better way to align the text
        lat = 'Latitude:      ' + str(lat)
        plt.text(14, -0.95, lon)
        plt.text(14, -0.82, lat)

    plt.show()

cursor.close()

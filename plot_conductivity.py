import sys

import pandas as pd
import numpy as np
import lasio
import matplotlib.pyplot as plt

#import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as mPolygon
from matplotlib.collections import PatchCollection, LineCollection
import matplotlib.image as mpimg
import matplotlib.text as mtext

import cx_Oracle
#from skimage.transform import resize       # https://scikit-image.org/docs/dev/install.html

sys.path.append(r'H:\\Python\\Oracle\\\\')
import connect_to_oracle

oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

def log_plot(logs, bore_name):
    logs = logs.sort_values(by='Depth')
    top = 0
    bot = logs.Depth.max()
    
    f, ax = plt.subplots(nrows=1, ncols=4, figsize=(12,8))
    ax[0].plot(logs.VALUE, logs.Depth, color='green')
    #ax[0].plot(logs.GAMMA_CALIBRATED, logs.Depth, color='green')
    #ax[1].plot(logs.INDUCTION_CALIBRATED, logs.Depth, color='red')
    #ax[2].plot(logs.DT, logs.Depth, color='black')
    #ax[3].plot(logs.MELCAL, logs.Depth, color='blue')
    #ax[4].plot(logs.RHOB, logs.Depth, color='c')
    #ax[5].plot(logs.Vsh, logs.Depth, color='m')
    
    for i in range(len(ax)):
        ax[i].set_ylim(top,bot)
        ax[i].invert_yaxis()
        ax[i].grid()
        
    ax[0].set_xlabel("GAMMA\nCALIBRATED")
    ax[0].set_xlim(logs.VALUE.min(),logs.VALUE.max())
    #ax[0].set_xlim(logs.GAMMA_CALIBRATED.min(),logs.GAMMA_CALIBRATED.max())
    ax[0].set_ylabel("Depth(m)")
    ax[1].set_xlabel("INDUCTION\nCALIBRATED")
    #ax[1].set_xlim(logs.INDUCTION_CALIBRATED.min(),logs.INDUCTION_CALIBRATED.max())
    #ax[2].set_xlabel("DT")
    #ax[2].set_xlim(logs.DT.min(),logs.DT.max())
    #ax[3].set_xlabel("MELCAL")
    #ax[3].set_xlim(logs.MELCAL.min(),logs.MELCAL.max())
    #ax[4].set_xlabel("RHOB")
    #ax[4].set_xlim(logs.RHOB.min(),logs.RHOB.max())
    #ax[5].set_xlabel("Vsh")
    #ax[5].set_xlim(logs.Vsh.min(),logs.Vsh.max())
    
    ax[1].set_yticklabels([]); ax[2].set_yticklabels([]);
    ax[3].set_yticklabels([])
    #ax[4].set_yticklabels([]); ax[5].set_yticklabels([]) 
    
    f.suptitle('Bore:{}'.format(bore_name), fontsize=14,y=0.94)

    plt.show()

# Get list of unique entities with conductivity
borehole_query ='''
    select
        distinct SAMPLINGFEATURENAME
    from
        ROCKPROPS.WEBSVC_ROCKPROPS_ELEC_COND
    where
        samplingfeaturetype ='borehole'
    and
        boreholecollarlatitude > -26.0
    '''

#cons = pd.read_sql(query, oracon)
boreholes = cur.execute(borehole_query)

#for row in boreholes:
#    print(row[0])

# Test borehole RN034364 or RN019387
#active_hole = 'RN034364'
active_hole = 'RN019387'    # Cond has med+deep at each level (double-ups)
cond_query ='''
    select
        *
    from
        ROCKPROPS.WEBSVC_ROCKPROPS_ELEC_COND
    where
        SAMPLINGFEATURENAME = '{}'
    order by
        BOREHOLEINTERVALBEGIN_M
    '''.format(active_hole)

borehole_cond = pd.read_sql(cond_query, oracon)
bh_cond = borehole_cond.rename(
    columns={"BOREHOLEINTERVALBEGIN_M" : "Depth"})

print(bh_cond.head())
# Assume boreholeintervalbegin_m and boreholeintervalend_m are the same
# Draw cond diagram
log_plot(bh_cond, active_hole)

"""
borehole_cond.plot.line('VALUE',
                        'BOREHOLEINTERVALBEGIN_M',
                        legend=False,
                        figsize=(3, 9)
                        ).invert_yaxis()
plt.margins(x=.5)
plt.tight_layout()
plt.plot
plt.savefig(r'C:\\Users\\u25834\\Desktop\\{}_cond.png'.format(active_hole), pad_inches = 1)
plt.show()
"""

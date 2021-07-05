# Python 3.6
# Initial data quality checking script by M Peljo, 30/07/2020
# Requires "connect_to_oracle.py" located in user's H:\ drive
# 
# Update the index of projects variable (lines 91, 92)
#   to process the associated subset of .LAS files.
#
# Uncomment line 76 to view plots as they are created.

import sys
import os
import pandas as pd
import lasio
import matplotlib.pyplot as plt

# Connect to oracle using credentials stored in safe location
sys.path.append(r'H:\\Python\\Oracle\\\\')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

# -------------FUNCTIONS---------------------------
def log_plot(neils_logs, oracond_logs, oragam_logs, borehole, save=False):
    neils_logs = neils_logs.sort_values(by='Depth')
    oracond_logs = oracond_logs.sort_values(by='Depth')
    oragam_logs = oragam_logs.sort_values(by='Depth')
    top = 0
    bot = 0
    # Set maximum logging depth for all plots
    #if oracond_logs.empty and oragam_logs.empty:
    #    bot = neils_logs.Depth.max()
    #else:
    bot = max(
            neils_logs.Depth.max(),
            oracond_logs.Depth.max(),
            oragam_logs.Depth.max()
    )
    bot = bot * 1.05
    
    f, ax = plt.subplots(nrows=1, ncols=4, figsize=(12,8))
    ax[0].plot(neils_logs.GAMMA_CALIBRATED, neils_logs.Depth, color='green')
    # Uncomment next line to overprint the LAS gamma with the ROCKPROPS gamma
    # ax[0].plot(oragam_logs.VALUE, oragam_logs.Depth, color='black', linestyle='dashed')
    ax[1].plot(oragam_logs.VALUE, oragam_logs.Depth, color='red')
    ax[2].plot(neils_logs.INDUCTION_CALIBRATED, neils_logs.Depth, color='green')
    ax[3].plot(oracond_logs.VALUE, oracond_logs.Depth, color='red')

    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()
        
    ax[0].set_xlabel("CALIBRATED\nGAMMA\nfrom LAS")
    ax[0].set_xlim(neils_logs.GAMMA_CALIBRATED.min(),neils_logs.GAMMA_CALIBRATED.max())
    ax[0].set_ylabel("Depth(m)")
    if oragam_logs.empty:
        ax[1].set_xlabel("Gamma\nnot found in\nROCKPROPS")
    else:
        ax[1].set_xlabel("ROCKPROPS\nGamma")
        ax[1].set_xlim(neils_logs.GAMMA_CALIBRATED.min(),neils_logs.GAMMA_CALIBRATED.max())
    ax[2].set_xlabel("CALIBRATED\nConductivity\nfrom LAS")
    ax[2].set_xlim(neils_logs.INDUCTION_CALIBRATED.min(),neils_logs.INDUCTION_CALIBRATED.max())
    if oracond_logs.empty:
        ax[3].set_xlabel("Conductivity\nnot found in\nROCKPROPS")
    else:
        ax[3].set_xlabel("ROCKPROPS\nConductivity")
        ax[3].set_xlim(neils_logs.INDUCTION_CALIBRATED.min(),neils_logs.INDUCTION_CALIBRATED.max())
    
    ax[1].set_yticklabels([]); ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    #ax[4].set_yticklabels([]); ax[5].set_yticklabels([]) 
    
    f.suptitle('Bore: {}'.format(borehole), fontsize=14,y=0.94)

    if save is True:
        save_file = '{}{}.png'.format(out_path, borehole)
        plt.savefig(save_file)
        plt.close()
    else:
        plt.show()


# -------------PROGRAM-----------------------------
# Build list of las files, starting with project folders
projects = ("Alice Springs",
            "Daly River",
            "Howard East",
            "Remote Communities",
            "Tennant Creek",
            "Ti-Tree",
            "West Davenport"
            )

bores = []
indgam_path = r'\\prod.lan\active\proj\futurex\StuartCorridor\Data\Processed\Geophysics\InductionGamma\Final\{}\\'.format(projects[5])
out_path = r"\\prod.lan\active\proj\futurex\StuartCorridor\Working\Matti\Conductivity_QC\{}\\".format(projects[5])

# Get list of bores in the folder
for dir, subs, files in os.walk(indgam_path):
    for file in files:
        if file.endswith('.las'):
            bore_name = file.split('.')[0]
            bores.append(bore_name)
            print(bore_name)

# Get Oracle data
# Test borehole RN034364 or RN019387
# active_hole = 'RN019387'    # Cond has med+deep at each level (double-ups)
# bores = ['RN034364']      # Uncomment to test a single "Alice Springs" bore with med & deep cond
for bore in bores:
    print(bore)
    file_path = indgam_path + '{}.las'.format(bore)
    # Conductivity data
    cond_query ='''
        select
            *
        from
            ROCKPROPS.WEBSVC_ROCKPROPS_ELEC_COND
        where
            SAMPLINGFEATURENAME = '{}'
        order by
            BOREHOLEINTERVALBEGIN_M
        '''.format(bore)

    rockprops_cond = pd.read_sql(cond_query, oracon)
    # Set the depth parameter to align with LAS data
    rockprops_cond = rockprops_cond.rename(
        columns={"BOREHOLEINTERVALBEGIN_M" : "Depth"})
    print(rockprops_cond.head())

    # Gamma data
    gamma_query ='''
        select
            *
        from
            ROCKPROPS.WEBSVC_ROCKPROPS_NATGAM
        where
            SAMPLINGFEATURENAME = '{}'
        order by
            BOREHOLEINTERVALBEGIN_M
        '''.format(bore)

    rockprops_gamma = pd.read_sql(gamma_query, oracon)
    # Set the depth parameter to align with LAS data
    rockprops_gamma = rockprops_gamma.rename(
        columns={"BOREHOLEINTERVALBEGIN_M" : "Depth"})

    # Get Neil & Mike's processed data
    las = lasio.read(file_path)
    df = las.df()
    df_idx = df.rename_axis('Depth').reset_index()
    # Standardise column names
    for column in df_idx.columns:
        if "GAMMA" in column:
            df_idx = df_idx.rename(
                columns={column : "GAMMA_CALIBRATED"}
            )
        if "INDUCTION" in column:
            df_idx = df_idx.rename(
                columns={column : "INDUCTION_CALIBRATED"}
            )

    # Plot LAS data and ROCKPROPS data
    if "GAMMA_CALIBRATED" in df_idx.columns and "INDUCTION_CALIBRATED" in df_idx.columns:
        log_plot(df_idx, rockprops_cond, rockprops_gamma, bore, save=True)
    else:
        print('{} has non-standard column names'.format(bore))

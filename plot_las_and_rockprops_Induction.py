# Python 3.6
# Initial data quality checking script by M Peljo, 30/07/2020
# Requires "connect_to_oracle.py" located in user's H:\ drive

import sys
import pandas as pd
import lasio
import matplotlib.pyplot as plt

# Connect to oracle using credentials stored in safe location
sys.path.append(r'H:\\Python\\Oracle\\\\')
import connect_to_oracle
oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

# -------------FUNCTIONS---------------------------
def log_plot(neils_logs, rockprops_gamma, rockprops_med_cond, rockprops_deep_cond, borehole, save=False):
    """Creates log-scale plots of hydrochemistry data, either to the screen or to .png file

    Parameters:
    neils_logs (dataframe):         A dataframe created from LAS file containing both deep-
            and medium-channel conductivity log data.

    rockprops_gamma (dataframe):    A dataframe containing gamma log data. This is intended
            to have been extracted from Oracle ROCKPROPS.

    rockprops_med_cond (dataframe): A dataframe containing medium-channel conductivity
            log data. This is intended to have been extracted from Oracle ROCKPROPS.

    rockprops_deep_cond (dataframe): A dataframe containing deep-channel conductivity
            log data. This is intended to have been extracted from Oracle ROCKPROPS.

    borehole (str):     The name of the borehole. For labelling the plot.

    save (boolean):     Save .png plots to file (True), or display plots to screen (False)


    Returns:
    Nothing
    """
    
    neils_logs = neils_logs.sort_values(by='Depth')
    rockprops_gamma = rockprops_gamma.sort_values(by='Depth')
    rockprops_med_cond = rockprops_med_cond.sort_values(by='Depth')
    rockprops_deep_cond = rockprops_deep_cond.sort_values(by='Depth')
    top = 0
    bot = 0

    # Set maximum logging depth for all plots
    bot = max(
        neils_logs.Depth.max(),
        rockprops_gamma.Depth.max(),
        rockprops_med_cond.Depth.max(),
        rockprops_deep_cond.Depth.max()
    )

    # Extend log a little deeper than the deepest measurement
    bot = bot * 1.05

    f, ax = plt.subplots(nrows=1, ncols=6, figsize=(12, 8))

    ax[0].plot(neils_logs.GR, neils_logs.Depth, color='green')
    ax[0].set_xscale('log')
    ax[1].plot(rockprops_gamma.VALUE, rockprops_gamma.Depth, color='red')
    ax[1].set_xscale('log')
    ax[2].plot(neils_logs.DEEP_INDUCTION, neils_logs.Depth, color='green')
    ax[2].set_xscale('log')
    # Uncomment next line to overprint the LAS gamma with the ROCKPROPS gamma
    #ax[0].plot(rockprops_deep_cond_logs.VALUE, rockprops_deep_cond_logs.Depth, color='black', linestyle='dashed')
    ax[3].plot(rockprops_deep_cond.VALUE, rockprops_deep_cond.Depth, color='red')
    ax[3].set_xscale('log')
    ax[4].plot(neils_logs.MEDIUM_INDUCTION, neils_logs.Depth, color='green')
    ax[4].set_xscale('log')
    ax[5].plot(rockprops_med_cond.VALUE, rockprops_med_cond.Depth, color='red')
    ax[5].set_xscale('log')

    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()

    ax[0].set_xlabel("Gamma\nfrom LAS")
    ax[0].set_xlim(neils_logs.GR.min(),neils_logs.GR.max())
    ax[0].set_ylabel("Depth(m)")
    if rockprops_gamma.empty:
        ax[1].set_xlabel("Gamma\nnot found in\nROCKPROPS")
    else:
        ax[1].set_xlabel("ROCKPROPS\nGamma")
        ax[1].set_xlim(neils_logs.GR.min(),neils_logs.GR.max())
    ax[2].set_xlabel("LAS\nDeep\nInduction")
    ax[2].set_xlim(neils_logs.DEEP_INDUCTION.min(), neils_logs.DEEP_INDUCTION.max())
    if rockprops_deep_cond.empty:
        ax[3].set_xlabel("Deep\nInduction\nnot found in\nROCKPROPS")
    else:
        ax[3].set_xlabel("ROCKPROPS\nDeep\nInduction")
        ax[3].set_xlim(neils_logs.DEEP_INDUCTION.min(), neils_logs.DEEP_INDUCTION.max())
    ax[4].set_xlabel("LAS\nMedium\nInduction")
    ax[4].set_xlim(neils_logs.MEDIUM_INDUCTION.min(), neils_logs.MEDIUM_INDUCTION.max())
    if rockprops_med_cond.empty:
        ax[5].set_xlabel("Medium\nInduction\nnot found in\nROCKPROPS")
    else:
        ax[5].set_xlabel("ROCKPROPS\nMedium\nInduction")
        ax[5].set_xlim(neils_logs.MEDIUM_INDUCTION.min(), neils_logs.MEDIUM_INDUCTION.max())

    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])

    f.suptitle('Bore: {}'.format(borehole), fontsize=14, y=0.94)

    if save is True:
        save_file = '{}{}.png'.format(out_path, borehole)
        plt.savefig(save_file)
        plt.close()
    else:
        plt.show()

def plot_conductivity(plotting_data, save=False):
    """Creates log-scale plots of hydrochemistry data, either to the screen or to .png file

    Parameters:
    plotting_data (tuple) contains:
        borehole (str):         The borehole name
        
        project (str):          The project area name
        
        df_idx (dataframe):     Borehole conductivity log, read from LAS file and converted to
                                    indexed dataframe
        
        cond_data (dataframe):  Conductivity data extracted from ROCKPROPS.WEBSVC_ROCKPROPS_ELEC_COND
                                    for this borehole

    save (boolean):     Save .png plots to file (True), or display plots to screen (False)

    Returns:
    Nothing
    """
    
    las_cond = plotting_data[2].sort_values(by='Depth')
    print(las_cond.head())

    neils_logs = plotting_data[2].sort_values(by='Depth')
    #rockprops_gamma = rockprops_gamma.sort_values(by='Depth')
    #rockprops_med_cond = rockprops_med_cond.sort_values(by='Depth')
    rp = plotting_data[3]
    rockprops_med_cond = rp[rp['METHOD'].str.contains('medium')]
    #print(rockprops_med_cond.head())
    #rockprops_deep_cond = rockprops_deep_cond.sort_values(by='Depth')
    rockprops_deep_cond = rp[rp['METHOD'].str.contains('deep')]
    top = 0
    bot = 0

    # Set maximum logging depth for all plots
    bot = max(
        neils_logs.Depth.max(),
        #rockprops_gamma.Depth.max(),
        rockprops_med_cond.Depth.max(),
        rockprops_deep_cond.Depth.max()
    )

    # Extend log a little deeper than the deepest measurement
    bot = bot * 1.05

    f, ax = plt.subplots(nrows=1, ncols=6, figsize=(12, 8))

    ax[0].plot(neils_logs.GR, neils_logs.Depth, color='green')
    ax[0].set_xscale('log')
    #ax[1].plot(rockprops_gamma.VALUE, rockprops_gamma.Depth, color='red')
    ax[1].set_xscale('log')
    ax[2].plot(neils_logs.DEEP_INDUCTION, neils_logs.Depth, color='green')
    ax[2].set_xscale('log')
    # Uncomment next line to overprint the LAS gamma with the ROCKPROPS gamma
    #ax[0].plot(rockprops_deep_cond_logs.VALUE, rockprops_deep_cond_logs.Depth, color='black', linestyle='dashed')
    ax[3].plot(rockprops_deep_cond.VALUE, rockprops_deep_cond.Depth, color='red')
    ax[3].set_xscale('log')
    ax[4].plot(neils_logs.MEDIUM_INDUCTION, neils_logs.Depth, color='green')
    ax[4].set_xscale('log')
    ax[5].plot(rockprops_med_cond.VALUE, rockprops_med_cond.Depth, color='red')
    ax[5].set_xscale('log')

    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()

    ax[0].set_xlabel("Gamma\nfrom LAS")
    ax[0].set_xlim(neils_logs.GR.min(),neils_logs.GR.max())
    ax[0].set_ylabel("Depth(m)")
    """if rockprops_gamma.empty:
        ax[1].set_xlabel("Gamma\nnot found in\nROCKPROPS")
    else:
        ax[1].set_xlabel("ROCKPROPS\nGamma")
        ax[1].set_xlim(neils_logs.GR.min(),neils_logs.GR.max())"""
    ax[2].set_xlabel("LAS\nDeep\nInduction")
    ax[2].set_xlim(neils_logs.DEEP_INDUCTION.min(), neils_logs.DEEP_INDUCTION.max())
    if rockprops_deep_cond.empty:
        ax[3].set_xlabel("Deep\nInduction\nnot found in\nROCKPROPS")
    else:
        ax[3].set_xlabel("ROCKPROPS\nDeep\nInduction")
        ax[3].set_xlim(neils_logs.DEEP_INDUCTION.min(), neils_logs.DEEP_INDUCTION.max())
    ax[4].set_xlabel("LAS\nMedium\nInduction")
    ax[4].set_xlim(neils_logs.MEDIUM_INDUCTION.min(), neils_logs.MEDIUM_INDUCTION.max())
    if rockprops_med_cond.empty:
        ax[5].set_xlabel("Medium\nInduction\nnot found in\nROCKPROPS")
    else:
        ax[5].set_xlabel("ROCKPROPS\nMedium\nInduction")
        ax[5].set_xlim(neils_logs.MEDIUM_INDUCTION.min(), neils_logs.MEDIUM_INDUCTION.max())

    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])

    f.suptitle('Bore: {}'.format(borehole), fontsize=14, y=0.94)

    if save is True:
        save_file = '{}{}.png'.format(out_path, borehole)
        plt.savefig(save_file)
        plt.close()
    else:
        plt.show()
    

def get_las_data():
    pass

def get_rockprops_data():
    pass

def get_websvc_conductivity(borehole_name):
    conductivity_query = '''
        select
            *
        from
            ROCKPROPS.WEBSVC_ROCKPROPS_ELEC_COND
        where
            SAMPLINGFEATURENAME = '{}'
        order by
            BOREHOLEINTERVALBEGIN_M
        '''.format(borehole_name)
    conductivity_data = pd.read_sql(conductivity_query, oracon)
    return conductivity_data



# -------------PROGRAM-----------------------------
# Build list of las files, starting with project folders
# Dictionary is BORE: project_area
"""
dual_cond_bores = {"RN010285": "Remote Communities",
                   "RN013214": "Remote Communities",
                   "RN015877": "Remote Communities",
                   "RN018144": "Remote Communities",
                   "RN019379": "Alice Springs",
                   "RN019387": "Alice Springs",
                   "RN019450": "West Davenport",
                   "RN019451": "West Davenport",
                   "RN019452": "West Davenport",
                   "RN019453": "West Davenport",
                   "RN019454": "West Davenport",
                   "RN019455": "West Davenport",
                   "RN019456": "West Davenport",
                   "RN019457": "West Davenport",
                   "RN019673": "Alice Springs",
                   "RN019674": "Alice Springs",
                   "RN019676": "Alice Springs",
                   "RN019678": "Alice Springs",
                   "RN019680": "West Davenport",    # Only has medium channel in ROCKPROPS
                   "RN019681": "West Davenport",
                   "RN019806": "West Davenport",}
"""
dual_cond_bores = {"RN019681": "West Davenport",
}

for borehole, project in dual_cond_bores.items():
    print("Now processing {} from {}.".format(borehole, project))

    #indgam_path = r'\\prod.lan\active\proj\futurex\StuartCorridor\Data\Processed\Geophysics\InductionGamma\Final\{}\\'.format(project)
    indgam_path = r'\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\neils-final\final\induction\/'
    file_path = indgam_path + '{}_induction.las'.format(borehole)
    #out_path = r"\\prod.lan\active\proj\futurex\StuartCorridor\Working\Matti\Conductivity_QC\{}\\".format(project)

    # Get Oracle data
    
    # Conductivity data
    cond_data = get_websvc_conductivity(borehole)
    #cond_data.rename(columns={"BOREHOLEINTERVALBEGIN_M": "Depth"})
    cond_data['Depth'] = cond_data['BOREHOLEINTERVALBEGIN_M']

    print(cond_data.columns)
    print(cond_data.head())

    """for method in cond_data.METHOD.unique():
        print(method)       # medium, deep, probe
        channel = ""
        if method.find("medium") >= 0:
            channel = "electrical conductivity - borehole medium channel"
        elif method.find("deep") >= 0:
            channel = "electrical conductivity - borehole deep channel"
        elif method.find("probe") >= 0:
            channel = "electrical conductivity - borehole probe"
        print(channel)
    """

    """
    rockprops_med_cond = pd.read_sql(cond_query, oracon)
    # Set the depth parameter to align with LAS data
    rockprops_med_cond = rockprops_med_cond.rename(
        columns={"BOREHOLEINTERVALBEGIN_M" : "Depth"})

    # Copy ROCKPROPS data to prepare one dataframe
    #   each with medium and deep data
    rockprops_deep_cond = rockprops_med_cond.copy(deep=True)
    rockprops_deep_cond = rockprops_deep_cond[rockprops_deep_cond.METHOD != 'electrical conductivity - borehole medium channel']
    rockprops_med_cond = rockprops_med_cond[rockprops_med_cond.METHOD != 'electrical conductivity - borehole deep channel']


    rockprops_gamma = pd.read_sql(gamma_query, oracon)
    # Set the depth parameter to align with LAS data
    rockprops_gamma = rockprops_gamma.rename(
        columns={"BOREHOLEINTERVALBEGIN_M" : "Depth"})
    
    """
    # LAS file data
    # Get Neil & Mike's processed data
    las = lasio.read(file_path)
    df = las.df()
    df_idx = df.rename_axis('Depth').reset_index()
    #print(df_idx.head())

    plotting_data = (borehole, project, df_idx, cond_data)

    # Draw conductivity plot
    plot_conductivity(plotting_data)

    # Plot LAS data and ROCKPROPS data
    #log_plot(df_idx, rockprops_gamma, rockprops_med_cond, rockprops_deep_cond, borehole, save=True) # Add save=True to save png files
    
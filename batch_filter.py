# "\\prod.lan\active\proj\futurex\StuartCorridor\Working\Neil\borehole_filtereing_HE\scripts\filter_logs.bat"
import numpy as np
import lasio
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
import datetime
import math

# Define key functions

def plot_logs(ax, ser, title, logplot = True):
    
    ax.plot(ser.values, ser.index)
    if logplot:
        ax.set_xscale('log')
       
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
    ax.set_title(title)

def combination(n, r): # calculation of combinations, n choose k
    return int((math.factorial(n)) / ((math.factorial(r)) * math.factorial(n - r)))   

def pascals_triangle(rows):
    result = [] 
    for count in range(rows): # start at 0, up to but not including rows number.
        # this is really where you went wrong:
        row = [] # need a row element to collect the row in
        for element in range(count + 1): 
            # putting this in a list doesn't do anything.
            # [pascals_tri_formula.append(combination(count, element))]
            row.append(combination(count, element))
        result.append(row)
        # count += 1 # avoidable
    return result[rows-1]

def binom_filter(x, kernel):
    return np.mean(np.convolve(x, kernel, 'same'))
    
def run_filter(series, window, min_periods, filter):
    if filter == 'median':
        return series.rolling(window = window, min_periods = min_periods).median()
    
    elif filter == 'binomial':
        kernel = pascals_triangle(window)/np.sum(pascals_triangle(window))
        return series.rolling(window = window, min_periods = min_periods).apply(binom_filter, args = (kernel,), raw=True)
    
    elif filter == 'mean':
        return series.rolling(window = window, min_periods = min_periods).mean()

        
        
def filter_log(infile, bore_id, cols, window, min_periods, centre, csv_dir, jpeg_dir,
               filters  = ['median'], remove_negs = True, logplot = True,
               min_depth = np.nan, max_depth = np.nan):
               
    # Open the las file
    las = lasio.read(infile)
    df_logs = las.df()
    
    # GEt prefix for file naming
    prefix = infile.split('\\')[-1].replace('LAS','las').split('.las')[0]
 
    # Iterate through columns
    columns = [x.strip() for x in cols.split(',')]
    for item in columns:
        # Remove any white spaces
        item = item.strip()
        
        # Create a data series from the column of interest
        series = df_logs[item]
        
        # Remove nans
        
        series = series.dropna()

        # Remove negative values
        if remove_negs:
         
            series = series[series>0]
        # Now filter using parameters described above
        
        filtered = series.copy()
        
        for filter in filters:
        
            filtered = run_filter(filtered, window, min_periods, filter)
     
        
        # Clip the filtered if values are assigned

        if np.isfinite(min_depth):
            filtered =  filtered[filtered.index > min_depth]
        
        if np.isfinite(max_depth):
            filtered =  filtered[filtered.index < max_depth]
        
        # Create a plot
    
        fig, (ax1,ax2) = plt.subplots(1,2, figsize = (8,8), sharex = True, sharey = True)
        
        # Plot the unfiltered data
        plot_logs(ax1, series, logplot = logplot, title = "unfiltered")
        ax1.invert_yaxis()
        plot_logs(ax2, filtered, logplot = logplot, title = "filtered")
        
        # Create directories if need be
        
        for dir in [csv_dir, jpeg_dir]:
            new_dir = os.path.join(dir, bore_id)
            
            print(new_dir)

            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        
        plt.savefig(os.path.join(jpeg_dir, bore_id) + '\\' + prefix + '_' + item + '_window_' + str(window) + '.png')
        
        filtered.to_csv(os.path.join(csv_dir, bore_id) + '\\' + prefix + '_' + item + '_window_' + str(window) + '.csv')
        
        plt.close()
        
    # Write out metadata file
    filename = os.path.join(csv_dir, bore_id) + '\\filtering_metadata.txt'
        
    with open(filename, 'w') as f:
        s= 'Downhole logs filtered on the ' + str(datetime.datetime.now()) + '\n'
        s+= 'The filtered variables are {} .\n'.format(cols)
        
        filter_string = ', '.join(filters)
        s+= 'Filtering using {} filter(s) with window size {} and minimum period of {}\n'.format(str(filter_string), str(window), str(min_periods))
        if np.isfinite(min_depth):
            s+= 'The log were clipped above {} m\n'.format(str(min_depth))
        if np.isfinite(max_depth):
            s+= 'The log were clipped below {} m\n'.format(str(max_depth))
        f.write(s)

#### Main Program #############
# Read in csv with parameters
infile = sys.argv[1]

# Filter all variables in csv

df = pd.read_csv(infile)

# Iterate through and extract filtering parameters from the rows
"""
Infile:         The input LAS file. Neil copied the raw file to a "data" folder for safety
window:         5
min_periods:    5
Columns:        INDUCTION_CALIBRATED.   The LAS Column Definition containing data
centre:         True    Does not appear to be used
resample:       False  
resample_interval:      Does not appear to be used
logplot:        True    Set horizontal scale to log scale
remove_negs:    True    Delete rows containing negative values
min_depth:      5       Clip top of filtered log to depth if set
max_depth:      <none>  Clip bottom of filtered log to depth if set
csv_dir:        folder  The output folder for CSV-formatted filtered data
jpeg_dir        folder  The output folder for .png images of filtered data

"""
for index, row in df.iterrows():

    infile = row['Infile']
    bore_id = row['Bore_ID']
    filter = row['filter']
    Columns = row['Columns']
    window = row['window']
    min_periods = row['min_periods']
    centre = row['centre']
    csv_dir = row['csv_dir']
    jpeg_dir = row['jpeg_dir']
    remove_negs = row['remove_negs']
    logplot = row['logplot']
    min_depth = row['min_depth']
    max_depth = row['max_depth']
    filters = [row['filter_1']]
    
    if not pd.isnull(row['filter_2']):
        filters.append(row['filter_2'])
    
    if filter == 1:

        filter_log(infile, bore_id, Columns, window, min_periods, centre, csv_dir, jpeg_dir, filters,
        remove_negs, logplot, min_depth = min_depth, max_depth = max_depth)



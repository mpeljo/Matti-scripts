#!/usr/bin/env python
# 
# 

"""
To start the loop creator application: create a .bat file like this,
ensuring appropriate virtual environment with relevant modules installed...

    @echo off
    echo .......................................
    echo Python v3.9, SMR loop calculator v0.2.0
    echo .......................................
    "C:/W10DEV/Anaconda3/envs/py39/python.exe" "%cd%\GMR_loop_creator_v3\loop_calculator.py" "-f" "%cd%"
    pause

To do:
-!!!!!!!!!!!!!!!!!!!!!!!!!
    Confirm with user before overwriting existing site!!!!!!

- Make program flow more logical (eg functions call functions at present, difficult to follow)
- Tidy up function parameters and calls
- Add AGRF magnetic field predictions
- Note: To install GeoPandas, 5/10/2022:
   https://geopandas.org/en/stable/getting_started/install.html
   The following commands create a new environment with the name geo_env,
   configures it to install packages always from conda-forge,
   and installs GeoPandas in it:

 conda create -n geo_env
 conda activate geo_env
 conda config --env --add channels conda-forge
 conda config --env --set channel_priority strict
 conda install python=3 geopandas

Version 0.2.0
- Use vector cross product to determine whether a clockwise or anticlockwise
    antenna loop should be created
- Simplify the loop generation code

Version 0.1.5
- Fixed bug where, if SE or SW was first corner, the app erroneously reported that
    any bearing to next corner was bad due to overflow-style error in the
    check_bearing_direction function
- Add requirement and args input to start app with argument for folder name

Version 0.1.4
- Changed input coordinates of first corner from GDA94 to WGS84,
    using EPSG codes from
    https://desktop.arcgis.com/en/arcmap/latest/map/projections/pdf/projected_coordinate_systems.pdf
    since they will be acquired by GPS in WGS84
- Added names to each GPX file waypoint, for example
    Example_c1 for the first corner

Version 0.1.3
- Added compass point to metadata _params.txt output.
- Reduced the number of significant figures of some
    values in the _params.txt output file.
- Added error message for when bearing to second point is
    not compatible with first corner compass label.
    Eg bearing 0 from first corner='n'.
- Added "Starting corner" label for compass points on
    the GUI
- Added filter to suppress FutureWarning from geopandas
    (Bug #2347 - https://github.com/geopandas/geopandas/issues/2347)
    (pandas.Int64Index is deprecated...) that arose in the
    make_clockwise_square and make_anticlockwise_square fxns.
    Used a sledgehammer approach and suppressed all FutureWarning.
    The filter can be refined now or removed in later versions of geopandas.

Version 0.1.2
- First numbered version

Requirements:
Python 3.9
Numpy
Pandas
Geopandas
pathlib

Calculate vertices of a square, given a corner, length of sides,
and compass angle of the first side from the corner. Save data as
SHP, GPX, CSV files and write metadata as a text file, all in a
folder that follows field data collection protocols (2015/2313).

Inspired by applications written by Joseph Bell and Neil Symington.
"""

import os, sys
import getopt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPoint
import matplotlib.pyplot as plt
from datetime import datetime
from math import pi, cos, sin, radians, fabs
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import warnings

# Suppress FutureWarning from geopandas (pandas.Int64Index is deprecated...)
warnings.simplefilter(action='ignore', category=FutureWarning)

gui_fields = [  'Site name',
                'First corner Easting (m)',
                'First corner Northing (m)',
                'Bearing to next corner',
                'Length of sides (m)'
]

gui_field_defaults = [  'Symonston',
                        696109,
                        6086750,
                        0,
                        100
]

cardinals = {
    (0, 1): 'N',
    (0, 2): 'NE',
    (1, 2): 'E',
    (2, 2): 'SE',
    (2, 1): 'S',
    (2, 0): 'SW',
    (1, 0): 'W',
    (0, 0): 'NW',
    (1, 1): '',
}

octant_angles = {
    'N':    0,
    'E':    90,
    'S':    180,
    'W':    270,
    'NE':   45,
    'SE':   135,
    'SW':   225,
    'NW':   315,
}

BEARING_TOLERANCE = 30

# Australian UTM projection EPSG values
projections = {
    'WGS_1984_UTM_Zone_48S': 32748,
    'WGS_1984_UTM_Zone_49S': 32749,
    'WGS_1984_UTM_Zone_50S': 32750,
    'WGS_1984_UTM_Zone_51S': 32751,
    'WGS_1984_UTM_Zone_52S': 32752,
    'WGS_1984_UTM_Zone_53S': 32753,
    'WGS_1984_UTM_Zone_54S': 32754,
    'WGS_1984_UTM_Zone_55S': 32755,
    'WGS_1984_UTM_Zone_56S': 32756,
    'WGS_1984_UTM_Zone_57S': 32757,
    'WGS_1984_UTM_Zone_58S': 32758,
}

# Set up some stuff...
# Write corner coordinates into a list
corners = np.nan * np.ones(shape = (4,2), dtype = float)
corners_gdf = gpd.GeoDataFrame()

# Start with the desktop as the working folder. This may change
#   depending on where the app is run from, via the argument that is
#   passed to the app
data_folder = os.path.join(str(Path.home()), r'Desktop\SMR')
shapefile_dir = os.getcwd() + '\\shape_gpx_files'
parameters_dir = os.getcwd() + '\\parameter_files'

epsg = 0

def get_args(argv):
    arg_folder = ""
    arg_help = "{0} -f <folderPath>".format(argv[0])

    try:
        opts, _ = getopt.getopt(argv[1:], "hf:", ["help", "folder="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-f", "--folder"):
            if not os.path.isdir(arg):
                print(arg_help)
                sys.exit(2)
            else:
                arg_folder = arg
    return arg_folder

# GUI functions
def fetch(entries):
    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        print('{}: {}'.format(field, text)) 

def makeform(root):
    entries = []
    
    for field in list(zip(gui_fields, gui_field_defaults)):
        row = tk.Frame(root)
        lab = tk.Label(row, width=20, text=field[0], anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, field[1])
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))

    # Add selection menu to constrain projections
    opt_var = tk.StringVar(root)
    opt_var.set(list(projections.keys())[0])
    row = tk.Frame(root)
    lab = tk.Label(row, width=20, text='UTM Projection', anchor='w')
    ent = tk.OptionMenu(row, opt_var, *(list(projections.keys())))
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    lab.pack(side=tk.LEFT)
    ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
    entries.append(('Projection', opt_var))

    # Add radio buttons to constrain starting corner
    row2 = tk.Frame(root, width=40, height=40)
    corner_selector_lbl = tk.Label(
        row2,
        width=20,
        text='Select starting corner:',
        font=('Arial', 12),
        anchor='w'
    )
    corner_selector_lbl.pack()
    row2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    selection = tk.StringVar(None, 'N')
    row3 = tk.Frame(root)
    row3.pack()

    for i in range(3):
        row3.columnconfigure(i, weight=1, minsize=75)
        row3.rowconfigure(i, weight=1, minsize=50)
        for j in range(0, 3):
            if (i, j) != (1, 1):    # Don't create a button in the centre grid square
                frame = tk.Frame(
                    master=row3,
                    #relief=tk.RAISED,
                    borderwidth=1
                )
                cardinal = cardinals[i,j]
                frame.grid(row=i, column=j, padx=5, pady=5)
                #label = tk.Label(master=frame, text=cardinal)
                #label.pack(padx=5, pady=5)
                r_btn = tk.Radiobutton(
                    frame,
                    text=cardinal,
                    value=cardinal,
                    variable=selection,
                ).pack(fill='x')
    entries.append(('Corner', selection))
    
    
    """row = tk.Frame(root)
    corner_label = tk.Label(row, width=20, text='Select starting corner:', font=("Arial", 12), anchor='w')
    corner_label.pack()
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    selection = tk.StringVar(None, "n")
    for choice in gui_corner_choices:
        r = tk.Radiobutton(
            root,
            text=choice[0],
            value=choice[1],
            variable=selection,
        )
        r.pack(fill='x', padx=5, pady=5)
    entries.append(('Corner', selection))"""

    return entries

# Functions to create and save square
def get_anglediff(angle1, angle2):
    diff = ((angle2 - angle1 + 180) % 360) - 180
    print('ang1: {}, ang2: {}, diff: {}'.format(angle1, angle2, diff))
    return (diff + 360) if (diff < -180) else diff

def convert_to_math(angle):
    degrees = (450 - angle) % 360
    return radians(degrees)

def get_vector_coords(rad_angle):
    x = cos(rad_angle)
    y = sin(rad_angle)
    return x, y

def get_explicit_rotation(rot_selection):
    selection = rot_selection.get()
    return selection

def within_tolerance(start_direction, bearing):
    cw_centre = start_direction + 135
    acw_centre = start_direction - 135
    cw_angle_diff = fabs(get_anglediff(cw_centre, bearing))
    acw_angle_diff = fabs(get_anglediff(acw_centre, bearing))
    cw_diff = cw_angle_diff < BEARING_TOLERANCE
    acw_diff = acw_angle_diff < BEARING_TOLERANCE
    print('CW diff: {}, ACW diff {}'.format(cw_diff, acw_diff))
    return cw_diff or acw_diff

def choose_rotation():
    rot_check = tk.Toplevel(root)
    rot_check.title("Select desired antenna style")
    rot_row = tk.Frame(rot_check)
    rotation_text = """
            The system needs additional information
            to generate the coordinates.
            Do you intend the antenna to be generated
            clockwise (CW) or anticlockwise (ACW)?"""
    info_lbl = tk.Label(master=rot_row, text=rotation_text)
    info_lbl.pack(anchor=tk.CENTER)
    rot_row.pack()
    rot_selection = tk.IntVar(None)
    row2 = tk.Frame(rot_check)
    r1 = tk.Radiobutton(row2, text="CW", value=-1, variable=rot_selection)
    r2 = tk.Radiobutton(row2, text="ACW", value=1, variable=rot_selection)
    r1.pack(fill='x')
    r2.pack(fill='x')
    row2.pack()
    button = tk.Button(
        row2,
        text="OK",
        command=get_explicit_rotation(rot_selection)
        )
    button.pack()
    return(rot_selection)

def corner_select_error():
    messagebox.showerror('Bad geometry', 'The first corner is not compatible with the bearing')

def is_clockwise(start_vec, bearing_vec):
    cross_product = np.cross(start_vec, bearing_vec)
    cross_product = float("{:.10f}".format(cross_product))
    # Cross product equalling zero means the two inputs are collinear.
    # Collinear vectors have no clock sense (no rotational direction).
    if cross_product == 0:
        corner_select_error()
        quit()

    if(cross_product < 0):
        return(True)
    else:
        return(False)

def get_diagnostic_string(entries):
    site_name = entries[0][1].get()
    initial_x = float(entries[1][1].get())
    initial_y = float(entries[2][1].get())
    bearing =   float(entries[3][1].get())
    length =    float(entries[4][1].get())
    epsg = projections.get(entries[5][1].get())
    initial_point = entries[6][1].get()
    diagnostic_text = ("""
        Data entered by operator:
        Site name:     {}
        Easting:       {}
        Northing:      {}
        Bearing:       {}
        Side length:   {}
        EPSG code:     {}
        First corner:  {}"""
        .format(site_name, initial_x, initial_y, bearing, length, epsg, initial_point))
    return diagnostic_text

def calculate_corners(entries, data_folder):
    print(get_diagnostic_string(entries))
    
    site_name = entries[0][1].get()
    initial_x = float(entries[1][1].get())
    initial_y = float(entries[2][1].get())
    bearing =   float(entries[3][1].get())
    length =    float(entries[4][1].get())
    epsg = projections.get(entries[5][1].get())
    initial_point = entries[6][1].get()

    site_path = os.path.join(data_folder, site_name)
    if os.path.exists(site_path):
        err_msg = """
            The folder
            {}
            already exists.
            Please delete the folder or try again.
            
            The program will now quit."""
        messagebox.showerror('Folder exists', err_msg.format(site_path))
        quit()

    #draw_inputs(entries)
    start_direction = octant_angles[initial_point]

    if not within_tolerance(start_direction, bearing):
        corner_select_error()
        quit()

    rotation_sense = check_bearing_direction(start_direction, bearing)
    
    print('Square type: {}'.format(rotation_sense))
    
    # Get math angle info of bearing to second peg
    angle = ((450 - bearing)) % 360
    square_angle = angle * (pi / 180)
    corners = np.nan * np.ones(shape = (4,2), dtype = float)
    corners[0] = [initial_x, initial_y]
    for i in range(3):
        dx = length * cos(square_angle)
        dy = length * sin(square_angle)
        corners[i+1] = [corners[i][0] + dx, corners[i][1] + dy]
        if rotation_sense == 'clockwise':
            square_angle = square_angle - (90 * (pi/180))    # - is CW
        else:
            square_angle = square_angle + (90 * (pi/180))    # + is CCW
    

    # create a dataframe for the antenna corners
    df = pd.DataFrame(
            data = corners,
            columns = ['easting', 'northing'],
            index = ['_c'.join((site_name, str(x))) for x in np.arange(1,5)])
    # convert to a geodataframe
    corners_gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.easting, df.northing)).set_crs(epsg)  # type: ignore
    corners_gdf.index.names = ['name']
    draw_gpd_square(corners_gdf)
    print('Writing data to {}'.format(data_folder))
    write_parameters(corners_gdf, site_name, entries, data_folder, rotation_sense)
    write_spatial_files(corners_gdf, site_name, data_folder, entries)
    quit()

def check_bearing_direction(initial_dir, bearing_dir):
    startx, starty = get_vector_coords(convert_to_math(initial_dir))
    bearingx, bearingy = get_vector_coords(convert_to_math(bearing_dir))
    start_vec = np.array([startx, starty])
    bearing_vec = np.array([bearingx, bearingy])
    if is_clockwise(start_vec, bearing_vec):
        return('clockwise')
    else:
        return('anticlockwise')

def get_centroid(corners):
    square = MultiPoint([[a.x, a.y] for a in corners.geometry.values])
    return square.centroid

def draw_gpd_square(gdf):
    _, ax = plt.subplots(figsize = (6, 6))
    gdf.plot(ax=ax)
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.index):
        ax.annotate(label, xy=(x, y))
    plt.show()

def write_spatial_files(gdf, site_name, data_folder, entries):
    gpd.options.display_precision = 9
    output_dir = os.path.join(data_folder, site_name, 'SiteInfo')
    photo_dir = os.path.join(output_dir, 'Photos')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)
    shpfile = os.path.join(output_dir, site_name + ".shp")
    gpxfile = os.path.join(output_dir, site_name + ".gpx")
    csvfile = os.path.join(output_dir, site_name + ".csv")

    # Write data out as a shape file, gpx file, csv file
    gdf.to_file(shpfile)
    gdf.to_csv(csvfile)

    gpd.options.display_precision = 6
    latlon_gdf = gdf.to_crs(epsg=4326)
    # Need <extensions> to add eastings and northings to .gpx file
    latlon_gdf.to_file(gpxfile, driver='GPX', GPX_USE_EXTENSIONS=True)
    gpd.options.display_precision = 9
    print(latlon_gdf)

def write_parameters(corners, site_name, params, data_folder, rotation_sense):
    gpd.options.display_precision = 1
    dateTimeObj = datetime.now()
    lines = ['Date and time:                {}'.format(dateTimeObj)]
    lines.append('Site name:                    {}'.format(params[0][1].get()))
    lines.append('Projection:                   {}'.format(params[5][1].get()))
    lines.append('First corner compass point:   {}'.format(params[6][1].get()))
    lines.append('First corner mE:              {}'.format(params[1][1].get()))
    lines.append('First corner mN:              {}'.format(params[2][1].get()))
    lines.append('Bearing to 2nd corner (deg):  {}'.format(params[3][1].get()))
    lines.append('Corner layout rotation:       {}'.format(rotation_sense))
    lines.append('Side length (m):              {}'.format(params[4][1].get()))
    
    lines.append('\nAntenna corners:')
    corners_rnd = corners.round(0)
    lines.append(str(corners_rnd))

    gpd.options.display_precision = 3
    lines.append('\nAntenna centroid:')
    lines.append(str(get_centroid(corners)))

    output_dir = os.path.join(data_folder, site_name, 'SiteInfo')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    outfile = os.path.join(output_dir, site_name + "_params.txt")

    with open(outfile, 'w') as f:
        f.write('\n'.join(lines))


#############   MAIN   #####################################################
if __name__ == '__main__':
    # Get folderpath as an argument
    data_folder = get_args(sys.argv)
    data_folder = os.path.join(data_folder, 'SMR')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # Create form for operator input.
    # Collect data in "ents" structure.
    # Run calculations etc by pressing the
    # "Run" button, from the "calculate_corners" function.
    
    root = tk.Tk()
    root.title('SMR loop creator v.0.2.0')
    ents = makeform(root)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
    b1 = tk.Button(root, text='Run',
                    command=(lambda e=ents: calculate_corners(e, data_folder)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(root, text='Cancel',
                    command=root.quit)
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    root.mainloop()

        


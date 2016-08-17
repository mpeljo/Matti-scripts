#!/usr/bin/env python
#title           :coords.py
#description     :Calculates the location of geophones in 3D - Menindee seismic
#                  survey July 2016.
#author          :Matti Peljo
#date            :20160817
#version         :0.1
#usage           :python coords.py
#notes           :Proof of concept
#python_version  :2.6.6  
#==============================================================================
import math

# Constants

# Offset:
#  Position was recorded to the "right" of each geophone,
#  ie, each position was measured at a point along the line
#  defined by measurements n and n+1, but a short offset distance
#  from n towards n+1.
#  This means the actual location of the geophone is offset to
#  the "left" of the recorded location.
offset = 0.05

# test points
a = [633191.292, 6412757.425, 59.029]
b = [633191.947, 6412756.659, 59.067]

# Read point a

# Read next point

# Calculate the vector. In this case, note that as the geophone is located
#   to the "left" of the measured location, we can define the vector in the
#   reverse direction, then add a vector of length "offset" to the location
#   of the first point.
#
#   Vba = [bx - ax, by - ay, bz - az]

Vba = [
    b[0] - a[0],
    b[1] - a[1],
    b[2] - a[2]
    ]

print 'the vector is:', Vba

# Calculate length of the vector

length = math.sqrt(
    (Vba[0]**2) +
    (Vba[1]**2) +
    (Vba[2]**2)
    )
print length


# Calculate the unit vector
unitVector = [
    Vba[0]/length,
    Vba[1]/length,
    Vba[2]/length
    ]
print 'unitVector is:', unitVector

# Calculate the vector with length = "offset"
offsetVector = [
    unitVector[0]*offset,
    unitVector[1]*offset,
    unitVector[2]*offset
    ]

# Calculate coordinates of geophone actual location
geophoneLocation = [
    a[0] - offsetVector[0],
    a[1] - offsetVector[1],
    a[2] - offsetVector[2]
    ]
print 'Geophone Location is:', geophoneLocation

# What to do if this is the last point in the line



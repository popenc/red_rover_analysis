"""
Simple desktop program to plot CSV lat lon
data from ROS bag files using matplotlib
"""

# import numpy as np
import matplotlib.pyplot as plt
import sys
import csv
import utm
import json


file_name = sys.argv[1]  # input = filename with extension
csv_data = ""
lat_array = []
lon_array = []
easting_array = []
northing_array = []
time_array = []

print("INPUT: {}".format(file_name))

# Read in the file:
with open(file_name, 'r') as csv_file:
	reader = csv.reader(csv_file)
	data_list = list(reader)
csv_file.close()

# print("DATA LIST: {}".format(data_list))

# list of list -> step through collecting lat/lons:

mod_data_list = []  # modified data list w/ easting and northing values

headers_list = data_list[0]
headers_list = headers_list + ['easting', 'northing', 'zone number', 'zone letter']

mod_data_list.append(headers_list)

for data_arr in data_list[1:]:

	# lat_array.append(data_arr[3])
	# lon_array.append(data_arr[4])

	_temp_list = data_arr

	# print("DATA ARR LAT: {}".format(data_arr[3]))
	_temp_list[3] = float(_temp_list[3])
	_temp_list[4] = float(_temp_list[4])

	utm_tuple = utm.from_latlon(_temp_list[3], _temp_list[4])
	_temp_list = _temp_list + list(utm_tuple)
	mod_data_list.append(_temp_list)

	easting_array.append(utm_tuple[0])
	northing_array.append(utm_tuple[1])
	time_array.append(float(data_arr[0]))


# Writes CSV with added Easting and Northing values
# fileout_name = "{}_utm.csv".format(file_name.split(".")[0])
# with open(fileout_name, 'w', newline='') as csv_file:
# 	writer = csv.writer(csv_file)
# 	writer.writerows(mod_data_list)
# csv_file.close()


# print("LATS: {}".format(lat_array))
# print("LONS: {}".format(lon_array))


# flipped_lon_array = list(reversed(lon_array[1:]))
# flipped_lat_array = list(reversed(lat_array[1:]))


# with open('flipped_lons.csv', 'w') as csv_file:
# 	flipped_lons = []
# 	for i in range(0, len(flipped_lat_array) - 1):
# 		csv_file.write("{}, {} \n".format(flipped_lat_array[i], flipped_lon_array[i]))
# csv_file.close()


# plt.gca().invert_yaxis()


# plt.plot(lat_array[1:], lon_array[1:])
# plt.plot(easting_array, northing_array)
# plt.plot(time_array, easting_array)
plt.plot(time_array, northing_array)
plt.show()
import matplotlib.pyplot as plt
import sys
import csv
import gmplot
import utm



def find_header_index(headers, data):
	"""
	Gets first row (headers) and finds index
	of user-entered header names.
	Assuming two headers (e.g., lat, lon)
	"""

	print("HEADS: {}".format(headers))
	print("TYPE: {}".format(type(headers)))
	print("Data Row: {}".format(data[0]))

	_headers_index = []

	for _header in headers:
		_headers_index.append(data[0].index(_header))

	return _headers_index


# def convert_to_float(data_array):
# 	_float_list = []
# 	for item in data_array:
# 		_float_list.append(float(item))
# 	return _float_list


def build_plot_arrays(headers_index, data_list):
	"""
	Takes list of lists input, and returns two arrays
	for making simple x,y plots.
	"""
	_xarray, _yarray = [], []
	# list of list -> step through collecting lat/lons:
	for data_arr in data_list[1:]:
		_lat = float(data_arr[headers_index[0]])
		_lon = float(data_arr[headers_index[1]])
		_xarray.append(_lat)
		_yarray.append(_lon)

	return _xarray, _yarray


def open_file(filename):
	# Read in the file:
	with open(filename, 'r') as csv_file:
		reader = csv.reader(csv_file)
		data_list = list(reader)
	csv_file.close()
	return data_list


def convert_to_latlon(utm_data):
	"""
	Converts UTM to lat/lon values.
	Input: list of [easting, northing] items
	"""
	zone_number = 17
	zone_letter = "N"
	latlon_list = [['latitude', 'longitude']]

	for xypair in utm_data[1:]:
		latlon_pair = list(utm.to_latlon(float(xypair[0]), float(xypair[1]), zone_number, zone_letter))  # tuple -> list
		latlon_list.append(latlon_pair)

	return latlon_list


def add_line_data():
	"""
	Adds additional CSV data of lines for testing the pure pursuit
	algorithm. Initial test are intended to be straight paths behind
	the engineering annex building.
	"""
	line_data = open_file('Data/2018-01-23/pure_pursuit_line_test_1.csv')
	line_data = convert_to_latlon(line_data)  # returns list of pairs, with first pair being 'latitude' & 'longitude'
	headers = ['latitude', 'longitude']
	headers_index = find_header_index(headers, line_data)
	return build_plot_arrays(headers_index, line_data)




if __name__ == '__main__':

	filename = sys.argv[1]  # input = filename with extension
	headers = sys.argv[2:]  # assuming remaining args after filename are headers to plot
	requested_headers = []
	lat_array, lon_array = [], []  # initializing lists
	line_lats, line_lons = [], []
	csv_data = ""

	print("Input File: {}".format(filename))
	data_list = open_file(filename) # Read in the CSV file
	headers_index = find_header_index(headers, data_list)  # Find index of xy headers
	print("headers index: {}".format(headers_index))

	# Break up list of rows in CSV into two arrays for plotting:
	lat_array, lon_array = build_plot_arrays(headers_index, data_list)


	# Trying to add line GPS data as well to make sure it's not overlapping anything:
	line_lats, line_lons = add_line_data()
	# print("line lats: {}".format(line_lats))
	# print("line lons: {}".format(line_lons))


	# gmplot library stuff:
	gmap = gmplot.GoogleMapPlotter(31.4736, -83.5299, 20)  # initial start pos and zoom level

	gmap.plot(lat_array, lon_array, 'cornflowerblue', edge_width=2)  # build plot
	gmap.plot(line_lats, line_lons, 'red', edge_width=3)

	# gmap.draw("{}.html".format(sys.argv[1]))  # save as html
	gmap.draw("Data/2018-01-23/turn_test_with_lines_1.html")
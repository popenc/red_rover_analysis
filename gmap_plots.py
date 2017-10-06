import matplotlib.pyplot as plt
import sys
import csv
import gmplot


file_name = sys.argv[1]  # input = filename with extension
requested_headers = []
csv_data = ""
lat_array = []
lon_array = []


def find_header_index(data):
	"""
	Gets first row (headers) and finds index
	of user-entered header names.

	Assuming two headers (e.g., lat, lon)
	"""

	_headers = sys.argv[2:]  # assuming args after filename are headers to plot

	print("HEADS: {}".format(_headers))
	print("TYPE: {}".format(type(_headers)))

	print("Data Row: {}".format(data[0]))

	# _num_headers = len(sys.arv[2:])
	_headers_index = []

	for _header in _headers:
		_headers_index.append(data[0].index(_header))

	return _headers_index


def convert_to_float(data_array):
	_float_list = []
	for item in data_array:
		_float_list.append(float(item))
	return _float_list


print("INPUT: {}".format(file_name))

# Read in the file:
with open(file_name, 'r') as csv_file:
	reader = csv.reader(csv_file)
	data_list = list(reader)
csv_file.close()

headers_index = find_header_index(data_list)

print("headers index: {}".format(headers_index))

# list of list -> step through collecting lat/lons:
for data_arr in data_list:
	lat_array.append(data_arr[headers_index[0]])
	lon_array.append(data_arr[headers_index[1]])

# plt.plot(lat_array[1:], lon_array[1:])
# plt.show()

gmap_lats = convert_to_float(lat_array[1:])
gmap_lons = convert_to_float(lon_array[1:])

print("lats: {}".format(gmap_lats))
print("item types: {}".format(type(gmap_lats[2])))

# gmplot library stuff
gmap = gmplot.GoogleMapPlotter(31.4736, -83.5299, 20)  # initial start pos and zoom level
gmap.plot(gmap_lats, gmap_lons, 'cornflowerblue', edge_width=2)
gmap.draw("{}.html".format(sys.argv[1]))  # save as html
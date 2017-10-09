"""
Simple desktop program to plot CSV lat lon
data from ROS bag files using matplotlib
"""

# import numpy as np
import matplotlib
matplotlib.use('Agg')  # temp fix for "_tkinter:TclError-no $DISPLAY env var" plt.show() error
import matplotlib.pyplot as plt
import sys
import csv
import utm
import json



class GPSPlot(object):

	def __init__(self):
		self.utm_keys = ['easting', 'northing', 'zone number', 'zone letter']
		# some ros gps headers of interest:
		self.ros_gps_headers = {
			'time': '%time', 
			'lat': 'field.latitude', 
			'lon': 'field.longitude', 
			'alt': 'field.altitude'
		}
		self.filename = ''  # csv file with gps data
		self.csv_data = []  # list of lists, csv data
		self.xheader = ''  # column name of data for x axis
		self.yheader = ''  # column name of data for y axis
		self.x_array = []  # x axis data for plot
		self.y_array = []  # y axis data for plot



	"""
	#########################
	### private functions ###
	#########################
	"""

	def find_header_index(self, csv_data, header):
		"""
		Returns index of header from CSV data,
		assumes row one of csv_data are headers.
		"""
		print("Searching for {} in csv data".format(header))
		print("Looking in headers: {}".format(csv_data[0]))
		try:
			return csv_data[0].index(header)
		except ValueError as e:
			logging.warning("header: {} not in csv data..".format(header))
		except Exception as e:
			raise e

	def create_csv(self, fileout):
		"""
		Creates CSV file with self.filename + '_utm.csv' name,
		created at location python program is executed.
		Essentially the input CSV w/ additional UTM data.
		Inputs:
			+ fileout - filename for output file
			+ path - TODO...
		"""
		with open(fileout_name, 'w', newline='') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerows(mod_data_list)
		csv_file.close()
		logging.info("file: {} created...".format(fileout))
		return

	def convert_latlon_to_utm(self, lat, lon):
		"""
		Converts lat/lon to utm,
		stores in easting and northing lists
		"""
		try:
			return utm.from_latlon(lat, lon)
		except Exception as e:
			raise e




	"""
	################################
	### main() level functions ###
	################################
	"""

	def upload_csv(self, filename):
		_csv_data = []
		# Read in the file:
		with open(filename, 'r') as _csv_file:
			reader = csv.reader(_csv_file)
			_csv_data = list(reader)
		_csv_file.close()
		return _csv_data

	def add_utm_to_csvdata(self, csv_data):
		"""
		Adds UTM data to input CSV, assumes
		headers for lat/lons are in ros format.
		Returns: modified csv data as list of lists (rows)
		"""
		_headers_list = csv_data[0]
		_headers_list = _headers_list + self.utm_keys

		_mod_data_list = []
		_mod_data_list.append(_headers_list)

		# find lat/lon columns..
		_lat_index = self.find_header_index(csv_data, self.ros_gps_headers['lat'])  # finds header indexes for self.x/yheader
		_lon_index = self.find_header_index(csv_data, self.ros_gps_headers['lon'])

		for _data_row in csv_data[1:]:
			_temp_row = _data_row
			_lat = float(_temp_row[_lat_index])  # convert to float
			_lon = float(_temp_row[_lon_index])  # convert to float 
			_utm_tuple = self.convert_latlon_to_utm(_lat, _lon)  # get utm from lat/lon
			_temp_row = _temp_row + list(_utm_tuple)  # add utm data to row
			_mod_data_list.append(_temp_row)

		return _mod_data_list

	def plotxy(self, csv_data, xheader, yheader):
		"""
		Plot xheader vs yheader csv col data w/ pyplot
		"""

		print("CSV Data: {}".format(csv_data))
		print("Finding {} and {} in csv data..".format(xheader, yheader))

		# find cols from csv data:
		_x_index = self.find_header_index(csv_data, xheader)
		_y_index = self.find_header_index(csv_data, yheader)
		_x_array = []
		_y_array = []
		_plot_data = {
			'xarray': [],
			'yarray': [],
			'properties': None  # TODO..
		}

		# build x and y array for plotting:
		for _data_row in csv_data[1:]:
			_plot_data['xarray'].append(float(_data_row[_x_index]))
			_plot_data['yarray'].append(float(_data_row[_y_index]))

		return _plot_data



if __name__ == '__main__':
	"""
	If being run by user as standalone script,
	take the following inputs:
	e.g., python plot_lat_lon.py [filename] [xheader] [yheader] [function]
	functions: 
		+ plotxy - plots [xheader] vs [yheader] from [filename] csv.
		+ utm_csv - converts lat/lons to utm, adds utm data to input csv and saves to disk.
		+ analyze_turn_tests - for turn tests; gets peaks and troughs in time window,
			average min/maxes, other stats (probably).
		+ gmap_plot - plot lat/lons on a google maps page.
	"""

	# Get arguments and build GPSPlot class instance:
	gps_plot = GPSPlot()
	gps_plot.filename = sys.argv[1]
	gps_plot.xheader = sys.argv[2]
	gps_plot.yheader = sys.argv[3]

	_csv_data = gps_plot.upload_csv(gps_plot.filename)  # upload csv data of filename
	_func = sys.argv[4]

	# upload csv data into list of lists:
	if _func == 'utm_csv':
		_csv_data = gps_plot.add_utm_to_csvdata(_csv_data)
		_fileout_name = "{}_utm.csv".format(self.filename.split(".")[0])  # filename --> inputfile + "_utm.cscv"
		gps_plot.create_csv(_fileout_name)
		print ("file: {} created..".format(_fileout_name))

	# plot xheader col vs yheader col:
	elif _func == 'plotxy':
		_plot_data = gps_plot.plotxy(_csv_data, gps_plot.xheader, gps_plot.yheader)  # plot obj.x/yheader
		print("plot data parsed, now making plot..")
		plt.plot(_plot_data['xarray'], _plot_data['yarray'])  # other options, titles, ranges???
		plt.show()  # display plot!
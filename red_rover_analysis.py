"""
Simple desktop program to plot CSV lat lon
data from ROS bag files using matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
from algorithms import detect_peaks
import datetime
import time
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

	def create_csv(self, fileout_name, fileout_data):
		"""
		Creates CSV file with self.filename + '_utm.csv' name,
		created at location python program is executed.
		Essentially the input CSV w/ additional UTM data.
		Inputs:
			+ fileout - filename for output file
			+ path - TODO...
		"""
		with open(fileout_name, 'w') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerows(fileout_data)
		csv_file.close()
		# logging.info("file: {} created...".format(fileout))
		return

	def create_output_file(self, fileout_name, fileout_data):
		"""
		Creates general output file, whereas create_csv() is 
		only for CSV files.
		"""
		with open(fileout_name, 'w') as fileout:
			# writer = csv.writer(fileout)
			fileout.write(fileout_data)
		fileout.close()
		# logging.info("file: {} created...".format(fileout))
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

	def convertUnixTime(self, time):
		"""
		Converts ROS %time values (unixtime) into
		DateTime objects in UTC format (avoiding DST business)
		"""
		return datetime.datetime.utcfromtimestamp(time)  # unixtime --> datetime

	def findNearest(self, data_array, val):
		"""
		Returns index of value from data_array
		closest to val
		"""
		nearest_val = min(data_array, key=lambda x:abs(x-val))
		print("nearest val in data array: {}".format(nearest_val))
		return data_array.index(nearest_val)

	def convertDegreeLatLonToDecimalLatLon(self, data_list):
		_dec_lat_lons = []
		for point in data_list:
			_dec_lat_lons.append(string2latlon(point['lat'], point['lon'], 'd% %m% %S% %H'))
		return _dec_lat_lons




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

		# print("CSV Data: {}".format(csv_data))
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

			# if 'time' in xheader:
			# 	_ut = float(_data_row[_x_index])  # ros ut format --> 1.50714738486656e+18
			# 	_ut = _ut / pow(10,9)  # format to proper magnitude
			# 	_plot_data['xarray'].append(self.convertUnixTime(_ut))
			# else:
			_plot_data['xarray'].append(float(_data_row[_x_index]))
			_plot_data['yarray'].append(float(_data_row[_y_index]))

		return _plot_data

	def find_peaks(self, csv_data, xheader, yheader, axrange, valley=False):
		"""
		Finds peaks of data, returns list
		"""
		_x_index = self.find_header_index(csv_data, xheader)
		_y_index = self.find_header_index(csv_data, yheader)
		_x_array = []
		_y_array = []

		for _data_row in csv_data[1:]:
			# build x/y arrays for findings peaks:
			_x_array.append(float(_data_row[_x_index]))
			_y_array.append(float(_data_row[_y_index]))

		print("min range: {}, max range: {}".format(axrange[0], axrange[1]))
		print(type(axrange[0]))

		ind = axrange[0].index("e")
		min_index_key = float(axrange[0][0:ind-1])  # trim off "e+18" (assuming unix time)
		ind = axrange[1].index("e")
		max_index_key = float(axrange[1][0:ind-1])


		# get peaks for requested range:
		try:
			_min_index = self.findNearest(_x_array, float(axrange[0]))
			_max_index = self.findNearest(_x_array, float(axrange[1]))
		except Exception as e:
			print("exception getting min/max from data: {}, {}".format(axrange[0], range[1]))
			raise e

		print("min/max index range for finding peaks: {}/{}".format(_min_index, _max_index))

		_y_array = _y_array[_min_index:_max_index]
		_x_array = _x_array[_min_index:_max_index]

		_peak_indexes = detect_peaks.detect_peaks(_y_array, valley=False)  # no filter

		# build x,y lists for peak points:
		_xmaximas, _ymaximas = [], []
		for _peak_index in _peak_indexes:
			_xmaximas.append(_x_array[_peak_index])
			_ymaximas.append(_y_array[_peak_index])

		_peak_indexes = detect_peaks.detect_peaks(_y_array, valley=True)  # no filter

		# build x,y lists for peak points:
		_xminimas, _yminimas = [], []
		for _peak_index in _peak_indexes:
			_xminimas.append(_x_array[_peak_index])
			_yminimas.append(_y_array[_peak_index])

		_plot_data = {
			'xarray': _x_array,
			'yarray': _y_array,
			'xminimas': _xminimas,
			'yminimas': _yminimas,
			'xmaximas': _xmaximas,
			'ymaximas': _ymaximas
		}

		return _plot_data



class GPSDataHandler(GPSPlot):
	"""
	Originally created for making a .gpx file from a .csv of lat/lons.
	Inherits GPSPlot initially for use of its CSV functions.
	"""
	def __init__(self, input_file, output_file="gpx_output.gpx"):
		self.input_file = input_file  # input csv filename
		self.output_file = output_file  # output gpx filename

		# Template for gpx output file:
		self.gpx_template = """
		<?xml version="1.0" encoding="UTF-8" standalone="no"?>
		<gpx
		   version="1.1"
		   creator=""
		   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		   xmlns="http://www.topografix.com/GPX/1/1"
		   xsi:schemaLocation="http://www.topografix.com/GPX/1/1/gpx.xsd">
		<metadata>
		<name> peanut_field_latlon_only.gpx </name>
		   <copyright author="">
		      <year>2018</year>
		   </copyright>
		</metadata>
			<rte>{}</rte>
		</gpx>
		"""
		self.gpx_point = '<rtept lat="{}" lon="{}"></rtept>'  # lat/lon template for gpx point

	def create_gpx_from_csv(self, row_skip=2):
		"""
		Reads in CSV of lat/lons,
		then wraps gpx tags around it,
		finally saves it as a gpx file.
		"""
		# 1. Read in CSV file (returns list of lists, where lists are rows):
		csv_data = self.upload_csv(self.input_file)

		# 2. Fill in gpx template with lat/lons from CSV:
		gpx_points = ""
		# for row in csv_data:
		for i in range(0, len(csv_data) - 1, row_skip):
			_row = csv_data[i]
			gpx_points += self.gpx_point.format(_row[0], _row[1])  # building string of gpx points
		
		# gpx_content = self.gpx_template.replace(" ", "").replace("\n", "").replace("\t", "")  # get instance of gpx template
		# gpx_content.format(gpx_points)  # insert points into gpx template
		gpx_content = self.gpx_template.format(gpx_points).replace("\n", "").replace("\t", "")  # get instance of gpx template

		# 3. Output gpx content to output file:
		print("Creating the following template: {}, with output file name: {}".format(gpx_content, self.output_file))
		# self.create_csv(self.output_file, gpx_content)
		self.create_output_file(self.output_file, gpx_content)
		print("File created!")

		return


def main_gpx(input_file):
	"""
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	Main function for creating GPX file from lat/lon CSV data
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""
	handler = GPSDataHandler(input_file)

	print("Create GPX file {} from CSV data in {}".format(handler.output_file, handler.input_file))

	handler.create_gpx_from_csv()

	print("GPX file successfully created!")

	return



def main():
	"""
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	Main function for plotting GPS data, detecting peaks, etc.
	++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	If being run by user as standalone script,
	take the following inputs:
	e.g., python plot_lat_lon.py [filename] [xheader] [yheader] [function] [xmin, optional] [xmax, optional] [ymin, optional] [ymax, optional]
	functions: 
		+ plotxy - plots [xheader] vs [yheader] from [filename] csv.
		+ utm_csv - converts lat/lons to utm, adds utm data to input csv and saves to disk.
		+ analyze_turn_tests - for turn tests; gets peaks and troughs in time window,
			average min/maxes, other stats (probably).
		+ gmap_plot - plot lat/lons on a google maps page.
	"""
	if sys.argv[2] == "to_dec":
		gps = GPSPlot()
		data = gps.upload_csv(sys.argv[1])
		easting_index = 8
		northing_index = 9
		zone_number = 17
		zone_letter = "N"

		_declatlon_list = []  # format: list(list[lat, lon])
		for item in data[1:]:
			_latlon = []
			_easting = item[easting_index].split('(')[0]
			print("easting: {}".format(_easting))
			_northing = item[northing_index]
			print("northing: {}".format(_northing))
			_latlondec = utm.to_latlon(float(_easting), float(_northing), zone_number, zone_letter)
			_declatlon_list.append([_latlondec[0], _latlondec[1]])  # list of list items of lat,lon in dec

		print("creating a file for updated data!")

		fileout = open('lat_lon_decimals.csv', 'w')
		for item in _declatlon_list:
			fileout.write("{}, {}\n".format(item[0], item[1]))
		fileout.close()

	else:

		# Get arguments and build GPSPlot class instance:
		gps_plot = GPSPlot()
		gps_plot.filename = sys.argv[1]
		gps_plot.xheader = sys.argv[2]
		gps_plot.yheader = sys.argv[3]

		_csv_data = gps_plot.upload_csv(gps_plot.filename)  # upload csv data of filename
		_func = sys.argv[4]

		# _axes_range = [None, None, None, None]  # [xmin, xmax, ymin, ymax]
		_axes_range = []

		# check for provided range (todo: handle Nones):
		if len(sys.argv) > 5:
			# assuming x/y min/max ranges are set..
			_axes_range.append(sys.argv[5])
			_axes_range.append(sys.argv[6])
			_axes_range.append(sys.argv[7])
			_axes_range.append(sys.argv[8])
			print("Axes range: {}".format(_axes_range))


		print("Requested function: {}".format(_func))


		if _func == 'utm_csv':
			_csv_data = gps_plot.add_utm_to_csvdata(_csv_data)
			_fileout_name = "{}_utm.csv".format(self.filename.split(".")[0])  # filename --> inputfile + "_utm.cscv"
			gps_plot.create_csv(_fileout_name, _csv_data)
			print ("file: {} created..".format(_fileout_name))

		# plot xheader col vs yheader col:
		elif _func == 'plotxy':

			print("entering plotxy function..")
			print("Axes range: {}".format(_axes_range))

			if _axes_range and len(_axes_range) == 4:
				plt.xlim(float(_axes_range[0]), float(_axes_range[1]))
				print("set x range from {} to {}".format(_axes_range[0], _axes_range[1]))

				plt.ylim(float(_axes_range[2]), float(_axes_range[3]))
				print("set y range from {} to {}".format(_axes_range[2], _axes_range[3]))

			_plot_data = gps_plot.plotxy(_csv_data, gps_plot.xheader, gps_plot.yheader)  # plot obj.x/yheader
			print("plot data parsed, now making plot..")

			plt.plot(_plot_data['xarray'], _plot_data['yarray'])  # other options, titles, ranges???
			plt.ylabel(gps_plot.yheader)
			plt.xlabel(gps_plot.xheader)
			plt.grid(True)




			#################################################################################
			# Inserting temporary code segment for adding lines to turn tests data.			#
			# This is to help determine some good lines to test the pure pursuit algorithm.	#
			#################################################################################
			_csv_data = gps_plot.upload_csv('Data/2018-01-23/pure_pursuit_line_test_1.csv')  # upload csv data of filename
			_plot_data = gps_plot.plotxy(_csv_data, 'easting', 'northing')
			plt.plot(_plot_data['xarray'], _plot_data['yarray'], 'go')  # plot line as green dots




			# title is filename without file extension!
			_title = gps_plot.filename[0:gps_plot.filename.index(".")]
			plt.title("Turn Tests 10-04-2017 (5min Single Avg)")
			# plt.title(gps_plot.filename)
			# plt.title("{} vs {}".format(gps_plot.yheader, gps_plot.xheader))
			plt.show()  # display plot!

		elif _func == 'findpeaks':
			# finds peaks of data, returns list of them
			_plot_data = gps_plot.find_peaks(_csv_data, gps_plot.xheader, gps_plot.yheader, _axes_range)

			_x_array = _plot_data.get('xarray')
			_y_array = _plot_data.get('yarray')
			_xmaximas = _plot_data.get('xmaximas')
			_ymaximas = _plot_data.get('ymaximas')
			_xminimas = _plot_data.get('xminimas')
			_yminimas = _plot_data.get('yminimas')

			print("y-minimas: {}".format(_yminimas))
			print("y-maximas: {}".format(_ymaximas))
			print("x-minimas: {}".format(_xminimas))
			print("x-maximas: {}".format(_xmaximas))

			# now plot xy w/ peaks:
			plt.plot(_x_array, _y_array, _xmaximas, _ymaximas, 'g^', _xminimas, _yminimas, 'bv')  # other options, titles, ranges???
			plt.ylabel(gps_plot.yheader)
			plt.xlabel(gps_plot.xheader)
			plt.grid(True)

			plt.title("Turn Tests 10-04-2017 (5min Single Avg)")
			plt.show()  # display plot!




if __name__ == '__main__':
	
	# Run original code, plots data, reads/writes CSVs, plots/detects data min/maxes
	main()

	# Converts CSV lat/lon file into GPX template (input: name of input file)
	# main_gpx(sys.argv[1])


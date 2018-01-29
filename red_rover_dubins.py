"""
++++++++++++++++++++
+ Red Rover Dubins +
++++++++++++++++++++

A version of the red rover model using the Dubins curves.
The idea is to use the Dubins model alongside interp1d and savitzky
golay filtering to create a smooth path-following algorithm.

Links:
  + https://github.com/AndrewWalker/Dubins-Curves
  + https://github.com/AndrewWalker/pydubins
  + https://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.interpolate.interp1d.html
  + http://scipy-cookbook.readthedocs.io/items/SavitzkyGolay.html

pydubins README: This software finds the shortest paths between configurations
for the Dubins' car [Dubins57], the forward only car-like vehicle with a constrained
turning radius. A good description of the equations and basic strategies for doing
this are described in section 15.3.1 "Dubins Curves" of the book "Planning Algorithms" [LaValle06].
The approach used to find paths is based on the algebraic solutions published in [Shkel01].
However, rather than using angular symmetries to improve performance, the simpler
approach to test all possible solutions is used here. This code is primarily a Cython
wrapper of https://github.com/AndrewWalker/Dubins-Curves
"""

import red_rover_model
import numpy as np
from scipy.interpolate import interp1d # Different interface to the same function
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from algorithms import savitzky_golay
import matplotlib.pyplot as plt
import math
import dubins
import sys



sample_points = np.array([[ 6.55525 ,  3.05472 ],
	   [ 6.17284 ,  2.802609],
	   [ 5.53946 ,  2.649209],
	   [ 4.93053 ,  2.444444],
	   [ 4.32544 ,  2.318749],
	   [ 3.90982 ,  2.2875  ],
	   [ 3.51294 ,  2.221875],
	   [ 3.09107 ,  2.29375 ],
	   [ 2.64013 ,  2.4375  ],
	   [ 2.275444,  2.653124],
	   [ 2.137945,  3.26562 ],
	   [ 2.15982 ,  3.84375 ],
	   [ 2.20982 ,  4.31562 ],
	   [ 2.334704,  4.87873 ],
	   [ 2.314264,  5.5047  ],
	   [ 2.311709,  5.9135  ],
	   [ 2.29638 ,  6.42961 ],
	   [ 2.619374,  6.75021 ],
	   [ 3.32448 ,  6.66353 ],
	   [ 3.31582 ,  5.68866 ],
	   [ 3.35159 ,  5.17255 ],
	   [ 3.48482 ,  4.73125 ],
	   [ 3.70669 ,  4.51875 ],
	   [ 4.23639 ,  4.58968 ],
	   [ 4.39592 ,  4.94615 ],
	   [ 4.33527 ,  5.33862 ],
	   [ 3.95968 ,  5.61967 ],
	   [ 3.56366 ,  5.73976 ],
	   [ 3.78818 ,  6.55292 ],
	   [ 4.27712 ,  6.8283  ],
	   [ 4.89532 ,  6.78615 ],
	   [ 5.35334 ,  6.72433 ],
	   [ 5.71583 ,  6.54449 ],
	   [ 6.13452 ,  6.46019 ],
	   [ 6.54478 ,  6.26068 ],
	   [ 6.7873  ,  5.74615 ],
	   [ 6.64086 ,  5.25269 ],
	   [ 6.45649 ,  4.86206 ],
	   [ 6.41586 ,  4.46519 ],
	   [ 5.44711 ,  4.26519 ],
	   [ 5.04087 ,  4.10581 ],
	   [ 4.70013 ,  3.67405 ],
	   [ 4.83482 ,  3.4375  ],
	   [ 5.34086 ,  3.43394 ],
	   [ 5.76392 ,  3.55156 ],
	   [ 6.37056 ,  3.8778  ],
	   [ 6.53116 ,  3.47228 ]])



def interp1d_example_1():
	"""
	Borrowing from algorithms/interp1d_example.py, this function
	will use the same setup, but with GPS data instead of a random
	set of points.
	"""

	# This code segment reads in a csv file of gps data to use for modeling:
	# # 1. Read in GPS points from peanut field data:
	# # filename = 'Data/2017-10-04/turn_test_5min_single_avg_20171004_fix_utm.csv'  # input csv filename
	# filename = 'Data/2017-09-20/gps_field_test_fixtopic_20170920_reduced_utm.csv'
	# t_header, x_header, y_header = 'field.header.seq', 'easting', 'northing'  # header declarations
	# t_arr, x_arr, y_arr = red_rover_model.get_data_from_csv(filename, t_header, x_header, y_header, 2)  # path arrays
	# xy_pairs = zip(x_arr, y_arr)  # aggregating lists to convert to np.array
	# sample_points = np.array(xy_pairs)  # converts [(x1,y1), (x2,y2), ..] xy_pairs to np.array type, hopefully

	x, y = sample_points.T
	i = np.arange(len(sample_points))

	#You can try Rbf, fitpack2 method
	# 8x the original number of points
	# interp_i = np.linspace(0, i.max(), 8 * i.max())
	interp_i = np.linspace(0, i.max(), 2 * i.max())

	#use interp1d to increase data points
	xi = interp1d(i, x, kind='cubic')(interp_i)
	yi = interp1d(i, y, kind='cubic')(interp_i)
	# f = interp1d(x, y, kind='cubic')

	#use this savitzky filter from http://scipy-cookbook.readthedocs.io/items/SavitzkyGolay.html
	# yhat = savitzky_golay.savitzky_golay(yi, 31, 5) # window size 51, polynomial order 3
	yhat = savitzky_golay.savitzky_golay(y, 5, 3)
	yhat_interp = savitzky_golay.savitzky_golay(yi, 5, 3)

	plot_interp1d_example(x, y, xi, yi, yhat, yhat_interp)  # plot paths


def plot_interp1d_example(x, y, xi, yi, yhat, yhat_interp):

	# Plot all sorts of points and lines:
	# points_1, = plt.plot(xi, yi, 'mo', label='interp1d(x) vs. interp1d(y) points', markersize=5)
	path_1, = plt.plot(xi, yi, 'm', label='int(x) vs. int(y)')
	path_2, = plt.plot(x, yhat, 'c', label='x vs. sav(y)')
	path_3, = plt.plot(xi, yhat_interp, 'b', label='int(x) vs. sav(int(y))')
	points_2, = plt.plot(x, y, 'ko', markersize=8)  # original as black dots
	points_3, = plt.plot(x[0], y[0], 'go', markersize=10)  # starting point as green dot
	points_4, = plt.plot(x[-1], y[-1], 'ro', markersize=10)  # end point as red dot

	# Setup legends for plots:
	# legend_1 = plt.legend(handles=[line1], loc=1)\
	legends = plt.legend(bbox_to_anchor=(0.5, 1), loc=2, borderaxespad=0.)

	plt.show()


def plot_dubins_path(qs, q0, q1):
		"""
		Plots the dubins path between a starting and ending point.
		Inputs:
			qs - dubins path data [[x,y,angle], ..]
			q0 - initial position [x,y,angle]
			q1 - target position [x,y,angle]
		Returns: None
		"""
		xs = qs[:,0]
		ys = qs[:,1]
		us = xs + np.cos(qs[:, 2])
		vs = ys + np.sin(qs[:, 2])
		plt.plot(q0[0], q0[1], 'gx', markeredgewidth=4, markersize=10)  # actual start point
		plt.plot(q1[0], q1[1], 'rx', markeredgewidth=4, markersize=10)  # actual end point
		plt.plot(xs, ys, 'b-')
		plt.plot(xs, ys, 'r.')
		plt.plot(qs[0][0], qs[0][1], 'go', markersize=5)  # dubins start point
		plt.plot(qs[-1][0], qs[-1][1], 'ro', markersize=5)  # dubins end point
		plt.plot(sample_points[:,0], sample_points[:,1], 'k-')  # plot sample points path
		for i in xrange(qs.shape[0]):
			plt.plot([xs[i], us[i]], [ys[i], vs[i]],'r-')
		plt.show()


def plot_full_dubins_path(qs_array):
	"""
	Like plot_dubins_path() function, but plots a full set of points
	instead a single A -> B two point dataset.
	"""
	# Initial setup: No directional plotting, just dots and path at the moment..
	for qs in qs_array:
		xs = qs[:,0]
		ys = qs[:,1]
		plt.plot(xs, ys, 'b-')
		plt.plot(xs, ys, 'r.')
	plt.show()


def build_dubins_points(points):
	"""
	Takes sample points, which are a list of lists, and
	converts them to a tuple with an additional element for 
	vehicle orientation.
	"""
	dubins_path = []
	for xypair in points:
		dubin_pt = (xypair[0], xypair[1], 0.0)  # todo: not just default 0 for angle
		dubins_path.append(dubin_pt)  # add dubin point tuple to list
	return dubins_path


def dubins_example_1():
	"""
	A simple example of the dubins model
	"""
	# Original q0, q1 from simple dubins example:
	# q0 = (0.0, 0.0, math.pi/4)  # initial configuration
	# q1 = (-4.0, 4.0, -math.pi)  # final configuration

	turning_radius = 2.5  # min turning radius? (.pyx file just says 'turning radius')
	step_size = 0.5  # sampling interval

	dubin_path = build_dubins_points(sample_points)

	qs_array = []  # an array of qs of type np.array

	# # Testing dubins model for path instead of just
	# # a single point A -> B test:
	# for i in range(0, len(dubin_path) - 1):

	# 	q0 = dubin_path[i]
	# 	q1 = dubin_path[i + 1]

	# 	print("q0, q1: {}, {}".format(q0, q1))

	# 	qs,_ = dubins.path_sample(q0, q1, turning_radius, step_size)
	# 	qs = np.array(qs)

	# 	qs_array.append(qs)

	# plot_full_dubins_path(qs_array)


	#############################################################
	# Original, working intial example of Dubins with 2 points: #
	#############################################################
	# Trying to use sample_points now for dubins example.
	# I'm still a little baffled by only having a start and end point for the model.
	q0 = (sample_points[0][0], sample_points[0][1], math.pi/4.0)
	q1 = (sample_points[-1][0], sample_points[-1][1], -math.pi)
	turning_radius = 2.5  # min turning radius? (.pyx file just says 'turning radius')
	step_size = 0.5  # sampling interval
	print("q0, q1: {}, {}".format(q0, q1))
	qs, _ = dubins.path_sample(q0, q1, turning_radius, step_size)
	qs = np.array(qs)
	print("Dubins qs: {}".format(qs))
	plot_dubins_path(qs, q0, q1)



if __name__ == '__main__':

	model = sys.argv[1]  # get model name from command line

	print("Running {} model..".format(model))

	if model == 'interp1d':
		interp1d_example_1()  # run interp1d example 1
	
	elif model == 'dubins':
		dubins_example_1()  # run dubins example 1

	print("Finished running {} model..".format(model))
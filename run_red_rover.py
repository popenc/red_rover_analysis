"""
The controller for the different red rover models.

This module shares all the static content for running
a model scenario, and executes the model using a terminal
argument, e.g., "python run_red_rover.py dubins" runs the
dubins model for a given scenario hardcoded in this module.
"""

import sys
import math
import matplotlib.pyplot as plt
import red_rover_dubins
import red_rover_model
import red_rover_analysis




class RedRoverController(object):

	def __init__(self):
		self.model_names = ['simple', 'interp1d', 'dubins', 'combined', 'test_path']

	def create_straight_path(self, spacing, num_points, row=1):
		"""
		Creates a straight line of num_points of given 
		spacing between them.
		"""
		x_array, y_array = [], []
		for i in range(1, num_points, spacing):
			x_array.append(row)  # NOTE: straight line at x=1m
			y_array.append(i)
		return x_array, y_array

	def create_straight_rows(self, spacing, num_points, row_spacing, num_rows):
		"""
		Similar to the create_straight_path function, 
		but with parallel rows.

		Inputs:
		  + spacing - spacing of points in a row.
		  + num_points - num of points per row.
		  + row_spacing - spacing between rows.
		  + num_rows - number of rows.
		"""
		x_array, y_array = [], []
		for i in range(0, num_rows):
			xrow, yrow = self.create_straight_path(spacing, num_points, row=i*row_spacing	)
			x_array += xrow
			y_array += yrow
		return x_array, y_array

	def test_path(self, x_path, y_path):
		"""
		Plots path to check how it looks before using
		"""
		plt.plot(x_path, y_path, 'bo')
		plt.plot(x_path, y_path, 'b-')
		plt.show()


if __name__ == '__main__':

	_model_name = sys.argv[1]  # get model name from terminal
	_rrc_obj = RedRoverController()  # create instance of RRC

	# Raise error if no model name specified:
	if _model_name not in _rrc_obj.model_names:
		_err_msg = "Enter a model name: {}".format(_rrc_obj.model_names)
		raise KeyError(_err_msg)


	# x_path, y_path = _rrc_obj.create_straight_path(1, 10)  # path to follow
	x_path, y_path = _rrc_obj.create_straight_rows(1, 2, 6, 1)  # path to follow

	initial_pos = (2, -5, math.pi/2.0)  # initial rover position
	final_pos = (x_path[-1], y_path[-1] + 1, (3*math.pi)/2.0)  # final rover position

	if _model_name == 'simple':
		# red_rover_model.run_red_rover_model(2, 2)  # inputs: look-ahead, gps row step size
		red_rover_model.run_red_rover_model(initial_pos, final_pos, x_path, y_path)

	elif _model_name == 'interp1d':
		red_rover_dubins.interp1d_example_1()

	elif _model_name == 'dubins':
		red_rover_dubins.dubins_example_1(initial_pos, final_pos, x_path, y_path)

	elif _model_name == 'combined':
		red_rover_dubins.combined_savitzky_dubins_example()

	elif _model_name == 'test_path':
		_rrc_obj.test_path(x_path, y_path)

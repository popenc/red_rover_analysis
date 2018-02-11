"""
The controller for the different red rover models.

This module shares all the static content for running
a model scenario, and executes the model using a terminal
argument, e.g., "python run_red_rover.py dubins" runs the
dubins model for a given scenario hardcoded in this module.
"""

import sys
import red_rover_dubins
import red_rover_model
import red_rover_analysis




class RedRoverController(object):

	def __init__(self):
		self.model_names = ['basic', 'interp1d', 'dubins']


if __name__ == '__main__':

	_model_name = sys.argv[1]  # get model name from terminal
	_rrc_obj = RedRoverController()  # create instance of RRC

	# Raise error if no model name specified:
	if _model_name not in _rrc_obj.model_names:
		raise """Enter a model name, e.g., 'python run_red_rover.py dubins'. \n 
			Model names: {}""".format(_rrc_obj.model_names)

	if _model_name == 'basic':
		red_rover_model.run_red_rover_model(2, 2)  # inputs: look-ahead, gps row step size

	elif _model_name == 'interp1d':
		red_rover_dubins.interp1d_example_1()

	elif _model_name == 'dubins':
		red_rover_dubins.dubins_example_1()

	elif _model_name == 'combined':
		red_rover_dubins.combined_savitzky_dubins_example()

"""
The controller for the different red rover models.

This module shares all the static content for running
a model scenario, and executes the model using a terminal
argument, e.g., "python run_red_rover.py dubins" runs the
dubins model for a given scenario hardcoded in this module.
"""

import sys
import math
import utm
import rospy
import math
import matplotlib.pyplot as plt
import red_rover_dubins
import red_rover_model
import red_rover_analysis




class RedRoverController(object):

	def __init__(self):
		self.model_names = ['simple', 'interp1d', 'dubins', 'combined', 'test_path']

		# NOTE: Test with just first two points, then try full path:
		self.eng_annex_goals_1 = [[259742.1089532437, 3485056.983515083],  # Set of goals from 4-5-18 eng. annex test row
						[259739.9971399921, 3485057.0322162253]]
						# [259737.0933967415, 3485057.0991809973],
						# [259733.65459685936, 3485056.8703144793],
						# [259729.15988999663, 3485056.665800806],
						# [259726.22773249005, 3485055.5007375698],
						# [259721.68329927392, 3485053.1401727293],
						# [259717.40284074377, 3485050.7735215155],
						# [259713.1223801818, 3485048.406871946]]

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

	def transform_angle_by_quadrant(self, initial_angle, x_diff, y_diff):
		"""
		Takes the change in X and Y to determine how the Jackal
		should turn.
		"""
		if x_diff > 0 and y_diff > 0:
			print("p1 in quadrant: {}".format(1))
			# Point B in quadrant 1..
			return math.degrees(initial_angle)
		elif x_diff < 0 and y_diff > 0:
			print("p1 in quadrant: {}".format(2))
			# Point B in quadrant 2..
			return 180 - math.degrees(initial_angle)
		elif x_diff < 0 and y_diff < 0:
			print("p1 in quadrant: {}".format(3))
			# Point B in quadrant 3..
			return 180 + math.degrees(initial_angle)
		elif x_diff > 0 and y_diff < 0:
			print("p1 in quadrant: {}".format(4))
			# Point B in quadrant 4..
			return 360 - math.degrees(initial_angle)
		elif x_diff == 0 and y_diff == 0:
			# No change in angle..
			return 0.0
		else:
			raise "!Error occurred in basic_drive_3/transform_angle_by_quadrant func.."


	# def call_jackal_pos_service(self, distance):
	# 	"""
	# 	Get current GPS fix from Jackal's position
	# 	"""
	# 	rospy.wait_for_service('get_jackal_pos')
	# 	get_jackal_pos = rospy.ServiceProxy('get_jackal_pos', JackalPos)
	# 	return get_jackal_pos(distance)


if __name__ == '__main__':

	_model_name = sys.argv[1]  # get model name from terminal
	_rrc_obj = RedRoverController()  # create instance of RRC

	# Raise error if no model name specified:
	if _model_name not in _rrc_obj.model_names:
		_err_msg = "Enter a model name: {}".format(_rrc_obj.model_names)
		raise KeyError(_err_msg)

	# Creating a path:
	# x_path, y_path = _rrc_obj.create_straight_rows(1, 2, 6, 1)  # path to follow
	# initial_pos = (2, -5, math.pi/2.0)  # initial rover position
	# final_pos = (x_path[-1], y_path[-1] + 1, (3*math.pi)/2.0)  # final rover position


	# current_position = _rrc_obj.call_jackal_pos_service(0)
	# lat = curr_pose.jackal_fix.latitude
	# _lon = curr_pose.jackal_fix.longitude
	# print("Jackal's current lat, lon: {}, {}".format(_lat, _lon))
	# curr_pose_utm = utm.from_latlon(curr_pose.jackal_fix.latitude, curr_pose.jackal_fix.longitude)


	# Engineering annex goals 1:
	goals_list = _rrc_obj.eng_annex_goals_1
	x_path, y_path = [], []
	for xygoal in goals_list:
		x_path.append(xygoal[0])
		y_path.append(xygoal[1])

	initial_angle = math.radians(150)

	initial_xy = (259746.13804448023, 3485055.429863461, None)
	final_pos = (x_path[-1], y_path[-1], math.pi)

	x_diff = x_path[0] - initial_xy[0]
	y_diff = y_path[0] - initial_xy[1]

	# _trans_angle = self.transform_imu_frame(degrees(A[2]))
	AB_theta0 = math.atan2(abs(y_diff), abs(x_diff))  # get intitial angle, pre transform
	AB_angle = _rrc_obj.transform_angle_by_quadrant(AB_theta0, x_diff, y_diff)  # determine angle between vector A and B
	
	turn_angle = AB_angle - initial_angle  # angle to turn (signage should denote direction to turn)

	initial_pos = (initial_xy[0], initial_xy[1], turn_angle)


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

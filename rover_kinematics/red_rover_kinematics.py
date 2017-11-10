"""
This module is intended for developing a test setup for the
kinematics of the red rover.

Phase 1 - Simple plots of radii based on angle.
Phase 2 - Determining left or right turn based on position and reference point.
Phase 3 - Point following with python.
Phase 4 - A dynamic model using ROS (kind of like the turtlesim example)
"""

import matplotlib.pyplot as plt
import numpy as np
import sys



class RoverKinematics(object):
	"""
	Building a path-following algorithm, starting simple as possible
	and moving toward more complexity.
	"""

	def __init__(self):

		self.rover_pos = None
		self.ref_pos = None
		self.left_a = 27.974966981  # constant for left turn equation
		self.left_b = 0.7213692582  # contstant for left turn equation
		self.right_a = 26.2074918622  # constant for right turn equation
		self.right_b = 0.7724722082  # constant for right turn equation


	def calculate_radius(self, angle, direction):
		"""
		Calculates radius based on turn equation and direction
		"""
		if direction == "left":
			return self.left_a * angle**-self.left_b
		if direction == "right":
			return self.right_a * angle**-self.right_b
		else:
			return None


	def calculate_angle(self, radius, direction):
		"""
		Calculates angle based on turn equation and direction
		"""
		if direction == "left":
			return (self.left_a / radius)**(1.0/self.left_b)
		if direction == "right":
			return (self.right_a / radius)**(1.0/self.right_b)
		else:
			return None


	def simplest_pursuit(self, rover_pos, ref_pos):
		"""
		Given the rover's location, the x and y distance from
		the reference point is returned.

		rover_pos - initially assuming rover, [0,0]
		ref_pos - reference point position, [x,y]
		"""
		_x_diff = abs(ref_pos[0] - rover_pos[0])
		_y_diff = abs(ref_pos[1] - rover_pos[1])

		_turn_obj = self.determine_turn_direction(rover_pos, ref_pos)  # get direction of turn
		_turn_radius = (_x_diff**2 + _y_diff**2) / (2.0 * _x_diff)  # turn radius equation from pure pursuit paper
		_turn_angle = (_turn_obj['a'] / _turn_radius)**(1.0 / _turn_obj['b'])  # determine angle to turn to acheive given radius

		print("Turn direction: {}, radius: {}, angle: {}".format(_turn_obj['turn'], _turn_radius, _turn_angle))

		return _turn_angle


	def determine_turn_direction(self, rover_pos, ref_pos):
		"""
		Determines if rover should turn left or right
		based on it's position relative to a reference point
		"""
		_rov_pos_x = rover_pos[0]  # get x position of rover
		_ref_pos_x = ref_pos[0]  # get x position of ref pt

		# initial algorithm not using coords or utm, just
		# assuming rover pos is origin..

		_x_diff = _ref_pos_x - _rov_pos_x

		if _x_diff < 0:
			# ref pos is left of rover
			return {'a': self.left_a, 'b': self.left_b, 'turn': "left"}
		elif _x_diff > 0:
			# ref pos is right of rover
			return {'a': self.right_a, 'b': self.right_b, 'turn': "right"}
		else:
			# ref pos straight ahead
			return None


	def plot_turn(self, radius):
		"""
		Plots the turn radius
		"""
		theta = np.linspace(0, 2*np.pi, 100)

		# the radius of the circle
		r = radius

		# compute x1 and x2
		x1 = radius*np.cos(theta)
		x2 = radius*np.sin(theta)

		# create the figure
		fig, ax = plt.subplots(1)
		ax.plot(x1, x2)
		ax.set_aspect(1)
		plt.grid(True)
		plt.show()







if __name__ == '__main__':
	"""
	Run on the command line
	E.g., python red_rover_kinematics.py 5.1 left -- turn left at 5.1 deg angle
	"""
	_angle = float(sys.argv[1])
	_turn_dir = sys.argv[2]
	_rover = RoverKinematics()

	_turn_radius = _rover.calculate_radius(_angle, _turn_dir)

	if _turn_radius:
		print("Plotting turn radius: {} at {} degree angle".format(_turn_radius, _angle))
		_rover.plot_turn(_turn_radius)

	else:
		print("Error getting turn radius..")
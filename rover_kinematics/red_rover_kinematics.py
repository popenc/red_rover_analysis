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
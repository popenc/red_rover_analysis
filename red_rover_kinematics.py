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
		
		self.left_a = 27.974966981  # constant for left turn equation
		self.left_b = 0.7213692582  # contstant for left turn equation
		self.right_a = 26.2074918622  # constant for right turn equation
		self.right_b = 0.7724722082  # constant for right turn equation


	# def calculate_radius(self, angle, direction):
	# 	"""
	# 	Calculates radius based on turn equation and direction
	# 	"""
	# 	if direction == "left":
	# 		return self.left_a * angle**-self.left_b
	# 	if direction == "right":
	# 		return self.right_a * angle**-self.right_b
	# 	else:
	# 		return None
	def calculate_radius(self, rover_pos, ref_pos):
		"""
		Calculates radius based on pure pursuit paper
		"""
		_x_diff = abs(ref_pos[0] - rover_pos[0])
		_y_diff = abs(ref_pos[1] - rover_pos[1])
		return (_x_diff**2 + _y_diff**2) / (2.0 * _x_diff)


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


	def determine_turn_direction(self, rover_pos, ref_pos):
		"""
		Determines if rover should turn left or right
		based on it's position relative to a reference point.
		"""

		# initial algorithm not using coords or utm, just
		# assuming rover pos is origin..

		_x_diff = ref_pos[0] - rover_pos[0]

		if _x_diff < 0:
			# ref pos is left of rover
			return "left"
		elif _x_diff > 0:
			# ref pos is right of rover
			return "right"
		else:
			# ref pos straight ahead
			return None


	def plot_turn(self, radius):
		"""
		Plots the turn radius
		"""
		theta = np.linspace(0, 2*np.pi, 100)

		# compute x1 and x2
		x1 = radius*np.cos(theta)
		x2 = radius*np.sin(theta)

		# create the figure
		fig, ax = plt.subplots(1)
		ax.plot(x1, x2)
		ax.set_aspect(1)
		plt.grid(True)
		plt.show()


	def plot_turn_to_ref(self, plot_data):
		"""
		Plots rover as dot, ref point, then turn
		radius rover takes to ref point.
		"""

		# rover point pair:
		x_rov = plot_data['rover_pos'][0]
		y_rov = plot_data['rover_pos'][1]

		# reference point pair:
		x_ref = plot_data['ref_pos'][0]
		y_ref = plot_data['ref_pos'][1]

		theta = np.linspace(0, 2*np.pi, 100)
		plot_data['y_turn'] = plot_data['radius'] * np.sin(theta)

		if plot_data['direction'] == "left":
			plot_data['x_turn'] = plot_data['radius'] * np.cos(theta) - plot_data['radius']
		elif plot_data['direction'] == "right":
			plot_data['x_turn'] = plot_data['radius'] * np.cos(theta) + plot_data['radius']

		plt.plot([x_rov], [y_rov], 'ro', [x_ref], [y_ref], 'bo', plot_data.get('x_turn'), plot_data.get('y_turn'))
		plt.axis([-10, 10, -10, 10])
		plt.show()

		return




if __name__ == '__main__':
	"""
	Run on the command line.
	Using a ref point and equations from pure pursuit paper.
	"""

	_ref_pos = [float(sys.argv[1]), float(sys.argv[2])]  # [x,y] ref point
	_rover_pos = [0,0]  # Assuming rover at 0,0
	
	print("Rover position: {}".format(_rover_pos))
	print("Reference point: {}".format(_ref_pos))

	_rover = RoverKinematics()

	_direction = _rover.determine_turn_direction(_rover_pos, _ref_pos)
	_radius = _rover.calculate_radius(_rover_pos, _ref_pos)
	_angle = _rover.calculate_angle(_radius, _direction)

	_plot_data = {
		'rover_pos': _rover_pos,
		'ref_pos': _ref_pos,
		'direction': _direction,
		'radius': _radius,
		'angle': _angle
	}

	print("Plot data: {}".format(_plot_data))

	_rover.plot_turn_to_ref(_plot_data)
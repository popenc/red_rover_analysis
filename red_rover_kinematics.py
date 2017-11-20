"""
This module is intended for developing a test setup for the
kinematics of the red rover.

Phase 1 - Simple plots of radii based on angle.
Phase 2 - Determining left or right turn based on position and reference point.
Phase 3 - Point following with python.
Phase 4 - A dynamic model using ROS (kind of like the turtlesim example)
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
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

		# pyplot graph settings:
		self.graph_xmin = -50
		self.graph_xmax = 50
		self.graph_ymin = -50
		self.graph_ymax = 50

		self.look_ahead_radius = 0.5  # radius around ref pt for rover to start calculating next turn

		self.rover_left_turn_max = 24.8  # max left turning angle from turn tests
		self.rover_right_turn_max = 22.1  # max right turning angle from turn tests

		self.rover_left_radius_min = 2.26  # min left turn radius for rover, in meters
		self.rover_right_radius_min = 2.25  # min right turn radius in meters

		self.angle_increment = 5  # divide up angle from pt->pt by this much


	def calculate_radius(self, ref1, ref2):
		"""
		Calculates radius based on pure pursuit paper
		"""
		_x_diff = abs(ref2[0] - ref1[0])
		_y_diff = abs(ref2[1] - ref1[1])

		if _x_diff == 0:
			return 0

		return (_x_diff**2 + _y_diff**2) / (2.0 * _x_diff)


	def calculate_rover_pivot(self, radius, direction):
		"""
		Calculates angle based on turn equation and direction
		"""
		if direction == "left":
			return (self.left_a / radius)**(1.0/self.left_b)
		if direction == "right":
			return (self.right_a / radius)**(1.0/self.right_b)
		else:
			return None

	def calculate_angle(self, radius, step_distance):
		"""
		Different than "calculate_rover_pivot", which is the angle
		of the Rover's pivot as it turns. This angle is calculated
		b/w the points and is based off the law the cosines.
		"""
		return np.arccos(1 - (step_distance**2 / (2*radius**2)))


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


	def build_turn_plot_data(self, plot_data):

		_refs_list = plot_data.get('ref_pos_list', [])
		# _theta = np.linspace(0, 2*np.pi, 100)
		_turn_plots = []  # list of [x,y] for plotting turns

		for i in range(0, len(_refs_list) - 1):

			_ref1 = _refs_list[i]  # initial position [x,y]
			_ref2 = _refs_list[i + 1]  # destination position [x,y]
			_radius = plot_data['radius_list'][i]
			_turn = None

			if plot_data['direction_list'][i] == "left":
				# _xturn = plot_data['radius_list'][i] * np.cos(theta) - plot_data['radius_list'][i]
				_turn = plt.Circle((_ref1[0] - _radius, _ref1[1]), _radius, color='g', fill=False)
			elif plot_data['direction_list'][i] == "right":
				_turn = plt.Circle((_ref1[0] + _radius, _ref1[1]), _radius, color='g', fill=False)
				# _xturn = plot_data['radius_list'][i] * np.cos(theta) + plot_data['radius_list'][i]

			_turn_plots.append(_turn)

		return _turn_plots


	def plot_turn_to_ref(self, plot_data):
		"""
		Plots rover as dot, ref point, then turn
		radius rover takes to ref point.
		"""

		_refs_list = plot_data.get('ref_pos_list', [])

		ax = plt.gca()  # get axes instance from plot
		_xref_array, _yref_array = [], []

		_turn_plots = self.build_turn_plot_data(plot_data)

		for _turn in _turn_plots:
			ax.add_patch(_turn)  # adding turns to plot

		for ref_pair in _refs_list[1:]:
			# loop ref points, skipping rover position

			# Building reference points plot arrays ([x1,x2,..], [y1,y2,..]):
			_xref_array.append(ref_pair[0])
			_yref_array.append(ref_pair[1])

			# Creating look-adhead radius around ref point: 
			_halo = plt.Circle((ref_pair[0], ref_pair[1]), self.look_ahead_radius, color='b', fill=False, linestyle='dashed')
			ax.add_patch(_halo)

		plt.plot(
			[_refs_list[0][0]], [_refs_list[0][1]], 'rs',  # plots rover position
			_xref_array, _yref_array, 'bo',  # plots reference points
			plot_data.get('x_turn'), plot_data.get('y_turn'),  # plots first turn radius
		)

		plt.axis([self.graph_xmin, self.graph_xmax, self.graph_ymin, self.graph_ymax])
		plt.grid(True)
		plt.show()

		return


		



if __name__ == '__main__':
	"""
	Run on the command line.
	Using a ref point and equations from pure pursuit paper.
	"""

	# _ref_pos = [float(sys.argv[1]), float(sys.argv[2])]  # [x,y] ref point as command-line input
	_rover_pos = [2, 3]  # Assuming rover at 0,0
	_end_pos = [-15, 20]
	_ref_pos_list = [[5, 6], [6, 10], [5.5, 15]]  # now trying two hardcoded ref points - beginnings of straight line

	_rover = RoverKinematics()

	_plot_data = {
		'rover_pos': _rover_pos,
		'ref_pos': _ref_pos_list[0],
		'ref_pos_list': _ref_pos_list,
		'direction_list': [],  # turn direction to each ref point
		'radius_list': [],  # radius of turn to each ref point
		'angle_list': [],  # turn angle to each ref point
		'path': [],
	}

	_ref_pos_list.insert(0, _rover_pos)  # add rover position to beginning of ref points list..

	_x_path, _y_path = [], []
	_xrefs, _yrefs = [], []

	# Looping reference points:
	# for _ref_pos in _ref_pos_list:
	for i in range(0, len(_ref_pos_list) - 1):

		_ref1 = _ref_pos_list[i]
		_ref2 = _ref_pos_list[i + 1]

		_xrefs.append(_ref2[0])  # start at ref2 since 1st point is rover
		_yrefs.append(_ref2[1])

		_direction = _rover.determine_turn_direction(_ref1, _ref2)  # determine turn direction to ref point
		_radius = _rover.calculate_radius(_ref1, _ref2)  # calculate turn radius to ref point

		# Have to calculate d before _angle above!!!
		_d = np.sqrt((_ref2[0] - _ref1[0])**2 + (_ref2[1] - _ref1[1])**2)
		_angle = _rover.calculate_angle(_radius, _d)  # calculate initial angle

		print("Calculated distance b/w points: {}".format(_d))
		print("Calulated angle: {}".format(_angle))

		# Initial position:
		_x = _ref1[0]
		_y = _ref1[1]

		print("Initial position: {}".format(_ref1))
		print("Ref points: {}".format(_ref_pos_list))
		print("Direction for turn 1: {} \nRadius: {} \nAngle: {}".format(_direction, _radius, _angle))
		print("Incrementing angles by: {} degrees".format(_angle / _rover.angle_increment))

		for i in range(1, _rover.angle_increment):

			_bin = i * (_angle / _rover.angle_increment)

			print("angle: {}".format(_bin))

			_x, _path = None, None
			if _direction == "right":
				_x = - _radius * np.cos(_bin) + _radius + _ref1[0]
				_path = _ref1[0] + _radius
			elif _direction == "left":
				_x = _radius * np.cos(_bin) - _radius + _ref1[0]
				_path = _ref1[0] - _radius
			
			_y = _radius * np.sin(_bin) + _ref1[1]

			_plot_data['direction_list'].append(_direction)
			_plot_data['radius_list'].append(_radius)
			_plot_data['angle_list'].append(_angle)

			_plot_data['path'].append([_x, _y])
			_x_path.append(_x)
			_y_path.append(_y)

		print("Plot data: {}".format(_plot_data))

		ax = plt.gca()
		_projected_path = plt.Circle((_path, _ref1[1]), _radius, color='b', fill=False, linestyle='dashed')
		ax.add_patch(_projected_path)

	plt.plot(
		_rover_pos[0], _rover_pos[1], 'rs',
		# _end_pos[0], _end_pos[1], 'go',
		_xrefs, _yrefs, 'go',
		_x_path, _y_path, 'bo'	  # plots reference points
	)

	plt.axis([_rover.graph_xmin, _rover.graph_xmax, _rover.graph_ymin, _rover.graph_ymax])
	plt.grid(True)
	plt.show()
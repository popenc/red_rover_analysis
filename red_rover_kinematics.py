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



class State:

    def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
        self.dt = 0.1  # [s]
        self.L = 2.9  # [m]
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v


    def update(self, state, a, delta):

        state.x = state.x + state.v * math.cos(state.yaw) *self.dt
        state.y = state.y + state.v * math.sin(state.yaw) *self.dt
        state.yaw = state.yaw + state.v / self.L * math.tan(delta) *self.dt
        state.v = state.v + a *self.dt

        return state



class RoverModel(object):
    """
    Building a path-following algorithm, starting simple as possible
    and moving toward more complexity.
    """

    def __init__(self):
        
        self.left_a = 27.974966981  # constant for left turn equation
        self.left_b = 0.7213692582  # constant for left turn equation
        self.right_a = 26.2074918622  # constant for right turn equation
        self.right_b = 0.7724722082  # constant for right turn equation

        # pyplot graph settings:
        self.graph_xmin = -50
        self.graph_xmax = 50
        self.graph_ymin = -50
        self.graph_ymax = 50

        # self.look_ahead_radius = 0.5  # radius around ref pt for rover to start calculating next turn
        self.look_ahead_distance = 1.5  # TODO: Get value(s) that make sense for this

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


    def calc_target_index(self, state, cx, cy):
        dx = [state.x - icx for icx in cx]
        dy = [state.y - icy for icy in cy]

        d = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in zip(dx, dy)]

        ind = d.index(min(d))

        L = 0.0

        while Lf > L and (ind + 1) < len(cx):
            dx = cx[ind + 1] - cx[ind]
            dy = cx[ind + 1] - cx[ind]
            L += math.sqrt(dx ** 2 + dy ** 2)
            ind += 1

        return ind


    def find_closest_point(self, state, cx, cy)
        """
        Finds closest point from rover in the path;
        this is the initial point the rover drives to.
        """

        dx = [state.x - icx for icx in cx]
        dy = [state.y - icy for icy in cy]

        d = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in zip(dx, dy)]

        ind = d.index(min(d))  # index of the point closest to the rover

        return ind


    # def plot_turn(self, radius):
    #   """
    #   Plots the turn radius
    #   """
    #   theta = np.linspace(0, 2*np.pi, 100)

    #   # compute x1 and x2
    #   x1 = radius*np.cos(theta)
    #   x2 = radius*np.sin(theta)

    #   # create the figure
    #   fig, ax = plt.subplots(1)
    #   ax.plot(x1, x2)
    #   ax.set_aspect(1)
    #   plt.grid(True)
    #   plt.show()






if __name__ == '__main__':
    """
    Run on the command line.
    Using a ref point and equations from pure pursuit paper.
    """

    _rover_pos = [2, 3]  # Assuming rover at 0,0
    # _ref_pos_list = [[5, 6], [6, 10], [5.5, 15]]  # now trying two hardcoded ref points - beginnings of straight line
    _ref_pos_list = [[6,15], [6.1, 25]]

    _rover = RoverModel()

    _ref_pos_list.insert(0, _rover_pos)  # add rover position to beginning of ref points list..

    _x_path, _y_path = [], []  # rover's path to ref points
    _xrefs, _yrefs = [], []  # reference points to follow

    _plot_data = {
        'rover_pos': _rover_pos,
        'ref_pos': _ref_pos_list[0],
        'ref_pos_list': _ref_pos_list,
        'direction_list': [],  # turn direction to each ref point
        'radius_list': [],  # radius of turn to each ref point
        'angle_list': [],  # turn angle to each ref point
        'path': [],
    }



    # target_speed = 0.447  # 1mph in m/s

    # T = 60.0  # max simulation time

    # state = State(x=x0, y=y0, yaw=0.0, v=0.0)

    # lastIndex = len(cx) - 1
    # time = 0.0
    # x = [state.x]
    # y = [state.y]
    # yaw = [state.yaw]
    # v = [state.v]
    # t = [0.0]

    # target_ind = calc_target_index(state, cx, cy)

    # while T >= time and lastIndex > target_ind:

    #     ai = PIDControl(target_speed, state.v)
    #     di, target_ind = pure_pursuit_control(state, cx, cy, target_ind)
    #     state = state.update(state, ai, di)

    #     time = time + state.dt

    #     x.append(state.x)
    #     y.append(state.y)
    #     yaw.append(state.yaw)
    #     v.append(state.v)
    #     t.append(time)




    # Looping reference points:
    for i in range(0, len(_ref_pos_list) - 1):

        _ref1 = _ref_pos_list[i]
        _ref2 = _ref_pos_list[i + 1]

        _xrefs.append(_ref2[0])  # start at ref2 since 1st point is rover
        _yrefs.append(_ref2[1])
        # _xrefs.append(_ref1[0])  # trying to start at rover pos
        # _yrefs.append(_ref1[1])

        _direction = _rover.determine_turn_direction(_ref1, _ref2)  # determine turn direction to ref point
        _radius = _rover.calculate_radius(_ref1, _ref2)  # calculate turn radius to ref point

        # Have to calculate d before _angle above!!!
        _d = np.sqrt((_ref2[0] - _ref1[0])**2 + (_ref2[1] - _ref1[1])**2)
        _angle = _rover.calculate_angle(_radius, _d)  # calculate initial angle

        print("Calculated distance b/w points: {}".format(_d))
        print("Calulated angle: {}".format(_angle))
        print("Initial position: {}".format(_rover_pos))
        print("Ref points: {}".format(_ref_pos_list))
        print("Direction for turn 1: {} \nRadius: {} \nAngle: {}".format(_direction, _radius, _angle))
        print("Incrementing angles by: {} degrees".format(_angle / _rover.angle_increment))

        # Initial position:
        _x = _ref1[0]
        _y = _ref1[1]

        # for i in range(1, _rover.angle_increment):
        for i in range(0, _rover.angle_increment + 1):

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

        # Plots radii of turns:
        # ax = plt.gca()
        # _projected_path = plt.Circle((_path, _ref1[1]), _radius, color='b', fill=False, linestyle='dashed')
        # ax.add_patch(_projected_path)

    plt.plot(
        _x_path, _y_path, 'b-',   # plots reference points
        _x_path, _y_path, 'bo',
        _xrefs, _yrefs, 'go',
        _rover_pos[0], _rover_pos[1], 'rs',
    )

    plt.axis([_rover.graph_xmin, _rover.graph_xmax, _rover.graph_ymin, _rover.graph_ymax])
    plt.grid(True)
    plt.show()





##### This is from pure_pursuit. Comparing that code with the code I originally #############
##### started working on that's based off the paper: "Evaluation of simple pure pursuit #####
##### path-following algorithm for an autonomous articulated-steer vehicle" #################
# def main():

#     cx = [10.0 * math.cos(ix) for ix in np.arange(0, 10, 0.1)]
#     cy = [10.0 * math.sin(iy) for iy in np.arange(0, 10, 0.1)]

#     print("x: {}".format(cx))
#     print("y: {}".format(cy))

#     x0 = -11.0  # initial rover xpos
#     y0 = -11.0  # initial rover ypos

#     target_speed = 0.447  # 1mph in m/s

#     T = 60.0  # max simulation time

#     state = State(x=x0, y=y0, yaw=0.0, v=0.0)

#     lastIndex = len(cx) - 1
#     time = 0.0
#     x = [state.x]
#     y = [state.y]
#     yaw = [state.yaw]
#     v = [state.v]
#     t = [0.0]

#     target_ind = calc_target_index(state, cx, cy)

#     while T >= time and lastIndex > target_ind:

#         ai = PIDControl(target_speed, state.v)
#         di, target_ind = pure_pursuit_control(state, cx, cy, target_ind)
#         state = state.update(state, ai, di)

#         time = time + state.dt

#         x.append(state.x)
#         y.append(state.y)
#         yaw.append(state.yaw)
#         v.append(state.v)
#         t.append(time)
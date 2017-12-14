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
import math
import csv
import codecs
from pure_pursuit import State, PurePursuitModel



class RoverModel(object):
    """
    Building a path-following algorithm, starting simple as possible
    and moving toward more complexity.
    """

    def __init__(self, x0=0.0, y0=0.0, Lf=1.0, T=60.0, V=0.447):
        
        ############## ROVER STATIC CONSTANTS ##############################################
        self.left_a = 27.974966981  # constant for left turn equation
        self.left_b = 0.7213692582  # constant for left turn equation
        self.right_a = 26.2074918622  # constant for right turn equation
        self.right_b = 0.7724722082  # constant for right turn equation

        # pyplot graph settings:
        self.graph_xmin = -50
        self.graph_xmax = 50
        self.graph_ymin = -50
        self.graph_ymax = 50

        # max turn angles for L/R:
        self.left_turn_max = 24.8  # max left turning angle from turn tests
        self.right_turn_max = 22.1  # max right turning angle from turn tests

        # min turn radius for L/R:
        self.left_radius_min = 2.26  # min left turn radius for rover, in meters
        self.right_radius_min = 2.25  # min right turn radius in meters
        #####################################################################################


        ############## ROVER ADJUSTABLE CONSTANTS ###########################################
        self.angle_increment = 5  # divide up angle from pt->pt by this much
        self.Lf = Lf  # TODO: Get value(s) that make sense for this
        self.T = T  # total model time
        self.V = V  # rover's target speed, 1mph ~0.447m/s
        #####################################################################################


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
        based on it's position relative to as reference point.
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


    def set_graph_ranges(self, x_path, y_path, ext):
        """
        Sets x and y range for graph from path data.
        ext - amount to extend at each bound
        """
        self.graph_xmin = x_path[0] - ext
        self.graph_xmax = x_path[-1] + ext
        self.graph_ymin = y_path[0] - ext
        self.graph_ymax = y_path[-1] + ext


def get_data_from_csv(filename, x_header, y_header):
    """
    Opens CSV by filename, and gets data from columns
    matching the header_list. Intended for reading in
    lat/lon or UTM x,y for rover path.
    """
    _csv_data, x_path, y_path = [], [], []

    # Read in the file:
    with open(filename, 'r') as _csv_file:
    # with codecs.open(filename, 'rU', 'utf-16') as _csv_file:
        reader = csv.reader(_csv_file)
        _csv_data = list(reader)
    _csv_file.close()

    # if header list items are integers and not strings, assume they're indices:
    start_index = 0
    try:
        x_index = _csv_data[0].index(x_header)  # trying to get header for x path
        y_index = _csv_data[0].index(y_header)  # trying to get header for y path
        start_index = 1  # headers are strings, so skip first row
    except ValueError as e:
        x_index = x_header  # assume x_header is index of x col
        y_index = y_header  # same for y

    for row in _csv_data[start_index:-1]:
        x_path.append(float(row[x_index]))
        y_path.append(float(row[y_index]))

    return x_path, y_path







def run_red_rover_model(Lf):
    """
    Incrementing lookahead for testing, saving plots of pngs
    """

    # Lf = 1.0  # rover's look-ahead distance
    # Lf = 0.5
    # T = 1200.0  # total time of model
    # T = 2400
    T = 6000
    V = 0.447  # rover's target velocity
    Kp = 1.0  # proportional gain for rover's velocity

    # Gets UTM data from turn test CSV:
    # x0, y0 = 259730.257383921, 3485055.70975021
    # cx, cy = rover_model.get_data_from_csv('points_of_interest/turn_tests_straight_line.csv', 0, 1)

    x0, y0 = 259551, 3.48472e6
    cx, cy = get_data_from_csv('2017-09-20/gps_field_test_fixtopic_20170920_reduced_utm.csv', 'easting', 'northing')


    rover_model = RoverModel(x0, y0, Lf, T, V)  # initialize rover model
    pure_pursuit_model = PurePursuitModel(Lf, Kp)  # initialize pure pursuit model
    state = State(x=x0, y=y0, yaw=0.0, v=0.0)  # initialize current state of rover

    lastIndex = len(cx) - 1
    time = 0.0
    x = [state.x]
    y = [state.y]
    yaw = [state.yaw]
    v = [state.v]
    t = [0.0]

    print("Rover starting position: ({}, {})".format(x0, y0))
    print("Last index of course: {}".format(lastIndex))

    target_ind = pure_pursuit_model.calc_target_index(state, cx, cy)

    print("Rover heading to point: ({}, {})".format(cx[target_ind], cy[target_ind]))

    while rover_model.T >= time and lastIndex > target_ind:

        ai = pure_pursuit_model.PIDControl(rover_model.V, state.v)
        di, target_ind = pure_pursuit_model.pure_pursuit_control(state, cx, cy, target_ind)
        state = state.update(state, ai, di)

        time = time + state.dt

        print("Time: {}".format(time))
        print("Rover's updated position: ({}, {})".format(state.x, state.y))
        print("Rover's target position: ({}, {})".format(cx[target_ind], cy[target_ind]))

        x.append(state.x)
        y.append(state.y)
        yaw.append(state.yaw)
        v.append(state.v)
        t.append(time)


    flg, ax = plt.subplots(1)
    plt.plot(cx, cy, ".r", label="course")
    plt.plot(x, y, "-b", label="trajectory")  # plots a blue line that's the rover path
    # plt.plot(x, y, "bo", label="trajectory")  # plots dots
    plt.legend()
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    plt.axis("equal")
    plt.grid(True)
    rover_model.set_graph_ranges(cx, cy, 2.5e2)
    plt.axis([rover_model.graph_xmin, rover_model.graph_xmax, rover_model.graph_ymin, rover_model.graph_ymax])


    # def update_line(num, data, line):
    #     # data_to_set = data[0:num]
    #     # line.set_data(data[..., :num])
    #     data_to_set = []
    #     for i in range(0, num + 1):
    #         data_to_set.append(data[i])
    #     line.set_data(data[0][0:num], data[1][0:num])
    #     return line,

    # fig1 = plt.figure()

    # # data = np.random.rand(2, 25)
    # l, = plt.plot([], [], 'r-')
    # # plt.xlim(0, 1)
    # # plt.ylim(0, 1)
    # # plt.xlabel('x')
    # # plt.title('test')
    # # line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(data, l),
    # #                                    interval=50, blit=True)
    # line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=([cx, cy], l),
    #                                    interval=50, blit=True)


    # flg, ax = plt.subplots(1)
    # plt.plot(t, v, "-r")
    # plt.xlabel("Time[s]")
    # plt.ylabel("Speed[m/s]")
    # plt.grid(True)

    # plt.show()
    plt.savefig('Plots/path_follow_20171214_{}.png'.format(Lf))



if __name__ == '__main__':
    """
    Runs the red rover pure pursuit model.

    rover_pos - starting position of rover
    cx, cy - points to follow (the course)

    Plots two graphs: position vs time, and vecolity vs time
    """

    for i in range(1, 10, 1):
        Lf = i / 10.0  # incrementing look ahead
        print ("Running red rover model with look-ahead of {}".format(Lf))
        run_red_rover_model(Lf)

    # run_red_rover_model(1.0)


    # Straight line course:
    # cy = np.arange(0, 50, 5)  # y positions of rover's course to follow
    # cx = [0.1*(np.random.random() - 0.5) for iy in cy]  # x position of rover's course to follow

    # Circle course:
    # cx = [10.0 * math.cos(ix) for ix in np.arange(0, 10, 0.1)]
    # cy = [10.0 * math.sin(iy) for iy in np.arange(0, 10, 0.1)]

    # x0 = 2.0  # rover's starting x position
    # y0 = 3.0  # rover's starting y position

    # x0 = 259730.257383921  # first x position in path
    # y0 = 3485055.70975021  # first y position in path


    # # Lf = 1.0  # rover's look-ahead distance
    # Lf = 0.03
    # T = 30.0  # total time of model
    # V = 0.447  # rover's target velocity
    # Kp = 1.0  # proportional gain for rover's velocity

    # rover_model = RoverModel(x0, y0, Lf, T, V)  # initialize rover model
    # pure_pursuit_model = PurePursuitModel(Lf, Kp)  # initialize pure pursuit model
    # state = State(x=x0, y=y0, yaw=0.0, v=0.0)  # initialize current state of rover

    # # Gets UTM data from turn test CSV:
    # cx, cy = rover_model.get_data_from_csv('points_of_interest/turn_tests_straight_line.csv', 0, 1)

    # lastIndex = len(cx) - 1
    # time = 0.0
    # x = [state.x]
    # y = [state.y]
    # yaw = [state.yaw]
    # v = [state.v]
    # t = [0.0]

    # print("Rover starting position: ({}, {})".format(x0, y0))
    # print("Last index of course: {}".format(lastIndex))

    # target_ind = pure_pursuit_model.calc_target_index(state, cx, cy)

    # print("Rover heading to point: ({}, {})".format(cx[target_ind], cy[target_ind]))

    # while rover_model.T >= time and lastIndex > target_ind:

    #     ai = pure_pursuit_model.PIDControl(rover_model.V, state.v)
    #     di, target_ind = pure_pursuit_model.pure_pursuit_control(state, cx, cy, target_ind)
    #     state = state.update(state, ai, di)

    #     time = time + state.dt

    #     print("Time: {}".format(time))
    #     print("Rover's updated position: ({}, {})".format(state.x, state.y))
    #     print("Rover's target position: ({}, {})".format(cx[target_ind], cy[target_ind]))

    #     x.append(state.x)
    #     y.append(state.y)
    #     yaw.append(state.yaw)
    #     v.append(state.v)
    #     t.append(time)



    # flg, ax = plt.subplots(1)
    # plt.plot(cx, cy, ".r", label="course")
    # plt.plot(x, y, "-b", label="trajectory")  # plots a blue line that's the rover path
    # # plt.plot(x, y, "bo", label="trajectory")  # plots dots
    # plt.legend()
    # plt.xlabel("x[m]")
    # plt.ylabel("y[m]")
    # plt.axis("equal")
    # plt.grid(True)
    # rover_model.set_graph_ranges(cx, cy, 1e1)
    # plt.axis([rover_model.graph_xmin, rover_model.graph_xmax, rover_model.graph_ymin, rover_model.graph_ymax])

    # flg, ax = plt.subplots(1)
    # plt.plot(t, v, "-r")
    # plt.xlabel("Time[s]")
    # plt.ylabel("Speed[m/s]")
    # plt.grid(True)

    # plt.show()
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


def get_data_from_csv(filename, t_header, x_header, y_header, row_step_size=2):
    """
    Opens CSV by filename, and gets data from columns
    matching the header_list. Intended for reading in
    lat/lon or UTM x,y, and time for rover path.
    Inputs:
        + row_step_size - amount of gps rows to step (e.g., 2 - get every other row)
        + filename - name of data file with gps path data
        + t_header - header name for time
        + x_header - header name for easting values
        + y_header - header name for northing values
    """
    _csv_data, x_path, y_path, t_path = [], [], [], []

    # Read in the file:
    with open(filename, 'r') as _csv_file:
    # with codecs.open(filename, 'rU', 'utf-16') as _csv_file:
        reader = csv.reader(_csv_file)
        _csv_data = list(reader)
    _csv_file.close()

    # if header list items are integers and not strings, assume they're indices:
    start_index = 0
    try:
        t_index = _csv_data[0].index(t_header)
        x_index = _csv_data[0].index(x_header)  # trying to get header for x path
        y_index = _csv_data[0].index(y_header)  # trying to get header for y path
        start_index = 1  # headers are strings, so skip first row
    except ValueError as e:
        t_index = t_header # assuming ValueError means header is int instead of string
        x_index = x_header  # assume x_header is index of x col
        y_index = y_header  # same for y

    # Getting time, easting, and northing from every row in CSV path data:
    # for row in _csv_data[start_index:-1]:
    # Getting time, easting, and northing from every 5th row in CSV path data:
    for i in range(start_index, len(_csv_data), int(row_step_size)):
        _row = _csv_data[i]
        t_path.append(float(_row[t_index]))
        x_path.append(float(_row[x_index]))
        y_path.append(float(_row[y_index]))

    return t_path, x_path, y_path


def save_csv_file(filename, csv_data):
    """
    Saves CSV file for analyzing intersection issue
    """
    fileout = open(filename, 'w')
    writer = csv.writer(fileout)
    # for row in csv_data:
    #     writer.writerow(row)
    writer.writerows(csv_data)
    fileout.close()
    return True


def get_gps_time_diffs(ct):
    """
    Input: GPS course time stamps list.
    Returns: Difference b/w timestamps
    """
    ct_diff = []
    diff_sum = 0.0
    for i in range(0, len(ct) - 1):
        ct_diff.append(ct[i + 1] - ct[i])
        diff_sum += ct_diff[i]

    avg_diff = diff_sum / len(ct_diff)

    print("time diff list: {}".format(ct_diff))
    print("times list: {}".format(ct))
    print("average time diff: {}".format(avg_diff))
    print("min time diff: {}".format(min(ct_diff)))
    print("max time diff: {}".format(max(ct_diff)))




def run_red_rover_model(Lf=0.5, row_step_size=2):
    """
    Incrementing lookahead for testing, saving plots of pngs
    Input: Lf - look-ahead distance in meters
    """

    T = 120  # total time of model, units of seconds
    V = 0.447  # rover's target velocity in m/s
    Kp = 1.0  # proportional gain for rover's velocity

    # Gets UTM data from turn test CSV:
    # x0, y0 = 259730.257383921, 3485055.70975021
    # cx, cy = rover_model.get_data_from_csv('points_of_interest/turn_tests_straight_line.csv', 0, 1)

    x0, y0 = 259551, 3.48472e6  # Initial rover starting position (original, works)
    # x0, y0 = 259543, 3484716  # Good start position for path intersection troubleshooting
    path_filename = 'Data/2017-09-20/gps_field_test_fixtopic_20170920_reduced_utm.csv'

    # ct, cx, cy = get_data_from_csv(
    #                 path_filename, 'field.header.stamp', 'easting', 'northing', row_step_size)
    ci, cx, cy = get_data_from_csv(
                    path_filename, 'field.header.seq', 'easting', 'northing', row_step_size)

    # temp code for looking at time diffs:
    # get_gps_time_diffs(ct)
    # return

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
    ind, ind_slope = [], [0]
    csv_data_out = [['time', 'index', 'rover_pos_x', 'rover_pos_y', 'target_pos_x', 'target_pos_y']]  # cols: index, time, rover_pos, target_pos

    print("Rover starting position: ({}, {})".format(x0, y0))
    print("Last index of course: {}".format(lastIndex))

    target_ind = pure_pursuit_model.calc_target_index(state, cx, cy)
    ind.append(target_ind)  # index list for calculating slope

    print("Rover heading to point: ({}, {})".format(cx[target_ind], cy[target_ind]))

    j = 0
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
        ind.append(target_ind)

        csv_data_out.append([time, target_ind, state.x, state.y, cx[target_ind], cy[target_ind]])

        slope_index = (ind[j + 1] - ind[j]) / (t[j + 1] - t[j])
        ind_slope.append(slope_index)
        j += 1


    flg, ax = plt.subplots(1)
    plt.plot(cx, cy, ".r", label="course")
    plt.plot(x, y, "-b", label="trajectory")  # plots a blue line that's the rover path
    # plt.plot(x, y, "bo", label="trajectory")  # plots dots
    plt.legend()
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    plt.axis("equal")
    plt.grid(True)
    rover_model.set_graph_ranges(cx, cy, 2.5e2)  # Working full view settings
    # rover_model.set_graph_ranges([x0, x0], [y0, y0], 0.8e1)  # Intersection issue settings 1
    plt.axis([rover_model.graph_xmin, rover_model.graph_xmax, rover_model.graph_ymin, rover_model.graph_ymax])

    # Velocity plot stuff:
    # flg, ax = plt.subplots(1)
    # plt.plot(t, v, "-r")
    # plt.xlabel("Time[s]")
    # plt.ylabel("Speed[m/s]")
    # plt.grid(True)

    # Index slope plot stuff:
    flg, ax = plt.subplots(1)
    plt.plot(t, ind_slope, "-r")
    plt.xlabel("Time[s]")
    plt.ylabel("Index slope[m/s]")
    plt.grid(True)


    # Saving output CSV for analyzing turn position and index
    # for path intersection problem:
    # filename = 'Data/2018-01-15/path_cross_example_data_2.csv'
    # save_csv_file(filename, csv_data_out)
    # print "CSV {} saved.".format(filename)

    # Display plot:
    plt.show()

    # Saving plots as images settings:
    # figure_name = 'path_follow_peanut_field_20180115_RSS{}.png'.format(row_step_size)
    # print("Saving figure: {}".format(figure_name))
    # plt.savefig('Plots/2018_01/{}'.format(figure_name))  # for plots across look-aheads
    # print("Plot saved.")





if __name__ == '__main__':
    """
    Runs the red rover pure pursuit model.

    rover_pos - starting position of rover
    cx, cy - points to follow (the course)

    Plots two graphs: position vs time, and vecolity vs time
    """

    # Creating plots with varying look-aheads:
    # for i in range(1, 20):
    #     Lf = i / 10.0  # incrementing look ahead
    #     run_red_rover_model(Lf)

    # Stepping through path row skipping amounts to see
    # how it affects the model:
    # for i in range (1, 11):
    #     row_step_size = i / 1.0
    #     run_red_rover_model(0.5, row_step_size)

    # Run model a single time w/ defaults:
    run_red_rover_model(0.5, 1)  # Defaults: Lf=0.5, rows_step_size=2
#! /usr/bin/python
# -*- coding: utf-8 -*-
u"""

Path tracking simulation with pure pursuit steering control and PID speed control.

author: Atsushi Sakai

This is a fork of Sakai's pure pursuit algorithm that I found on GitHub, with a repo
named PythonRobotics. (27 Nov. 2017; NP)

"""
import numpy as np
import math
import matplotlib.pyplot as plt




class State(object):

    def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
        self.dt = 0.2  # time step for model [s]
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




class PurePursuitModel(object):
    """
    "Classifying" the pure pursuit model to be used
    by the red rover model
    """
    def __init__(self, Lf=1.0, Kp=1.0):

        self.Kp = Kp  # speed propotional gain
        self.Lf = Lf  # look-ahead distance
        self.animation = False



    def PIDControl(self, target, current):
        a = self.Kp * (target - current)
        return a


    def pure_pursuit_control(self, state, cx, cy, pind):

        ind = self.calc_target_index(state, cx, cy)

        if pind >= ind:
            # use prev ind if prev ind >= ind
            ind = pind

        if ind < len(cx):
            # set tx ty to x,y of current path
            tx = cx[ind]
            ty = cy[ind]
        else:
            # if ind beyond path, go to last point in path
            tx = cx[-1]
            ty = cy[-1]
            ind = len(cx) - 1

        alpha = math.atan2(ty - state.y, tx - state.x) - state.yaw

        if state.v < 0:  # backward?
            alpha = math.pi - alpha

        delta = math.atan2(2.0 * state.L * math.sin(alpha) / self.Lf, 1.0)

        return delta, ind


    def calc_target_index(self, state, cx, cy):
        dx = [state.x - icx for icx in cx]
        dy = [state.y - icy for icy in cy]

        d = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in zip(dx, dy)]

        ind = d.index(min(d))

        L = 0.0
        while self.Lf > L and (ind + 1) < len(cx):
            dx = cx[ind + 1] - cx[ind]
            dy = cy[ind + 1] - cy[ind]
            L += math.sqrt(dx ** 2 + dy ** 2)
            print("Distance b/w points: {}".format(L))
            ind += 1


            # 1. Check to make sure turn angle is >= min turn angle
            

            # 2. Check to make sure the index change isn't large enough to be deemed
            # the incorrect path.



        print("Target index: {}".format(ind))

        return ind


    def check_index_slope(self, max_slope=1000):
        """
        Determine if rover is heading down the
        correct path at a GPS path intersection.
        """
        


    def find_closer_point(self):
        """
        Search for next closest point if the 
        max index slope is exceeded.
        """
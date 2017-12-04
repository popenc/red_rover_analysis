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
# import unicycle_model

Kp = 1.0  # speed propotional gain
# Lf = 1.0  # look-ahead distance
# Lf = 0.01
Lf = 1.2
# Lf = 2.0



#  animation = True
animation = False


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




def PIDControl(target, current):
    a = Kp * (target - current)

    return a


def pure_pursuit_control(state, cx, cy, pind):

    ind = calc_target_index(state, cx, cy)

    if pind >= ind:
        ind = pind

    if ind < len(cx):
        tx = cx[ind]
        ty = cy[ind]
    else:
        tx = cx[-1]
        ty = cy[-1]
        ind = len(cx) - 1

    alpha = math.atan2(ty - state.y, tx - state.x) - state.yaw

    if state.v < 0:  # backward?
        alpha = math.pi - alpha

    delta = math.atan2(2.0 * state.L * math.sin(alpha) / Lf, 1.0)

    return delta, ind


def calc_target_index(state, cx, cy):
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


def main():

    #  target course
    # cy = np.arange(0, 50, 0.1)
    # cx = [0.1*(np.random.random() - 0.5) for ix in cy]

    cx = [10.0 * math.cos(ix) for ix in np.arange(0, 10, 0.1)]
    cy = [10.0 * math.sin(iy) for iy in np.arange(0, 10, 0.1)]

    print("x: {}".format(cx))
    print("y: {}".format(cy))

    x0 = -11.0  # initial rover xpos
    y0 = -11.0  # initial rover ypos

    target_speed = 1.6  # i think it's in km/h, so 1.6km/h is ~1mph

    # T = 30.0  # max simulation time
    # T = 60.0
    T = 120.0

    state = State(x=x0, y=y0, yaw=0.0, v=0.0)

    lastIndex = len(cx) - 1
    time = 0.0
    x = [state.x]
    y = [state.y]
    yaw = [state.yaw]
    v = [state.v]
    t = [0.0]

    target_ind = calc_target_index(state, cx, cy)

    while T >= time and lastIndex > target_ind:

        ai = PIDControl(target_speed, state.v)
        di, target_ind = pure_pursuit_control(state, cx, cy, target_ind)
        state = state.update(state, ai, di)

        time = time + state.dt

        x.append(state.x)
        y.append(state.y)
        yaw.append(state.yaw)
        v.append(state.v)
        t.append(time)


    flg, ax = plt.subplots(1)
    plt.plot(cx, cy, ".r", label="course")
    plt.plot(x, y, "-b", label="trajectory")
    plt.legend()
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    plt.axis("equal")
    plt.grid(True)

    flg, ax = plt.subplots(1)
    plt.plot(t, [iv * 3.6 for iv in v], "-r")
    plt.xlabel("Time[s]")
    plt.ylabel("Speed[km/h]")
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    print("Pure pursuit path tracking simulation start")
    main()

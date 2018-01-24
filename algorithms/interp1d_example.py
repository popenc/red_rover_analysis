import numpy as np
from scipy.interpolate import interp1d # Different interface to the same function
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from savitzky_golay import *
import matplotlib.pyplot as plt

pts = np.array([[ 6.55525 ,  3.05472 ],
   [ 6.17284 ,  2.802609],
   [ 5.53946 ,  2.649209],
   [ 4.93053 ,  2.444444],
   [ 4.32544 ,  2.318749],
   [ 3.90982 ,  2.2875  ],
   [ 3.51294 ,  2.221875],
   [ 3.09107 ,  2.29375 ],
   [ 2.64013 ,  2.4375  ],
   [ 2.275444,  2.653124],
   [ 2.137945,  3.26562 ],
   [ 2.15982 ,  3.84375 ],
   [ 2.20982 ,  4.31562 ],
   [ 2.334704,  4.87873 ],
   [ 2.314264,  5.5047  ],
   [ 2.311709,  5.9135  ],
   [ 2.29638 ,  6.42961 ],
   [ 2.619374,  6.75021 ],
   [ 3.32448 ,  6.66353 ],
   [ 3.31582 ,  5.68866 ],
   [ 3.35159 ,  5.17255 ],
   [ 3.48482 ,  4.73125 ],
   [ 3.70669 ,  4.51875 ],
   [ 4.23639 ,  4.58968 ],
   [ 4.39592 ,  4.94615 ],
   [ 4.33527 ,  5.33862 ],
   [ 3.95968 ,  5.61967 ],
   [ 3.56366 ,  5.73976 ],
   [ 3.78818 ,  6.55292 ],
   [ 4.27712 ,  6.8283  ],
   [ 4.89532 ,  6.78615 ],
   [ 5.35334 ,  6.72433 ],
   [ 5.71583 ,  6.54449 ],
   [ 6.13452 ,  6.46019 ],
   [ 6.54478 ,  6.26068 ],
   [ 6.7873  ,  5.74615 ],
   [ 6.64086 ,  5.25269 ],
   [ 6.45649 ,  4.86206 ],
   [ 6.41586 ,  4.46519 ],
   [ 5.44711 ,  4.26519 ],
   [ 5.04087 ,  4.10581 ],
   [ 4.70013 ,  3.67405 ],
   [ 4.83482 ,  3.4375  ],
   [ 5.34086 ,  3.43394 ],
   [ 5.76392 ,  3.55156 ],
   [ 6.37056 ,  3.8778  ],
   [ 6.53116 ,  3.47228 ]])


x, y = pts.T
i = np.arange(len(pts))

#You can try Rbf, fitpack2 method
# 8x the original number of points
interp_i = np.linspace(0, i.max(), 8 * i.max())

#use interp1d to increase data points
xi = interp1d(i, x, kind='cubic')(interp_i)
yi = interp1d(i, y, kind='cubic')(interp_i)

#use this savitzky filter from http://scipy-cookbook.readthedocs.io/items/SavitzkyGolay.html
yhat = savitzky_golay(yi, 31, 5) # window size 51, polynomial order 3

plt.plot(xi, yi, 'r')  # plots data w/out savitzky filtering
plt.plot(xi, yhat, 'b')  # plots data w/ savitzky filtering
plt.plot(x, y, 'ko')  # plots points to follow


plt.show()
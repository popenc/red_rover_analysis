"""
A version of the red rover model using the Dubins curves.
The idea is to use the Dubins model alongside interp1d and savitzky
golay filtering to create a smooth path-following algorithm.

Links:
  + https://github.com/AndrewWalker/Dubins-Curves
  + https://github.com/AndrewWalker/pydubins
  + https://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.interpolate.interp1d.html
  + http://scipy-cookbook.readthedocs.io/items/SavitzkyGolay.html
"""


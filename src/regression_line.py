#!/usr/bin/python

#   Copyright (C) 2013
#   Adam Okuliar        aokuliar at redhat dot com
#   Jiri Hladky         hladky dot jiri at gmail dot com
#   Petr Benas          petrbenas at gmail dot com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy
from scipy import stats

class RegressionLine:
    def __init__(self):
        self.points = [] # vector of points to be regressed
        self.xVals = []
        self.yVals = []
        # computed attributes
        self.slope = 0
        self.stdError = 0
        self.confIntMax = 0
        self.confIntMin = 0

    def addPoint(self, x, y):
        self.points.append((x, y))
        self.xVals.append(x)
        self.yVals.append(y)

    def computeSlope(self):
        x = numpy.array(self.xVals)
        y = numpy.array(self.yVals)
        AverageX = numpy.mean(self.xVals)
        
        # slope a solves
        # a^2 * Sum[xi yi] + a * Sum [xi^2 - yi^2] - Sum [xi yi] = 0
        A = numpy.sum(x*y)
        B = numpy.sum([x**2 - y**2])
        discriminant = numpy.sqrt( B**2 + 4 * A**2)
        
        a = ( -B + discriminant ) / ( 2 * A )
        self.slope = a
        if len(self.xVals) == 1:
            self.stdError = 0
            self.confIntMax = self.confIntMin = a
            return
        
        # distance of points from line with slope=a
        D = numpy.abs(a*x-y) / numpy.sqrt(a**2 + 1)
        # standard error of a
        a_se = numpy.sqrt( numpy.sum(D**2) / numpy.sum((x - AverageX)**2) / (len(x) - 1) )
        # 90% confidence interval
        h = a_se * stats.t._ppf((1+0.90)/2., len(x)-1)

        self.stdError = a_se
        self.confIntMax = a + h
        self.confIntMin = a - h

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

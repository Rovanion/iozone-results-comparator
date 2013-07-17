#!/usr/bin/python

#   Copyright (C) 2011
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

class OperationResults:
    def __init__(self, Type):
        # following needs to be provided
        self.colnames = []
        self.data = {} # row_name -> [[values file 1], [values file 2], ...]
        self.lindata = [] # data in linear from, zeros excluded
                  # [ [values col 1], [values col 2], ...]
        self.indexedData = {} # (row name, col name) -> [values from all files]
        self.alldata = []
        self.datatype = Type

        # following will be computed
        self.voidcolumns = [] # list of columns with no values
        self.means = []
        self.devs = []
        self.ci_mins = []
        self.ci_maxes = []
        self.gmeans = []
        self.medians = []
        self.first_qrts = []
        self.third_qrts = []
        self.mins = []
        self.maxes = []
        self.indexedMeans = {} # (row name, col name) -> mean of all files values

        if (Type == 'fs'):
            self.xlabel = 'File size [kB]'
            self.ylabel = 'Block size [kB]'
        elif (Type == 'bs'):
            self.xlabel = 'Block size [kB]'
            self.ylabel = 'File size [kB]'
        else:
            raise Exception('Invalid set code')
            

    def set_colnames(self, ColNames):
        self.colnames = ColNames
        for colname in ColNames:
            self.lindata.append([])

    def add_row(self, rowname, values):
        self.data[rowname].append(values)
        for valnr in range(len(values)):
            if (values[valnr] == float(0)):
                continue
            self.lindata[valnr].append(values[valnr])
            self.alldata.append(values[valnr])

            colname = self.colnames[valnr]
            if (rowname, colname) not in self.indexedData.keys():
                self.indexedData[(rowname, colname)] = []
            self.indexedData[(rowname, colname)].append(values[valnr])
    
    # confidence = confidence interval probability rate in percent
    def compute_all_stats(self, confidence=0.90):
        for i in range(len(self.lindata)):
            n = len(self.lindata[i])
            if (n == 0):
                self.voidcolumns.append(i)
                break

            (mean, dev, ci_min, ci_max, gmean, median, first_qrt, third_qrt, minimum, maximum) = self.stats(self.lindata[i])

            self.means.append(mean) 
            self.devs.append(dev) 
            self.ci_mins.append(ci_min)
            self.ci_maxes.append(ci_max)
            self.gmeans.append(gmean)
            self.medians.append(median)
            self.first_qrts.append(first_qrt)
            self.third_qrts.append(third_qrt)
            self.mins.append(minimum)
            self.maxes.append(maximum)

        # and stats for summary
        (self.mean, self.dev, self.ci_min, self.ci_max,
            self.gmean, self.median, self.first_qrt, self.third_qrt,
            self.minimum, self.maximum) = self.stats(self.alldata)

        # compute row and col indexed data averages (for linear regression)
        for (row, col) in self.indexedData.keys():
            self.indexedMeans[(row, col)] = numpy.mean(self.indexedData[(row, col)])

    def stats(self, data, confidence=0.90):
        n = len(data)

        mean = numpy.mean(data) # arithmetic mean
        dev = numpy.std(data, ddof=1) # delta degree of freedom = 1  -  sample standard deviation (Bessel's correction)
        se = dev/numpy.sqrt(n) # standard error
        err = se * stats.t._ppf((1+confidence)/2., n-1) # confidence interval
        ci_min = mean - err # confidence interval
        ci_max = mean + err # confidence interval
        gmean = stats.gmean(data) # geometric mean
        median = numpy.median(data) # median
        first_qrt = stats.scoreatpercentile(data, 25) # first quartile
        third_qrt = stats.scoreatpercentile(data, 75) # third quartile
        minimum = sorted(data)[0]
        maximum = sorted(data)[-1]

        return (mean, dev, ci_min, ci_max, gmean, median, first_qrt, third_qrt, minimum, maximum)

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


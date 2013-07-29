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

class MultisetData:
    def __init__(self):
        # dict key = set name
        # val = dict with operation name keys and opearation_results values
        self.fs = {}
        self.bs = {}

    def addDataSet(self, setName):
        self.fs[setName] = {}
        self.bs[setName] = {}
    
    def addOperationResults(self, setName, dataType, operation, results):
        if (dataType == 'fs'):
            self.fs[setName][operation] = results
        elif (dataType == 'bs'): 
            self.bs[setName][operation] = results
        else:
            raise Exception('Invalid data type')

    def computeStats(self):
        for dataSet in self.fs.keys():
            for op in self.fs[dataSet].keys():
                self.fs[dataSet][op].compute_all_stats()
        for dataSet in self.bs.keys():
            for op in self.bs[dataSet].keys():
                self.bs[dataSet][op].compute_all_stats()

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

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

import os
from copy import deepcopy

import operation_results

class TsvOutput:
    def __init__(self, outputDir):
        self.outputDir = outputDir
        if not (os.path.exists(outputDir)):
            os.makedirs(outputDir)

    def normalMode(self, dataFS, dataBS):
        self.fs = dataFS
        self.bs = dataBS

        for op in self.fs.common_ops:
            self.tab_delimited(self.fs.base[op], op, 'baseline')
            self.tab_delimited(self.fs.set1[op], op, 'set1')
            self.tab_delimited(self.bs.base[op], op, 'baseline')
            self.tab_delimited(self.bs.set1[op], op, 'set1')

        # why deepcopy? Because of the ALL pseudooperation removal we are passing the data
        # by value, not by reference
        self.tab_delimited_summary(deepcopy(dataBS.base), dataBS.common_ops[:], 'baseline')
        self.tab_delimited_summary(deepcopy(dataBS.set1), dataBS.common_ops[:], 'set1')

    # craate tab delimieted output for single operation
    # data - OperationResults object
    # setName - baseline/set1
    # operation - name of operation being written
    def tab_delimited(self, data, operation, setName):
        tabdName = operation + '_' + data.datatype + '_' + setName + '.tsv'
        self.tabd = open(self.outputDir+'/'+tabdName, 'w')
    
        self.tabd.write('# ' + operation + ' throughput for any ' +  data.datatype + '. Open it with: LC_ALL=en_US.UTF-8\n')
        self.tabd.write('# Read this file into Open Office  with command oocalc <filename>\n')
        self.tabd.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
        self.tabd.write(data.xlabel)
        for colName in data.colnames:
            self.tabd.write('\t'+str(colName))
        self.tabd.write('\n')
    
        rowColMap = {} # row name -> [ present column names]
        for (row, col) in sorted(data.indexedData.keys()):
            if not row in rowColMap.keys():
                rowColMap[row] = []
            rowColMap[row].append(col)

        # write the data
        nrOfRuns = len(data.indexedData[data.indexedData.keys()[0]])
        for rowName in sorted(rowColMap.keys()):
            for runNr in range(0, nrOfRuns ):
                self.tabd.write(data.ylabel + ' = ' + str(rowName) + ' Run = ' + str(runNr + 1))
                # missing values from the beginning of the row? 
                firstNonEmpty = data.colnames[0]
                while (firstNonEmpty < rowColMap[rowName][0]):
                    self.tabd.write('\t')
                    firstNonEmpty *= 2

                for colName in rowColMap[rowName]:
                    self.tabd.write('\t' + str(round(data.indexedData[(rowName, colName)][runNr], 2)))

                # missing values from the end of the row? 
                lastNonEmpty = rowColMap[rowName][-1]
                while (lastNonEmpty < data.colnames[-1]):
                    self.tabd.write('\t')
                    lastNonEmpty *= 2
                self.tabd.write('\n')
    
        self.write_tabd_stats(data)
        self.write_oocalc_formulas(str(4 + nrOfRuns * len(rowColMap.keys())))
        self.tabd.close()
    
    # write oocalc formulas to the end of tabd
    # it's useful in verification this script computes the same stat values OO does
    # tabd - where to write
    # dataEnd - line number of last dataline
    def write_oocalc_formulas(self, dataEnd):
        self.tabd.write('#OOCALC formulas\n')
        self.tabd.write('#mean val.\t=AVERAGE(B5:B' + dataEnd + ')\n')
        self.tabd.write('#standard dev.\t=STDEV(B5:B' + dataEnd + ')\n')
        self.tabd.write('#ci. min. 90%\t=AVERAGE(B5:B' + dataEnd + ')-TINV(1/10;COUNT(B5:B' + dataEnd + ')-1)*STDEV(B5:B' + dataEnd + ')/SQRT(COUNT(B5:B' + dataEnd + '))\n')
        self.tabd.write('#ci. max 90%\t=AVERAGE(B5:B' + dataEnd + ')+TINV(1/10;COUNT(B5:B' + dataEnd + ')-1)*STDEV(B5:B' + dataEnd + ')/SQRT(COUNT(B5:B' + dataEnd + '))\n')
        self.tabd.write('#geom. mean\t=GEOMEAN(B5:B' + dataEnd + ')\n')
        self.tabd.write('#median\t=MEDIAN(B5:B' + dataEnd + ')\n')
        self.tabd.write('#first quatile\t=QUARTILE(B5:B' + dataEnd + ';1)\n')
        self.tabd.write('#third quartile\t=QUARTILE(B5:B' + dataEnd + ';3)\n')
        self.tabd.write('#minimum\t=QUARTILE(B5:B' + dataEnd + ';0)\n')
        self.tabd.write('#maximum\t=QUARTILE(B5:B' + dataEnd + ';4)\n')

    # write statistical values to the bottom lines of tab delimited output
    # tabd - where to write
    # statVals - list of values in specific order(see valNames var in this function)
    def write_tabd_stats(self, data):
        # data nr value name
        order = ('mean val.', 'standard dev.', 'ci. min. 90%', 'ci. max 90%', 'geom. mean', 'median',
            'first quartile', 'third quartile', 'minimum', 'maximum')
        sources = {'mean val.' : data.means, 'standard dev.' : data.devs, 'ci. min. 90%' : data.ci_mins,
                'ci. max 90%' : data.ci_maxes, 'geom. mean' : data.gmeans, 'median' : data.medians,
                'first quartile' : data.first_qrts, 'third quartile' : data.third_qrts, 
                'minimum' : data.mins, 'maximum' : data.maxes}
    
        self.tabd.write('# Statistics (excluding 0 values)\n')
        for stat in order:
            self.tabd.write('#' + stat)
            for val in sources[stat]:
                self.tabd.write('\t'+str(round(val, 2)))
            self.tabd.write('\n')

    # craate tab delimited output of sumary sorted by operation and overall summary
    def tab_delimited_summary(self, data, operations, setName):
        self.tabd = open(self.outputDir + '/' + 'summary_sorted_by_operation' + '_' + setName + '.tsv', 'w')

        self.tabd.write('# iozone measured throughput[MB/s] for any FS and any BS. Open it with: LC_ALL=en_US.UTF-8\n')
        self.tabd.write('# Read this file into Open Office  with command oocalc <filename>\n')
        self.tabd.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')

        # we don't want the ALL pseudooperation here
        operations.remove('ALL')
        del data['ALL']

        self.tabd.write('Operation')
        for operation in operations:
            self.tabd.write('\t' + operation)
        self.tabd.write('\n')

        nrOfRuns = len(data[operations[0]].indexedData[data[operations[0]].indexedData.keys()[0]])

        # write the data
        for (row, col) in sorted(data[operations[0]].indexedData.keys()):
            for run in range(0, nrOfRuns):
                self.tabd.write(data[operations[0]].ylabel + ' = ' + str(row) + ' ' +
                        data[operations[0]].xlabel + ' = ' + str(col) + ' Run = ' + str(run + 1))
                for op in operations:
                    self.tabd.write('\t' + str(round(data[op].indexedData[(row, col)][run], 2)))
                self.tabd.write('\n')

        # compute statistics

        # operation_results object is used for computing the stats and 
        # as a temporary storage of stats before outputing them to the TSV file
        opRes = operation_results.OperationResults('fs') # the type really does not matter at all here

        for op in operations:
            (mean, dev, ci_min, ci_max, gmean, median, first_qrt, third_qrt, minimum, maximum) = opRes.stats(data[op].alldata)
            opRes.means.append(mean) 
            opRes.devs.append(dev) 
            opRes.ci_mins.append(ci_min)
            opRes.ci_maxes.append(ci_max)
            opRes.gmeans.append(gmean)
            opRes.medians.append(median)
            opRes.first_qrts.append(first_qrt)
            opRes.third_qrts.append(third_qrt)
            opRes.mins.append(minimum)
            opRes.maxes.append(maximum)

        # write all statistic values to tabd sorted by operation
        self.write_tabd_stats(opRes)
        self.write_oocalc_formulas(str(4 + nrOfRuns * len(data[operations[0]].indexedData.keys())))
        self.tabd.close()

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

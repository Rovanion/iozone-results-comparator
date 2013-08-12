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
# data - both sets data in  [[(FS, BSdata)],[(FS, BSdata)]] # [0] = base, [1] = set1 format
# operations - operations order for tab delimited
def tab_delimited_summary(data, order):
    for setNr in range(len(data)):
        if (setNr == 0):
            setName = 'baseline'
        else:
            setName = 'set1'
        tabdOperationName = 'summary_sorted_by_operation' + '_' + setName + '.tsv'
        tabdAllName = 'summary_all' + '_' + setName + '.tsv'
        tabdOperation = open(tabdDir+'/'+tabdOperationName, 'w')
        tabdAll = open(tabdDir+'/'+tabdAllName, 'w')

        tabdOperation.write('# iozone measured throughput[MB/s] for any FS and any BS. Open it with: LC_ALL=en_US.UTF-8\n')
        tabdOperation.write('# Read this file into Open Office  with command oocalc <filename>\n')
        tabdOperation.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
        tabdAll.write('# iozone measured throughput[MB/s] for any FS, any BS and any operation. Open it with: LC_ALL=en_US.UTF-8\n')
        tabdAll.write('# Read this file into Open Office  with command oocalc <filename>\n')
        tabdAll.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
        tabdAll.write('ALL\n')

        tabdOperation.write('Operation')
        for operation in order:
            tabdOperation.write('\t'+operation)
        tabdOperation.write('\n')

        # prepare data for stats
        columnValues = [] # [[col1_row1, col1_row2, ...], [col2_row1, col2_row2, ...], ...]
        allSetData = []
        valsOp = {}
        valsAll = {}
        for m in order:
            columnValues.append([])

        # prepare data in format more usable for what will follow
        for opNr in range(len(data[setNr])):
            (x, y) = data[setNr][opNr]
            Run = 0
            FS = y[0][0]
            for row in y:
                if (row[0] == FS):
                    Run += 1
                else:
                    FS = row[0]
                    Run = 1
                for bsNr in range(len(x)):
                    valsOp[(FS, x[bsNr], Run, opNr)] = row[bsNr+1]
                    valsAll[(opNr, FS, x[bsNr], Run)] = row[bsNr+1]
                    columnValues[opNr].append(row[bsNr+1])
                    allSetData.append(row[bsNr+1])

        # write conted of tabd sorted by operation
        row = []
        dataLineNr = 4
        for key in sorted(valsOp.keys()):
            (FS, BS, Run, opNr) = key
            if (valsOp[key] != 0):
                val = str(round(valsOp[key],2))
            else:
                val = ''
            row.append(val)
            if (opNr == 0):
                caption = 'Filesize[kB] = ' + str(FS) + ' Block size [kB] = ' + str(BS) + ' Run=' + str(Run)
            if (opNr == (len(order) - 1 )):
                empty = True;
                for val in row:
                    if val:
                        empty = False;
                if not (empty):
                    tabdOperation.write(caption)
                    for val in row:
                        tabdOperation.write('\t' + val)
                    tabdOperation.write('\n')
                    dataLineNr += 1
                row = []

        # write overall tabd content
        tabdAllLine = 4
        for key in sorted(valsAll.keys()):
            (opNr, FS, BS, Run) = key
            if (valsAll[key] != 0):
                tabdAll.write('Operation ' + order[opNr] + ' Filesize[kB] = ' + str(FS) + ' Block size [kB] = ' + str(BS) + ' Run = ' + str(Run) + '\t' + str(round(valsAll[key],2)) + '\n')
                tabdAllLine += 1

        # compute statistics
        (avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)

        # write all statistic values to tabd sorted by operation
        statValsOperation = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
        write_tabd_stats(tabdOperation, statValsOperation)
        write_oocalc_formulas(tabdOperation, str(dataLineNr))
        tabdOperation.close()


        # write all statistic values to all data tabd
        columnValues = [allSetData]
        (avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)
        statValsAll = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
        write_tabd_stats(tabdAll, statValsAll)
        write_oocalc_formulas(tabdAll, str(tabdAllLine))
        tabdAll.close()

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

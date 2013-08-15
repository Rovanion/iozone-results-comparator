#!/usr/bin/python

#   Copyright (C) 2011, 2013
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

from scipy import stats

from regression_line import RegressionLine

class StatsComparision:
    def __init__(self):
        # dict key = operation name
        # val = operation_results object instance
        self.base = {}
        self.set1 = {}
        self.ttest_pvals = {}
        self.ttest_res = {}
        self.differences = {}
        self.common_ops = []
        self.op_common_cols = {} # op -> [col list]
        self.summary_base= [] # row(e.g. devs [op1 val, op2 val, ...], meds [], ... 
        self.summary_set1= []

        self.summary_diffs = []
        self.summary_pvals = []
        self.summary_res = []
        
        self.regressionLines = {} # operation name -> RegressionLine object

        self.order=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
        "striderd", "fwrite", "frewrite", "fread", "freread", "ALL"]

    def add_operation_results(self, setName, operation, results):
        if (setName == 'baseline'):
            self.base[operation] = results
        elif (setName == 'set1'): 
            self.set1[operation] = results
        else:
            raise Exception('Invalid set name')
    
    def compare(self):
        self.get_common()
        self.delete_uncommon()

        for op in self.common_ops:
            self.base[op].compute_all_stats()
            self.set1[op].compute_all_stats()

        # summary data is stored in fs only, no need for counting this redundantly in bs
        if (self.base[self.base.keys()[0]].datatype == 'fs'):
            self.summary()

        self.ttest_diff()
        # summary data is stored in fs only, no need for counting this redundantly in bs
        if (self.base[self.base.keys()[0]].datatype == 'fs'):
            self.summary_ttest()

    def ttest_diff(self):
        for op in self.common_ops:
            self.differences[op] = []
            self.ttest_pvals[op] = []
            self.ttest_res[op] = []
            for colnr in range(len(self.op_common_cols[op])):
                diff = (self.set1[op].medians[colnr] / self.base[op].medians[colnr] - 1) * 100
                self.differences[op].append(diff)

                if len(self.base[op].lindata[colnr]) == 1 and len(self.set1[op].lindata[colnr]) == 1:
                    self.ttest_pvals[op].append(float('NaN'))
                    self.ttest_res[op].append('N/A')
                    continue

                (tstat, pval) = stats.ttest_ind(self.base[op].lindata[colnr], self.set1[op].lindata[colnr])
                self.ttest_pvals[op].append(pval)

                # 90% probability
                if (pval > 0.1):
                    self.ttest_res[op].append('SAME')
                else:
                    self.ttest_res[op].append('DIFF')

    def summary_ttest(self):
        for i in range(len(self.common_ops)):
            op = self.common_ops[i]
            # summary_base[5] - medians
            diff = (self.summary_set1[5][i] / self.summary_base[5][i] -1)*100
            self.summary_diffs.append(diff)

            if len(self.base[op].alldata) == 1 and len(self.set1[op].alldata) == 1:
                self.summary_pvals.append(float('NaN'))
                self.summary_res.append('N/A')
                continue

            (tstat, pval) = stats.ttest_ind(self.base[op].alldata, self.set1[op].alldata)
            self.summary_pvals.append(pval)

            # 90% probability
            if (pval > 0.1):
                self.summary_res.append('SAME')
            else:
                self.summary_res.append('DIFF')

                
    def get_common(self):
        # get common operations
        for op in self.order:
            if op in self.set1 and op in self.base:
                self.common_ops.append(op)

        # get common cols
        self.op_common_cols[op] = []
        for op in self.common_ops:
            self.op_common_cols[op] = []
            for colname in self.base[op].colnames:
                if colname in self.set1[op].colnames:
                    self.op_common_cols[op].append(colname)

    def delete_uncommon(self):
        for op in self.common_ops:
            for colname in reversed(self.base[op].colnames):
                if not colname in self.op_common_cols[op]:
                    self.base[op].removeColumn(colname)
            for colname in reversed(self.set1[op].colnames):
                if not colname in self.op_common_cols[op]:
                    self.set1[op].removeColumn(colname)
    
    def summary(self):
        for (source, dest) in ((self.base, self.summary_base), (self.set1, self.summary_set1)):
            #for op in self.common_ops:
            for i in range(0, 10): # we've got 10 statistic values, see below
                dest.append([])

            for op in self.common_ops:
                vals = (source[op].mean, source[op].dev, source[op].ci_min, source[op].ci_max,
                    source[op].gmean, source[op].median, source[op].first_qrt,
                    source[op].third_qrt, source[op].minimum, source[op].maximum)
                for i in range(len(vals)):
                    dest[i].append(vals[i])

    def computeRegressionLines(self):
        for op in self.common_ops:
            regLine = RegressionLine()
            for (row, col) in self.base[op].indexedMeans.keys():
                regLine.addPoint(self.base[op].indexedMeans[(row, col)], self.set1[op].indexedMeans[(row, col)])
            regLine.computeSlope()
            self.regressionLines[op] = regLine

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

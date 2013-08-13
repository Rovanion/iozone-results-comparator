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

import sys
import argparse
import re

import parse_iozone
import stats_comparision
import html
import operation_results
import multiset_data
import tsv_output

# the main class
class IozoneResultsComparator:
    def __init__(self):
        self.sets = {}

        self.parse_args()    
        self.html = html.Html(self.args.html_dir, self.args.tsv_dir, sys.argv[0])
        self.tsv = tsv_output.TsvOutput(self.args.tsv_dir)

    def parse_args(self):
        self.argparser = argparse.ArgumentParser(description='Iozone results comparator') 
        self.argparser.add_argument('--baseline', nargs='+', required=True,
            help='Set of iozone result files to form the baseline.')
        self.argparser.add_argument('--set1', nargs='+', required=True,
            help='Set of iozone results files to compared against baseline.')
        self.argparser.add_argument('--multiset', required=False, action='store_true',
            help='Enables the multiset visual comparision mode.')
        self.argparser.add_argument('--html_dir', nargs=1, required=False, action='store', 
            default='html_out', help='Where to wite the output HTML.')
        self.argparser.add_argument('--tsv_dir', nargs=1, required=False, action='store', 
            default='tsv_out', help='Where to write the output TSV.')
        (self.args, self.remainingArgs) = self.argparser.parse_known_args()
        self.sets['baseline'] = self.args.baseline
        self.sets['set1'] = self.args.set1

    # get results from files, store them in iozone result objects inside of stats_comparision objects
    def get_data_normal_mode(self):
        self.fs = stats_comparision.StatsComparision()
        self.bs = stats_comparision.StatsComparision()

        self.parsed_base=parse_iozone.ParseIozone(self.args.baseline)
        for op in self.parsed_base.operations:
            self.fs.add_operation_results('baseline', op, self.parsed_base.get_FS_list_for_any_BS(op))
            self.bs.add_operation_results('baseline', op, self.parsed_base.get_BS_list_for_any_FS(op))

        self.parsed_set1=parse_iozone.ParseIozone(self.args.set1)
        for op in self.parsed_base.operations:
            self.fs.add_operation_results('set1', op, self.parsed_set1.get_FS_list_for_any_BS(op))
            self.bs.add_operation_results('set1', op, self.parsed_set1.get_BS_list_for_any_FS(op))

        self.agregate_all(self.fs, self.parsed_base.operations, 'fs', 'baseline')
        self.agregate_all(self.bs, self.parsed_base.operations, 'bs', 'baseline')
        self.agregate_all(self.fs, self.parsed_set1.operations, 'fs', 'set1')
        self.agregate_all(self.bs, self.parsed_set1.operations, 'bs', 'set1')

    # aggregate all the data to the ALL pseudooperation
    def agregate_all(self, dest, operations, dataType, setName):
        if (setName == 'baseline'):
            source = dest.base
        else:
            source = dest.set1
        res = operation_results.OperationResults(Type=dataType)
        res.set_colnames(source[operations[0]].colnames[:]) # we want to copy the list by value, not by refference
        for op in operations:
            for rowName in source[op].data.keys():
                for fileValues in source[op].data[rowName]:
                    res.add_row(rowName, fileValues)
        dest.add_operation_results(setName, 'ALL', res)

    def compare(self):
        self.fs.compare()
        self.bs.compare()
        self.fs.computeRegressionLines()

        self.tsv.normalMode(self.fs, self.bs)
        self.html.init_normal_mode(self.fs, self.bs, self.args.baseline, self.args.set1)
        self.html.normal_mode()

    def parse_multiset_args(self):
        currentSet = ''
        setArg = re.compile('--set\d+')
        setName = re.compile('--')
        if not comparator.remainingArgs or not setArg.match(comparator.remainingArgs[0]):
                raise Exception('Wrong multiset arguments')

        for arg in comparator.remainingArgs:
            if setArg.match(arg):
                currentSet = setName.split(arg)[1]
                self.sets[currentSet] = []
            else:
                self.sets[currentSet].append(arg)

    def get_data_multiset_mode(self):
        self.multiset = multiset_data.MultisetData()
        for setName in sorted(self.sets.keys()):
            parser = parse_iozone.ParseIozone(self.sets[setName])
            self.multiset.addDataSet(setName)
            for op in parser.operations:
                self.multiset.addOperationResults(setName, 'fs', op, parser.get_FS_list_for_any_BS(op))
                self.multiset.addOperationResults(setName, 'bs', op, parser.get_BS_list_for_any_FS(op))

    def multiset_mode(self):
        self.multiset.computeStats()
        self.html.init_multiset_mode(self.multiset, self.sets)
        self.html.multiset_mode()

if __name__ == '__main__':
    comparator = IozoneResultsComparator()
    if not comparator.args.multiset:
        comparator.get_data_normal_mode()
        comparator.compare()
    else:
        comparator.parse_multiset_args()
        comparator.get_data_multiset_mode()
        comparator.multiset.get_common()
        comparator.multiset_mode()


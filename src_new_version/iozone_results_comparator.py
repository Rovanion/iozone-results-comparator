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

import sys
import argparse

import parse_iozone
import stats_comparision
import html

# the main class
class IozoneResultsComparator:
    def __init__(self):
        self.parse_args()    
        self.get_data()

    def parse_args(self):
        self.argparser = argparse.ArgumentParser(description='Iozone results comparator') 
        self.argparser.add_argument('--baseline', nargs='+', required=True,
            help='Set of iozone result files to form the baseline.')
        self.argparser.add_argument('--set1', nargs='+', required=True,
            help='Set of iozone results files to compared against baseline.')
        self.argparser.add_argument('--html', required=False, action='store_true',
            help='Whether to produce HTML output.')
        self.argparser.add_argument('--csv', required=False, action='store_true',
            help='Whether to produce CSV output.')
        # TODO jmena operaci z tridy parse iozone
        self.argparser.add_argument('--html_detail', nargs=1, required=False, action='store',
            help='Name of operation to have a closer look at.', choices=['iwrite',
            'rewrite', 'iread', 'reread', 'randrd', 'randwr', 'bkwdrd', 'recrewr', 
            'striderd', 'fwrite', 'frewrite', 'fread', 'freread', 'ALL'])
        self.argparser.add_argument('--html_dir', nargs=1, required=False, action='store', 
            default='html_out', help='Where to output HTML.')
        self.argparser.add_argument('--csv_dir', nargs=1, required=False, action='store',
            default='csv_out', help='Where to output CSV.')
        self.args = self.argparser.parse_args()
    
        if not (self.args.html or self.args.csv or self.args.html_detail):
            print 'Try to use --html, --csv or --html_detail option to get any output.'
            sys.exit(0)

    # get results from files, store them in iozone result objects inside of stats_comparision objects
    def get_data(self):
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

    def compare(self):
        self.fs.compare()
        self.bs.compare()
        self.fs.computeRegressionLines()
        if (self.args.html):
            self.html = html.Html(self.args.html_dir, self.fs, self.bs, self.args.baseline, self.args.set1)
            self.html.normal_mode()


    def debug(self):
        #print self.fs.base['iwrite'].data
        #print self.fs.base['iwrite'].colnames
        #print self.bs.base['bkwdrd'].lindata[0]
        #print self.bs.set1['bkwdrd'].lindata[0]
        #print self.fs.differences['iwrite']
        #print self.fs.ttest_res
        pass


if __name__ == '__main__':
    comparator = IozoneResultsComparator()
    comparator.compare()
    comparator.debug()

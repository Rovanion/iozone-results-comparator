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

import os
import shutil

import plotter
import googlecharts

class Html:
    def __init__(self, OutDir):
        self.outdir = OutDir
        if not (os.path.exists(OutDir)):
            os.makedirs(OutDir)
        shutil.copyfile('./stylesheet.css',OutDir+'/stylesheet.css')
        self.htmldoc=open(OutDir+'/index.html','w')

        self.googlecharts = googlecharts.GoogleCharts()
        self.plotter = plotter.Plotter(self.outdir)

    def init_normal_mode(self, Fs, Bs, BaseFiles, Set1Files):
        self.fs = Fs
        self.bs = Bs
        self.basefiles = BaseFiles
        self.set1files = Set1Files

    def write_header(self):
        html_header='''
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> 
        <title>Iozone results</title>
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        </head>
        <body>
        <link rel="stylesheet" type="text/css" href="stylesheet.css">
        <div class="main">
        <div class="inner">
        '''
        self.htmldoc.write(html_header)

    def write_footer(self):
        html_footer='''
        </div>
        </div>
        </body>
        </html>
        '''
        self.htmldoc.write(html_footer)
        self.htmldoc.close()
        print 'Finished.\nTo view results open in your web browser:'
        print 'file://' + os.getcwd() + '/' + self.outdir + '/index.html'

    def write_info(self):
        self.htmldoc.write('<hr>')
        self.htmldoc.write('<DL class="filelist">')
        self.htmldoc.write('<DT><STRONG>Baseline data set</STRONG><UL>')
        for file_name in self.basefiles:
            self.htmldoc.write('<LI>'+file_name)
        self.htmldoc.write('</UL>')
        self.htmldoc.write('<DT><STRONG>Investigated data set</STRONG><UL>')
        for file_name in self.set1files:
            self.htmldoc.write('<LI>'+file_name)
        self.htmldoc.write('</UL>')
        self.htmldoc.write('</DL>')
        self.htmldoc.write('<p>Plotted values are median with first and third quartile errorbars.<br>')
        self.htmldoc.write('mean => Arithmetic mean<br>')
        self.htmldoc.write('standar dev. => Sample standard deviation<br>')
        self.htmldoc.write('ci. max 90%, ci.min => confidence interval at confidence level 90% => it means that mean value of the distribution lies with 90% propability in interval ci_min-ci_max<br>')
        self.htmldoc.write('geom. mean => Geometric mean<br>')
        self.htmldoc.write('median => Second quartile = cuts data set in half = 50th percentile <br>')
        self.htmldoc.write('first quartile => cuts off lowest 25% of data = 25th percentile <br>')
        self.htmldoc.write('third quartile => cuts off highest 25% of data, or lowest 75% = 75th percentile <br>')
        self.htmldoc.write('minimum => Lowest value of data set <br>')
        self.htmldoc.write('maximum => Hightest value of data set <br>')
        self.htmldoc.write('baseline set1 difference => Difference of medians of both sets in percennt.<br>')
        self.htmldoc.write('ttest p-value => Student\'s t-test p-value = probability the both data sets are equal <br>')
        self.htmldoc.write('ttest equality => If p-value is higher than 0.1, data sets are considered being equal with 90% probability. Otherwise the data sets are considered being different.<br>')
        self.htmldoc.write('Linear regression of all results regression line is in y = ax form, b coeficient is zero. </p>')
        self.htmldoc.write('<p>for details about operations performed see <a href="http://www.iozone.org/docs/IOzone_msword_98.pdf">Iozone documentation</a>')
        self.htmldoc.write('</p>')

    def write_multiset_info(self):
        self.htmldoc.write('<DL class="filelist">')
        for setName in sorted(self.filenames.keys()):
            self.htmldoc.write('<DT><STRONG>' + setName + ' data set</STRONG><UL>')
            for file_name in self.filenames[setName]:
                self.htmldoc.write('<LI>'+file_name)
            self.htmldoc.write('</UL>')
        self.htmldoc.write('</DL>')
        self.htmldoc.write('<p>Plotted values are median with first and third quartile errorbars.<br>')
        self.htmldoc.write('median => Second quartile = cuts data set in half = 50th percentile <br>')
        self.htmldoc.write('first quartile => cuts off lowest 25% of data = 25th percentile <br>')
        self.htmldoc.write('third quartile => cuts off highest 25% of data, or lowest 75% = 75th percentile <br>')
        self.htmldoc.write('<p>for details about operations performed see <a href="http://www.iozone.org/docs/IOzone_msword_98.pdf">Iozone documentation</a>')
        self.htmldoc.write('</p>')

    def normal_mode(self):
        self.write_header()
        self.norm_summary()
        self.plotter.summary(self.fs.summary_base, self.fs.summary_set1)

        for op in self.plotter.order:
            if op not in self.fs.common_ops:
                break
            self.norm_operation(op)            
        self.write_info()
        self.write_footer()
        
    def norm_operation(self, Op):
        self.htmldoc.write('<hr>\n')
        self.htmldoc.write('<h3 id="' + Op + '">' + self.googlecharts.opnames[Op] + '</h3>\n')
        self.htmldoc.write('<div id="'+ Op + '_fs" class="normplot plot"></div>\n')
        self.htmldoc.write(self.googlecharts.norm_plot(Op, self.fs))
        self.norm_table(Op, self.fs)
        self.htmldoc.write('<div id="'+ Op + '_bs" class="normplot plot"></div>\n')
        self.htmldoc.write(self.googlecharts.norm_plot(Op, self.bs))
        self.norm_table(Op, self.bs)
        self.norm_regression(Op)
        self.htmldoc.write('<a href="#top">Back on top</a>\n')
        

    def norm_table(self, Op, Source):
        self.htmldoc.write('<table>\n')
        # table header
        self.htmldoc.write('<tr>')
        self.htmldoc.write('<th class=\"bottomline\">'+self.googlecharts.opnames[Op]+'</th>\n')
        self.htmldoc.write('<th class=\"bottomline\">'+Source.base[Op].xlabel+'</th>\n')
        for colname in Source.base[Op].colnames:
            self.htmldoc.write('<th>'+str(int(colname))+'</th>\n')
        self.htmldoc.write('</tr>\n')

        # the two table main parts
        self.norm_table_set(Op, Source, 'baseline')
        self.norm_table_set(Op, Source, 'set1')

        self.write_diff_ttest(Source.differences[Op], Source.ttest_pvals[Op], Source.ttest_res[Op])

        self.htmldoc.write('</table>\n')

    def write_diff_ttest(self, Diffs, Pvals, Results):
        # write differences
        self.htmldoc.write('<tr class=\"bottomline topline\">\n')
        self.htmldoc.write('<td colspan="2">baseline set1 difference</td>\n')
        for diff in Diffs:
            self.htmldoc.write('<td>'+str(round(diff,2))+' % </td>\n')
        self.htmldoc.write('</tr>\n')

        # write p-values
        self.htmldoc.write('<tr class=\"bottomline\">\n')
        self.htmldoc.write('<td colspan="2">ttest p-value</td>\n')
        for pval in Pvals:
            self.htmldoc.write('<td>'+str(round(pval,4))+'</td>\n')
        self.htmldoc.write('</tr>\n')

        # write ttest results in text form
        self.htmldoc.write('<tr class=\"bottomline\">\n')
        self.htmldoc.write('<td colspan="2">ttest equality</td>\n')
        for res in Results:
            self.htmldoc.write('<td>'+res+'</td>\n')
        self.htmldoc.write('</tr>\n')

    def norm_table_set(self, Op, Source, SetName):
        self.htmldoc.write('<tr class=\"topline\">\n')
        self.htmldoc.write('<td rowspan="10">' + SetName + '</td><td>mean val.</td>\n')
        for mean in Source.base[Op].means:
            self.htmldoc.write('<td class=\"topline\">'+str(round(mean,2))+'</td>\n')
        self.htmldoc.write('</tr>\n')

        rows = (('standard dev.', Source.base[Op].devs), ('ci. min. 90%', Source.base[Op].ci_mins),
            ('ci. max. 90%', Source.base[Op].ci_maxes), ('geom. mean', Source.base[Op].gmeans),
            ('<b>median</b>', Source.base[Op].medians), ('<b>first quartile</b>', Source.base[Op].first_qrts),
            ('<b>third quartile</b>', Source.base[Op].third_qrts), ('minimum', Source.base[Op].mins),
            ('maximum', Source.base[Op].maxes))
        for (name, data) in rows:
            self.htmldoc.write('<td>' + name + '</td>\n')
            for val in data:
                self.htmldoc.write('<td>'+str(round(val,2))+'</td>\n')
            self.htmldoc.write('</tr>\n')

    def norm_summary(self):
        rownames = ('standard dev.', 'ci. min. 90%', 'ci. max. 90%', 'geom. mean',
            'median', 'first quartile', 'third quartile', 'minimum', 'maximum')

        self.htmldoc.write('<h3 id="summary top">Overall summary</h3>')
        self.htmldoc.write('<img src=\"summary.png\" alt=\"summary\" class="plot"/>\n')
        self.htmldoc.write('<table>\n')
        self.htmldoc.write('<tr>')
        self.htmldoc.write('<td/><td>Operation</td>\n')
        for op in self.plotter.order:
            if op not in self.fs.common_ops:
                break
            self.htmldoc.write('<td><a href=\"#' + op + '\">'+self.googlecharts.opnames[op]+'</a></td>\n')
        self.htmldoc.write('</tr>\n')

        # summary data is stored in fs instance, no need for counting this redundantly in bs
        for (setname, source) in (('baeline', self.fs.summary_base), ('set1', self.fs.summary_set1)):
            self.htmldoc.write('<tr class=\"topline\">\n')
            self.htmldoc.write('<td rowspan="10">' + setname + '</td><td>mean val.</td>\n')
            for val in source[0]:
                self.htmldoc.write('<td>'+str(round(val,2))+'</td>\n')
            self.htmldoc.write('</tr>\n')
            for i in range(len(rownames)):
                self.htmldoc.write('<td>' + rownames[i] + '</td>\n')
                # source[0] is mean
                for val in source[1+i]:
                    self.htmldoc.write('<td>'+str(round(val,2))+'</td>\n')
                self.htmldoc.write('</tr>\n')

        self.htmldoc.write('<tr class=\"bottomline topline\">\n')
        self.htmldoc.write('<td colspan="2">linear regression slope 90%</td>\n')
        for op in self.plotter.order:
            if op not in self.fs.common_ops:
                break
            self.htmldoc.write('<td>'+str(round(self.fs.regressionLines[op].confIntMin,2))+' - '+str(round(self.fs.regressionLines[op].confIntMax,2))+'</td>\n')
        self.htmldoc.write('</tr>\n')

        self.write_diff_ttest(self.fs.summary_diffs, self.fs.summary_pvals, self.fs.summary_res)
        self.htmldoc.write('</table>\n')

    def norm_regression(self, Op):
        slope = self.fs.regressionLines[Op].slope
        std_err = self.fs.regressionLines[Op].stdError
        ci_min = self.fs.regressionLines[Op].confIntMin
        ci_max = self.fs.regressionLines[Op].confIntMax

        self.htmldoc.write('<img src=\"' + Op + '_compare.png\" alt=\"' + Op + '\_compare" class="plot"/>\n')
        self.plotter.regression(Op, self.fs.regressionLines[Op])

        self.htmldoc.write('<table><tr><th colspan="2"> Regression line </th></tr>\n')
        self.htmldoc.write('<tr class=\"topline\"><td> slope </td><td>' + str(round(slope,5)) + '</td></tr>\n')
        self.htmldoc.write('<tr class=\"topline\"><td> std. error </td><td>' + str(round(std_err,5)) + '</td></tr>\n')
        self.htmldoc.write('<tr class=\"topline bottomline\"><td> ci. max 90% </td><td>' + str(round(ci_min,5)) + '</td></tr>\n')
        self.htmldoc.write('<tr><td> ci. min. 90% </td><td>' + str(round(ci_max,5)) + '</td></tr></table>\n')

    def init_multiset_mode(self, dataSets, filenames):
        self.multiset = dataSets
        self.filenames = filenames

    def multiset_mode(self):
        self.write_header()
        for op in self.plotter.order:
            if op not in self.multiset.common_ops:
                break
            self.multiset_operation(op)            
        self.write_multiset_info()
        self.write_footer()

    def multiset_operation(self, op):
        self.htmldoc.write('<h3 id="' + op + '">' + self.googlecharts.opnames[op] + '</h3>\n')
        self.htmldoc.write('<div id="'+ op + '_fs" class="normplot plot"></div>\n')
        self.htmldoc.write(self.googlecharts.multiset_plot(op, self.multiset.fs, 'fs'))
        self.htmldoc.write('<div id="'+ op + '_bs" class="normplot plot"></div>\n')
        self.htmldoc.write(self.googlecharts.multiset_plot(op, self.multiset.bs, 'bs'))
        self.htmldoc.write('<a href="#top">Back on top</a>\n')
        self.htmldoc.write('<hr>\n')

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'

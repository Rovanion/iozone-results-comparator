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
from jinja2 import Template

class Highcharts:
    def __init__(self):
        self.opnames={"iwrite":"Write", "rewrite":"Re-write", "iread":"Read",
        "reread":"Re-read", "randrd":"Random read", "randwr":"Random write",
        "bkwdrd":"Backwards read", "recrewr":"Record rewrite", "striderd":"Strided Read",
        "fwrite":"Fwrite","frewrite":"Frewrite", "fread":"Fread", "freread":"Freread", "ALL":"ALL"}

        self.order=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
        "striderd", "fwrite", "frewrite", "fread", "freread"]

        self.normTemplate = Template('''<script type='text/javascript'>
            $(function () { 
                $('#{{ id }}').highcharts({
                    chart: {
		            	zoomType: 'xy'
		            },
                    title: {
                        text: '{{ title }}'
                    },
                    xAxis: {
                        title: {
                            text: '{{ xlabel }}'
                        }
                    },
                    yAxis: {
                        title: {
                            text: 'Operation speed [MB/s]'
                        }
                    },
                    tooltip: {
			            shared: true
		            },
                    series: [{
                        name: 'baseline',
			            type: 'spline',
                        color : 'black',
			            data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
                        tooltip: {
                            pointFormat: '<b>{series.name}:</b> median <b>{point.y:.1f} MB/s</b>, '
                        }
		            }, {
			            type: 'errorbar',
			            data: [[6, 8], [5.9, 7.6], [9.4, 10.4], [14.1, 15.9], [18.0, 20.1], [21.0, 24.0], [23.2, 25.3], [26.1, 27.8], [23.2, 23.9], [18.0, 21.1], [12.9, 14.0], [7.6, 10.0]],
			            tooltip: {
                            pointFormat: 'first quartile <b>{point.low} MB/s</b>, third quartile <b>{point.high} MB/s</b><br/>'
			            }
		            }, {
                        name: 'set1',
			            type: 'spline',
                        color : 'red',
                        data: [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
                        tooltip: {
                            pointFormat: '<span style="font-weight: bold; color: {series.color}">{series.name}:</span> median <span style="font-weight: bold; color: {series.color}">{point.y:.1f} MB/s</span>, '
                        }
		            }, {
			            type: 'errorbar',
                        color : 'red',
                        data: [[48, 51], [68, 73], [92, 110], [128, 136], [140, 150], [171, 179], [135, 143], [142, 149], [204, 220], [189, 199], [95, 110], [52, 56]],
			            tooltip: {
                            pointFormat: 'first quartile <span style="font-weight: bold; color: {series.color}">{point.low} MB/s</span>,third quartile <span style="font-weight: bold; color: {series.color}">{point.high} MB/s</span><br/>'
			            }
                    }]
                });
            });
        </script>
        ''')
        
    def norm_plot(self, Op, Source):
        datalines = [Source.base[Op].medians, Source.set1[Op].medians]
        errorbars_mins = [numpy.array(Source.base[Op].medians)
            - numpy.array(Source.base[Op].first_qrts), 
            numpy.array(Source.set1[Op].medians)
            - numpy.array(Source.set1[Op].first_qrts)] 
        errorbars_maxes = [numpy.array(Source.base[Op].third_qrts)
            - numpy.array(Source.base[Op].medians), 
            numpy.array(Source.set1[Op].third_qrts)
            - numpy.array(Source.set1[Op].medians)] 

        textstr = 'Plotted values are\n - first quartile\n - median\n - third quartile\nfor each datapoint.'
        colnames = Source.op_common_cols[Op]

        return self.normTemplate.render(id = Op + '_' + Source.base[Op].datatype,
                title = self.opnames[Op], xlabel = Source.base[Op].xlabel)
            
#        plt.clf()
#        # create plot lines for both sets
#        p=plt.plot(colnames,datalines[0],'o-',color='black',label='baseline')
#        plt.errorbar(colnames,datalines[0], yerr=[errorbars_mins[0], errorbars_maxes[0]] ,color='black', fmt='o-',)
#        p=plt.plot(colnames,datalines[1],'o-',color='red',label='set1')
#        plt.errorbar(colnames,datalines[1], yerr=[errorbars_mins[1], errorbars_maxes[1]] ,color='red', fmt='o-',)
#        
#        plt.grid(True)
#        plt.semilogx()
#        #plt.semilogy()
#        plt.xlabel(Source.base[Op].xlabel)
#        plt.ylabel('Operation speed [MB/s]')
#        plt.title(self.opnames[Op])
#        # add legend details
#        font = FontProperties(size='small');
#        a = plt.legend(loc=0, prop=font);
#        txt = matplotlib.offsetbox.TextArea(textstr, textprops=dict(size=7))
#        box = a._legend_box
#        box.get_children().append(txt)
#        box.set_figure(box.figure)
#
#        # Fedora 14 bug 562421 workaround
#        with warnings.catch_warnings():
#            warnings.filterwarnings("ignore",category=UserWarning)
#            plt.savefig(self.outdir + '/' + Op + '_' + Source.base[Op].datatype)
#
#        plt.clf()


#    def summary(self, Base, Set1):
#        # create the whiskers summary plot
#        textstr = 'Plotted values are\n - (sample minimum)\n - lower quartile \n - median\n - upper quartine\n - (sample maximum)\nfor each datapoint.'
#        plt.clf()
#        width=0.35
#        x=numpy.arange(len(Base))
#
#        # baseline set1 bars one next another
#        x1=x+width/2
#        x2=x+1.5*width
#
#        fig = plt.figure()
#        DefaultSize = fig.get_size_inches()
#        fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]))
#        ax = fig.add_subplot(111)
#
#        # whiskers
#        # Base[5] - meds
#        # Base[8] - mins
#        # Base[9] - maxes
#        ax.errorbar(x1,Base[5],yerr=[numpy.array(Base[5]) - numpy.array(Base[8]),numpy.array(Base[9]) - numpy.array(Base[5])],color='red',linestyle='None',marker='None')
#        ax.errorbar(x2,Set1[5],yerr=[numpy.array(Set1[5]) - numpy.array(Set1[8]),numpy.array(Set1[9]) - numpy.array(Set1[5])],color='black',linestyle='None',marker='None')
#
#        # baseline bars
#        # Base[6] - first quartiles
#        # Base[7] - third quartiles
#        rects1 = ax.bar(x,numpy.array(Base[5]) - numpy.array(Base[6]),width,bottom=Base[6],color='red')
#        ax.bar(x,numpy.array(Base[7]) - numpy.array(Base[5]),width,bottom=Base[5],color='red')
#
#        # set1 bars
#        rects2 = ax.bar(x+width,numpy.array(Set1[5]) - numpy.array(Set1[6]),width,bottom=Set1[6],color='white')
#        ax.bar(x+width,numpy.array(Set1[7]) - numpy.array(Set1[5]),width,bottom=Set1[5],color='white')
#
#        ax.set_ylabel('Operation speed [MB/s]')
#        ax.set_title('Summary sorted by operation')
#        ax.set_xticks(x+width)
#        opNames = []
#        # operations names on X axis
#        # TODO operations missing?
#        for op in self.order:
#            opNames.append(self.opnames[op])
#        ax.set_xticklabels(tuple(opNames), size=9)
#
#        # legend
#        font = FontProperties(size='small');
#        a = plt.legend((rects1[0], rects2[0]), ('Baseline', 'Set1'), loc=0, prop=font);
#        txt = matplotlib.offsetbox.TextArea(textstr, textprops=dict(size=7))
#        box = a._legend_box
#        box.get_children().append(txt)
#        box.set_figure(box.figure)
#
#        # Fedora 14 bug 562421 workaround
#        with warnings.catch_warnings():
#            warnings.filterwarnings("ignore",category=UserWarning)
#            plt.savefig(self.outdir+'/'+'summary')
#
#        fig.set_size_inches( (DefaultSize[0]/1.5, DefaultSize[1]))
#        plt.clf()

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


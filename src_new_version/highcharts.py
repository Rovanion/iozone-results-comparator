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

import json
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
                        text: '{{ title }}',
                        style : {
                            color : 'black'
                        }
                    },
                    xAxis: {
                        title: {
                            text: '{{ xlabel }}',
                            style : {
                                color : 'black'
                            }
                        },
                        categories : {{ categories }}
                    },
                    yAxis: {
                        title: {
                            text: 'Operation speed [MB/s]',
                            style : {
                                color : 'black'
                            }
                        }
                    },
                    tooltip: {
			            shared: true
		            },
                    series: [{
                        name: 'baseline',
			            type: 'spline',
                        color : 'black',
			            data: {{ baselineData }},
                        tooltip: {
                            pointFormat: '<b>{series.name}:</b> median <b>{point.y:.1f} MB/s</b>, '
                        }
		            }, {
			            type: 'errorbar',
			            data: {{ baselineErrBars }},
			            tooltip: {
                            pointFormat: 'first quartile <b>{point.low:.1f} MB/s</b>, third quartile <b>{point.high:.1f} MB/s</b><br/>'
			            }
		            }, {
                        name: 'set1',
			            type: 'spline',
                        color : 'red',
                        data: {{ set1Data }},
                        tooltip: {
                            pointFormat: '<span style="font-weight: bold; color: {series.color}">{series.name}:</span> median <span style="font-weight: bold; color: {series.color}">{point.y:.1f} MB/s</span>, '
                        }
		            }, {
			            type: 'errorbar',
                        color : 'red',
                        data: {{ set1ErrBars }},
			            tooltip: {
                            pointFormat: 'first quartile <span style="font-weight: bold; color: {series.color}">{point.low:.1f} MB/s</span>,third quartile <span style="font-weight: bold; color: {series.color}">{point.high:.1f} MB/s</span><br/>'
			            }
                    }]
                });
            });
        </script>
        ''')
        
    def norm_plot(self, Op, Source):
        baselineErrBars = []
        for i in range(0, len(Source.base[Op].first_qrts)):
            baselineErrBars.append([Source.base[Op].first_qrts[i], Source.base[Op].third_qrts[i]])

        set1ErrBars = []
        for i in range(0, len(Source.set1[Op].first_qrts)):
            set1ErrBars.append([Source.set1[Op].first_qrts[i], Source.set1[Op].third_qrts[i]])

        categories = []
        x = 4
        for i in range(0, len(Source.base[Op].medians)):
            categories.append(x)
            x = x*2


        return self.normTemplate.render(id = Op + '_' + Source.base[Op].datatype,
                title = self.opnames[Op], xlabel = Source.base[Op].xlabel, 
                baselineData = json.dumps(Source.base[Op].medians),
                baselineErrBars = json.dumps(baselineErrBars),
                set1Data = json.dumps(Source.set1[Op].medians),
                set1ErrBars = json.dumps(set1ErrBars), 
                categories = categories)

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


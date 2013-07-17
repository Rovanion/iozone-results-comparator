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
        self.summaryTemplate = Template('''<script type='text/javascript'>
            $(function () {
                $('#summary').highcharts({
            
                    chart: {
                        type: 'boxplot'
                    },
                    
                    title: {
                        text: 'Summary sorted by operation',
                        style : {
                            color : 'black'
                        }
                    },
                    
            
                    xAxis: {
                        categories: {{ categories }},
                        title: {
                            text: 'Operation',
                            style : {
                                color : 'black'
                            }
                        }
                    },
                    
                    yAxis: {
                        title: {
                            text: 'Operation speed [MB/s]',
                            style : {
                                color : 'black'
                            }
                        }
                    },
                
                    series: [{
                        name: 'baseline',
                        data: {{ baseline }},
                        color : 'black',
                        tooltip: {
                            headerFormat: '{point.key}<br/>'
                        }
                    }, {
                        name: 'set1',
                        data: {{ set1 }},
                        color : 'red',
                        tooltip: {
                            headerFormat: '{point.key}<br/>'
                        }
                    }]
                
                });
            });
        </script>
        ''')
        self.regressionTemplate = Template('''<script type='text/javascript'>
            $(function () {
                $('#{{ id }}_regression').highcharts({
                    chart: {
                        zoomType: 'xy'
                    },
                    title: {
                        text: 'Linear regression of all {{ operation }} values',
                        style : {
                            color : 'black'
                        }
                    },
                    xAxis: {
                        title: {
                            text: 'baseline throughput [MB/s]',
                            style : {
                                color : 'black'
                            }
                        }
                    },    
                    yAxis: {
                        title: {
                            text: 'set1 throughput [MB/s]',
                            style : {
                                color : 'black'
                            }
                        }
                    },            
                    series: [{
                        name: 'faster in baseline',
                        type: 'scatter',
                        data: [[1,1],[4,3]],
                        zIndex: 1,
                        marker: {
                            fillColor: 'red',
                        }
                    }, {
                        name: 'faster in set1',
                        type: 'scatter',
                        data: [[1,2],[3,5]],
                        zIndex: 1,
                        marker: {
                            fillColor: 'black',
                        }
                    }, {
                        name: 'reg. line 90% conf. int.',
                        data: [[0,0], [19,23]],
                        type: 'arearange',
                        color: 'pink',
                        fillOpacity: 0.3,
                        zIndex: 0,
                        pointInterval : 20
                    }, {
                        name: 'y=x line',
                        data: [[0,0], [20, 20]],
                        type: 'line',
                        color: 'black',
                        zIndex: 0,
                        marker: {
                            enabled: false
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

    # TODO the ALL pseudooperation
    def summary(self, Base, Set1):
        # whiskers
        # Base[5] - meds
        # Base[8] - mins
        # Base[9] - maxes
        # baseline bars
        # Base[6] - first quartiles
        # Base[7] - third quartiles
        categories = []
        baseline = []
        set1 = []
        for i in range(0, len(self.order)):
            categories.append(self.opnames[self.order[i]])
            baseline.append([Base[8][i], Base[6][i], Base[5][i], Base[7][i], Base[9][i]])
            set1.append([Set1[8][i], Set1[6][i], Set1[5][i], Set1[7][i], Set1[9][i]])

        return self.summaryTemplate.render(categories = json.dumps(categories),
                baseline = json.dumps(baseline), set1 = json.dumps(set1))

    def regression(self, Op, Base, Set1):
        return self.regressionTemplate.render(id = Op, operation = self.opnames[Op])

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


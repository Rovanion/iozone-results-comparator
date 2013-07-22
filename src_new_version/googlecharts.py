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

import json
from jinja2 import Template

class GoogleCharts:
    def __init__(self):
        self.opnames={"iwrite":"Write", "rewrite":"Re-write", "iread":"Read",
        "reread":"Re-read", "randrd":"Random read", "randwr":"Random write",
        "bkwdrd":"Backwards read", "recrewr":"Record rewrite", "striderd":"Strided Read",
        "fwrite":"Fwrite","frewrite":"Frewrite", "fread":"Fread", "freread":"Freread", "ALL":"ALL"}

        self.order=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
        "striderd", "fwrite", "frewrite", "fread", "freread", "ALL"]

        self.normTemplate = Template('''<script type="text/javascript">
            // Load the Visualization API and the piechart package.
            google.load('visualization', '1.0', {'packages':['corechart']});
            // Set a callback to run when the Google Visualization API is loaded.
            google.setOnLoadCallback(drawChart);
            // Callback that creates and populates a data table, 
            // instantiates the chart, passes in the data and draws it.
            function drawChart() {
                var data = new google.visualization.DataTable();
                data.addColumn('string', 'This does not matter'); // Implicit domain label col.
                data.addColumn('number', 'baseline'); // Implicit series 1 data col.
                data.addColumn({type:'number', role:'interval', label:'Bar'});  // interval role col.
                data.addColumn({type:'number', role:'interval'});  // interval role col.
                data.addColumn('number', 'set1'); // Implicit series 1 data col.
                data.addColumn({type:'number', role:'interval'});  // interval role col.
                data.addColumn({type:'number', role:'interval'});  // interval role col.
                data.addRows({{ dataRows }});
            // Set chart options
            var options = {title : '{{ title }}', colors : ['black', 'red'],
                focusTarget : 'category', vAxis : {title : 'Operation speed [MB/s]'},
                hAxis : {title : '{{ xlabel }}', textStyle : {fontSize : 9}}};
            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.LineChart(document.getElementById('{{ id }}'));
            chart.draw(data, options);
        }
        </script>''')
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
                        data: {{ baselineFaster }},
                        zIndex: 1,
                        marker: {
                            fillColor: 'red',
                        }
                    }, {
                        name: 'faster in set1',
                        type: 'scatter',
                        data: {{ set1Faster }},
                        zIndex: 1,
                        marker: {
                            fillColor: 'black',
                        }
                    }, {
                        name: 'reg. line 90% conf. int.',
                        data: [[0,0], [{{ ciMin }}, {{ ciMax }}]],
                        type: 'arearange',
                        color: 'pink',
                        fillOpacity: 0.3,
                        zIndex: 0,
                        pointInterval : {{ maxX }}
                    }, {
                        name: 'y=x line',
                        data: [[0,0], [{{ maxX }}, {{ maxX }}]],
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
        # columns have following meanding:
        # xAxisLabel, baseline median, base errbar low, base errbar high, set1 median, set1 errbar low, set1 errbar high
        dataRows = []
        
        x = 4
        for i in range(0, len(Source.base[Op].medians)):
            dataRows.append([str(x), round(Source.base[Op].medians[i], 2),
                round(Source.base[Op].first_qrts[i], 2),
                round(Source.base[Op].third_qrts[i], 2), round(Source.set1[Op].medians[i], 2),
                round(Source.set1[Op].first_qrts[i], 2), round(Source.set1[Op].third_qrts[i], 2)])
            x = x*2

        return self.normTemplate.render(id = Op + '_' + Source.base[Op].datatype,
                title = self.opnames[Op], xlabel = Source.base[Op].xlabel, 
                dataRows = json.dumps(dataRows))

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

    def regression(self, Op, RegLine):
        baselineFaster = []
        set1Faster = []
        maxX = 0
        for (x, y) in RegLine.points:
            if (x > maxX):
                maxX = x
            if (x < y):
                baselineFaster.append([x, y])
            else:
                set1Faster.append([x, y])

        return self.regressionTemplate.render(id = Op, operation = self.opnames[Op],
                baselineFaster = json.dumps(baselineFaster), 
                set1Faster = json.dumps(set1Faster), maxX = maxX,
                ciMin = RegLine.confIntMin * maxX, ciMax = RegLine.confIntMax * maxX)

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


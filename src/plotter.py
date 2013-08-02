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

import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties

class Plotter:
    def __init__(self, OutDir):
        self.outdir = OutDir
        self.opnames={"iwrite":"Write", "rewrite":"Re-write", "iread":"Read",
        "reread":"Re-read", "randrd":"Random\nread", "randwr":"Random\nwrite",
        "bkwdrd":"Backwards\nread", "recrewr":"Record\nrewrite", "striderd":"Strided\nRead",
        "fwrite":"Fwrite","frewrite":"Frewrite", "fread":"Fread", "freread":"Freread", "ALL":"ALL"}

        self.order=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
        "striderd", "fwrite", "frewrite", "fread", "freread", "ALL"]
        
    def summary(self, Base, Set1):
        # create the whiskers summary plot
        textstr = 'Plotted values are\n - (sample minimum)\n - lower quartile \n - median\n - upper quartine\n - (sample maximum)\nfor each datapoint.'
        plt.clf()
        width=0.35
        x=numpy.arange(len(Base))

        # baseline set1 bars one next another
        x1=x+width/2
        x2=x+1.5*width

        fig = plt.figure()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*1.75, DefaultSize[1]))
        ax = fig.add_subplot(111)

        # whiskers
        # Base[5] - meds
        # Base[8] - mins
        # Base[9] - maxes
        ax.errorbar(x1,Base[5],yerr=[numpy.array(Base[5]) - numpy.array(Base[8]),numpy.array(Base[9]) - numpy.array(Base[5])],color='red',linestyle='None',marker='None')
        ax.errorbar(x2,Set1[5],yerr=[numpy.array(Set1[5]) - numpy.array(Set1[8]),numpy.array(Set1[9]) - numpy.array(Set1[5])],color='black',linestyle='None',marker='None')

        # baseline bars
        # Base[6] - first quartiles
        # Base[7] - third quartiles
        rects1 = ax.bar(x,numpy.array(Base[5]) - numpy.array(Base[6]),width,bottom=Base[6],color='red')
        ax.bar(x,numpy.array(Base[7]) - numpy.array(Base[5]),width,bottom=Base[5],color='red')

        # set1 bars
        rects2 = ax.bar(x+width,numpy.array(Set1[5]) - numpy.array(Set1[6]),width,bottom=Set1[6],color='white')
        ax.bar(x+width,numpy.array(Set1[7]) - numpy.array(Set1[5]),width,bottom=Set1[5],color='white')

        ax.set_ylabel('Operation speed [MB/s]')
        ax.set_title('Summary sorted by operation')
        ax.set_xticks(x+width)
        opNames = []
        # operations names on X axis
        # TODO operations missing?
        for op in self.order:
            opNames.append(self.opnames[op])
        ax.set_xticklabels(tuple(opNames), size=9)

        # legend
        font = FontProperties(size='small');
        a = plt.legend((rects1[0], rects2[0]), ('Baseline', 'Set1'), loc=0, prop=font);
        txt = matplotlib.offsetbox.TextArea(textstr, textprops=dict(size=7))
        box = a._legend_box
        box.get_children().append(txt)
        box.set_figure(box.figure)
        plt.savefig(self.outdir+'/'+'summary')

    def regression(self, Op, RegLine):
        name = Op + '_compare'
        maxX = 0
        baselineFasterX = []
        baselineFasterY = []
        set1FasterX = []
        set1FasterY = []
        # faster in baseline will be plotted in red, faster in set1 in black
        for (x, y) in RegLine.points:
            if (x > maxX):
                maxX = x
            if (x > y):
                baselineFasterX.append(x)
                baselineFasterY.append(y)
            else:
                set1FasterX.append(x)
                set1FasterY.append(y)

        plt.clf()
        fig = plt.figure()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*1.75, DefaultSize[1]))
        ax = fig.add_subplot(111)
        #  Legend does not support <class 'matplotlib.collections.PolyCollection'> workaround. This line is not actually visible
        d, = ax.plot([0, 1.05*maxX], [0, 1.05*maxX*((RegLine.confIntMax+RegLine.confIntMin)/2)], '-', color='pink')
        a, = ax.plot(baselineFasterX, baselineFasterY, 'r.')
        b, = ax.plot(set1FasterX, set1FasterY, 'k.')
        # y = x line
        c, = ax.plot([0, 1.05*maxX], [0, 1.05*maxX], 'k-')
        # ci_min line
        ax.plot([0, 1.05*maxX], [0, 1.05*maxX*RegLine.confIntMin], 'r-')
        # ci_maxX line
        ax.plot([0, 1.05*maxX], [0, 1.05*maxX*RegLine.confIntMax], 'r-')
        # filling between ci_min and ci_maxX lines
        ax.fill_between([0, 1.05*maxX], [0, 1.05*maxX*RegLine.confIntMin], [0, 1.05*maxX*RegLine.confIntMax], color='pink')
        plt.grid(True)
        plt.xlabel('baseline throughput [MB/s]')
        plt.ylabel('set1 throughput [MB/s]')
        plt.title('Linear regression of all ' + self.opnames[Op] + ' values')
        font = FontProperties(size='x-small');
        leg = plt.legend((a, b, c, d), ('Faster in baseline', 'Faster in set1', 'y = x line', 'reg. line 90% conf. int.'), loc=0, prop=font);
        plt.savefig(self.outdir+'/'+name)
        
    def percentual_plot(self, Op, Source):
        xVals = []
        yVals = []
        diameters = []
        colors = []
        base = Source.base[Op].indexedData
        set1 = Source.set1[Op].indexedData

        for (bs, fs) in base:
            xVals.append(str(fs))
            yVals.append(str(bs))
            baseAvg = numpy.mean(base[(bs, fs)])
            set1Avg = numpy.mean(set1[(bs, fs)])
            colors.append('k' if set1Avg > baseAvg else 'r')
            diameters.append(10 * abs((baseAvg-set1Avg))/(baseAvg/100))

        plt.clf()
        fig = plt.figure()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*1.75, DefaultSize[1]))

        plt.grid()
        plt.scatter(xVals, yVals, diameters, colors, label='foo')
        plt.loglog(basex=2, basey=2)

        plt.xlabel('File size')
        plt.ylabel('Block size')
        plt.title('Percentual difference')

        plt.savefig(self.outdir + '/' +  Op + '_pcnt')

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


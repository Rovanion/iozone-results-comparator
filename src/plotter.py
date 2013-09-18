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

    def summary(self, Base, Set1, ops):
        # create the whiskers summary plot
        textstr = 'Plotted values are\n - (sample minimum)\n - lower quartile \n - median\n - upper quartine\n - (sample maximum)\nfor each datapoint.'
        plt.clf()
        width=0.35
        x=numpy.arange(len(Base[5]))

        # baseline set1 bars one next another
        x1=x+width/2
        x2=x+1.5*width

        fig = plt.figure()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*1.75, DefaultSize[1]))
        ax = fig.add_subplot(111)

        # whiskers
        # Base[1] - meds
        # Base[3] - mins
        # Base[4] - maxes
        ax.errorbar(x1,Base[1],yerr=[numpy.array(Base[1]) - numpy.array(Base[3]),numpy.array(Base[4]) - numpy.array(Base[1])],color='red',linestyle='None',marker='None')
        ax.errorbar(x2,Set1[1],yerr=[numpy.array(Set1[1]) - numpy.array(Set1[3]),numpy.array(Set1[4]) - numpy.array(Set1[1])],color='black',linestyle='None',marker='None')

        # baseline bars
        # Base[0] - first quartiles
        # Base[2] - third quartiles
        rects1 = ax.bar(x,numpy.array(Base[1]) - numpy.array(Base[0]),width,bottom=Base[0],color='red')
        ax.bar(x,numpy.array(Base[2]) - numpy.array(Base[1]),width,bottom=Base[1],color='red')

        # set1 bars
        rects2 = ax.bar(x+width,numpy.array(Set1[1]) - numpy.array(Set1[0]),width,bottom=Set1[0],color='white')
        ax.bar(x+width,numpy.array(Set1[2]) - numpy.array(Set1[1]),width,bottom=Set1[1],color='white')

        ax.set_ylabel('Operation speed [MB/s]')
        ax.set_title('Summary sorted by operation')
        ax.set_xticks(x+width)
        opNames = []
        # operations names on X axis
        for op in ops:
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
        base = Source.base[Op].indexedData
        set1 = Source.set1[Op].indexedData

        # percent categories tune here:
        categories = [0, 5, 15, 30, float('inf')]
        colorsSlower = ['#FFFF66', '#FFBB00', '#FF7700', '#FF0000']
        colorsFaster = ['#0066FF', '#000099', '#660066', '#000000']

        plt.clf()
        fig = plt.figure()
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0]*1.75, DefaultSize[1]))
        plt.grid()

        # this is ineffective, but the code is much nicer to read this way
        for catNr in range(len(categories) - 2, -1, -1):    # going backwards produces nicer legend
            baseX = []
            baseY = []
            baseDia = []
            set1X = []
            set1Y = []
            set1Dia = []

            for (bs, fs) in base:
                baseAvg = numpy.mean(base[(bs, fs)])
                set1Avg = numpy.mean(set1[(bs, fs)])
                pcnt = abs((baseAvg-set1Avg))/(baseAvg/100)
                if (pcnt < categories[catNr]) or (pcnt >= categories[catNr + 1]): 
                    continue
                if set1Avg > baseAvg:
                    set1X.append(str(fs))
                    set1Y.append(str(bs))
                    set1Dia.append(10 * pcnt)
                else:
                    baseX.append(str(fs))
                    baseY.append(str(bs))
                    baseDia.append(10 * pcnt)

            intLeft = str(categories[catNr])
            intRight = str(categories[catNr + 1])
            if intRight == 'inf':
                name = ' > ' + intLeft + '%'
            else:
                name = intLeft + '% - ' + intRight + '%'

            if len(baseDia) > 0:
                plt.scatter(baseX, baseY, baseDia, colorsSlower[catNr], label='Slower in Set1 ' + name)
            if len(set1Dia) > 0:
                plt.scatter(set1X, set1Y, set1Dia, colorsFaster[catNr], label='Faster in Set1 ' + name)
        
        plt.loglog(basex=2, basey=2)
        plt.xlabel('File size')
        plt.ylabel('Block size')
        plt.title('Percentual difference')

        plt.legend(loc = 'upper left', scatterpoints = 1, fontsize = 10)

        plt.savefig(self.outdir + '/' +  Op + '_pcnt')

if __name__ == '__main__':
    print 'Try running iozone_results_comparator.py'


#!/usr/bin/python

#   iozone_results_comparator.py - parse iozone output files and write stats and plots to output html
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
sys.path.append('/exports/perf/python')
import os
import argparse
import re
import numpy
from scipy import stats
import warnings
import shutil
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager, FontProperties

out_dir='Compare-html' # normal mode output directory name
out_file='index.html' # main html file name
tabdDir = 'Tab_delimited' # tab delimited output directory

# write html header and page beginning
# htmldoc - where to write
# baseFiles - input files used to get baseline data
# set1Files - input files used to get set1 data
def write_header(htmldoc, baseFiles, set1Files, title='Iozone', header='Iozone results'):
	html_header='''
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> 
	<title>'''+title+'''</title>
	</head>
	<body>
	<link rel="stylesheet" type="text/css" href="stylesheet.css">
	<div class="main">
	<div class="inner">

	<h1 id="top">
	'''+header+'''
	</h1>
	'''
	htmldoc.write(html_header)
	htmldoc.write('<DL class="filelist">')
	htmldoc.write('<DT><STRONG>Baseline data set</STRONG><UL>')
	for file_name in baseFiles:
		htmldoc.write('<LI>'+file_name)
	htmldoc.write('</UL>')
	htmldoc.write('<DT><STRONG>Investigated data set</STRONG><UL>')
	for file_name in set1Files:
		htmldoc.write('<LI>'+file_name)
	htmldoc.write('</UL>')
	htmldoc.write('</DL>')
	htmldoc.write('<p>mean => Arithmetic mean<br>')
	htmldoc.write('standar dev. => Sample standard deviation<br>')
	htmldoc.write('ci. max 90%, ci.min => confidence interval at confidence level 90% => it means that mean value of the distribution lies with 90% propability in interval ci_min-ci_max<br>')
	htmldoc.write('geom. mean => Geometric mean<br>')
	htmldoc.write('median => Second quartile = cuts data set in half = 50th percentile <br>')
	htmldoc.write('first quartile => cuts off lowest 25% of data = 25th percentile <br>')
	htmldoc.write('third quartile => cuts off highest 25% of data, or lowest 75% = 75th percentile <br>')
	htmldoc.write('minimum => Lowest value of data set <br>')
	htmldoc.write('maximum => Hightest value of data set <br>')
	htmldoc.write('baseline set1 difference => Difference of medians of both sets in percennt. Arithmetic means are used in detail mode instead.<br>')
	htmldoc.write('ttest p-value => Student\'s t-test p-value = probability the both data sets are equal <br>')
	htmldoc.write('ttest equality => If p-value is higher than 0.1, data sets are considered being equal with 90% probability. Otherwise the data sets are considered being different.<br>')
	htmldoc.write('Linear regression of all results regression line is in y = ax form, b coeficient is zero. </p>')
	htmldoc.write('<p>for details about operations performed see <a href="http://www.iozone.org/docs/IOzone_msword_98.pdf">Iozone documentation</a>')
	htmldoc.write('</p>')
	return;

# end the page and close htmldoc
# htmldoc - where to write
def write_footer(htmldoc):
	html_footer='''
	</div>
	</div>
	</body>
	</html>
	'''
	htmldoc.write(html_footer)
	return

# create the plot image file
# graphlabel - label on the top of plot
# xlabel - label of x axis
# ylabel - label of y axis
# data - data in write_operation format
# name - figure name
# semilogx - wheather use logaritmic scale on X axis
# semilogy - wheather use logaritmic scale on Y axis
# type - to differ normal and detail mode plots
def make_plot(graphlabel,xlabel,ylabel,data,name,semilogx=False,semilogy=False, type='normal'):
	# check for data delimeters, wheather it can be plotted
	ok=True
	l=len(data[0][2])+1 #JH
	for data_item in data[1:]:
		for run in data_item[2]:
			if len(run)!=l:
				ok=False
	if not ok:
		print 'figure '+name+' has different vector sizes, skipping plot'
		sys.stdout.flush()
		print l,
		for data_item in data[1:]:
			for run in data_item[2]:
				print len(run),
				
		print ''
		return

	# different values are being plotted in normal and detail mode
	datalines = []
	errorbars_maxes = []
	errorbars_mins = []
	if (type == 'normal'):
		datalines.append(data[1][9])
		datalines.append(data[2][9])
		errorbars_mins.append(numpy.array(data[1][9]) - numpy.array(data[1][10]))
		errorbars_mins.append(numpy.array(data[2][9]) - numpy.array(data[2][10]))
		errorbars_maxes.append(numpy.array(data[1][11]) - numpy.array(data[1][9]))
		errorbars_maxes.append(numpy.array(data[2][11]) - numpy.array(data[2][9]))
		textstr = 'Plotted values are\n - first quartile\n - median\n - third quartile\nfor each datapoint.'
	elif (type == 'detail'):
		datalines.append(data[1][3])
		datalines.append(data[2][3])
		errorbars_mins.append(numpy.array(data[1][3]) - numpy.array(data[1][5]))
		errorbars_mins.append(numpy.array(data[2][3]) - numpy.array(data[2][5]))
		errorbars_maxes.append(numpy.array(data[1][6]) - numpy.array(data[1][3]))
		errorbars_maxes.append(numpy.array(data[2][6]) - numpy.array(data[2][3]))
		textstr = 'Plotted values are\n - ci. min. 90%\n - mean val.\n - ci. max 90%\nfor each datapoint.'
	else:
		print 'unknown make_plot function type parameter'
		return

	# get rid of starting and/or ending zero values - useful for detail mode
	minIndex = 0
	maxIndex = len(data[0][2])
	while (datalines[0][minIndex] == datalines[1][minIndex] == 0):
		minIndex += 1
	while (datalines[0][maxIndex - 1] == datalines[1][maxIndex - 1] == 0):
		maxIndex -= 1
	
	plt.clf()
	# create plot lines for both sets
	for i in range(len(datalines)):
		p=plt.plot(data[0][2][minIndex:maxIndex],datalines[i][minIndex:maxIndex],'o-',color=data[i+1][1],label=data[i+1][0])
		plt.errorbar(data[0][2][minIndex:maxIndex],datalines[i][minIndex:maxIndex], yerr=[errorbars_mins[i][minIndex:maxIndex], errorbars_maxes[i][minIndex:maxIndex]] ,color=data[i+1][1], fmt='o-',)
	
	plt.grid(True)
	if semilogx:
		plt.semilogx()
	if semilogy:
		plt.semilogy()
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(graphlabel)
	# add legend details
	font = FontProperties(size='small');
	a = plt.legend(loc=0, prop=font);
	txt = matplotlib.offsetbox.TextArea(textstr, textprops=dict(size=7))
	box = a._legend_box
	box.get_children().append(txt)
	box.set_figure(box.figure)

	# Fedora 14 bug 562421 workaround
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore",category=UserWarning)
		plt.savefig(out_dir+'/'+name)

	plt.clf()
	return

# class to parse iozone results from input data files
class Parse_iozone:
	# init, check wheather input files are readable
	def __init__(self,iozone_file_list):
		self.names=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
				"striderd", "fwrite", "frewrite", "fread", "freread"]
		self.names_dictionary = {}
		count = 0
		for item in self.names:
			self.names_dictionary[item]=count
			++count

		self.files=[]
		self.operations = [] #List of operations
		self.columns = {}
		assert (iozone_file_list is not None)
		for file_name in iozone_file_list:
			if os.access(file_name, os.R_OK):
				self.files.append(file_name)
			else:
				sys.stderr.write('File "%s" is not readable.\n' % (file_name))
		self.read_all_files()
		self.get_all_operations()

	# split line to get data for operations
	def split_iozone_line(self,line):
		field_list = [16, 8, 8, 8, 9, 9, 8, 8, 8, 9, 9, 9, 9, 8, 9]
		offset = 0
		output = []
		line=line.rstrip('\n')
		for i in range(len(field_list)):
			width = field_list[i]
			substring=line[offset:width+offset]
			offset += width
			if len(substring) == width:
				matchObj = re.match( r'^\s+$', substring, re.M)
				if matchObj:
					output.append(None)
				else:
					output.append(int(substring))
			else:
				output.append(None)
				if i != len(field_list) -1 or ( width - len(substring) ) > 3 :
					sys.stderr.write('%s "%s"\n' % ("Line:", line ) )
					sys.stderr.write('\t%s "%s"\n' % ("Substring:", substring ) )
					sys.stderr.write('\t%s %d, %s %d\n' % ("Length:", len(substring), "Expecting:", width  ) )
		return output

	# read data from input files
	def read_all_files(self):
		file_counter = 0
		for file_name in self.files:
			this_file_columns = {}
			++file_counter
			f = open(file_name, "r")
			for line in f:
				matchObj = re.match( r'^\s+\d+\s+\d+\s+\d+', line, re.M)
				if matchObj:
					#Data lines
					line_in_array = self.split_iozone_line(line);
					#sys.stderr.write('%s\t%s\n' % (line_in_array[0],line_in_array[-1]) )
					file_size = line_in_array.pop(0);
					block_size = line_in_array.pop(0);
					for j in range( 0, len(self.names), 1 ):
						column_name = self.names[j]
						full_column_name = 'FS_' + str(file_size) + '_BLOCK_' + str(block_size) + '_' + column_name
						key=(file_size,block_size,column_name)
						if ( j>len(line_in_array) ) or ( line_in_array[j] is None ):
							#Check if key exists already
							if ( file_counter > 1 and self.columns.has_key(key) ):
								sys.stderr.write('%s: file number %d: value %s exists in previous files but not in this one!\n'
										%(file_name, file_counter, full_column_name) )
								self.columns[key].append(None)
								this_file_columns[key]=None
						else:
							# We have non-empty value
							if ( file_counter > 1 and not (self.columns.has_key(key) ) ):
								sys.stderr.write('%s: file number %d: value %s is not defined in previous files!\n'
									%(file_name, file_counter, full_column_name) )
								self.columns[key]=[]
								for temp_file_counter in range (1,file_counter-1,1):
									self.columns[key].append(None)
							#Now add values to the array
							if not (self.columns.has_key(key) ):
								self.columns[key]=[]

							self.columns[key].append(line_in_array[j]/1024.0)
							this_file_columns[key]=None

			#File parsing is complete.
			for key in self.columns.iterkeys():
				if ( not ( this_file_columns.has_key(key) ) ):
					sys.stderr.write('%s: file number %d: value %s exists in previous files but not in this one!\n'
							%(file_name, file_counter, full_column_name) )
					self.columns[key].append(None)
					this_file_columns[key]=None
		return

	# check which operations were present on inut iozone files
	def get_all_operations(self):
		all_names = {}

		for key in self.columns.iterkeys():
			(FS,BS,NAME) = key
			all_names[NAME] = self.names_dictionary[NAME]

		for item in self.names:
			if item in all_names.keys():
				self.operations.append(item)

		return

	# return part of write_operation format data for operation , FS oriented
	def get_FS_list_for_any_BS(self,operation):
		all_BS = {}
		all_FS = {}
		x = []
		y = []
		for key in self.columns.iterkeys():
			(FS,BS,NAME) = key
			if ( NAME == operation):
				if not all_BS.has_key(BS):
					all_BS[BS]=[]
				all_BS[BS].append(FS)
				if not all_FS.has_key(FS):
					all_FS[FS]=[]
				all_FS[FS].append(BS)

		for FS in sorted(all_FS.keys()):
			#List of all file sizes
			x.append(FS)

		for BS in sorted(all_BS.keys()):
			for file_number in range (len(self.files)):
				row = []
				row.append(BS)
				for FS in sorted(all_FS.keys()):
					#We are creating a row of table
					#Columns - different file sizes (FS)
					# format is array ['label',Y_for_FS1, Y_for_FS2]
					#We need to check if Y_for_FS1 exists
					if self.columns.has_key((FS,BS,operation)):
						assert(len( self.columns[(FS,BS,operation)]  ) == len(self.files))
						row.append(self.columns[FS,BS,operation][file_number])
					else:
						row.append(0)
				y.append(row)
		return (x,y)

	# return part of write_operation format data for operation , BS oriented
	def get_BS_list_for_any_FS(self,operation):
		all_BS = {}
		all_FS = {}
		x = []
		y = []
		for key in self.columns.iterkeys():
			(FS,BS,NAME) = key
			if ( NAME == operation):
				if not all_BS.has_key(BS):
					all_BS[BS]=[]
				all_BS[BS].append(FS)
				if not all_FS.has_key(FS):
					all_FS[FS]=[]
				all_FS[FS].append(BS)

		for BS in sorted(all_BS.keys()):
			#List of all block sizes
			x.append(BS)

		for FS in sorted(all_FS.keys()):
			for file_number in range (len(self.files)):
				row = []
				row.append(FS)
				for BS in sorted(all_BS.keys()):
					#We are creating a row of table
					#Columns - different block sizes (BS)
					# format is array ['label',Y_for_BS1, Y_for_BS2]
					#We need to check if Y_for_BS1 exists
					if self.columns.has_key((FS,BS,operation)):
						assert(len( self.columns[(FS,BS,operation)]  ) == len(self.files))
						row.append(self.columns[FS,BS,operation][file_number])
					else:
						row.append(0)
				y.append(row)
		return (x,y)

	# return all set data for operation given
	def get_all_for_operation(self,operation):
		result = []
		for key in self.columns.iterkeys():
			(FS,BS,NAME) = key
			if ( NAME == operation):
				for val in self.columns[key]:
					result.append(val)
		return result

	# get all set data for all operations
	def get_all_data_list(self):
		result = []
		for key in self.columns.iterkeys():
			for val in self.columns[key]:
				result.append(val)
		return result

# checks wheather is file readable
# file_name - file to check
def is_file_readable(file_name):
	if os.access(file_name, os.R_OK):
		return file_name
	else:
		msg='File "%s" is not readable.\n' % (file_name)
		raise argparse.ArgumentTypeError(msg)

# count mean, standard deviation and confidence interval of data given in list
# data = input data onedimensional list
# confidence = confidence interval probability rate in percent
# m = mean
# sd = standard deviation
# h = error
# m-h = confidence interval min
# m+h = confidence interval max
# gm = geometric mean
# med = median
# frstQrt = first quartile
# thrdQrt = third quartile
# minVal = sample minimum
# maxVal = sample maximum
def mean_confidence_interval(data, confidence=0.90):
	actualInput = remove_zeros_from_list(data)

	# if input were all zeros
	if not actualInput:
		return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

	n = len(actualInput)
	m = numpy.mean(actualInput) # arithmetic mean
	gm = stats.gmean(actualInput) # geometric mean
	med = numpy.median(actualInput) # median
	frstQrt = stats.scoreatpercentile(actualInput, 25) # first quartile
	thrdQrt = stats.scoreatpercentile(actualInput, 75) # third quartile
	minVal = sorted(actualInput)[0]
	maxVal = sorted(actualInput)[-1]

	sd = numpy.std(actualInput, ddof=1) # delta degree of freedom = 1  -  sample standard deviation (Bessel's correction)
	se = sd/numpy.sqrt(n) # standard error
	h = se * stats.t._ppf((1+confidence)/2., n-1) # confidence interval
	return (m, sd, h, m-h, m+h, gm, med, frstQrt, thrdQrt, minVal, maxVal)

# compute all statistical values here
# data is twodimensional array
# order - order of column data values
# returns vectors of statistical values describing input data columns
def compute_all_stats(data, order=None):
	# if no order given, just walk through data
	if (order == None):
		order = range(len(data))

	devs=[]
	avgs=[]
	ci_mins=[]
	ci_maxes=[]
	errs=[]
	gms=[]
	meds=[]
	frstQrts=[]
	thrdQrts=[]
	minVals=[]
	maxVals=[]

	for colNr in order:
		(avg, dev, err, ci_min, ci_max, gm, med, frstQrt, thrdQrt, minVal, maxVal) = mean_confidence_interval(data[colNr])
		avgs.append(avg)
		devs.append(dev)
		errs.append(err)
		ci_mins.append(ci_min)
		ci_maxes.append(ci_max)
		gms.append(gm)
		meds.append(med)
		frstQrts.append(frstQrt)
		thrdQrts.append(thrdQrt)
		minVals.append(minVal)
		maxVals.append(maxVal)

	return (avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)

# count ttest p-value from two sets of tada
# data[[baseline col1, baseline col2, ...], [set1 col1, set1 col2, ]]
# return [col1 result, col2 result]
def ttest_equality(data):
	res = []
	for i in range(len(data[0])):
		# scipy's ttest uses mean from scipy, which is deprecated. this is temporary workout
		# until it's fixed to use mean from numpy
		with warnings.catch_warnings():
			warnings.filterwarnings("ignore",category=DeprecationWarning)
			(tstat, pval) = stats.ttest_ind(remove_zeros_from_list(data[0][i]), remove_zeros_from_list(data[1][i]))
		res.append(pval)
	return res

# self-explanatory
# list input, outputs list with zero values erased
def remove_zeros_from_list(dataIn):
	# get rid of zeros. Zero indicates value missing, so there is no
	# intention to take it as a valid value.
	actualInput = []
	for i in dataIn:
		if (i != float(0)):
			actualInput.append(i)
	return actualInput

# count statistics in one dimension for data given

# input data format:
#data[0][0]=label for x values
#data[0][1]=label for values to be agregated in second col
#data[0][2]=[column names]
#data[1][0]=label for set
#data[1][1]=color for set
#data[1][2]=[[row1_name, run1_value_for_col1,run1_value_for_col2], [row2_name, run1_value_for_col1,run1_value_for_col2],]

# adds folloiwing to input data:
# data[i][3] = arithmetic means
# data[i][4] = deviations
# data[i][5] = ci_mins
# data[i][6] = ci_maxes
# data[i][7] = errors
# data[i][8] = geometric means
# data[i][9] = medians
# data[i][10] = first quartiles
# data[i][11] = third quartiles
# data[i][12] = minimal Values
# data[i][13] = maximal Values
# data[-1] = ttest results
def stats_one_dim(data):
	# basic check for expected data format
	assert(len(data)==3)
	for i in range(1,len(data)):
		nrOfCols=len(data[1][2][0])-1
		cols=[] # list of lists of colunn values.
		for f in range(nrOfCols):
			cols.append([])

		# get data from input format to cols data structure
		for v in range(len(data[i][2])):
			for j in range(nrOfCols):
				cols[j].append(float(data[i][2][v][j+1])) # fill column list

		# compute statistics
		(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(cols, range(nrOfCols))
		# append results to input
		data[i].append(avgs)
		data[i].append(devs)
		data[i].append(ci_mins)
		data[i].append(ci_maxes)
		data[i].append(errs)
		data[i].append(gms)
		data[i].append(meds)
		data[i].append(frstQrts)
		data[i].append(thrdQrts)
		data[i].append(minVals)
		data[i].append(maxVals)

		if (i == 1): # computing baseline
			baselineCols = cols

	# compute ttest
	ttestInput=[baselineCols]
	ttestInput.append(cols)
	data.append(ttest_equality(ttestInput))
	return

# remove columns full of zeros in both sets
# data - data - [setNr][row]
# data are changed in situ, return index of firs non-zero column(from original data)
def remove_all_zeros_columns(data):
	# detect all-zeros columns
	oldNrOfCols=len(data[0][0])
	zeros = []
	for i in range(oldNrOfCols):
		zeros.append(True)

	# if there is single non-zero value, the column is not emply
	for colNr in range(oldNrOfCols): # for every column
		for set in data: # for both sets
			for row in set: # for every line
				if (row[colNr] != 0):
					zeros[colNr] = False

	# remove all-zeros columns - we count averages, otherwise we would divide by a zero
	for colNr in reversed(range(oldNrOfCols)): # for every column
		for setNr in range(len(data)): # for both sets
			for rowNr in range(len(data[setNr])): # for every line
				if (zeros[colNr]):
					del data[setNr][rowNr][colNr]
	# return index of first valid column
	for i in range(len(zeros)):
		if not (zeros[i]):
			return i

# detail mode for closer view to one operation results
# it basicaly does what __main__ does in normal mode
# base - Parse_iozone object with baseline data
# set1 - Parse_iozone object with set1 data
# operation - operation to write
def detail(base, set1, operation):
	global out_dir
	# all operations - recursively call detail function for all operations
	if (operation == 'ALL'):
		for op in set1.names:
			detail(base, set1, op)
		sys.exit(0)

	if not (operation in set1.names):
		print 'Unknown operation ' + operation
		print 'Valid operations are: ' + ', '.join(set1.names) + ', ALL'
		sys.exit(1)

	# Fixed Block Size
	print 'writing detailed info about ' + operation + ' for fixed block size'
	out_dir='Compare_' + operation + '_for_fixed_Block_Size'
	try:
		shutil.rmtree('./'+out_dir)
	except:
		pass
	os.makedirs(out_dir)
	shutil.copyfile('./stylesheet.css',out_dir+'/stylesheet.css')
	htmldoc=open(out_dir+'/'+out_file,'w')

	# prepare data to write_operation data format
	write_header(htmldoc, base.files, set1.files, operation + ' for fixed BS', 'Iozone results for ' + operation +', data are arranged by block size');
	data = []
	data.append(['File size [kB]','Block size [kB]'])
	data.append(['baseline','black'])
	(x1,y1)=base.get_FS_list_for_any_BS(operation)
	data[0].append(x1)
	data[1].append(y1)
	data.append(['set1','red'])
	(x2,y2)=set1.get_FS_list_for_any_BS(operation)
	assert(x1==x2)
	data[2].append(y2)

	# call write function
	write_detail_html(htmldoc,operation,data)
	write_footer(htmldoc)
	htmldoc.close()

	# Fixed file size
	print 'writing detailed info about ' + operation + ' for fixed file size'
	out_dir='Compare_' + operation + '_for_fixed_File_Size'
	try:
		shutil.rmtree('./'+out_dir)
	except:
		pass
	os.makedirs(out_dir)
	shutil.copyfile('./stylesheet.css',out_dir+'/stylesheet.css')
	htmldoc=open(out_dir+'/'+out_file,'w')

	# prepare data to write_operation data format
	write_header(htmldoc, base.files, set1.files, operation + ' for fixed FS', 'Iozone results for ' +  operation + ', data are arranged by file size');
	data = []
	data.append(['Block size [kB]', 'File size [kB]'])
	data.append(['baseline','black'])
	(x1,y1)=base.get_BS_list_for_any_FS(operation)
	data[0].append(x1)
	data[1].append(y1)
	data.append(['set1','red'])
	(x2,y2)=set1.get_BS_list_for_any_FS(operation)
	assert(x1==x2)
	data[2].append(y2)

	# call write function
	write_detail_html(htmldoc,operation,data)
	write_footer(htmldoc)
	htmldoc.close()

	print 'Finished.\nTo view detailed info about ' + operation + ' see following pages in your web browser'
	print 'file://' + os.getcwd() + '/Compare_' + operation + '_for_fixed_Block_Size/index.html'
	print 'file://' + os.getcwd() + '/Compare_' + operation + '_for_fixed_File_Size/index.html'

# write tables and plots in detail mode
# basicaly what write_operation function does in normal mode, although not only stats are printed, also prints the data
# htmldoc - where to write
# operation - name of operation being currently written
# data - data in write_operation function format
def write_detail_html(htmldoc,operation,data):
	# aggregate values
	agrVals = [{},{}] # {'block size': [[file1_col1, file1_col2, ..], [file2_col1, file2_col2,...] ...]}
	# for every set
	for i in range(len(data)-1):
		# for every block/file size
		for v in range(len(data[i+1][2])):
			key = data[i+1][2][v][0]
			val = data[i+1][2][v][1:] # cutting row name
			if not key in agrVals[i].keys():
				agrVals[i][key] = []
			agrVals[i][key].append(val)

	# for every key
	for key in sorted(agrVals[0].keys()):
		# remove all zeros columns. starColNr = first valid column number, needed for propriate legend
		startColNr = remove_all_zeros_columns([ agrVals[0][key], agrVals[1][key] ])
		nrOfCols=len(agrVals[0][key][0])

		htmldoc.write('<a name="'+str(key)+'"></a> \n')
		htmldoc.write('<img src=\"'+str(key)+'.png\" alt=\"'+str(key)+'\" class="plot"  />\n')

		htmldoc.write('<table>\n')
		htmldoc.write('<tr class=\"bottomline\">')
		htmldoc.write('<td rowspan=\"2\"/>\n')
		htmldoc.write('<td rowspan=\"2\">'+data[0][1]+'</td>\n')
		htmldoc.write('<td colspan=\"'+str(nrOfCols)+'\">' + data[0][0] + '</td>\n')
		htmldoc.write('</tr>\n')
		htmldoc.write('<tr>')
		for m in range(startColNr, startColNr + nrOfCols):
			htmldoc.write('<td>'+str(int(data[0][2][m]))+'</td>\n')
		htmldoc.write('</tr>\n')

		# for both sets
		for i in range(len(data)-1):
			for rowNr in range(len(agrVals[i][key])):
				if (rowNr == 0):
					htmldoc.write('<tr class=\"topline\">')
					htmldoc.write('<td rowspan=\"'+str(len(agrVals[i][key])+10)+'\">'+data[i+1][0]+'</td>')
					htmldoc.write('<td>'+str(int(key))+'</td>')
				else:
					htmldoc.write('<tr>')
					htmldoc.write('<td>'+str(int(key))+'</td>')
				for val in agrVals[i][key][rowNr]:
					htmldoc.write('<td>'+str(round(val,2))+'</td>')

				htmldoc.write('</tr>\n')

			# prepare data for stats
			columnValues = [] # [[col1_row1, col1_row2, ...], [col2_row1, col2_row2, ...], ...]
			for m in data[0][2]:
				columnValues.append([])
			for row in agrVals[i][key]:
				for colNr in range(len(row)):
					columnValues[colNr].append(row[colNr])

			# compute statistics
			(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)

			if (i == 0):
				avgs_baseline = avgs
				columnValues_baseline = columnValues

			# statistic vals
			statVals = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
			# data nr value name
			valNames = ('mean val.', 'standard dev.', 'ci. min. 90%', 'ci. max 90%', 'geom. mean', 'median',
					'first quartile', 'third quartile', 'minimum', 'maximum')

			# write all statistic values
			for v in range(len(statVals)):
				if (v == 0):
					htmldoc.write('<tr class=\"topline\">\n')
				else:
					htmldoc.write('<tr>\n')
				htmldoc.write('<td>' + valNames[v] + '</td>\n')
				for m in range(nrOfCols):
					htmldoc.write('<td>'+str(round(statVals[v][m],2))+'</td>\n')
				htmldoc.write('</tr>\n')

			# append results to input
			data[i+1].append(avgs)
			data[i+1].append(devs)
			data[i+1].append(ci_mins)
			data[i+1].append(ci_maxes)
			data[i+1].append(errs)

		# count differences a ttest
		differences = []
		for m in range(nrOfCols):
			differences.append((avgs[m] /avgs_baseline[m] - 1) * 100)
		ttestInput=[[],[]]
		for i in range(nrOfCols):
			ttestInput[0].append(columnValues_baseline[i])
			ttestInput[1].append(columnValues[i])
		ttestResults = ttest_equality(ttestInput)
		# and let it be written
		write_diff_ttest(htmldoc, differences, ttestResults)

		# make plot
		make_plot(data[0][1]+' = '+str(key),data[0][0],'Operation speed [MB/s]',data,str(key),semilogx=True,semilogy=False, type='detail')
		# delete what was appended above to use make_plot function
		del data[1][3:]
		del data[2][3:]
	return

# write differences and ttest results and close table
# htmldoc - where to write
# differences - list of set1 baseline differences
# tterst Results - list of t-test p-values
def write_diff_ttest(htmldoc, differences, ttestResults):
	# write differences
	nrOfCols = len(differences)
	htmldoc.write('<tr class=\"bottomline topline\">\n')
	htmldoc.write('<td colspan="2">baseline set1 difference</td>\n')
	for m in range(nrOfCols):
		htmldoc.write('<td>'+str(round(differences[m],2))+' % </td>\n')
	htmldoc.write('</tr>\n')

	# write p-values
	htmldoc.write('<tr class=\"bottomline\">\n')
	htmldoc.write('<td colspan="2">ttest p-value</td>\n')
	for m in range(nrOfCols):
		htmldoc.write('<td>'+str(round(ttestResults[m],4))+'</td>\n')
	htmldoc.write('</tr>\n')

	# tuple ternary operator workaround
	ternary_op = ('DIFF', 'SAME')
	htmldoc.write('<tr class=\"bottomline\">\n')
	htmldoc.write('<td colspan="2">ttest equality</td>\n')
	# write ttest result according p-val
	for m in range(nrOfCols):
		if (math.isnan(ttestResults[m])):
			res = 'nan'
		else:
			res = ternary_op[(ttestResults[m] > 0.1)]
		htmldoc.write('<td>'+res+'</td>\n') # 90% probability
	htmldoc.write('</tr>\n')
	htmldoc.write('</table>\n')
	return

# write table of operation stats
# htmldoc - where to write
# operation - operation name
# data - input data in following format:

#data[0][0]=label for x values
#data[0][1]=label for values to be agregated in second col
#data[0][2]=[column names]
#data[1][0]=label for set
#data[1][1]=color for set
#data[1][2]=[[row1_name, run1_value_for_col1,run1_value_for_col2], [row2_name, run1_value_for_col1,run1_value_for_col2],]
# data[i][3] = arithmetic means
# data[i][4] = deviations
# data[i][5] = ci_mins
# data[i][6] = ci_maxes
# data[i][7] = errors
# data[i][8] = geometric means
# data[i][9] = medians
# data[i][10] = first quartiles
# data[i][11] = third quartiles
# data[i][12] = minimal Values
# data[i][13] = maximal Values
# data[-1] = ttest results

# filename - how to name plot image file
def write_operation(htmldoc,operation,data,filename):
	htmldoc.write('<img src=\"'+filename+'.png\" alt=\"'+filename+'\" class="plot"/>\n')

	htmldoc.write('<table>\n')
	# table header
	htmldoc.write('<tr>')
	htmldoc.write('<th class=\"bottomline\">'+operation_name(operation)+'</th>\n')
	htmldoc.write('<th class=\"bottomline\">'+data[0][0]+'</th>\n')
	for m in data[0][2]:
		htmldoc.write('<th>'+str(int(m))+'</th>\n')
	htmldoc.write('</tr>\n')

	nrOfCols=len(data[1][2][0])-1

	# compute statistics
	stats_one_dim(data)

	# for both data sets
	for i in range(1,(len(data)-1)):

		# agregate rows with the same row main value(BS/FS)
		agrVals={} # {'block size': [column number][val_file1, val_file2, ..], ...}
		for v in range(len(data[i][2])):
			for j in range(nrOfCols):
				# agregate by row name
				key = data[i][2][v][0]
				val = data[i][2][v][j+1]
				if not key in agrVals.keys():
					agrVals[key] = []
					for column in range(nrOfCols):
						agrVals[key].append([])
				agrVals[key][j].append(val)

		# recognize set name
		htmldoc.write('<tr class=\"topline\">\n')
		if (i == 1):
			htmldoc.write('<td rowspan="10">baseline</td><td>mean val.</td>\n')
		else:
			htmldoc.write('<td rowspan="10">set1</td><td>mean val.</td>\n')

		for m in range(nrOfCols):
			htmldoc.write('<td class=\"topline\">'+str(round((data[i][3][m]),2))+'</td>\n')
		htmldoc.write('</tr>\n')

		# data nr value name
		valNames = {4:'standard dev.', 5:'ci. min. 90%', 6:'ci. max 90%', 8:'geom. mean', 9:'median',
				10:'first quartile', 11:'third quartile', 12:'minimum', 13:'maximum'}

		# write all statistic values
		for v in sorted(valNames.keys()):
			htmldoc.write('<tr>\n')
			htmldoc.write('<td>' + valNames[v] + '</td>\n')
			for m in range(nrOfCols):
				htmldoc.write('<td>'+str(round(data[i][v][m],2))+'</td>\n')
			htmldoc.write('</tr>\n')

	# count differences
	differences = []
	for m in range(nrOfCols):
		differences.append((data[2][9][m] / data[1][9][m] - 1) * 100)
	# write differences and ttest results
	write_diff_ttest(htmldoc, differences, data[-1])

	# link to tabd, need inverse agregation
	if (filename == operation + '_BS'):
		inverseFSBS = '_FS'
	else:
		inverseFSBS = '_BS'
	hrefBaseline = operation + inverseFSBS + '_baseline.tsv'
	hrefSet1 = operation + inverseFSBS + '_set1.tsv'
	htmldoc.write('<div class=\"rawdata belowtable\">See raw data <a href=\"../'+tabdDir+'/'+hrefBaseline+'\">'+hrefBaseline+'</a>')
	htmldoc.write(' and <a href=\"../'+tabdDir+'/'+hrefSet1+'\">'+hrefSet1+'</a>.</div>\n')

	# dataXX[:-1] cuts data[3] where ttest results are stored, make_plot function cannot handle it itself
	make_plot(operation_name(operation),data[0][0],'Operation speed [MB/s]',data[:-1],filename,semilogx=True,semilogy=False, type='normal')
	return

# write Overall Summary plot and table
# data - both sets data in  [[(FS, BSdata)],[(FS, BSdata)]] # [0] = base, [1] = set1 format
# operations - operations order for tab delimited
# regLines - Linear regression of all results
def write_overFSBS_summary(resultsForOp, operations, regLines):
	htmldoc.write('<h3 id="summary">Overall summary</h3>')

	htmldoc.write('<img src=\"summary.png\" alt=\"summary\" class="plot"/>\n')
	htmldoc.write('<table>\n')
	htmldoc.write('<tr>')
	htmldoc.write('<td/><td>Operation</td>\n')
	for operation in operations:
		htmldoc.write('<td>'+operation_name(operation)+'</td>\n')
	htmldoc.write('</tr>\n')

	nrOfOps = len(resultsForOp[0].keys())
	setNr = 0

	# for both sets
	for i in range(len(resultsForOp)):
		setNr += 1

		# compute statistics
		(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(resultsForOp[i], operations)

		# save some values from baseline to not to be replaced by set1 values in second iteration
		if (i == 0):
			setname = 'baseline'
			meds_baseline = meds
			frstQrts_baseline = frstQrts
			thrdQrts_baseline = thrdQrts
			minVals_baseline = minVals
			maxVals_baseline = maxVals
		else:
			setname = 'set1'

		htmldoc.write('<tr class=\"topline\">\n')
		htmldoc.write('<td rowspan="10">'+setname+'</td><td>mean val.</td>\n')
		for m in range(nrOfOps):
			htmldoc.write('<td class=\"topline\">'+str(round(avgs[m],2))+'</td>\n')
		htmldoc.write('</tr>\n')

		# statistic vals
		statVals = (devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
		# data nr value name
		valNames = ('standard dev.', 'ci. min. 90%', 'ci. max 90%', 'geom. mean', 'median',
				'first quartile', 'third quartile', 'minimum', 'maximum')

		# write all statistic values
		for v in range(len(statVals)):
			htmldoc.write('<tr>\n')
			htmldoc.write('<td>' + valNames[v] + '</td>\n')
			for m in range(len(statVals[v])):
				htmldoc.write('<td>'+str(round(statVals[v][m],2))+'</td>\n')
			htmldoc.write('</tr>\n')

		if (setNr == 1):
			baseline_avgs = avgs

	htmldoc.write('<tr class=\"bottomline topline\">\n')
	htmldoc.write('<td colspan="2">linear regression slope 90%</td><td></td>\n')
	# excluding operation ALL
	for m in range(nrOfOps - 1):
		(slope, std_err, ci_min, ci_max) = regLines[m]
		htmldoc.write('<td>'+str(numpy.around(ci_min,2))+' - '+str(numpy.around(ci_max,2))+'</td>\n')
	htmldoc.write('</tr>\n')

	# compute and write differences and t-test values
	differences = []
	for m in range(nrOfOps):
		differences.append((meds[m] / meds_baseline[m] - 1) * 100)
	ttestInput=[[],[]]
	for operation in operations:
		ttestInput[0].append(resultsForOp[0][operation])
		ttestInput[1].append(resultsForOp[1][operation])
	ttestResults = ttest_equality(ttestInput)
	write_diff_ttest(htmldoc, differences, ttestResults)

	# link tab delimited
	hrefSorted = 'summary_sorted_by_operation_'
	htmldoc.write('<div class=\"rawdata belowtable\">See raw data <a href=\"../'+tabdDir+'/'+hrefSorted+'baseline.tsv\">'+hrefSorted+'baseline.tsv</a>')
	htmldoc.write(' and <a href=\"../'+tabdDir+'/'+hrefSorted+'set1.tsv\">'+hrefSorted+'set1.tsv</a>.<br>')
	htmldoc.write('All data are aggregated in <a href=\"../'+tabdDir+'/summary_all_baseline.tsv\">summary_all_baseline.tsv</a>.</div>')

	# create the whiskers summary plot
	textstr = 'Plotted values are\n - (sample minimum)\n - lower quartile \n - median\n - upper quartine\n - (sample maximum)\nfor each datapoint.'
	plt.clf()
	width=0.35
	x=numpy.arange(len(operations))

	# baseline set1 bars one next another
	x1=x+width/2
	x2=x+1.5*width

	fig = plt.figure()
	DefaultSize = fig.get_size_inches()
	fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]))
	ax = fig.add_subplot(111)

	# whiskers
	ax.errorbar(x1,meds_baseline,yerr=[numpy.array(meds_baseline) - numpy.array(minVals_baseline),numpy.array(maxVals_baseline) - numpy.array(meds_baseline)],color='red',linestyle='None',marker='None')
	ax.errorbar(x2,meds,yerr=[numpy.array(meds) - numpy.array(minVals),numpy.array(maxVals) - numpy.array(meds)],color='black',linestyle='None',marker='None')

	# baseline bars
	rects1 = ax.bar(x,numpy.array(meds_baseline) - numpy.array(frstQrts_baseline),width,bottom=frstQrts_baseline,color='red')
	ax.bar(x,numpy.array(thrdQrts_baseline) - numpy.array(meds_baseline),width,bottom=meds_baseline,color='red')

	# set1 bars
	rects2 = ax.bar(x+width,numpy.array(meds) - numpy.array(frstQrts),width,bottom=frstQrts,color='white')
	ax.bar(x+width,numpy.array(thrdQrts) - numpy.array(meds),width,bottom=meds,color='white')

	ax.set_ylabel('Operation speed [MB/s]')
	ax.set_title('Summary sorted by operation')
	ax.set_xticks(x+width)
	opNames = []
	# operations names on X axis
	for op in operations:
		opNames.append(operation_name(op))
	ax.set_xticklabels(tuple(opNames), size=9)

	# legend
	font = FontProperties(size='small');
	a = plt.legend((rects1[0], rects2[0]), ('Baseline', 'Set1'), loc=0, prop=font);
	txt = matplotlib.offsetbox.TextArea(textstr, textprops=dict(size=7))
	box = a._legend_box
	box.get_children().append(txt)
	box.set_figure(box.figure)

	# Fedora 14 bug 562421 workaround
	with warnings.catch_warnings():
		warnings.filterwarnings("ignore",category=UserWarning)
		plt.savefig(out_dir+'/'+'summary')

	plt.clf()
	return

# Return full iozone documentation name of operation
# operation this script internal operation name(no spaces, usable in filename)
def operation_name(operation):
	names={"iwrite":"Write", "rewrite":"Re-write", "iread":"Read",
	"reread":"Re-read", "randrd":"Random\nread", "randwr":"Random\nwrite",
	"bkwdrd":"Backwards\nread", "recrewr":"Record\nrewrite", "striderd":"Strided\nRead",
	"fwrite":"Fwrite","frewrite":"Frewrite", "fread":"Fread", "freread":"Freread", "ALL":"ALL"}
	return names[operation]

# write statistical values to the bottom lines of tab delimited output
# tabd - where to write
# statVals - list of values in specific order(see valNames var in this function)
def write_tabd_stats(tabd, statVals):
	# data nr value name
	valNames = ('mean val.', 'standard dev.', 'ci. min. 90%', 'ci. max 90%', 'geom. mean', 'median',
		'first quartile', 'third quartile', 'minimum', 'maximum')

	tabd.write('# Statistics (excluding 0 values)\n')
	for v in range(len(statVals)):
		tabd.write('#' + valNames[v])
		for m in range(len(statVals[v])):
			tabd.write('\t'+str(round(statVals[v][m],2)))
		tabd.write('\n')
	return

# write oocalc formulas to the end of tabd
# it's useful in verification this script computes the same stat values OO does
# tabd - where to write
# dataEnd - line number of last dataline
def write_oocalc_formulas(tabd, dataEnd):
	tabd.write('#OOCALC formulas\n')
	tabd.write('#mean val.\t=AVERAGE(B5:B' + dataEnd + ')\n')
	tabd.write('#standard dev.\t=STDEV(B5:B' + dataEnd + ')\n')
	tabd.write('#ci. min. 90%\t=AVERAGE(B5:B' + dataEnd + ')-TINV(1/10;COUNT(B5:B' + dataEnd + ')-1)*STDEV(B5:B' + dataEnd + ')/SQRT(COUNT(B5:B' + dataEnd + '))\n')
	tabd.write('#ci. max 90%\t=AVERAGE(B5:B' + dataEnd + ')+TINV(1/10;COUNT(B5:B' + dataEnd + ')-1)*STDEV(B5:B' + dataEnd + ')/SQRT(COUNT(B5:B' + dataEnd + '))\n')
	tabd.write('#geom. mean\t=GEOMEAN(B5:B' + dataEnd + ')\n')
	tabd.write('#median\t=MEDIAN(B5:B' + dataEnd + ')\n')
	tabd.write('#first quatile\t=QUARTILE(B5:B' + dataEnd + ';1)\n')
	tabd.write('#third quartile\t=QUARTILE(B5:B' + dataEnd + ';3)\n')
	tabd.write('#minimum\t=QUARTILE(B5:B' + dataEnd + ';0)\n')
	tabd.write('#maximum\t=QUARTILE(B5:B' + dataEnd + ';4)\n')

# craate tab delimieted output for single operation
# data - input in write_operation function format
# operation - name of operation being written
# fsbs - determines whether the data has FS or BS orientation - needed for file name
def tab_delimited(data, operation, fsbs):
	for setNr in range(1, len(data) - 1):
		if (setNr == 1):
			setName = 'baseline'
		else:
			setName = 'set1'
		tabdName = operation + '_' + fsbs + '_' + setName + '.tsv'
		tabd = open(tabdDir+'/'+tabdName, 'w')

		tabd.write('# ' + operation + ' throughput for any ' + fsbs + '. Open it with: LC_ALL=en_US.UTF-8\n')
		tabd.write('# Read this file into Open Office  with command oocalc <filename>\n')
		tabd.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
		tabd.write(data[0][0])
		for i in data[0][2]:
			tabd.write('\t'+str(i))
		tabd.write('\n')

		# write the data
		dataLineNr = 4
		rowNr = 0
		rowName = data[setNr][0]
		for row in data[setNr][2]:
			if (row[0] == rowName):
				rowNr += 1
			else:
				rowName = row[0]
				rowNr = 1
			tabd.write(data[0][1] + ' = ' + str(row[0])+' Run='+str(rowNr))
			for val in row[1:]:
				if (val != 0):
					val2write = str(round(val,2))
				else:
					val2write = ''
				tabd.write('\t' + val2write)
			tabd.write('\n')
			dataLineNr += 1

		# prepare data for stats
		columnValues = [] # [[col1_row1, col1_row2, ...], [col2_row1, col2_row2, ...], ...]
		for m in data[setNr][2][0][1:]:
			columnValues.append([])
		for row in data[setNr][2]:
			for colNr in range(1, len(row)):
				columnValues[colNr-1].append(row[colNr])

		# compute statistics
		(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)

		# write all statistic values
		statVals = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
		write_tabd_stats(tabd, statVals)
		write_oocalc_formulas(tabd, str(dataLineNr))
		tabd.close()
	return

# craate tab delimited output of sumary sorted by operation and overall summary
# data - both sets data in  [[(FS, BSdata)],[(FS, BSdata)]] # [0] = base, [1] = set1 format
# operations - operations order for tab delimited
def tab_delimited_summary(data, order):
	for setNr in range(len(data)):
		if (setNr == 0):
			setName = 'baseline'
		else:
			setName = 'set1'
		tabdOperationName = 'summary_sorted_by_operation' + '_' + setName + '.tsv'
		tabdAllName = 'summary_all' + '_' + setName + '.tsv'
		tabdOperation = open(tabdDir+'/'+tabdOperationName, 'w')
		tabdAll = open(tabdDir+'/'+tabdAllName, 'w')

		tabdOperation.write('# iozone measured throughput[MB/s] for any FS and any BS. Open it with: LC_ALL=en_US.UTF-8\n')
		tabdOperation.write('# Read this file into Open Office  with command oocalc <filename>\n')
		tabdOperation.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
		tabdAll.write('# iozone measured throughput[MB/s] for any FS, any BS and any operation. Open it with: LC_ALL=en_US.UTF-8\n')
		tabdAll.write('# Read this file into Open Office  with command oocalc <filename>\n')
		tabdAll.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
		tabdAll.write('ALL\n')

		tabdOperation.write('Operation')
		for operation in order:
			tabdOperation.write('\t'+operation)
		tabdOperation.write('\n')

		# prepare data for stats
		columnValues = [] # [[col1_row1, col1_row2, ...], [col2_row1, col2_row2, ...], ...]
		allSetData = []
		valsOp = {}
		valsAll = {}
		for m in order:
			columnValues.append([])

		# prepare data in format more usable for what will follow
		for opNr in range(len(data[setNr])):
			(x, y) = data[setNr][opNr]
			Run = 0
			FS = y[0][0]
			for row in y:
				if (row[0] == FS):
					Run += 1
				else:
					FS = row[0]
					Run = 1
				for bsNr in range(len(x)):
					valsOp[(FS, x[bsNr], Run, opNr)] = row[bsNr+1]
					valsAll[(opNr, FS, x[bsNr], Run)] = row[bsNr+1]
					columnValues[opNr].append(row[bsNr+1])
					allSetData.append(row[bsNr+1])

		# write conted of tabd sorted by operation
		row = []
		dataLineNr = 4
		for key in sorted(valsOp.keys()):
			(FS, BS, Run, opNr) = key
			if (valsOp[key] != 0):
				val = str(round(valsOp[key],2))
			else:
				val = ''
			row.append(val)
			if (opNr == 0):
				caption = 'Filesize[kB] = ' + str(FS) + ' Block size [kB] = ' + str(BS) + ' Run=' + str(Run)
			if (opNr == (len(order) - 1 )):
				empty = True;
				for val in row:
					if val:
						empty = False;
				if not (empty):
					tabdOperation.write(caption)
					for val in row:
						tabdOperation.write('\t' + val)
					tabdOperation.write('\n')
					dataLineNr += 1
				row = []

		# write overall tabd content
		tabdAllLine = 4
		for key in sorted(valsAll.keys()):
			(opNr, FS, BS, Run) = key
			if (valsAll[key] != 0):
				tabdAll.write('Operation ' + order[opNr] + ' Filesize[kB] = ' + str(FS) + ' Block size [kB] = ' + str(BS) + ' Run = ' + str(Run) + '\t' + str(round(valsAll[key],2)) + '\n')
				tabdAllLine += 1

		# compute statistics
		(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)

		# write all statistic values to tabd sorted by operation
		statValsOperation = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
		write_tabd_stats(tabdOperation, statValsOperation)
		write_oocalc_formulas(tabdOperation, str(dataLineNr))
		tabdOperation.close()


		# write all statistic values to all data tabd
		columnValues = [allSetData]
		(avgs, devs, errs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals) = compute_all_stats(columnValues)
		statValsAll = (avgs, devs, ci_mins, ci_maxes, gms, meds, frstQrts, thrdQrts, minVals, maxVals)
		write_tabd_stats(tabdAll, statValsAll)
		write_oocalc_formulas(tabdAll, str(tabdAllLine))
		tabdAll.close()
	return

# create visual comparisions of both sets plots and tab delimited
# data - both sets data in  [[(FS, BSdata)],[(FS, BSdata)]] # [0] = base, [1] = set1 format
# operations - operations order for tab delimited
def xy_fsbs_avg(data, operations):
	tabd = open(tabdDir+'/comparison_of_averages.tsv', 'w')
	tabd.write('# comparison of averages for iozone measured throughput[MB/s] for any FS and any BS. Open it with: LC_ALL=en_US.UTF-8\n')
	tabd.write('# Read this file into Open Office  with command oocalc <filename>\n')
	tabd.write('# Read this file into language R with command data <- read.delim("<filename>",comment.char = "#")\n')
	tabd.write('Operation')

	for operation in operations:
		tabd.write('\t'+operation+' baseline\t'+operation+' set1')
	tabd.write('\n')

	vals = {}
	# this might look strange, but when we don't have to search if key exists for every value, 
	# it saves a lot of runtime. Nicer code with key check will run for 30 secs, this one for four.
	for setNr in range(len(data)):
		for opNr in range(len(data[setNr])):
			(x, y) = data[setNr][opNr]
			Run = 0
			FS = y[0][0]
			for row in y:
				if (row[0] == FS):
					Run += 1
				else:
					FS = row[0]
					Run = 1
				for bsNr in range(len(x)):
					vals[(FS, x[bsNr], opNr, setNr)] = []

	# now is sure key exist, so place the values
	for setNr in range(len(data)):
		for opNr in range(len(data[setNr])):
			(x, y) = data[setNr][opNr]
			Run = 0
			FS = y[0][0]
			for row in y:
				if (row[0] == FS):
					Run += 1
				else:
					FS = row[0]
					Run = 1
				for bsNr in range(len(x)):
					if (row[bsNr+1] != 0):
						vals[(FS, x[bsNr], opNr, setNr)].append(row[bsNr+1])

	# compute averages of vals lists
	avgs = {}
	for key in sorted(vals.keys()):
		(FS, BS, opNr, setNr) = key
		if (vals[(FS, BS, opNr, setNr)]):
			avgs[(FS, BS, opNr, setNr)] = numpy.mean(vals[(FS, BS, opNr, setNr)])

	# column values for operations
	columnValues = []
	for op in operations:
		# two times - for both sets
		columnValues.append([])
		columnValues.append([])

	# write tab delimited and fill columnValues list
	row = []
	for key in sorted(avgs.keys()):
		(FS, BS, opNr, setNr) = key
		val = avgs[(FS, BS, opNr, setNr)]
		row.append(val)
		if (opNr == 0 and setNr == 0):
			caption = 'Filesize[kB] = ' + str(FS) + ' Block size [kB] = ' + str(BS)
		if (opNr == (len(operations) - 1 ) and setNr == 1):
			tabd.write(caption)
			for val in row:
				tabd.write('\t' + str(round(val,2)))
			tabd.write('\n')
			row = []
		columnValues[2 * opNr + setNr].append(val)

	# compute stats
	slopes = []
	std_errs = []
	ci_mins = []
	ci_maxes = []
	for opNr in range(len(operations)):
		(slope, std_err, ci_min, ci_max) = regline_slope(columnValues[2*opNr], columnValues[2*opNr+1])
		slopes.append(slope)
		std_errs.append(std_err)
		ci_mins.append(ci_min)
		ci_maxes.append(ci_max)

	# create plots
	for opNr in range(len(operations)):
		name = operations[opNr] + '_compare'
		baselineFasterX = []
		baselineFasterY = []
		set1FasterX = []
		set1FasterY = []
		# faster in baseline will be plotted in red, faster in set1 in black
		for i in range(len(columnValues[2*opNr])):
			if (columnValues[2*opNr][i] >= columnValues[2*opNr+1][i]):
				baselineFasterX.append(columnValues[2*opNr][i])
				baselineFasterY.append(columnValues[2*opNr+1][i])
			else:
				set1FasterX.append(columnValues[2*opNr][i])
				set1FasterY.append(columnValues[2*opNr+1][i])

		if (sorted(columnValues[2*opNr])[-1] > sorted(columnValues[2*opNr+1])[-1]):
			max = sorted(columnValues[2*opNr])[-1]
		else:
			max = sorted(columnValues[2*opNr+1])[-1]

		plt.clf()
		fig = plt.figure()
		ax = fig.add_subplot(111)
		#  Legend does not support <class 'matplotlib.collections.PolyCollection'> workaround. This line is not actually visible
		d = ax.plot([0, 1.05*max], [0, 1.05*max*((ci_maxes[opNr]+ci_mins[opNr])/2)], '-', color='pink')
		a = ax.plot(baselineFasterX, baselineFasterY, 'r.')
		b = ax.plot(set1FasterX, set1FasterY, 'k.')
		# y = x line
		c = ax.plot([0, 1.05*max], [0, 1.05*max], 'k-')
		# ci_min line
		ax.plot([0, 1.05*max], [0, 1.05*max*ci_mins[opNr]], 'r-')
		# ci_max line
		ax.plot([0, 1.05*max], [0, 1.05*max*ci_maxes[opNr]], 'r-')
		# filling between ci_min and ci_max lines
		ax.fill_between([0, 1.05*max], [0, 1.05*max*ci_mins[opNr]], [0, 1.05*max*ci_maxes[opNr]], color='pink')
		plt.grid(True)
		plt.xlabel('baseline throughput [MB/s]')
		plt.ylabel('set1 throughput [MB/s]')
		plt.title('Linear regression of all ' + operations[opNr] + ' values')
		font = FontProperties(size='x-small');
		leg = plt.legend((a, b, c, d), ('Faster in baseline', 'Faster in set1', 'y = x line', 'reg. line 90% conf. int.'), loc=0, prop=font);
		# Fedora 14 bug 562421 workaround
		with warnings.catch_warnings():
			warnings.filterwarnings("ignore",category=UserWarning)
			plt.savefig(out_dir+'/'+name)

	regLines = [] # regression lines info will be returned to be writted in form of tabs in __main__
	tabd.write('# Slope of regression line')
	for opNr in range(len(operations)):
		tabd.write('\t' + str(round(slopes[opNr],5)) + '\t')
		regLines.append((slopes[opNr], std_errs[opNr], ci_mins[opNr], ci_maxes[opNr]))
	tabd.write('\n')

	tabd.write('# Standard error of regression line slope')
	for opNr in range(len(operations)):
		tabd.write('\t' + str(round(std_errs[opNr],5)) + '\t')
	tabd.write('\n')

	tabd.write('# Regression line slope ci. min. 90%.')
	for opNr in range(len(operations)):
		tabd.write('\t' + str(round(ci_mins[opNr],5)) + '\t')
	tabd.write('\n')

	tabd.write('# Regression line slope ci. max 90%')
	for opNr in range(len(operations)):
		tabd.write('\t' + str(round(ci_maxes[opNr],5)) + '\t')
	tabd.write('\n')

	tabd.close()
	return regLines

# compute slope of regression line
# Xvals - array of X-axis values
# Yvals - array of Y-axis values of same lenght as Xvals
# return counted slope, standard error, confidence interval min and max
def regline_slope(Xvals, Yvals):
	x = numpy.array(Xvals)
	y = numpy.array(Yvals)
	AverageX = numpy.mean(Xvals)

	# slope a solves
	# a^2 * Sum[xi yi] + a * Sum [xi^2 - yi^2] - Sum [xi yi] = 0
	A = numpy.sum(x*y)
	B = numpy.sum([x**2 - y**2])
	discriminant = numpy.sqrt( B**2 + 4 * A**2)

	a = ( -B + discriminant ) / ( 2 * A )
	# distance of points from line with slope=a
	D = numpy.abs(a*x-y) / numpy.sqrt(a**2 + 1)
	# standard error of a
	a_se = numpy.sqrt( numpy.sum(D**2) / numpy.sum((x - AverageX)**2) / (len(x) - 1) )
	# 90% confidence interval
	h = a_se * stats.t._ppf((1+0.90)/2., len(x)-1)
	return (a, a_se, a-h, a+h)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Parse iozone files')
	parser.add_argument('--baseline', nargs='+',type=is_file_readable,required=True,
			help='Set of iozone result files to form the baseline.')
	parser.add_argument('--set1', nargs='+',type=is_file_readable,required=True,
			help='Set of iozone results files to compared against baseline.')
	parser.add_argument('--detail', nargs=1, required=False, action='store',
			help='Name of operation to have a closer look at.')
	args = parser.parse_args()

	# parse input files
	base=Parse_iozone(args.baseline)
	set1=Parse_iozone(args.set1)
	print 'Creating plots. This will take several seconds.'

	# detail mode
	if (args.detail != None):
		operation = ''.join(args.detail)
		detail(base, set1, operation)
		sys.exit()
	try:
		shutil.rmtree('./'+out_dir)
		shutil.rmtree('./'+tabdDir)
	except:
		pass

	# prepare output directories
	os.makedirs(out_dir)
	os.makedirs(tabdDir)
	shutil.copyfile('./stylesheet.css',out_dir+'/stylesheet.css')
	htmldoc=open(out_dir+'/'+out_file,'w')

	write_header(htmldoc, base.files, set1.files);
	for operation in set1.operations:
		htmldoc.write('<a href=\"#' + operation + '\">' + operation_name(operation) + '</a><br>\n')
	htmldoc.write('<a href=\"#summary\">Summary</a><br><hr>\n')

	# all results for operation for both sets for tab delimited
	#resultsForOp = [[(FS, BSdata)],[(FS, BSdata)]] # [0] = base, [1] = set1
	resultsForOp = [[],[]]
	for operation in set1.operations:
		(x1,y1)=base.get_BS_list_for_any_FS(operation)
		(x2,y2)=set1.get_BS_list_for_any_FS(operation)
		resultsForOp[0].append((x1, y1))
		resultsForOp[1].append((x2, y2))

	tab_delimited_summary(resultsForOp, set1.operations)
	regLines = xy_fsbs_avg(resultsForOp, set1.operations)
	opNr = 0

	# write tables, tab delimited output and create plots for every operation
	for operation in set1.operations:
		# block size oriented tables and plots
		data = []
		data.append(['File size [kB]','Block size [kB]'])
		data.append(['baseline','black'])
		(x1,y1)=base.get_FS_list_for_any_BS(operation)
		data[0].append(x1)
		data[1].append(y1)
		data.append(['set1','red'])
		(x2,y2)=set1.get_FS_list_for_any_BS(operation)
		assert(x1==x2)
		data[2].append(y2)

		htmldoc.write('<h3 id="' + operation + '">' + operation_name(operation) + '</h3>\n')
		write_operation(htmldoc,operation,data,operation+'_FS')
		tab_delimited(data, operation, 'BS')

		# file size oriented tables and plots
		data = []
		data.append(['Block size [kB]','File size [kB]'])
		data.append(['baseline','black'])
		(x1,y1)=base.get_BS_list_for_any_FS(operation)
		data[0].append(x1)
		data[1].append(y1)
		data.append(['set1','red'])
		(x2,y2)=set1.get_BS_list_for_any_FS(operation)
		assert(x1==x2)
		data[2].append(y2)

		write_operation(htmldoc,operation,data,operation+'_BS')
		tab_delimited(data, operation, 'FS')

		# visual comparision of both sets plot and table
		htmldoc.write('<img src=\"'+operation+'_compare.png\" alt=\"'+operation+'\_compare" class="plot"/>\n')
		(slope, std_err, ci_min, ci_max) = regLines[opNr]

		htmldoc.write('<div class=\"rawdata abovetable\">See <a href=\"../'+tabdDir+'/comparison_of_averages.tsv\">comparison_of_averages.tsv</a>.</div>\n')
		htmldoc.write('<table><tr><th colspan="2"> Regression line </th></tr>\n')
		htmldoc.write('<tr class=\"topline\"><td> slope </td><td>' + str(round(slope,5)) + '</td></tr>\n')
		htmldoc.write('<tr class=\"topline\"><td> std. error </td><td>' + str(round(std_err,5)) + '</td></tr>\n')
		htmldoc.write('<tr class=\"topline bottomline\"><td> ci. max 90% </td><td>' + str(round(ci_min,5)) + '</td></tr>\n')
		htmldoc.write('<tr><td> ci. min. 90% </td><td>' + str(round(ci_max,5)) + '</td></tr></table>\n')
		opNr += 1
		htmldoc.write('<a href="#top">Back on top</a>\n')
		htmldoc.write('<hr>\n')

	# all results for operation for both sets for html
	resultsForOp = [{},{}] # [0] = base, [1] = set1; dict key is op name
	for operation in set1.operations:
		y1 = base.get_all_for_operation(operation)
		resultsForOp[0][operation] = y1
		y2 = set1.get_all_for_operation(operation)
		resultsForOp[1][operation] = y2

	# results for all blocksizes and filesizes for one set, needed for summary at the end
	allSetData = [] # [0] = base, [1] = set1
	allSetData.append(base.get_all_data_list())
	allSetData.append(set1.get_all_data_list())

	resultsForOp[0]['ALL'] = allSetData[0]
	resultsForOp[1]['ALL'] = allSetData[1]
	write_overFSBS_summary(resultsForOp, ['ALL'] + set1.operations, regLines)

	htmldoc.write('<a href="#top">Back on top</a>\n')
	write_footer(htmldoc)
	htmldoc.close()
	print 'Finished.\nTo view results open in your web browser:'
	print 'file://' + os.getcwd() + '/Compare-html/index.html'


#!/usr/bin/python

import os
import sys
import re

import operation_results

# class to parse iozone results from input data files
class ParseIozone:
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
		res = operation_results.OperationResults(Type='fs')
		colnames = []
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
			colnames.append(FS)

		res.set_colnames(colnames)

		for BS in sorted(all_BS.keys()):
			res.data[BS] = []
			for file_number in range (len(self.files)):
				row = []
				for FS in sorted(all_FS.keys()):
					#We are creating a row of table
					#Columns - different file sizes (FS)
					#We need to check if Y_for_FS1 exists
					if self.columns.has_key((FS,BS,operation)):
						assert(len( self.columns[(FS,BS,operation)]  ) == len(self.files))
						row.append(self.columns[FS,BS,operation][file_number])
					else:
						row.append(0)
				res.add_row(BS, row)
		return (res)

	# return part of write_operation format data for operation , BS oriented
	def get_BS_list_for_any_FS(self,operation):
		all_BS = {}
		all_FS = {}
		res = operation_results.OperationResults(Type='bs')
		colnames = []
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
			colnames.append(BS)

		res.set_colnames(colnames)

		for FS in sorted(all_FS.keys()):
			res.data[FS] = []
			for file_number in range (len(self.files)):
				row = []
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
				#res.data[FS].append(row)
				res.add_row(FS, row)
		return (res)

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


if __name__ == '__main__':
	print 'Try running iozone_results_comparator.py'

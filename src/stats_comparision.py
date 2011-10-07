#!/usr/bin/python

from scipy import stats

class StatsComparision:
	def __init__(self):
		# dict key = operation name
		# val = operation_results object instance
		self.base = {}
		self.set1 = {}
		self.ttest_pvals = {}
		self.ttest_res = {}
		self.differences = {}
		self.common_ops = []
		self.op_common_cols = {} # op -> [col list]
		self.summary_base= [] # row(e.g. devs [op1 val, op2 val, ...], meds [], ... 
		self.summary_set1= []

		self.summary_diffs = []
		self.summary_pvals = []
		self.summary_res = []

		self.order=["iwrite", "rewrite", "iread", "reread", "randrd", "randwr", "bkwdrd", "recrewr", 
		"striderd", "fwrite", "frewrite", "fread", "freread"]

	def add_operation_results(self, setName, operation, results):
		if (setName == 'baseline'):
			self.base[operation] = results
		elif (setName == 'set1'): 
			self.set1[operation] = results
		else:
			raise Exception('Invalid set name')
	
	def compare(self):
		self.get_common()

		for op in self.common_ops:
			self.base[op].compute_all_stats()
			self.set1[op].compute_all_stats()

		# summary data is stored in fs only, no need for counting this redundantly in bs
		if (self.base[self.base.keys()[0]].datatype == 'fs'):
			self.summary()

		self.ttest_diff()

	def ttest_diff(self):
		for op in self.common_ops:
			self.differences[op] = []
			self.ttest_pvals[op] = []
			self.ttest_res[op] = []
			# TODO common cols jeste nefunguje na 100%, neuvazuje se posunuti od zacatku
			for colnr in range(len(self.op_common_cols[op])):
				diff = (self.base[op].medians[colnr] / self.set1[op].medians[colnr] -1)*100
				self.differences[op].append(diff)

				(tstat, pval) = stats.ttest_ind(self.base[op].lindata[colnr], self.set1[op].lindata[colnr])
				self.ttest_pvals[op].append(pval)

				# 90% probability
				if (pval > 0.1):
					self.ttest_res[op].append('SAME')
				else:
					self.ttest_res[op].append('DIFF')

		# summary data is stored in fs only, no need for counting this redundantly in bs
		if (self.base[self.base.keys()[0]].datatype == 'fs'):
			for i in range(len(self.order)):
				op = self.order[i]
				if op not in self.common_ops:
					break
				# summary_base[5] - medians
				diff = (self.summary_set1[5][i] / self.summary_base[5][i] -1)*100
				self.summary_diffs.append(diff)

				(tstat, pval) = stats.ttest_ind(self.base[op].alldata, self.set1[op].alldata)
				self.summary_pvals.append(pval)

				# 90% probability
				if (pval > 0.1):
					self.summary_res.append('SAME')
				else:
					self.summary_res.append('DIFF')

				
	def get_common(self):
		# get common operations
		for op in sorted(self.base):
			if op in self.set1:
				self.common_ops.append(op)

		# get common cols
		self.op_common_cols[op] = []
		for op in self.common_ops:
			self.op_common_cols[op] = []
			for colname in self.base[op].colnames:
				if colname in self.set1[op].colnames:
					self.op_common_cols[op].append(colname)
	
	def summary(self):
		for (source, dest) in ((self.base, self.summary_base), (self.set1, self.summary_set1)):
			for op in self.common_ops:
				dest.append([])

			for op in self.order:
				if op not in self.common_ops:
					break

				vals = (source[op].mean, source[op].dev, source[op].ci_min, source[op].ci_max,
					source[op].gmean, source[op].median, source[op].first_qrt,
					source[op].third_qrt, source[op].minimum, source[op].maximum)
				for i in range(len(vals)):
					dest[i].append(vals[i])


if __name__ == '__main__':
	print 'Try running iozone_results_comparator.py'

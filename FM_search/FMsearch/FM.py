#!/usr/bin/env python3
import sys, string, re, os, fileinput

# class MoveToFront(object):

# 	# def __init__(self)
# 	def encode(self, word):
# 		alph = ['A','C','G','T']
# 		output = []
# 		for let in word:
# 			index = alph.index(let)
# 			output+=[index]
# 			alph.pop(index)
# 			alph = [let]+alph
# 		return output

# 	def decode(self, word):
# 		alph = ['A','C','G','T']
# 		output = []
# 		for let in word:
# 			letter = str(alph[let])
# 			output += letter
# 			alph.pop(let)
# 			alph = [letter] + alph
# 		return output

# structure used to hold all permutations of an input
class CircularSuffixArray(object):

	def CircularSuffixArray(self, word):
		#unsorted suffixes
		suffixes = []
		trans = word
		#original positions of indexes
		SA=[]
		for i in range(0, len(word)):
			suffixes += [(trans, i)]
			trans = trans[1:]+trans[0]
		#sorted suffixes
		trans = sorted(suffixes, key = lambda word: word[0])
		for i in trans:
			SA += [i[1]]
		return (suffixes, trans, SA)

#return the original index position of a sorted suffix
	def index(self, pos, suffs):
		if pos < len(suffs):
			return suffs[pos][1]
		else:
			return -1


class BurrowsWheeler(object):

	#perform burrows wheeler transform
	def transform(self, word):
		CSA = CircularSuffixArray()
		orig, trans, SA = CSA.CircularSuffixArray(word)
		index = -1
		output = []
		#create output of last column and index of originally first element
		for i in range(0,len(trans)):
			if trans[i][1] == 0:
				index = i
			output += trans[i][0][-1]
		return (index, ''.join(output), SA)

	#recreate the first column of the sorted suffix array, along with character counts
	def fCol(self, totals):
		first = {}
		total_chars = 0
		for c,count in sorted(totals.items()):
			first[c] = (total_chars, total_chars + count)
			total_chars += count
		return first

	#create the ranks table used in BW inverse transform
	def ranks(self, word):
		totals = {}
		ranks = []
		for char in word:
			if char not in totals:
				totals[char] = 0
			ranks += [totals[char]]
			totals[char] += 1
		return totals, ranks

	#retrieve original string
	def inverseTransform(self, pos, word):
		totals,ranks = self.ranks(word)
		first_col = self.fCol(totals)
		output = ''
		index = pos
		for i in range(0, len(word)):
			c = word[index]
			output = c + output
			index = first_col[c][0] + ranks[index]
		return output

#Future optimizations: Checkpointing in SA, efficient occ implementation
class FMIndex(object):

	def __init__(self, word, c=None, SA=None, occ=None,totals=None):
		print('here')
		bw = BurrowsWheeler()
		#create new Index
		if c == None or SA == None or occ == None or totals==None:
			self.pos, self.trans, self.SA = bw.transform(word)
			self.totals, self.ranks = bw.ranks(self.trans)
			self.counts = bw.fCol(self.totals)
			self.occ = self.build_occ(self.trans)
			self.c = self.build_count()
		#create index from saved structures
		else:
			self.c=c
			self.occ=occ
			self.SA=SA
			self.totals=totals

	# build table of character positions in sorted first column of suffixes
	def build_count(self):
		c = {}
		for i in sorted("".join(set(self.trans))):
			c[i] = self.counts[i][0]
		return c

	# build table of character occurences up to every index 
	#TO DO: constant time implementation
	def build_occ(self, trans):
		occ = {}
		for i in "".join(set(self.trans)):
			if i == trans[0]:
				occ[i] = [1]
			else:
				occ[i] = [0]

		for i in self.trans[1:]:
			for c in occ.keys():
				if c == i:
					occ[c] += [occ[c][len(occ[c])-1] +1]
				else:
					occ[c] += [occ[c][len(occ[c])-1]]
		return occ

	def occ_val(self, query, max_ind):
		return self.occ[query][max_ind-1]

	#search for a substring in the FM Index
	#algorithm from original FM paper
	def search(self, query):
		i = len(query)
		c = query[i-1]
		if c not in self.c.keys():
			return ('No', [-1])
		sp = self.c[c]+1
		ep = self.c[c] + self.totals[c]
		while sp <= ep and i >=2:
			c = query[i-2]
			if c not in self.c.keys():
				return ('None present', [-1])
			sp = self.c[c] + self.occ_val(c,sp-1) + 1
			ep = self.c[c] + self.occ_val(c,ep)
			i -= 1
		if (ep < sp):
			return ('No', [-1])
		else:
			locations = []
			for i in range(sp-1, ep):
				locations += [self.SA[i]]
			return(str(ep-sp+1), locations)

#testing
def main():
	testFM = FMIndex(word='mississippi$')
	print(testFM.occ)
	print(testFM.c)
	print(testFM.totals)
	print(testFM.SA)
	# print(testFM.pos)
	# print(sorted('mississippi$'))
	# print(testFM.trans)
	# print(testFM.totals)
	# print(testFM.ranks)
	# print(testFM.counts)
	# print(testFM.occ)
	# print(testFM.c)
	occ,loc = testFM.search('issi')
	print(occ + ' occurence(s) beginning at indexes: ')
	for i in loc[::-1]:
		print(str(i))

if __name__ == "__main__":
	main()

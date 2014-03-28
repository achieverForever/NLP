 #!/ usr/ bin/ python
 # -*- coding: utf-8 -*-  

import re

K_DICT_FILE = 'word_frequency.txt'

class Word:
	def __init__(self, beg, end):
		self.beg = beg
		self.end = end
		self.p = 0.0
		self.leftNeighbour = None


class MaxProbabilitySegment:
	def __init__(self):
		self.mydict = self.buildDict()

	def buildDict(self):
		with open(K_DICT_FILE, encoding='gbk') as f:
			mydict = {}
			for line in f:
				tokens = line.split(',')
				mydict[tokens[0]] = float(tokens[2].rstrip('%\n')) * 0.01
			return mydict

	# @param inputStr, input string
	# @return segmented string using Maximum Probability algorithm
	def MaxProbability(self, inputStr):
		if inputStr == '':
			return ''
		inputStr = self.removeWhiteSpace(inputStr)
		candidates = []
		maxEnding = None	# Keep track of the ending word with maximum cumulative probability
		maxProb = 0.0
		length = len(inputStr)
		for i in range(0, length):	# Start position
			for j in range(1, length-i+1):	# Substring length
				subStr = inputStr[i:i+j]
				if subStr in self.mydict:
					# Make one candidate word
					w = Word(i, i+j-1)
					w.p = self.mydict[subStr]
					w.leftNeighbour = self.findBestLeftNeighbour(w, candidates)
					if w.leftNeighbour is not None:
						w.p *= w.leftNeighbour.p
					candidates.append(w)
					# Find ending word with maximum cumulative probability
					if (i+j) == length and w.p > maxProb:
						maxEnding = w
						maxProb = w.p
		if maxEnding is None:
			maxEnding = Word(length, length)
		return self.constructResult(maxEnding, inputStr, candidates)

	# @param word, a candidate word inputStr[beg..end]
	# @param candidates, list of candidate words found so far
	# @return the left neighbour of word with largest probability or None if word has no left neighbour
	def findBestLeftNeighbour(self, word, candidates):
		if word.beg == 0:
			return None
		maxLeftNeighbour = None
		maxProb = 0.0
		for w in candidates:
			if w.end == (word.beg-1) and w.p > maxProb:
				maxProb = w.p
				maxLeftNeighbour = w
		return maxLeftNeighbour

	# @param maxEnding, ending word with maximum cumulative probability
	# @param inputStr, input string
	# @param candidates, list of candidate words
	# @return segmented string 
	def constructResultRecursive(self, maxEnding, inputStr, candidates):
		word = inputStr[maxEnding.beg:maxEnding.end+1]
		if maxEnding.leftNeighbour is None and maxEnding.beg >= 0:
			# The path is broken when we reach a non-starting word without left neighbour,
			# we need to restart the backtracking from a new max-ending word
			newMaxEnding = None
			begin = maxEnding.beg
			skipped = ''
			while newMaxEnding is None and begin > 0:
				begin = begin - 1
				skipped = inputStr[begin:begin+1] + skipped
				dummy = Word(begin, 0)
				newMaxEnding = self.findBestLeftNeighbour(dummy, candidates)
			if newMaxEnding is None:
				# Have we skipped all substring to the left of me?
				return (skipped + '/  ' + word) if skipped != '' else word
			else:
				# Found one new maxEndingWord to continue our backtracking
				return self.constructResultRecursive(newMaxEnding, inputStr, candidates) + '/  ' + skipped + '/  ' + word
		else:
			return self.constructResultRecursive(maxEnding.leftNeighbour, inputStr, candidates) + '/  ' + word

	def constructResult(self, maxEnding, inputStr, candidates):
		res = ''
		while True:
			word = inputStr[maxEnding.beg:maxEnding.end+1]
			if maxEnding.leftNeighbour is None and maxEnding.beg >= 0:
				newMaxEnding = None
				begin = maxEnding.beg
				skipped = ''
				while newMaxEnding is None and begin > 0:
					begin = begin - 1
					skipped = inputStr[begin:begin+1] + skipped
					dummy = Word(begin, 0)
					newMaxEnding = self.findBestLeftNeighbour(dummy, candidates)
				if newMaxEnding is None:
					# Have we skipped all substring to the left of me?
					res = (skipped + '/  ' + word + '/  ' + res) if skipped != '' else word + '/  ' + res
					break
				else:
					# Found one new maxEndingWord to continue our backtracking
					maxEnding = newMaxEnding
					res =  skipped + '/  ' + word + '/  ' + res
			else:
				maxEnding = maxEnding.leftNeighbour
				res = word + '/  ' + res
		return res


	def removeWhiteSpace(self, inputStr):
		return re.sub(r'\s+', '', inputStr)

def main():
	# inputStr = '原子结合成分子时'
	# inputStr = '做完作业才能看电视'
	inputStr = '结s合成'
	inputStr = '云南幼儿园7dsf名儿童毒鼠强中毒'
	mp = MaxProbabilitySegment()
	print(mp.MaxProbability(inputStr))


if __name__ == '__main__':
	main()







	
import re
import operator
import io
import sys

RULES_FILE = 'data/rules_pcfg.txt'

class DictList(dict):
	'''
	Make a custom dict which can store duplicate key-values in list
	'''
	def __setitem__(self, key, value):
		try:
			self[key]
		except KeyError:
			super(DictList, self).__setitem__(key, [])
		self[key].append(value)


class SplitPoint:
	'''
	Define a SplitPoint class to store the spliting information during the parsing process
	eg. When calculating P[i][j][X] for NT X spanning over subsequence word_i...word_j, we 
	record the split position s and the production (X -> Y Z) we chose.
	'''
	def __init__(self, s=-1, Y=-1, Z=-1):
		self.s = s
		self.Y = Y
		self.Z = Z

	def __str__(self):
		return '(Y:{0}, Z:{1}, {2})'.format(self.Y, self.Z, self.s)


class CYKParser:
	'''
	Implement CYK algorithm for parsing PCFG
	'''
	def __init__(self):
		self.rules = DictList()
		self.nonterminals = []
		self.words = []
		self.P = None
		self.BP = None
		self.symb2id = {}
		self.id2symb = {}
		self.loadRules(RULES_FILE)

	def loadRules(self, rulesfile):
		currIdx = 1
		with open(rulesfile) as fd:
			# First pass, build symbol->id and id->symbol mapping for later use
			for line in fd:
				if line.strip() == '' or line.startswith('#'):
					continue
				else:
					symbols = line.split()
					head = symbols[0]
					if head not in self.symb2id:
						self.symb2id[head] = currIdx
						self.id2symb[currIdx] = head
						currIdx += 1
		with open(rulesfile) as fd:
			# Second pass, parse each rule and store them into a dict	
			for line in fd:
				if line.strip() == '':
					continue
				head, body = re.split('->', line.strip())
				head = head.strip()
				body = body.split()
				body[-1] = float(body[-1])
				self.rules[head] = body
			self.nonterminals = ['#'] + sorted(self.symb2id, key=self.symb2id.get)	# For one-based array

	# @param word, a word string
	# @param symbol, a non-terminal symbol string
	# @return probability of 'symbol' generating 'word', otherwise return -1.0
	def checkWordInRules(self, word, symbol):
		ruleList = self.rules[symbol]
		for r in ruleList:
			if r[0] == word:
				return r[1]
		return -1.0

	def printParseTree(self, beg, end, symbol):
		sys.stdout = mystdout = io.StringIO()
		self.printParseTreeAux(beg, end, self.symb2id[symbol])
		parseString = mystdout.getvalue()
		sys.stdout = sys.__stdout__
		mystdout.close()

		return parseString

	# @param beg, beginning pos of the subsequence
	# @param end, ending pos of the subsequence (inclusive)
	# @param symbol_id, the NT symbol id
	# @return a parse string using recursion
	def printParseTreeAux(self, beg, end, symbol_id):
		''' 
		Construct a parse string using the backpoint information recursively.
		'''
		backPt = self.BP[beg][end][symbol_id]
		symb = self.id2symb[symbol_id]
		if backPt.s == -1:
			print(symb + '(' + self.words[beg-1] + ')', end='')
		else:
			print(symb, end='')
			print('(', end='')
			self.printParseTreeAux(beg, backPt.s, backPt.Y)
			self.printParseTreeAux(backPt.s+1, end, backPt.Z)
			print(')', end='')

	# @param sentence, a string to be parsed
	# @return a parse string and its probability
	def parse(self, sentence):
		'''
		Implement CYK algorithm for parsing PCFG.
		'''
		words = sentence.split()
		self.words = words
		N = len(words)			# Number of words
		M = len(self.symb2id)	# Number of non-terminal symbols

		# N x N x M, P[i][j][k] stores the maximum probability of non-terminal
		# symbol Xk spanning over word_i...word_j (inclusive) 
		self.P = [ [[ 0.0 for i in range(M+1) ] for j in range(N+1)] for k in range(N+1)]

		# N x N x M, BP[i][j][k] stores the split point s of the partition which has the 
		# maximum probability of (X -> Y Z) spanning over word_i...word_j (inclusive) 
		self.BP = [ [[ SplitPoint() for i in range(M+1) ] for j in range(N+1)] for k in range(N+1)]
	
		# Initialization
		for i in range(1, N+1):			# For each word
			for j in range(1, M+1):		# For each non-terminal symbol
				symb = self.id2symb[j]
				prob = self.checkWordInRules(words[i-1], symb)
				if prob < 0.0:
					self.P[i][i][j] = 0.0
				else:
					self.P[i][i][j] = prob

		for _len in range(1, N):	# Subsequence length 
			for i in range(1, N-_len+1):	# Subsequence starting pos
				j = i + _len 				# Subsequence ending pos
				for k in range(1, M+1):			# For each NT symbol X
					X = self.nonterminals[k]
					maxProb = 0.0
					maxSplitPos = SplitPoint()
					for production in self.rules[X]:	# For each production of X (X -> Y Z)
						if len(production) < 3:
							continue
						Y = production[0]
						Z = production[1]
						Y_id = self.symb2id[Y]
						Z_id = self.symb2id[Z]
						prob = production[2]
						for s in range(i, j):	# For each possible split point s
							p = prob * self.P[i][s][Y_id] * self.P[s+1][j][Z_id]
							if maxProb < p:
								maxProb = p
								maxSplitPos = SplitPoint(s, Y_id, Z_id)

					self.P[i][j][k] = maxProb
					self.BP[i][j][k] = maxSplitPos
		
		S_id = self.symb2id['S']
		parseString = self.printParseTree(1, N, 'S')
		prob = self.P[1][N][S_id]

		return (parseString, prob)

def main():
	sentence = 'fish people fish tanks'
	parser = CYKParser()
	parseString, prob = parser.parse(sentence)
	print(parseString)
	print(prob)

if __name__ == '__main__':
	main()
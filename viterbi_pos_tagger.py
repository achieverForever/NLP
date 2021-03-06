#!/usr/bin/python
# -*- coding: utf-8 -*-
from max_prob_segment import MaxProbabilitySegment

WORDS_FILE = 'data/words.txt'
TAGS_FILE = 'data/tags.txt'
TRANS_MATRIX_FILE = 'data/trans_matrix.txt'
EMIT_MATRIX_FILE = 'data/emit_matrix.txt'
INIT_PROB_FILE = 'data/init_prob.txt'


class HMMModel:
	def __init__(self):
		self.states = None
		self.trans_p = None
		self.emit_p = None
		self.init_p = None
		self.word2id = None
		self.loadModelParameters()

	def loadModelParameters(self):
		''' Load HMM model parameters from files '''
		self.states = []
		self.word2id = {}
		with open(WORDS_FILE, encoding='utf-8') as fd:
			for i, w in enumerate(fd):
				self.word2id[w.strip()] = i
		with open(TAGS_FILE, encoding='utf-8') as fd2:
			for i, t in enumerate(fd2):
				self.states.append(t.strip())
		numTags = len(self.states)

		self.trans_p = [[] for i in range(numTags)]
		self.emit_p = [[] for j in range(numTags)]
		self.init_p = []

		with open(TRANS_MATRIX_FILE) as fd:
			for i, line in enumerate(fd):
				self.trans_p[i] = list(map(float, line.split()))
		with open(EMIT_MATRIX_FILE) as fd:
			for i, line in enumerate(fd):
				self.emit_p[i] = list(map(float, line.split()))
		with open(INIT_PROB_FILE) as fd:
			line = fd.read()
			self.init_p = list(map(float, line.split()))


class HMM_Viterbi_POS_TAGGER:
	def __init__(self):
		self.hmm = HMMModel()

	# @param observations, a lisf of segmented word
	# @return a pos-tagged string using HMM-Viterbi algorithm
	def Viterbi(self, observations):
		''' Calculate the hidden state sequence with maxinum probability using HMM-Viterbi algorithm '''
		K = len(self.hmm.states)
		# obs = [self.hmm.word2id[w] for w in observations]	# Convert word to id
		obs = []
		for w in observations:
			try:
				obs.append(self.hmm.word2id[w])
			except:		
				obs.append(-1)
		T = len(obs)
	  
		# K x T
		# V[i][j] stores the probability of the most likely path so far S = {s1,s2,...,sj}, 
		# with sj = states[i] at time j
		V = [[0.0 for i in range(T)] for j in range(K)]

		# K x T
		# P[i][j] stores the previous state sj-1 of the most likely path so far 
		P = [[-1 for i in range(T)] for j in range(K)]
		
		# For each state at time 0, compute its probability
		for i in range(K):	
			emit_i_0 = 1e-20 if obs[0] == -1 else self.hmm.emit_p[i][obs[0]]
			V[i][0] = self.hmm.init_p[i] * emit_i_0
			P[i][0] = i

		for t in range(1, T):	# For each time step
			obs_t = obs[t]
			for j in range(K):	# For each state at time t
				maxp = -1.0
				prev = -1
				for k in range(K):	# For each previous state
					# Special handling of the new word not in dictionary
					emit_j_t = 1e-20 if obs_t == -1 else self.hmm.emit_p[j][obs[t]]
					if maxp < emit_j_t * self.hmm.trans_p[k][j] * V[k][t-1]:
						maxp = emit_j_t * self.hmm.trans_p[k][j] * V[k][t-1]
						prev = k
				V[j][t] = maxp
				P[j][t] = prev

		# Find the last hidden state with maximum probability
		maxp, state = max([(V[i][T-1], i) for i in range(K)])

		# Construct the tags sequence 
		prev = state
		tags = []
		for t in reversed(range(T)):
			tags = [self.hmm.states[prev]] + tags
			prev = P[prev][t]
		
		res = ''
		for i in range(T):
			res += observations[i] + '/' + tags[i] + '   '
		return res


if __name__ == '__main__':
	inputStr = '在这一年中，中国的改革开放和现代化ss建设继续向前迈进。'
	mp = MaxProbabilitySegment()
	segmented =  mp.MaxProbability(inputStr)
	print(segmented)
	obs = [w.strip('/') for w in segmented.split()]
	tagger = HMM_Viterbi_POS_TAGGER()
	print(tagger.Viterbi(obs))




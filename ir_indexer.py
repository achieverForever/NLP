import operator
import re
import string
import math


class Index:
	'''
	A class representing an Inverted-Index object
	'''
	def __init__(self, docId, wordPos):
		self.docId = docId
		self.wordPos = wordPos

	def __str__(self):
		return '({0},{1})'.format(self.docId, self.wordPos)


class Indexer:
	def __init__(self, docsFile, indexFile, dictFile, paramsFile):
		self.docsFile = docsFile
		self.indexFile = indexFile
		self.dictFile = dictFile
		self.paramsFile = paramsFile
		self.totalDocs = 0				# Total number of documents
		self.totalTermsPerDoc = []		# Total number of terms in each document
		self.dict = None 
		self.indices = None

		# Use this to build the indices
		self.buildDict()
		self.buildIndex()

		# Use this to prepare data for the searcher
		# self.loadDict()
		# self.loadIndexFromFile()
		# self.loadParamsFromFile()


	def buildDict(self):
		self.dict = {}
		newIndex = 0
		with open(self.docsFile) as fd:
			for i, line in enumerate(fd):
				line = line.lower()
				words = self.preprocess(line)	# Preprocess each doc 
				for word in words:
					if word not in self.dict:
						self.dict[word] = newIndex
						newIndex += 1
		with open(self.dictFile, 'w') as fd:
			for word, id in sorted(self.dict.items(), key=operator.itemgetter(1)):
				fd.write(word + '\n')

	def loadDict(self):
		self.dict = {}
		with open(self.dictFile) as fd:
			for id, word in enumerate(fd):
				self.dict[word.strip()] = id

	# @param doc, a document's string
	# @return a list of words with punctuations removed
	def preprocess(self, doc):
		regex = re.compile('[{0}]'.format(re.escape(string.punctuation)))
		doc = regex.sub('', doc)
		return doc.split()

	def buildIndex(self):
		forwardIndices = []

		with open(self.docsFile) as fd:
			for i, doc in enumerate(fd):
				doc = doc.lower()
				self.totalDocs += 1
				words = self.preprocess(doc)
				self.totalTermsPerDoc.append(len(words))
				for j, word in enumerate(words):
					forwardIndices.append( (word, Index(i, j)) )

			# Sort the forward indices such that index objects of the same term groups together
			forwardIndices.sort(key=lambda x: x[0])
			
			# Initialize the value of each term=>indices mapping to a empty list
			self.indices = {}
			for word in self.dict:
				self.indices[word] = []

			# Collect the indices
			for word, index in forwardIndices:
				self.indices[word].append(index)

			self.saveIndexToFile()
			self.saveParamsToFile()

	def saveIndexToFile(self):
		'''
		Serialized the indices to file
		'''
		with open(self.indexFile, 'w') as fd:
			for term, indexList in self.indices.items():
				fd.write(term)
				for index in indexList:
					fd.write(' ' + str(index))
				fd.write('\n')

	def loadIndexFromFile(self):
		'''
		Deserialize the indices from file
		'''
		with open(self.indexFile) as fd:
			self.indices = {}
			for word in self.dict:
				self.indices[word] = []

			for line in fd:
				term = ''
				indexList = []

				items = line.strip().split()
				term = items[0]

				if len(items) > 1:
					for item in items[1:]:
						it = item.strip('()')
						docId, wordPos = it.split(',')
						self.indices[term].append( Index(int(docId), int(wordPos)) )

	def saveParamsToFile(self):
		with open(self.paramsFile, 'w') as fd:
			fd.write(str(self.totalDocs) + '\n')
			fd.write(' '.join( [str(n) for n in self.totalTermsPerDoc] ))
	
	def loadParamsFromFile(self):
		with open(self.paramsFile) as fd:
			self.totalDocs = int(fd.readline())
			self.totalTermsPerDoc = [int(n) for n in fd.readline().split()]

	def getDocsFromIds(self, docIds):
		docs = {}
		docIds.sort()
		with open(self.docsFile) as fd:
			j = 0
			for i, doc in enumerate(fd):
				if i == docIds[j]:
					docs[docIds[j]] = doc
					j += 1
				if j == len(docIds):
					break
			return docs

	# @param term, the term to evaluate TF-IDF
	# @param docId, the document id
	# @return a float which is the TF-IDF value of the given term
	def computeTFIDF(self, term, docId):
		'''
		Compute the TFIDF given a term and the document it resides
		'''
		numTerms = 0	# Count of occurences of the given term in the this doc
		numDocs = 0		# Count of docs containing the given term

		seenDocs = set()
		for index in self.indices[term]:
			if index.docId == docId:
				numTerms += 1
			if index.docId not in seenDocs:
				seenDocs.add(index.docId)
				numDocs += 1
		tf = numTerms / self.totalTermsPerDoc[docId]
		df = self.totalDocs / numDocs

		tfidf = (1. + math.log10(tf)) * math.log10(df)

		return tfidf



def main():
	indexer = Indexer('data/docs.txt', 'data/index.txt', 'data/dict.txt', 'data/params.txt')

	# indexer.buildIndex()
	# tfidf = indexer.computeTFIDF('what', 0)
	# print(tfidf)



if __name__ == '__main__':
	main()





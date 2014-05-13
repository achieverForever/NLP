from ir_indexer import Indexer

SEARCH_MODE_KEYWORD = 0
SEARCH_MODE_PHRASE = 1

class Query:
	'''
	Query class representing a query, two search modes are supported currently, 
	keyword and phrase
	'''
	def __init__(self, queryString, searchMode):
		self.queryString = queryString
		self.searchMode = searchMode


class Hit:
	'''
	A class representing a search hit, used to display the search result
	'''
	def __init__(self, docId, score):
		self.docId = docId
		self.score = score

	def __str__(self):
		return 'doc: {0}, score: {1:.6f}'.format(self.docId, self.score)

class IndexSearcher:

	def __init__(self, indexer):
		self.indexer = indexer

	# @param query, a Query object representing a query
	# @param topN, number of hits returned with top-n scores
	# @return a list of Hit objects representing search results or None if no match
	def search(self, query, topN=10):
		'''
		Use TF-IDF to evaluate the score of each document in the corpus given a query and
		return topN documents with the highest score
		'''
		hits = []
		indices = self.indexer.indices
		dictionary = self.indexer.dict

		if query.searchMode == SEARCH_MODE_KEYWORD:
			q = query.queryString.lower().strip()
			# Return None if query string is not in our dictionary
			if q not in dictionary or q == '':
				return
			else:
				indexList = indices[q]
				# Query string does not appear in our corpus
				if not indexList:
					return
				else:
					# Used to ensure we just compute TFIDF for once for those terms which 
					# occurs multiple times in a doc
					seenDocs = set()	
					for index in indexList:
						if index.docId not in seenDocs:
							seenDocs.add(index.docId)
							score = self.indexer.computeTFIDF(q, index.docId)
							hits.append( Hit(index.docId, score) )

					# Sort the hits according to score 
					hits.sort(key=lambda x: x.score, reverse=True)
					# Return top-n hits or less if total number of hits is less than topN
					topN = min(len(hits), topN)
					return hits[:topN]

		elif query.searchMode == SEARCH_MODE_PHRASE:
			docSet = set()	# Docs left in this set are those containing all query terms of the query string
			queries = query.queryString.lower().strip().split()
			flag = False

			if not queries:
				return

			for q in queries:
				# Part of the query string is not in corpus, return None
				if q not in dictionary:
					return
				
				indexList = indices[q]
				# Part of the query string is not in corpus, return None
				if not indexList:
					return
				else:
					newDocSet = set([index.docId for index in indexList])
					if not flag:
						flag = True
						docSet = newDocSet
					else:
						docSet = docSet.intersection(newDocSet)

			for doc in docSet:

				# Check if this document contains the whole continguous query string
				if not self.containsWholeQuery(queries, doc):
					continue
				else:
					score = 0.0
					# Compute the score of this document
					for q in queries:
						score += self.indexer.computeTFIDF(q, doc)
					hits.append(Hit(doc, score))

			# It's possible that there is not any document containing the whole continguous query string
			if not hits:
				return

			hits.sort(key=lambda x: x.score, reverse=True)
			topN = min(len(hits), topN)

			return hits[:topN]

		else:
			raise ValueError('Invalid query, not supported search mode')

	def containsWholeQuery(self, queries, docId):
		'''
		Check if the target document contains a whole continguous query terms 
		'''
		if len(queries) == 1:
			# Since the doc must contain every query word of query string, so this doc must
			# contain the whole continguous query string if it's length is 1
			return True
		else:
			# Begin recursively checking if the next term of the query follows
			# the current term in the same document
			q = queries[0]
			for index in [idx for idx in self.indexer.indices[q] if idx.docId == docId]:
				pos = index.wordPos
				if self.hasTermAtPosition(queries, 1, docId, pos+1):
					return True
			return False

	# @param queries, a list of query terms
	# @param i, used to get the current query term
	# @param docId, the target document of interest
	# @param pos, position of the current query term in the target document
	# @return True if `queries[i]` is at position `pos` in document `docId` recursively or False 
	def hasTermAtPosition(self, queries, i, docId, pos):
		'''
		Recursively check if the query terms exists in order in the target document
		'''
		if i == len(queries):
			return True
		q = queries[i]
		for index in self.indexer.indices[q]:
			if index.docId == docId and index.wordPos == pos:
				return self.hasTermAtPosition(queries, i+1, docId, pos+1)
		return False		




def main():
	indexer = Indexer('data/docs.txt', 'data/index.txt', 'data/dict.txt', 'data/params.txt')
	searcher = IndexSearcher(indexer)

	q = Query('what', SEARCH_MODE_KEYWORD)
	hits = searcher.search(q, 10)
	if hits is not None:
		for hit in hits:
			print(hit)

	q = Query('I am', SEARCH_MODE_PHRASE)
	hits = searcher.search(q, 10)
	if hits is not None:
		for hit in hits:
			print(hit)

		docIds = [hit.docId for hit in hits]
		docs = searcher.indexer.getDocsFromIds(docIds)
		for id, doc in docs.items():
			print(doc)

if __name__ == '__main__':
	main()




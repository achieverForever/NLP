WORDS_FILE = 'data/words.txt'
TAGS_FILE = 'data/tags.txt'
TRANS_MATRIX_FILE = 'data/trans_matrix.txt'
EMIT_MATRIX_FILE = 'data/emit_matrix.txt'
TRAINING_TEXT_FILE = 'data/199801.txt'
INIT_PROB_FILE = 'data/init_prob.txt'


def collectWordsTags():
	with open(TRAINING_TEXT_FILE, encoding='gbk') as fd_in, open(WORDS_FILE, 'w', encoding='utf-8') as fd_out, open('tags.txt', 'w', encoding='utf-8') as fd_out2:
		seenWords = {}
		seenTags = {}
		for line in fd_in:
			pairs = line.split()
			for p in pairs[1:]:
				word = (p.split('/'))[0]
				tag = (p.split('/'))[1]
				if word not in seenWords:
					seenWords[word] = 1
					fd_out.write(word + '\n')
				if tag not in seenTags:
					seenTags[tag] = 1
					fd_out2.write(tag + '\n')

def computeHMMParameters():
	word2id = {}
	tag2id = {}
	with open(WORDS_FILE, encoding='utf-8') as fd:
		for i, w in enumerate(fd):
			word2id[w.strip()] = i
	with open(TAGS_FILE, encoding='utf-8') as fd2:
		for i, t in enumerate(fd2):
			tag2id[t.strip()] = i

	N = len(tag2id)
	V = len(word2id)
	# num_Tag2Tag[i][j] stores the number of occurences that tag i is followed by tag j
	num_Tag2Tag = [[0 for i in range(N)] for j in range(N)]
	# num_Tag2Word[i][j] stores the number of occurences that tag i emits word j
	num_Tag2Word = [[0 for i in range(V)] for j in range(N)]
	# num_StartTag[i] stores the number of occurences that tag i is at the beginning of a sentence
	num_StartTag = [0 for i in range(N)]

	with open(TRAINING_TEXT_FILE, encoding='gbk') as fd:
		totalSentences = 0
		for line in fd:
			totalSentences += 1
			pairs = line.split()
			length = len(pairs)
			for i in range(1, length-1):
				w1, t1 = pairs[i].split('/')
				w2, t2 = pairs[i+1].split('/')
				w1 = word2id[w1]
				t1 = tag2id[t1]
				w2 = word2id[w2]
				t2 = tag2id[t2]
				num_Tag2Tag[t1][t2] = num_Tag2Tag[t1][t2] + 1
				num_Tag2Word[t1][w1] = num_Tag2Word[t1][w1] + 1
				num_Tag2Word[t2][w2] = num_Tag2Word[t2][w2] + 1
				if i == 1:
					num_StartTag[t1] = num_StartTag[t1] + 1
	with open(TRANS_MATRIX_FILE, 'w', encoding='utf-8') as fd_trans, open(EMIT_MATRIX_FILE, 'w', encoding='utf-8') as fd_emit:
		for i in range(N):
			s1 = sum(num_Tag2Tag[i])
			trans_p = [str(ct/s1) for ct in num_Tag2Tag[i]]
			fd_trans.write(' '.join(trans_p) + '\n')
			s2 = sum(num_Tag2Word[i])
			emit_p = [str(ct/s2) for ct in num_Tag2Word[i]]
			fd_emit.write(' '.join(emit_p) + '\n')
	with open(INIT_PROB_FILE, 'w', encoding='utf-8') as fd_init:
		init_p = [str(ct/totalSentences) for ct in num_StartTag]
		fd_init.write(' '.join(init_p))


if __name__ == '__main__':
	# collectWordsTags()
	computeHMMParameters()

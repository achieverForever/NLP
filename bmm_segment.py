 #!/ usr/ bin/ python
 # -*- coding: utf-8 -*-  
import re
from tkinter import simpledialog
from tkinter import *

K_DICT_FILE = 'data/chinese_dict.txt'

class BMMSegment:
	def __init__(self, maxLen):
		self.maxLen = maxLen
		self.myDict = self.buildDict()

	# @return a set of words as dictionary
	def buildDict(self):
		with open(K_DICT_FILE, encoding='gbk') as f:
			words = []
			for line in f:
				tokens = line.split(',')
				words.append(tokens[0])
			return set(words)

	# @param inputStr, a string to be segmented
	# @return a list of cutting flag
	def MM(self, inputStr):
		totalLen = len(inputStr)
		startPos = 0
		result = [False] * totalLen

		while startPos < totalLen:
			remainLen = totalLen - startPos
			currLen = self.maxLen if remainLen >= self.maxLen else remainLen
			subStr = inputStr[startPos:startPos+currLen]
			while subStr not in self.myDict and currLen > 0:
				currLen = currLen - 1
				subStr = inputStr[startPos:startPos+currLen]
			# Sub-string length decrease to zero, not found in dictionary
			if currLen == 0:
				step = self.maxLen if remainLen >= self.maxLen else remainLen
				oldPos = startPos
				startPos += step
				result[oldPos+step-1] = True
				tmp = inputStr[oldPos:startPos]
				print('[Error] Failed to segment "' + tmp + '", no match found in dictionary')
			else:
				# Match found in dictionary, mark a cutting flag
				result[startPos+len(subStr)-1] = True
				startPos += currLen
		return result
		
	# @param inputStr, a string to be segmented
	# @return a list of cutting flag
	def RMM(self, inputStr):
		totalLen = len(inputStr)
		endPos = totalLen - 1
		result = [False] * totalLen

		while endPos >= 0:
			remainLen = endPos + 1
			currLen = self.maxLen if remainLen >= self.maxLen else remainLen
			subStr = inputStr[endPos-currLen+1:endPos+1]
			while subStr not in self.myDict and currLen > 0:
				currLen = currLen - 1
				subStr = inputStr[endPos-currLen+1:endPos+1]
			# Sub-string length decrease to zero, not found in dictionary
			if currLen == 0:
				# raise Exception('[Error] Failed to segment : ' + inputStr[endPos:endPos+self.maxLen].encode('cp936'))
				step = self.maxLen if remainLen >= self.maxLen else remainLen
				oldPos = endPos
				endPos -= step
				result[oldPos] = True
				tmp = inputStr[oldPos-step+1:oldPos+1]
				print('[Error] Failed to segment "' + tmp + '", no match found in dictionary')
			else:
				# Match found in dictionary, mark a cutting flag
				result[endPos] = True
				endPos -= currLen
		return result

	# @param inputStr, a string to be segmented
	# @return a segmented string
	def BMM(self, inputStr, inTextBox):
		if inputStr == '':
			return ''

		inputStr = self.removeWhiteSpace(inputStr)

		totalLen = len(inputStr)
		cutFlags = [False] * totalLen

		forward = self.MM(inputStr)
		reverse = self.RMM(inputStr)
		p = 0

		while p < totalLen:
			# Find the unmatched position and put the matched cutting flags to cutFlags
			while forward[p] == reverse[p]:
				cutFlags[p] = forward[p]
				p += 1 	
				if p == totalLen:
					break

			# If there is unmatched substring, pass it to user to handle the ambiguity
			if p < totalLen:
				notMatchStartPos = p

				# Find the unmatched ending position
				while forward[p] != reverse[p]:
					p += 1
				notMatchEndPos = p
				prev = self.findPreviousCutPos(cutFlags, notMatchStartPos)

				# Prompt the user to handle the ambiguity for inputStr[prev+1..notMatchEndPos] 
				print('Please handle the ambiguity for "' + inputStr[prev+1:notMatchEndPos+1] + '" manually')
				self.highlightText(inputStr, prev+1, notMatchEndPos, inTextBox)
				self.resolveAmbiguity(inputStr, cutFlags, prev+1, notMatchEndPos)
				if notMatchEndPos < totalLen:
					cutFlags[notMatchEndPos] = True
				p += 1
		self.highlightText(inputStr, -1, -1, inTextBox)	# Restore the normal style
		return self.constructResult(inputStr, cutFlags)

	# @param cutFlags, list of cutting flag of the result string
	# @param pos, position we are currently at
	# @return previous cutting position if we found one, otherwise return -1
	def findPreviousCutPos(self, cutFlags, pos):
		while pos >= 0 and not cutFlags[pos]:
			pos -= 1
		return pos

	# @param inputStr, input string
	# @param cutFlags, list of cutting flag of the result string
	# @param beg, ambigious substring's begining position
	# @param end, ambigious substring's ending position
	# @return nothing
	def resolveAmbiguity(self, inputStr, cutFlags, beg, end):

		inStr = simpledialog.askstring('请人工消除歧义', '如: 幼儿/园地/节目 ', initialvalue=inputStr[beg:end+1])
		if inStr is None:
			return
		inStr = inStr.strip('/')

		# Convert manually cuttng string to cutting position array
		p = 0
		cuts = []
		for w in inStr:
			if w == '/':
				p = p - 1
				cuts.append(p)
			p = p + 1
		for c in cuts:
			cutFlags[beg+c] = True

	# @param inputStr, input string
	# @param cutFlags, list of cutting flag of the result string
	# @return segmented string contructed from cutFlags array
	def constructResult(self, inputStr, cutFlags):
		result = ''
		for i, isCut in enumerate(cutFlags):
			if isCut:
				result += inputStr[i] + '/  '
			else:
				result += inputStr[i]
		return result

	def removeWhiteSpace(self, inputStr):
		return re.sub(r'\s+', '', inputStr)

	def highlightText(self, inputStr, beg, end, inTextBox):
		if inTextBox is None:
			return
		inTextBox.delete('1.0', END)
		if beg == -1 and end == -1:
			inTextBox.insert(INSERT, inputStr)
		else:
			# Highlight the skeptical substring
			inTextBox.insert(INSERT, inputStr[:beg])
			inTextBox.insert(INSERT, inputStr[beg:end+1], 'highlight')
			inTextBox.insert(INSERT, inputStr[end+1:])


def main():
	# inputStr = "人民币为人民服务"
	inputStr = "在这一年中，中国的改革开放和现代化建设继续向前迈进。国民经济保持了“高增长、低通胀”的良好发展态势。农业生产再次获得好的收成，企业改革继续深化，人民生活进一步改善。对外经济技术合作与交流不断扩大。"
	bmm = BMMSegment(4)
	result = bmm.BMM(inputStr, None)
	print('BMM:')
	print(result)


if __name__ == '__main__':
	main()
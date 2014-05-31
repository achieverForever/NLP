import re

HTML_FILE = '凤凰网.html'

def fetchLinks(htmlFile):
	links = []

	# Note that we use the non-greedy qualifier `"(.*?)"` which will match as little text as possible,
	# eg. If we use `"(.*)"` (greedy qualifier), 
	# """<a href="http://news.ifeng.com/app/special-api/new-list/ifeng/ifeng_client_spread/" target="_blank">"""
	# The final match extends from the `"` to the `"` after `_blank`, which isn't what we want.
	re_link = re.compile('<a\s+.*href="(.*?)"')

	with open(htmlFile, encoding='utf-8') as fd:
		count = 0
		for line in fd:
			match = re_link.search(line)
			if match is not None:
				links.append(match.group(1))
				count += 1
		return links

def fetchTitles(htmlFile):
	titles = []
	re_header = re.compile('<h\d>.*?</h\d>', re.DOTALL)		# Match <h1..7></h1..7> tag
	re_title = re.compile('<a.*?>(.*?)</a>', re.DOTALL)		# Match <a></a> tag
	with open(htmlFile, encoding='utf-8') as fd:
		html = fd.read()
	count = 0
	for match in re_header.finditer(html):
		header = match.group(0)
		matches = re_title.finditer(header)
		for m in matches:
			titles.append(m.group(1).strip())
			count += 1
	return titles

if __name__ == '__main__':
	fetchLinks(HTML_FILE)
	fetchTitles(HTML_FILE)






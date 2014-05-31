#!/usr/bin/python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename

from ir_indexer import Indexer
from ir_index_searcher import *
from tkHyperlinkManager import HyperlinkManager

import time
import re

class App(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()

        indexer = Indexer('data/docs.txt', 'data/index.txt', 'data/dict.txt', 'data/params.txt')
        self.searcher = IndexSearcher(indexer)
        self.resultDocs = {}
        self.query = ''

    def initUI(self):
      
        self.parent.bind('<Return>', self.onSearch)
        self.parent.title("基于TF-IDF信息检索 -- Search for Shakespeare")
        self.pack(fill=BOTH, expand=1)

        self.label1 = Label(self, text="请输入搜索内容：(关键词或短语)")
        self.label1.pack()
        
        self.searchFor = Entry(self, width=30)
        self.searchFor.focus_set()
        self.searchFor.pack(expand=1)

        self.search = Button(self, text="Go", command=self.onSearch)
        self.search.pack()

        self.mode= IntVar()
        self.mode.set(1)
        self.keywordMode = Radiobutton(self, text="关键词模式", variable=self.mode, value=1)
        self.keywordMode.pack()

        self.phraseMode = Radiobutton(self, text="短语模式", variable=self.mode, value=2)
        self.phraseMode.pack()

        self.label2 = Label(self, text=' 结果：')
        self.label2.pack(anchor="w")


        self.bottomPanel = Frame(self)
        self.bottomPanel.pack(fill=BOTH, expand=1)

        self.outputText = Text(self.bottomPanel, width=40, background="white")
        self.outputText.grid(in_=self.bottomPanel, row=0, column=0, sticky="sw")

        self.docText = Text(self.bottomPanel, width=50, background="white")
        self.docText.grid(in_=self.bottomPanel ,row=0, column=1, sticky="es")
        self.docText.tag_config('highlight', background='yellow')

        self.hyperlinkManager = HyperlinkManager(self.outputText)

    def onSearch(self, event=None):
        query = self.searchFor.get().strip()
        self.outputText.delete('1.0', END)
        self.docText.delete('1.0', END)
        self.query = query.lower()
        isResultEmpty = True
        start = time.clock()

        if self.mode.get() == 1:
            q = Query(query, SEARCH_MODE_KEYWORD)

            hits = self.searcher.search(q, 10)
            elapsed = time.clock() - start

            if hits is not None:
                isResultEmpty = False
                for hit in hits:
                    linkText = 'doc {0}'.format(hit.docId)
                    self.outputText.insert(INSERT, linkText, 
                    self.hyperlinkManager.add(self.onLinkClicked, hit.docId))
                    self.outputText.insert(INSERT, '    score: {0:.6f}\n'.format(hit.score))
        else:
            q = Query(query, SEARCH_MODE_PHRASE)
            hits = self.searcher.search(q, 10)
            elapsed = time.clock() - start

            if hits is not None:
                isResultEmpty = False
                for hit in hits:
                    linkText = 'doc {0}'.format(hit.docId)
                    self.outputText.insert(INSERT, linkText, 
                    self.hyperlinkManager.add(self.onLinkClicked, hit.docId))
                    self.outputText.insert(INSERT, '    score: {0:.6f}\n'.format(hit.score))

        if isResultEmpty:
            self.outputText.insert(INSERT, '0 results returned')
            return

        self.label2['text'] = ' 结果：     耗时：{0:.1f} ms'.format(elapsed*1000)
        docIds = [hit.docId for hit in hits]
        self.resultDocs = self.searcher.indexer.getDocsFromIds(docIds)
        self.onLinkClicked(hits[0].docId)

    def onLinkClicked(self, docId):
        self.docText.delete('1.0', END)
        # self.docText.insert(INSERT, self.resultDocs[docId])

        doc = self.resultDocs[docId]
        p = re.compile(self.query, re.IGNORECASE)
        lastPos = 0
        while True:
            m = p.search(doc, lastPos)
            if m is None:
                break
            before = doc[lastPos:m.start()]
            lastPos = m.end()
            self.docText.insert(INSERT, before)

            self.docText.insert(INSERT, doc[m.start():m.end()], "highlight")

        if lastPos < len(doc):
            self.docText.insert(INSERT, doc[lastPos:])



def main():
  
    root = Tk()
    root.option_add("*Font", "微软雅黑 10")
    root.geometry("730x500+300+300")
    app = App(root)
    root.mainloop()  


if __name__ == '__main__':
    main()
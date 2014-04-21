#!/usr/bin/python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename

from bmm_segment import BMMSegment
from max_prob_segment import MaxProbabilitySegment
from viterbi_pos_tagger import HMM_Viterbi_POS_TAGGER
from top_down_parser import TopDownParser

import time

class App(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        
        self.bmm = BMMSegment(4)
        self.mp = MaxProbabilitySegment()
        self.tagger = HMM_Viterbi_POS_TAGGER()
        self.parser = TopDownParser()
  
    def initUI(self):
      
        self.parent.title("双向最大匹配分词")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, pad=7)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(5, weight=3)

        self.menubar = Menu(self.parent)
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="读入规则文件", command=self.onLoadRules)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="退出", command=self.parent.quit)
        self.menubar.add_cascade(label="文件", menu=self.fileMenu)

        self.parent.config(menu=self.menubar)

        
        self.label1 = Label(self, text="请输入语法规则或加载规则文件(如：S -> NP VP)")
        self.label1.grid(sticky=W, pady=4, padx=5)
        
        self.inputText = ScrolledText(self)
        self.inputText.grid(row=1, column=0, columnspan=2, rowspan=3, 
            padx=5, sticky=E+W+N)
        self.inputText.tag_config('highlight', background='yellow')

        self.label2 = Label(self, text='请输入文本：')
        self.label2.grid(row=4, column=0, sticky=W, pady=4, padx=5)

        self.outputText = ScrolledText(self)
        self.outputText.grid(row=5, column=0, columnspan=2, rowspan=3, 
            padx=5, sticky=E+S+W)

        self.rightFrame = Frame(self)
        self.rightFrame.grid(row=1, column=2, columnspan=7)

        self.bmmBtn = Button(self.rightFrame, text="双向最大匹配", command=self.onBMM)
        self.bmmBtn.pack(side="top", expand=True, pady=8)

        self.mpBtn = Button(self.rightFrame, text="最大概率分词", command=self.onMP)
        self.mpBtn.pack(side="top", expand=True, pady=8)

        self.hmmBtn = Button(self.rightFrame, text='HMM词性标注', command=self.onHMM)
        self.hmmBtn.pack(side="top", expand=True, pady=8)

        self.parseBtn = Button(self.rightFrame, text='语法分析', command=self.onParse)
        self.parseBtn.pack(side="top", expand=True, pady=8)

        # HINT: Place additional button here

        self.quitBtn = Button(self.rightFrame, text="退出", command=self.onQuit)
        self.quitBtn.pack(side="top", expand=True, pady=8)


    def onQuit(self):
        self.quit()

    def onBMM(self):
        self.outputText.delete('1.0', END)
        inStr = self.inputText.get('1.0', END).strip()

        start = time.clock()
        result = self.bmm.BMM(inStr, self.inputText)

        self.outputText.insert(INSERT, result)
        elapsed = time.clock() - start

        if result != '':
            self.label2['text'] = '分词结果    耗时: ' + '{0:.1f} ms'.format(elapsed*1000)

    def onMP(self):
        self.outputText.delete('1.0', END)
        inStr = self.inputText.get('1.0', END).strip()

        start = time.clock()
        result = self.mp.MaxProbability(inStr)

        self.outputText.insert(INSERT, result)
        elapsed = time.clock() - start

        if result != '':
            self.label2['text'] = '分词结果    耗时: ' + '{0:.1f} ms'.format(elapsed*1000)

    def onHMM(self):
        self.outputText.delete('1.0', END)
        inStr = self.inputText.get('1.0', END).strip()
        if inStr == '':
            return 

        start = time.clock()

        segmented = self.mp.MaxProbability(inStr)

        obs = [w.strip('/') for w in segmented.split()]
        result = self.tagger.Viterbi(obs)
        elapsed = time.clock() - start

        self.outputText.insert(INSERT, result)

        if result != '':
            self.label2['text'] = '词性标注结果     耗时: ' + '{0:.1f} ms'.format(elapsed*1000)

    def onParse(self):
        inStr = self.outputText.get('1.0', END).strip()
        if inStr == '':
            sentence = ['the', 'old', 'man', 'cried']
            self.outputText.insert(INSERT, ' '.join(sentence))
        else:
            sentence = inStr.strip().split()

        start = time.clock()
        succeed = self.parser.parse(sentence)
        elapsed = time.clock() - start

        if succeed:
            self.label2['text'] = '语法分析完成     结果：成功       耗时：' + '{0:.1f} ms'.format(elapsed*1000)
            newWindow = Toplevel(self)
            newWindow.title('自顶向下语法分析')
            self.textbox = Entry(newWindow)
            self.textbox.pack(fill=X, expand=1)
            self.tree = Treeview(newWindow)
            self.tree.heading('#0', text='语法树', anchor='w')
            self.tree.pack(fill=BOTH, expand=1)

            parseString = self.parser.printParseTree()
            self.textbox.insert(INSERT, parseString)

            self.buildParseTree('', 'S', self.parser.rules, self.parser.choices)            
        else:
            self.label2['text'] = '语法分析完成     结果：失败       耗时：' + '{0:.1f} ms'.format(elapsed*1000)

    def onLoadRules(self):
        fname = askopenfilename(initialdir='./data', initialfile='rules.txt')
        if fname != '':
            self.inputText.delete('1.0', END)
            with open(fname) as f:
                self.inputText.insert(INSERT, f.read())
            self.parser.loadRules(fname)

    def buildParseTree(self, parent, symbol, rules, choices):
        if choices[symbol] == -1:
            newNode = self.tree.insert(parent, 'end', text=symbol, open=True)
            self.tree.insert(newNode, 'end', text=' | '.join(rules[symbol][0]))
        else:
            c = choices[symbol]
            newParent = self.tree.insert(parent, 'end', text=symbol, open=True)
            for symbl in rules[symbol][c]:
                self.buildParseTree(newParent, symbl, rules, choices)

def main():
  
    root = Tk()
    root.option_add("*Font", "微软雅黑 10")
    root.geometry("700x500+300+300")
    app = App(root)
    root.mainloop()  


if __name__ == '__main__':
    main()
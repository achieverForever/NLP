#!/usr/bin/python
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from bmm_segment import BMMSegment
from max_prob_segment import MaxProbabilitySegment
from viterbi_pos_tagger import HMM_Viterbi_POS_TAGGER
import time

class App(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        
        self.initUI()
        
        self.bmm = BMMSegment(4)
        self.mp = MaxProbabilitySegment()
        self.tagger = HMM_Viterbi_POS_TAGGER()
  
    def initUI(self):
      
        self.parent.title("双向最大匹配分词")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, pad=7)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(5, weight=3)
        
        self.cap1Lbl = Label(self, text="输入文本")
        self.cap1Lbl.grid(sticky=W, pady=4, padx=5)
        
        self.inputText = ScrolledText(self)
        self.inputText.grid(row=1, column=0, columnspan=2, rowspan=3, 
            padx=5, sticky=E+W+N)
        self.inputText.tag_config('highlight', background='yellow')

        self.cap2Lbl = Label(self, text='分词结果')
        self.cap2Lbl.grid(row=4, column=0, sticky=W, pady=4, padx=5)

        self.outputText = ScrolledText(self)
        self.outputText.grid(row=5, column=0, columnspan=2, rowspan=3, 
            padx=5, sticky=E+S+W)
        
        self.rightFrame = Frame(self)
        self.rightFrame.grid(row=1, column=2, columnspan=7)

        self.bmmBtn = Button(self.rightFrame, text="双向最大匹配", command=self.onBMM)
        self.bmmBtn.pack(side="top", expand=True, pady=10)

        self.mpBtn = Button(self.rightFrame, text="最大概率分词", command=self.onMP)
        self.mpBtn.pack(side="top", expand=True, pady=10)

        self.hmmBtn = Button(self.rightFrame, text='HMM-Viterbi词性标注', command=self.onHMM)
        self.hmmBtn.pack(side="top", expand=True, pady=10)

        # HINT: Place additional button here

        self.quitBtn = Button(self.rightFrame, text="退出", command=self.onQuit)
        self.quitBtn.pack(side="top", expand=True, pady=10)


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
            self.cap2Lbl['text'] = '分词结果    耗时: ' + '{0:.1f} ms'.format(elapsed*1000)

    def onMP(self):
        self.outputText.delete('1.0', END)
        inStr = self.inputText.get('1.0', END).strip()

        start = time.clock()
        result = self.mp.MaxProbability(inStr)

        self.outputText.insert(INSERT, result)
        elapsed = time.clock() - start

        if result != '':
            self.cap2Lbl['text'] = '分词结果    耗时: ' + '{0:.1f} ms'.format(elapsed*1000)

    def onHMM(self):
        self.outputText.delete('1.0', END)
        inStr = self.inputText.get('1.0', END).strip()
        start = time.clock()

        segmented = self.mp.MaxProbability(inStr)

        obs = [w.strip('/') for w in segmented.split()]
        result = self.tagger.Viterbi(obs)
        elapsed = time.clock() - start

        self.outputText.insert(INSERT, result)

        if result != '':
            self.cap2Lbl['text'] = '词性标注结果     耗时: ' + '{0:.1f} ms'.format(elapsed*1000)


def main():
  
    root = Tk()
    root.option_add("*Font", "微软雅黑 10")
    root.geometry("700x500+300+300")
    app = App(root)
    root.mainloop()  


if __name__ == '__main__':
    main()
#!/usr/bin/env python27

import ttanr
import Tkinter as Tk
import tkFileDialog
import tkMessageBox
import os.path

class TTANR:
    def __init__(self,root):
        self.root=root
        self.outDir= os.path.join(os.path.expanduser("~"),"Documents")

        inputFrame=Tk.Frame(root)
        inputFrame.pack()
        Tk.Label(inputFrame,text="Select input source")
        self.chooseO8N=Tk.BooleanVar()
        o8nRButton=Tk.Radiobutton(inputFrame,text="OCTGN File",variable=self.chooseO8N,value=True,command=self.inputO8N)
        ndbRButton=Tk.Radiobutton(inputFrame,text="netrunnerdb",variable=self.chooseO8N,value=False,command=self.inputNDB)

        o8nRButton.pack(side=Tk.LEFT)
        ndbRButton.pack(side=Tk.LEFT)

        o8nFrame=Tk.Frame(root)
        o8nFrame.pack()
        Tk.Label(o8nFrame,text="Select file to import").pack()
        self.o8nEntry=Tk.Entry(o8nFrame)
        self.o8nEntry.pack(side=Tk.LEFT)
        self.o8nButton=Tk.Button(o8nFrame,text="Browse",command=self.pickO8NFile)
        self.o8nButton.pack(side=Tk.LEFT)
        
        numberFrame = Tk.Frame(root)
        numberFrame.pack()
        Tk.Label(numberFrame,text="Enter netrunnerdb # to import").pack()
        self.deckEntry=Tk.Entry(numberFrame)
        self.deckEntry.pack()

        ndbRButton.select()
        ndbRButton.invoke()

        outputDirFrame = Tk.Frame(root)
        outputDirFrame.pack()
        Tk.Label(outputDirFrame,text="Location to export files?").pack()
        self.outputDirEntry=Tk.Entry(outputDirFrame)
        self.outputDirEntry.insert(0,self.outDir)
        self.outputDirEntry.pack(side=Tk.LEFT)
        outputDirButton=Tk.Button(outputDirFrame,text="Browse",command=self.pickOutputDir)
        outputDirButton.pack(side=Tk.LEFT)

        urlFrame = Tk.Frame(root)
        urlFrame.pack()
        self.useUrl=Tk.BooleanVar()
        urlButton=Tk.Checkbutton(urlFrame,text="Set base url in file?",variable=self.useUrl,onvalue=True,offvalue=False,command=self.toggleUrl)
        self.urlEntry=Tk.Entry(urlFrame)
        urlButton.pack(side=Tk.LEFT)

        self.urlEntry.config(state=Tk.DISABLED)
        self.urlEntry.pack(side=Tk.LEFT)

        self.install=Tk.BooleanVar()
        installFrame=Tk.Frame(root)
        installFrame.pack()
        installButton=Tk.Checkbutton(installFrame,text="Install to TTS dir?",variable=self.install,onvalue=True,offvalue=False)
        installButton.select()
        installButton.pack()

        goFrame=Tk.Frame(root)
        goFrame.pack()
        goButton=Tk.Button(goFrame,text="GO",command=self.go)
        goButton.pack(side=Tk.LEFT)

    def toggleUrl(self):
        if self.useUrl.get():
            self.urlEntry.config(state=Tk.NORMAL)
        else:
            self.urlEntry.config(state=Tk.DISABLED)

    def inputO8N(self):
        self.o8nEntry.config(state=Tk.NORMAL)
        self.o8nButton.config(state=Tk.NORMAL)
        self.deckEntry.config(state=Tk.DISABLED)

    def inputNDB(self):
        self.o8nEntry.config(state=Tk.DISABLED)
        self.o8nButton.config(state=Tk.DISABLED)
        self.deckEntry.config(state=Tk.NORMAL)

    def pickO8NFile(self):
        self.deckFile=tkFileDialog.askopenfilename(
            parent=self.root,
            initialdir=os.path.join(os.path.expanduser("~"),"Downloads"),
            filetypes=[('OCTGN files','*.o8d')],
            defaultextension='o8d',
            title='Choose deck file')
        self.o8nEntry.delete(0,Tk.END)
        self.o8nEntry.insert(0,self.deckFile)
    
    def pickOutputDir(self):
        self.outDir=tkFileDialog.askdirectory(
            parent=self.master,
            initialdir=self.outDir,
            mustexist=True
        )
        self.outputDirEnty.delete(0,Tk.END)
        self.outputDirEntry.insert(0,self.outDir)

    def go(self):
        deckID=self.deckEntry.get()
        deck=None
        if self.chooseO8N:
            deck=ttanr.load_octgn_deck(self.deckFile)
        else:
            deck=ttanr.load_netrunnerdb_deck(deckID)

        if self.useUrl.get():
            ttanr.write_files(deck,self.urlEntry.get(),self.install.get())
        else:
            ttanr.write_files(deck,"null://",self.install.get())

        tkMessageBox.showinfo("ttanr","Done")


def main():
    root = Tk.Tk()
    root.wm_title("TTANR")
    ttanr=TTANR(root)
    root.mainloop()


if __name__ == "__main__":
    main()

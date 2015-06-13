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
        numberFrame = Tk.Frame(root)
        numberFrame.pack()
        Tk.Label(numberFrame,text="Enter netrunnerdb # to import").pack()
        self.deckEntry=Tk.Entry(numberFrame)
        self.deckEntry.pack()

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

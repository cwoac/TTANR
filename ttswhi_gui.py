#!/usr/bin/env python27

import ttswhi
import Tkinter as Tk
import tkFileDialog
import tkMessageBox
import os.path

class TTSWHI:
    def __init__(self,root):
        self.root=root
        self.backFile=None
        self.deckFile=None
        self.outDir= os.path.join(os.path.expanduser("~"),"Documents")

        numberFrame = Tk.Frame(root)
        numberFrame.pack()
        Tk.Label(numberFrame,text="Enter cardbox # to import").pack()
        self.deckEntry=Tk.Entry(numberFrame)
        self.deckEntry.pack()

        backFrame=Tk.Frame(root)
        backFrame.pack()
        self.customBack=Tk.BooleanVar()
        customBackButton=Tk.Checkbutton(backFrame,text="Custom back image?",variable=self.customBack,onvalue=True,offvalue=False,command=self.toggleBack)
        customBackButton.pack()
        self.customBackEntry=Tk.Entry(backFrame)
        self.customBackEntry.pack(side=Tk.LEFT)
        self.customBackFileButton=Tk.Button(backFrame,text="Browse",command=self.pickBackFile)
        self.customBackFileButton.pack(side=Tk.LEFT)
        self.toggleBack()


        outputDirFrame = Tk.Frame(root)
        outputDirFrame.pack()
        self.outputLocal=Tk.BooleanVar()
        outputCheckButton=Tk.Checkbutton(outputDirFrame,text="Export files for upload?",variable=self.outputLocal,onvalue=True,offvalue=False,command=self.toggleOutput)
        outputCheckButton.select()
        outputCheckButton.pack()
        self.outputDirEntry=Tk.Entry(outputDirFrame)
        self.outputDirEntry.insert(0,self.outDir)
        self.outputDirEntry.pack(side=Tk.LEFT)
        self.outputDirButton=Tk.Button(outputDirFrame,text="Browse",command=self.pickOutputDir)
        self.outputDirButton.pack(side=Tk.LEFT)

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

    def toggleOutput(self):
        if self.outputLocal.get():
            self.outputDirEntry.config(state=Tk.NORMAL)
            self.outputDirButton.config(state=Tk.NORMAL)
        else:
            self.outputDirEntry.config(state=Tk.DISABLED)
            self.outputDirButton.config(state=Tk.DISABLED)

    def toggleBack(self):
        if self.customBack.get():
            self.customBackEntry.config(state=Tk.NORMAL)
            self.customBackFileButton.config(state=Tk.NORMAL)
        else:
            self.customBackEntry.config(state=Tk.DISABLED)
            self.customBackFileButton.config(state=Tk.DISABLED)

    def toggleUrl(self):
        if self.useUrl.get():
            self.urlEntry.config(state=Tk.NORMAL)
        else:
            self.urlEntry.config(state=Tk.DISABLED)

    def pickBackFile(self):
        self.backFile=tkFileDialog.askopenfilename(
            parent=self.root,
            initialdir=os.path.join(os.path.expanduser("~"),"Downloads"),
            filetypes=[('JPEG files','*.jpg'),('PNG files','*.png')],
            title='Choose background image file')
        self.customBackEntry.delete(0,Tk.END)
        self.customBackEntry.insert(0,self.backFile)

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
        deck=ttswhi.load_deckbox_deck(deckID)
        deck['back_filename']=self.backFile

        if self.useUrl.get():
            ttswhi.write_files(deck,self.urlEntry.get(),self.outputLocal.get(),self.outputDirEntry.get(),self.install.get())
        else:
            ttswhi.write_files(deck,"null://",self.outputLocal.get(),self.outputDirEntry.get(),self.install.get())

        tkMessageBox.showinfo("TTS WHI","Done")


def main():
    root = Tk.Tk()
    root.wm_title("TTS WHI")
    ttswhi=TTSWHI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

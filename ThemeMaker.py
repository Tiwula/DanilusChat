import json
import tkinter
from tkinter import *
from tkinter import font, scrolledtext, colorchooser, filedialog

def setCol(entry):
    col = colorchooser.askcolor()
    back = entry.get()
    try:
        entry.delete('0', 'end')
        entry.insert('0', col[1].upper())
    except:
        entry.delete('0', 'end')
        entry.insert('0', back)

def init(se, win):
    pop = tkinter.Toplevel(win)
    pop.title("Config")
    #pop.geometry("300x150")
    textfont = font.Font(family='Arial', size='12')
    sel = IntVar(pop)
    pop.resizable(False, False)

    Label(pop, text="Author nick and site").grid(row=0, columnspan=2)
    entrNick = Entry(pop)
    entrNick.grid(row=1, column=0, padx=4)
    entrSite = Entry(pop, width=40)
    entrSite.grid(row=1, column=1, padx=5)


    Label(pop, text="Mian").grid(row=2, columnspan=2)

    Label(pop, text="Background").grid(row=3, column=0)
    entrMBG = Entry(pop)
    entrMBG.delete('0', 'end')
    entrMBG.insert('0', se.config["main"]["BColor"])
    entrMBG.bind('<ButtonRelease-3>', lambda e: setCol(entrMBG))
    entrMBG.grid(row=4, column=0, padx=4)

    Label(pop, text="Title format").grid(row=3, column=1)
    entrMTT = Entry(pop, width=40)
    entrMTT.delete('0', 'end')
    entrMTT.insert('0', se.config["main"]["TitleFormat"])
    entrMTT.grid(row=4, column=1, padx=5)#nswe


    Label(pop, text="Text").grid(row=5, columnspan=2)

    Label(pop, text="Background").grid(row=6, column=0)
    entrTBG = Entry(pop)
    entrTBG.delete('0', 'end')
    entrTBG.insert('0', se.config["text"]["BColor"])
    entrTBG.bind('<ButtonRelease-3>', lambda e: setCol(entrTBG))
    entrTBG.grid(row=7, column=0, padx=4)

    Label(pop, text="Foreground").grid(row=6, column=1)
    entrTFG = Entry(pop)
    entrTFG.delete('0', 'end')
    entrTFG.insert('0', se.config["text"]["FColor"])
    entrTFG.bind('<ButtonRelease-3>', lambda e: setCol(entrTFG))
    entrTFG.grid(row=7, column=1, padx=5)


    Label(pop, text="Input").grid(row=8, columnspan=2)

    Label(pop, text="Background").grid(row=9, column=0)
    entrIBG = Entry(pop)
    entrIBG.delete('0', 'end')
    entrIBG.insert('0', se.config["input"]["BColor"])
    entrIBG.bind('<ButtonRelease-3>', lambda e: setCol(entrIBG))
    entrIBG.grid(row=10, column=0, padx=4)

    Label(pop, text="Foreground").grid(row=9, column=1)
    entrIFG = Entry(pop)
    entrIFG.delete('0', 'end')
    entrIFG.insert('0', se.config["input"]["FColor"])
    entrIFG.bind('<ButtonRelease-3>', lambda e: setCol(entrIFG))
    entrIFG.grid(row=10, column=1, padx=5)

    Label(pop, text="Cursor Color").grid(row=11, columnspan=2)
    entrICC = Entry(pop)
    entrICC.delete('0', 'end')
    entrICC.insert('0', se.config["input"]["CCursor"])
    entrICC.bind('<ButtonRelease-3>', lambda e: setCol(entrICC))
    entrICC.grid(row=12, columnspan=2, padx=5)


    Label(pop, text="Popup menu").grid(row=13, columnspan=2)

    Label(pop, text="Background").grid(row=14, column=0)
    entrPBG = Entry(pop)
    entrPBG.delete('0', 'end')
    entrPBG.insert('0', se.config["input"]["BColor"])
    entrPBG.bind('<ButtonRelease-3>', lambda e: setCol(entrPBG))
    entrPBG.grid(row=15, column=0, padx=4)

    Label(pop, text="Foreground").grid(row=14, column=1)
    entrPFG = Entry(pop)
    entrPFG.delete('0', 'end')
    entrPFG.insert('0', se.config["input"]["FColor"])
    entrPFG.bind('<ButtonRelease-3>', lambda e: setCol(entrPFG))
    entrPFG.grid(row=15, column=1, padx=5)


    fontList = Listbox(pop, width=30)
    fontList.grid(row=0, rowspan=7, column=2, padx=10, pady=3)
    fontList.bind('<ButtonRelease-1>', lambda e: textfont.config(family=fontList.get(fontList.curselection())))
    for f in font.families():
        fontList.insert('end', f)

    sizeList = Listbox(pop, width=5)
    sizeList.grid(row=0, rowspan=7, column=3, padx=3, pady=3)
    sizeList.bind('<ButtonRelease-1>', lambda e: textfont.config(size=sizeList.get(sizeList.curselection())))
    for i in range(5, 26):
        sizeList.insert('end', i)

    # Create enry for example
    entry = Entry(pop, font=textfont, width=20)
    entry.grid(row=7, column=2, columnspan=2, pady=3)

    R1 = Radiobutton(pop, text="Text", variable=sel, value=1)
    R1.grid(row=8, column=2, pady=3)

    R2 = Radiobutton(pop, text="Input", variable=sel, value=2)
    R2.grid(row=9, column=2, pady=3)

    R3 = Radiobutton(pop, text="Popup menu", variable=sel, value=3)
    R3.grid(row=10, column=2, pady=3)

    # Create Ok button
    okButton = Button(pop, text='Apply', command=lambda: choice(se, sel.get(), textfont['family'], textfont['size']))
    okButton.grid(row=11, column=2, columnspan=2, padx=5)

    def apply():
        """data = []
        data[0] = 
        data[1] = 
        data[2] = 
        data[3] = 
        data[4] = 
        data[5] = 
        data[6] = 
        data[7] = 
        data[8] = 
        data[9] = 
        data[10] = 
        data[11] = 
        data[12] = 
        data[13] = 
        data[14] = """

        se.config["author"]["Author"] = entrNick.get().strip()
        se.config["author"]["Site"] = entrSite.get().strip()

        se.config["main"]["BColor"] = entrMBG.get().strip()
        se.config["main"]["TitleFormat"] = entrMTT.get().strip()

        se.config["text"]["BColor"] = entrTBG.get().strip()
        se.config["text"]["FColor"] = entrTFG.get().strip()

        se.config["input"]["BColor"] = entrIBG.get().strip()
        se.config["input"]["FColor"] = entrIFG.get().strip()
        se.config["input"]["CCursor"] = entrICC.get().strip()

        se.config["popup"]["BColor"] = entrPBG.get().strip()
        se.config["popup"]["FColor"] = entrPFG.get().strip()

        se.apply()

    previewButton = Button(pop, text='Apply & Preview', command=apply)
    previewButton.grid(row=16, columnspan=2, pady=5)

    saveButton = Button(pop, text='Save', command=lambda: se.save())
    saveButton.grid(row=16, column=1, columnspan=2, pady=5)

# Define a function to implement choice function
def choice(se, sel, font, size):
    if sel == 1:
        se.config["text"]["FFont"] = font
        se.config["text"]["SFont"] = int(size)
    elif sel == 2:
        se.config["input"]["FFont"] = font
        se.config["input"]["SFont"] = int(size)
    elif sel == 3:
        se.config["popup"]["FFont"] = font
        se.config["popup"]["SFont"] = int(size)

class win:
    def __init__(self):
        self.config = {}

        self.config["author"] = {}
        self.config["main"] = {}
        self.config["text"] = {}
        self.config["input"] = {}
        self.config["popup"] = {}

        self.config["author"]["Author"] = ""
        self.config["author"]["Site"] = ""

        self.config["main"]["BColor"] = "#FFFFFF"
        self.config["main"]["TitleFormat"] = "Chat - &HOST&:&PORT&@&NICK&"

        self.config["text"]["FFont"] = "Arial"
        self.config["text"]["SFont"] = 12
        self.config["text"]["BColor"] = "#FFFFFF"
        self.config["text"]["FColor"] = "#000000"

        self.config["input"]["FFont"] = "Arial"
        self.config["input"]["SFont"] = 12
        self.config["input"]["BColor"] = "#FFFFFF"
        self.config["input"]["FColor"] = "#000000"
        self.config["input"]["CCursor"] = "#000000"

        self.config["popup"]["FFont"] = "Arial"
        self.config["popup"]["SFont"] = 10
        self.config["popup"]["BColor"] = "#FFFFFF"
        self.config["popup"]["FColor"] = "#000000"

        self.win = Tk()
        self.win.configure(bg='lightgray')
        self.win.title(self.config["main"]["TitleFormat"] + ' (Theme Maker by Danilus)')

        self.textArea = scrolledtext.ScrolledText(self.win)
        self.textArea.pack(fill='both')
        self.textArea.config(font=('Arial', 12))

        self.inputArea = Entry(self.win)
        self.inputArea.config(font=('Arial', 12))
        self.inputArea.pack(pady=3, fill='x', side='bottom')
        self.inputArea.bind('<Button-3>', self.popup)

        self.popupMenu = Menu(self.inputArea, tearoff=0)
        self.popupMenu.add_command(label="&0 Black")
        self.popupMenu.add_command(label="&r Reset")

        init(self, self.win)

        self.win.resizable(False, False)

        self.win.mainloop()

    def popup(self, event):
        try:
            self.popupMenu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popupMenu.grab_release()

    def apply(self):
        """self.config["main"]["BColor"] = data[0]
        self.config["main"]["TitleFormat"] = data[1]

        self.config["text"]["FFont"] = data[2]
        self.config["text"]["SFont"] = data[3]
        self.config["text"]["BColor"] = data[4]
        self.config["text"]["FColor"] = data[5]

        self.config["input"]["FFont"] = data[6]
        self.config["input"]["SFont"] = data[7]
        self.config["input"]["BColor"] = data[8]
        self.config["input"]["FColor"] = data[9]
        self.config["input"]["CCursor"] = data[10]

        self.config["popup"]["FFont"] = data[11]
        self.config["popup"]["SFont"] = data[12]
        self.config["popup"]["BColor"] = data[13]
        self.config["popup"]["FColor"] = data[14]"""

        self.textArea.config(bg=self.config['text']['BColor'], fg=self.config['text']['FColor'], font=(self.config['text']['FFont'], self.config['text']['SFont']))
        self.inputArea.config(insertbackground=self.config['input']['CCursor'], bg=self.config['input']['BColor'], fg=self.config['input']['FColor'], font=(self.config['input']['FFont'], self.config['input']['SFont']))
        self.popupMenu.config(bg=self.config['popup']['BColor'], fg=self.config['popup']['FColor'], font=(self.config['popup']['FFont'], self.config['popup']['SFont']))
        self.win.config(bg=self.config['main']['BColor'])
        self.win.title(self.config['main']['TitleFormat'] + ' (Theme Maker by Danilus)')

    def save(self):
        f = filedialog.asksaveasfile(initialfile = 'Untitled theme.thm',defaultextension=".thm",filetypes=[("Theme","*.thm")])
        json.dump(self.config, f)
        f.close()

main = win()
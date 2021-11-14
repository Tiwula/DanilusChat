import socket
import threading as th
import tkinter
from tkinter.font import Font
from tkinter.constants import *
import tkinter.scrolledtext
from tkinter import Tk, messagebox
from datetime import datetime as dt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import sys, traceback, os
import winsound
import json

args = sys.argv

cfgDone = False

if len(args) == 6:
    if args[1] == "launcher":
        HOST = args[2]
        PORT = args[3]
        NICK = args[4]
        THEME = args[5]
        f = open('client-cfg.json')
        settings = json.load(f)
        f.close()
        cfgDone = True

if cfgDone == False:
    try:
        f = open('client-cfg.json')
        settings = json.load(f)
        f.close()

        HOST = settings['client']['IPhost']
        PORT = settings['client']['PortHost']
        NICK = settings['client']['Nick']
        THEME = settings['settings']['Theme']
    except:
        messagebox.showerror("/// Error ///", "Config read error")
        defText = """{
        "client": {
            "IPhost": "127.0.0.1",
            "PortHost": 9574,
            "Nick": "User"
        },
        "settings": {
            "Timestamp": true,
            "Colored": true,
            "Sounds": true,
            "Theme": "default.thm"
        }
    }"""
        f = open('client-cfg.json', 'w')
        f.write(defText)
        f.close()
        settings = json.loads(defText)

        HOST = settings['client']['IPhost']
        PORT = settings['client']['PortHost']
        NICK = settings['client']['Nick']
        THEME = settings['settings']['Theme']

try:
    os.mkdir('themes')
except:
    pass

class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.history = ['']
        self.curSel = 0
        self.histLen = 100
        self.counter = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except Exception as ex:
            messagebox.showerror("Connection error", str(ex) + '\n\nCheck client-cfg > client')
            raise("Connection error")

        msg = Tk()
        msg.withdraw()

        self.nick = NICK

        self.guiDone = False
        self.running = True

        try:
            f = open('themes\\'+THEME)
            self.theme = json.load(f)
            f.close()
        except:
            self.defaultConfig()

        try:
            self.fdf = self.theme['text']['FFont']
            self.fds = self.theme['text']['SFont']
        except Exception as ex:
            messagebox.showerror("/// Error ///", "Theme loading error\n" + str(ex))
            

        guiThread = th.Thread(target=self.guiLoop)
        self.receiveThread = th.Thread(target=self.receivLoop)

        guiThread.start()
        
        
        try:
            self.FDefault = Font(family=self.theme['text']['FFont'], size=int(self.theme['text']['SFont']))
            self.tformat = self.theme['main']['TitleFormat']
        except Exception as ex:
            messagebox.showerror("/// Error ///", "Theme loading error\n" + str(ex))
            self.win.quit()

        
            
        self.receiveThread.start()

    def defaultConfig(self):
        messagebox.showerror("/// Error ///", "Theme loading error\n\nThe default theme will be loaded automatically\n\nIf the error persists, check the client configuration")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        
        defText = """{
    "author":
    {
        "Author": "Danilus",
        "Site": "https://github.com/Danilus-s"
    },
    "main":
    {
        "BColor": "#FFFFFF",
        "TitleFormat": "Chat - &HOST&:&PORT&@&NICK&"
    },
    "text":
    {
        "FFont": "Arial",
        "SFont": 12,
        "BColor": "#FFFFFF",
        "FColor": "#000000"
    },
    "input":
    {
        "FFont": "Arial",
        "SFont": 12,
        "BColor": "#FFFFFF",
        "FColor": "#000000",
        "CCursor": "#000000"
    },
    "popup":
    {
        "FFont": "Arial",
        "SFont": 10,
        "BColor": "#FFFFFF",
        "FColor": "#000000"
    }
}"""

        f = open('themes\\default.thm', 'w')
        f.write(defText)
        f.close()
        self.theme = json.loads(defText)
        

    def guiLoop(self):
        self.win = Tk()
        self.win.configure(bg='lightgray')
        self.win.title('Chat ~ Client')

        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)

        self.textArea = tkinter.scrolledtext.ScrolledText(self.win)
        self.textArea.grid(row=0, column=0, sticky='nswe')
        self.textArea.config(state='disabled', font=('Comic Sans MS', 12))


        #configure formating
        self.textArea.tag_configure("ColorBlack", foreground='#000000')
        self.textArea.tag_configure("ColorDBlue", foreground='#0000AA')
        self.textArea.tag_configure("ColorDGreen", foreground='#00AA00')
        self.textArea.tag_configure("ColorDAqua", foreground='#00AAAA')
        self.textArea.tag_configure("ColorDRed", foreground='#AA0000')
        self.textArea.tag_configure("ColorDPurple", foreground='#AA00AA')
        self.textArea.tag_configure("ColorGold", foreground='#FFAA00')
        self.textArea.tag_configure("ColorGray", foreground='#AAAAAA')
        self.textArea.tag_configure("ColorDGray", foreground='#555555')
        self.textArea.tag_configure("ColorBlue", foreground='#5555FF')
        self.textArea.tag_configure("ColorGreen", foreground='#55FF55')
        self.textArea.tag_configure("ColorAqua", foreground='#55FFFF')
        self.textArea.tag_configure("ColorRed", foreground='#FF5555')
        self.textArea.tag_configure("ColorLPurple", foreground='#FF55FF')
        self.textArea.tag_configure("ColorYellow", foreground='#FFFF55')
        self.textArea.tag_configure("ColorWhite", foreground='#FFFFFF')

        self.textArea.tag_configure("FontBold", font=(self.fdf, self.fds, 'bold'))
        self.textArea.tag_configure("FontItalic", font=(self.fdf, self.fds, 'italic'))
        self.textArea.tag_configure("FontUnderline", font=(self.fdf, self.fds, 'underline'))
        self.textArea.tag_configure("FontOverstrike", font=(self.fdf, self.fds, 'overstrike'))


        self.inputArea = tkinter.Entry(self.win)
        self.inputArea.config(font=('Arial', 12))
        self.inputArea.grid(row=1, column=0, sticky='swe')

        self.inputArea.bind('<Return>', self.write)
        self.inputArea.bind('<Down>', self.hist)
        self.inputArea.bind('<Up>', self.hist)
        self.inputArea.bind('<Control-space>', self.popup)
        self.inputArea.bind('<Button-3>', self.popup)

        self.popupMenu = tkinter.Menu(self.inputArea, tearoff=0)
        self.popupMenu.add_command(label="&0 Black", command=lambda: self.formIns('&0'))
        self.popupMenu.add_command(label="&1 Dark Blue", command=lambda: self.formIns('&1'))
        self.popupMenu.add_command(label="&2 Dark Green", command=lambda: self.formIns('&2'))
        self.popupMenu.add_command(label="&3 Dark Aqua", command=lambda: self.formIns('&3'))
        self.popupMenu.add_command(label="&4 Dark Red", command=lambda: self.formIns('&4'))
        self.popupMenu.add_command(label="&5 Dark Purple", command=lambda: self.formIns('&5'))
        self.popupMenu.add_command(label="&6 Gold", command=lambda: self.formIns('&6'))
        self.popupMenu.add_command(label="&7 Gray", command=lambda: self.formIns('&7'))
        self.popupMenu.add_command(label="&8 Dark Gray", command=lambda: self.formIns('&8'))
        self.popupMenu.add_command(label="&9 Blue", command=lambda: self.formIns('&9'))
        self.popupMenu.add_command(label="&a Green", command=lambda: self.formIns('&a'))
        self.popupMenu.add_command(label="&b Aqua", command=lambda: self.formIns('&b'))
        self.popupMenu.add_command(label="&c Red", command=lambda: self.formIns('&c'))
        self.popupMenu.add_command(label="&d Light Purple", command=lambda: self.formIns('&d'))
        self.popupMenu.add_command(label="&e Yellow", command=lambda: self.formIns('&e'))
        self.popupMenu.add_command(label="&f White", command=lambda: self.formIns('&f'))

        self.popupMenu.add_command(label="&l Bold", command=lambda: self.formIns('&l'))
        self.popupMenu.add_command(label="&m Strikethrough", command=lambda: self.formIns('&m'))
        self.popupMenu.add_command(label="&n Underline", command=lambda: self.formIns('&n'))
        self.popupMenu.add_command(label="&o Italic", command=lambda: self.formIns('&o'))

        self.popupMenu.add_command(label="&r Reset", command=lambda: self.formIns('&r'))

        self.inputArea.focus_set()

        self.guiDone = True

        self.win.protocol('WM_DELETE_WINDOW', self.stop)

        try:
            self.textArea.config(bg=self.theme['text']['BColor'], fg=self.theme['text']['FColor'], font=(self.theme['text']['FFont'], int(self.theme['text']['SFont'])))
            self.inputArea.config(insertbackground=self.theme['input']['CCursor'], bg=self.theme['input']['BColor'], fg=self.theme['input']['FColor'], font=(self.theme['input']['FFont'], int(self.theme['input']['SFont'])))
            self.popupMenu.config(bg=self.theme['popup']['BColor'], fg=self.theme['popup']['FColor'], font=(self.theme['popup']['FFont'], int(self.theme['popup']['SFont'])))
            self.textArea.tag_configure("Reset", foreground=self.theme['text']['FColor'], font=self.FDefault)
            self.win.config(bg=self.theme['main']['BColor'])
        except:
            self.defaultConfig()

        self.win.mainloop()
       

    def popup(self, event):
        try:
            self.popupMenu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popupMenu.grab_release()

    def formIns(self, event):
        self.inputArea.insert(self.inputArea.index(INSERT), event)

    def hist(self, event):
        if event.keysym == 'Up' and self.curSel < len(self.history)-1:
            if self.curSel == 0:
                self.history[0] = self.inputArea.get()
            self.curSel += 1
            self.inputArea.delete('0', 'end')
            self.inputArea.insert('0', self.history[self.curSel])
        elif event.keysym == 'Down' and self.curSel > 0:
            self.curSel -= 1
            self.inputArea.delete('0', 'end')
            self.inputArea.insert('0', self.history[self.curSel])

    def findNL(self, text):
        count = 0
        while True:
            i = text.find('\n')
            
            if i == -1:
                return count
                break

            count += 1
            text = text[:i] + text[i+2:]

    def write(self, event):
        try:
            message = self.inputArea.get().strip()
            self.history.insert(1, message)
            if len(self.history) > self.histLen:
                self.history.pop(self.histLen)
            if message.startswith('!'):
                com = message[1:].split(' ')
                if com[0] == 'exit' or com[0] == 'stop':
                    self.disconnect()
                if com[0] == 'connect' and len(com) == 1:
                    self.connect(self.host, self.port)
                if com[0] == 'connect' and len(com) == 3:
                    self.connect(com[1], com[2])
            else:
                self.sock.send(self.encrypt(message))
        except Exception as ex:
            self.writeLine(str(ex))
        self.inputArea.delete('0', 'end')
        self.history[0] = ''
        self.curSel = 0
    
    def disconnect(self):
        self.running = False
        self.sock.close()
        self.writeLine("Disconnected")

    def connect(self, host, port):
        self.running = True
        self.writeLine(f"Connecting to {host}@{port}.")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.receiveThread = th.Thread(target=self.receivLoop)
        self.receiveThread.start()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def form(self, txt):
        text = txt
        if settings['settings']['Timestamp']:
                d = dt.now()
                newd = d.strftime('&7%H:%M:%S&r ')
                text = newd + text
        poss = []
        cod = []
        while True:
            i = text.find('&')
            
            if i == -1:
                break

            code = text[i:i+2]
            pos = i+2
            text = text[:i] + text[i+2:]
            poss.append(i)
            cod.append(code)
        self.writeLine(text)
        for i in range(0, len(poss)):
            
            col = ''

            if settings['settings']['Colored']:
                #Color
                if cod[i] == '&0':
                    col = "ColorBlack"
                elif cod[i] == '&1':
                    col = "ColorDBlue"
                elif cod[i] == '&2':
                    col = "ColorDGreen"
                elif cod[i] == '&3':
                    col = "ColorDAqua"
                elif cod[i] == '&4':
                    col = "ColorDRed"
                elif cod[i] == '&5':
                    col = "ColorDPurple"
                elif cod[i] == '&6':
                    col = "ColorGold"
                elif cod[i] == '&7':
                   col = "ColorGray"
                elif cod[i] == '&8':
                    col = "ColorDGray"
                elif cod[i] == '&9':
                    col = "ColorBlue"
                elif cod[i] == '&a':
                    col = "ColorGreen"
                elif cod[i] == '&b':
                    col = "ColorAqua"
                elif cod[i] == '&c':
                    col = "ColorRed"
                elif cod[i] == '&d':
                    col = "ColorLPurple"
                elif cod[i] == '&e':
                     col = "ColorYellow"
                elif cod[i] == '&f':
                     col = "ColorWhite"

                #Font
                elif cod[i] == '&l':
                    col = "FontBold"
                elif cod[i] == '&o':
                    col = "FontItalic"
                elif cod[i] == '&n':
                    col = "FontUnderline"
                elif cod[i] == '&m':
                    col = "FontOverstrike"

                #Reset
                elif cod[i] == '&r':
                    col = "ColorReset"


            if col != '':
                self.textArea.config(state='normal')
                if i+1 == len(poss):
                    self.textArea.tag_add(col, str(self.counter)+'.'+str(poss[i]), str(self.counter)+'.'+str(len(text)))
                else:
                    self.textArea.tag_add(col, str(self.counter)+'.'+str(poss[i]), str(self.counter)+'.'+str(poss[i+1]))
                self.textArea.config(state='disabled')


    def writeLine(self, message):
        if self.guiDone:
            self.textArea.config(state='normal')
            mes = message
            self.textArea.insert('end', mes+'\n')
            self.textArea.yview('end')
            self.textArea.config(state='disabled')
            if str(message).find('\n'):
                self.counter += self.findNL(message)
            self.counter += 1
            if self.win.focus_get() == None and settings['settings']['Sounds']:
                winsound.Beep(600, 100)

    def encrypt(self, message):
        message = str(message).encode('utf-8')
        return  self.pubKey.encrypt(message, padding.OAEP
                        (mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                        )
    def decrypt(self, message):
        return  self.privKey.decrypt(message, padding.OAEP(
                        mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                        ).decode('utf-8')

    def receivLoop(self):
        
        #key gen
        self.privKey  = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        
        self.sock.send('COM:READY'.encode('utf-8'))
        if self.guiDone:
            rdict = {   '&HOST&' : self.host,
                            '&PORT&' : self.port,
                            '&NICK&' : self.nick
                            }
            text = self.theme['main']['TitleFormat']
            for k in rdict:
                text = text.replace(k, str(rdict[k]))
            self.win.title(text)
        while self.running:
            try:
                message = self.sock.recv(2048)
                try:
                    if (message == ""):
                        try:  
                            self.sock.send(self.encrypt('/ping'))
                        except socket.error:  
                            self.writeLine("Connection lost")
                            self.sock.close()
                            self.running = False
                            break
                except:
                    pass
                deMesg = ''
                try: 
                    deMesg = message.decode('utf-8')
                except:
                    pass


                if deMesg[0:4] == 'COM:':
                    #nick
                    if deMesg == 'COM:NICK':
                        self.sock.send(self.nick.encode('utf-8'))

                    #get server key
                    elif deMesg == 'COM:SERVERPUB':
                        self.sock.send('COM:READYSERVERPUB'.encode('utf-8'))
                        pub = self.sock.recv(2048)
                        self.pubKey = serialization.load_pem_public_key( pub, backend=default_backend() )
                        self.sock.send('COM:CLIENTPUB'.encode('utf-8'))


                    #send client key
                    elif deMesg == 'COM:READYCLIENTPUB':
                        pub = self.privKey.public_key()
                        pem = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo)
                        self.sock.send(pem)
                        
                        
                else:
                    try:
                        self.form(self.decrypt(message))
                    except:
                        self.writeLine("Connection lost")
                        self.sock.close()
                        self.running = False
                        break
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(e)
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                self.writeLine(str(e))
                self.sock.close()
                break

client = Client(HOST, int(PORT))
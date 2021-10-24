import socket
import threading as th
import configparser as cp
import tkinter
from tkinter.font import Font
from tkinter.constants import *
import tkinter.scrolledtext
from tkinter import Tk
from datetime import datetime as dt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import sys, traceback, os
import io, random
import winsound

try:
    cfgParser = cp.ConfigParser()
    cfgParser.read(r'client.cfg')

    servData = cfgParser['client']
    HOST = servData['IPhost']
    PORT = servData['PortHost']
    NICK = servData['Nick']

    setData = cfgParser['settings']
    sett = {}
    sett['Timestamp'] = setData['Timestamp']
    if sett['Timestamp'].lower() == 'true':
        sett['Timestamp'] = True
    else:
        sett['Timestamp'] = False

    sett['Colored'] = setData['Colored']
    if sett['Colored'].lower() == 'true':
        sett['Colored'] = True
    else:
        sett['Colored'] = False

    sett['Sounds'] = setData['Sounds']
    if sett['Sounds'].lower() == 'true':
        sett['Sounds'] = True
    else:
        sett['Sounds'] = False
    
    theme = setData['Theme']
except:
    f = io.open('client.cfg', 'w')
    f.write(
    f"""[client]
IPhost = 127.0.0.1
PortHost = 9574
Nick = User{random.randrange(1, 255)}

[settings]
Timestamp = True
Colored = True
Sounds = True
Theme = default.thm""")
    f.close()
    quit()

class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.history = ['']
        self.curSel = 0
        self.histLen = 100
        self.counter = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        msg = Tk()
        msg.withdraw()

        self.nick = NICK

        self.guiDone = False
        self.running = True

        try:
            themeParser = cp.ConfigParser()
            themeParser.read('themes\\'+theme)
        except:
            self.defaultConfig()

        try:
            self.fdf = themeParser['text']['FFont']
            self.fds = themeParser['text']['SFont']
        except Exception as ex:
            print(str(ex))
            self.defaultConfig()

        guiThread = th.Thread(target=self.guiLoop)
        self.receiveThread = th.Thread(target=self.receivLoop)

        guiThread.start()
        
        
        try:
            self.FDefault = Font(family=themeParser['text']['FFont'], size=int(themeParser['text']['SFont']))
            self.tformat = themeParser['main']['TitleFormat']
        except Exception as ex:
            print(str(ex))
            self.defaultConfig()

        
            
        self.receiveThread.start()

    def defaultConfig(self):
        os.mkdir('themes')
        f = io.open('themes\\default.thm', 'w')
        f.write(
"""[main]
BColor = #FFFFFF
TitleFormat = Chat - &HOST&:&PORT&@&NICK&

[text]
FFont = Comic Sans MS
SFont = 12
BColor = #FFFFFF
FColor = #000000

[input]
FFont = Comic Sans MS
SFont = 12
BColor = #FFFFFF
FColor = #000000
CCursor = #000000

[popup]
FFont = Comic Sans MS
SFont = 12
BColor = #FFFFFF
FColor = #000000""")
        f.close()
        quit()

    def guiLoop(self):
        self.win = Tk()
        self.win.configure(bg='lightgray')
        self.win.title('Chat ~ Client')

        self.textArea = tkinter.scrolledtext.ScrolledText(self.win)
        self.textArea.pack(fill='both')
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
        self.inputArea.config(font=('Comic Sans MS', 12))
        self.inputArea.pack(pady=3, fill='x', side='bottom')

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
            themeParser = cp.ConfigParser()
            themeParser.read('themes\\'+theme)
            self.textArea.config(bg=themeParser['text']['BColor'], fg=themeParser['text']['FColor'], font=(themeParser['text']['FFont'], int(themeParser['text']['SFont'])))
            self.inputArea.config(insertbackground=themeParser['input']['CCursor'], bg=themeParser['input']['BColor'], fg=themeParser['input']['FColor'], font=(themeParser['input']['FFont'], int(themeParser['input']['SFont'])))
            self.popupMenu.config(bg=themeParser['popup']['BColor'], fg=themeParser['popup']['FColor'], font=(themeParser['popup']['FFont'], int(themeParser['popup']['SFont'])))
            self.textArea.tag_configure("Reset", foreground=themeParser['text']['FColor'], font=self.FDefault)
            self.win.config(bg=themeParser['main']['BColor'])
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
                """if com[0] == 'connect' and len(com) == 1:
                    self.connect(self.host, self.port)
                if com[0] == 'connect' and len(com) == 3:
                    self.connect(com[1], com[2])"""
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
        self.writeLine("Disconnected.")

    """def connect(self, host, port):
        self.running = True
        self.writeLine(f"Connecting to {host}@{port}.")
        del self.sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.receiveThread.run()"""

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        quit()

    def form(self, txt):
        text = txt
        if sett['Timestamp']:
                d = dt.now()
                newd = d.strftime('%H:%M:%S ')
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

            if sett['Colored']:
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
            if self.win.focus_get() == None and sett['Sounds']:
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
            text = self.tformat
            for k in rdict:
                text = text.replace(k, str(rdict[k]))
            self.win.title(text)
        while self.running:
            try:
                message = self.sock.recv(2048)
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
                    self.form(self.decrypt(message))
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
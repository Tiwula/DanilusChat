import random
import socket
import threading as th
import json
from rich.console import Console
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import sys, traceback, importlib, os, requests


con = Console()

try:
    response = requests.get("https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/sfuncs.py")
    try:
        with open("sfuncs.py", "r") as f:
            data = f.read()
            if len(data) != len(response.text):
                get = con.input(f'[cyan bold][XX-XX-XXXX XX:XX:XX][/] [yellow bold]<sfuncs>[/] "sfuncs" updated. Your filesize: {len(data)}; New filesize: {len(response.text)}. Update? [Y/n]')
                if get.lower().replace(' ', '').startswith('y') or get.replace(' ', '') == '':
                    with open('sfuncs.py', 'w') as f:
                        f.write(response.text)
    except:
        with open('sfuncs.py', 'w') as f:
            f.write(response.text)
except:
    pass

import sfuncs as sf


settings = {}
try:
    with open('server-cfg.json') as f:
        settings = json.load(f)
except:
    defText = """{
	"IPhost": "127.0.0.1",
	"PortHost": 9574,
	"Password": "1234",
	"Debug": true,
	"Formating": true,
	"FormatingNick": true,
	"MultiAccount": true
}"""
    f = open('server-cfg.json', 'w')
    f.write(defText)
    f.close()
    settings = json.loads(defText)
sf.settings = settings

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((settings['IPhost'], settings['PortHost']))

server.listen()

clients = {}
banIpList = []
banNickList = []

try:
    os.mkdir('plugins')
except:
    pass

try:
    os.mkdir('userdata')
except:
    pass

plug = []
pluginfo = {}
debugPlugInfo = {}
for path in os.listdir('plugins'):
    try:
        if path[len(path)-3:] == '.py':
            pname = path[0:len(path)-3]
            plug.append(importlib.import_module('plugins.'+pname))
            sf.log("plugins", f"{pname} initialized.")
            try:
                pluginfo[pname] = plug.plugininfo
            except:
                pluginfo[pname] = {"name": pname, "author": "NoName", "version": "1.0"}
            debugPlugInfo[plug[len(plug)-1]] = pname
    except Exception as ex:
        sf.log('debug', 'Error loading plugin '+pname)
        sf.log('debug', ex)
sf.pluginfo = pluginfo

for i in plug:
    try:
        i.init()
    except AttributeError:
        pass
    except Exception as ex:
        sf.log('debug', 'Error loading plugin '+debugPlugInfo[i])
        sf.log('debug', ex)
        with open('logs\\'+debugPlugInfo[i]+'.log', 'w') as f:
                    traceback.print_exc(file=f)


def sendToAll(data, event="receive message") -> None:
    if event == "receive message":
        for i in plug:
            try:
                i.receive(data)
            except AttributeError:
                pass
            except Exception as ex:
                sf.log('debug', 'Error execute plugin callback '+debugPlugInfo[i])
                sf.log('debug', ex)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                with open('logs\\'+debugPlugInfo[i]+'.log', 'w') as f:
                    traceback.print_exc(file=f)
    elif event == "new user":
        for i in plug:
            try:
                i.newUser(data)
            except AttributeError:
                pass
            except Exception as ex:
                sf.log('debug', 'Error execute plugin callback '+debugPlugInfo[i])
                sf.log('debug', ex)
                with open('logs\\'+debugPlugInfo[i]+'.log', 'w') as f:
                    traceback.print_exc(file=f)

class User:
    def __init__(self, nickname, addr, pubKey, privKey, admin=False, prefix=None, color='&r'):
        self.nickname = nickname
        self.admin = admin
        self.addr = addr
        self.pubKey = pubKey
        self.privKey = privKey
        self.prefix = prefix
        self.color = color
        self.displayNick = nickname

def encrypt(pubKey ,message) -> str:
    message = str(message).encode('utf-8')
    return  pubKey.encrypt(message, padding.OAEP
                    (mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    )
def decrypt(privKey, message) -> bytes:
    return  privKey.decrypt(message, padding.OAEP(
                    mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    ).decode('utf-8')

def loadData(client):
    back = clients[client]
    try:
        f = open(f'userdata\\{clients[client].addr} {clients[client].nickname}.json', 'r')
        cli = json.load(f)
        clients[client].displayNick = cli['displayNick']
        clients[client].admin = cli['admin']
        clients[client].prefix = cli['prefix']
        clients[client].color = cli['color']
    except Exception as ex:
        clients[client] = back
        sf.log('server', f"Error loading data for user {clients[client].displayNick}.")
        sf.log('server', ex)

def saveData(client):
    cli = {}
    for cl in clients:
        cli['addr'] = clients[cl].addr
        cli['nickname'] = clients[cl].nickname
        cli['admin'] = clients[cl].admin
        cli['prefix'] = clients[cl].prefix
        cli['color'] = clients[cl].color
        cli['displayNick'] = clients[cl].displayNick
    with open(f'userdata\\{clients[client].addr} {clients[client].nickname}.json', 'w') as f:
        json.dump(cli, f)

def handle(client):
    sf.clients = clients
    while True:
        #saveData(client)
        sf.canSend = True
        try:
            message = decrypt(clients[client].privKey, client.recv(2048)).strip()
            if not settings['Formating']:
                message = sf.removeFormat(message)
            if message == '':
                continue
            sf.log(clients[client].displayNick, message)
            sendToAll((client, message))
            if sf.canSend:
                if message[0:1] == '/':
                    com = str(message[1:]).split(' ')
                    if com[0] == 'admin' and not clients[client].admin and len(com) == 2:
                        sf.log('debug', com[1] + ' ' + settings['Password'])
                        if com[1] == settings['Password']:
                            clients[client].admin = True
                            saveData(client)
                            client.send(encrypt(clients[client].pubKey, "<server -> me> Successfully"))
                        else:
                            client.send(encrypt(clients[client].pubKey, "<server -> me> Unsuccessfully"))

                    elif com[0] == 'admin' and clients[client].admin and len(com) == 2:
                            for cl in clients:
                                if clients[cl].displayNick == com[1]:
                                    clients[cl].admin = True
                                    saveData(cl)
                                    client.send(encrypt(clients[client].pubKey, "<server -> me> Successfully"))
                                    break
                            client.send(encrypt(clients[client].pubKey, "<server -> me> Unsuccessfully"))
                            
                    elif com[0] == 'unadmin' and clients[client].admin and len(com) == 2:
                            for cl in clients:
                                if clients[cl].displayNick == com[1]:
                                    clients[cl].admin = False
                                    saveData(cl)
                                    client.send(encrypt(clients[client].pubKey, "<server -> me> Successfully"))
                                    break
                            client.send(encrypt(clients[client].pubKey, "<server -> me> Unsuccessfully"))

                    elif com[0] == 'nick' and clients[client].admin and len(com) == 3:
                        sf.log('debug', clients)
                        for cl in clients:
                            if clients[cl].displayNick == com[1]:
                                clients[cl].displayNick = com[2]
                                sf.log('debug', f'send "nick" to {clients[client].displayNick}')
                                client.send(encrypt(clients[cl].pubKey, f"<server -> me> nickname of {com[1]} set to {com[2]}"))
                                sf.broadcast(f"{com[1]} is now {com[2]}")
                                saveData(cl)
                                break

                    elif com[0] == 'kick' and clients[client].admin and len(com) >= 2:
                        sf.log('debug', 'start search name')
                        for cl in clients:
                            sf.log('debug', clients[cl].displayNick)
                            if clients[cl].displayNick == sf.listJoin(com[1:]) and clients[cl].addr != settings['IPhost']:
                                sf.log('debug','Found ' + clients[cl].displayNick)
                                cl.send(encrypt(clients[cl].pubKey, f"<server -> me> You were kicked by {clients[client].displayNick}."))
                                cl.close()
                                clients.pop(cl)
                                sf.broadcast(f"{clients[cl].displayNick} kicked by {clients[client].displayNick}.")
                                break

                    elif com[0] == 'ban' and clients[client].admin and len(com) >= 2:
                        sf.log('debug', 'start search name')
                        
                        for cl in clients:
                            sf.log('debug', clients[cl].displayNick)
                            if clients[cl].displayNick == sf.listJoin(com[1:]) and clients[cl].addr != settings['IPhost']:
                                sf.log('debug','Found ' + clients[cl].displayNick)
                                sf.banNick(clients[cl].nickname)
                                cl.send(encrypt(clients[cl].pubKey, f"<server -> me> You were banned by {clients[client].displayNick}."))
                                cl.close()
                                clients.pop(cl)
                                sf.broadcast(f"{clients[cl].displayNick} banned by {clients[client].displayNick}.")
                                break

                    elif com[0] == 'banip' and clients[client].admin and len(com) == 2:
                        sf.banIP(com[1])
                        for cl in clients:
                            sf.log('debug', clients[cl].displayNick)
                            if clients[cl].addr == com[1]  and clients[cl].addr != settings['IPhost']:
                                sf.log('debug','Found ' + clients[cl].displayNick)
                                cl.send(encrypt(clients[cl].pubKey, f"<server -> me> You were banned by {clients[client].displayNick}."))
                                cl.close()
                                clients.pop(cl)
                                sf.broadcast(f"{clients[cl].displayNick} banned by {clients[client].displayNick}.")
                                break

                    elif com[0] == 'unban' and clients[client].admin and len(com) >= 2:
                        try:
                            sf.unbanNick(sf.listJoin(com[1:]))
                        except:
                            pass

                    elif com[0] == 'unbanip' and clients[client].admin and len(com) == 2:
                        try:
                            sf.unbanIP(com[1])
                        except:
                            pass

                    elif com[0] == 'dm' and len(com) >= 3:
                        sf.log('debug', f'dm from {clients[client].displayNick} to {com[1]}: {sf.listJoin(com[2:])}')
                        for cl in clients:
                            if clients[cl].displayNick == com[1]:
                                client.send(encrypt(clients[client].pubKey, f"<me -> {com[1]}> {sf.listJoin(com[2:])}"))
                                cl.send(encrypt(clients[cl].pubKey, f"<{clients[client].displayNick} -> me> {sf.listJoin(com[2:])}"))
                                break

                    elif com[0] == 'me' and len(com) >= 2:
                        sf.log('debug', f'me from {clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        sf.broadcast(f"*{clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))}")

                    elif com[0] == 'try' and len(com) >= 2:
                        sf.log('debug', f'try from {clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        tr = bool(random.randint(0,1))
                        if tr:
                            sf.broadcast(f"*{clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))} &2(Successfully)&r")
                        else:
                            sf.broadcast(f"*{clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))} &4(Unsuccessfully)&r")

                    elif com[0] == 'do' and len(com) >= 2:
                        sf.log('debug', f'do from {clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        sf.broadcast(f"*{sf.removeFormat(sf.listJoin(com[1:]))} &7({clients[client].displayNick})&r")

                    elif com[0] == 'list' and len(com) == 1:
                        sf.log('debug', f'send list to {clients[client].displayNick}')
                        text = "<server -> me> list of connected users:"
                        for cl in clients:
                            if clients[cl].admin:
                                text = text + f'\na {clients[cl].displayNick} > {clients[cl].addr}'
                            else:
                                text = text + f'\n- {clients[cl].displayNick} > {clients[cl].addr}'
                        client.send(encrypt(clients[client].pubKey, text))

                    elif com[0] == 'color' and clients[client].admin and len(com) >= 3:
                        col = sf.removeFont(com[1][0:2])
                        for cl in clients:
                            if clients[cl].displayNick == com[1]:
                                clients[cl].color = col
                                saveData(cl)
                                break

                    elif com[0] == 'color' and len(com) == 2:
                        col = sf.removeFont(com[1][0:2])
                        clients[client].color = col
                        saveData(client)
                    
                    elif com[0] == 'prefix' and clients[client].admin and len(com) >= 3:
                        for cl in clients:
                            if clients[cl].displayNick == com[1]:
                                clients[cl].prefix = sf.removeFont(sf.listJoin(com[2:]))
                                if sf.removeFont(sf.listJoin(com[2:])) == '' or sf.removeFont(sf.listJoin(com[2:])) == 'remove':
                                    clients[cl].prefix = None
                                saveData(cl)
                                break

                    elif com[0] == 'prefix' and len(com) >= 2:
                        clients[client].prefix = sf.removeFont(sf.listJoin(com[1:]))
                        if sf.removeFont(sf.listJoin(com[1:])) == '' or sf.removeFont(sf.listJoin(com[1:])) == 'remove':
                            clients[client].prefix = None
                        saveData(client)
                    

                    elif com[0] == 'help' and len(com) == 1:
                        sf.log('debug', f'send help to {clients[client].displayNick}')
                        client.send(encrypt(clients[client].pubKey, """<server -> me> help:
\t/dm [nick] [message]
\t/me [message]
\t/do [message]
\t/try [message]
\t/help
\t/color [formatColor] [nick?]
\t/prefix [nick?] [prefix or 'remove']
\t/list"""))
                        if clients[client].admin:
                            client.send(encrypt(clients[client].pubKey, """\t/kick [nick]
\t/ban [nick]
\t/banip [nick]
\t/unban [nick]
\t/unbanip [nick]
\t/admin [nick]"""))

                else:
                    if sf.canSend:
                        mess = message
                        mess = f'<{clients[client].color}{clients[client].displayNick}&r> ' + message
                        if clients[client].prefix:
                            mess = f'[{clients[client].prefix}&r] ' + mess
                        if clients[client].admin:
                            mess = '[&cAdmin&r] ' + mess
                        sf.broadcast(mess)
                    sf.canSend = True
        except Exception as ex:
            try:
                nk = clients[client].displayNick
                clients.pop(client)
                client.close()
                sf.broadcast(f"{nk} disconnected :(")
            except:
                pass
            try:
                sf.log("debug", f"{nk} disconnected.")
            except:
                sf.log("debug", f"disconnected.")
            sf.log("debug", ex)
            break

def stop():
    sf.log("server", "server stoped.")
    server.close()
    exit(0)

def receive():
    while True:
        try:
            client, addr = server.accept()
            getReady = client.recv(2048).decode('utf-8')
            if getReady == 'COM:READY':
                
                
                #gen key pairs
                privKey = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
                
                
                #send server pub key
                client.send('COM:SERVERPUB'.encode('utf-8'))
                getReady = client.recv(2048).decode('utf-8')
                sf.log("debug", f"{addr[0]}: send server pub key...")
                if getReady == 'COM:READYSERVERPUB':
                    pub = privKey.public_key()
                    pem = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo)
                    client.send(pem)
                    sf.log("debug", f"{addr[0]}: send server pub key --> +")
                else:
                    client.close()
                    sf.log("debug", f"{addr[0]}: send server pub key --> -")
                    continue


                #get client pub key
                getReady = client.recv(2048).decode('utf-8')
                sf.log("debug", f"{addr[0]}: get client pub key...")
                if getReady == 'COM:CLIENTPUB':
                    client.send('COM:READYCLIENTPUB'.encode('utf-8'))
                    pubKey = client.recv(2048)
                    pubKey = serialization.load_pem_public_key( pubKey, backend=default_backend() )
                    sf.log("debug", f"{addr[0]}: get client pub key --> +")
                else:
                    client.close()
                    sf.log("debug", f"{addr[0]}: get client pub key --> -")
                    continue


                #nick
                client.send("COM:NICK".encode('utf-8'))
                nickname = client.recv(2048).decode('utf-8')
                

                
                nick = sf.prepareNick(nickname)
                if not settings['FormatingNick']:
                    nick = sf.removeFormat(nick)

                if sf.getBan(nick, addr[0]):
                    client.send(encrypt(pubKey, '<server -> me> You were banned from this server.'))
                    client.close()
                    continue

                clients[client] = User(nick, addr[0], pubKey, privKey)
                sf.addUser(client, nick, addr[0], pubKey, privKey)
                sendToAll((client, nick, addr[0]), "new user")
                
                loadData(client)
                saveData(client)

                sf.log("server", f"Connected with: {str(addr[0])} and with nickname: {clients[client].displayNick}({clients[client].nickname}).")

                thread = th.Thread(target=handle, args=(client,))
                thread.start()
                
                sf.broadcast(f"{clients[client].displayNick} connected! Have fun :)")
            else:
                client.close()
        except Exception as ex:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            print(str(ex))
        



sf.log("server", "server started.")
sf.log("server",  f"work at {settings['IPhost']}@{settings['PortHost']}.")

receive()
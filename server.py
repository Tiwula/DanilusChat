import random
import socket
import threading as th
import json
from rich.console import Console
from datetime import datetime as dt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import sys, traceback, os


con = Console()

d = dt.now() 
try:
    os.mkdir('logs')
except:
    pass
logname = d.strftime('logs\\server_%d-%m-%Y_%H.%M.%S.log')

settings = {}
try:
    f = open('server-cfg.json')
    settings = json.load(f)
    f.close()
except:
    f = open('server-cfg.json', 'w')
    f.write(
"""{
	"IPhost": "127.0.0.1",
	"PortHost": 9574,
	"Password": 1234,
	"Debug": true,
	"Formating": true,
	"FormatingNick": true,
	"MultiAccount": true
}""")
    f.close()
    quit()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((settings['IPhost'], settings['PortHost']))

server.listen()

clients = {}
banIpList = []
banNickList = []


class User:
    def __init__(self, nickname, addr, pubKey, privKey, admin=False, prefix=None, color='&r'):
        self.nickname = nickname
        self.admin = admin
        self.addr = addr
        self.pubKey = pubKey
        self.privKey = privKey
        self.prefix = prefix
        self.color = color

def log(fro, message):
    if fro != 'debug' or fro == 'debug' and settings['Debug']:
        d = dt.now()
        newd = d.strftime('[%d-%m-%Y %H:%M:%S]')
        f = open(logname, 'a')
        f.write(f'{newd} <{fro}> {message}' + '\n')
        con.print(f'[cyan bold]{newd}[/] [yellow bold]<{fro}>[/] {message}')
        f.close()

def broadcast(message) -> None:
    log('debug', f'broadcast started > {message}')
    for client in clients:
        client.send(encrypt(clients[client].pubKey, message))

def removeFormat(text):
    txt = str(text)
    flist = [ '&0', '&1', '&2', '&3', '&4', '&5', '&6', '&7', '&8', '&9', '&a', '&b', '&c', '&d', '&e', '&f', '&n', '&m', '&l', '&o', '&r' ]
    for i in flist:
        txt = txt.replace(i, '')
    return txt

def removeFont(text):
    txt = str(text)
    flist = [ '&n', '&m', '&l', '&o' ]
    for i in flist:
        txt = txt.replace(i, '')
    return txt


def listJoin(org_list, seperator=' ') -> str:
    return seperator.join(org_list)

def encrypt(pubKey ,message) -> str:
    message = str(message).encode('utf-8')
    return  pubKey.encrypt(message, padding.OAEP
                    (mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    )
def decrypt(privKey, message) -> bytes:
    return  privKey.decrypt(message, padding.OAEP(
                    mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    ).decode('utf-8')

def handle(client):
    while True:
        try:
            message = decrypt(clients[client].privKey, client.recv(2048)).strip()
            if not settings['Formating']:
                message = removeFormat(message)
            if message == '':
                continue
            log(clients[client].nickname, message)
            if message[0:1] == '/':
                com = str(message[1:]).split(' ')
                if com[0] == 'admin' and not clients[client].admin and len(com) == 2:
                    if com[1] == settings['Password']:
                        clients[client].admin = True
                        client.send(encrypt(clients[client].pubKey, "<server -> me> Successfully"))
                    else:
                        client.send(encrypt(clients[client].pubKey, "<server -> me> Unsuccessfully"))

                elif com[0] == 'admin' and clients[client].admin and len(com) == 2:
                        for cl in clients:
                            if clients[cl].nickname == com[1]:
                                clients[cl].admin = True
                                client.send(encrypt(clients[client].pubKey, "<server -> me> Successfully"))
                            else: 
                                client.send(encrypt(clients[client].pubKey, "<server -> me> Unsuccessfully"))

                elif com[0] == 'nick' and clients[client].admin and len(com) == 3:
                    log('debug', clients)
                    for cl in clients:
                        if clients[cl].nickname == com[1]:
                            clients[cl].nickname = com[2]
                            log('debug', f'send "nick" to {clients[client].nickname}')
                            client.send(encrypt(clients[client].pubKey, f"<server> nickname of {com[1]} set to {com[2]}"))
                            broadcast(f"{com[1]} is now {com[2]}")
                            break

                elif com[0] == 'kick' and clients[client].admin and len(com) >= 2:
                    log('debug', 'start search name')
                    for cl in clients:
                        log('debug', clients[cl].nickname)
                        if clients[cl].nickname == listJoin(com[1:]):
                            log('debug','Found ' + clients[cl].nickname)
                            cl.send(encrypt(clients[client].pubKey, f"<server -> me> You were kicked by {clients[client].nickname}."))
                            cl.close()
                            broadcast(f"{clients[cl].nickname} kicked by {clients[client].nickname}.")
                            break

                elif com[0] == 'ban' and clients[client].admin and len(com) >= 2:
                    log('debug', 'start search name')
                    if not listJoin(com[1:]) in banNickList: 
                        banNickList.append(listJoin(com[1:]))
                        broadcast(f"{listJoin(com[1:])} banned by {clients[client].nickname}.")
                    for cl in clients:
                        log('debug', clients[cl].nickname)
                        if clients[cl].nickname == listJoin(com[1:]):
                            log('debug','Found ' + clients[cl].nickname)
                            cl.send(encrypt(clients[client].pubKey, f"<server -> me> You were banned by {clients[client].nickname}."))
                            cl.close()
                            break

                elif com[0] == 'banip' and clients[client].admin and len(com) == 2:
                    if not com[1] in banIpList: 
                        banIpList.append(com[1])
                        broadcast(f"{clients[cl].nickname} banned by {clients[client].nickname}.")
                    for cl in clients:
                        log('debug', clients[cl].nickname)
                        if clients[cl].addr == com[1]:
                            log('debug','Found ' + clients[cl].nickname)
                            cl.send(encrypt(clients[client].pubKey, f"<server -> me> You were banned by {clients[client].nickname}."))
                            cl.close()
                            broadcast(f"{clients[cl].nickname} banned by {clients[client].nickname}.")
                            break

                elif com[0] == 'unban' and clients[client].admin and len(com) >= 2:
                    try:
                        banNickList.remove(listJoin(com[1:]))
                    except:
                        pass

                elif com[0] == 'unbanip' and clients[client].admin and len(com) == 2:
                    try:
                        banIpList.remove(com[1])
                    except:
                        pass

                elif com[0] == 'dm' and len(com) >= 3:
                    log('debug', f'dm from {clients[client].nickname} to {com[1]}: {listJoin(com[2:])}')
                    for cl in clients:
                        if clients[cl].nickname == com[1]:
                            client.send(encrypt(clients[client].pubKey, f"<me -> {com[1]}> {listJoin(com[2:])}"))
                            cl.send(encrypt(clients[cl].pubKey, f"<{clients[client].nickname} -> me> {listJoin(com[2:])}"))
                            break

                elif com[0] == 'me' and len(com) >= 2:
                    log('debug', f'me from {clients[client].nickname}: {listJoin(com[1:])}')
                    broadcast(f"*{clients[client].nickname} {removeFormat(listJoin(com[1:]))}")

                elif com[0] == 'try' and len(com) >= 2:
                    log('debug', f'try from {clients[client].nickname}: {listJoin(com[1:])}')
                    tr = bool(random.randint(0,1))
                    if tr:
                        broadcast(f"*{clients[client].nickname} {removeFormat(listJoin(com[1:]))} &2(Successfully)&r")
                    else:
                        broadcast(f"*{clients[client].nickname} {removeFormat(listJoin(com[1:]))} &4(Unsuccessfully)&r")

                elif com[0] == 'do' and len(com) >= 2:
                    log('debug', f'do from {clients[client].nickname}: {listJoin(com[1:])}')
                    broadcast(f"*{removeFormat(listJoin(com[1:]))} &7({clients[client].nickname})&r")

                elif com[0] == 'list' and len(com) == 1:
                    log('debug', f'send list to {clients[client].nickname}')
                    text = "<server -> me> list of connected users:"
                    for cl in clients:
                        if clients[cl].admin:
                            text = text + f'\na {clients[cl].nickname} > {clients[cl].addr}'
                        else:
                            text = text + f'\n- {clients[cl].nickname} > {clients[cl].addr}'
                    client.send(encrypt(clients[client].pubKey, text))

                elif com[0] == 'color' and clients[client].admin and len(com) >= 3:
                    col = removeFont(com[1][0:2])
                    for cl in clients:
                        if clients[cl].nickname == com[1]:
                            clients[cl].color = col
                            break

                elif com[0] == 'color' and len(com) == 2:
                    col = removeFont(com[1][0:2])
                    clients[client].color = col
                
                elif com[0] == 'prefix' and clients[client].admin and len(com) >= 3:
                    for cl in clients:
                        if clients[cl].nickname == com[1]:
                            clients[cl].prefix = removeFont(listJoin(com[2:]))
                            if removeFont(listJoin(com[2:])) == '' or removeFont(listJoin(com[2:])) == 'remove':
                                clients[cl].prefix = None
                            break

                elif com[0] == 'prefix' and len(com) >= 2:
                    clients[client].prefix = removeFont(listJoin(com[1:]))
                    if removeFont(listJoin(com[1:])) == '' or removeFont(listJoin(com[1:])) == 'remove':
                        clients[client].prefix = None
                

                elif com[0] == 'help' and len(com) == 1:
                    log('debug', f'send help to {clients[client].nickname}')
                    client.send(encrypt(clients[client].pubKey, """<server -> me> help:
\t/me [message]
\t/do [message]
\t/try [message]
\t/help
\t/color [foramtColor] [nick?]
\t/prefix [nick?] [prefix or 'remove']
\t/list"""))
                    if clients[client].admin:
                        client.send(encrypt(clients[client].pubKey, """/kick [nick]
\t/ban [nick]
\t/banip [nick]
\t/unban [nick]
\t/unbanip [nick]"""))

            else:
                mess = message
                mess = f'<{clients[client].color}{clients[client].nickname}&r> ' + message
                if clients[client].prefix:
                    mess = f'[{clients[client].prefix}&r] ' + mess
                if clients[client].admin:
                    mess = '[&cAdmin&r] ' + mess
                broadcast(mess)
        except Exception as ex:
            try:
                nk = clients[client].nickname
                clients.pop(client)
                client.close()
                broadcast(f"{nk} disconnected :(")
            except:
                pass
            log("debug", f"{nk} disconnected. {ex}")
            break

def stop():
    log("server", "server stoped.")
    running = False
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
                log("debug", f"{addr[0]}: send server pub key...")
                if getReady == 'COM:READYSERVERPUB':
                    pub = privKey.public_key()
                    pem = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo)
                    client.send(pem)
                    log("debug", f"{addr[0]}: send server pub key --> +")
                else:
                    client.close()
                    log("debug", f"{addr[0]}: send server pub key --> -")
                    continue


                #get client pub key
                getReady = client.recv(2048).decode('utf-8')
                log("debug", f"{addr[0]}: get client pub key...")
                if getReady == 'COM:CLIENTPUB':
                    client.send('COM:READYCLIENTPUB'.encode('utf-8'))
                    pubKey = client.recv(2048)
                    pubKey = serialization.load_pem_public_key( pubKey, backend=default_backend() )
                    log("debug", f"{addr[0]}: get client pub key --> +")
                else:
                    client.close()
                    log("debug", f"{addr[0]}: get client pub key --> -")
                    continue


                #nick
                client.send("COM:NICK".encode('utf-8'))
                nickname = client.recv(2048).decode('utf-8')
                

                if nickname in banNickList or addr[0] in banIpList:
                    client.send('<server -> me> You were banned from this server.'.encode('utf-8'))
                    client.close()
                    continue
                if not settings['FormatingNick']:
                    nick = removeFormat(nickname).replace(' ', '')
                nick = removeFont(nickname).replace(' ', '')

                clients[client] = User(nick, addr[0], pubKey, privKey)

                log("server", f"Connected with: {str(addr)} and with nick: {nickname}.")
                
                thread = th.Thread(target=handle, args=(client,))
                thread.start()
                
                broadcast(f"{nickname} connected! Have a fun :)")
            else:
                client.close()
        except Exception as ex:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            print(str(ex))
        



log("server", "server started.")
log("server",  f"work at {settings['IPhost']}@{settings['PortHost']}.")

receive()
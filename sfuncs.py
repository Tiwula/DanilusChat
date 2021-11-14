from datetime import datetime as dt
from rich.console import Console
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os

con = Console()

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

clients = {}

def addUser(client, nick, addr, pubKey, privKey):
    clients[client] = User(nick, addr, pubKey, privKey)

def getClients() -> clients:
    return clients

settings = {}

d = dt.now() 
try:
    os.mkdir('logs')
except:
    pass
logname = d.strftime('logs\\server_%d-%m-%Y_%H.%M.%S.log')

def log(fro, message) -> None:
    if fro != 'debug' or fro == 'debug' and settings['Debug']:
        d = dt.now()
        newd = d.strftime('[%d-%m-%Y %H:%M:%S]')
        f = open(logname, 'a')
        f.write(f'{newd} <{fro}> {message}' + '\n')
        con.print(f'[cyan bold]{newd}[/] [yellow bold]<{fro}>[/] {message}')
        f.close()

def encrypt(pubKey ,message) -> str:
    message = str(message).encode('utf-8')
    return  pubKey.encrypt(message, padding.OAEP
                    (mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    )
def decrypt(privKey, message) -> bytes:
    return  privKey.decrypt(message, padding.OAEP(
                    mgf=padding.MGF1( algorithm=hashes.SHA256() ), algorithm=hashes.SHA256(), label=None)
                    ).decode('utf-8')

def broadcast(message) -> None:
    log('debug', f'broadcast started > {message}')
    for client in clients:
        client.send(encrypt(clients[client].pubKey, message))

def listJoin(org_list, seperator=' ') -> str:
    return seperator.join(org_list)

def removeFormat(text) -> str:
    txt = str(text)
    flist = [ '&0', '&1', '&2', '&3', '&4', '&5', '&6', '&7', '&8', '&9', '&a', '&b', '&c', '&d', '&e', '&f', '&n', '&m', '&l', '&o', '&r' ]
    for i in flist:
        txt = txt.replace(i, '')
    return txt

def prepareNick(text) -> str:
    txt = str(text)
    flist = [ ' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|' ]
    for i in flist:
        txt = txt.replace(i, '')
    return txt

def removeFont(text) -> str:
    txt = str(text)
    flist = [ '&n', '&m', '&l', '&o' ]
    for i in flist:
        txt = txt.replace(i, '')
    return txt

def banNick(nick) -> None:
    f = open('bannick-list.txt')
    text = f.read()
    f.close()
    curList = text.split('\n')
    if not nick in curList:
        f = open(open('bannick-list.txt', 'a'))
        f.write(nick + '\n')
        f.close()

def banIP(ip) -> None:
    f = open('banip-list.txt')
    text = f.read()
    f.close()
    curList = text.split('\n')
    if not ip in curList:
        f = open(open('banip-list.txt', 'a'))
        f.write(ip + '\n')
        f.close()

def unbanNick(nick) -> None:
    f = open('bannick-list.txt')
    text = f.read()
    f.close()
    curList = text.split('\n')
    if nick in curList:
        curList.remove(nick)
        textToWrite = listJoin(curList, '\n')
        f = open(open('bannick-list.txt', 'w'))
        f.write(textToWrite)
        f.close()

def unbanIP(ip) -> None:
    f = open('banip-list.txt')
    text = f.read()
    f.close()
    curList = text.split('\n')
    if ip in curList:
        curList.remove(ip)
        textToWrite = listJoin(curList, '\n')
        f = open(open('banip-list.txt', 'w'))
        f.write(textToWrite)
        f.close()
    

def send(client, message):
    client.send(encrypt(clients[client].pubKey, message))
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

def send(client, message):
    client.send(encrypt(clients[client].pubKey, message))
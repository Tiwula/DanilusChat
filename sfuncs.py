import functools
from datetime import datetime as dt
from rich.console import Console
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
import json
import typing

con = Console()

def getID():
    count = 0
    for i in os.listdir('userdata'):
        if i[len(i)-5:] == ".json":
            count += 1
    return count

class User:
    def __init__(self, nickname, addr, pubKey, privKey, admin=False, prefix=None, color='&r', id=None):
        if id:
            self.id = id
        else:
            self.id = getID()
        self.nickname = nickname
        self.admin = admin
        self.addr = addr
        self.pubKey = pubKey
        self.privKey = privKey
        self.prefix = prefix
        self.color = color
        self.displayNick = nickname


class PluginError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Plugin:
    def __init__(self, name: str, author: str, version: str):
        self.name = name
        self.author = author
        self.version = version
        self.commands = []
        self.events = {}

    def get_data(self):
        return {"name": self.name, "author": self.author, "version": self.version}

    def get_commands(self):
        return self.commands

    def command(self, name: str, description: str):
        if " " in name:
            raise PluginError('Can\'t use spaces in command name')

        def command_decorator(func):
            log(self.name, "Added command " + name)
            self.commands.append({"name": name, "description": description, "callback": func})
        return command_decorator

    def set_callback(self, func: typing.Callable, cb: str):
        cblist = ['init', 'newUser', 'receive']
        if cb not in cblist:
            raise PluginError('Unknown callback! Correct callbacks: ' + cblist)
        self.events[cb] = func


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


def encrypt(pubKey, message) -> str:
    message = str(message).encode('utf-8')
    return pubKey.encrypt(message, padding.OAEP
    (mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                          )


def decrypt(privKey, message) -> bytes:
    return privKey.decrypt(message, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                           ).decode('utf-8')


def broadcast(message) -> None:
    log('debug', f'broadcast started > {message}')
    for client in clients:
        client.send(encrypt(clients[client].pubKey, message))


def listJoin(org_list, seperator=' ') -> str:
    return seperator.join(org_list)


def removeFormat(text) -> str:
    txt = str(text)
    flist = ['&0', '&1', '&2', '&3', '&4', '&5', '&6', '&7', '&8', '&9', '&a', '&b', '&c', '&d', '&e', '&f', '&n', '&m',
             '&l', '&o', '&r']
    for i in flist:
        txt = txt.replace(i, '')
    return txt


def prepareNick(text) -> str:
    txt = str(text)
    flist = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for i in flist:
        txt = txt.replace(i, '')
    return txt


def removeFont(text) -> str:
    txt = str(text)
    flist = ['&n', '&m', '&l', '&o']
    for i in flist:
        txt = txt.replace(i, '')
    return txt


def banNick(nick) -> None:
    text = ""
    try:
        f = open('bannick-list.txt')
        text = f.read()
        f.close()
    except:
        pass
    curList = text.split('\n')
    if not nick in curList:
        f = open('bannick-list.txt', 'a')
        f.write(nick + '\n')
        f.close()


def banIP(ip) -> None:
    text = ""
    try:
        f = open('banip-list.txt')
        text = f.read()
        f.close()
    except:
        pass
    curList = text.split('\n')
    if not ip in curList:
        f = open('banip-list.txt', 'a')
        f.write(ip + '\n')
        f.close()


def unbanNick(nick) -> None:
    text = ""
    try:
        f = open('bannick-list.txt')
        text = f.read()
        f.close()
    except:
        pass
    curList = text.split('\n')
    if nick in curList:
        curList.remove(nick)
        textToWrite = listJoin(curList, '\n')
        f = open('bannick-list.txt', 'w')
        f.write(textToWrite)
        f.close()


def unbanIP(ip) -> None:
    text = ""
    try:
        f = open('banip-list.txt')
        text = f.read()
        f.close()
    except:
        pass
    curList = text.split('\n')
    if ip in curList:
        curList.remove(ip)
        textToWrite = listJoin(curList, '\n')
        f = open('banip-list.txt', 'w')
        f.write(textToWrite)
        f.close()


def getBan(nick, addr) -> bool:
    text = []
    ret = False
    try:
        with open('banip-list.txt', 'r') as f:
            text = f.read().split('\n')
    except:
        pass
    if addr in text:
        ret = True

    try:
        with open('bannick-list.txt', 'r') as f:
            text = f.read().split('\n')
    except:
        pass
    if nick in text:
        ret = True

    return ret


def loadData(client):
    back = clients[client]
    try:
        f = open(f'userdata\\{clients[client].addr} {clients[client].nickname}.json', 'r')
        cli = json.load(f)
        clients[client].id = cli['id']
        clients[client].displayNick = cli['displayNick']
        clients[client].admin = cli['admin']
        clients[client].prefix = cli['prefix']
        clients[client].color = cli['color']
    except Exception as ex:
        clients[client] = back
        log('server', f"Error loading data for user {clients[client].displayNick}.")
        log('server', ex)


def saveData(client):
    cli = {}
    cli['id'] = clients[client].id
    cli['addr'] = clients[client].addr
    cli['nickname'] = clients[client].nickname
    cli['admin'] = clients[client].admin
    cli['prefix'] = clients[client].prefix
    cli['color'] = clients[client].color
    cli['displayNick'] = clients[client].displayNick
    with open(f'userdata\\{clients[client].addr} {clients[client].nickname}.json', 'w') as f:
        json.dump(cli, f)


def dump(f):
    dat = globals()
    for i in dat:
        f.write(str(i) + "\t\t = \t" + str(dat[i]) + "\n")


def send(client, message):
    client.send(encrypt(clients[client].pubKey, message))
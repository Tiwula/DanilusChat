import random
import socket
import threading as th
import json
from datetime import datetime as dt
from rich.console import Console
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import sys, traceback, importlib, os, requests
import sfuncs as sf


con = Console()


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

try:
    os.mkdir('plugins')
except:
    pass

try:
    os.mkdir('userdata')
except:
    pass

plugmodules = {}
pluglist = []
plfiles = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
for i in plfiles:
    if i[len(i)-3:] == ".py":
        try:
            plugname = i[:-3]
            plugmodules[i] = importlib.import_module('plugins.' + plugname)
            try:
                plugdata = plugmodules[i].plugin.get_data()
                pluglist.append(plugdata)
            except Exception as exc:
                sf.log("plugins", "Error while trying to load plugin data of " + i)
                sf.log("plugins", exc)
                pass
        except Exception as exc:
            sf.log("plugins", "Error while trying to import plugin " + i)
            sf.log("plugins", exc)
            pass


for i in plugmodules:
    try:
        plugmodules[i].plugin.events["init"]()
    except AttributeError:
        pass
    except Exception as ex:
        sf.log('debug', 'Error loading plugin ' + i)
        sf.log('debug', ex)


def sendToAll(data, event="receive message") -> None:
    if event == "receive message":
        for i in plugmodules:
            try:
                plugmodules[i].plugin.events["receive"](data)
            except AttributeError:
                pass
            except Exception as ex:
                sf.log('debug', 'Error execute plugin callback')
                sf.log('debug', ex)
    elif event == "new user":
        for i in plugmodules:
            try:
                plugmodules[i].plugin.events["newUser"](data)
            except AttributeError:
                pass
            except Exception as ex:
                sf.log('debug', 'Error execute plugin callback ' + i)
                sf.log('debug', ex)


def encrypt(pubKey, message) -> str:
    message = str(message).encode('utf-8')
    return pubKey.encrypt(message, padding.OAEP
    (mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                          )


def decrypt(privKey, message) -> bytes:
    return privKey.decrypt(message, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                           ).decode('utf-8')


def dump(prefix='def'):
    d = dt.now()
    dumpName = d.strftime('logs\\dump_' + prefix + '_%d-%m-%Y_%H.%M.%S.log')
    dat = globals()
    with open(dumpName, 'w') as f:
        f.write('--------MAIN--------\n\n')
        for i in dat:
            f.write(str(i) + "\t\t = \t" + str(dat[i]) + "\n")
        f.write('--------SF--------\n\n')
        sf.dump(f)


def handle(client):
    while True:
        # saveData(client)
        sf.canSend = True
        try:
            message = decrypt(sf.clients[client].privKey, client.recv(2048)).strip()
            if not settings['Formating']:
                message = sf.removeFormat(message)
            if message == '':
                continue
            sf.log(sf.clients[client].displayNick, message)
            sendToAll((client, message))
            if sf.canSend:
                if message[0:1] == '/':
                    com = str(message[1:]).split(' ')

                    for pl in plfiles:
                        for plcmd in plugmodules[pl].plugin.get_commands():
                            if com[0] == plcmd["name"]:
                                args = [i for i in com[1:] if len(com) > 1]
                                plcmd["callback"](args, client)

                    if com[0] == 'admin' and not sf.clients[client].admin and len(com) == 2:
                        sf.log('debug', com[1] + ' ' + settings['Password'])
                        if com[1] == settings['Password']:
                            sf.clients[client].admin = True
                            sf.saveData(client)
                            client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Successfully"))
                        else:
                            client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Unsuccessfully"))

                    elif com[0] == 'admin' and sf.clients[client].admin and len(com) == 2:
                        ok = False
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1]:
                                sf.clients[cl].admin = True
                                sf.saveData(cl)
                                client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Successfully"))
                                ok = True
                                break
                        if ok == False:
                            client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Unsuccessfully"))

                    elif com[0] == 'unadmin' and sf.clients[client].admin and len(com) == 2:
                        ok = False
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1]:
                                sf.clients[cl].admin = False
                                sf.saveData(cl)
                                client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Successfully"))
                                ok = True
                                break
                        if ok == False:
                            client.send(encrypt(sf.clients[client].pubKey, "<server -> me> Unsuccessfully"))

                    elif com[0] == 'nick' and sf.clients[client].admin and len(com) == 3:
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1]:
                                oldNick = sf.clients[cl].displayNick
                                sf.clients[cl].displayNick = com[2]
                                sf.log('debug', f'send "nick" to {sf.clients[client].displayNick}')
                                client.send(encrypt(sf.clients[client].pubKey,
                                                    f"<server -> me> nickname of {oldNick} set to {com[2]}."))
                                sf.broadcast(f"{oldNick} is now {com[2]}.")
                                sf.saveData(cl)
                                dump('nick')
                                break

                    elif com[0] == 'kick' and sf.clients[client].admin and len(com) == 2:
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1] and sf.clients[cl].addr != settings['IPhost']:
                                nick = sf.clients[cl].displayNick
                                nick2 = sf.clients[client].displayNick
                                sf.log('debug', 'Found ' + sf.clients[cl].displayNick)
                                cl.send(encrypt(sf.clients[cl].pubKey,
                                                f"<server -> me> You were kicked by {sf.clients[client].displayNick}."))
                                cl.close()
                                sf.clients.pop(cl)
                                sf.broadcast(f"{nick} kicked by {nick2}.")
                                dump('kick')
                                break

                    elif com[0] == 'ban' and sf.clients[client].admin and len(com) == 2:
                        for cl in sf.clients:
                            if sf.clients[cl].nickname == com[1] and sf.clients[cl].addr != settings['IPhost']:
                                nick = sf.clients[cl].displayNick
                                nick2 = sf.clients[client].displayNick
                                sf.log('debug', 'Found ' + sf.clients[cl].displayNick)
                                sf.banNick(sf.clients[cl].nickname)
                                cl.send(encrypt(sf.clients[cl].pubKey,
                                                f"<server -> me> You were banned by {sf.clients[client].displayNick}."))
                                cl.close()
                                sf.clients.pop(cl)
                                sf.broadcast(f"{nick} banned by {nick2}.")
                                break

                    elif com[0] == 'banip' and sf.clients[client].admin and len(com) == 2:
                        if settings['IPhost'] == com[1]:
                            continue
                        sf.banIP(com[1])
                        for cl in sf.clients:
                            if sf.clients[cl].addr == com[1]:
                                nick = sf.clients[cl].displayNick
                                nick2 = sf.clients[client].displayNick
                                sf.log('debug', 'Found ' + sf.clients[cl].displayNick)
                                cl.send(encrypt(sf.clients[cl].pubKey,
                                                f"<server -> me> You were banned by {sf.clients[client].displayNick}."))
                                cl.close()
                                sf.clients.pop(cl)
                                sf.broadcast(f"{nick} banned by {nick2}.")
                                break

                    elif com[0] == 'unban' and sf.clients[client].admin and len(com) == 2:
                        try:
                            sf.unbanNick(com[1])
                        except:
                            pass

                    elif com[0] == 'unbanip' and sf.clients[client].admin and len(com) == 2:
                        try:
                            sf.unbanIP(com[1])
                        except:
                            pass

                    elif com[0] == 'dm' and len(com) >= 3:
                        sf.log('debug', f'dm from {sf.clients[client].displayNick} to {com[1]}: {sf.listJoin(com[2:])}')
                        for cl in sf.clients:
                            if sf.clients[cl].displayNick == com[1]:
                                client.send(
                                    encrypt(sf.clients[client].pubKey, f"<me -> {com[1]}> {sf.listJoin(com[2:])}"))
                                cl.send(encrypt(sf.clients[cl].pubKey,
                                                f"<{sf.clients[client].displayNick} -> me> {sf.listJoin(com[2:])}"))
                                break

                    elif com[0] == 'me' and len(com) >= 2:
                        sf.log('debug', f'me from {sf.clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        sf.broadcast(f"*{sf.clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))}")

                    elif com[0] == 'try' and len(com) >= 2:
                        sf.log('debug', f'try from {sf.clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        tr = bool(random.randint(0, 1))
                        if tr:
                            sf.broadcast(
                                f"*{sf.clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))} &2(Successfully)&r")
                        else:
                            sf.broadcast(
                                f"*{sf.clients[client].displayNick} {sf.removeFormat(sf.listJoin(com[1:]))} &4(Unsuccessfully)&r")

                    elif com[0] == 'do' and len(com) >= 2:
                        sf.log('debug', f'do from {sf.clients[client].displayNick}: {sf.listJoin(com[1:])}')
                        sf.broadcast(f"*{sf.removeFormat(sf.listJoin(com[1:]))} &7({sf.clients[client].displayNick})&r")

                    elif com[0] == 'list' and len(com) == 1:
                        sf.log('debug', f'send list to {sf.clients[client].displayNick}')
                        text = "<server -> me> list of connected users:"
                        for cl in sf.clients:
                            if sf.clients[cl].admin:
                                text = text + f'\na [{str(sf.clients[cl].id)}] {sf.clients[cl].displayNick} ({sf.clients[cl].nickname}) > {sf.clients[cl].addr}'
                            else:
                                text = text + f'\n- [{str(sf.clients[cl].id)}] {sf.clients[cl].displayNick} ({sf.clients[cl].nickname}) > {sf.clients[cl].addr}'
                        client.send(encrypt(sf.clients[client].pubKey, text))

                    elif com[0] == 'color' and sf.clients[client].admin and len(com) == 3:
                        col = sf.removeFont(com[2][0:2])
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1]:
                                if col == '':
                                    sf.clients[cl].color = '&r'
                                else:
                                    sf.clients[cl].color = col
                                sf.saveData(cl)
                                break

                    elif com[0] == 'color' and len(com) == 2:
                        col = sf.removeFont(com[1][0:2])
                        if col == '':
                            sf.clients[client].color = '&r'
                        else:
                            sf.clients[client].color = col
                        sf.saveData(client)

                    elif com[0] == 'prefix' and sf.clients[client].admin and len(com) >= 3:
                        for cl in sf.clients:
                            if str(sf.clients[cl].id) == com[1]:
                                sf.clients[cl].prefix = sf.removeFont(sf.listJoin(com[2:]))
                                if sf.removeFont(sf.listJoin(com[2:])) == '' or sf.removeFont(
                                        sf.listJoin(com[2:])) == 'remove':
                                    sf.clients[cl].prefix = None
                                sf.saveData(cl)
                                break

                    elif com[0] == 'prefix' and len(com) >= 2:
                        sf.clients[client].prefix = sf.removeFont(sf.listJoin(com[1:]))
                        if sf.removeFont(sf.listJoin(com[1:])) == '' or sf.removeFont(sf.listJoin(com[1:])) == 'remove':
                            sf.clients[client].prefix = None
                        sf.saveData(client)

                    elif com[0] == 'dump' and sf.clients[client].admin:
                        dump('command by ' + sf.clients[client].displayName)

                    elif com[0] == 'help' and len(com) == 1:
                        sf.log('debug', f'send help to {sf.clients[client].displayNick}')
                        client.send(encrypt(sf.clients[client].pubKey, """<server -> me> help:
\t/dm [nick] [message]
\t/me [message]
\t/do [message]
\t/try [message]
\t/help
\t/color [formatColor]
\t/prefix [prefix or 'remove']
\t/list"""))
                        if sf.clients[client].admin:
                            client.send(encrypt(sf.clients[client].pubKey, """\t/kick [id]
\t/color [id?] [formatColor]
\t/prefix [id?] [prefix or 'remove']
\t/ban [nick]
\t/banip [ip]
\t/unban [nick]
\t/unbanip [ip]
\t/admin [id]
\t/unadmin [id]
\t/nick [id] [newNick]"""))

                else:
                    if sf.canSend:
                        mess = message
                        mess = f'<{sf.clients[client].color}{sf.clients[client].displayNick}&r> ' + message
                        if sf.clients[client].prefix:
                            mess = f'[{sf.clients[client].prefix}&r] ' + mess
                        if sf.clients[client].admin:
                            mess = '[&cAdmin&r] ' + mess
                        sf.broadcast(mess)
                    sf.canSend = True
        except Exception as ex:
            try:
                nk = sf.clients[client].displayNick
                sf.clients.pop(client)
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

                # gen key pairs
                privKey = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

                # send server pub key
                client.send('COM:SERVERPUB'.encode('utf-8'))
                getReady = client.recv(2048).decode('utf-8')
                sf.log("debug", f"{addr[0]}: send server pub key...")
                if getReady == 'COM:READYSERVERPUB':
                    pub = privKey.public_key()
                    pem = pub.public_bytes(encoding=serialization.Encoding.PEM,
                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
                    client.send(pem)
                    sf.log("debug", f"{addr[0]}: send server pub key --> [green]+[/]")
                else:
                    client.close()
                    sf.log("debug", f"{addr[0]}: send server pub key --> [red]-[/]")
                    continue

                # get client pub key
                getReady = client.recv(2048).decode('utf-8')
                sf.log("debug", f"{addr[0]}: get client pub key...")
                if getReady == 'COM:CLIENTPUB':
                    client.send('COM:READYCLIENTPUB'.encode('utf-8'))
                    pubKey = client.recv(2048)
                    pubKey = serialization.load_pem_public_key(pubKey, backend=default_backend())
                    sf.log("debug", f"{addr[0]}: get client pub key --> [green]+[/]")
                else:
                    client.close()
                    sf.log("debug", f"{addr[0]}: get client pub key --> [red]-[/]")
                    continue

                # nick
                client.send("COM:NICK".encode('utf-8'))
                nickname = client.recv(2048).decode('utf-8')

                nick = sf.prepareNick(nickname)
                if not settings['FormatingNick']:
                    nick = sf.removeFormat(nick)

                if sf.getBan(nick, addr[0]):
                    client.send(encrypt(pubKey, '<server -> me> You were banned from this server.'))
                    client.close()
                    continue

                sf.addUser(client, nick, addr[0], pubKey, privKey)
                sendToAll((client, nick, addr[0]), "new user")

                sf.loadData(client)
                sf.saveData(client)

                sf.log("server",
                       f"Connected with: {str(addr[0])} and with nickname: [{sf.clients[client].id}] {sf.clients[client].displayNick}({sf.clients[client].nickname}).")

                thread = th.Thread(target=handle, args=(client,))
                thread.start()

                sf.broadcast(f"{sf.clients[client].displayNick} connected! Have fun :)")
            else:
                client.close()
        except Exception as ex:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            print(str(ex))


sf.log("server", "server started.")
sf.log("server", f"work at {settings['IPhost']}@{settings['PortHost']}.")

receive()
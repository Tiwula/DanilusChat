import sfuncs as sf

plugininfo = {"name": "Inventory", "author": "Danilus", "version": "1.0"}

inventory = {}

def newUser(data):
    inventory[data[0]] = []
    sf.log("inventory plugin", "New inventory created!")

def receive(data):
    client = data[0]
    message = data[1]
    clients = sf.clients
    if message[0:1] == '/':
        com = str(message[1:]).split(' ')

        if com[0] == 'give' and clients[client].admin and len(com) >= 3:
            for cl in clients:
                if clients[cl].displayNick == com[1]:
                    inventory[cl].append(sf.listJoin(com[2:]))
                    sf.log("inventory plugin", f"Give {clients[cl].displayNick} {sf.listJoin(com[2:])}")
                    break

        elif com[0] == 'take' and clients[client].admin and len(com) >= 3:
            for cl in clients:
                if clients[cl].displayNick == com[1]:
                    inventory[cl].remove(sf.listJoin(com[2:]))
                    sf.log("inventory plugin", f"Take {clients[cl].displayNick} {sf.listJoin(com[2:])}")
                    break

        elif com[0] == 'gave' and len(com) >= 3:
            if sf.listJoin(com[2:]) in inventory[client]:
                for cl in clients:
                    if clients[cl].displayNick == com[1]:
                        inventory[cl].append(sf.listJoin(com[2:]))
                        inventory[client].remove(sf.listJoin(com[2:]))
                        sf.broadcast(f'*{clients[client].displayNick} gave {sf.listJoin(com[2:])} to {clients[cl].displayNick}')
                        sf.log("inventory plugin", f"{clients[client].displayNick} gave {sf.listJoin(com[2:])} to {clients[cl].displayNick}")
                        break

        elif com[0] == 'inv' and len(com) == 1:
            text = "Inventory:"
            counter = 0
            for i in inventory[client]:
                text = text + f"\n\t[{counter+1}] {i}"
                counter+=1
            sf.send(client, text)

        elif com[0] == 'inv' and clients[client].admin and len(com) == 2:
            for cl in clients:
                if clients[cl].displayNick == com[1]:
                    text = f"{clients[cl].displayNick}'s inventory:"
                    for i in inventory[cl]:
                        text = f"\n\t{i}"
                    sf.send(client, text)
import requests
import os
import sys

# Server.py
sys.stdout.write("get server.py from https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/server.py... ")
sys.stdout.flush()
try:
    response = requests.get("https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/server.py")
    if response.text == "404: Not Found":
        print(response.text)
        input()
        exit()
    with open('server.py', 'w') as f:
        f.write(response.text)
except Exception as ex:
    print(ex)
    exit()
sys.stdout.write("Done.\n")
sys.stdout.flush()

#lib
sys.stdout.write("get sfuncs.py from https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/sfuncs.py... ")
sys.stdout.flush()
try:
    response = requests.get("https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/sfuncs.py")
    if response.text == "404: Not Found":
        print(response.text)
        input()
        exit()
    with open('sfuncs.py', 'w') as f:
        f.write(response.text)
except Exception as ex:
    print(ex)
    exit()
sys.stdout.write("Done.\n")
sys.stdout.flush()


#requirements
sys.stdout.write("get requirements.txt from https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/ServerInstaller/requirements.txt... ")
sys.stdout.flush()
try:
    response = requests.get("https://raw.githubusercontent.com/Danilus-s/DanilusChat/main/ServerInstaller/requirements.txt")
    if response.text == "404: Not Found":
        print(response.text)
        input()
        exit()
    with open('requirements.txt', 'w') as f:
        f.write(response.text)
except Exception as ex:
    print(ex)
    exit()
sys.stdout.write("Done.\n")
sys.stdout.flush()
print('')

os.system('pip3 install -r requirements.txt')

input()
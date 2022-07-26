import sfuncs as sf

plugin = sf.Plugin("ExamplePlugin", "Iriscent", "0.0.1")

pname = plugin.get_data()["name"]


@plugin.command("hi", "This is an example command")
def hi(args, cln):
    sf.log(pname, "hi command called with message " + str(args) + " by " + sf.clients[cln].nickname)


@plugin.command("anothercommand", "This is a second command, yep you can do multiple!!!!")
def cmd2(args, cln):
    sf.log(pname, sf.clients[cln].nickname + " sent anothercommand")
    sf.send(cln, "replying to command")


def init():
    sf.log(pname, "init")


def new_user(data):
    sf.log(pname, "new user")


def receive(data):
    sf.log(pname, "new message")


plugin.set_callback(init, "init")
plugin.set_callback(new_user, "newUser")
plugin.set_callback(receive, "receive")

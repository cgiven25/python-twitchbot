############################################################################
# Chris Given's Twitch Chatbot
# Last modified: 11:32 AM, 8/26/18
# Recent changelog:
#   - Timestamped messages now print to the terminal.
#   - Subscriber notifications (>=3 months so I don't get global timed out)
#   - Sends a message when someone is banned (and it's set up for timeouts)
import irc.bot
import requests
from time import gmtime, strftime

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, clientID, token, channel):
        self.client_id = clientID
        self.token = token
        self.channel = "#" + channel

        # Get the channel id for API-based functions
        url = "https://api.twitch.tv/helix/users?login={}".format(channel)
        headers = {"Client-ID": clientID}
        response = requests.get(url, headers = headers).json()
        self.channelID = response["data"][0]["id"]

        # Information for Twitch IRC server
        server = "irc.chat.twitch.tv"
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, "oauth:" + token)], username, username)

    # ========== Event Handlers ========== #
    # These handle messages from the IRC server
    # USERNOTICE: (Re)subscriptions, raids, and rituals
    # CLEARCHAT: Bans and timeouts
    # ROOMSTATE: Changes to room (slow mode, r9k, etc.)
    # HOSTTARGET: Channel hosts/unhosts
    # PUBMSG: Public message (all twitch chat msgs come here)
    # All handlers have a c (connection) and e (event) parameter.
    # The events hold important information about each message.
    # The connection is required to send messages (c.privmsg).
    def on_welcome(self, c, e):
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_usernotice(self, c, e):
        months = 0
        name = ""
        for tag in e.tags:
            if tag["key"] == "msg-param-months":
                months = int(tag["value"])
            if tag["key"] == "display-name":
                name = tag["value"]
        if months >= 3:
            print("PepoDance {} has subscribed for {} months! PepoDance".format(name, months))

    def on_clearchat(self, c, e):
        target = e.arguments[0]
        timeout = True if "ban-duration" in e.tags[0].values() else False
        if timeout:
            pass
        else:
            c.privmsg(self.channel, "{} has been obliterated.".format(target))

    def on_roomstate(self, c, e):
        pass

    def on_hosttarget(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        message = " ".join(e.arguments)
        name = e.tags[2]["value"]
        time = strftime("%H:%M:%S", gmtime())
        print(time, "-", name + ":", message)

def main():
    with open("client.txt") as cl:
        client = cl.read()
    with open("token.txt") as tok:
        token = tok.read()
    username = "codetoad"
    channel = "ninja"
    bot = Bot(username, client, token, channel)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect()
        print()
        exit()

if __name__ == "__main__":
    main()
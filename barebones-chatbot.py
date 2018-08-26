import irc.bot
import irc.events
import requests

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
        pass

    def on_clearchat(self, c, e):
        pass

    def on_roomstate(self, c, e):
        pass

    def on_hosttarget(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        pass

def main():
    with open("client.txt") as cl:
        client = cl.read()
    with open("token.txt") as tok:
        token = tok.read()
    username = "[BOT USERNAME]"
    channel = "[CHANNEL TO BOT]"
    bot = Bot(username, client, token, channel)
    bot.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit()

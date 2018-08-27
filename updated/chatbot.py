############################################################################
# Chris Given's Twitch Chatbot
# Last modified: 7:10 AM, 8/27/18
# Recent changelog:
#   - Added cooldowns for data collection and commands
#   - Added data collection intervals:
#       - Allows the game to be saved as an instance variable
#       - So when people ask for game you can prevent another API call
#   - NOTE: added dependency for schedule module
import irc.bot
import requests
from time import gmtime, strftime, time
from schedule import every, run_pending

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, clientID, token, channel):
        self.client_id = clientID
        self.token = token
        self.channel = "#" + channel
        self.game = None
        self.title = None

        self.lastCommandTime = time()
        self.commands = ["game", "ribbit",]

        # Get the channel id for API-based functions
        url = "https://api.twitch.tv/helix/users?login={}".format(channel)
        headers = {"Client-ID": clientID}
        response = requests.get(url, headers = headers).json()
        self.channelID = response["data"][0]["id"]

        # Cooldowns for certain functions
        # Data collection: Get game and title every n seconds
        #   - NOTE: You only get 30 API calls per minute without a bearer token.
        # Commands: Bot will not respond if a command has been issued in n seconds
        self.cooldowns = {"dataCollection": 60,
                          "commands": 3,}
        self.collect()
        every(self.cooldowns["dataCollection"]).seconds.do(self.collect)

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
        ban = False if "ban-duration" in e.tags[0].values() else True
        if ban:
            c.privmsg(self.channel, "{} has been obliterated.".format(target))

    def on_roomstate(self, c, e):
        pass

    def on_hosttarget(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        run_pending()
        message = " ".join(e.arguments)
        name = e.tags[2]["value"]
        currentTime = strftime("%H:%M:%S", gmtime())
        print(currentTime, "-", name + ":", message)
        if message[0] == "!" and time() - self.lastCommandTime > self.cooldowns["commands"]:
            c.privmsg(self.channel, self.do_command(e.arguments, name))

    # Collect game and title information
    # This saves it so it can be on demand when someone asks for it instead of having to wait for API calls
    # which might slow down the bot.
    def collect(self):
        response = requests.get("https://api.twitch.tv/helix/streams?user_id={}".format(self.channelID),
                                headers={"Client-ID": self.client_id}).json()
        try:
            gameID = response["data"][0]["game_id"]
            response = requests.get("https://api.twitch.tv/helix/games?id={}".format(gameID),
                                    headers={"Client-ID": self.client_id}).json()
            try:
                self.game = response["data"][0]["name"]
            except KeyError:
                self.game = "an unlisted game"
        except IndexError:
            self.game = "offline"

    # Execute a command when the first character of a chat message is "!".
    def do_command(self, arguments, name):
        command = arguments[0][1:]
        if command not in self.commands:
            return
        elif command == "ribbit":
            return "/me ribbits."
        elif command == "game":
            return "{} is playing {}.".format(self.channel[1:], self.game)
        self.lastCommandTime = time()

def main():
    with open("client.txt") as cl:
        client = cl.read()
    with open("token.txt") as tok:
        token = tok.read()
    username = "codetoad"
    channel = "codetoad"
    bot = Bot(username, client, token, channel)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect()
        print()
        exit()

if __name__ == "__main__":
    main()
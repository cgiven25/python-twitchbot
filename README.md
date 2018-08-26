# Twitch Chatbot

This is a chatbot for twitch.tv written in Python based off of the code [here](https://github.com/twitchdev/chat-samples/blob/master/python/chatbot.py) but updated for Python 3 and the New Twitch API.

## Setup
Before you can use this program, you need to make sure you have the irc and requests libraries installed.
A quick run of ```pip install requests``` and ```pip install irc``` will verify if you have them and download them if you don't.

To use chatbots on Twitch you will need a client-id (which you can get by registering an app [here](glass.twitch.tv)) and an OAuth token.  There is an official Twitch authentication process but if you want to get started quickly you can use [this third-party website.](https://twitchapps.com/tmi/)

Once all that is done, just edit the script to include your username, client id, and token.

### Notes
The original upload is a barebones, functional chatbot that connects to the IRC server and does nothing.  The methods are there and unedited for people that know what they want to do and just want a template.  I will be uploading my version while I work on it, which will be a more complete, functional chatbot.

The barebones version is compatible with Python 2 and 3, but I will not be considering Python 2 support while I write my version.  If you're still using Python 2, consider switching, because support for it will not last forever.

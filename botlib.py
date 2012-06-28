import random
from sys import argv
from os import environ

# Admin name(s) for certain commands
# Usage:
#       if sender in ADMINS:
#           myfunc()
ADMINS = ("SlimTim10", "Z_Mass")

def parsemsg(privmsg):
# Split the received PRIVMSG message into two useful parts
# Example message:
#   :SlimTim10!~SlimTim10@127-0-0-1.network.com PRIVMSG #channel :Hello?
    parts = privmsg[1:].split(':', 1)
# The information part of the message (sender, "PRIVMSG", channel/nickname)
    info = parts[0].split(' ')
    msg = parts[1].rstrip()	# The message part (e.g., "Hello?")
# The sender of the message (e.g., "SlimTim10")
    sender = info[0].split('!')[0]
# The string to be returned
    ret = ''

# Treat messages starting with '!' as commands (e.g., "!say hi")
    if msg[0] == '!':
# Split command message into two parts: bot command and following text
        cmd = msg.split(' ', 1)

# The '!say' command makes the bot say something
# To-do: make this command work for private messages sent directly to the bot
        if cmd[0] == '!say':
# Send the message to where the '!say' command was sent
            ret = 'PRIVMSG ' + info[2] + ' :' + cmd[1] + '\n'

# The '!die' command makes the bot quit (admin command)
        if cmd[0] == '!die' and sender in ADMINS:
            ret = 'QUIT\n'

# To-do: add a '!calc' command that evaluates basic mathematical expressions
# Difficulty: easy

# To-do: add a '!insult' command that makes the bot say a randomly selected
# 	insult to the command sender
# Difficulty: easy

# To-do: find and fix the bug
# To-do: add helpful comments to this command's code
        if cmd[0] == '!rps':
            try:
                user_rps = int(cmd[1])
                if user_rps < 0 or user_rps > 3:
                    raise Exception("Invalid")
                else:
                    rps_names = ['rock', 'paper', 'scissors']
                    bot_rps = random.randint(0, 3)
                    ret = 'PRIVMSG ' + info[2] + ' :Player chose ' + \
                    rps_names[user_rps] + '. LPMCBot chose ' + \
                    rps_names[bot_rps] + '. '
                    if user_rps == bot_rps:
                        ret += 'Tie game.\n'
                    else:
                        result = user_rps - bot_rps
                        if result == -2 or result == 1:
                            ret += 'Player wins!\n'
                        else:
                            ret += 'Player loses.\n'
            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: 0 = Rock, 1 = Paper, 3 = Scissors. ' + \
                'Example: !rps 1\n'


# To-do: add a '!ttt' command that starts a game of Tic Tac Toe to be played
# 	against the bot
# Difficulty: hard

    return ret			# Return the appropriate string


def setConfig():
    # This function will set the config values one of three ways
    # Default values as a backup, if there are environment variables
    # set those will be used, unless the first argument passed to lpmcbot.py
    # is -i or --interactive, then the user will be prompted for the settings.

    # Check if an argument was passed
    mode = None
    try:
        mode = argv[1]
    except IndexError:
        pass

    if mode == '-i' or mode == '--interactive':
        # Prompt for values
        print "Welcome to the LPMC Bot Interative startup.\n"
        print "A few settings must be entered before we can start.\n"
        NICK = raw_input("NICK: ")
        USER = raw_input("USER: ")
        REALNAME = NICK
        CHANNEL = raw_input("CHANNEL: ")
        print "Thank you. Starting up the bot.\n"

    else:
        try:
            # Check for environment variables
            NICK     = environ['NICK']
            USER     = environ['USER']
            REALNAME = environ['NICK']
            CHANNEL  = environ['CHANNEL']
            print "Initializing using environment variables.\n"

        except KeyError:
            # Fall back on defaults
            NICK     = "LPMCBot"
            USER     = "LPMCbot"
            REALNAME = "LPMCBot"
            CHANNEL  = "#LPMCBot"
            print "Initializing using default values.\n"

    return (NICK, USER, REALNAME, CHANNEL)


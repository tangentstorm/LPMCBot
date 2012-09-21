import sys
import os
import random
import socket
import re
import ConfigParser
import urllib
import ast
import json
from sys import argv, exc_info
from os import environ, makedirs
from math import *
from time import strftime, localtime
from tttlib import *
from datetime import datetime

# Admin name(s) for certain commands
# Usage:
#       if sender in ADMINS:
#           myfunc()
ADMINS = ["SlimTim10", "jfredett", "intothev01d"]

# records when users were last seen
# Key: username ; Value: time last seen
last_seen = {}
# maximum number of users allowed in last_seen
seen_limit = 100

def split_privmsg(privmsg):
    # Split the received PRIVMSG message into two useful parts
    # Example message:
    #   :SlimTim10!~SlimTim10@127-0-0-1.network.com PRIVMSG #channel :Hello?
    parts = privmsg[1:].split(':', 1)
    # The information part of the message (sender, "PRIVMSG", channel/nickname)
    info = parts[0].split(' ')
    msg = parts[1].rstrip()    # The message part (e.g., "Hello?")
    # The sender of the message (e.g., "SlimTim10")
    sender = info[0].split('!')[0]

    return info, msg, sender

def parsemsg(info, msg, sender):

#updates last_seen dict (and limits how big it can be)
    if info[1] == 'PRIVMSG':
        last_seen[sender] = localtime() # updates a user's latest time if already in list
        
        if len(last_seen) > seen_limit: # removes oldest user in a full lsit
            oldest_user = min(last_seen, key=last_seen.get)
            del last_seen[oldest_user]

# The string to be returned
    ret = ''
# Treat messages starting with '!' as commands (e.g., "!say hi")
    if msg[0] == '!':
# Split command message into two parts: bot command and following text
        cmd = msg.split(' ', 1)

# The '!say' command makes the bot say something,
# assuming a message is provided
        if cmd[0] == '!say' and len(cmd) > 1:
            # Bot will respond to !say command via private message if
            # privmsg is not "PRIVMSG + #channel + cmd"
            if info[2][0] != '#':
                ret = 'PRIVMSG ' + sender + ' :' + cmd[1] + '\n'
# Send the message to where the '!say' command was sent
            else:
                ret = 'PRIVMSG ' + info[2] + ' :' + cmd[1] + '\n'

# --- Utilities ---
        
        # The following is the implementation of commands which alter usermodes
        # !<command> <nickname>
        # This command will change the mode of the sender if no paramter is given, otherwise
        # it will modify the specified user. (admin command)
        # Syntax of message sent to irc server: MODE #channel +-ov nickname
        modeCommands = { '!op': '+o', '!deop': '-o', '!voice': '+v', '!devoice': '-v' }
        
        if cmd[0] in modeCommands.keys() and sender in ADMINS:
            # Begin forming return string by writing: MODE channelname
            ret = 'MODE ' + info[2]
            # Next, specify the mode
            ret += ' ' + modeCommands[cmd[0]] + ' '

            # Finally, specify target     
            if len(cmd) == 1:
                ret += sender
            else:
                ret += cmd[1]
            return ret + "\n" # we should be all done now.

# The '!die' command makes the bot quit (admin command)
        if cmd[0] == '!die' and sender in ADMINS:
            ret = 'QUIT\n'

# The '!kick' command kicks a user from the channel (with an optional message)
        if cmd[0] == '!kick' and sender in ADMINS:
            if len(cmd) == 2:
                kick_params = cmd[1].split()
                
                # Start building the return message with KICK channel user 
                ret = 'KICK ' + info[2] + ' ' + kick_params[0] 

                # Add the kick message if one is given
                if len(kick_params) > 1:
                    ret += ' :' + ' '.join(kick_params[1:])

                ret += '\n'
            else:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: !kick <user> [<message>]\n'

# The '!add_admin' command adds an admin
        if cmd[0] == "!add_admin" and sender in ADMINS:
            try:
                user_to_add = cmd[1]
                ADMINS.append(user_to_add)
                ret = 'PRIVMSG ' + info[2] + \
                ' :'+user_to_add+' added as admin\n'

            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Specify a user\n'

# The '!remove_admin' command removes an admin
        if cmd[0] == "!remove_admin" and sender in ADMINS:
            try:
                user_to_remove = cmd[1]
                ADMINS.remove(user_to_remove)
                ret = 'PRIVMSG ' + info[2] + \
                ' :'+user_to_remove+' removed as admin\n'

            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Specify an admin\n'

# The '!list_admins' lists all the Admins
        if cmd[0] == '!list_admins':
            ret = 'PRIVMSG ' + info[2] + \
            ' :Admins:'+ ", ".join(ADMINS) + '\n'
# --- End Utilities ---

# The !weather command returns the weather for a zip/postal code
        if cmd[0] == '!weather':
            ret = 'PRIVMSG ' + info[2] + ' :'
            if len(cmd) > 1:
                weather = weatherlookup(cmd[1])                 
                try:
                    temp_f = weather['data']['current_condition'][0]['temp_F']
                    temp_c = weather['data']['current_condition'][0]['temp_C']
                    ret += 'The current temperature in ' + cmd[1] + ' is ' + \
                        temp_f + 'F/' + \
                        temp_c + 'C.\n'
                except KeyError:
                    ret += 'Could not find weather information. Make sure you entered a valid zip code, city, state or country.\n'
            else:
                ret += 'Command help: Please specify a zip code, city, state or country.\n'

# The !seen commmand returns the last time a user posted
        if cmd[0] == '!seen':
            if len(cmd) > 1:
                if cmd[1] in last_seen:
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + cmd[1] + ' last seen ' + strftime("%B %d, %Y @ %I:%M %p %Z", last_seen[cmd[1]]) + '\n'
                else:
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :Error: User has not been seen\n'
            else:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Please specify user: "!seen <user>"\n'


# The '!calc' command evaluates basic mathematical expressions
        if cmd[0] == '!calc':
            #try evaluating user input
            try:
                # exlude __builtins__ to prevent access to globals that aren't
                # needed and create dictionary of all math functions from the math module
                # functions compatible from 2.5.2 and up
                safe_dict = {'__builtins__':None, 'abs':abs, 'acos':acos,
                            'asin':asin, 'atan':atan, 'atan2':atan2, 'ceil':ceil,
                            'cos':cos, 'cosh':cosh, 'degrees':degrees, 'e':e,
                            'exp':exp, 'fabs':fabs, 'floor':floor, 'fmod':fmod,
                            'frexp':frexp, 'hypot':hypot, 'ldexp':ldexp, 'log':log,
                            'log10':log10, 'modf':modf, 'pi':pi, 'pow':pow,
                            'radians':radians, 'sin':sin, 'sinh':sinh, 'sqrt':sqrt,
                            'tan':tan, 'tanh':tanh}
                # if command is !calc math print list of available math functions
                if cmd[1] == 'math':
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + str(safe_dict.keys()) + '\n'
                # otherwise evaluate user input while passing in safe globals
                # dictionary and no locals
                else:
                    user_input = eval(cmd[1],safe_dict,{})
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + str(user_input) + '\n'
            # throws exception on garbage input
            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Enter only numbers and valid mathematical functions ' + \
                ' Example: !calc 2+2 or !calc abs(-2) ' + \
                ' For a list of available math fuctions use !calc math\n'


# The '!insult' command prints out a randomly selected insult from a list.
        if cmd[0] == '!insult':
            # Tupple containing all the insults.
            # More can be added without modifying any other code.
            insults = ("Hey, you be quiet now!",
                       "What are you? An idiot!?",
                       "I know where you live..",
                       "You cur!",
                       "You insolent cad!",
                       "I challenge you to a duel at dawn!",
                       "So what, wanna fight about it?",
                       "I fart in your general direction.",
                       "Your mother was a hamster and your father smelt of elderberries.",
                       "You're a jerk, a complete kneebiter!")

            # Pick a random element in the insults tuple
            choice = random.choice(insults)
            # Return the insult
            ret = 'PRIVMSG ' + info[2] + ' :' + choice + '\n'

# The !rps command initializes a game of rock-paper-scissors.
        if cmd[0] == '!rps':
            try:
                # User inputs an integer 0 through 2 that is an index to the list of choices
                user_rps = int(cmd[1])
                # Exception if any int other than 0, 1, or 2
                if user_rps < 0 or user_rps > 2:
                    raise Exception("Invalid")
                else:
                    # The list that the index integers correspond to
                    rps_names = ['rock', 'paper', 'scissors']
                    # Bot produces a random integer 0 through 2
                    bot_rps = random.randint(0, 2)
                    # Produces a message with the results of the player's choice and the bot's random int
                    ret = 'PRIVMSG ' + info[2] + ' :Player chose ' + \
                    rps_names[user_rps] + '. LPMCBot chose ' + \
                    rps_names[bot_rps] + '. '
                    # The result of the game is dsplayed 
                    if user_rps == bot_rps:
                        ret += 'Tie game.\n'
                    elif user_rps == (bot_rps + 1) % 3:
                        ret += 'Player wins!\n'
                    else:
                        ret += 'Player loses.\n'
            # Exception raised if not an int. Displays help message and example.
            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: 0 = Rock, 1 = Paper, 2 = Scissors. ' + \
                'Example: !rps 1\n'

# To-do: add A.I. for the bot rather than random picking
# Difficulty: hard
        if cmd[0] == '!ttt':
            try:
                user_ttt = int(cmd[1])
                if user_ttt < 0 or user_ttt > 9:
                    raise Exception("Invalid")
                winner = 0
                availableSpaces = []
                for i in range(len(TICTACTOE)):      #this checks for open spaces 
                    if (TICTACTOE[i] == '_'):           #it's run after every cmd
                        availableSpaces.append(i+1)

                if (user_ttt == 0):                         #this initializes the board
                    for i in range(len(TICTACTOE)):
                        TICTACTOE.pop(0)
                    for i in range(9):
                        TICTACTOE.append('_')
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + 'New Game started! To play, type !ttt followed ' + \
                    'by a number. Example: "!ttt 3" for top right corner.' + '\n' 

                elif (user_ttt in availableSpaces):       #this handles the player's move 
                    TICTACTOE[user_ttt - 1] = 'O'
                    availableSpaces.remove(user_ttt)
                    output_lines = []
                    for i in range(9):
                        output_lines.append(TICTACTOE[i])
                    winner = tttWinCheck()
                    if (len(availableSpaces) and winner == 0):          #the following handles bot's move
                        print str(TICTACTOE)
                        botPick = tttAI()
                        TICTACTOE[botPick - 1] = 'X'
                        availableSpaces.remove(botPick)
                        for i in range(9):
                            output_lines[i] += TICTACTOE[i]
                        if (winner == 0):winner = tttWinCheck()

                    # Output game board in 3 lines of messages
                    ret = 'PRIVMSG ' + info[2] + ' :'
                    for i in range(0, 9, 3):
                        for j in range(len(output_lines[0])):
                            for k in range(3):
                                ret = ret + output_lines[k+i][j] + ' '
                            ret = ret + '  '
                        ret = ret + '\nPRIVMSG ' + info[2] + ' :'
                    ret += '\n'

                    if (len(availableSpaces) == 0 and len(TICTACTOE) > 0 and winner == 0):
                        ret = 'PRIVMSG ' + info[2] + ' : Tie game! Start a new game with !ttt 0.\n'
                        for i in range(len(TICTACTOE)):
                            TICTACTOE.pop(0)

                elif(len(TICTACTOE)):
                    ret = 'PRIVMSG ' + info[2] + ' : Space is already taken.' + '\n' 

                if (winner != 0):
                    ret = ret + 'PRIVMSG ' + info[2] + ' : The winner is ' + winner + '!\n'
                    for i in range(len(TICTACTOE)):
                        TICTACTOE.pop(0)
            except Exception, err:
            #How-To stuff
                print str(err)
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Tic-Tac-Toe. ' + \
                'To start a new game: !ttt 0\n'

        if cmd[0] == "!lookup":
            try:
                definition = lookup(cmd[1])
                ret = 'PRIVMSG ' + info[2] + \
                ' :'+cmd[1]+': '+definition+'\n'

            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Specify a word\n'

# The '!uptime' command returns the total time the bot has been running
        if cmd[0] == '!uptime':
            # Subtracts current time from time connection was opened
            now = datetime.now()
            uptime = now - connection_time
            
            # Converts timedelta into individual days, hours, etc.
            days_passed = int(uptime.days)
            hours_passed = int(uptime.seconds / 3600)
            minutes_passed = int((uptime.seconds / 60) % 60)
            seconds_passed = int(uptime.seconds % 60)
            
            # Returns the formatted string
            ret = 'PRIVMSG ' + info[2] + ' :Current Uptime: '+ \
            str(days_passed) + ' days ' + \
            str(hours_passed) + ' hours ' + \
            str(minutes_passed) + ' minutes and ' + \
            str(seconds_passed) + ' seconds.' + '\n'

# The '!help' command lists commands available to users
        #List all of the available commands and an example of how to use !help
        if cmd[0] == '!help':
            if len(cmd) == 1:
                ret = 'PRIVMSG ' + info[2] + \
                      ' :Current available commands:' + \
                      ' {!say, !list_admins, !seen, !calc, !insult, !rps, !ttt, !uptime, !weather} ' + \
                      ' To get further information on a command use "!help <command>". ' + \
                      ' Example: "!help say"\n'
            else:
                valid_help_cmd = True
                #Gives a help description for a specified command
                if cmd[1] == 'say':
                    help_cmd_name = '!say'
                    help_cmd_description = 'Makes the bot print a message.'
                    help_cmd_example = '"!say Hello"'
                elif cmd[1] == 'list_admins':
                    help_cmd_name = '!list_admins'
                    help_cmd_description = 'Lists the current administrators.'
                    help_cmd_example = '"!list_admins"'
                elif cmd[1] == 'seen':
                    help_cmd_name = '!seen'
                    help_cmd_description = 'Prints the last time a user was seen.'
                    help_cmd_example = '"!seen <user>"'
                elif cmd[1] == 'calc':
                    help_cmd_name = '!calc'
                    help_cmd_description = 'Performs basic calculations.'
                    help_cmd_example = '"!calc 2+2"'
                elif cmd[1] == 'insult':
                    help_cmd_name = '!insult'
                    help_cmd_description = 'Prints a random insult.'
                    help_cmd_example = '"!insult"'
                elif cmd[1] == 'rps':
                    help_cmd_name = '!rps'
                    help_cmd_description = 'Begins a game of Rock-Paper-Scissors.'
                    help_cmd_example = '"!rps 0"'
                elif cmd[1] == 'ttt':
                    help_cmd_name = '!ttt'
                    help_cmd_description = 'Begins a game of Tic Tac Toe.'
                    help_cmd_example = '"!ttt 5"'
                elif cmd[1] == 'uptime':
                    help_cmd_name = '!uptime'
                    help_cmd_description = 'Shows how long the bot has been running.'
                    help_cmd_example = '"!uptime"'
                else:
                    valid_help_cmd = False

                if valid_help_cmd == True:
                    #returns the description of the given command
                    ret = 'PRIVMSG ' + info[2] + \
                          ' :Command: %s' % (help_cmd_name) + \
                          ' Description: %s' % (help_cmd_description) + \
                          ' Example: %s\n' % (help_cmd_example)
                else:
                    ret = 'PRIVMSG ' + info[2] + ' :"!%s" is not a valid command.\n' % (cmd[1])

# The !admin_help command lists commands available only to admins
        if cmd[0] == '!admin_help' and sender in ADMINS:
            ret = 'PRIVMSG ' + info[2] + ' :Admin only commands:\n'+ \
                  'PRIVMSG ' + info[2] + ' :Command       |Use                                     |Example\n'               + \
                  'PRIVMSG ' + info[2] + ' ================================================================\n'               + \
                  'PRIVMSG ' + info[2] + ' :!add_admin    |Adds a user as an admin                 |"!add_admin <user>\n'    + \
                  'PRIVMSG ' + info[2] + ' :!remove_admin |Removes a user from admin status        |"!remove_admin <user>\n' + \
                  'PRIVMSG ' + info[2] + ' :!die          |kills the bot                           |\n'                      
                       
                  
            

    # The following shall look for websites posted in chat. It will then
    # obtain the Title of the page and return a message to the user to be sent

    # The following is a regex to match basic websites.
    # group(1) shall be the server address (e.g. www.reddit.com)
    # group(2) shall be the page to request (e.g. /r/lpmc)
    # Note: This regex will not match the following example sites:
    #       http://m.reddit.com, http://www.google.co.uk
    website = re.match('^http://((?:www\.)?\w+\.\w{2,3})(/.*)?',msg)
    if website:
        # creates socket object
        sock = socket.socket()
        try:
            # Connect to webserver on port 80
            sock.connect((website.group(1), 80))
            # Connection will timeout after 5 seconds. This was initially set
            # to 1 second, but frequent timeouts were experienced.
            sock.settimeout(5)
            # if no specific page is specified after domain, request /
            if website.group(2) == None:
                sock.send('GET / HTTP/1.0\r\n')
            else:
                sock.send('GET ' +website.group(2)+' HTTP/1.0\r\n')
            sock.send('HOST: ' + website.group(1) + '\r\n\r\n')
            # This will store the full page when we are finished
            source = ''
            # buff shall store 512 bytes of the page at a time
            buff = sock.recv(512)
            # keep receiving information, storing into the buffer, and then
            # concatenating source until buff == ''
            while buff != '':
                source += buff
                buff = sock.recv(512)
            # find the title of the page.
            titleRegex = re.compile('.*<title>(.+)</title>.*', 
                                    re.DOTALL).match(source)
            # remove preceding and trailing whitespace from the title
            titleStr = titleRegex.group(1).strip()
            # and finally, set ret to equal our message reporting our findings.
            ret =   'PRIVMSG ' + info[2] + ' :Title: ' + titleStr + '\n'
        except:
            print "Error:", exc_info()[0] # in case of exception, print error.
            pass
        sock.close()

    return ret            # Return the appropriate string

# looks up definition of -word- from google dictionary, returns as a string
def lookup(word):
    try:
        # loads json page to 'page' from a search to google for 'word'
        url="http://www.google.com/dictionary/json?callback=s&q="+word+"&sl=en&tl=en&restrict=pr,de&client=te"
        page=urllib.urlopen(url);
    except:
        return "Problem looking up word..."
    # reads content, ignoring first 2 and last 10 chars (because they mess up the tree structure)
    content=page.read()[2:-10]
    page.close()

    # converts content to a dict, which holds all the valuable information
    dic=ast.literal_eval(content)

    # tests whether the page is for a definition or not
    if dic.has_key("webDefinitions"):
        # picks the first entry
        webdef=dic["webDefinitions"][0]["entries"][0]
        # picks out just the definition
        word_def=webdef["terms"][0]['text'].split(';')[0]
        # formats definition for output
        plain_def = word_def.strip().replace("&#39","'").replace("&quot", "")
        return plain_def
    else:
        return "Definition unavailable"

def weatherlookup(code):
    try:
        url="http://free.worldweatheronline.com/feed/weather.ashx?q=" + code + "&format=json&num_of_days=2&key=67cd8f4a2f184852121809"
        page = urllib.urlopen(url)
        data = json.loads(page.read())
        return data
    except:
        return

def setConfig():
    """Return a dict containing bot config values."""
    # This function will set the config values one of three ways
    # Default values as a backup, if there are environment variables
    # set those will be used, unless the first argument passed to lpmcbot.py
    # is -i or --interactive, then the user will be prompted for the settings.

    # Check if an argument was passed
    flags = ''
    long_args = ''
    try:
        # If first char is -, assume it is a group of flags, ex: '-il'
        if argv[1][0] == '-' and argv[1][1] != '-':
            # Remove the '-'
            flags = argv[1][1:]
        # Is the first arg a long arg? ex: '--log'
        elif argv[1][:2] == '--':
            long_args = argv
    except IndexError:
        pass

    # -- Startup settings --
    if 'i' in flags or '--interactive' in long_args:
        # Prompt for values
        print "Welcome to the LPMC Bot Interative startup.\n"
        print "A few settings must be entered before we can start.\n"
        NICK = raw_input("NICK: ")
        USER = raw_input("USER: ")
        REALNAME = NICK
        CHANNEL = raw_input("CHANNEL: ")
        # Add User to ADMINS list (to let User use '!die' command)
        add_admin = raw_input("ADMIN: ")
        ADMINS.append(add_admin)
        print "Thank you. Starting up the bot.\n"
    # -- Config file settings --
    elif ('c' in flags or '--config' in long_args) and len(argv) >= 3:
        config_name = argv[2]
        config = ConfigParser.RawConfigParser()
        config.read(config_name)
        NICK = config.get('MAIN', 'NICK')
        USER = config.get('MAIN', 'USER')
        REALNAME = config.get('MAIN', 'REALNAME')
        CHANNEL = config.get('MAIN', 'CHANNEL')
        del ADMINS[:]
        ADMINS.extend(config.get('MAIN', 'ADMINS').replace(' ', '').split(','))
        print "Startup Settings retrieved from config file"
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
            CHANNEL  = "#LPMC"
            print "Initializing using default values.\n"
    # Stores the connection time for '!uptime' command        
    global connection_time
    connection_time = datetime.now()


    # -- Logging settings --
    if 'l' in flags or '--log' in long_args:
        LOG = True
    else:
        try:
            # Check for LOG env var seperate from essential settings
            LOG = environ['LOG']
        except KeyError:
            LOG = False

    config_values = {'NICK': NICK,
                     'USER': USER,
                     'REALNAME': REALNAME,
                     'CHANNEL': CHANNEL,
                     'LOG': LOG}
    return config_values


# -- Logging functions --

def open_log_file(server, channel):
    """Open the log file and return it"""
    # Get the name of the server and create a log directory
    log_dir = 'log_files/%s' % server.split('.')[1]
    try:
        makedirs(log_dir)
    except OSError as e:
        if e.errno == 17:
            # The dir already exists
            pass
        else:
            raise e
    # Create path to file using channel (without '#')
    # Example: "log_files/freenode/lpmc.log"
    file_path = '%s/%s.log' % (log_dir, channel[1:])
    log = open(file_path, 'a')
    return log

def write_log_header(bot_nick, log_file):
    """Create a header and write to the log file"""
    # Header message
    msg = strftime('\t* %c *\n') + '\t* Logged in as: %s *\n' % bot_nick
    # Create border
    longest = len(max(msg.split('\n'), key=len))
    border = '\t%s\n' % ('*' * (longest - 1))
    # Assemble the header
    header = border + msg + border
    log_file.write(header)

def log_event(msg, sender, log_file):
    """Log an event to current channel's log file."""
    # Create a timestamp, example format: '02:45 PM |'
    timestamp = strftime('%I:%M %p |\t')
    # Avoid logging garbage
    if 'PREFIX=(ov)@+' in msg:
        pass
    else:
        log_file.write(timestamp + sender + '\t' + msg + '\n')

def end_log_session(log_file):
    """Delimit each log session and close file."""
    log_file.write('\n\t\t***** ***** *****\n\n')
    log_file.close()

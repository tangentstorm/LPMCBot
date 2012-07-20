# Python Libraries
import sys
import socket
import string

# User-Defined Functions
from botlib import *

settings = setConfig()

# Config
HOST       = 'irc.freenode.net' # The server we want to connect to
PORT       = 6667               # The connection port (commonly 6667 for IRC)
NICK       = settings['NICK']   # The nickname of the bot
USER       = settings['USER']   # The username of the bot
REALNAME   = settings['REALNAME']  # The real name of the bot
CHANNEL    = settings['CHANNEL']   # The default channel for the bot
readbuffer = ''                 # Used to store incoming messages from the server

# Plugin Settings
LOG = settings['LOG']           # Is logging enabled? (True or False)

# Enable Plugins as required
if LOG:
    log_file = open_log_file(CHANNEL)

# Create the socket
s = socket.socket()
# Connect to the server
s.connect((HOST, PORT))

# Identify to the server
# Command: USER
# Parameters: <username> <hostname> <servername> <realname>
s.send('USER ' + USER + ' ' + HOST + ' server :' + REALNAME + '\n')

# Give the nickname to the server
# Command: NICK
# Parameters: <nickname> [ <hopcount> ]
s.send('NICK ' + NICK + '\n')

# Infinite listening loop while the bot is in the channel
while True:
    line = s.recv(500)          # Receive a server message (max 500 characters)
    print line                  # Output the server message

# Look for the freenode welcome message
    if 'Welcome to the freenode Internet Relay Chat Network' in line:
# Join the channel
        s.send('JOIN ' + CHANNEL + '\n')

# Handle a private message
    if 'PRIVMSG' in line:
        # If enabled, log messages
        if LOG:
            log_event(line, log_file)
        # Use the message parsing function
        send_msg = parsemsg(line)
        s.send(send_msg)

        if send_msg == 'QUIT\n':
            print "QUITTING"
            if LOG:
                end_log_session(log_file)
            break

# Handle a PING from the server
    if 'PING' in line:
# Remove the trailing characters
        line = line.rstrip()
# Split the line into an array (using whitespace as a delimiter)
        line = line.split()
# Send back PONG with the correct parameter
        s.send('PONG ' + line[1] + '\n')

# Python Libraries
import sys
import socket
import string

# User-Defined Functions
from botlib import *

# setConfig() returns a tupple containing NICK, USER, REALNAME, CHANNEL
# A tupple has it's first index set to 0, so settings[0] returns the first
# element in it.
settings = setConfig()

# Config
HOST       = 'irc.freenode.net' # The server we want to connect to
PORT       = 6667               # The connection port (commonly 6667 for IRC)
NICK       = settings[0]        # The nickname of the bot
USER       = settings[1]        # The username of the bot
REALNAME   = settings[2]        # The real name of the bot
CHANNEL    = settings[3]        # The default channel for the bot
readbuffer = ''                 # Used to store incoming messages from the server


s = socket.socket()             # Create the socket

s.connect((HOST, PORT))         # Connect to the server

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
# Use the message parsing function
        send_msg = parsemsg(line)
        s.send(send_msg)
        if send_msg == 'QUIT\n':
            print "QUITTING"
            break

# Handle a PING from the server
    if 'PING' in line:
# Remove the trailing characters
        line = line.rstrip()
# Split the line into an array (using whitespace as a delimiter)
        line = line.split()
# Send back PONG with the correct parameter
        s.send('PONG ' + line[1] + '\n')    

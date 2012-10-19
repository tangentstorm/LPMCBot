"""
An example test suite.
"""
import unittest
import botlib

def response_to( cmd ):
    """
    Returns the bot's response to the specified command.

    This wraps the command in the data structure that
    botlib.parsemsg expects, and -- if the message would be
    sent back to the public channel -- strips out the IRC
    cruft from the response.
    """
    info = ( "sender!~sender@x-y-z.com", "PRIVMSG", "#channel" )
    res = botlib.parsemsg( info, cmd, "sender" )
    normal = "PRIVMSG #channel :"
    if res.startswith( normal ) : res = res.replace( normal, '')
    return res.strip() # discard whitespace

class BotTest( unittest.TestCase ):
    """
    This builds a test suite out of its own methods.
    Any method whose name begins with test_xxx will
    be executed as a test case.
    """
    def setUp( self ):
        """
        The setUp() method runs automatically before each test.
        Here, we are clearing the ADMINS list, so that each test 
        will run as if it were sent by a normal user.
        """
        botlib.ADMINS = []

    def sudo( self ):
        botlib.ADMINS = [ "sender" ]

    def test_calc( self ):
        self.assertEquals( "3", response_to( "!calc 1 + 2" ))

    def test_die( self ):
        """
        Only admins should be able to issue the !die command.
        """
        botlib.ADMINS = []
        self.assertEquals( "", response_to( "!die" ))

        botlib.ADMINS = [ "sender" ]
        self.assertEquals( "QUIT", response_to( "!die" ))

if __name__=="__main__":
    unittest.main()

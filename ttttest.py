from tttlib import *

#Unit tests return true if all test cases have been passed

def tttWinTest():
    
    #Test case group 1
    TICTACTOE[4] = "X"
    
    #Test case group 1, test 1
    TICTACTOE[0] = "X"
    if (8 != tttWin()):
        return "Group 1, test 1: " + str(tttWin())
    else:
        TICTACTOE[0] = "_"
        
    #Test case group 1, test 2
    TICTACTOE[2] = "X"
    if (6 != tttWin()):
        return "Group 1, test 2: " + str(tttWin()) 
    else:
        TICTACTOE[2] = "_"
    
    #Test case group 1, test 3
    TICTACTOE[6] = "X"
    if (2 != tttWin()):
        return "Group 1, test 3: " + str(tttWin())
    else:
        TICTACTOE[6] = "_"
    
    #Test case group 1, test 4
    TICTACTOE[8] = "X"
    if (0 != tttWin()):
        return "Group 1, test 4: " + str(tttWin())
    else:
        TICTACTOE[8] = "_"
        
    TICTACTOE[4] = "_"    
    
    #Test case group 2
    
    #Test case group 2, test 1
    TICTACTOE[0] = "X"
    TICTACTOE[1] = "X"
    if (2 != tttWin()):
        return "Group 2, test 1: " + str(tttWin())
    else:
        TICTACTOE[0] = "_"
        TICTACTOE[1] = "_"
    
    #Test case group 2, test 2
    TICTACTOE[0] = "X"
    TICTACTOE[2] = "X"
    if (1 != tttWin()):
        return "Group 2, test 2: " + str(tttWin())
    else:
        TICTACTOE[0] = "_"
        TICTACTOE[2] = "_"
    
    #Test case group 2, test 3
    TICTACTOE[1] = "X"
    TICTACTOE[2] = "X"
    if (0 != tttWin()):
        return "Group 2, test 3: " + str(tttWin())
    else:
        TICTACTOE[1] = "_"
        TICTACTOE[2] = "_"
    
    #Test case group 3
    
    #Test case group 3, test 1
    TICTACTOE[0] = "X"
    TICTACTOE[3] = "X"
    if (6 != tttWin()):
        return "Group 3, test 1: " + str(tttWin())
    else:
        TICTACTOE[0] = "_"
        TICTACTOE[3] = "_"
        
    #Test case group 3, test 2
    TICTACTOE[0] = "X"
    TICTACTOE[6] = "X"
    if (3 != tttWin()):
        return "Group 3, test 2: " + str(tttWin())
    else:
        TICTACTOE[0] = "_"
        TICTACTOE[6] = "_"
        
    #Test case group 3, test 3
    TICTACTOE[3] = "X"
    TICTACTOE[6] = "X"
    if (0 != tttWin()):
        return "Group 3, test 3: " + str(tttWin())
    else:
        TICTACTOE[3] = "_"
        TICTACTOE[6] = "_"
        
    #If all test cases return true
    return True
    
def tttCenterTest():
    #Test case 1
    TICTACTOE[5] = "_"    
    if (-1 == tttCenter()):
        return False
    
    #Test case 2
    TICTACTOE[5] = "X"
    if (-1 != tttCenter()):
        return False
        
    #If both pass returns true
    return True
    
def tttCornerTest():
    
    #Reset environment
    TICTACTOE[0] = "_"
    TICTACTOE[2] = "_"
    TICTACTOE[6] = "_"
    TICTACTOE[8] = "_"
    
    #Test case 1
    if (0 != tttCorner()):
        return False
    
    #Test case 2
    TICTACTOE[0] = "X"
    if (2 != tttCorner()):
        return False
        
    #Test case 3    
    TICTACTOE[2] = "X"
    if (6 != tttCorner()):
        return False
        
    #Test case 4
    TICTACTOE[6] = "X"
    if (8 != tttCorner()):
        return False
        
    #Test case 5
    TICTACTOE[8] = "X"
    if (-1 != tttCorner()):
        return False
    
    #If all pass return true
    return True
    
def tttEdgeTest():

    #Reset environment
    TICTACTOE[1] = "_"
    TICTACTOE[3] = "_"
    TICTACTOE[5] = "_"
    TICTACTOE[7] = "_"

    #Test case 1
    if (1 != tttEdge()):
        return False
    
    #Test case 2
    TICTACTOE[1] = "X"
    if (3 != tttEdge()):
        return False
        
    #Test case 3    
    TICTACTOE[3] = "X"
    if (5 != tttEdge()):
        return False
        
    #Test case 4
    TICTACTOE[5] = "X"
    if (7 != tttEdge()):
        return False
        
    #Test case 5
    TICTACTOE[7] = "X"
    if (-1 != tttEdge()):
        return False
    
    #If all pass return true
    return True
    
print tttWinTest()
print tttCenterTest()
print tttCornerTest()
print tttEdgeTest()
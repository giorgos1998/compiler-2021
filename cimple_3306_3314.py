# Giorgos Papadatos 3306 cs03306
# Athanasios Papias 3314 cs03314

# Thanasi check oti einai swsta ta apo panw

import sys
import string
import re

letters = string.ascii_letters
numbers = string.digits
keywords = ["program","declare","if","else","while","switchcase","forcase","incase","case","default",
            "not","and","or","function","procedure","call","return","in","inout","input","print"]
lineCounter = 1

# Token class used by lexical analyzer
class Token:
    def __init__(self, tkType, content, line):
        self.tkType = tkType
        self.content = content
        self.line = line

# Displays error message to user with required info
def errorHandler(message):
    exitMessage = "ERROR at line " + str(lineCounter) + ": " + message
    sys.exit(exitMessage)


def genquad(par1, par2, par3, par4):
    pass

def newTemp():
    return 0

def backpatch(par1, par2):
    pass

def nextquad():
    return 0

def merge(par1, par2):
    return (0,0)

def makelist(par1):
    return 0


# Lexical Analyzer
def lexAn():

    state = "start"
    idSize = 0
    content = ""
    tkType = ""

    while True:

        lastPosition = sourceFile.tell()
        buffer = sourceFile.read(1)

        # reached EOF
        if buffer == "":
            errorHandler("Compiler reached end of file before program terminator (.)")

        # comment handling
        elif state == "start" and buffer == "#":
            state = "comment"
        
        elif state == "comment":
            if buffer == "#":
                state = "start"
                
        # whitespace handling
        elif state == "start" and buffer in string.whitespace:
            
            # keeps track of current line
            if buffer == "\n":
                global lineCounter
                lineCounter += 1


        # identifier handling
        elif state == "start" and buffer in letters:
            state = "identifier"
            tkType = "identifier"
            idSize += 1
            content += buffer
        
        elif state == "identifier":
            if idSize > 30:
                errorHandler("Cannot have identifier larger than 30 characters.")
            if buffer in letters or buffer in numbers:
                idSize += 1
                content += buffer
            else:
                sourceFile.seek(lastPosition)
                break
        
        # number handling
        elif state == "start" and buffer in numbers:
            state = "number"
            tkType = "number"
            content += buffer
        
        elif state == "number":
            if buffer in numbers:
                content += buffer
            else:
                sourceFile.seek(lastPosition)
                break
        
        # operator handling
        elif state == "start" and buffer in "+-":
            content = buffer
            tkType = "addOp"
            break

        elif state == "start" and buffer in "*/":
            content = buffer
            tkType = "mulOp"
            break

        # assignment handling
        elif state == "start" and buffer == ":":
            state = "assignment"
            tkType = "assignment"
            content += buffer
        
        elif state == "assignment":
            if buffer == "=":
                content += buffer
                break
            else:
                errorHandler("Invalid syntax, expected '=' after ':'")

        # relation operator handling
        elif state == "start" and buffer == "<":
            state = "smallerOp"
            tkType = "relOp"
            content += buffer
        
        elif state == "smallerOp":
            if buffer == "=":
                content += buffer
                break
            elif buffer == ">":
                content += buffer
                break
            else:
                sourceFile.seek(lastPosition)
                break

        elif state == "start" and buffer == ">":
            state = "greaterOp"
            tkType = "relOp"
            content += buffer

        elif state == "greaterOp":
            if buffer == "=":
                content += buffer
                break
            else:
                sourceFile.seek(lastPosition)
                break

        elif state == "start" and buffer == "=":
            tkType = "relOp"
            content = buffer
            break

        # delimiter handling
        elif state == "start" and buffer in ",;":
            tkType = "delimiter"
            content = buffer
            break

        # group symbol handling
        elif state == "start" and buffer in "[]()}{":
            tkType = "groupSymbol"
            content = buffer
            break

        # program termination handling
        elif state == "start" and buffer == ".":
            tkType = "terminator"
            content = buffer

            # check for additional code after program end
            localBuffer = sourceFile.read(1)
            while localBuffer != "":
                if localBuffer not in string.whitespace:
                    print("WARNING: Additional code found after program end. Additional code will be ignored.")
                    break
                localBuffer = sourceFile.read(1)
            
            break

        # unknown character handling
        else:
            errorHandler("Character '" + buffer + "' is not supported in C-imple.")

    # check if identifier is a keyword
    if tkType == "identifier" and content in keywords:
        tkType = "keyword"
    
    # create and return token
    token = Token(tkType, content, lineCounter)
    return token

################################### Syntax ###################################

def REL_OP():
    global token
    if token.tkType == "relOp": 
        token = lexAn()
    else:
        errorHandler("Relational operator expected")

def ADD_OP():
    global token
    if token.tkType == "addOp":
        token = lexAn()
    else:
        errorHandler("'+' or '-' exptected")

def MUL_OP():
    global token
    if token.tkType == "mulOp":
        token = lexAn()
    else:
        errorHandler("'*' or '/' expected")

def INTEGER():
    global token
    number = token.content
    if token.tkType == "number":
        token = lexAn()
    else:
        errorHandler(token.content + " is not of type int, expected integer")
    # will not reach return statement if there is a problem with the number
    return number
    

def ID():
    global token
    if token.tkType == "identifier":
       token = lexAn()
    else:
        errorHandler(token.content + " is not acceptable as identifier")

def optionalSign():
    global token
    if token.tkType == "addOp":
        ADD_OP()
       

def actualparitem():
    global token
    if token.tkType == "keyword" and token.content == "in":
        token = lexAn()
        expression()
    elif token.tkType == "keyword" and token.content == "inout":
        token = lexAn()
        ID()
    else:
        errorHandler("Keyword 'in' or 'inout' expected before parameter name")


def actualparlist():
    global token
    if token.tkType == "groupSymbol" and token.content == ")":
        token = lexAn()
    else:
        while True:
            actualparitem()
            if token.tkType == "delimiter" and token.content == ",":
                token = lexAn()
            elif token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                break
            else: 
                errorHandler("Missing ')' after function/procedure parameters")

def idtail():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        actualparlist()
        # ')' is checked in actualparlist()

 
# bfactTF is a list that contains the True and False lists for the whole boolfactor
# (bfactTF[0] = R.true, bfactTF[1] = R.false)
# we get the results with the return values, not with parameters
def boolfactor():
    global token
    bfactTF = []
    if token.tkType == "keyword" and token.content == "not":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "[":
            token = lexAn()
            # get condition lists and reverse them
            bfactTF_reversed = condition()
            bfactTF = [bfactTF_reversed[1], bfactTF_reversed[0]]
            if token.tkType == "groupSymbol" and token.content == "]":
                token = lexAn()
            else:
                errorHandler("Missing ']' at the end of 'not' expression")
        else:
            errorHandler("Missing '[' after 'not' keyword")
    elif token.tkType == "groupSymbol" and token.content == "[":
        token = lexAn()
        # get condition lists and pass them to caller
        bfactTF = condition()
        if token.tkType == "groupSymbol" and token.content == "]":
            token = lexAn()
        else:
            errorHandler("Missing ']' at the end of a bool expression")
    else:
        E1result = expression()
        # keep token before checking
        relop = token.content
        REL_OP()
        E2result = expression()

        # create and save quad that must be filled with jump address in case of True
        bfactTF[0] = makelist(nextquad())
        genquad(relop, E1result, E2result, "_")
        # create and save quad that must be filled with jump address in case of False
        bfactTF[1] = makelist(nextquad())
        genquad("jump", "_", "_", "_")

    # return boolfactor result to caller
    return bfactTF

        
# btermTF is a list that contains the True and False lists for the whole boolterm
# (btermTF[0] = Q.true, btermTF[1] = Q.false)
# we get the results with the return values, not with parameters
def boolterm():
    global token
    btermTF = boolfactor()
    while token.tkType == "keyword" and token.content == "and":
        # backpatch True list with next quad (if true, check next 'and' condition)
        backpatch(btermTF[0], nextquad())
        # bfactTF is a list that contains the True and False lists of the 2nd boolfactor (R2)
        token = lexAn()
        bfactTF = boolfactor()
        # get all False lists that we don't know where to jump yet
        btermTF[1] = merge(btermTF[1], bfactTF[1])
        # btermTF[0] now contains the only True quad that must be backpatched later
        btermTF[0] = bfactTF[0]

    # return boolterm result lists to caller
    return btermTF

def factor():
    global token
    result = ""
    if token.tkType == "number":
        result = INTEGER()
    elif token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        result = expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' at the end of an arithmetic expression")
    else:
        # NOTE result is function name here, not sure what to do
        result = token.content
        ID()
        idtail()
    return result
        

# F1result = F1.place (result of 1st factor), F2result = F2.place (result of 2nd factor)
# we get the results with the return values, not with parameters
def term():
    global token
    F1result = factor()
    while token.tkType == "mulOp":
        MUL_OP()
        F2result = factor()
        w = newTemp()
        genquad("x", F1result, F2result, w)
        F1result = w
    return F1result
          

# T1result = T1.place (result of 1st temp), T2result = T2.place (result of 2nd temp)
# we get the results with the return values, not with parameters
def expression():
    global token
    # NOTE sign will need some special handling
    optionalSign()
    T1result = term()
    while token.tkType == "addOp":
        ADD_OP()
        T2result = term()
        w = newTemp()
        genquad("+", T1result, T2result, w)
        T1result = w
    return T1result


# condTF is a list that contains the True and False lists for the whole condition
# (condTF[0] = B.true, condTF[1] = B.false)
# we get the results with the return values, not with parameters
def condition():
    global token
    condTF = boolterm()
    while token.tkType == "keyword" and token.content == "or":
        # backpatch false list with the next quad (if false, check next 'or' condition)
        backpatch(condTF[1], nextquad())
        # btermTF is a list that contains the True and False lists of the 2nd boolterm (Q2)
        token = lexAn()
        btermTF = boolterm()
        # get all True lists that we don't know where to jump yet
        condTF[0] = merge(condTF[0], btermTF[0])
        # condTF[1] now contains the only False quad that must be backpatched later 
        condTF[1] = btermTF[1]
    
    # return condition result lists to caller
    return condTF

def elsepart():
    global token
    if token.tkType == "keyword" and token.content == "else":
        token = lexAn()
        statements()


def assignStat():
    global token
    ID()
    if token.tkType == "assignment" and token.content == ":=":
        token = lexAn()
        expression()
    else:
        errorHandler("Missing assignment symbol ':='")  


def ifStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after 'if' condition")
        statements()
        elsepart() 
    else:
        errorHandler("Missing '(' after 'if' keyword")   


def whileStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
            statements()
        else:
            errorHandler("Missing ')' after 'while' condition")
    else:
        errorHandler("Missing '(' after 'while' keyword")   
                  

def switchcaseStat():
    global token
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                statements()
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")

    if token.tkType == "keyword" and token.content == "default":
        token = lexAn()
        statements()
    else:
        errorHandler("Keyword: 'default' expected at the end of switchcase")


def forcaseStat():
    global token
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                statements()
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")

    if token.tkType == "keyword" and token.content == "default":
        token = lexAn()
        statements()
    else:
        errorHandler("Keyword: 'default' expected at the end of forcase")


def incaseStat():
    global token
    # incase can be empty (according to grammar)
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                statements()
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")


def returnStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after return condition")
    else: 
        errorHandler("Missing '(' after 'return' keyword")


def callStat():
    global token
    ID()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        actualparlist()
        # ')' is checked in actualparlist()
    else: 
        errorHandler("Missing '(' after function/procedure name")
    

def printStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' at the end of 'print' statement")
    else: 
        errorHandler("Missing '(' after 'print' keyword")


def inputStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        ID()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' at the end of 'input' statement")
    else: 
        errorHandler("Missing '(' after 'input' keyword")


def formalparitem():
    global token
    if token.tkType == "keyword" and (token.content == "in" or token.content == "inout"):
        token = lexAn()
        ID()
    else:
        errorHandler("Keyword 'in' or 'inout' expected before parameter name")


def formalparlist():
    global token
    if token.tkType == "groupSymbol" and token.content == ")":
        token = lexAn()
    else:
        while True:
            formalparitem()
            if token.tkType == "delimiter" and token.content == ",":
                token = lexAn()
                continue
            elif token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                break
            else: 
                errorHandler("Missing ')' at function/procedure declaration")


def varlist():
    global token
    ID()
    while token.tkType == "delimiter" and token.content == ",":
        token = lexAn()
        ID()

    
def declarations():
    global token
    while token.tkType == "keyword" and token.content == "declare":
        token = lexAn()
        varlist()
        if token.tkType == "delimiter" and token.content == ";":
            token = lexAn()
        else:
            errorHandler("Missing ';' at the end of variable declaration")
        

def subprogram():    
    global token
    funcName = token.content
    ID()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        formalparlist()
        block(funcName, False)
    else:
        errorHandler("Missing '(' at function/procedure declaration")


def statement():
    global token
    if token.tkType == "identifier":
        assignStat()
    elif token.tkType == "keyword" and token.content == "if":
        token = lexAn()
        ifStat()
    elif token.tkType == "keyword" and token.content == "while":
        token = lexAn()
        whileStat()
    elif token.tkType == "keyword" and token.content == "switchcase":
        token = lexAn()
        switchcaseStat()
    elif token.tkType == "keyword" and token.content == "forcase":
        token = lexAn()
        forcaseStat()
    elif token.tkType == "keyword" and token.content == "incase":
        token = lexAn()
        incaseStat()
    elif token.tkType == "keyword" and token.content == "call":
        token = lexAn()
        callStat()
    elif token.tkType == "keyword" and token.content == "return":
        token = lexAn()
        returnStat()
    elif token.tkType == "keyword" and token.content == "input":
        token = lexAn()
        inputStat()
    elif token.tkType == "keyword" and token.content == "print":
        token = lexAn()
        printStat()
    # statement can be empty


def statements():
    global token
    if token.tkType == "groupSymbol" and token.content == "{":
        token=lexAn()
        while True:
            statement()
            if token.tkType == "delimiter" and token.content == ";":
                token = lexAn()
                if token.tkType == "groupSymbol" and token.content == "}":
                    token = lexAn()
                    break
            else:
                errorHandler("Missing ';' at end of statement") 
    else:
        statement()
        if token.tkType == "delimiter" and token.content == ";":
            token = lexAn()
        else:
            errorHandler("Missing ';' at end of statement") 

        
    
def subprograms():
    global token
    while (token.tkType == "keyword" and (token.content == "function" or token.content == "procedure")) :
        token=lexAn()
        subprogram()
        
        
def block(programName, isMain):
    global token
    declarations()
    subprograms()
    genquad("begin_block", programName, "_", "_")
    statements()
    # block() is common for main and other functions, so we need isMain to know if we must add 'halt'
    if isMain:
        genquad("halt", "_", "_", "_")
    genquad("end_block", programName, "_", "_")


def program():
    global token
    if token.tkType == "keyword" and token.content == "program":
        token = lexAn()
        programName = token.content
        ID()
        block(programName, True)
        if token.tkType == "terminator":
            print("No syntax errors found")
        else:
            errorHandler("Terminator '.' missing")     
    else:
        errorHandler("Keyword 'program' missing")


def synAn():
    global token
    program()
        

################################### Main ###################################

# Gets file to compile
try:
    sourceFile = open(sys.argv[1])
except IndexError:
    sys.exit("Error: You must provide a file to compile")
except FileNotFoundError:
    sys.exit("Error: '" + sys.argv[1] + "' is not a valid file")
except:
    sys.exit("Unknown error occured")
else:
    if sys.argv[1][-3:] != ".ci":
        sys.exit("Error: Source file must be a C-imple file (.ci)")

token = lexAn()
synAn()
# while token.tkType != "terminator":
#     print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)
#     token = lexAn()
# print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)

sourceFile.close()
# print("program finished")
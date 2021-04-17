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
    # NOTE no need to check all types of relOp's, already done on lexical analyzer
    if token.tkType == "relOp" and (token.content == "=" or token.content == "<=" or token.content == ">=" or token.content == ">" or token.content == "<" or token.content == "<>"): 
        token = lexAn()
    else:
        errorHandler("Relational operator expected")

def ADD_OP():
    global token
    # NOTE no need to check all types of addOp's, already done on lexical analyzer
    if token.tkType == "addOp" and (token.content == "+" or token.content == "-"):
        token = lexAn()
    else:
        errorHandler("\'+\' or \'-\' exptected")

def MUL_OP():
    global token
    # NOTE no need to check all types of mulOp's, already done on lexical analyzer
    if token.tkType == "mulOp" and (token.content == "*" or token.content == "/"):
        token = lexAn()
    else:
        errorHandler("\'*\' or \'/\' expected")

def INTEGER():
    global token
    # NOTE no need to check if token is number, lexical analyzer has already done that
    if token.tkType == "number" and token.content.isnumeric():
        token = lexAn()
    else:
        errorHandler(token.content + " " + "is not of type int")

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
    # BUG actualparlist can be empty, should handle this case
    while True:
        actualparitem()
        if token.tkType == "delimiter" and token.content == ",":
            continue
        elif token.tkType == "groupSymbol" and token.content == ")":
            break
        else: 
            errorHandler("Missing ')' after function/procedure parameters")

def idtail():
    global token
    # BUG idtail can be empty
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        actualparlist()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after function/procedure parameters")
    else:
        errorHandler("Missing '(' after function/procedure name")

 

def boolfactor():
    global token
    if token.tkType == "keyword" and token.content == "not":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "[":
            token = lexAn()
            condition()
            # NOTE token change here should not be needed
            token = lexAn()
            if token.tkType == "groupSymbol" and token.content == "]":
                token = lexAn()
            else:
                errorHandler("Missing ']' at the end of 'not' expression")
        else:
            errorHandler("Missing '[' after 'not' keyword")
    elif token.tkType == "groupSymbol" and token.content == "[":
        token = lexAn()
        condition()
        # NOTE token change here should not be needed
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "]":
            token = lexAn()
        else:
            errorHandler("Missing ']' at the end of a bool expression")
    else:
        expression()
        REL_OP()
        expression()
        

def boolterm():
    global token
    boolfactor()
    while token.tkType == "keyword" and token.content == "and":
        token = lexAn()
        boolfactor()

def factor():
    global token
    if token.tkType == "number":
        INTEGER()
    elif token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' at the end of an arithmetic expression")
    else:
        ID()
        # NOTE no need to check for '(', only idtail can follow
        if token.tkType == "groupSymbol" and token.content == "(":
            idtail()
        

def term():
    global token
    factor()
    while token.tkType == "mulOp":
        MUL_OP()
        factor()
          

def expression():
    global token
    optionalSign()
    term()
    while token.tkType == "addOp":
        ADD_OP()
        term()

def condition():
    global token
    boolterm()
    while token.tkType == "keyword" and token.content == "or":
        token = lexAn()
        boolterm()

def elsepart():
    global token
    if token.tkType == "keyword" and token.content == "else":
        token = lexAn()
        statements()
    else:
        # BUG else part is not mandatory (check grammar)
        errorHandler("else part expected")

def assignStat():
    global token
    ID()
    if token.tkType == "assignment" and token.content == ":=":
        token = lexAn()
        expression()
    else:
        errorHandler("Missing assignment symbol ':='")  
    return True

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
    return True


def whileStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after 'while' condition")
        statements()
        # NOTE token should not change here, but on statements()
        token = lexAn() 
    else:
        errorHandler("Missing '(' after 'while' keyword")   
    return True
                  

def switchcaseStat():
    global token
    # BUG switchcase can have only 'default' (yeah stupid but grammar is like that...)
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    # NOTE token should change inside statements()
                    token = lexAn()
                    if token.tkType == "keyword" and token.content != "case":
                        # BUG if token is 'case' it doesn't get the next token (which should be '(')
                        # possible fix: move token = lexAn() inside while
                        break
                else:
                    errorHandler("Missing ')' after 'case' condition")
            else:
                errorHandler("Missing '(' after 'case' keyword")
        if token.tkType == "keyword" and token.content == "default":
            token = lexAn()
            statements()
            # NOTE token should change inside statements()
            token = lexAn()
        else:
            errorHandler("Keyword: 'default' expected at the end of switchcase")
    else:
        errorHandler("Keyword: 'case' expected inside switchcase")
    return True

def forcaseStat():
    global token
    # BUG forcase can have only 'default' (yeah stupid but grammar is like that...)
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    # NOTE token should change inside statements()
                    token = lexAn()
                    if token.tkTypen == "keyword" and token.content != "case":
                        # BUG if token is 'case' it doesn't get the next token (which should be '(')
                        # possible fix: move token = lexAn() inside while
                        break
                else:
                    errorHandler("Missing ')' after 'case' condition")
            else:
                errorHandler("Missing '(' after 'case' keyword")
        if token.tkType == "keyword" and token.content == "default":
            token = lexAn()
            statements()
            # NOTE token should change inside statements()
            token = lexAn()
        else:
            errorHandler("Keyword: 'default' expected at the end of forcase")
    else:
        errorHandler("Keyword: 'case' exptected inside forcase")
    return True

def incaseStat():
    global token
    # BUG incase can be empty (bruh...)
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    # NOTE token should change inside statements()
                    token = lexAn()
                    if token.tkType == "keyword" and token.content != "case":
                        # BUG if token is 'case' it doesn't get the next token (which should be '(')
                        # possible fix: move token = lexAn() inside while
                        break
                else:
                    errorHandler("Missing ')' after 'case' condition")
            else:
                errorHandler("Missing '(' after 'case' keyword")
    else:
        errorHandler("Keyword: 'case' expected inside incase")
    return True

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
    
    return True

def callStat():
    global token
    ID()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        # BUG should call actualparlist(), not expression()
        expression()
        # NOTE token ')' is checked in actualparlist(), no need to double check
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after function/procedure parameters")
    else: 
        errorHandler("Missing '(' after function/procedure name")
    return True

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
    return True

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
    return True

def formalparitem():
    global token
    if token.tkType == "keyword" and (token.content == "in" or token.content == "inout"):
        token = lexAn()
        ID()
    else:
        errorHandler("Keyword 'in' or 'inout' expected before parameter name")


# BUG what if we have no parameters for the function?
# Maybe check for ')' here?
def formalparlist():
    global token
    while True:
        formalparitem()
        #token = lexAn()
        if token.tkType == "delimiter" and token.content == ",":
            continue
        else: 
            break

# BUG what if there is only one decleration? e.g. declare x;
# Maybe delimiter ';' handling should be in declarations() (check grammar)
def varlist():
    global token
    ID()
    while token.tkType == "delimiter" and token.content == ",":
        token = lexAn()
        ID()
        if token.tkType == "delimiter" and token.content == ";":
            break
        if token.tkType == "delimiter" and token.content != ";" and token.content != ",":
            errorHandler("Missing ';' at the end of variable declaration")
    
def declarations():
    global token
    while token.tkType == "keyword" and token.content == "declare":
        token = lexAn()
        varlist()
        # NOTE token should change in varlist()
        token = lexAn()

def subprogram():    
    global token
    # NOTE subprograms() already checked for keywords, double checking here not needed
    if token.tkType == "keyword" and (token.content == "function" or token.content == "procedure"):
        token = lexAn()
        ID()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            formalparlist()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                block()
            else:
                errorHandler("Missing ')' at function/procedure declaration")
        else:
            errorHandler("Missing '(' at function/procedure declaration")
    else:
        errorHandler("Expected keyword: 'function' or 'procedure'") 


def statement():
    global token
    # flag used to determine if given word is a known command or not
    isCommand = False
    if token.tkType == "identifier":
        # NOTE token should change here
        # BUG missing token
        isCommand=assignStat()
    elif token.tkType == "keyword" and token.content == "if":
        token = lexAn()
        isCommand=ifStat()
    elif token.tkType == "keyword" and token.content == "while":
        token = lexAn()
        isCommand=whileStat()
    elif token.tkType == "keyword" and token.content == "switchcase":
        token = lexAn()
        isCommand=switchcaseStat()
    elif token.tkType == "keyword" and token.content == "forcase":
        token = lexAn()
        isCommand=forcaseStat()
    elif token.tkType == "keyword" and token.content == "incase":
        token = lexAn()
        isCommand=incaseStat()
    elif token.tkType == "keyword" and token.content == "call":
        token = lexAn()
        isCommand=callStat()
    elif token.tkType == "keyword" and token.content == "return":
        token = lexAn()
        isCommand=returnStat()
    elif token.tkType == "keyword" and token.content == "input":
        token = lexAn()
        isCommand=inputStat()
    elif token.tkType == "keyword" and token.content == "print":
        token = lexAn()
        isCommand=printStat()
    if isCommand == False:
        errorHandler("Unknown command '" + token.content + "'")


def statements():
    global token
    if token.tkType == "groupSymbol" and token.content == "{":
        token=lexAn()
        while True:
            statement()
            if token.tkType == "delimiter" and token.content == ";":
                token = lexAn()
                # BUG Final statement doesn't need ';' (according to grammar)
                if token.tkType == "groupSymbol" and token.content == "}":
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
        # NOTE token should be prepared here for subprogram() to use
        subprogram()
        # NOTE token should change in subprogram() (possibly)
        token = lexAn()
        
        
        

def block():
    # NOTE possibly no need to add token here
    global token
    declarations()
    subprograms()
    statements()


def program():
    global token
    if token.tkType == "keyword" and token.content == "program":
        token = lexAn()
        ID()
        block()
        # NOTE token should change in block()
        token = lexAn()
        if token.tkType == "terminator":
            print("end")
        else:
            errorHandler("Terminator '.' missing")     
    else:
        errorHandler("Keyword 'program' missing")

def synAn():
    global token
    program()
        
    
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

# token = lexAn()
# synAn()
# while token.tkType != "terminator":
#     print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)
#     token = lexAn()
# print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)

sourceFile.close()
print("program finished")
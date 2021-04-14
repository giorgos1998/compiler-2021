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
    if token.tkType == "relOp" and (token.content == "=" or token.content == "<=" or token.content == ">=" or token.content == ">" or token.content == "<" or token.content == "<>"): 
        token = lexAn()
    else:
        errorHandler("Relational operator expected")

def ADD_OP():
    global token
    if token.tkType == "addOp" and (token.content == "+" or token.content == "-"):
        token = lexAn()
    else:
        errorHandler("\'+\' or \'-\' exptected")

def MUL_OP():
    global token
    if token.tkType == "mulOp" and (token.content == "*" or token.content == "/"):
        token = lexAn()
    else:
        errorHandler("\'*\' or \'/\' expected")

def INTEGER():
    global token
    if token.tkType == "number" and token.content.isnumeric():
        token = lexAn()
    else:
        errorHandler(token.content + " " + "is not of type int")

def ID():
    global token
    if token.tkType == "identifier":
       token = lexAn()
    else:
        errorHandler(token.content + " " + "is not acceptable as identifier")

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
        errorHandler("Expected in or inout")

def actualparlist():
    global token
    x=False
    while True:
        actualparitem()
        if token.tkType == "delimiter" and token.content == ",":
            continue
        elif token.tkType == "groupSymbol" and token.content == ")":
            break
        else: 
            errorHandler("Missing \')\'")

def idtail():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        actualparlist()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
    else:
        errorHandler("Missing \'(\'")

 

def boolfactor():
    global token
    if token.tkType == "keyword" and token.content == "not":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "[":
            token = lexAn()
            condition()
            token = lexAn()
            if token.tkType == "groupSymbol" and token.content == "]":
                token = lexAn()
            else:
                errorHandler("Missing \']\'")
        else:
            errorHandler("Missing \'[\'")
    elif token.tkType == "groupSymbol" and token.content == "[":
        token = lexAn()
        condition()
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "]":
            token = lexAn()
        else:
            errorHandler("Missing \']\'")
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
            errorHandler("Missing \')\'")
    else:
        ID()
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
        errorHandler("else part expected")

def assignStat():
    global token
    ID()
    if token.tkType == "assignment" and token.content == ":=":
        token = lexAn()
        expression()
    else:
        errorHandler("Missing assignment symbol \':=\'")  
    return True

def ifStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
        statements()
        elsepart() 
    else:
        errorHandler("Missing \'(\'")   
    return True


def whileStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
        
        statements()
        token = lexAn() 
    else:
        errorHandler("Missing \'(\'")   
    return True
                  

def switchcaseStat():
    global token
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if token.tkType == "keyword" and token.content != "case":
                        break
                else:
                    errorHandler("Missing \')\'")
            else:
                errorHandler()
        if token.tkType == "keyword" and token.content == "default":
            token = lexAn()
            statements()
            token = lexAn()
        else:
            errorHandler("Keyword: \'default\' exptected")
    else:
        errorHandler("Keyword: \'case\' exptected")
    return True

def forcaseStat():
    global token
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if toke.tkTypen == "keyword" and token.content != "case":
                        break
                else:
                    errorHandler("Missing \')\'")
            else:
                errorHandler("Missing \'(\'")
        if token.tkType == "keyword" and token.content == "default":
            token = lexAn()
            statements()
            token = lexAn()
        else:
            errorHandler("Keyword: \'default\' exptected")
    else:
        errorHandler("Keyword: \'case\' exptected")
    return True

def incaseStat():
    global token
    if token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token.tkType == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token.tkType == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if token.tkType == "keyword" and token.content != "case":
                        break
                else:
                    errorHandler("Missing \')\'")
            else:
                errorHandler("Missing \'(\'")
    else:
        errorHandler("Keyword: \'case\' exptected")
    return True

def returnStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
    else: 
        errorHandler("Missing \'(\'")
    
    return True

def callStat():
    global token
    ID()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
    
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
    else: 
        errorHandler("Missing \'(\'")
    return True

def printStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
    else: 
        errorHandler("Missing \'(\'")
    return True

def inputStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        ID()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing \')\'")
    else: 
        errorHandler("Missing \'(\'")
    return True

def formalparitem():
    global token
    if token.tkType == "keyword" and (token.content == "in" or token.content == "inout"):
        token = lexAn()
        ID()
    else:
        errorHandler("Keyword \'in\' or \'inout\' expected")



def formalparlist():
    global token
    x=False
    while True:
        formalparitem()
        #token = lexAn()
        if token.tkType == "delimiter" and token.content == ",":
            continue
        else: 
            break

    
def varlist():
    global token
    ID()
    while token.tkType == "delimiter" and token.content == ",":
        token = lexAn()
        ID()
        if token.tkType == "delimiter" and token.content == ";":
            break
        if token.tkType == "delimiter" and token.content != ";" and token.content != ",":
            errorHandler("Missing \';\'")
    
def declarations():
    global token
    while token.tkType == "keyword" and token.content == "declare":
        token = lexAn()
        varlist()
        token = lexAn()

def subprogram():    
    global token
    if token.tkType == "keyword" and (token.content == "function" or token.content == "procedure") :
        token = lexAn()
        ID()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            formalparlist()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                block()
            else:
                errorHandler("Missing \')\'")
        else:
            errorHandler("Missing \'(\'")
    else:
        errorHandler("Expected keyword: \'function\' or \'procedure\'") 


def statement():
    global token
    comm=False
    if token.tkType == "identifier":
        comm=assignStat()
    elif token.tkType == "keyword" and token.content == "if":
        token = lexAn()
        comm=ifStat()
    elif token.tkType == "keyword" and token.content == "while":
        token = lexAn()
        comm=whileStat()
    elif token.tkType == "keyword" and token.content == "switchcase":
        token = lexAn()
        comm=switchcaseStat()
    elif token.tkType == "keyword" and token.content == "forcase":
        token = lexAn()
        comm=forcaseStat()
    elif token.tkType == "keyword" and token.content == "incase":
        token = lexAn()
        comm=incaseStat()
    elif token.tkType == "keyword" and token.content == "call":
        token = lexAn()
        comm=callStat()
    elif token.tkType == "keyword" and token.content == "return":
        token = lexAn()
        comm=returnStat()
    elif token.tkType == "keyword" and token.content == "input":
        token = lexAn()
        comm=inputStat()
    elif token.tkType == "keyword" and token.content == "print":
        token = lexAn()
        comm=printStat()
    if comm == False:
        errorHandler("Unknown command")


def statements():
    global token
    if token.tkType == "groupSymbol" and token.content == "{":
        token=lexAn()
        x=0
        while True:
            statement()
            if token.tkType == "delimiter" and token.content == ";":
                token = lexAn()
                if token.tkType == "groupSymbol" and token.content == "}":
                    break
            else:
                errorHandler("Missing \';\'") 
    else:
        statement()
        if token.tkType == "delimiter" and token.content == ";":
            token = lexAn()
        else:
            errorHandler("Missing \';\'") 

        
    


def subprograms():
    global token
    while (token.tkType == "keyword" and token.content == "function" or token.content == "procedure") :
        subprogram()
        token = lexAn()
        
        
        

def block():
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
        token = lexAn()
        if token.tkType == "terminator":
            x="end"
        else:
            errorHandler("Terminator \'.\' missing")     
    else:
        errorHandler("Keyword \'program\' missing")

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

token = lexAn()
synAn()
while token.tkType != "terminator":
    print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)
    token = lexAn()
print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)

sourceFile.close()
print("program finished")
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
    if token = "relOp" and (token.content == "=" or token.content == "<=" or token.content == ">=" or token.content == ">" or token.content == "<" or token.content == "<>"): 
        #ok
    else:
        errorHandler("Relational operator expected")

def ADD_OP():
    if token = "addOp" and (token.content == "+" or token.content == "-"):
        #ok
    else:
        errorHandler("\'+\' or \'-\' exptected")

def MUL_OP():
    if token = "mulOp" and (token.content == "*" or token.content == "/"):
        #ok
    else:
        errorHandler("\'*\' or \'/\' expected")

def INTEGER():
    if token = "number" and isinstance(token.content, int):
        #ok
    else:
        errorHandler(token.content + "is not of type int")

def ID():
    if token = "identifier":
        #ok
    else:
        errorHandler(token.content + "is not acceptable as identifier")

def optionalSign():
    ADD_OP()

def expression():
    optionalSign()
    token = lexAn()
    term()
    token = lexAn()
    while token = "addOp":
        ADD_OP()
        token = lexAn()
        term()
        token = lexAn()

def actualparitem():
    if token == "keyword" and (token.content == "in" or token.content == "inout"):
        token = lexAn()
        if token == "Identifier":
            #ok
        else:
            errorHandler(token.content + "is not acceptable as identifier")
    else:
        errorHandler("Expected in or inout")

def actualparlist():
    x=False
    while True:
        token = lexAn()
        actualparitem()
        token = lexAn()
        if token == "delimeter" and token.content == ",":
            continue
        elif token == "groupSymbol" and token.content == ")":
            break
        else: 
            errorHandler("Missing \')\'")

def idtail():
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        actualparlist()
        token = lexAn()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler("Missing \')\'")
    else:
        errorHandler("Missing \'(\'")



def factor():
    if token = "number":
        token = lexAn()
        INTEGER()
        token = lexAn()
    elif token == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler()
    elif token = "identifier":
        token = lexAn()
        idtail()
    else:
        errorHandler("Wrong expression")



def term():
    factor()
    token = lexAn()
    while token = "mulOp:
        MUL_OP()
        token = lexAn()
        boolfactor()
        token = lexAn()    

def boolfactor():
    if token = "keyword" and token.content == "not":
        token = lexAn()
        if token == "groupSymbol" and token.content == "[":
            token = lexAn()
            condition()
            token = lexAn()
            if token == "groupSymbol" and token.content == "]":
                #ok
            else:
                errorHandler("Missing \']\'")
        else:
            errorHandler("Missing \'[\'")
    elif token == "groupSymbol" and token.content == "[":
            token = lexAn()
            condition()
            token = lexAn()
            if token == "groupSymbol" and token.content == "]":
                #ok
            else:
                errorHandler("Missing \']\'")
    else:
        token = lexAn()
        expression()
        token = lexAn()
        REL_OP
        token = lexAn()
        expression()
        token = lexAn()

def boolterm():
    boolfactor()
    token = lexAn()
    while token = "keyword" and token.content == "and":
        token = lexAn()
        boolfactor()
        token = lexAn()



def condition():
    boolterm()
    token = lexAn()
    while token = "keyword" and token.content == "or":
        token = lexAn()
        boolterm()
        token = lexAn()

def elsepart():
    if token = "keyword" and token.content == "else":
        token = lexAn()
        statements()
    else:
        errorHandler("else part expected")

def assignStat():
    if token == "assignment" and token.content == ":=":
        token = lexAn()
        expression()
        if token == "delimeter" and token.content == ";":
            #ok
        else:
            errorHandler("Missing \';\'")
    else:
        errorHandler("Missing assignment symbol \':=\'")  
    return True

def ifStat():
    
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        token = lexAn()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler("Missing \')\'")
        statements()
        elsepart() 
    else:
        errorHandler("Missing \'(\'")   
    return True


def whileStat():
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        condition()
        token = lexAn()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler("Missing \')\'")
        token = lexAn()
        statements() 
    else:
        errorHandler("Missing \'(\'")   
    return True
                  

def switchcaseStat():
    if token = "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if token = "keyword" and token.content != "case":
                        break
                else:
                    errorHandler("Missing \')\'")
            else:
                errorHandler()
        if token = "keyword" and token.content == "default":
            token = lexAn()
            statements()
            token = lexAn()
        else:
            errorHandler("Keyword: \'default\' exptected")
    else:
        errorHandler("Keyword: \'case\' exptected")
    return True

def forcaseStat():
    if token = "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if token = "keyword" and token.content != "case":
                        break
                else:
                    errorHandler("Missing \')\'")
            else:
                errorHandler("Missing \'(\'")
        if token = "keyword" and token.content == "default":
            token = lexAn()
            statements()
            token = lexAn()
        else:
            errorHandler("Keyword: \'default\' exptected")
    else:
        errorHandler("Keyword: \'case\' exptected")
    return True

def incaseStat():
    if token = "keyword" and token.content == "case":
        token = lexAn()
        while True:
            if token == "groupSymbol" and token.content == "(":
                token = lexAn()
                condition()
                token = lexAn()
                if token == "groupSymbol" and token.content == ")":
                    token = lexAn()
                    statements()
                    token = lexAn()
                    if token = "keyword" and token.content != "case":
                        break
                else:
                    errorHandler()
            else:
                errorHandler()
    else:
        errorHandler()
    return True

def returnStat():
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        token = lexAn()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler()
    else: 
        errorHandler()
    return True

def callStat():
    if token == "identifier":

        if token == "groupSymbol" and token.content == "(":
            token = lexAn()
            expression()
            token = lexAn()
            if token == "groupSymbol" and token.content == ")":
                #ok
            else:
                errorHandler()
        else: 
            errorHandler()
    else: 
        errorHandler()
    return True

def printStat():
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        expression()
        token = lexAn()
        if token == "groupSymbol" and token.content == ")":
            #ok
        else:
            errorHandler()
    else: 
        errorHandler()
    return True

def inputStat():
    if token == "groupSymbol" and token.content == "(":
        token = lexAn()
        if token == "identifier":
            token = lexAn()
            if token == "groupSymbol" and token.content == ")":
                #ok
            else:
                errorHandler()
        else:
            errorHandler()
    else: 
        errorHandler()
    return True

def formalparitem():
    if token == "keyword" and (token.content == "in" or token.content == "inout"):
        token = lexAn()
        if token == "Identifier":
            #ok
        else:
            errorHandler()
    else:
        errorHandler()



def formalparlist():
    x=False;
    while True:
        if token == "groupSymbol" and token.content == ")":
            break
        token = lexAn()
        formalparitem()
        token = lexAn()
        if token == "delimeter" and token.content == ",":
            continue
        elif token == "groupSymbol" and token.content == ")":
            break
        else: 
            errorHandler()

    
def varlist():
    if token == "identifier":
        while token == "identifier":
            token = lexAn()
            if token == "delimeter" and token.content == ",":
                token = lexAn()
                continue
            elif token == "delimeter" and token.content == ";":
                break;
            else:
                errorHandler()
    else:
        errorHandler()
    
    
def declarations():
    while token == "keyword" and token.content == "declare":
                varlist()
                token = lexAn()

def subprogram():    
    
    flag = 0
    if token == "keyword" and (token.content == "function" or token.content == "procedure") :
        token = lexAn()
        if token == "identifier":
            token = lexAn()
            if token == "groupSymbol" and token.content == "(":
                token = lexAn()
                formalparlist()
                token = lexAn()
                if token == "groupSymbol" and token.content == ")":
                    block()
                else:
                    errorHandler()
            else:
                errorHandler()
        else:
            errorHandler()
    else:
        errorHandler() 


def statement():
        comm=False
        if token = "identifier":
            token = lexAn()
            comm=assignStat()
        elif token = "keyword" and token.content = "if":
            token = lexAn()
            comm=ifStat()
        elif token = "keyword" and token.content = "while":
            token = lexAn()
            comm=whileStat()
        elif token = "keyword" and token.content = "switchcase":
            token = lexAn()
            comm=switchcaseStat()
        elif token = "keyword" and token.content = "forcase":
            token = lexAn()
            comm=forcaseStat()
        elif token = "keyword" and token.content = "incase":
            token = lexAn()
            comm=incaseStat()
        elif token = "keyword" and token.content = "call":
            token = lexAn()
            comm=callStat()
        elif token = "keyword" and token.content = "return":
            token = lexAn()
            comm=returnStat()
        elif token = "keyword" and token.content = "input":
            token = lexAn()
            comm=inputStat()
        elif token = "keyword" and token.content = "print":
            token = lexAn()
            comm=printStat()
        else:
        errorHandler()
        if comm == False:
            errorHandler()


def statements():
        if token = "groupSymbol" and token.content = "{":
            while True:
                token=lexAn()
                statement()
                token=lexAn()
                if token == "delimeter" and token.content == ";":
                    continue;
                elif token == "groupSymbol" and token.content = "}":
                    break;
                else:
                    errorHandler() 
        else:
            statement()
            if token == "delimeter" and token.content == ";":
                
                    #ok
            else:
                errorHandler() 

        
    


def subprograms():
    while (token == "keyword" and token.content == "function") :
        subprogram()
        
        
        

def programBlock():
    token = lexAn()
    declarations()
    token = lexAn()
    subprograms()
    token = lexAn()
    statements()


def program():

    if token == "keyword" and token.content == "program":
        token = lexAn()
        if token == "identifier":
            programBlock()
            token = lexAn()
            if token == "terminator"
                #end
            else:
                errorHandler()     
        else:
            errorHandler()
    else:
        errorHandler()
    
   
    

def synAn():
    while True:
        token = lexAn()
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
while token.tkType != "terminator":
    print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)
    token = lexAn()
print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)

sourceFile.close()
print("program finished")
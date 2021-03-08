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



def assignStat():
    if ":=" in bffr :
        if re.match('[\w\s]+'':=''[\w\s]+'';',bffr):
            #ok
        else:
            errorHandler()
        return True
    
def ifStat():
    if "if" == bffr.split(" ")[0] :
        if re.match('/if/\s+([\w\s]+[<>/==//!=//>=//<=//<>/][\w\s]+)',bffr):
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "{":
                block()
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "}":
                #ok
            else:
                errorHandler()
        else:
            errorHandler()
        return True

def whileStat():
    if "while" == bffr.split(" ")[0] :
        if re.match('/while/\s+([\w\s]+[<>/==//!=//>=//<=//<>/][\w\s]+)',bffr):
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "{":
                block()
            else:
                errorHandler()
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "}":
                #ok
            else:
                errorHandler()
        else:
            errorHandler()
        return True
                  

def switchcaseStat():
    if "switchcase" == bffr:
        counter+=1
        bffr = buffer[counter]
        if re.match('/case/\s+(\s+([\w\s]+[<>/==//!=//>=//<=//<>/][\w\s]+)[\w\s]+)*',bffr):
            counter+=1
            bffr = buffer[counter]
            if re.match('/default/[\w\s]+',bffr):
                counter+=1
                bffr = buffer[counter]
                if bffr[0] == "{":
                    block()
                else:
                    errorHandler()
                counter+=1
                bffr = buffer[counter]
                if bffr[0] == "}":
                    #ok
                else:
                    errorHandler()
            else:
                errorHandler()
        else:
            errorHandler()
        return True


def forcaseStat():
    if "forcase" == bffr:
        counter+=1
        bffr = buffer[counter]
        if re.match('/case/\s+(\s+([\w\s]+[<>/==//!=//>=//<=//<>/][\w\s]+)[\w\s]+)*',bffr):
            counter+=1
            bffr = buffer[counter]
            if re.match('/default/[\w\s]+',bffr):
            if bffr[0] == "{":
                    block()
                else:
                    errorHandler()
                counter+=1
                bffr = buffer[counter]
                if bffr[0] == "}":
                    #ok
                else:
                    errorHandler()
            else:
                errorHandler()
        else:
            errorHandler()
        return True

def incaseStat():
    if "incase" == bffr:
        counter+=1
        bffr = buffer[counter]
        if re.match('/case/\s+(\s+([\w\s]+[<>/==//!=//>=//<=//<>/][\w\s]+)[\w\s]+)*',bffr):
            if bffr[0] == "{":
                block()
            else:
                errorHandler()
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "}":
                #ok
            else:
                errorHandler()
        else:
            errorHandler()
        return True    

def callStat():
    if "call" == bffr.split(" ")[0] :
        if re.match('/call/[\w\s]+([\w\s]+)*',bffr):
            #ok
        else:
            errorHandler()
        return True


def returnStat():
    if "return" == bffr.split(" ")[0] :
        if re.match('/return/\s+([\w\s]+)*',bffr):
            #ok
        else:
            errorHandler()
        return True

def inputStat():
    if "input" == bffr.split(" ")[0] :
        if re.match('/input/\s+([\w\s]+)*',bffr):
            #ok
        else:
            errorHandler()
        return True

def printStat():
    if "input" == bffr.split(" ")[0] :
        if re.match('/print/\s+([\w\s]+)*',bffr):
            #ok
        else:
            errorHandler()
        return True

def declerations():
    
    counter+=1
    bffr = buffer[counter]
    

    while bffr[0] = "#" :
        counter+=1
        bffr = buffer[counter]
        bffr = bffr.replace(","," ").split()
    
    while bffr[0]= "declare" :
        bffr = buffer[counter]
        if re.match('/declare/[\w\s,]+;',bffr):
            #ok
        else:
            errorHandler()
        counter+=1
        bffr = buffer[counter]
        bffr = bffr.replace(","," ").split()
        while bffr[0] = "#" :
            counter+=1
            bffr = buffer[counter]
            bffr = bffr.replace(","," ").split(" ")

   
def subprograms():
    
    bffr = buffer[counter]
        while bffr[0] = "#" :
        counter+=1
        bffr = buffer[counter]
        bffr = bffr.replace(","," ").split()
    
    while (bffr[0]= "function" or bffr[0]= "procedure"):
        bffr = buffer[counter]
        if re.match('/function/[\w\s]+([\w\s]+)',bffr) or re.match('/procedure/[\w\s]+([\w\s]+)',bffr):
            if bffr[0] == "{":
                    block()
            else:
                errorHandler()
            counter+=1
            bffr = buffer[counter]
            if bffr[0] == "}":
                #ok
            else:
                errorHandler()
        else:
            errorHandler()
            

def block():
    bffr = buffer[counter]
    bffr = bffr.replace(","," ").split(" ")
    while bffr[0] = "#" :
        counter+=1
        bffr = buffer[counter]
        bffr = bffr.replace(","," ").split(" ")

    if bffr[counter][0] == "{":
        counter+=1
        bffr = buffer[counter]
        bffr = bffr.replace(","," ").split(" ")
        while(bffr[0][0] != "}")
            while bffr[0] = "#" :
                counter+=1
                bffr = buffer[counter]
                bffr = bffr.replace(","," ").split(" ")
            bffr = buffer[counter]
            comm=False
            comm=assignStat()
            comm=ifStat()
            comm=whileStat()
            comm=switchcaseStat()
            comm=forcaseStat()
            comm=incaseStat()
            comm=callStat()
            comm=returnStat()
            comm=inputStat()
            comm=printStat()
            if comm == False:
                errorHandler()


        

def programBlock():
    declarations()
    subprograms()
    block()

def program():
    bffr = buffer[counter]
    bffr = bffr.replace(","," ").split(" ")
    if "program" == bffr[0] :
        bffr = buffer[counter]
        if re.match('/program/[\w\s]+')
        programBlock()
    else:
        errorHandler()
    if bffr[-1] == ".":
        #ok
    else:
        errorHandler()

def synAn():
    while True:
        buffer = sourceFile.readlines()
        counter = 0
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
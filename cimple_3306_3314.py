# Giorgos Papadatos 3306 cs03306
# Athanasios Papias 3314 cs03314

import sys
import string
import re

letters = string.ascii_letters
numbers = string.digits
keywords = ["program","declare","if","else","while","switchcase","forcase","incase","case","default",
            "not","and","or","function","procedure","call","return","in","inout","input","print"]
lineCounter = 1

quadList = []       # list with created quads
quadNum = 0         # current quad label
tempNum = 0         # current temporary variable number

symbolTable = []    # list with active scopes (Symbol Table)
scopeDepth = 0      # current maximum nesting level in symbol table
mainFrameSize = 0   # frame size of the main function

transQuad = 0       # current quad for translation
assemblyList = []   # list with assembly instructions

# Token class used by lexical analyzer
class Token:
    def __init__(self, tkType, content, line):
        self.tkType = tkType
        self.content = content
        self.line = line

# Scope class used in symbol table
class Scope:
    def __init__(self, nestingLevel):
        self.entities = []
        self.nestingLevel = nestingLevel
        self.size = 12

    def ToString(self):
        result = "LEVEL: " + str(self.nestingLevel) + "\nSIZE: " + str(self.size) + "\n"
        return result

# Variable entity class used in scopes of symbol table
class variableEntity:
    def __init__(self, name):
        self.name = name
        self.offset = -1

    def ToString(self):
        result = "TYPE: variable\nNAME: " + self.name + "\nOFFSET: " + str(self.offset) + "\n"
        return result

# Variable entity class used in scopes of symbol table
class functionEntity:
    def __init__(self, name, type):
        self.name = name
        self.arguments = []
        self.framelength = -1
        self.type = type
        self.startQuad = -1

    def ToString(self):
        result = "TYPE: function\nNAME: " + self.name + "\nARGUMENTS: " + str(self.arguments) + "\nFRAMELENGTH: "
        result += str(self.framelength) + "\nTYPE: " + self.type + "\nSTART: L" + str(self.startQuad) + "\n"
        return result

# parameter entity class used in scopes of symbol table
class parameterEntity:
    def __init__(self, name, mode):
        self.name = name
        self.mode = mode
        self.offset = -1

    def ToString(self):
        result = "TYPE: parameter\nNAME: " + self.name + "\nMODE: " + self.mode + "\nOFFSET: " + str(self.offset) + "\n"
        return result


########## Syntax Table functions ##########

def printSymbolTable():
    for i in range(len(symbolTable)-1, -1, -1):
        scope = symbolTable[i]
        line = "(" + str(scope.nestingLevel) + "/" + str(scope.size) + ")"

        for entity in scope.entities:
            line += " <-- |" + entity.name + "/"
            if type(entity) is variableEntity:
                line += str(entity.offset) + "|"
            elif type(entity) is parameterEntity:
                line += str(entity.offset) + "/" + entity.mode + "|"
            else:
                line += str(entity.framelength) + "/" + entity.type + "|"
                for argument in entity.arguments:
                    line += "<" + argument + ">"
        
        print(line)
        if i != 0:
            print("  |")
            print("  v")
        else:
            print()

# Creates a new scope, increases current nesting level and adds scope to the symbol table
def addScope():
    global scopeDepth
    scopeDepth += 1
    scope = Scope(scopeDepth)
    symbolTable.append(scope)
    # print("------ ADDED SCOPE ------")
    # print(scope.ToString())

# Removes last scope from symbol table and decreases current nesting level
def removeScope():
    global scopeDepth
    global mainFrameSize
    print("###### SYMBOL TABLE BEFORE REMOVAL ######\n")
    printSymbolTable()
    scopeDepth -= 1
    scopeSize = symbolTable.pop().size
    if scopeDepth == 0:
        mainFrameSize = scopeSize
    else:
        symbolTable[-1].entities[-1].framelength = scopeSize
    # print("------ REMOVED SCOPE ------")
    # print("Current depth:", scopeDepth, "\n")
    print("###### SYMBOL TABLE AFTER REMOVAL ######\n")
    printSymbolTable()
    if scopeDepth == 0:
        print("Symbol table is empty")
        print("Main frame size:", mainFrameSize, "\n")

# Adds given entity to the last scope (entity types: var, func, par)
def addEntity(entity, entityType):
    topScope = symbolTable[-1]
    if entityType != "func":
        entity.offset = topScope.size
        topScope.size += 4
    topScope.entities.append(entity)
    # print("------ ADDED ENTITY ------")
    # print(entity.ToString())


# Searches for given symbol in symbol table and returns how many levels away is the symbol
def searchSymbolTable(symbol):
    global scopeDepth
    for i in range(len(symbolTable)-1, -1, -1):
        scope = symbolTable[i]
        for entity in scope.entities:
            if entity.name == symbol:
                return scopeDepth - scope.nestingLevel
    errorHandler("Cannot find '" + symbol + "', variable or function not declared")



########## Error handler function ##########

# Displays error message to user with required info
def errorHandler(message):
    exitMessage = "ERROR at line " + str(lineCounter) + ": " + message
    sys.exit(exitMessage)


########## Intermediate code functions ##########

def genquad(op, x, y, z):
    global quadList
    global quadNum
    quadList.append([op,x,y,z])
    quadNum += 1

def newTemp():
    global tempNum
    temp = "T_" + str(tempNum)
    tempNum += 1
    # add temp variable entity to scope
    addEntity(variableEntity(temp), "var")
    return temp

def backpatch(list1, z):
    global quadList
    for label in list1:
        # NOTE might need label-1
        quadList[label-1][3] = z

def nextquad():
    global quadNum
    return quadNum + 1

def merge(list1, list2):
    return list1 + list2

def makelist(x):
    return [x]

def emptylist():
    return []


########## Assembly code functions ##########

# Translates quads of current code block
def translateBlock(isMain):
    global transQuad
    for i in range(transQuad, len(quadList)-1):
        quad = quadList[i]
        
        labelBlock = ""
        label = "L" + str(i + 1) + ":"
        labelBlock += label
    
        qType = str(quad[0])
        op1 = str(quad[1])
        op2 = str(quad[2])
        resTarget = str(quad[3])

        if qType == "begin_block":
            if isMain:
                # add main label
                assemblyList.append("Lmain:\n")
                # make enough space in stack for main
                labelBlock += "\t\t" + "addi $sp, $sp, " + str(symbolTable[-1].size) + "\n"
                # save at $s0 the start of main's frame to get easy access to global variables
                labelBlock += "\t\t" + "move $s0, $sp" + "\n"
            else:
                # store return address
                labelBlock += "\t\t" + "sw $ra, -0($sp)" + "\n"
        
        elif qType == "end_block":
            if not isMain:
                # load return address to $ra and return
                labelBlock += "\t\t" + "lw $ra, -0($sp)" + "\n"
                labelBlock += "\t\t" + "jr $ra" + "\n"

        elif qType == "jump":
            labelBlock += "\t\t" + "b L" + resTarget + "\n"

        elif qType == "inp":
            labelBlock += "\t\t" + "li $v0, 5" + "\n"
            labelBlock += "\t\t" + "syscall" + "\n"
            labelBlock += "\t\t" + storerv("$v0", op1) + "\n"       # NOTE should change

        elif qType == "out":
            labelBlock += "\t\t" + "li $v0, 1" + "\n"
            labelBlock += "\t\t" + loadvr(op1, "$a0") + "\n"        # NOTE should change
            labelBlock += "\t\t" + "syscall" + "\n"

        elif qType == "halt":
            labelBlock += "\t\t" + "li $v0, 10" + "\n"
            labelBlock += "\t\t" + "syscall" + "\n"

        elif qType == "=":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "beq $t1, $t2, L" + resTarget + "\n"

        elif qType == "<":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "blt $t1, $t2, L" + resTarget + "\n"

        elif qType == ">":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "bgt $t1, $t2, L" + resTarget + "\n"

        elif qType == "<>":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "bne $t1, $t2, L" + resTarget + "\n"

        elif qType == "<=":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "ble $t1, $t2, L" + resTarget + "\n"

        elif qType == ">=":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "bge $t1, $t2, L" + resTarget + "\n"

        elif qType == ":=":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + storerv("$t1", resTarget) + "\n"# NOTE should change

        elif qType == "+":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "add $t1, $t1, $t2" + "\n"
            labelBlock += "\t\t" + storerv("$t1", resTarget) + "\n"# NOTE should change

        elif qType == "-":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "sub $t1, $t1, $t2" + "\n"
            labelBlock += "\t\t" + storerv("$t1", resTarget) + "\n"# NOTE should change

        elif qType == "*":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "mul $t1, $t1, $t2" + "\n"
            labelBlock += "\t\t" + storerv("$t1", resTarget) + "\n"# NOTE should change

        elif qType == "/":
            labelBlock += "\t\t" + loadvr(op1, "$t1") + "\n"       # NOTE should change
            labelBlock += "\t\t" + loadvr(op2, "$t2") + "\n"       # NOTE should change
            labelBlock += "\t\t" + "div $t1, $t1, $t2" + "\n"
            labelBlock += "\t\t" + storerv("$t1", resTarget) + "\n"# NOTE should change

        # TODO function handling (ret, par, call)

        assemblyList.append(labelBlock)




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
    op = ""
    if token.tkType == "relOp":
        op = token.content
        token = lexAn()
    else:
        errorHandler("Relational operator expected")
    return op

def ADD_OP():
    global token
    op = ""
    if token.tkType == "addOp":
        op = token.content
        token = lexAn()
    else:
        errorHandler("'+' or '-' exptected")
    return op

def MUL_OP():
    global token
    op = ""
    if token.tkType == "mulOp":
        op = token.content
        token = lexAn()
    else:
        errorHandler("'*' or '/' expected")
    return op

def INTEGER():
    global token
    number = ""
    if token.tkType == "number":
        number = token.content
        token = lexAn()
    else:
        errorHandler(token.content + " is not of type int, expected integer")
    return number
    

def ID():
    global token
    name = ""
    if token.tkType == "identifier":
        name = token.content
        token = lexAn()
    else:
        errorHandler(token.content + " is not acceptable as identifier")
    return name


def optionalSign():
    global token
    op = "no-op"
    if token.tkType == "addOp":
        op = ADD_OP()
    return op
       

def actualparitem(parList):
    global token
    parType = ""
    par = ""
    if token.tkType == "keyword" and token.content == "in":
        parType = "CV"
        token = lexAn()
        par = expression()
    elif token.tkType == "keyword" and token.content == "inout":
        parType = "REF"
        token = lexAn()
        par = ID()
    else:
        errorHandler("Keyword 'in' or 'inout' expected before parameter name")
    
    parList.append((par, parType))


def actualparlist(parList):
    global token
    if token.tkType == "groupSymbol" and token.content == ")":
        token = lexAn()
    else:
        while True:
            actualparitem(parList)
            if token.tkType == "delimiter" and token.content == ",":
                token = lexAn()
            elif token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                break
            else: 
                errorHandler("Missing ')' after function/procedure parameters")

def idtail(parList):
    global token
    # '(' is checked in caller (factor())
    actualparlist(parList)
    # ')' is checked in actualparlist()

 
# bfactTF is a list that contains the True and False lists for the whole boolfactor
# (bfactTF[0] = R.true, bfactTF[1] = R.false)
# we get the results with the return values, not with parameters
def boolfactor():
    global token
    bfactTF = [[],[]]
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
        relop = REL_OP()
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
        # ID will be a variable or a function
        # if it is a variable, we want to return it as the factor result
        # if it is a function, it will be followed by a '('
        result = ID()
        # here we handle function calling (has return statement)
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            # the ID we saved as 'result' is the function name
            funcName = result
            # idtail() will get parameters and save their info in parList
            # parList holds needed parameter info to generate quads in proper order
            parList = []
            idtail(parList)
            # result contains the variable that has the return value of the function
            result = newTemp()
            for param in parList:
                genquad("par", param[0], param[1], "_")
            genquad("par", result, "RET", "_")
            genquad("call", funcName, "_", "_")

    return result
        

# F1result = F1.place (result of 1st factor), F2result = F2.place (result of 2nd factor)
# we get the results with the return values, not with parameters
def term():
    global token
    F1result = factor()
    while token.tkType == "mulOp":
        # save operator, 2nd term and create a new temporary variable (w)
        op = MUL_OP()
        F2result = factor()
        w = newTemp()
        # multiply/divide 2nd term with 1st and store result to w
        genquad(op, F1result, F2result, w)
        # save w to 1st temp to use it on the next operation (or to return it as the result)
        F1result = w
    return F1result
          

# T1result = T1.place (result of 1st temp), T2result = T2.place (result of 2nd temp)
# we get the results with the return values, not with parameters
def expression():
    global token
    op = optionalSign()
    T1result = term()
    # if there is an optional sign:
    if op != "no-op":
        t = newTemp()
        # add/subtract from zero the content of the 1st term and save it to t (temporary variable)
        genquad(op, "0", T1result, t)
        # save t to the 1st term to use it later
        T1result = t
    while token.tkType == "addOp":
        # save operator, 2nd term and create a new temporary variable (w)
        op = ADD_OP()
        T2result = term()
        w = newTemp()
        # add/subtract 2nd term from 1st and store result to w
        genquad(op, T1result, T2result, w)
        # save w to 1st temp to use it on the next operation (or to return it as the result)
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
    assignTarget = ID()
    if token.tkType == "assignment" and token.content == ":=":
        token = lexAn()
        # Eresult has the variable that contains the expression result
        Eresult = expression()
        genquad(":=", Eresult, "_", assignTarget)
    else:
        errorHandler("Missing assignment symbol ':='")  


def ifStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        condTF = condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
        else:
            errorHandler("Missing ')' after 'if' condition")
        # if the condition is True, we want the program to jump here
        backpatch(condTF[0], nextquad())
        statements()
        # after the if statements are completed, the program must skip the else part
        # we don't know yet where to jump so we save the jump command and we will backpatch it later
        ifList = makelist(nextquad())
        genquad("jump", "_", "_", "_")
        # if the condition is False, we want the program to jump straight to the else part
        backpatch(condTF[1], nextquad())
        elsepart()
        # now we have generated the code of the else part, so we know where to jump to skip it
        backpatch(ifList, nextquad())
    else:
        errorHandler("Missing '(' after 'if' keyword")   


def whileStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        # keep while condition position to come back for the next loop
        whileQuad = nextquad()
        condTF = condition()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
            # we want the program to go here if the while condition is True, so we backpatch the True list
            backpatch(condTF[0], nextquad())
            statements()
            # jump back to check again the while condition
            genquad("jump", "_", "_", whileQuad)
            # if the condition is False, we want the program to jump here (after the while)
            backpatch(condTF[1], nextquad())
        else:
            errorHandler("Missing ')' after 'while' condition")
    else:
        errorHandler("Missing '(' after 'while' keyword")   
                  

def switchcaseStat():
    global token
    # we need to keep a list that will contain the exit jumps of all the cases
    # so that we can backpatch them at the end of the switch
    exitList = emptylist()
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condTF = condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                # if the case condition is True, we want the program to execute case statements
                backpatch(condTF[0], nextquad())
                statements()
                # if we executed the case statements, we want the program to jump at the end of the switch
                # we don't know where the switch ends yet so we add it to the exit list we made earlier
                caseExit = makelist(nextquad())
                genquad("jump", "_", "_", "_")
                exitList = merge(exitList, caseExit)
                # if the case condition is False, we want the program to move to the next case
                backpatch(condTF[1], nextquad())
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")

    if token.tkType == "keyword" and token.content == "default":
        token = lexAn()
        statements()
        # now the whole switch is completed and we are at its end, we need to backpatch the exit list here
        backpatch(exitList, nextquad())
    else:
        errorHandler("Keyword: 'default' expected at the end of switchcase")


def forcaseStat():
    global token
    # keep forcase start to come back for the next loop
    forQuad = nextquad()
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condTF = condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                # if the case condition is True, we want the program to execute case statements
                backpatch(condTF[0], nextquad())
                statements()
                # once the statements are executed, the program must jump at the forcase start
                genquad("jump", "_", "_", forQuad)
                # if the case condition is False, we want the program to move to the next case
                backpatch(condTF[1], nextquad())
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")

    if token.tkType == "keyword" and token.content == "default":
        # once the program has reached the default statement, it continues its normal flow
        token = lexAn()
        statements()
    else:
        errorHandler("Keyword: 'default' expected at the end of forcase")


def incaseStat():
    global token
    # to check if any case has been executed, we will need to add a flag to the program
    # if the program executes a case, it will set it to '1'
    # at the end of 'incase' if the flag is '1' the program will execute incase again, else it will contunue the flow
    flag = newTemp()
    # save the starting point of incase to jump back
    incaseQuad = nextquad()
    # initialize flag to '0' every time incase starts
    genquad(":=", "0", "_", flag)
    while token.tkType == "keyword" and token.content == "case":
        token = lexAn()
        if token.tkType == "groupSymbol" and token.content == "(":
            token = lexAn()
            condTF = condition()
            if token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                # if the case condition is True, we want the program to execute case statements
                backpatch(condTF[0], nextquad())
                # the case condition is True, so the program sets flag to '1'
                genquad(":=", "1", "_", flag)
                statements()
                # if the case condition is False, we want the program to move to the next case
                backpatch(condTF[1], nextquad())
            else:
                errorHandler("Missing ')' after 'case' condition")
        else:
            errorHandler("Missing '(' after 'case' keyword")
    # the program has reached the end of incase, now it must check the flag and if it's '1' jump back to the start
    genquad("=", flag, "1", incaseQuad)

def returnStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        Eresult = expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
            genquad("retv", Eresult, "_", "_")
        else:
            errorHandler("Missing ')' after return condition")
    else: 
        errorHandler("Missing '(' after 'return' keyword")

# here we call a procedure (no return statement)
def callStat():
    global token
    procName = ID()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        # parList holds needed parameter info to generate quads in proper order
        parList = []
        actualparlist(parList)
        # ')' is checked in actualparlist()
        for param in parList:
            genquad("par", param[0], param[1], "_")
        genquad("call", procName, "_", "_")
    else: 
        errorHandler("Missing '(' after function/procedure name")
    

def printStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        Eresult = expression()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
            genquad("out", Eresult, "_", "_")
        else:
            errorHandler("Missing ')' at the end of 'print' statement")
    else: 
        errorHandler("Missing '(' after 'print' keyword")


def inputStat():
    global token
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        inputTarget = ID()
        if token.tkType == "groupSymbol" and token.content == ")":
            token = lexAn()
            genquad("inp", inputTarget, "_", "_")
        else:
            errorHandler("Missing ')' at the end of 'input' statement")
    else: 
        errorHandler("Missing '(' after 'input' keyword")


def formalparitem():
    global token
    if token.tkType == "keyword" and token.content == "in":
        token = lexAn()
        parName = ID()
        # add parameter entity to last scope and return parameter mode
        addEntity(parameterEntity(parName, "CV"), "par")
        return "IN"
    elif token.tkType == "keyword" and token.content == "inout":
        token = lexAn()
        parName = ID()
        # add parameter entity to last scope and return parameter mode
        addEntity(parameterEntity(parName, "REF"), "par")
        return "IO"
    else:
        errorHandler("Keyword 'in' or 'inout' expected before parameter name")


def formalparlist():
    global token
    if token.tkType == "groupSymbol" and token.content == ")":
        token = lexAn()
        return []
    else:
        # argList stores all parameter modes (arguments) for this function
        argList = []
        while True:
            argList.append(formalparitem())
            if token.tkType == "delimiter" and token.content == ",":
                token = lexAn()
                continue
            elif token.tkType == "groupSymbol" and token.content == ")":
                token = lexAn()
                break
            else: 
                errorHandler("Missing ')' at function/procedure declaration")
        return argList


def varlist():
    global token
    varName = ID()
    addEntity(variableEntity(varName), "var")
    while token.tkType == "delimiter" and token.content == ",":
        token = lexAn()
        varName = ID()
        addEntity(variableEntity(varName), "var")


    
def declarations():
    global token
    while token.tkType == "keyword" and token.content == "declare":
        token = lexAn()
        varlist()
        if token.tkType == "delimiter" and token.content == ";":
            token = lexAn()
        else:
            errorHandler("Missing ';' at the end of variable declaration")
        

def subprogram(funcType):    
    global token
    funcName = ID()
    # create and add a function entity to the last scope
    entity = functionEntity(funcName, funcType)
    addEntity(entity, "func")
    # add a new scope for the function
    addScope()
    if token.tkType == "groupSymbol" and token.content == "(":
        token = lexAn()
        # get parameter types and pass them to the function entity
        entity.arguments = formalparlist()
        # ')' is checked in formalparlist()
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
        if token.content == "function":
            token=lexAn()
            subprogram("func")
        else:
            token=lexAn()
            subprogram("proc")
        
        
def block(programName, isMain):
    global token
    declarations()
    subprograms()
    if isMain:
        # TODO add Lmain label
        pass
    else:
        # the function entity is not on the last scope at this point, but on the previous one
        # also, it is the last entity in that scope so far 
        symbolTable[-2].entities[-1].startQuad = nextquad()
    genquad("begin_block", programName, "_", "_")
    statements()
    # block() is common for main and other functions, so we need isMain to know if we must add 'halt'
    if isMain:
        genquad("halt", "_", "_", "_")
    genquad("end_block", programName, "_", "_")
    translateBlock(isMain)
    # function ended, remove it's scope from the symbol table
    removeScope()


def program():
    global token
    if token.tkType == "keyword" and token.content == "program":
        token = lexAn()
        programName = ID()
        # add scope to symbol table for main
        addScope()
        # add initial jump to main in assembly
        assemblyList.append("L0:\t\t" + "b Lmain\n")
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

########## Gets file to compile ##########
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

fileName = sys.argv[1][:-3]

# prepare 1st token for syntax analyzer
token = lexAn()
synAn()

# while token.tkType != "terminator":
#     print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)
#     token = lexAn()
# print("LINE: " + ("%-10s" % lineCounter) + "TYPE: " + ("%-17s" % token.tkType) + "TOKEN:", token.content)

sourceFile.close()

########## create intermediate-code file (.int) ##########
try:
    intFile = open(fileName + ".int", "w")
except:
    sys.exit("Error occured in intermediate-code file creation")
for num, quad in enumerate(quadList):
    label = str(num + 1) + ": "
    intFile.write(label + str(quad[0]) + " " + str(quad[1]) + " " + str(quad[2]) + " " + str(quad[3]) + "\n")

intFile.close()
print("Generated '" + fileName + ".int" + "' successfully")

########## create C code file (if source code only has a main function) ##########

# a list with all the program variables (including temporary ones)
variableList = []
# a list with all the C commands
cList = []
# a flag to mark whether the program contains another function or not
hasFunction = False

for num, quad in enumerate(quadList):
    
    lineContent = ""
    label = "L_" + str(num + 1) + ": "
    lineContent += label
    
    qType = str(quad[0])
    op1 = str(quad[1])
    op2 = str(quad[2])
    resTarget = str(quad[3])

    quadStr = qType + " " + op1 + " " + op2 + " " + resTarget

    if qType == "begin_block":
        lineContent += "\n"
        # continue will skip the rest of the for loop, so we need to append the label here
        cList.append(lineContent)
        continue
    
    elif qType == ":=":
        lineContent += (resTarget + "=" + op1 + "; //(" + quadStr + ")\n")
    
    elif qType in "+-*/":
        lineContent += (resTarget + "=" + op1 + qType + op2 + "; //(" + quadStr + ")\n")

    elif qType in "<><=>=":

        # fix different operators
        if qType == "=":
            qType = "=="
        elif qType == "<>":
            qType = "!="
        
        lineContent += ("if (" + op1 + qType + op2 + ") goto L_" + resTarget + "; //(" + quadStr + ")\n")

    elif qType == "jump":
        lineContent += ("goto L_" + resTarget + "; //(" + quadStr + ")\n")

    elif qType == "inp":
        lineContent += ("scanf(\"%d\",&" + op1 + "); //(" + quadStr + ")\n")

    elif qType == "out":
        lineContent += ("printf(\"%d\\n\"," + op1 + "); //(" + quadStr + ")\n")
    
    elif qType == "halt":
        # this last print is required, gcc throws error when last label is empty
        lineContent += "printf(\"Execution finished\\n\");\n"
        # break will skip the rest of the for loop, so we need to append the line here
        cList.append(lineContent)
        break

    else:
        hasFunction = True
        print("Source code contains function/method other than main, C file will not be created")
        break

    # add generated line to the list
    cList.append(lineContent)

    # add new variables to the list (variables always start with a letter)
    if op1[0] in letters and op1 not in variableList:
        variableList.append(op1)
    
    elif op2[0] in letters and op2 not in variableList:
        variableList.append(op2)

    elif resTarget[0] in letters and resTarget not in variableList:
        variableList.append(resTarget)


if hasFunction == False:

    try:
        cFile = open(fileName + ".c", "w")
    except:
        sys.exit("Error occured in C-code file creation")

    cFile.write("#include <stdio.h>\n\n")
    cFile.write("int main()\n{\n")
    cFile.write("\tint " + ",".join(variableList) + ";\n")
    for line in cList:
        cFile.write("\t" + line)
    cFile.write("}")

    cFile.close()
    print("Generated '" + fileName + ".c" + "' successfully")
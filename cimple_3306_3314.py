# Giorgos Papadatos 3306 cs03306
# Athanasios Papias 3314 cs03314

# Thanasi check oti einai swsta ta apo panw

# Module to read command-line arguments
import sys

# Token class used by lexical analyzer
class Token:
    def __init__(self, type, content):
        self.type = type
        self.content = content

# Displays error message to user with required info
# def errorHandler():

# Lexical Analyzer
# def lexAn():
#     currentState = ""
    
#     return word

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

print("program finished")
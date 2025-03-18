# author: Michal Belovec, xbelov04

import re, sys, xml.etree.ElementTree as ET, argparse


class Item:
    def __init__(self, argumentValue, argumentType):
        self.value = argumentValue
        self.type = argumentType
class Argument:
    def __init__(self, argumentValue, argumentType):
        self.value = argumentValue
        self.type = argumentType
    def getValue(self):
        return self.value
    def getType(self):
        return self.type

class Instruction:
    def __init__(self, instructionName, instructionOrder, instructionLine):
        self.name = instructionName
        self.order = instructionOrder
        self.line = instructionLine
        self.arguments = []
    def getName(self):
        return self.name
    def getOrder(self):
        return self.order
    def getLine(self):
        return self.line
    def addArgument(self, argument: Argument):
        self.arguments.append(argument)

class Variable:
    def __init__(self, variableName):
        self.name = variableName[3:]    #name of var
        self.frame = variableName[:3]  #GF@, LF@ alebo TF@
        self.value = None
        self.type = None
    def addValues(self, variableValue, variableType): 
        self.value = variableValue
        self.type = variableType
    def getName(self):
        return self.name
    def getValue(self):
        return self.value
    def getFrame(self):
        return self.frame
    def getType(self):
        return self.type
    def __str__(self):
        return f"{self.name}, {self.value}, {self.type}"
    
class Label:
    def __init__(self, labelName, labelLine):
        self.name = labelName
        self.line = labelLine

class Program:
    def __init__(self):
        self.instructions = []
        self.labels = []
        self.gf = [] # global frame
        self.lf = None  # local frame
        self.tf = None  # temporary frame
        self.frameStack = []    # stack for frames
        self.callStack = [] # stack for calls
        self.dataStack = [] # stack for data
    
    #instructions
    def addInstruction(self, instruction: Instruction):
        self.instructions.append(instruction)

    #labels
    def addLabel(self, label: Label):
        self.labels.append(label)

    #global frame
    def addGF(self, var: Variable):
        self.gf.append(var)
    def existedGF(self, var: Variable):
        for j in self.gf:
            if var.getName() == j.name:
                sys.stderr.write("ERROR: Attempt to redefine variable.\n")
                exit(52)

    #local frame
    def initLF(self):
        self.lf = []
    def addLF(self, var: Variable):
        if self.lf is None:
            sys.stderr.write("ERROR: Local rame doesn't exist.\n")
            exit(55)
        self.lf.append(var)
    def existedLF(self, var: Variable):
        if self.lf is None:
            sys.stderr.write("ERROR: Local rame doesn't exist.\n")
            exit(55)
        for j in self.lf:
            if var.getName() == j.name:
                sys.stderr.write("ERROR: Attempt to redefine variable.\n")
                exit(52)

    #temporary frame
    def initTF(self):
        self.tf = []
    def addTF(self, var: Variable):
        if self.tf is None:
            sys.stderr.write("ERROR: Temporary frame doesn't exist.\n")
            exit(55)
        self.tf.append(var)
    def existedTF(self, var: Variable):
        if self.tf is None:
            sys.stderr.write("ERROR: Temporary frame doesn't exist.\n")
            exit(55)
        for j in self.tf:
            if var.getName() == j.name:
                sys.stderr.write("ERROR: Attempt to redefine variable.\n")
                exit(52)

# constants
argVar = ("var")
argSymb = ("int", "string", "bool", "nil", "var")
argInt = ("int", "var")
argString = ("string", "var")
argBool = ("bool", "var")
argNil = ("nil", "var")
argLabel = ("label")
argType = ("type")

def fix(word: str) -> str:
    return re.sub("[ \t\n]*", "", word)

def checkLabel(name: str):
    for g in p.labels:
        if g.name == name:
            exit(52)

def checkType(instruction: Instruction, num: int, arg1, arg2, arg3):
    
    if arg1 is None:
        return
    if instruction.arguments[0].type not in arg1:
            sys.stderr.write("ERROR: Wrong type of instruction argument.\n")
            exit(53)
    if arg2 is None:
        return
    if instruction.arguments[1].type not in arg2:
            sys.stderr.write("ERROR: Wrong type of instruction argument.\n")
            exit(53)
    if arg3 is None:
        return
    if instruction.arguments[2].type not in arg3:
            sys.stderr.write("ERROR: Wrong type of instruction argument.\n")
            exit(53)

def gfIndex(var: str):
    index = 0
    for v in p.gf:
        if v.name == var:
            return index
        index = index + 1
    sys.stderr.write("ERROR: Variable was not defined.\n")
    exit(54)

def lfIndex(var: str):
    index = 0
    if p.lf is None: exit(55)
    for v in p.lf:
        if v.name == var:
            return index
        index = index + 1
    sys.stderr.write("ERROR: Variable was not defined.\n")
    exit(54)
def tfIndex(var: str):
    index = 0
    if p.tf is None: exit(55)
    for v in p.tf:
        if v.name == var:
            return index
        index = index + 1
    sys.stderr.write("ERROR: Variable was not defined.\n")
    exit(54)

def find(var: str) -> Variable:
    name = var[3:]
    frame = var[:3]
    found = False
    index = 0
    if frame == "GF@":
        for v in p.gf:
            if v.name == name:
                found = True
                break
            index = index + 1
        if found is False:
            sys.stderr.write("ERROR: Variable was not defined.\n")
            exit(54)
        return p.gf[index]

    if frame == "LF@":
        if not p.existedLF:
            sys.stderr.write("ERROR: Local frame isn't existed.\n")
            exit(55)
        for v in p.lf:
            if v.name == name:
                found = True
                break
            index = index + 1
        if found is False:
            sys.stderr.write("ERROR: Variable was not defined.\n")
            exit(54)
        return p.lf[index]

    if frame == "TF@":
        if not p.existedTF:
            sys.stderr.write("ERROR: Local frame isn't existed.\n")
            exit(55)
        for v in p.tf:
            if v.name == name:
                found = True
                break
            index = index + 1
        if found is False:
            sys.stderr.write("ERROR: Variable was not defined.\n")
            exit(54)
        return p.tf[index]

def indexWrite(val, typ, var):
    frame = var[:3]
    name = var[3:]
    if frame == 'GF@':
        index = gfIndex(name)
        p.gf[index].addValues(val, typ)
        # print(p.gf[index])
    elif frame == 'LF@':
        index = lfIndex(name)
        p.lf[index].addValues(val, typ)
        # print(p.lf[index])
    elif frame == 'TF@':
        index = tfIndex(name)
        p.tf[index].addValues(val, typ)
        # print(p.tf[index])

def nonDeclared(var: Variable):
    if var.value is None or var.type is None:
        sys.stderr.write("ERROR: Undeclared variable.\n")
        exit(56)

#instructions
def MOVE(instruction: Instruction):
    

    val = instruction.arguments[1].value
    typ = instruction.arguments[1].type

    indexWrite(val, typ, instruction.arguments[0].value)


    # else:   #it is int, bool, string or nil

def CREATEFRAME(instruction: Instruction):
    p.initTF()

def PUSHFRAME(instruction: Instruction):
    if p.tf is None:
        sys.stderr.write("ERROR: Temporary frame does not exist.\n")
        exit(55)
    
    p.frameStack.append(p.lf)
    p.lf = p.tf
    p.tf = None

def POPFRAME(instruction: Instruction):
    if p.lf is None:
        sys.stderr.write("ERROR: Temporary frame does not exist.\n")
        exit(55)
    
    p.tf = p.lf
    length = len(p.frameStack)
    if length == 0:
        sys.stderr.write("ERROR: Frame stack is empty.\n")
        exit(56)
    p.lf = p.frameStack[len(p.frameStack)-1]
    p.frameStack.pop()

def DEFVAR(instruction: Instruction):

    var = Variable(instruction.arguments[0].value)
    if var.frame == "GF@":
        p.existedGF(var)
        p.addGF(var)
    elif var.frame == "LF@":
        p.existedLF(var)
        p.addLF(var)
    elif var.frame == "TF@":
        p.existedTF(var)
        p.addTF(var)
    else:
        sys.stderr.write("ERROR: Wrong frame of variable.\n")
        exit(52)

def CALL(instruction: Instruction):
    global i
    p.callStack.append(instruction.line)
    val = instruction.arguments[0].value
    for j in p.labels:
        if j.name == val:
            i = j.line - 1
            return
    exit(52)

def RETURN(instruction: Instruction):
    global i
    if len(p.callStack) == 0:
        sys.stderr.write("ERROR: Call stack is empty.\n")
        exit(56)
    i = p.callStack[len(p.callStack)-1]-1
    p.callStack.pop()

def PUSHS(instruction: Instruction):
    if instruction.arguments[0].type == "var":
        var = find(instruction.arguments[0].value)
        nonDeclared(var)
        typ = var.type
        val = var.value
    else:
        typ = instruction.arguments[0].type
        val = instruction.arguments[0].value

    item = Item(val, typ)
    p.dataStack.append(item)

def POPS(instruction: Instruction):
    if len(p.dataStack) == 0:
        sys.stderr.write("ERROR: Data stack is empty.\n")
        exit(56)
    
    item = p.dataStack[len(p.dataStack)-1]
    p.dataStack.pop()
    indexWrite(item.value, item.type, instruction.arguments[0].value)

def ADD(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 != 'int' or typ2 != 'int':
        exit(53)

    try:
        val1 = int(val1)
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    indexWrite(val1+val2, 'int', instruction.arguments[0].value)
    

def SUB(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 != 'int' or typ2 != 'int':
        exit(53)

    try:
        val1 = int(val1)
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    indexWrite(val1-val2, 'int', instruction.arguments[0].value)

def MUL(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 != 'int' or typ2 != 'int':
        exit(53)

    try:
        val1 = int(val1)
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    indexWrite(val1*val2, 'int', instruction.arguments[0].value)

def IDIV(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 != 'int' or typ2 != 'int':
        exit(53)

    try:
        val1 = int(val1)
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    if val2 == 0:
        sys.stderr.write("ERROR: Can't divide with zero.\n")
        exit(57)

    indexWrite(val1//val2, 'int', instruction.arguments[0].value)

def LT(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value
    
    if(typ1 == "nil" or typ2 == "nil"):
        sys.stderr.write("ERROR: Wrong type - nil.\n")
        exit(53)

    if typ1 != typ2:
        exit(53)

    if typ1 == "bool":
        if val1 == "false" and val2 == "true":
            indexWrite("true", "bool", instruction.arguments[0].value)
            return
        else:  
            indexWrite("false", "bool", instruction.arguments[0].value)
            return

    if typ1 == "int" and typ2 == "int":
        try:
            val1 = int(val1)
            val2 = int(val2)
        except:
            sys.stderr.write("ERROR: Wrong value of int.\n")
            exit(32)
    if val1<val2:
        indexWrite("true", "bool", instruction.arguments[0].value)
    else:
        indexWrite("false", "bool", instruction.arguments[0].value)

def GT(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value
    
    if(typ1 == "nil" or typ2 == "nil"):
        sys.stderr.write("ERROR: Wrong type - nil.\n")
        exit(53)

    if typ1 != typ2:
        exit(53)

    if typ1 == "bool":
        if val1 == "true" and val2 == "false":
            indexWrite("true", "bool", instruction.arguments[0].value)
            return
        else:  
            indexWrite("false", "bool", instruction.arguments[0].value)
            return

    if typ1 == "int" and typ2 == "int":
        try:
            val1 = int(val1)
            val2 = int(val2)
        except:
            sys.stderr.write("ERROR: Wrong value of int.\n")
            exit(32)
    if val1>val2:
        indexWrite("true", "bool", instruction.arguments[0].value)
    else:
        indexWrite("false", "bool", instruction.arguments[0].value)

def EQ(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value
        
    if typ1 == 'nil' or typ2 == 'nil':
        if typ1 == typ2:
            indexWrite("true", "bool", instruction.arguments[0].value)
            return
        else:
            indexWrite("false", "bool", instruction.arguments[0].value)
            return

    if typ1 == typ2:
        if typ1 == 'int':
            try:
                val1 = int(val1)
                val2 = int(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of int.\n")
                exit(32)
        if typ1 == 'string':
            try:
                val1 = str(val1)
                val2 = str(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of string.\n")
                exit(32)

    else:
        exit(53)

    if val1 == val2:
        indexWrite("true", "bool", instruction.arguments[0].value)
    else:
        indexWrite("false", "bool", instruction.arguments[0].value)

def AND(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "bool":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "bool":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if val1 == "true" and val2 == "true":
        indexWrite("true", 'bool', instruction.arguments[0].value)
    else:
        indexWrite("false", 'bool', instruction.arguments[0].value)

def OR(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "bool":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "bool":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if val1 == "true" or val2 == "true":
        indexWrite("true", 'bool', instruction.arguments[0].value)
    else:
        indexWrite("false", 'bool', instruction.arguments[0].value)

def NOT(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "bool":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if val1 == "true":
        indexWrite("false", 'bool', instruction.arguments[0].value)
    else:
        indexWrite("true", 'bool', instruction.arguments[0].value)

def INT2CHAR(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var = find(instruction.arguments[1].value)
        nonDeclared(var)
        typ = var.type
        if typ != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val = var.value
    else:
        typ = instruction.arguments[1].type
        val = instruction.arguments[1].value

    try:
        val = chr(int(val))
    except:
        sys.stderr.write("ERROR: Wrong type of operand.\n")
        exit(58)

    indexWrite(val, "string", instruction.arguments[0].value)

def STRI2INT(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "string":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    try:
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)
    
    try:
        val1 = ord(val1[val2])
    except:
        sys.stderr.write("ERROR: Index is too high.\n")
        exit(58)

    indexWrite(val1, "string", instruction.arguments[0].value)

    

def READ(instruction: Instruction):
    

    #type - int, bool, string or nil
    typ = instruction.arguments[1].value
    if typ not in ["int", "bool", "string", "nil"]:
        sys.stderr.write("ERROR: Wrong value of type.\n")
        exit(32)
    try: val = input()
    except: 
        val = "nil"
        typ = "nil"

    if typ == "int":
        try: int(val)
        except:
            val = "nil"
            typ = "nil"
    elif typ == "string":
        try: str(val)
        except:
            val = "nil"
            typ = "nil"
    elif typ == "bool":
        if val.upper() != "TRUE":
            val = "false"
        else:
            val = "true"

    indexWrite(val, typ, instruction.arguments[0].value)



def WRITE(instruction: Instruction):
    if instruction.arguments[0].type != "var":
        val = instruction.arguments[0].value
        typ = instruction.arguments[0].type
    else:
        attr = find(instruction.arguments[0].value)
        nonDeclared(attr)
        val = attr.value
        typ = attr.type
    
    val = str(val)
    if typ == "nil":
        val = ""
    elif typ == "string":
        val = val.replace("\\010", "\n")
        val = val.replace("\\032", " ")
        val = val.replace("\\035", "#")
        val = val.replace("\\092", "\\")
    
    print(val, end="")

def CONCAT(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if typ1 != "string":
        sys.stderr.write("ERROR: Wrong type of operand.\n")
        exit(53)

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ2 != "string":
        sys.stderr.write("ERROR: Wrong type of operand.\n")
        exit(53)
    
    indexWrite(val1+val2, "string", instruction.arguments[0].value)

def STRLEN(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value
    
    if typ1 != "string":
        sys.stderr.write("ERROR: Wrong type of operand.\n")
        exit(53)
    
    indexWrite(len(val1), "int", instruction.arguments[0].value)

def GETCHAR(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "string":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value
    
    try:
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)
    
    try:
        res = val1[val2]
    except:
        sys.stderr.write("ERROR: Index is too high.\n")
        exit(58)

    indexWrite(res, "string", instruction.arguments[0].value)

def SETCHAR(instruction: Instruction):
    if instruction.arguments[0].type == "var":
        var1 = find(instruction.arguments[0].value)
        nonDeclared(var1)
        typ1 = var1.type
        if typ1 != "string":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val1 = var1.value
    else:
        typ1 = instruction.arguments[0].type
        val1 = instruction.arguments[0].value

    if instruction.arguments[1].type == "var":
        var2 = find(instruction.arguments[1].value)
        nonDeclared(var2)
        typ2 = var2.type
        if typ2 != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val2 = var2.value
    else:
        typ2 = instruction.arguments[1].type
        val2 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var3 = find(instruction.arguments[2].value)
        nonDeclared(var3)
        typ3 = var3.type
        if typ3 != "string":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
        val3 = var3.value
    else:
        typ3 = instruction.arguments[2].type
        val3 = instruction.arguments[2].value

    try:
        val2 = int(val2)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    try:
        val1 = val1[:val2] + val3[0] + val1[val2+1:]
    except:
        sys.stderr.write("ERROR: Index is too high.\n")
        exit(58)

    indexWrite(val1, "string", instruction.arguments[0].value)


def TYPE(instruction: Instruction):
    if instruction.arguments[1].type == "var":
        var = find(instruction.arguments[1].value)
        if var.value is None or var.type is None:
            val = ''
            typ = ''
        else:
            val = var.value
            typ = var.type
    else:
        typ = instruction.arguments[1].type
        val = instruction.arguments[1].value

    if typ not in ["int", "string", "bool", "nil", '']:
        sys.stderr.write("ERROR: Wrong type of operand.\n")
        exit(57)

    indexWrite(typ, "string", instruction.arguments[0].value)
    

def LABEL(instruction: Instruction):
    return

def JUMP(instruction: Instruction):
    global i
    val = instruction.arguments[0].value
    for j in p.labels:
        if j.name == val:
            i = j.line - 1
            return
    sys.stderr.write("ERROR: Wrong label.\n")
    exit(52)    

def JUMPIFEQ(instruction: Instruction):
    global i
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 == 'nil' or typ2 == 'nil':
        val = instruction.arguments[0].value
        for j in p.labels:
            if j.name == val:
                i = j.line
                return

    if typ1 == typ2:
        if typ1 == 'int':
            try:
                val1 = int(val1)
                val2 = int(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of int.\n")
                exit(32)
        if typ1 == 'string':
            try:
                val1 = str(val1)
                val2 = str(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of int.\n")
                exit(32)
    if typ1 != typ2:
        sys.stderr.write("ERROR: Different types of operands.\n")
        exit(53)
    if val1==val2:
        val = instruction.arguments[0].value
        for j in p.labels:
            if j.name == val:
                i = j.line - 1
                return
        sys.stderr.write("ERROR: Wrong label.\n")
        exit(52)
    return 
        

def JUMPIFNEQ(instruction: Instruction):
    global i
    if instruction.arguments[1].type == "var":
        var1 = find(instruction.arguments[1].value)
        nonDeclared(var1)
        typ1 = var1.type
        val1 = var1.value
    else:
        typ1 = instruction.arguments[1].type
        val1 = instruction.arguments[1].value

    if instruction.arguments[2].type == "var":
        var2 = find(instruction.arguments[2].value)
        nonDeclared(var2)
        typ2 = var2.type
        val2 = var2.value
    else:
        typ2 = instruction.arguments[2].type
        val2 = instruction.arguments[2].value

    if typ1 == 'nil' or typ2 == 'nil':
        val = instruction.arguments[0].value
        for j in p.labels:
            if j.name == val:
                i = j.line
                return

    if typ1 == typ2:
        if typ1 == 'int':
            try:
                val1 = int(val1)
                val2 = int(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of int.\n")
                exit(32)
        if typ1 == 'string':
            try:
                val1 = str(val1)
                val2 = str(val2)
            except:
                sys.stderr.write("ERROR: Wrong value of int.\n")
                exit(32)
    if typ1 != typ2:
        sys.stderr.write("ERROR: Different types of operands.\n")
        exit(53)
    if val1!=val2:
        val = instruction.arguments[0].value
        for j in p.labels:
            if j.name == val:
                i = j.line - 1
                return
        sys.stderr.write("ERROR: Wrong label.\n")
        exit(52)
    return

def EXIT(instruction: Instruction):
    if instruction.arguments[0].type != "var":
        val = instruction.arguments[0].value
        typ = instruction.arguments[0].type
    else:
        attr = find(instruction.arguments[0].value)
        nonDeclared(attr)
        val = attr.value
        typ = attr.type
    
    if typ != "int":
            sys.stderr.write("ERROR: Wrong type of operand.\n")
            exit(53)
    
    try: val = int(val)
    except:
        sys.stderr.write("ERROR: Wrong value of int.\n")
        exit(32)

    if val >= 0 and val < 50:
        exit(val)
    else:
        sys.stderr.write("ERROR: Non-valid exit value.\n")
        exit(57)

def DPRINT(instruction: Instruction):
    if instruction.arguments[0].type != "var":
        val = instruction.arguments[0].value
        typ = instruction.arguments[0].type
    else:
        attr = find(instruction.arguments[0].value)
        nonDeclared(attr)
        val = attr.value
        typ = attr.type

    if val is None: val = ""
    sys.stderr.write(val)

def BREAK(instruction: Instruction):
    sys.stderr.write("Position in code: " + str(instruction.line) + "\n")
    sys.stderr.write("Global frame: \n")
    for j in p.gf:
        sys.stderr.write(str(j) + "\n")
 

validInst = { 
    "MOVE": {"name": MOVE, "argv": 2, "arg1": argVar, "arg2": argSymb, "arg3": None},
    "CREATEFRAME": {"name": CREATEFRAME, "argv": 0, "arg1": None, "arg2": None, "arg3": None},
    "PUSHFRAME": {"name": PUSHFRAME, "argv": 0, "arg1": None, "arg2": None, "arg3": None},
    "POPFRAME": {"name": POPFRAME, "argv": 0, "arg1": None, "arg2": None, "arg3": None},
    "DEFVAR": {"name": DEFVAR, "argv": 1, "arg1": argVar, "arg2": None, "arg3": None},
    "CALL": {"name": CALL, "argv": 1, "arg1": argLabel, "arg2": None, "arg3": None},
    "RETURN": {"name": RETURN, "argv": 0, "arg1": None, "arg2": None, "arg3": None},
    "PUSHS": {"name": PUSHS, "argv": 1, "arg1": argSymb, "arg2": None, "arg3": None},
    "POPS": {"name": POPS, "argv": 1, "arg1": argVar, "arg2": None, "arg3": None},
    "ADD": {"name": ADD, "argv": 3, "arg1": argVar, "arg2": argInt, "arg3": argInt},
    "SUB": {"name": SUB, "argv": 3, "arg1": argVar, "arg2": argInt, "arg3": argInt},
    "MUL": {"name": MUL, "argv": 3, "arg1": argVar, "arg2": argInt, "arg3": argInt},
    "IDIV": {"name": IDIV, "argv": 3, "arg1": argVar, "arg2": argInt, "arg3": argInt},
    "LT": {"name": LT, "argv": 3, "arg1": argVar, "arg2": argSymb, "arg3": argSymb},
    "GT": {"name": GT, "argv": 3, "arg1": argVar, "arg2": argSymb, "arg3": argSymb},
    "EQ": {"name": EQ, "argv": 3, "arg1": argVar, "arg2": argSymb, "arg3": argSymb},
    "AND": {"name": AND, "argv": 3, "arg1": argVar, "arg2": argBool, "arg3": argBool},
    "OR": {"name": OR, "argv": 3, "arg1": argVar, "arg2": argBool, "arg3": argBool},
    "NOT": {"name": NOT, "argv": 2, "arg1": argVar, "arg2": argBool, "arg3": None},
    "INT2CHAR": {"name": INT2CHAR, "argv": 2, "arg1": argVar, "arg2": argInt, "arg3": None},
    "STRI2INT": {"name": STRI2INT, "argv": 3, "arg1": argVar, "arg2": argString, "arg3": argInt},
    "READ": {"name": READ, "argv": 2, "arg1": argVar, "arg2": argType, "arg3": None},
    "WRITE": {"name": WRITE, "argv": 1, "arg1": argSymb, "arg2": None, "arg3": None},
    "CONCAT": {"name": CONCAT, "argv": 3, "arg1": argVar, "arg2": argSymb, "arg3": argSymb},
    "STRLEN": {"name": STRLEN, "argv": 2, "arg1": argVar, "arg2": argString, "arg3": None},
    "GETCHAR": {"name": GETCHAR, "argv": 3, "arg1": argVar, "arg2": argString, "arg3": argInt},
    "SETCHAR": {"name": SETCHAR, "argv": 3, "arg1": argVar, "arg2": argInt, "arg3": argString},
    "TYPE": {"name": TYPE, "argv": 2, "arg1": argVar, "arg2": argSymb, "arg3": None},
    "LABEL": {"name": LABEL, "argv": 1, "arg1": argLabel, "arg2": None, "arg3": None},
    "JUMP": {"name": JUMP, "argv": 1, "arg1": argLabel, "arg2": None, "arg3": None},
    "JUMPIFEQ": {"name": JUMPIFEQ, "argv": 3, "arg1": argLabel, "arg2": argSymb, "arg3": argSymb},
    "JUMPIFNEQ": {"name": JUMPIFNEQ, "argv": 3, "arg1": argLabel, "arg2": argSymb, "arg3": argSymb},
    "EXIT": {"name": EXIT, "argv": 1, "arg1": argInt, "arg2": None, "arg3": None},
    "DPRINT": {"name": DPRINT, "argv": 1, "arg1": argSymb, "arg2": None, "arg3": None},
    "BREAK": {"name": BREAK, "argv": 0,"arg1": None, "arg2": None, "arg3": None},
    
 }

def parseArgs():
    if(len(sys.argv[1:])>2):
        sys.stderr.write("ERROR: Wrong number of arguments.\n")
        exit(11)
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('--help')
    argparser.add_argument('--source')
    argparser.add_argument('--input')
    args = argparser.parse_args()
    return args





if __name__ == "__main__":
    p = Program()

    args = parseArgs()
    
    if args.help:
        print("IPPcode23 Interpret")
        print("--source         - source file (XML)")
        print("--input          - input file for the program")
        exit(0)
    elif args.source is None and args.input is None:
        sys.stderr.write("ERROR: Source or input file is neccessary.\n")
        exit(10)
    
    if args.source is not None:
        try:
            sF = open(str(args.source), mode = "r")
        except:
            sys.stderr.write("ERROR: Can't open " + args.source + " file.\n")
            exit(10)
    else:
        sF = sys.stdin

    if args.input is not None:
        try:
            iF = open(str(args.input), mode = "r")
        except:
            sys.stderr.write("ERROR: Can't open " + args.input + " file.\n")
            exit(10)
        sys.stdin = iF
    else:
        iF = sys.stdin

    # xml load with xml.etree.ElementTree
    try: root = ET.parse(sF).getroot()
    except:
        sys.stderr.write('ERROR: XML not well-formed.\n')
        exit(31)

    # xml check
    if root.tag != 'program' or root.get('language').upper() != 'IPPCODE23':
        sys.stderr.write('ERROR: Wrong XML - Missing program tag or language is not IPPcode23.\n')
        exit(32)

    root[:] = sorted(root, key=lambda child: int(child.get('order')))

    line = 1

    for inst in root:
        if inst.tag != 'instruction' or inst.get('order') is None:
            sys.stderr.write('ERROR: Wrong XML - Missing instruction tag or order.\n')
            exit(32)
        if validInst.get(str(inst.get('opcode')).upper(), {}).get('name') is None:
            sys.stderr.write('ERROR: Wrong XML -Wrong opcode of instruction.\n')
            exit(32)
        if int(inst.attrib["order"]) <= 0:
            sys.stderr.write('ERROR: Wrong order of instruction.\n')
            exit(32)
        
        inst[:] = sorted(inst, key=lambda child: child.tag)

        instruction = Instruction(inst.attrib["opcode"].upper(), int(inst.attrib["order"]), line)     #create an instrction

        for argument in inst:
            if argument.text is not None:
                arg = Argument(fix(argument.text), argument.attrib['type'])      #create an argument
            else:
                arg = Argument(argument.text, argument.attrib['type'])
            instruction.addArgument(arg)        #add the argument to instruction

        p.addInstruction(instruction)       #add the instruction with arguments to the program class

        if instruction.getName() == "LABEL":
            checkLabel(instruction.arguments[0].value)
            checkType(instruction, 1, argLabel, None, None)
            label = Label(instruction.arguments[0].value, instruction.getLine())
            p.addLabel(label)
        
        line = line + 1

    i = 0
    end = len(p.instructions)

    while i < end:

        op = p.instructions[i].getName()
        argv = validInst[op]["argv"]
        arg1 = validInst[op]["arg1"]
        arg2 = validInst[op]["arg2"]
        arg3 = validInst[op]["arg3"]
        if len(p.instructions[i].arguments) != argv:
            sys.stderr.write('ERROR: Wrong number of instruction arguments.\n')
            exit(52)
        
        checkType(p.instructions[i], argv, arg1, arg2, arg3)
        validInst[op]["name"](p.instructions[i])

        i = i + 1
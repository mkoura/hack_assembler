#!/usr/bin/env python3
# encoding: utf-8


class CommandType:
    A = 1
    C = 2
    L = 3
    INVALID = 100


class Dest:
    NULL = 0
    M = 1
    D = 2
    MD = 3
    A = 4
    AM = 5
    AD = 6
    AMD = 7
    INVALID = 100


class Jump:
    NULL = 0
    JGT = 1
    JEQ = 2
    JGE = 3
    JTL = 4
    JNE = 5
    JLE = 6
    JMP = 7
    INVALID = 100


class Comp:
    C0 = 0
    C1 = 1
    C2 = 2
    C3 = 3
    C4 = 4
    C5 = 5
    C6 = 6
    C7 = 7
    C8 = 8
    C9 = 9
    C10 = 10
    C11 = 11
    C12 = 12
    C13 = 13
    C14 = 14
    C15 = 15
    C16 = 16
    C17 = 17
    C18 = 18
    C19 = 19
    C20 = 20
    C21 = 21
    C22 = 22
    C23 = 23
    C24 = 24
    C25 = 25
    C26 = 26
    C27 = 27
    INVALID = 100


class Parser:

    """Encapsulates access to the input code. Reads an assembly language com-
    mand, parses it, and provides convenient access to the command’s components
    (fields and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, asmfile):
        self.__asmfile = open(asmfile)
        self.curcommand = ""
        self.curtype = ""
        self.dstrtable = {
            'M': Dest.M,
            'D': Dest.D,
            'MD': Dest.MD,
            'A': Dest.A,
            'AM': Dest.AM,
            'AD': Dest.AD,
            'AMD': Dest.AMD,
        }
        self.jstrtable = {
            'JGT': Jump.JGT,
            'JEQ': Jump.JEQ,
            'JGE': Jump.JGE,
            'JTL': Jump.JTL,
            'JNE': Jump.JNE,
            'JLE': Jump.JLE,
            'JMP': Jump.JMP,
        }
        self.cstrtable = {
            '0': Comp.C0,
            '1': Comp.C1,
            '-1': Comp.C2,
            'D': Comp.C3,
            'A': Comp.C4,
            '!D': Comp.C5,
            '!A': Comp.C6,
            '-D': Comp.C7,
            '-A': Comp.C8,
            'D+1': Comp.C9,
            'A+1': Comp.C10,
            'D-1': Comp.C11,
            'A-1': Comp.C12,
            'D+A': Comp.C13,
            'D-A': Comp.C14,
            'A-D': Comp.C15,
            'D&A': Comp.C16,
            'D|A': Comp.C17,
            'M': Comp.C18,
            '!M': Comp.C19,
            '-M': Comp.C20,
            'M+1': Comp.C21,
            'M-1': Comp.C22,
            'D+M': Comp.C23,
            'D-M': Comp.C24,
            'M-D': Comp.C25,
            'D&M': Comp.C26,
            'D|M': Comp.C27,
        }

    def clean(self):
        """Cleaning actions.
        :returns: -

        """
        self.__asmfile.close()

    def begin(self):
        """Seek to the beginning of the file.
        :returns: -

        """
        self.__asmfile.seek(0)

    # @typechecked
    def stripTrailingComment(self, line: str) -> str:
        """Strip trailing comment.

        :line: assembler line
        :returns: string

        """
        try:
            return line[:line.index("//")].strip()
        except ValueError:
            return line

    def hasMoreCommands(self) -> bool:
        """Are there more commands in the input?
        :returns: boolean

        """
        for line in self.__asmfile:
            line = line.strip()
            if (not line) or (line[0:2] == '//'):
                continue
            else:
                self.curcommand = self.stripTrailingComment(line)
                return True

        return False

    def commandType(self) -> int:
        """Returns the type of the current command.
        :returns: integer

        """
        if self.curcommand[0] is '@':
            self.curtype = CommandType.A
        elif self.curcommand[0] is '(' and self.curcommand[-1] is ')':
            self.curtype = CommandType.L
        elif self.curcommand.find('=') or self.curcommand.find(';'):
            self.curtype = CommandType.C
        else:
            raise ValueError("Invalid CommandType")
            self.curtype = CommandType.INVALID

        return self.curtype

    def symbol(self) -> str:
        """Returns the symbol or decimal of current A or L command.
        :returns: string

        """
        symbol = ""
        if self.curcommand[0] is '@':
            symbol = self.curcommand[1:]
        elif self.curcommand[0] is '(' and self.curcommand[-1] is ')':
            symbol = self.curcommand[1:-1]
        return symbol

    def dest(self) -> int:
        """Returns the dest mnemonic in the current C-command.
        :returns: integer

        """
        eindex = self.curcommand.find('=')
        if eindex == -1:
            return Dest.NULL

        dstr = self.curcommand[0:eindex]

        try:
            dest = self.dstrtable[dstr]
        except KeyError:
            raise ValueError("Invalid 'dest'")
            dest = Dest.INVALID

        return dest

    def jump(self) -> int:
        """Returns the jump mnemonic in the current C-command.
        :returns: integer

        """
        jindex = self.curcommand.find(';')
        if jindex == -1:
            return Jump.NULL

        jstr = self.curcommand[jindex + 1:]

        try:
            jump = self.jstrtable[jstr]
        except KeyError:
            raise ValueError("Invalid 'jump'")
            jump = Jump.INVALID

        return jump

    def comp(self) -> int:
        """Returns the comp mnemonic in the current C-command.
        :returns: integer

        """
        cbegin = self.curcommand.find('=')
        cend = self.curcommand.find(';')
        if cbegin:
            cbegin += 1
        else:
            cbegin = 0
        if cend == -1:
            cend = len(self.curcommand)

        cstr = self.curcommand[cbegin:cend]

        try:
            comp = self.cstrtable[cstr]
        except KeyError:
            raise ValueError("Invalid 'comp'")
            comp = Comp.INVALID

        return comp


class Code:

    """Translates Hack assembly language mnemonics into binary codes. """

    def __init__(self):
        self.comptable = {
            Comp.C0: '101010',
            Comp.C1: '111111',
            Comp.C2: '111010',
            Comp.C3: '001100',
            Comp.C4: '110000',
            Comp.C5: '001101',
            Comp.C6: '110001',
            Comp.C7: '001111',
            Comp.C8: '110011',
            Comp.C9: '011111',
            Comp.C10: '110111',
            Comp.C11: '001110',
            Comp.C12: '110010',
            Comp.C13: '000010',
            Comp.C14: '010011',
            Comp.C15: '000111',
            Comp.C16: '000000',
            Comp.C17: '010101',
            Comp.C18: '110000',
            Comp.C19: '110001',
            Comp.C20: '110011',
            Comp.C21: '110111',
            Comp.C22: '110010',
            Comp.C23: '000010',
            Comp.C24: '010011',
            Comp.C25: '000111',
            Comp.C26: '000000',
            Comp.C27: '010101',
        }

    def dest(self, mnem: int) -> str:
        """Returns the binary code of the dest mnemonic.

        :mnem: dest mnemonic
        :returns: string

        """
        bmnem = bin(mnem)[2:]
        while len(bmnem) < 3:
            bmnem = "0" + bmnem

        return bmnem

    def jump(self, mnem: int) -> str:
        """Returns the binary code of the jump mnemonic.

        :mnem: jump mnemonic
        :returns: string

        """
        return self.dest(mnem)

    def comp(self, mnem: int) -> str:
        """Returns the binary code of the comp mnemonic.

        :mnem: comp mnemonic
        :returns: string

        """
        return ("0" if mnem <= 17 else "1") + self.comptable[mnem]


class SymbolTable:

    """Keeps a correspondence between symbolic labels and numeric addresses."""

    def __init__(self):
        self.curaddr = 16
        self.symtable = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576,
        }

    def addEntry(self, symbol, address=-1):
        """Adds the pair ( symbol, address ) to the table.

        :symbol: symbol to add
        :address: corresponding address
        :returns: -

        """
        if not self.contains(symbol):
            if address == -1:
                laddr = self.curaddr
                self.curaddr += 1
            else:
                laddr = address
            self.symtable[symbol] = laddr

    def contains(self, symbol) -> bool:
        """Does the symbol table contain the given symbol?

        :symbol: symbol to check
        :returns: Boolean

        """
        return True if symbol in self.symtable.keys() else False

    def getAddress(self, symbol):
        """Returns the address associated with the symbol.

        :symbol: symbol to get
        :returns: integer

        """
        return self.symtable[symbol]

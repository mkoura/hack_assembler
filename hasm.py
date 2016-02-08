#!/usr/bin/env python3
# encoding: utf-8

from __future__ import print_function
import sys
import os
import libhasm


def firstPass():
    """First pass.
    :returns: -

    """
    parser.begin()
    commCount = 0
    while parser.hasMoreCommands():
        try:
            commType = parser.commandType()
        except ValueError as e:
            raise ValueError("Error parsing command type for {0}: {1}"
                             .format(parser.curcommand, e.message))

        if (commType == libhasm.CommandType.C) or (commType == libhasm.CommandType.A):
            commCount += 1
        elif commType == libhasm.CommandType.L:
            symbol = parser.symbol()
            sym.addEntry(symbol, commCount)
        else:
            raise ValueError("Unknown command type for {0}."
                             .format(parser.curcommand))


def secondPass():
    """Second pass.
    :returns: -

    """
    parser.begin()
    while parser.hasMoreCommands():
        commType = parser.commandType()

        if commType == libhasm.CommandType.C:
            try:
                pcomp = parser.comp()
                pdest = parser.dest()
                pjump = parser.jump()
            except ValueError as e:
                raise ValueError("Error parsing {0}: {1} "
                                 .format(parser.curcommand, e.message))

            cline = "111" + codegen.comp(pcomp) \
                    + codegen.dest(pdest) + codegen.jump(pjump)

            print(cline, file=outfile)
        elif commType == libhasm.CommandType.A:
            symbol = parser.symbol()
            try:
                bsymbol = bin(int(symbol))[2:]
            except ValueError:
                sym.addEntry(symbol)
                try:
                    bsymbol = bin(int(sym.getAddress(symbol)))[2:]
                except ValueError as e:
                    raise ValueError("Cannot parse symbol {0}: {1}"
                                     .format(symbol), e.message)

            while len(bsymbol) < 15:
                bsymbol = "0" + bsymbol

            if len(bsymbol) >= 16:
                raise ValueError("Invalid command: " + parser.curcommand)

            print("0" + bsymbol, file=outfile)


if len(sys.argv) != 2:
    print("{0} takes a hack assembler file as a single argument."
          .format(os.path.basename(sys.argv[0])),
          file=sys.stderr)
    exit(1)

script, infile = sys.argv
infilename, infileext = os.path.splitext(infile)

if infileext != ".asm":
    print("The file extension of the input file has to be 'asm' instead of '{0}'."
          .format(infileext), file=sys.stderr)
    exit(1)

try:
    outfile = open(infilename + ".hack", "w")
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror), file=sys.stderr)
    exit(1)

parser = libhasm.Parser(infile)
codegen = libhasm.Code()
sym = libhasm.SymbolTable()

try:
    firstPass()
    secondPass()
except ValueError as e:
    print("Parsing error: {0}".format(e.message), file=sys.stderr)
    exit(1)

parser.clean()
outfile.close()

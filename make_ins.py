#!/usr/bin/env python3
'''
Converts a Jana2006 m40 file to ShelXL ins format with some modifications. 
Run this script with no arguments for more information.
'''




from textwrap import wrap
from string import ascii_letters
import pdb
import re
import sys


def shx_write(line, outFile):
    '''Writes a string to a file in ShelX format (= for continuation, max
    80 characters.) Note that outFile could be sys.stdout. 
    '''
    lineList = wrap(line, 77, subsequent_indent = ' ')
    for n in range(len(lineList)-1):
        lineList[n] = lineList[n] + ' ='
    for line in lineList: outFile.write(line + '\n')

def fix_param(x, fvarList=[]):
    '''Takes a single parameter from a ShelXL ins file as a string. If it's tied
    to a free variable, it uses the free variable list to calculate the real
    value of the parameter. A number between 5 and 15, which ShelXL interprets
    as "fixed", is returned as a float.
    If the parameter is exactly -1.2 or -1.5, we assume it is a H with riding
    isotropic ADP, and this number is left unchanged. Note that this could
    occasionally cause a problem with an atom on a special position with
    one of its coordinates -1.5.
    '''
    x = float(x)
    decade = int(round(x, -1))
    if abs(x+1.5) < 0.00001 or abs(x+1.2) < 0.00001: return x
    if x > 15:
        return 10 + ((x - decade) * fvarList[decade//10])
    if x < -15:
        return 10 + ((decade - x) * (1 - fvarList[abs(decade)//10]))
    if 5 < x < 15:
        return x
    if -5 < x < 5:
        return x + 10

def get_fp_fpp(sfacList, m40):
    '''Takes a list of SFAC names and the name of an m40 file. Returns a list
    of 3-tuples containing (SFAC name, f', f'').
    '''
    fpList, fppList = [], []
    with open(m40, 'r') as m40File:

        for i in range(6): m40Line = m40File.readline()
        #now m40Line is holding the first fprime line 

        lineCounter = 0

        for sfac in sfacList:
            fpList.append(m40Line[9*lineCounter : 9*(lineCounter+1)])
            lineCounter += 1
            if lineCounter == 6:
                m40Line = m40File.readline()
                lineCounter = 0

        if lineCounter > 0:
            m40Line = m40File.readline()
            lineCounter = 0

        for sfac in sfacList:
            fppList.append(m40Line[9*lineCounter : 9*(lineCounter+1)])
            lineCounter += 1
            if lineCounter == 6:
                m40Line = m40File.readline()
                lineCounter = 0

        return zip(sfacList, fpList, fppList)

def proc_template(insTemplate, m40, outFile):
    sfacList = []
    with open(insTemplate, 'r') as ins:
        for line in ins:

            if 'end template' in line.lower(): 
                outFile.write(line)
                break
            if (
                    not line.split() or
                    len(line) <= 1 or
                    line[0] == ' '
                ):
                outFile.write(line)
                continue

            head = line.split()[0].lower()

            if head == 'sfac':
                for word in line.split()[1:]:
                    if word[0] in ascii_letters: sfacList.append(word)
                    else: break

            if head == 'unit': #then we need to write all the DISP instructions
                for sfac in get_fp_fpp(sfacList, m40):
                    outFile.write('DISP {} {} {}\n'.format(*sfac))

            outFile.write(line)

def proc_m40_atoms(m40, outFile):
    with open(m40, 'r') as inFile:
        line = inFile.readline()
        while line[0] not in ascii_letters:
            line = inFile.readline()

        while 'block' not in line:
            name = line[0:4]
            sfac = line[9:11]
            uType = line[13]
            sof = '{:.5f}'.format(fix_param(line[19:27]))
            x = '{:.5f}'.format(fix_param(line[27:36]))
            y = '{:.5f}'.format(fix_param(line[36:45]))
            z = '{:.5f}'.format(fix_param(line[45:54]))

            line = inFile.readline()

            if uType == '2':
                u11,u22,u33,u12,u13,u23 = ('{:.5f}'.format(
                    fix_param(line[9*n:9*(n+1)])) for n in range(6))
            else:
                u11, u22, u33, u12, u13, u23 = ('{:.5f}'.format(
                    fix_param(line[0:9])), '', '', '', '', '')

            outLine = ('{} {} {} {} {} {} {} {} {} {} {} {}').format(
                name, sfac, x, y, z, sof, u11, u22, u33, u23, u13, u12)
            
            shx_write(outLine, outFile)

            line = inFile.readline()

        outFile.write('hklf 4\n')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('''
Usage: make_ins.py template m40

Converts a Jana2006 m40 file with f', f'' refinement ON into ShelXL ins format. 
Reads f' and f'' from the m40 and writes them as DISP instructions. Reads all
atoms from the m40, FREEZES ALL THEIR PARAMETERS, and writes them to the ins
file. 

The first input file, template, should have all the lines you wish your final 
ins file to contain, except for disp instructions, up to the first atom. This
may be a regular ShelXL ins file, but place the line: 'REM end template' before
the first atom. Note that the order of atoms given in the ShelXL SFAC 
instructions must match the order in the Jana2006 structure (found in the m50
file as 'chemform'). When several atoms of the same type have different 
anomalous scattering factors, they should be given on separate lines using the
long form of the SFAC instruction, which may be generated using WinGX DATABASE.

The second input file is the m40 file.

The output is written to stdout by default and can be written to a file using:

    make_ins.py template m40 > file.ins
''')

    else:
        template = sys.argv[1]
        m40 = sys.argv[2]
        outFile = sys.stdout
        proc_template(template, m40, outFile)
        proc_m40_atoms(m40, outFile)





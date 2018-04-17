#!/usr/local/bin/python3
'''Reads a ShelXL .ins file and writes Jana2006 equations and keep instructions
to constrain all ADP components to remain in a constant ratio to the very first
one in the ins file. Thus, in the Jana2006 refinement, all ADPs will keep their
original shapes and relative sizes but will be allowed to scale up or down 
uniformly. This is intended to model the effects of beam damage using a single
scalar parameter.

Call this from the command line with the name of your ins file and the atom 
types you wish to constrain. For example:

$ writeequations.py insfile co se p c h

will read the file insfile.ins and generate equations and/or keep instructions 
that relate U11 for the very first Co, Se, P, C, or H atom in the file to all 
following ADP components for those atom types. Riding ADPs (as for hydrogen
atoms) generate keep instructions; all free ADPs (anisotropic or isotropic) 
are converted to equations.

The output is stored in two files, insfile.equ and insfile.keep. The contents
of both files may be added to the "refine" section of the Jana2006 m50 file.
'''

import sys, re




def main():
    atTypes = '|'.join(sys.argv[2:])
    atSearchExp = re.compile(r'^((?:{})[0-9]+\S*)\s(?i)'.format(atTypes))
    inFile = open(sys.argv[1] + '.ins', 'r')
    outFile = open(sys.argv[1] + '.equ', 'w')
    keepFile = open(sys.argv[1] + '.keep', 'w')
    firstFlag = True
    while True:

        line = inFile.readline()
        if not line: break
        if not atSearchExp.search(line): continue
        if '=' in line:
            line = line[:line.find('=')] + inFile.readline()
        
        atName = atSearchExp.search(line).group(1)
        if firstFlag:
            parentTemp = atName
            firstFlag = False
            firstAtom = atName
            u11 = float(line.split()[6])


            u22Ratio = float(line.split()[7]) / u11
            u33Ratio = float(line.split()[8]) / u11
            u23Ratio = float(line.split()[9]) / u11
            u13Ratio = float(line.split()[10]) / u11
            u12Ratio = float(line.split()[11]) / u11


            outFile.write('equation : u22[{0}] = {1:.6f}*u11[{0}]\n'
                    .format(firstAtom, u22Ratio))
            outFile.write('equation : u33[{0}] = {1:.6f}*u11[{0}]\n'
                    .format(firstAtom, u33Ratio))
            outFile.write('equation : u23[{0}] = {1:.6f}*u11[{0}]\n'
                    .format(firstAtom, u23Ratio))
            outFile.write('equation : u13[{0}] = {1:.6f}*u11[{0}]\n'
                    .format(firstAtom, u13Ratio))
            outFile.write('equation : u12[{0}] = {1:.6f}*u11[{0}]\n'
                    .format(firstAtom, u12Ratio))
            continue



        if float(line.split()[6]) < -.9:
            keepFile.write('keep ADP riding {} {} {}\n'.format(
                parentTemp, abs(float(line.split()[6])), atName))
            continue

        parentTemp = atName
        atName = atSearchExp.search(line).group(1)
        u11Ratio = float(line.split()[6]) / u11
        outFile.write('equation : u11[{}] = {:.6f}*u11[{}]\n'
                .format(atName, u11Ratio, firstAtom))
        
        if len(line.split()) >= 12:
            u22Ratio = float(line.split()[7]) / u11
            u33Ratio = float(line.split()[8]) / u11
            u23Ratio = float(line.split()[9]) / u11
            u13Ratio = float(line.split()[10]) / u11
            u12Ratio = float(line.split()[11]) / u11
            outFile.write('equation : u22[{}] = {:.6f}*u11[{}]\n'
                    .format(atName, u22Ratio, firstAtom))
            outFile.write('equation : u33[{}] = {:.6f}*u11[{}]\n'
                    .format(atName, u33Ratio, firstAtom))
            outFile.write('equation : u23[{}] = {:.6f}*u11[{}]\n'
                    .format(atName, u23Ratio, firstAtom))
            outFile.write('equation : u13[{}] = {:.6f}*u11[{}]\n'
                    .format(atName, u13Ratio, firstAtom))
            outFile.write('equation : u12[{}] = {:.6f}*u11[{}]\n'
                    .format(atName, u12Ratio, firstAtom))


    outFile.close()
    keepFile.close()
        

if __name__ == '__main__':
    main()


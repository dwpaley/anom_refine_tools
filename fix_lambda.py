import sys, tempfile, shutil
'''This takes ins files with the wavelength noted in the filename, e.g.:

monoPplus/se/126599_097934/E126599_097934_0m.ins

has lambda=0.97934 A, and puts that wavelength on the CELL line.
'''


ins = sys.argv[1]
tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
wavelength = float(ins[-13:-7])/100000

with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp, open(ins) as f:
    for line in f.readlines():
        if line.lower()[0:4] == 'cell':
            entries = line.split()
            entries[1] = '{:.5f}'.format(wavelength)
            line = ' '.join(entries) + '\n'
        tmp.write(line)

shutil.move(tmp.name, ins)


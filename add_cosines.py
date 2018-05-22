import sys
''' This reads the reflections in an hkl file with run/frame numbers 
and finds the corresponding direction cosines in a raw file. Sadabs appears to 
modify the frame #s (by up to 5-10 frames) when outputting hkl files, so
the reflection with matching indices and run # and the closest frame # is
selected. If no match is found within WARN_TOL or FAIL_TOL frames, a warning
is issued or the job fails.

MAJOR CAVEAT: This was written for a specific task. It will fail if there are
more than 2 runs. It is not guaranteed to work under any circumstance. It's
probably better to use this as inspiration. Please contact the author at
dwp2111@columbia.edu for any necessary help adapting this script.

Having said that, the script should typically be called with:

$ python3 add_cosines.py name.raw name.hkl > name.hkl.cosines

'''

WARN_TOL = 10
FAIL_TOL = 40
reflections = dict()


with open(sys.argv[1]) as f:
    rawFile = f.readlines()

for line in rawFile:
    hkl = line[0:12]
    run = line[31]
    frame = float(line[121:127])
    if run == '2': frame += 360
    if hkl not in reflections.keys():
        reflections[hkl] = []
    reflections[hkl].append({'run': run, 'frame': frame, 'body': line[28:]})


def score(run, frame, match):
    return 10000*(match['run']!=run) + abs(frame - match['frame'])

with open(sys.argv[2]) as f:
    hklFile = f.readlines()

for line in hklFile:
    hkl = line[0:12]
    if hkl == '   0   0   0': break
    run = line[31]
    frame = float(line[35:40])
    matches = [(score(run, frame, match), match) for match in reflections[hkl]]
    best = min(matches)
    if best[0] > WARN_TOL: 
        sys.stderr.write('Alert: {}'.format(hkl))
    if best[0] > FAIL_TOL:
        sys.stderr.write('Warning: {}'.format(hkl))
        break

    else:
        print(line[0:28] + best[1]['body'], end='')
        

    

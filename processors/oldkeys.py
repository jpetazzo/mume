#!/usr/bin/env python
import sys
for line in sys.stdin:
    if ']' not in line: continue
    if line[3] == ' ': continue
    flags, line = line.split(']',1)
    flags = flags[1:].strip()
    line = [e.strip() for e in line.split('\t') if e]
    inventory = line[0]
    use_and_location = line[1]
    if ',' in use_and_location:
        exit_name, location = use_and_location.split(', ',1)
    else:
        exit_name, location = '?', use_and_location
    loads = line[2]
    roomdesc = line[3]
    print '-'
    print '  invdesc:', inventory
    print '  exit:', exit_name
    print '  location:', location
    print '  loads:', loads
    print '  roomdesc:', roomdesc
    if flags:
        print '  flags:', flags
    #idesc = line[0].strip()
    #rdesc = line[-1].strip()
    #tdesc = line[1].strip()
    #print '#sub {^%s$} {%%0 [%s]}'%(idesc,tdesc)
    #print '#sub {^%s$} {%%0 [%s]}'%(rdesc,tdesc)

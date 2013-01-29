#!/usr/bin/env python
for line in open('keysinfo.txt'):
    if ']' not in line: continue
    if line[3] == ' ': continue
    line = line.split(']',1)[1]
    line = [e for e in line.split('\t') if e]
    idesc = line[0].strip()
    rdesc = line[-1].strip()
    tdesc = line[1].strip()
    print '#sub {^%s$} {%%0 [%s]}'%(idesc,tdesc)
    print '#sub {^%s$} {%%0 [%s]}'%(rdesc,tdesc)

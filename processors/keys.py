#!/usr/bin/env python
import sys, yaml

roomdescs = {}
invdescs = {}

def add(h, data, k):
    if k not in data:
        return
    if data[k] not in h:
        h[data[k]] = []
    h[data[k]].append(data)

def makedesc(data):
    o = []
    for k in ['flags', 'exit', 'location', 'loads']:
        if k in data:
            if data[k] is not None:
                o.append(str(data[k]))
    return ', '.join(o)

for data in yaml.load(sys.stdin):
    add(roomdescs, data, 'roomdesc')
    add(invdescs, data, 'invdesc')

def makesubs(h):
    for k,v in h.items():
        if len(v)==1:
            desc = makedesc(v[0])
        if len(v)>1:
            desc = '; '.join(makedesc(d) for d in v)
        print '#sub {^%s$} {%%0 [%s]}'%(k,desc)

makesubs(roomdescs)
makesubs(invdescs)

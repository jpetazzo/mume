#!/usr/bin/env python

def extractinfo(data, field):
    if field not in data: return
    if '/' not in data[field]: return
    value, info = data[field].split('(')
    data[field] = value.strip()
    data['Info'] = info.split(')')[0].strip()


data = open('herbs.txt').read()
paragraphs = data.split('\n\n')
for p in paragraphs:
    data = {}
    for l in p.split('\n'):
        if not l: continue
        if l.startswith('#'): continue
        if ':' not in l:
            print 'Warning: skipping line', repr(l)
            continue
        k,v = l.split(':',1)
        data[k] = v
    if not data: continue
    if 'Name' not in data:
        print 'Missing Name in data', data
        continue
    if 'Description' not in data:
        print 'Missing Description in data', data
        continue
    extractinfo(data, 'Description')
    extractinfo(data, 'Loads')
    if 'Loads' in data: data['Info'] = 'loads: '+data['Info']
    for f in ['Description','Name','Info']:
        data[f] = data[f].strip()
    print '#sub {%s} {%%0 [%s, %s]}'%(data['Description'], data['Name'], data['Info'])


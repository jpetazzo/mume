#!/usr/bin/env python
import sys
import yaml

data = yaml.safe_load(sys.stdin)
for inroom,mob in data.items():
    if mob is None:
        mob = {}
    if '|' in inroom and 'trophy' in mob:
        print('Error: the following mob as "|inroom" + "trophy"; skipping.', file=sys.stderr)
        print(mob, file=sys.stderr)
        continue
    if '|' in inroom:
        inroom = inroom.replace('|','')
    if 'level' in mob and 'warning' in mob:
        label = '[{level}, WARNING: {warning}]'.format(**mob)
    elif 'level' in mob:
        label = '[{level}]'.format(**mob)
    elif 'warning' in mob:
        label = '[WARNING: {warning}]'.format(**mob)
    else:
        label = None
    if label:
        print('#sub {{^{inroom}$}} {{%0 {label} }}'.format(**locals()))

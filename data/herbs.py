#!/usr/bin/env python

import yaml

def extractinfo(herb, field):
    if field not in herb: return
    if '/' not in herb[field]: return
    value, info = herb[field].split('(')
    herb[field] = value.strip()
    herb['info'] = info.split(')')[0].strip()


data = yaml.load(open('herbs.yml'))
for herb in data:
    if 'name' not in herb:
        print 'the following herb has no name:'
        print herb
        continue
    if 'description' not in herb:
        print 'the following herb has no description:'
        print herb
        continue
    herb['info'] = '?'
    extractinfo(herb, 'description')
    extractinfo(herb, 'loads')
    if 'loads' in herb: herb['info'] = 'loads: '+herb['info']
    for f in ['description','name','info']:
        herb[f] = herb[f].strip()
    print '#sub {%s} {%%0 [%s, %s]}'%(herb['description'], herb['name'], herb['info'])


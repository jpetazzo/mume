#!/usr/bin/env python
import fnmatch, re, string, sys, yaml

ignore_lines = set()
ignore_prefixes = set()
ignore_suffixes = set()
ignore_factors = set()
ignore_globs = set()

data_mobs = yaml.load(open('data/mobs.yml'))
ignore_lines |= set(mob['inroom'] for mob in data_mobs if 'inroom' in mob)

data_herbs = yaml.load(open('data/herbs.yml'))
ignore_prefixes |= set(herb['description'].split('(')[0] for herb in data_herbs)

for line in open('data/lines.txt'):
    line = line.strip()
    if not line:
        continue
    if '*' in line[1:-1]:
        ignore_globs.add(line)
        continue
    if line[0] == '*' and line[-1] == '*':
        ignore_factors.add(line[1:-1])
        continue
    if line[0] == '*':
        ignore_suffixes.add(line[1:])
        continue
    if line[-1] == '*':
        ignore_prefixes.add(line[:-1])
        continue
    ignore_lines.add(line)

for line in sys.stdin:
    if line[0] not in string.uppercase:
        continue
    line = line.rstrip()
    if line[-1] != '.':
        continue
    if ' (' in line and ')' in line:
        line = re.sub(r' \([a-z]+\)','',line)
    if line in ignore_lines:
        continue
    if any(line.startswith(prefix) for prefix in ignore_prefixes):
        continue
    if any(line.endswith(suffix) for suffix in ignore_suffixes):
        continue
    if any(factor in line for factor in ignore_factors):
        continue
    if any(fnmatch.fnmatch(line, glob) for glob in ignore_globs):
        continue
    print line

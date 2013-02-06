#!/usr/bin/env python
import fnmatch, re, string, sys, yaml

ignore_lines = set()
ignore_prefixes = set()
ignore_suffixes = set()
ignore_factors = set()
ignore_globs = set()

data_mobs = yaml.load(open('data/mobs.yml'))
ignore_lines |= set(mob.replace('|','')
                    for mob in data_mobs)

data_herbs = yaml.load(open('data/herbs.yml'))
ignore_prefixes |= set(herb['description'].split('(')[0].strip() for herb in data_herbs)

def match_combat_line(line):
    # This is very crude for now.
    weapon_verbs = [
        ['cleave', 'cleaves'],
        ['crush', 'crushes'],
        ['hit', 'hits'],
        ['pierce', 'pierces'],
        ['pound', 'pounds'],
        ['shoot', 'shoots'],
        ['slash', 'slashes'],
        ['smite', 'smites'],
        ['stab', 'stabs'],
        ]
    for verb in weapon_verbs:
        # Regular "hit" line: ATTACKER VERBS TARGET's BODYPART
        if ' '+verb[1]+' ' in line:
            return True
        # Dodge: TARGET swiftly dodges ATTACKER's attempt to VERB PRONOUN.
        if 'attempt to '+verb[0]+' ' in line:
            return True
        # Parry: ATTACKER tires to VERB TARGET, but PRONOUN parries
        if ' tries to '+verb[0]+' ' in line:
            return True
        # Approach: ATTACKER approaches TARGET, trying to VERB PRONOUN.
        if ', trying to '+verb[0]+' ' in line:
            return True
        # Fail: ATTACKER fails to VERB TARGET.
        if ' fails to '+verb[0]+' ' in line:
            return True
    other_verbs = [
        'burns', 'sinks its fangs into', 'avoids being bashed by',
        'sprawling with a powerful', 'tries a kick at',
        'who deftly avoids the',
        ]
    for verb in other_verbs:
        if ' '+verb+' ' in line:
            return True
    # Keep at bay failed: TARGET tries to keep ATTACKER at bay, but fails.
    if ' tries to keep ' in line and ' at bay, but fails.' in line:
        return True
    # Bash to death: ATTACKER bashes TARGET to death.
    if ' bashes ' in line and ' to death.' in line:
        return True
    return False

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
    if match_combat_line(line):
        continue
    print line

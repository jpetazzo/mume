#!/usr/bin/env python
import fnmatch, re, string, sys, yaml


ignore_lines = set()
ignore_prefixes = set()
ignore_suffixes = set()
ignore_factors = set()
ignore_compiled = list()


elements = dict(
    mob = set(),
    Mob = set(),
    possessive = set(('his','her','its')),
    object = set()
    )


data_mobs = yaml.load(open('data/mobs.yml'))
for k,v in data_mobs.items():
    if '|' in k:
        trophy = k.split('|')[0]
        inroom = k.replace('|','')
    else:
        trophy = v and v.get('trophy')
        inroom = k
    ignore_lines.add(inroom)
    if trophy:
        elements['mob'].add(trophy.lower())
        elements['Mob'].add(trophy)


data_herbs = yaml.load(open('data/herbs.yml'))
ignore_prefixes |= set(herb['description'].split('(')[0].strip() for herb in data_herbs)


data_objects = yaml.load(open('data/objects.yml'))
for k,v in data_objects.items():
    if '|' in k:
        ininv = k.split('|')[0].lower()
        inroom = k.replace('|','')
    else:
        ininv = v
        inroom = k
    ignore_lines.add(inroom)
    if ininv:
        elements['object'].add(v)


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
        ' burns ', ' sinks its fangs into ', ' avoids being bashed by ',
        ' sprawling with a powerful bash.', ' tries a kick at ',
        ' who deftly avoids the ', ' is corroded by a splash of acid.',
        ' howls in pain as the claws of ', ' with its poisonous fangs.',
        ' bites ', 'throws a glowing magical missile at ',
        ]
    for verb in other_verbs:
        if verb in line:
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
    if '*' in line[1:-1] or '<' in line:
        # FIXME: we might have to call re.escape()!
        regex = line.replace(r'*','.*')
        for element in elements:
            regex = regex.replace('<'+element+'>',
                                  '(?P<'+element+'>.*)')
        ignore_compiled.append(re.compile(regex))
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
    if line[-1] not in '.?!':
        continue
    if ' (' in line and ')' in line:
        line = re.sub(r' \([A-Za-z]+\)','',line)
    if line in ignore_lines:
        continue
    if any(line.startswith(prefix) for prefix in ignore_prefixes):
        continue
    if any(line.endswith(suffix) for suffix in ignore_suffixes):
        continue
    if any(factor in line for factor in ignore_factors):
        continue
    match = None
    for regex in ignore_compiled:
        match = regex.match(line)
        if match:
            groups = match.groupdict()
            for element in groups:
                if groups[element] not in elements[element]:
                    print '<{0}> {1}'.format(element, groups[element])
            break
    if match:
        continue
    if match_combat_line(line):
        continue
    print line

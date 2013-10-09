#!/usr/bin/env python
import fnmatch, re, string, sys, yaml


ignore_lines = set()
ignore_prefixes = set()
ignore_suffixes = set()
ignore_factors = set()
ignore_compiled = list()


elements = dict(
    actor = set(),
    Actor = set(),
    target = set(),
    Target = set(),
    mob = set(),
    Mob = set(),
    possessive = set(('his','her','its')),
    subject = set(('he','she','it')),
    pronoun = set(('him', 'her', 'it')),
    object = set(),
    Object = set(),
    color = set(('clear', 'violet', 'black', 'yellow', 'purple')),
    Race = set(('Elf', 'Dwarf', 'Half-Elf', 'Orc')),
    fromdir = set(('from the north', 'from the south', 'from the west',
                   'from the east', 'from above', 'from below')),
    direction = set(('north', 'south', 'west', 'east', 'up', 'down')),
    door = set(),
    gauge = set(('full',)),
    key = set(),
    liquid = set(('beer', 'water')),
    unknown = set()
    )


def ignore(line):
    line = line.strip()
    if not line:
        return
    if '*' in line[1:-1] or '<' in line:
        # FIXME: we might have to call re.escape()!
        regex = line.replace(r'*','.*')
        for element in elements:
            regex = regex.replace('<'+element+'>',
                                  '(?P<'+element+'>.*)')
        ignore_compiled.append(re.compile(regex))
        return
    if line[0] == '*' and line[-1] == '*':
        ignore_factors.add(line[1:-1])
        return
    if line[0] == '*':
        ignore_suffixes.add(line[1:])
        return
    if line[-1] == '*':
        ignore_prefixes.add(line[:-1])
        return
    ignore_lines.add(line)


def add_mob(trophy):
    for set_name in ['Actor', 'Target', 'Mob']:
        elements[set_name].add(trophy)
        elements[set_name.lower()].add(trophy.lower())

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
        add_mob(trophy)

def add_char(char):
    for set_name in ['Actor', 'Target', 'Mob']:
        elements[set_name].add(char)
        elements[set_name.lower()].add(char)

data_chars = open('data/chars.txt').read().strip().split()
for char in data_chars:
    add_char(char)


data_herbs = yaml.load(open('data/herbs.yml'))
ignore_prefixes |= set(herb['description'].split('(')[0].strip() for herb in data_herbs)


data_keys = yaml.load(open('data/keys.yml'))
for data_key in data_keys:
    ignore_lines.add(data_key.get('roomdesc'))
    elements['object'].add(data_key.get('invdesc'))


data_objects = yaml.load(open('data/objects.yml'))
for k,v in data_objects.items():
    if '|' in k:
        ininv = k.split('|')[0].lower()
        inroom = k.replace('|','')
    else:
        ininv = v
        inroom = k
    ignore(inroom)
    if ininv:
        elements['object'].add(ininv)


elements['Object'] = set(o.capitalize() for o in elements['object'])


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
        ['whip', 'whips'],
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
        # You fail: You try to VERB TARGET, but PRONOUN parries successfully.
        if (line.startswith('You try to '+verb[0])
            and line.endswith('parries successfully.')):
            return True
    other_verbs = [
        ' burns ', ' cries \'Elbereth Gilthoniel\' and makes ',
        ' sinks its fangs into ', ' avoids being bashed by ',
        ' sprawling with a powerful bash.', ' tries a kick at ',
        ' who deftly avoids the ', ' is corroded by a splash of acid.',
        ' howls in pain as the claws of ', ' with its poisonous fangs.',
        ' bites ', 'throws a glowing magical missile at ',
        ' dodge a bash from ',
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
    ignore(line)


if sys.argv[1:]:
    input = open(sys.argv[1])
else:
    input = sys.stdin
for line in input:
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
                    print '<{0}> {1!r}'.format(element, groups[element])
            break
    if match:
        continue
    if match_combat_line(line):
        continue
    print line

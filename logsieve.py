#!/usr/bin/env python2
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
    damage = set((
        'cleave', 'crush', 'hit', 'pierce', 'pound',
        'shoot', 'slash', 'smite', 'stab', 'whip',
        'cleaves', 'crushes', 'hits', 'pierces', 'pounds',
        'shoots', 'slashes', 'smites', 'stabs', 'whips',
        )),
    bodypart = set((
        'left hindleg', 'right hindleg', 'left hindfoot', 'right hindfoot',
        'left wing', 'right wing',
        'left forefoot', 'right forefoot', 'left foreleg', 'right foreleg',
        'left hand', 'right hand', 'left arm', 'right arm',
        'head', 'body',
        )),
    unknown = set()
    )


def ignore(line):
    line = line.strip()
    if not line:
        return
    if '*' in line[1:-1] or '<' in line:
        # FIXME: we might have to call re.escape()!
        regex = line
        regex = regex.replace('.', '\\.')
        regex = regex.replace('*','.*')
        for element in elements:
            # Skip some special elements that are matched individually
            if element in ('damage', 'bodypart'): continue
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
    elements['Mob'].add(trophy)
    elements['mob'].add(trophy.lower())

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
    elements['Mob'].add(char)
    elements['mob'].add(char)

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
    return
    # This is very crude for now.
    weapon_verbs = [
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

# These should be after everything else, because they can be a bit over-generic.
# (For instance, "You recover two arrows and put them in your quiver" matches!)
ignore("You( barely| lightly|) (?P<damage>[a-z]+) <mob>'s (?P<bodypart>left [a-z]+|right [a-z]+|[a-z]+)( hard| very hard| extremely hard|)( and shatter it| and tickle it|).")
ignore("<Mob>( barely| lightly|) (?P<damage>[a-z]+) your (?P<bodypart>left [a-z]+|right [a-z]+|[a-z]+)( hard| very hard| extremely hard|)( and shatters it| and tickles it|).")
ignore("<Mob> tries to (?P<damage>[a-z]+) you, but your parry is successful.")
ignore("You swiftly dodge <mob>'s attempt to (?P<damage>[a-z]+) you.")

if sys.argv[1:]:
    input = open(sys.argv[1])
else:
    input = sys.stdin
for line in input:
    # Remove ANSI sequences.
    if "\x1b[" in line:
        line = re.sub('\x1b\\[[^m]*m', '', line)
    # If a line starts with something else than an uppercase letter,
    # ignore it. (This leads us to ignore inventory content, as well
    # as room descriptions and multi-line messages.)
    if line[0] not in string.uppercase:
        continue
    line = line.rstrip()
    # Also ignore lines that do not end with a punctuation message.
    # (These are probably multi-line messages as well.)
    if line[-1] not in '.?!':
        continue
    # Remove stuff between parenthesis. Notably, " (glowing)" mentions.
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
    print line

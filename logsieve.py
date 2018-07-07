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
    Race = set(('Elf', 'Dwarf', 'Half-Elf', 'Orc', 'Silvan')),
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
        'left leg', 'right leg', 'left foot', 'right foot',
        'left hand', 'right hand', 'left arm', 'right arm',
        'head', 'body', 'tail',
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

for line in open('data/lines.txt'):
    ignore(line)

# These should be after everything else, because they can be a bit over-generic.
# (For instance, "You recover two arrows and put them in your quiver" matches!)
ignore("You( barely| lightly| strongly|) (?P<damage>[a-z]+) <mob>'s (?P<bodypart>left [a-z]+|right [a-z]+|[a-z]+)( hard| very hard| extremely hard|)( and shatter it| and tickle it|).")
ignore("<Mob>( barely| lightly| strongly|) (?P<damage>[a-z]+) your (?P<bodypart>left [a-z]+|right [a-z]+|[a-z]+)( hard| very hard| extremely hard|)( and shatters it| and tickles it|).")
ignore("You try to (?P<damage>[a-z]+) <mob>, but <subject> parries successfully.")
ignore("<Mob> tries to (?P<damage>[a-z]+) you, but your parry is successful.")
ignore("You swiftly dodge <mob>'s attempt to (?P<damage>[a-z]+) you.")
ignore("<Mob> swiftly dodges your attempt to (?P<damage>[a-z]+) <pronoun>.")
ignore("Your attempt to (?P<damage>[a-z]+) <mob> fails.")
ignore("<Mob> fails to hit you.")
ignore("<Mob> sends you sprawling with a powerful bash.")
ignore("You dodge a bash from <mob> who loses <possessive> balance.")
ignore("<Mob> bites you!")

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
                value = groups[element]
                # The regexes parsing combat actions are imperfect.
                # When there is a line like "A wolf lightly hits your arm",
                # they can interpret the mob name to be "A wolf lightly".
                # This works around the issue.
                if element.lower() == 'mob':
                    if value.split()[-1] in ['barely', 'lightly', 'strongly']:
                        value = value.rsplit(None, 1)[0]
                if value not in elements[element]:
                    print '<{0}> {1!r}'.format(element, value)
            break
    if match:
        continue
    print line

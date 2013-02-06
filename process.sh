#!/bin/sh
processors/mobs.py < data/mobs.yml > tintin/data-mobs.tin
processors/herbs.py < data/herbs.yml > tintin/data-herbs.tin
processors/keys.py < data/keys.txt > tintin/data-keys.tin
#!/usr/bin/env python
import os, sys

all_file = sys.argv[1]
usage_file = sys.argv[2]

modules = []
used = []

with open(all_file, 'r') as all_modules:
  modules = [m.strip() for m in all_modules.read().strip().split('\n')]

with open(usage_file, 'r') as used_modules:
    used = [l.strip().split(' ')[0].split('/', 4)[-1].split('.lua')[0] for l in used_modules if l]
    #used = [m.strip() for m in a.read().strip().split('\n')]
  
unused = list(set(modules).difference(set(used)))
unused.sort()
print('\n'.join(unused))

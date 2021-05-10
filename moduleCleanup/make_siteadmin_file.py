#!/usr/bin/env python
import os, sys

depr_mods_file = sys.argv[1]
depr_message_file = sys.argv[2]

with open(depr_message_file, 'r') as f:
    depr_message = f.read().strip(' \n')

with open(depr_mods_file, 'r') as f:
  modules = [m.strip() for m in f.read().strip().split('\n')]

for module in modules:
    print("%s$:\n%s\n" % (module, depr_message))

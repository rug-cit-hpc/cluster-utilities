#!/usr/bin/env python

# moduleDiff.py
# Made for Python 2.7.5 (default for the Peregrine cluster)
# Author: Klemen Voncina

# This is a little tool to help see differences between installed modules on different architectures.
# Now, you may ask: "Klemen, why is there yet another python tool for this thing that you could probably do some other way?"
# The answer is because I find Python comfortable to use and trying various combinations of listing all of the modules then comparing the lists using 'diff'
# produces output that's more confusing than useful. So here we are.

# There's ways of comparing directories recursively, I realize. But I still think this may  be a better idea because its purpose built for exactly one thing.
# This program will only support pairwise comparison because otherwise its going to be a mess.

import os
import argparse
import sys

colors = {
	'blue' : '\033[94m', # some terminals don't support this so it just looks 'normal'
	'red'  : '\033[91m',
	'bold' : '\033[1m',
	'warn' : '\033[93m', # not sure yet what colour this is
	'end'  : '\033[0m' # if this isn't at the end of the string, the formatting can overflow onto more lines of text
}

# Paths to the different architectures' module locations
arch = {
	'haswell' : '/apps/haswell/modules/all/',
	'sandybridge' : '/apps/sandybridge/modules/all/',
	'skylake' : '/apps/skylake/modules/all/',
}

class Diff():
	# More of a struct to hold things than a class with its own methods
	def __init__(self):
		self.nameDirA = None
		self.nameDirB = None
		self.pathA = None
		self.pathB = None
		self.dirA = None
		self.dirB = None
		self.both = None
		self.onlyA = None
		self.onlyB = None
		#self.versionsA = None
		#self.versionsB = None
		self.versionsOnlyA = None
		self.versionsOnlyB = None
		self.checkErrorA = None
		self.checkErrorB = None

# Steps
# Step 1: list all directories in /apps/<architecture>/modules/all/
# Step 2: Compare those lists. If any big modules are missing, add them to the list of disparities.
# Step 3: For each module that both architectues have, go one directory layer deeper; list versions
# Step 4: Compare versions, if versions are missing, add them to the list of disparities
# Step 5: Produce (then print) list of disparities. Also save to file.

def compare(holder,early_stop):
	# get lists of sub-directories of direcotry A and B
	# Top level directory should not have permission issues.
	# Make them into sets because python has some good default stuff for sets
	holder.dirA = set(os.listdir(holder.pathA))
	holder.dirB = set(os.listdir(holder.pathB))
	# Both - a set of all modules installed on both architectures we're comparing
	holder.both = holder.dirA.intersection(holder.dirB)
	holder.onlyA= holder.dirA.difference(holder.dirB)
	holder.onlyB= holder.dirB.difference(holder.dirA)
	if early_stop: # Early stop only lists the top level directory differences.
		return holder
	# If we don't stop early, then continue on and explore the sub-directories.
	#holder.versionsA = {}
	#holder.versionsB = {}
	holder.versionsOnlyA = {}
	holder.versionsOnlyB = {}
	holder.checkErrorA = []
	holder.checkErrorB = []
	for module in holder.both:
		tempPathA = holder.pathA + "/" + module
		tempPathB = holder.pathB + "/" + module
		try:
			thingsA = set(os.listdir(tempPathA))
		except OSError as os.errno.EPERM:
			# if we can't access the directory
			holder.checkErrorA.append(module)
			continue
		try:
			thingsB = set(os.listdir(tempPathB))
		except OSError as os.errno.EPERM:
			holder.checErrorB.append(module)
			continue
		# once we've successfully read both sub-directories, we compare the contents
		if len(thingsA.difference(thingsB)) == 0:
			continue
		else:
			if len(thingsA.difference(thingsB)) > 0: holder.versionsOnlyA[module] = thingsA.difference(thingsB)
			if len(thingsB.difference(thingsA)) > 0: holder.versionsOnlyB[module] = thingsB.difference(thingsA)
	# Once we've gone through all the common modules, we can return the holder and we're done
	return holder

def main():
	# Argument Parser
	parser = argparse.ArgumentParser()
	parser.add_argument('dirs', metavar='dir', type=str, nargs=2,help='Directory name or path.')
	parser.add_argument('-s', help='Shallow. Only goes through top level module directory and does not compare versions.',action='store_true')
	args = parser.parse_args()
	# First we need to validate the directories we input
	holder = Diff()
	for d in args.dirs:
		for key,value in arch.iteritems():
			if d in value:
				if holder.nameDirA:
					holder.nameDirB = key
				else:
					holder.nameDirA = key
	if not holder.nameDirA or not holder.nameDirB:
		print("Could not find valid directory names. Please try again.")
		sys.exit()
	holder.pathA = arch.get(holder.nameDirA)
	holder.pathB = arch.get(holder.nameDirB)
	holder = compare(holder,args.s)
	print("Compared directories: {} and {}".format(holder.pathA,holder.pathB))
	print("Installed on {} but not on {}:".format(holder.nameDirA,holder.nameDirB))
	for i in holder.onlyA:
		print("	{}".format(i))
	print("Installed on {} but not on {}:".format(holder.nameDirB,holder.nameDirA))
	for i in holder.onlyB:
		print("	{}".format(i))
	if args.s:
		sys.exit()
	# If we are not doing only a shallow comparison, go on.
	print("Version mismatches:")
	# Since we're already knee deep in this whole set() datatype, may as well keep going, yeah?
	keysA = set(holder.versionsOnlyA.keys())
	keysB = set(holder.versionsOnlyB.keys())
	keysOnlyA = keysA.difference(keysB)
	keysOnlyB = keysB.difference(keysA)
	keysboth  = keysA.intersection(keysB)
	print("Versions only installed on {}".format(holder.nameDirA))
	if len(keysOnlyA) == 0:
		print("None")
	else:
		for key in keysOnlyA:
			print("	{}".format(key))
			value = holder.versionsOnlyA.get(key)
			for i in value:
				if i[-4:] == '.lua':
					i = i[:-4]
				print("		{}".format(i))
	print("Versions only installed on {}".format(holder.nameDirB))
	if len(keysOnlyB) == 0:
		print("None")
	else:
		for key in keysOnlyB:
			print("	{}".format(key))
			value = holder.versionsOnlyB.get(key)
			for i in value:
				if i[-4:] == '.lua':
					i = i[:-4]
				print("		{}".format(i))
	print("Modules with version mismatches:")
	for key in keysboth:
		print("	{}".format(key))
		valueA = holder.versionsOnlyA.get(key)
		valueB = holder.versionsOnlyB.get(key)
		print("	Versions only on {}".format(holder.nameDirA))
		for i in valueA:
			if i[-4:] == '.lua':
				i = i[:-4]
			print("		{}".format(i))
		print("	Versions only on {}".format(holder.nameDirB))
		for i in valueB:
			if i[-4:] == '.lua':
				i = i[:-4]
			print("		{}".format(i))

	""" Old print, not using the glory of set() :(
	keys_already = []
	for key, value in holder.versionsOnlyA.iteritems():
		if key in keys_already:
			continue
		else:
			keys_already.append(key)
			if holder.versionsOnlyB.get(key):
				print('  {}'.format(key))
				valueB = holder.versionsOnlyB.get(key)
				print("    Versions on {}:".format(holder.nameDirA))
				for version in value:
					print("      {}".format(version))
				print("    Versions on {}:".format(holder.nameDirB))
				for versions in valueB:
					print("      {}".format(version))
			else:
				print("  {} - Only on {}".format(key,holder.nameDirA))
				for version in value:
					print("    {}".format(version))
	for key, value in holder.versionsOnlyB.iteritems():
		if key in keys_already:
			continue
		else:
			keys_already.append(key)
			print("  {} - Only on {}".format(key,holder.nameDirB))
			for version in value:
				print("    {}".format(version))
	"""

main()
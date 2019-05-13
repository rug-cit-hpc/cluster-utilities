#!/usr/bin/env python
# Easy Config Backup
# Author: Klemen Voncina

# Premise:
# This checks through all the installed software, finds the easyconfig and if it is not already present in either the main Gent repository or our university repository
# places it in our repository for backup.

# This is just documentation of my thought process while making this thing.
#
# Very important to keep in mind, no edits will be made to the original files, we need to keep modifications constrained to just the repository we want to dump in.
# How do I ensure that no editing happens in a wrong place?
# - Absolute paths, never relative
# - Separate the two repositories we're looking into in to two distinct functions? Funciton that edits stuff can only get passed the name of the directory it can edit.
#   Just to make absolutely certain.
# 
# First off, file comparison, if a file is different from one we already have, we should definitely back it up. If it is exactly the same, then we don't need to back up.
# How to check if two files are the same, first idea was to compare files line by line; that's really long.
# instead, use a hashing library, hash the files, compare the hashes. We can use md5, it doesn't matter if the hash is secure, this isn't something that
# requires cryptographically secure hashing.
#
# Second off, if we decide to back up a file, what if the directory we want to put it in does not yet exist?
# Find out how to make directories from within python

# To find files use the following ls -1 /apps/<architecture>/software/*/*/easybuild/*.eb
# do something similar with the repositories, like ls -1 /path/to/repo/*/*/*.eb
# outputs the full path so then travel backwards through the string to the first '/' character to cut out just the name
# 

# slight hiccup:
# subprocess makes the whole thing a big string, and I need to use shell=True in the command to get output that isn't an error
# this means 2 things;
# 1. The simpler one - before its a list, it needs to be split by '\n' characters and the trailing empty string removed
# 2. The more complicated one - since we're getting file paths that are going to be used in the shell=True command from an external file
#    first we have to validate that what we're getting is a valid file path and not something else like a shell command injection.
# even though I add stuff to the end of the string in the command this could be bypassed with an injection that starts and ends with '&'
# how about this, we never expect a '&' character anywhere in the directory path string anyways. So if I simply remove all instances of '&'
# from the command string every time, any injection should simply fail because it becomes malformed input.

import os
import sys
import hashlib
import subprocess
import yaml # problem 1: yaml is not installed... [FIXED]
import shutil
#import pprint # only uncomment this if you uncomment the debug print at the end of the alphabetic_list_indicies() method

nonsense_str = "sldjaldjf"

software_paths = [
	'/apps/haswell/software/',
	'/apps/sandybridge/software/',
	'/apps/skylake/software/',
	'/apps/generic/software/',
	]

# as a stand in for yaml parsing, here's the dictionary, pre-formed
# How about, this is going to be used so rarely just edit this instead.
# A note: USE ABSOLUTE PATH!!!! Otherwise you may end up with a directory named "~" wherever you ran this script...
# There's nothing more nerve wracking than wondering if "rm -rf \~" is going to work as intended or its going to nuke
# your entire home directory. Just don't do it.
repos = {
	'cit_repo' : '/home/f115714/easybuild/cit-easybuild/easyconfigs/',
	'gent_repo': '/home/f115714/easybuild/easybuild-easyconfigs/easybuild/easyconfigs/'
}

# ls suffixes
dir_suffix = '*/*/easybuild/*.eb'
rep_suffix = '*/*/*.eb'

class EbFile():
	def __init__(self,path):
		# define all class variables here to avoid confusion
		self.absPath = path
		self.fileName = None
		self.softwareName = None
		self.find_name()
		#self.find_softName()
		self.sanity_check()

	def find_name(self):
		if self.absPath == None:
			print("Error finding file name from absolute path")
			sys.exit()
		str_len = len(str(self.absPath))
		while str_len != 0:
			str_len -= 1
			if self.absPath[str_len] == '/': # first file separator we hit going backwards
				self.fileName = self.absPath[str_len+1:]
				return
		if not self.fileName:
			print("Could not find file name from the following absolute path:")
			print("	{}".format(self.absPath))

	def find_softName(self):
		# sample: /apps/haswell/software/zlib/1.2.8/easybuild/zlib-1.2.8.eb
		# from this we want "zlib"
		# as an aside, could combine both the finding functions since they're both dependend on the '/' character
		str_len = len(str(self.absPath))
		count = 0
		# store the index in the string where the third and fourth '/' appear (counting from the end of the string backwards)
		third = None
		fourth= None
		while str_len != 0:
			str_len -= 1
			if self.absPath[str_len] == "/":
				count += 1
			if count == 3 and not third:
				third = str_len
			if count == 4:
				fourth = str_len
				break
		# now we cut up the string and extract just the bit we want
		fourth += 1
		self.softwareName = self.absPath[fourth:third]

	def sanity_check(self):
		# consider removing, sanity check is technically already done in find_name()
		obj_vars = [
			self.absPath,
			self.fileName,
			]
		for i in obj_vars:
			if not i:
				print("Error one of the variables is not set. Quitting.")
				sys.exit()

def list_to_obj(big_list):
	new_list = []
	for i in big_list:
		newObj = EbFile(i)
		new_list.append(newObj)
	return new_list

# Obsolete since we don't get input from file anymore and there is no intention to do so
# Still keeping this in here to avoid stupid things happening anyways.
def validate_input(d):
	# takes dictionary of repos as input
	# outputs the same thing if they're valid input, otherwise outputs garbage
	for key, value in d.iteritems():
		# basically, we assume that any instance of an & in the input is because someone is trying to inject
		# malicious code into the subprocess.check_output(shell=True) environment and we instead replace the '&'
		# with garbage to make the command fail.
		d[key] = value.translate(nonsense_str,"&")
	return d

def read_paths():
	paths_file = "ebpaths.yaml"
	paths_file = open(paths_file)
	paths = yaml.load(paths_file,Loader=yaml.BaseLoader)
	paths_file.close()
	return paths

def convert_output(big_string):
	# function to convert output of subprocess.check_output() from a big string to a list
	intermediate = big_string.split('\n')
	final = filter(None,intermediate)
	return final

def read_all_eb():
	# here we construct a massive list of EbFile objects which contains every single .eb file we find in the subdirectories
	# 1. We need all the top level directories where the eb files are
	mega_list_software = []
	for i in software_paths:
		ls_path = i + dir_suffix
		temp_list = subprocess.check_output('ls -1 {}'.format(ls_path),shell=True)
		temp_list = convert_output(temp_list)
		mega_list_software += temp_list # concatenate into big list
	#print("Mega list software size: {}".format(len(mega_list_software)))
	mega_list_repos = []
	# 2. As well as the eb files in both repositories
	for key, value in repos.iteritems():
		ls_path = value + rep_suffix
		temp_list = subprocess.check_output('ls -1 {}'.format(ls_path),shell=True)
		temp_list = convert_output(temp_list)
		mega_list_repos += temp_list
	#print("Mega list repos size: {}".format(len(mega_list_repos)))
	# Make all the items in the list into ojbects
	mega_list_software = list_to_obj(mega_list_software)
	mega_list_repos    = list_to_obj(mega_list_repos)
	# Sort the lists
	mega_list_software = sorted(mega_list_software,key=lambda item : item.fileName.lower())
	mega_list_repos    = sorted(mega_list_repos,key=lambda item : item.fileName.lower())
	#print("After Sorting")
	#print("Mega list software size: {}".format(len(mega_list_software)))
	#print("Mega list repos size: {}".format(len(mega_list_repos)))
	# Just return the two sorted lists.
	return mega_list_software, mega_list_repos

def test_func():
	mega_list = []
	for i in software_paths:
		ls_path = i + dir_suffix
		temp_list = subprocess.check_output('ls -1 {}'.format(ls_path),shell=True)
		temp_list = convert_output(temp_list)
		mega_list += temp_list
	# now we attempt to sort the list
	mega_list = list_to_obj(mega_list)
	mega_list_sorted = sorted(mega_list,key=lambda item : item.fileName.lower()) # well, this works!
	# now we test if the list is actually sorted
	print("Printing first 20 items.")
	for x in range(20):
		item = mega_list_sorted[x]
		print(item.fileName)
	print("Printing last 20 items.")
	for y in range(20,0,-1):
		item = mega_list_sorted[-y]
		print(item.fileName)
	# option 2
	'''
	print("Printing about 20 entries at intervals from the list.")
	for skip in range(0,len(mega_list_sorted),((int)len(mega_list_sorted)/50)):
		# prints about 20 items from the list but at intervals of 50
		item = mega_list_sorted[skip]
		print(item.fileName)
	'''
	print("Done.")

def alphabetic_list_indicies(big_list):
	# gets as input a list of EbFile() objects and returns a dictionary that contains information
	# about where each letter starts and ends. We assume that we get a sorted list.
	# the Gent repo will have some numbered stuff in there but that will literally not matter.
	index_dict = {}
	current_letter = None
	previous_letter= None
	for i in range(len(big_list)):
		first_letter = big_list[i].fileName[0].lower()
		if not index_dict.get(first_letter):
			previous_letter = current_letter
			current_letter = first_letter
			if previous_letter:
				index_dict[previous_letter][1] = i-1
			# then we add an entry, but do we do it now or at the end of it and enter the full tuple?
			index_dict[first_letter] = [None] * 2 # Initialize an empty list of length 2
			index_dict[first_letter][0] = i
		if i == len(big_list) - 1 and index_dict.get(first_letter): # if we are at the last item in the list
			index_dict[first_letter][1] = i
	#pprint.pprint(index_dict,width=1) # debugging if you put this back in make sure to see import section for pprint
	return index_dict

def main():
	# this won't have command line options cause it literally does one thing and that's it.
	#searchPaths = read_paths()
	#ebList = read_all_eb()
	#test_func()
	print("Reading all.")
	big_soft_list,big_repo_list = read_all_eb()
	#soft_dict = alphabetic_list_indicies(big_soft_list) # don't actually need this
	repo_dict = alphabetic_list_indicies(big_repo_list)
	print("Marking files for backup.")
	marked_for_backup = []
	for i in big_soft_list:
		# find i in big_repo_list
		i_first = i.fileName[0].lower()
		look_here = repo_dict.get(i_first)
		found = 0
		for idx in range(look_here[0],look_here[1]+1):
			if big_repo_list[idx].fileName == i.fileName:
				found = 1
				break
		if found == 0:
			if (len(marked_for_backup) > 0) and (not (i.fileName == marked_for_backup[-1].fileName)):
				marked_for_backup.append(i)
			elif len(marked_for_backup) == 0:
				marked_for_backup.append(i)
	print("The Following files are marked for backup")
	print("Number of files marked for backup = {}".format(len(marked_for_backup)))
	"""
	for eb in marked_for_backup:
		print(eb.softwareName)
	"""
	# now we start backing things up
	start_path = repos.get('cit_repo')
	for item in marked_for_backup:
		item.find_softName()
		letter = item.fileName[0].lower()
		path_letter = os.path.join(start_path,letter)
		path_software = os.path.join(path_letter,item.softwareName)
		path_full = os.path.join(path_software,item.fileName)
		if not os.path.exists(path_letter):
			os.makedirs(path_letter)
			print("Creating dir: {}".format(path_letter))
		if not os.path.exists(path_software):
			os.makedirs(path_software)
			print("Creating dir: {}".format(path_software))
		shutil.copy2(item.absPath,path_full)


main()
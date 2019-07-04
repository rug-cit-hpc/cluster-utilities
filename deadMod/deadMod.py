#!/usr/bin/env python2

# dead module finder
# a script that should hopefully spit out a list of both modules without software
# and software without module files

# same thing I've done before
# Go architecture by architecture, list all the things and see what does and doesn't match.

# Ideas:
# If .eb file exists then the software probably does as well?
# Alternatively, from the .eb file path, check if the binary folder contains anything

import sys
import os
import subprocess

software_paths = [
	'/apps/haswell/',
	'/apps/sandybridge/',
	'/apps/skylake/',
	#'/apps/generic/',
]

eb_suffix = 'software/*/*/easybuild/*.eb'
md_suffix= 'modules/all/*/*'

# Copied from ebBackup
class EbFile():
	def __init__(self,path):
		# define all class variables here to avoid confusion
		self.absPath = path
		self.fileName = None
		self.softwareName = None
		self.versionOnly = None
		self.find_names()
		self.fileName = self.fileName.replace('.eb','')
		self.find_softName()
		self.extract_version()

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

	def find_names(self):
		# This function should take the place of both find_name() and find_softName()
		if self.absPath == None:
			print("Path is empty. Quitting.")
			sys.exit()
		count = 0
		third = None
		for i in range(1,len(self.absPath)):
			if self.absPath[-i] == '/' and count == 0: # finding first '/'
				self.fileName = self.absPath[-(i-1):]
				count += 1
			elif self.absPath[-i] == '/' and count == 2: # finding third '/'
				third = i
				count += 1
			elif self.absPath[-i] == '/' and count == 3: # finding fourth '/'
				self.softwareName = self.absPath[-i:-(third+1)]
				return
			elif self.absPath[-i] == '/':
				count += 1

	def print_vars(self):
		# Debugging function
		print("Printing EbFile object:")
		print("absPath:	{}".format(self.absPath))
		print("fileName:	{}".format(self.fileName))
		print("softwareName:	{}".format(self.softwareName))
		print("versionOnly:	{}".format(self.versionOnly))

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

	def extract_version(self):
		# check prerequisites
		if (not self.fileName) or (not self.softwareName):
			print("Can't extract version number without file name or software name for following full path: {}".format(self.absPath))
			sys.exit()
		self.versionOnly = self.fileName.replace(self.softwareName+'-','')


class MdFile():
	def __init__(self,path):
		self.absPath = path
		self.fileName = None
		self.softwareName = None
		self.get_names()
		self.fileName = self.fileName.replace('.lua','')

	def get_names(self):
		count = 0
		prevloc = None
		for i in range(1,len(self.absPath)):
			if count == 1 and self.absPath[-i] == '/':
				self.softwareName = self.absPath[-(i-1):-(prevloc)]
				return
			if self.absPath[-i] == '/' and count == 0:
				self.fileName = self.absPath[-(i-1):]
				count += 1
				prevloc = i

	def print_vars(self):
		print("Printing MdFile object:")
		print("absPath:	{}".format(self.absPath))
		print("fileName:	{}".format(self.fileName))
		print("softwareName:	{}".format(self.softwareName))

def convert_output(big_string):
	# function to convert output of subprocess.check_output() from a big string to a list
	intermediate = big_string.split('\n')
	final = filter(None,intermediate)
	return final

def list_to_eb(big_list):
	new_list = []
	for i in big_list:
		newObj = EbFile(i)
		new_list.append(newObj)
	return new_list

def list_to_md(big_list):
	new_list = []
	for i in big_list:
		# filter out a few things
		if '.bak_' in i:
			continue
		newObj = MdFile(i)
		new_list.append(newObj)
	return new_list

def alphabetic_list_indicies(big_list):
	# gets as input a list of EbFile() or MdFile() objects and returns a dictionary that contains information
	# about where each letter starts and ends. We assume that we get a sorted list.
	# the Gent repo will have some numbered stuff in there but that will literally not matter.
	index_dict = {}
	current_letter = None
	previous_letter= None
	for i in range(len(big_list)):
		first_letter = big_list[i].softwareName[0].lower()
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

def compare_arch(archpath):
	print("Checking {} for possible dead modules.".format(archpath))
	ebpath = archpath + eb_suffix
	eblist = sorted(list_to_eb(convert_output(subprocess.check_output('ls -1 {}'.format(ebpath),shell=True))),key=lambda item : item.softwareName.lower())
	mdpath = archpath + md_suffix
	# Here's how to steamroll an error. If it breaks again, there's going to be very little I can do to fix it...
	try:
		mdlist = sorted(list_to_md(convert_output(subprocess.check_output('ls -1 {}'.format(mdpath),shell=True))),key=lambda item : item.softwareName.lower())
	except subprocess.CalledProcessError, e:
		# Your complaint has been filed under 'b' for Bullshit
		# Now run it again
		mdlist = sorted(list_to_md(convert_output(e.output)),key=lambda item : item.softwareName.lower())
	eb_dict = alphabetic_list_indicies(eblist)
	md_dict = alphabetic_list_indicies(mdlist)
	# First one way
	eb_noMatch = []
	md_noMatch = []
	for i in eblist:
		char = i.softwareName[0].lower()
		lookup = md_dict.get(char)
		found = 0
		for x in range(lookup[0],lookup[1]+1):
			if mdlist[x].softwareName == i.softwareName and mdlist[x].fileName == i.versionOnly:
				found = 1
		if found == 0:
			eb_noMatch.append(i)
	for j in mdlist:
		char = j.softwareName[0].lower()
		lookup = eb_dict.get(char)
		found = 0
		for y in range(lookup[0],lookup[1]+1):
			if eblist[y].softwareName == j.softwareName and eblist[y].versionOnly == j.fileName:
				found = 1
		if found == 0:
			md_noMatch.append(j)
	print("	Software without modules: {}".format(len(eb_noMatch)))
	for e in eb_noMatch:
		print("		{}".format(e.absPath))
	print("	Modules without software: {}".format(len(md_noMatch)))
	for m in md_noMatch:
		print("		{}".format(m.absPath))
	print("	Length of ebList = {}".format(len(eblist)))
	print("	Length of mdList = {}".format(len(mdlist)))

def main():
	#compare_arch(software_paths[0])
	for s in software_paths:
		compare_arch(s)

main()

	

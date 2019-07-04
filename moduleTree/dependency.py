import os
import sys

# Not using luaparser because its a shit piece of software

class dependency():
	def __init__(self,name_version,architecture,print_spacing):
		# reads LUA file (with or without .lua extension)
		# and creates a dependency node, this should go
		# all the way down to toolchain level
		""" name_version is a string in the format "name/version"
			of a piece of software.
		"""
		""" One thing to find out:
			Can we make an object make an instance of itself
			Inside an instance of itself?
		"""
		self.nver = name_version
		self.arch = architecture
		self.parseFile()


	def parseFile(self):
		str1 = "load("
		file_name = form_file_string(self.nver,self.arch)
		file_contents = None
		with open(file_name,'r') as f:
			# Alright, read, reads the entire file
			file_contents = f.read()
		file_contents.split("\n") # split by newlines
		refined_list = []
		for i in file_contents:
			if str1 in i:
				refined_list.append(i)

	def form_file_string(self,nver,arch):
		return "/apps/{arch}/modules/all/{nver}"
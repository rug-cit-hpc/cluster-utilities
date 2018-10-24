#!/usr/bin/env python
import subprocess, os, argparse

colors = {
	'blue' : '\033[94m', # some terminals don't support this so it just looks 'normal'
	'red'  : '\033[91m',
	'bold' : '\033[1m',
	'warn' : '\033[93m', # not sure yet what colour this is
	'end'  : '\033[0m' # if this isn't at the end of the string, the formatting can overflow onto more lines of text
}

# Some evil global variables
t_width = int(subprocess.check_output(['tput','cols'])) # checks terminal width, this should not change throughout program operation (because it should take less than 0.1 sec to run)

def percent_bar(percent):
	# Makes a string that when printed shows a percentage bar
	bar = "" # empty string
	fill ='#' # the fill character
	empty = '=' # the empty character
	warning = "!!!"
	ok = "   "
	b_width = t_width
	if(b_width > 60):
		# bar is limited to a width of 60 characters because massive bars looks terrible
		b_width = 60
	b_width = b_width-5 # some padding for the number
	if(percent <= 10):
		b_width -= 2
	elif(percent >= 100):
		b_width -= 4
	else:
		b_width -= 3
	comp = float(100-percent)
	if(comp < 1):
		comp = 1
	# b_width is now known, now we split into 'full' and 'empty'
	empty_w = int(b_width*(comp/100)) # Truncating because bar width is in int
	full_w = b_width - empty_w # determining empty first means we round down empty space rather than full
	bar = bar + (fill * full_w) + (empty * (empty_w-1))
	if(percent <= 100):
		bar += ok
	else:
		bar += warning
	num_string = " " + str(int(percent)) + "% "
	bar += num_string
	return bar

def strip_char(item):
	# takes a string with integers and characters and strips the characters from the end of it
	suffixes= { # not exact but close enough to unify and calculate a percentage. Axed 3 zeroes off the end just because its uneccessary
		'k' : 1,
		'M' : 1000,
		'G' : 1000000,
		'T' : 1000000000
	}
	if(item[-1] == '*'):
		item = item[:-1]
	item = suffixes.get(item[-1]) * int(item[:-1])
	return item

def date_pretty(date_string):
	# TODO: Implement this
	# Prints the time remaining a little prettier than XXdXXhXXmXXs
	pass

class Quota():
	# Lets try this implementation
	# Create an object that contains all quota information for one directory for one user
	# Then we can print it or not
	def __init__(self,group,directory):
		self.group = group
		self.directory = directory
		self.raw = subprocess.check_output(['lfs','quota','-g',str(self.group),str(self.directory),'-h'])
		# Initialize here just so we keep track of what's available in the object
		self.ref = filter(None,self.raw.split('\n')[2].split(' '))
		self.dusage = strip_char(self.ref[1])
		self.dalloc = strip_char(self.ref[2])
		self.dlimit = strip_char(self.ref[3])
		self.dgrace = self.ref[4]
		self.fusage = int(self.ref[5])
		self.falloc = int(self.ref[6])
		self.flimit = int(self.ref[7])
		self.fgrace = self.ref[8]
		self.bar = percent_bar(float((float(self.dusage)/float(self.dalloc))*100))
		# some more empty internal variables
		self._warn_use = None
		self._warn_files = None
		# functions to call
		self.gen_warnings()

	def gen_warnings(self):
		# data warnings
		if(self.dusage > self.dalloc):
			self._warn_use = 'red'
		elif(float(float(float(self.dalloc) - float(self.dusage))/float(self.dalloc)) < 0.06):
			self._warn_use = 'warn'
		else:
			self._warn_use = 'blue'
		# file warnings
		if(float(float(float(self.falloc) - float(self.fusage))/float(self.falloc) < 0.06)):
			self._warn_files = 'warn'
		elif(self.fusage > self.falloc):
			self._warn_files = 'red'
		else:
			self._warn_files = 'blue'

	def full_print(self):
		# print directory
		print "{}{}{}".format(colors.get('bold'),self.directory,colors.get('end'))
		# print bar
		print "{}{}{}{}{}".format(colors.get('bold'),colors.get(self._warn_use),self.bar,colors.get('end'),colors.get('end'))
		print "  Quota:	{}".format(self.ref[2])
		print "  Hard Limit:	{}".format(self.ref[3])
		print "{}  Usage:	{}{}".format(colors.get(self._warn_use),self.ref[1],colors.get('end'))
		print "  File Quota:	{}".format(self.falloc)
		print "  File Limit:	{}".format(self.flimit)
		print "{}  Files:	{}{}".format(colors.get(self._warn_files),self.fusage,colors.get('end'))
		if(self._warn_use == 'red' and self.dgrace != '-'):
			print "{}You have exceeded your storage limit of {}. Please reduce your storage usage below this limit or contact the system administrator to increase it within {}.{}".format(colors.get(self._warn_use),self.ref[1],self.dgrace,colors.get('end'))
		if(self._warn_files == 'red' and self.fgrace != '-'):
			print "{}You have exceeded your file limit of {}. Please reduce the number of files below this limit or contact the system administrator to increase it within {}.{}".format(colors.get(self._warn_files),self.fusage,self.fgrace,colors.get('end'))

	def return_warnings(self):
		return self._warn_use,self._warn_files


def main():
	groups = os.getgroups()
	directories = [
		'/home',
		'/data',
		'/scratch'
	]
	parser = argparse.ArgumentParser()
	#mutex = parser.add_mutually_exclusive_group()
	#mutex.add_argument('-u',type=str,help="Specify user. Only prints quota for specified user's own group.",const=groups)
	#mutex.add_argument('-g',type=str,help="Specify group. Only prints quota for specified group.",const=groups,nargs='?')
	parser.add_argument('-r',help="Only output quota info if user is close to limit or above quota",action="store_true")
	args = parser.parse_args()
	for g in groups:
		if(not args.r):
			print "Quotas for user group {}{}{}".format(colors.get('bold'),g,colors.get('end'))
		for d in directories:
			quota = Quota(g,d)
			if(args.r):
				dwarn,fwarn = quota.return_warnings()
				if(dwarn == 'red'):
					print "{}You have exceeded your storage quota on the {}{}{}{} filesystem, please reduce usage within {}.{}".format(colors.get(dwarn),colors.get('bold'),d,colors.get('end'),colors.get(dwarn),quota.dgrace,colors.get('end'))
				elif(dwarn == 'warn'):
					print "You have less than 5{} of your allocated storage remaining on the {} filesystem.".format(str('%'),d)
			else:
				quota.full_print()

main()


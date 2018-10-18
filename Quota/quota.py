#!/usr/bin/env python
import subprocess, os

colors = {
	'blue' : '\033[94m', # some terminals don't support this so it just looks 'normal'
	'red'  : '\033[91m',
	'bold' : '\033[1m',
	'end'  : '\033[0m' # if this isn't at the end of the string, the formatting can overflow onto more lines of text
}

def percent_bar(percent):
	# prints a bar that shows a 'percent filled' status
	bar = "" # the bar is formatted as a string, first its empty
	fill ='#'
	empty = '='
	warning = "!!!"
	ok = "   "
	t_width = int(subprocess.check_output(['tput','cols']))
	# maybe do this only once?
	if(t_width > 60):
		# bar is limited to a width of 60 characters because massive bars looks terrible
		t_width = 60
	b_width = t_width-5 # some padding for the number
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
	warning = 'blue'
	suffixes= { # not exact but close enough to unify and calculate a percentage
		'k' : 1000,
		'M' : 1000000,
		'G' : 1000000000,
		'T' : 1000000000000
	}
	if(item[-1] == '*'):
		warning = 'red'
		item = item[:-1]
	item = suffixes.get(item[-1]) * int(item[:-1])
	return item, warning

def date_pretty(date_string):
	# TODO: Implement this
	# Prints the time remaining a little prettier than XXdXXhXXmXXs
	pass

def get_and_print_quota(group,directory):
	# gets and prints the file quota for a user group
	raw = subprocess.check_output(['lfs','quota','-g',str(group),directory,'-h'])
	raw = raw.split("\n")[2].split(" ")
	ref = filter(None,raw)
	usage,warn_use = strip_char(ref[1])
	alloc,w = strip_char(ref[2])
	bar = percent_bar(float((float(usage)/float(alloc))*100))
	warn_files = 'blue'
	if(int(ref[6]) < int(ref[5])):
		warn_files='red'
	# printing here
	print colors.get('bold') + ref[0] 
	print colors.get(warn_use) + bar + colors.get('end') + colors.get('end')
	print "  Quota:      " + ref[2]
	print "  Hard Limit: " + ref[3]
	print colors.get(warn_use) + "  Used:       " + ref[1] + colors.get('end')
	print "  File Quota: " + ref[6]
	print "  File Limit: " + ref[7]
	print colors.get(warn_files) + "  Files:      " + ref[5] + colors.get('end')
	# Grace period handling here
	if(warn_use=='red' and ref[4] != '-'):
		#d = date_pretty(ref[4])
		print colors.get('red') + "You have exceeded your storage limit of " + str(ref[1]) + ". Please reduce your storage usage below this limit or contact the system administrator to increase it within " + str(ref[4]) + colors.get('end')
	if(warn_files == 'red' and ref[8] != '-'):
		# d2 = date_pretty(ref[8])
		print colors.get('red') + "You have exceeded your file limit of " + str(ref[6]) + ". Please reduce the number of files below this limit or contact your system administrator to increase it within " + str(ref[8]) + colors.get('end')

def main():
	# get user's groups
	groups = os.getgroups()
	directories = [
		'/home',
		'/data',
		'/scratch'
	]
	for g in groups:
		print "Quotas for user group " + colors.get('bold') + str(g) + colors.get('end')
		for d in directories:
			get_and_print_quota(g,d)
main()


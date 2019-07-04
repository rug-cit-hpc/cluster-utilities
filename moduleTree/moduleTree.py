import os
import sys
import argparse
from dependency import dependency

md_suffix = 'modules/all/*/*'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i',
		help="Interactive flag, instead of printing everything out at once, you should get prompted for every print-out.",
	 	action="store_true")
	args = parser.parse_args()

	if args.i:
		# We go into interactive mode with a loop and waitKey()
		pass
	else:
		# Just print everything
		pass

def create_big_list(arch):
	archpath = "/apps/{}/".format(arch)
	mdpath = archpath + md_suffix
	# WARNING: the following code is going to fail because some functions are missing
	# Here's how to steamroll an error. If it breaks again, there's going to be very little I can do to fix it...
	try:
		mdlist = sorted(list_to_md(convert_output(subprocess.check_output('ls -1 {}'.format(mdpath),shell=True))),key=lambda item : item.softwareName.lower())
	except subprocess.CalledProcessError, e:
		# Your complaint has been filed under 'b' for Bullshit
		# Now run it again
		mdlist = sorted(list_to_md(convert_output(e.output)),key=lambda item : item.softwareName.lower())

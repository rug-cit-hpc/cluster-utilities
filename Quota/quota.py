#!/usr/bin/env python
import argparse
import os
import subprocess

colors = {
    'blue': '\033[94m',  # some terminals don't support this so it just looks 'normal'
    'red': '\033[91m',
    'bold': '\033[1m',
    'warn': '\033[93m',  # not sure yet what colour this is
    'end': '\033[0m'  # if this isn't at the end of the string, the formatting can overflow onto more lines of text
}

# Some evil global variables
t_width = int(subprocess.check_output(['tput', 'cols']))
# checks terminal width, this should not change throughout program operation (because it should take less than 0.1 sec
# to run)


# define custom exceptions here
class CustomPermissionError(Exception):
    pass


class DataError(Exception):
    pass


def percent_bar(percent):
    # Makes a string that when printed shows a percentage bar
    bar = ""  # empty string
    fill = '#'  # the fill character
    empty = '='  # the empty character
    warning = "!!!"
    ok = "   "
    b_width = t_width
    if b_width > 60:
        # bar is limited to a width of 60 characters because massive bars looks terrible
        b_width = 60
    b_width = b_width - 5  # some padding for the number
    if percent <= 10:
        b_width -= 2
    elif percent >= 100:
        b_width -= 4
    else:
        b_width -= 3
    comp = float(100 - percent)
    if comp < 1:
        comp = 1
    # b_width is now known, now we split into 'full' and 'empty'
    empty_w = int(b_width * (comp / 100))  # Truncating because bar width is in int
    full_w = b_width - empty_w  # determining empty first means we round down empty space rather than full
    bar = bar + (fill * full_w) + (empty * (empty_w - 1))
    if percent <= 100:
        bar += ok
    else:
        bar += warning
    num_string = " " + str(int(percent)) + "% "
    bar += num_string
    return bar


def strip_char(item):
    # Takes a string with integers and characters and strips the characters from the end of it
    # Not exact but close enough to unify and calculate a percentage. Axed 3 zeroes off the end just because its
    # unnecessary
    suffixes = {
        'k': 1,
        'M': 1000,
        'G': 1000000,
        'T': 1000000000
    }
    if item[-1] == '*':
        item = item[:-1]
    item = suffixes.get(item[-1]) * float(item[:-1])
    return item


def date_pretty(date_string):
    # TODO: Implement this
    # Prints the time remaining a little prettier than XXdXXhXXmXXs
    pass
    return date_string


class Quota:
    # Lets try this implementation
    # Create an object that contains all quota information for one directory for one user
    # Then we can print it or not
    def __init__(self, group, directory, debug_flag):
        self.group = group
        self.directory = directory
        self.raw = subprocess.check_output(['lfs', 'quota', '-g', str(self.group), str(self.directory), '-h'],
                                           universal_newlines=True)
        if debug_flag:
            print(f'{colors.get("red")}Debug Raw{colors.get("end")}')
            print(self.raw)
            print(f'{colors.get("red")}End of Debug Raw{colors.get("end")}')

        # Check the raw for errors before further processing
        self.check_raw()

        # Initialize here just so we keep track of what's available in the object
        self.ref = self.raw.split('\n')[2].split()
        self.sanity_check()
        self.dusage = strip_char(self.ref[1])
        self.dalloc = strip_char(self.ref[2])
        self.dlimit = strip_char(self.ref[3])
        self.dgrace = self.ref[4]
        if self.dgrace == "none":
            self.dgrace = self.dgrace.upper()
        self.fusage = int(self.ref[5])
        self.falloc = int(self.ref[6])
        self.flimit = int(self.ref[7])
        self.fgrace = self.ref[8]
        if self.fgrace == "none":
            self.fgrace = self.fgrace.upper()
        if debug_flag:
            print(f'{colors.get("red")}Debug object variables{colors.get("end")}')
            print(f'Disk Usage: {self.dusage}	{type(self.dusage)}\n'
                  f'Disk Allocated: {self.dalloc}	{type(self.dalloc)}\n'
                  f'Disk Limit: {self.dlimit}	{type(self.dlimit)}\n'
                  f'File Usage: {self.fusage}	{type(self.fusage)}\n'
                  f'File Allocated: {self.falloc}	{type(self.falloc)}\n'
                  f'File Limit: {self.flimit}	{type(self.flimit)}\n'
                  f'Disk Grace: {self.dgrace}	{type(self.dgrace)}\n'
                  f'File Grace: {self.fgrace}	{type(self.fgrace)}')
            print(f'{colors.get("red")}End Debug object variables{colors.get("end")}')
        self.bar = percent_bar(float((float(self.dusage) / float(self.dalloc)) * 100))

        # some more empty internal variables
        self._warn_use = None
        self._warn_files = None

        # functions to call
        self.gen_warnings()

    def check_raw(self):
        # checks for messages like "Permission denied."
        if self.raw == 'Permission denied.':
            raise CustomPermissionError()

    def sanity_check(self):
        # check if there even is a quota for this user group otherwise raise exception
        if self.ref[2] in {None, '0'} or self.ref[6] in {None, '0'}:
            raise DataError()

    def gen_warnings(self):
        # data warnings
        if self.dusage > self.dalloc:
            self._warn_use = 'red'
        elif float(float(float(self.dalloc) - float(self.dusage)) / float(self.dalloc)) < 0.06:
            self._warn_use = 'warn'
        else:
            self._warn_use = 'blue'

        # file warnings
        if float(float(float(self.falloc) - float(self.fusage)) / float(self.falloc) < 0.06):
            self._warn_files = 'warn'
        elif self.fusage > self.falloc:
            self._warn_files = 'red'
        else:
            self._warn_files = 'blue'

    def full_print(self):
        # print directory
        print(f"{colors.get('bold')}{self.directory}{colors.get('end')}")
        # print bar
        print(f"{colors.get('bold')}{colors.get(self._warn_use)}{self.bar}{colors.get('end')}{colors.get('end')}")
        print(f"  Quota:	{self.ref[2]}")
        print(f"  Hard Limit:	{self.ref[3]}")
        print(f"{colors.get(self._warn_use)}  Usage:	{self.ref[1]}{colors.get('end')}")
        print(f"  File Quota:	{self.falloc}")
        print(f"  File Limit:	{self.flimit}")
        print(f"{colors.get(self._warn_files)}  Files:	{self.fusage}{colors.get('end')}")
        if self._warn_use == 'red' and self.dgrace != '-':
            print(
                f"{colors.get(self._warn_use)}You have exceeded your storage limit of {self.ref[2]}. "
                f"Please reduce your storage usage below this limit or contact the system administrator to increase it "
                f"within {self.dgrace}.{colors.get('end')}")
            if self.dgrace == "NONE":
                print(
                    f"{colors.get(self._warn_use)}You have exceeded your grace period of 7 days. "
                    f"You will be unable to write additional files to {self.directory} until you reduce storage usage "
                    f"below {self.ref[2]}.{colors.get('end')}")
        if self._warn_files == 'red' and self.fgrace != '-':
            print(
                f"{colors.get(self._warn_files)}You have exceeded your file limit of {self.fusage}. "
                f"Please reduce the number of files below this limit or contact the system administrator "
                f"to increase it within {self.fgrace}.{colors.get('end')}")
            if self.fgrace == "NONE":
                print(
                    f"{colors.get(self._warn_use)}You have exceeded your grace period of 7 days. "
                    f"You will be unable to write additional files to {self.directory} until you reduce file usage "
                    f"below {self.fusage}.{colors.get('end')}")

    def return_warnings(self):
        return self._warn_use, self._warn_files


def process_entity(group_id):
    # if possible, extracts username from group id, otherwise returns the value back unchanged
    gid = str(group_id)  # we don't really need it as an int at any point
    if gid[:2] == '10':
        entity = 'user'
        eid = 'p' + gid[2:]
    elif gid[:2] == '20':
        entity = 'user'
        eid = 'f' + gid[2:]
    elif gid[:1] == '3':
        entity = 'user'
        eid = 's' + gid[2:]
    elif gid[:1] == '4':
        entity = 'guest user'
        eid = 'g' + gid[1:]
    else:
        entity = 'user group'
        eid = gid
    return eid, entity


def main():
    groups = os.getgroups()
    directories = ['/home', '/data', '/scratch']
    parser = argparse.ArgumentParser()
    # mutex = parser.add_mutually_exclusive_group()
    # mutex.add_argument('-u',type=str,help="Specify user. Only prints quota for specified user's own group.",
    # const=groups)
    # mutex.add_argument('-g',type=str,help="Specify group. Only prints quota for specified group.",const=groups,
    # nargs='?')
    parser.add_argument('-r',
                        help="Only output quota info if user is close to limit or above quota",
                        action="store_true")
    parser.add_argument('-d',
                        help="Produce debugging output. Please note this is for developer use and likely prints utter "
                             "gibberish",
                        action="store_true")
    args = parser.parse_args()
    for g in groups:
        if not args.r:
            eid, entity = process_entity(g)
            print(f'Quotas for {entity} {colors.get("bold")}{eid}{colors.get("end")}')
        for d in directories:
            try:
                quota = Quota(g, d, args.d)
            except CustomPermissionError:
                if not args.r:
                    print(f'You do not have permission to view quota for '
                          f'{entity} {colors.get("bold")}{"eid"}{colors.get("end")}')
                continue
            except DataError:
                if not args.r:
                    print(f"No data for {entity} {colors.get('bold')}{eid}{colors.get('end')} "
                          f"in directory {colors.get('bold')}{d}{colors.get('end')}")
                continue
            if args.r:
                dwarn, fwarn = quota.return_warnings()
                if dwarn == 'red':
                    print(
                        f"{colors.get(dwarn)}You have exceeded your storage quota on the "
                        f"{colors.get('bold')}{d}{colors.get('end')}{colors.get(dwarn)} filesystem, "
                        f"please reduce usage within {quota.dgrace,}.{colors.get('end')}")
                elif dwarn == 'warn':
                    print(
                        f"You have less than 5{str('%')} of your allocated storage remaining on the {d} filesystem.")
            else:
                quota.full_print()


if __name__ == "__main__":
    main()

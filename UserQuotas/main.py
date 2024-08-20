#!/usr/bin/env python3
import logging
import sys
import json
import os
import grp

from pwd import getpwnam
from quota_tools.lustre_quota import LustreQuota
from datetime import datetime

lustre_filesystems = ['/projects', '/scratch']


def get_home_fs(user: str) -> str:
    """
    Returns the home filesystem path for the given user.

    Parameters:
    user (str): The username for which to retrieve the home filesystem path.

    Returns:
    str: The home filesystem path for the given user.
    """
    return getpwnam(user).pw_dir


def get_uid(user):
    return getpwnam(user).pw_uid

def get_gid(group):
    return grp.getgrnam(group).gr_gid

def get_gids(user):
    uid = getpwnam(user).pw_uid
    return os.getgrouplist(user, uid)


class DataError(Exception):
    pass


class Quota:
    def __init__(self, group, fs):
        self.group = group
        self.gid = get_gid(group)
        self.fs = fs
        self.quota_type = 'lustre' if fs in lustre_filesystems else 'nfs'
        self.quota = None

    def get_quota(self):
        if self.quota_type == 'lustre':
            try:
                self.quota = LustreQuota.get_quota(str(self.gid), self.fs, 'project').to_json()
            except DataError as e:
                logging.warn(f'No quota for {grp.getgrgid(self.gid).gr_name} on {self.fs}')
            return self
        else:
            logging.warn(f'Quota type {self.quota_type} not supported')
            return self
    
    def to_kb(self):
        for key in self.quota:
            if key in ['block_usage', 'block_soft', 'block_hard']:
                self.quota[key] = self.quota[key] // 1024
        return self

    def to_json(self):
        quota = {'user': self.group,
                 'path': self.fs + '/' + self.group,
                 'total_block_usage': self.quota['block_usage'],
                 'block_limit': self.quota['block_soft'],
                 'total_file_usage': self.quota['inode_usage'],
                 'file_limit': self.quota['inode_soft'],
                 }
        return quota

    
def main():
    user = sys.argv[1] if len(sys.argv) > 1 else None
    quotas = []
    user_home = get_home_fs(user)
    logging.basicConfig(filename=f'{user_home}/ondemand/logfile.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    for fs in lustre_filesystems:
        quotas.append(Quota(user, fs).get_quota().to_json())
    content = {
        'version': 1, 
        'timestamp': int(datetime.timestamp(datetime.now())), 
        'quotas': quotas
        }
    with open(f'{user_home}/ondemand/.quota.json', 'w') as outfile:
        json.dump(content, outfile, indent=4)


if __name__ == "__main__":
    main()

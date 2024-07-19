#!/bin/env python3

import os
import sys
import lustre_quota as lq

force_quota = False

def get_gids_from_directories(path):
    gids = []
    for item in os.listdir(path):
        item_path = os.path.join(path,item)
        if os.path.isdir(item_path):
            gids.append(str(os.stat(item_path).st_gid))
    return gids 

def copy_quota(account, quota_type, source_fs, dest_fs):
   account = str(account)
   source_quota = lq.LustreQuota.get_quota(account, source_fs, quota_type)
   print('Copying quota for %s from %s to %s: bsoft:%i bhard:%i isoft:%s ihard:%s' % 
         (account, source_fs, dest_fs, 
          source_quota.block_soft, source_quota.block_hard, 
          source_quota.inode_soft, source_quota.inode_hard))
   dest_quota = lq.LustreQuota.get_quota(account, dest_fs, quota_type)
   if dest_quota == source_quota:
       print('- Quota are the same on both file systems')
   elif not dest_quota.quota_exist() or force_quota:
       source_quota.set_quota(account, dest_fs, quota_type)
       print('- Transferred quota between the file systems')
   else:
       print('- Different quota already set on %s' % dest_fs)

# Check if right number of arguments has been provided
if len(sys.argv) < 3 or len(sys.argv) > 4:
   print('Error: Must specify source and destination file system.')
   sys.exit(-1)
source_file_system = sys.argv[1]
dest_file_system = sys.argv[2]

project_ids = get_gids_from_directories(sys.argv[1])

for id in project_ids:
   copy_quota(id, 'project', source_file_system, dest_file_system)

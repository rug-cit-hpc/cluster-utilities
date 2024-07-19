import sys
import subprocess

class LustreQuota:

    # Definitions the class uses
    lfscmd = '/usr/bin/lfs'
    quota_flag = {
        'user': '-u',
        'group': '-g',
        'project': '-p',
    }

    def __init__(self, block_usage, block_soft, 
                 block_hard, inode_usage, inode_soft, inode_hard):
         self.block_usage = block_usage
         self.block_soft = block_soft
         self.block_hard = block_hard
         self.inode_usage = inode_usage
         self.inode_soft = inode_soft
         self.inode_hard = inode_hard

    @classmethod
    def get_quota(cls, account, file_system, quota_type):
        cmdline = [cls.lfscmd, 'quota', cls.quota_flag[quota_type], account, file_system]
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        exit_code = p.wait()
        if exit_code !=0:
            print('Error: Problem reading quota.')
            sys.exit(-1)
        quota_found = False
        for line in output.decode('ASCII').splitlines():
            if file_system in line:
                quota_found =  True
                quota = [x.replace('*','') for x in line.split()]
        if not quota_found:
            print('Error: File system: %s not in quota output.' % file_system)
            print(output.decode('ASCII'))
            sys.exit(-1)
        return cls(int(quota[1]), int(quota[2]), int(quota[3]), 
                   int(quota[5]), int(quota[6]), int(quota[7]))

    def __eq__(self, other):
        return self.block_soft == other.block_soft and \
               self.block_hard == other.block_hard and \
               self.inode_soft == other.inode_soft and \
               self.inode_hard == other.inode_hard

    def quota_exist(self):
        return not self.block_soft == self.block_hard == self.inode_soft == self.inode_hard == 0

    def set_quota(self, account, file_system, quota_type):
        cmdline = [self.lfscmd, 'setquota', self.quota_flag[quota_type], account, 
                   '-b', str(self.block_soft), '-B', str(self.block_hard), 
                   '-i', str(self.inode_soft), '-I', str(self.inode_hard), file_system]
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        exit_code = p.wait()
        if exit_code !=0:
            print('Error: Problem setting quota.')
            sys.exit(-1)

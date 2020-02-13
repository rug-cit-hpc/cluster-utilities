import subprocess, json, os, argparse, grp
import pandas as pd
from datetime import datetime


def logwrite(string):
    logfile = open("/admin/cristian/UserQuotas/logfile.log", "a")
    today = datetime.today()
    str_today = today.strftime("%Y-%m-%d %H:%M:%S")
    logfile.write(str_today)
    logfile.write(" {}\n".format(string))
    logfile.close()


def strip_char(item):
    if item[-1] == '*':
        item = item[:-1]
    return int(item)


class DataError(Exception):
    pass


class Quota:
    def __init__(self, group, directory):
        self.group = group
        self.directory = directory
        self.raw = subprocess.check_output(['sudo', 'lfs', 'quota', '-g', str(self.group), str(self.directory)])
        self.check_raw()  # check the raw for errors before further processing
        # Initialize here just so we keep track of what's available in the object
        self.ref = str(self.raw, encoding='utf-8').split('\n')[2].split()

        self.sanity_check()
        self.dusage = int(strip_char(self.ref[1]))
        self.dalloc = int(strip_char(self.ref[2]))
        self.dlimit = int(strip_char(self.ref[3]))
        self.dgrace = self.ref[4]
        if self.ref[5][-1] == '*':
            self.fusage = int(self.ref[5][:-1])
        else:
            self.fusage = int(self.ref[5])
        self.falloc = int(self.ref[6])
        self.flimit = int(self.ref[7])


    def check_raw(self):
        if self.raw == 'Permission denied.':
            raise PermissionError()

    def sanity_check(self):
        # check if there even is a quota for this user group otherwise raise exception
        if self.ref[2] in {None, '0'} or self.ref[6] in {None, '0'}:
            raise DataError()

    def to_json(self):
        quota = {'user': self.group,
                 'path': self.directory + '/' + self.group,
                 'total_block_usage': self.dusage,
                 'block_limit': self.dalloc,
                 'total_file_usage': self.fusage,
                 'file_limit': self.falloc
                 }
        return quota


def get_users():
    test = subprocess.check_output(['getent', 'passwd'])
    test = [line.split(':') for line in str(test, encoding='utf-8').split('\n')]
    test = pd.DataFrame.from_records(test, columns=['Username', 'Passwd', 'UID', 'GID', 'Gecos', 'Home', 'Shell'])
    return test.sort_values(by='Username')


def main():
    logfile = open("/admin/cristian/UserQuotas/logfile.log", "a")
    logfile.close()

    excepted_users = ['adm', 'apache', 'bin', 'centos', 'chrony', 'cristian', 'daemon', 'dbus', 'egon', 'ftp', 'games',
                      'halt', 'lp', 'mail', 'munge', 'mysql', 'nfsnobody', 'nobody', 'nscd', 'nslcd', 'ondemand-nginx',
                      'operator', 'polkitd', 'postfix', 'root', 'rpc', 'rpcuser', 'saslauth', 'shutdown', 'sshd',
                      'sync', 'systemd-network', 'wim']
    users = get_users()
    for index, user in users.iterrows():
        if user['Username'] in excepted_users:
            continue
        # logwrite(os.getgrouplist(user['Username'], int(user['GID'])))
        quotas = []
        for filesystem in ['/home', '/data', '/scratch']:
            logwrite(f"INFO: Retrieving quota for {user['Username']} on {filesystem}")
            try:
                quota = Quota(group=user['Username'], directory=filesystem).to_json()
                quotas.append(quota)
            except DataError as e:
                logwrite(f'WARN: No quota for user {user["Username"]} on {filesystem}')
                continue
            except subprocess.CalledProcessError as e:
                logwrite(f'ERROR: {e}')
                continue
        content = {'version': 1, 'timestamp': int(datetime.timestamp(datetime.now())), 'quotas': quotas}
        with open(f'/tmp/jsons/{user["Username"]}.json', 'w') as outfile:
            json.dump(content, outfile, indent=4)


if __name__ == "__main__":
    main()

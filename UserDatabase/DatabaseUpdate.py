#!/usr/bin/env python3
import subprocess as sp
import sys as sys
from datetime import date, datetime

import ldap3 as ldap
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from sqlalchemy import create_engine

unknown = "UNK"


def logwrite(string):
    logfile = open("logfile.log", "a")
    today = datetime.today()
    str_today = today.strftime("%Y-%m-%d %H:%M:%S")
    logfile.write(str_today)
    logfile.write(" {}\n".format(string))
    logfile.close()


def password_decode():
    """
        Decode the password for the LDAP Peregrine account
    :return: password: string containing the LDAP Peregrine account password
    """
    input_file = open("LDAPPeregrine", "rb")
    enc_password = input_file.read()
    key1 = open("key.1", "r").read()
    key2 = open("key.2", "r").read()
    obj = AES.new(key1, AES.MODE_CBC, key2)
    password = obj.decrypt(enc_password)
    password = password[:8].decode("UTF-8")
    input_file.close()
    return password


def parse_ldap_results(ldap_results):
    """
        Parse the results returned by querying the LDAP
    :param ldap_results: Results from an LDAP query
    :return: users: pd.DataFrame containing the username, pnumber, department and faculty information for all users
    """
    names = [ldap_results[i]["fullName"][0] if ldap_results[i]["fullName"] else unknown
             for i in range(len(ldap_results))]
    p_numbers = [ldap_results[i]["uid"][0] if ldap_results[i]["uid"] else unknown for i in range(len(ldap_results))]
    departments = [ldap_results[i]["ou"][0] if ldap_results[i]["ou"] else "" for i in range(len(ldap_results))]
    users = pd.DataFrame(data=p_numbers, index=range(len(ldap_results)), columns=["Username"])
    users["Name"] = pd.DataFrame(data=names, index=range(len(ldap_results)))
    users["Department"], users["Faculty"] = (
        [','.join(departments[i].split(',')[0:-1]) if departments[i] else unknown for i in range(len(departments))],
        [departments[i].split(',')[-1] if departments[i] else unknown for i in range(len(departments))])
    umcg_filter = [users["Username"][i].startswith("umcg") for i in range(len(users))]
    users["Faculty"][umcg_filter] = "UMC"
    return users.replace(unknown, '')


def query_ldap():
    """
        Querying LDAP
    :return: users: pd.DataFrame containing user information from LDAP
    """
    ldap_conf = {}
    with open("LDAP.conf") as file:
        for line in file.readlines():
            key, value = line.split(":")[0].strip(), line.split(":")[1].strip()
            value = value.strip("\"")
            value = value.strip('\'')
            ldap_conf[key] = value
    server = ldap.Server(f"ldap://{ldap_conf['ldap_uri']}:{ldap_conf['ldap_port']}", use_ssl=True)
    username = f"{ldap_conf['ldap_username']}"
    password = f"{ldap_conf['ldap_password']}"
    connection = ldap.Connection(server=server, user=username, password=password, version=3, read_only=True)
    search_base = ldap_conf['ldap_search_base']
    try:
        search_filter = ldap_conf['ldap_search_filter']
        attributes = ["uid", "ou", "fullName"]
        connection.bind()
        connection.search(search_base=search_base, search_filter=search_filter, search_scope=ldap.SUBTREE,
                          attributes=attributes)
        results = [connection.response[i]["attributes"] for i in range(len(connection.response))]
        users = parse_ldap_results(results)
        return users
    except ConnectionRefusedError:
        print("Invalid password")
        sys.exit()
    finally:
        connection.unbind()


def create_ldap_db(filename):
    """
        Write LDAP user information to file
    :return:
    """
    new_users = query_ldap()
    new_users.to_csv(filename)


def read_db(filename):
    users = pd.DataFrame()
    try:
        users = pd.read_csv(filename, index_col=0, sep=",", names=["Username", "Name", "Department", "Faculty"],
                            header=0)
        users.fillna(unknown, inplace=True)
    except IOError:
        print("The user database does not exist. Please run \"create_ldap_db()\" to create it from LDAP.")

    return users


def read_imanager_db(filename):
    users = pd.DataFrame()
    try:
        users = pd.read_csv(filename, names=["Username"])
    # users.fillna(unknown, inplace=True)
    except IOError:
        print("The user database does not exist. Please run \"create_ldap_db()\" to create it from LDAP.")

    return users


def query_sreport():
    sreport = sp.Popen(["sreport", "cluster", "AccountUtilizationByUser", "format=Login,Used", "-n", "-P"],
                       stdout=sp.PIPE)
    report, error = sreport.communicate()
    users = [report.split()[i].decode("utf-8").split('|')[0] for i in range(len(report.split()))]
    sr_users = pd.DataFrame(users, columns=["Username"])
    sr_users = sr_users[sr_users["Username"] != ""]
    return sr_users


def query_saccmgr():
    sacctmgr_report = sp.Popen(["sacctmgr", "show", "user", "-P"], stdout=sp.PIPE)
    report, error = sacctmgr_report.communicate()
    users = [report.decode("utf-8").split('\n')[i].split('|')[0] for i in range(1, len(report.split()))]
    sr_users = pd.DataFrame(users, columns=["Username"])
    sr_users = sr_users[sr_users["Username"] != ""]
    return sr_users


def update_db(filename, list_of_exceptions, local_users):
    """
        Update the database
    :param filename: File to write the updated information to
    :param list_of_exceptions: Exceptions that shouldn't be updated
    :return:
    """

    # Read the existing users from the file
    old_users = pd.read_csv("UserDatabase.csv", index_col=0, infer_datetime_format="%Y-%m-%d", parse_dates=[5, 6])
    old_users['StartDate'] = old_users['StartDate'].dt.date
    old_users['EndDate'] = old_users['EndDate'].dt.date
    # old_users = old_users.sort_values(by="Username")
    # old_users = old_users.reset_index(drop=True)
    # old_users.to_csv(filename + '.csv', date_format="%Y-%m-%d")
    # print(old_users.tail())
    # return 0

    # Read the active users from LDAP
    ldap_users = query_ldap()
    ldap_users = ldap_users.sort_values(by="Username")
    ldap_users = ldap_users.reset_index(drop=True)
    ldap_users = ldap_users.assign(StartDate=pd.Series(date.today()))
    ldap_users = ldap_users.assign(EndDate=pd.Series(pd.NaT))
    ldap_users = ldap_users.assign(Active=pd.Series(1.0))

    # Check whether some active users have been removed
    active_users = old_users[old_users['Active'] == 1.0]
    for user_index, active_user in active_users.iterrows():
        if (active_user['Username'] not in ldap_users['Username'].values) and \
                (active_user['Username'] not in local_users):
            logwrite(f"INFO:    User {active_user['Username']} has been removed")
            old_users.loc[user_index, 'EndDate'] = date.today()
            old_users.loc[user_index, 'Active'] = 0.0

    users = old_users

    # For each active user, check whether they already exist in the database, and update if necessary
    for index, row in ldap_users.iterrows():
        # Do not update the exceptions
        if row['Username'] in list_of_exceptions.keys():
            continue

        # Do not update UMCG users
        if row['Username'].startswith("umcg"):
            continue

        # Is the username already present in the database?
        existing_users = old_users[old_users['Username'] == row['Username']]
        if len(existing_users) > 0:
            # Select the currently active user
            active_user = existing_users[existing_users['Active'] == 1.0]

            # Are more than one active entries for the user? There shouldn't be!!!
            if len(active_user) > 1:
                logwrite(f"ERROR:   {row['Username']} has more than one active user in the database")
                exit(1)
            # Are all entries for this user inactive? Then add a new entry, no updating necessary.
            elif len(active_user) < 1:
                logwrite(f'INFO:    Re-added user {row["Username"]}')
                row['StartDate'] = date.today()
                row['EndDate'] = pd.NaT
                row['Active'] = 1.0
                users = users.append(row)
            else:
                if (row['Name'] == users.loc[active_user.index[0], "Name"]) and \
                        (row['Department'] == users.loc[active_user.index[0], "Department"]) and \
                        (row['Faculty'] == users.loc[active_user.index[0], "Faculty"]):
                    continue
                else:
                    if (row['Department'] == '') or (row['Faculty'] == ''):
                        continue
                    else:
                        logwrite(f'INFO:    Updated user {row.Username}')
                        users.loc[active_user.index[0], "EndDate"] = date.today()
                        users.loc[active_user.index[0], "Active"] = 0.0
                        row['StartDate'] = date.today()
                        row['EndDate'] = pd.NaT
                        row['Active'] = 1.0
                        users = users.append(row)
        else:
            logwrite(f'INFO:    Added user {row.Username}')
            row['StartDate'] = date.today()
            row['EndDate'] = pd.NaT
            row['Active'] = 1.0
            users = users.append(row)

    users = users.sort_values(by="Username")
    users = users.reset_index(drop=True)
    users['Department'] = users['Department'].replace('', 'UNK')
    users['Faculty'] = users['Faculty'].replace('', 'UNK')
    users.to_csv(filename + ".csv", date_format="%Y-%m-%d")
    engine = create_engine(f"sqlite:///{filename}" + ".db")
    users.to_sql("PeregrineUsers", engine, if_exists="replace")

    return 0


def main():
    list_of_exceptions = {"f112450": "C. Navarro", "f112474": "Y. Kriksin", "f112614": "V. Risnita",
                          "f112803": "E. Eliav", "f112829": "L. Pasteka", "f112847": "S. Schmidt",
                          "f112964": "E. Carroll", "f113112": "M. Ilias", "slurmmon": "Slurm Monitor",
                          "bob": "B.E. Droge", "cristian": "C.A. Marocico", "fokke": "F. Dijkstra",
                          "ger": "G.J.C. Strikwerda", "kees": "K. Visser", "laurent": "L. Jensma",
                          "monk": "L.R.B. Schomaker", "robin": "R. Teeninga", "root": "root",
                          "ruben": "R. van Dijk", "test": "Test Account", "wim": "W.K. Nap",
                          "f114656": "Lukas Pasteka"}
    local_users = ['monk', 'root', 'slurmmon']
    update_db("UserDatabase", list_of_exceptions, local_users)
    return 0


if __name__ == "__main__":
    main()

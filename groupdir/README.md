# Group Directories

Use the script `create_groupdir.sh` to create a group directory for a specified group.
The script also takes care of setting permissions, ownerships, ACLs, and quotas.

## Usage
Just run the script as root:
```
sudo ./create_groupdir.sh
```

All required information will be asked, with appropriate defaults where possible.
Make sure to use the full name of the group, i.e. including the `pg-` prefix.

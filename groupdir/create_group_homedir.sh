#!/bin/bash

if [ -z $1 ]; then
   echo "Supply the name of the group"
   exit
fi

#if [ -z $2 ]; then
#   echo "Supply the primary owner of the group"
#   exit
#fi

#owner=$2
#if ! id $owner; then
#   echo "User $owner cannot be found"
#   exit
#fi


groupname=$1
gid=$( getent group $groupname | awk -F ':' '{print $3}' )
if [ -z $gid ]; then
   echo "Group $groupname cannot be found"
   exit
fi

homenumber=$( expr $gid % 4 + 1)

homedir=/home${homenumber}
echo $homedir

sudo mkdir $homedir/$groupname
sudo chown root.$1 $homedir/$groupname
sudo chmod 0770 $homedir/$groupname
sudo chmod g+s $homedir/$groupname
#
sudo setfacl -d -m group:$groupname:rwX $homedir/$groupname
# 
# Set quota on home directory
#
ssh 172.23.15.20${homenumber} sudo xfs_quota -x -c \'project -s -p /nfs/home/${groupname} ${gid}\' /nfs

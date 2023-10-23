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

lfs mkdir -c 5 /scratch/$groupname
lfs mkdir -c 2 /projects/$groupname
chown root.$1 /scratch/$groupname
chown root.$1 /projects/$groupname
chmod 0770 /scratch/$groupname
chmod 0770 /projects/$groupname
chmod g+s /scratch/$groupname
chmod g+s /projects/$groupname

chattr -p $gid +P /scratch/$groupname
chattr -p $gid +P /projects/$groupname

lfs setquota -p $gid -b 250G -B 250G -i 500k -I 500K /scratch
lfs quota -ph $gid /scratch
lfs setquota -p $gid -b 250G -B 250G -i 500k -I 500K /projects
lfs quota -ph $gid /projects

setfacl -d -m group:$groupname:rwX /scratch/$groupname
setfacl -d -m group:$groupname:rwX /projects/$groupname

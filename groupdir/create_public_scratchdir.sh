#!/bin/bash

if [ $# -eq 0 ]; then
   echo "Usage: $0 <group dir name> [<group owner>]"
   exit
fi

groupdir=$1
groupowner=$2

if [ -z $groupowner ]; then
    # default groupowner: hb-public-<lowercase name of group dir>
    groupowner="hb-public-$(echo $groupdir | tr '[:upper:]' '[:lower:]')"
fi

echo "Setting up /scratch/public/$groupdir with group owner $groupowner"

gid=$( getent group $groupowner | awk -F ':' '{print $3}' )
if [ -z $gid ]; then
    echo "Group $groupowner cannot be found"
    exit
fi

lfs mkdir -c 5 /scratch/public/$groupdir
chown root.$groupowner /scratch/public/$groupdir
chmod 0775 /scratch/public/$groupdir
chmod g+s /scratch/public/$groupdir

chattr -p $gid +P /scratch/public/$groupdir

lfs setquota -p $gid -b 250G -B 250G -i 500k -I 500K /scratch
lfs quota -ph $gid /scratch

setfacl -d -m group:$groupowner:rwX,other:rX /scratch/public/$groupdir

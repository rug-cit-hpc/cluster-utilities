#!/bin/bash

if [ -z $1 ]; then
   echo "Supply the name of the group"
   echo "and optionally the quota in GiB and again optionally the inode limit"
   exit
fi

groupname=$1
gid=$( getent group $groupname | awk -F ':' '{print $3}' )
if [ -z $gid ]; then
   echo "Group $groupname cannot be found"
   exit
fi

swdir=/userapps
echo $swdir

sudo mkdir $swdir/$groupname
sudo chown root.$1 $swdir/$groupname
sudo chmod 0770 $swdir/$groupname
sudo chmod g+s $swdir/$groupname
#
sudo setfacl -d -m group:$groupname:rwX $swdir/$groupname
# 
# Set quota on software directory
#
ssh 172.23.15.207 sudo xfs_quota -x -c \'project -s -p /nfs/userapps/${groupname} ${gid}\' /nfs

if [ -z $2 ]; then 
   echo "Set space quota to defaults"
   ssh 172.23.15.207 sudo xfs_quota -x -c \'limit -p bsoft=0 bhard=0 ${gid}\' /nfs
else
   echo "Set space quota to ${2}GB" 
   ssh 172.23.15.207 sudo xfs_quota -x -c \'limit -p bsoft=${2}g bhard=${2}g ${gid}\' /nfs
fi
if [ -z $3 ]; then
   echo "Set inode quota to defaults"
   ssh 172.23.15.207 sudo xfs_quota -x -c \'limit -p isoft=0 bhard=0 ${gid}\' /nfs
else
   echo "Set inode quota to ${3}"
   ssh 172.23.15.207 sudo xfs_quota -x -c \'limit -p isoft=${3} bhard=${3} ${gid}\' /nfs
fi

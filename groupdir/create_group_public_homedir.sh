#!/bin/bash

if [ -z $1 ]; then
   echo "Supply the name of the group"
   exit
fi

if [ -z $2 ]; then
   echo "Supply the primary owner of the group"
   exit
fi

owner=$2
if ! id $owner; then
   echo "User $owner cannot be found"
   exit
fi


foldername=$1
groupname=${1}-public
gid=$( getent group $groupname | awk -F ':' '{print $3}' )
if [ -z $gid ]; then
   echo "Group $groupname cannot be found"
   exit
fi

homenumber=1

homedir=/home${homenumber}/public
echo $homedir

sudo mkdir $homedir/$foldername
sudo chown $owner.${groupname} $homedir/$foldername
sudo chmod 0755 $homedir/$foldername
sudo chmod g+s $homedir/$foldername
#
#sudo setfacl -d -m group:$groupname-public:rwX $homedir/$groupname
# 
# Set quota on home directory
#
ssh 172.23.15.20${homenumber} sudo xfs_quota -x -c \'project -s -p /nfs/home/public/${foldername} ${gid}\' /nfs

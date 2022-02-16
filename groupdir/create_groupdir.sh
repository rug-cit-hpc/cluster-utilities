#!/bin/bash
#
# Script to create a group directory with the right permissions and quotas.
#

function echo_green() {
    echo -e "\e[32m$1\e[0m"
}

function echo_red() {
    echo -e "\e[31m$1\e[0m"
}

function echo_yellow() {
    echo -e "\e[33m$1\e[0m"
}

function error() {
    echo_red "ERROR: $1" >&2
    exit 1
}

if (( $EUID != 0 )); then
    error "Please run as root."
    exit
fi

# Determine name of the group for which a directory has to be created.
read -p "Group name: " groupname
if ! [ $(getent group ${groupname}) ]; then
    error "Group does not exist. Please make the group first."
    exit 1
fi

# Make the group directory.
read -p "Group directory: " -i "/data/${groupname}" -e groupdir
if [ -d "${groupdir}" ]; then
    echo_yellow "Group directory ${groupdir} already exists."
else
    mkdir ${groupdir}
    echo_green "Created group directory ${groupdir}"
fi
echo ""

# Set the ownership of the group directory.
read -p "Group directory owner: " groupowner
if ! [ $(getent group ${groupname}) ]; then
    error "User does not exist."
    exit 1
fi
chown ${groupowner}:${groupname} ${groupdir}
echo_green "Changed ownership of ${groupdir} to ${groupowner}:${groupname}"
echo ""

# Set the permissions on the group directory.
read -p "Permissions on group directory: " -i "u+rwx,g+rwxs,o-rwx" -e groupperms
chmod ${groupperms} ${groupdir}
echo_green "Changed permissions on ${groupdir} to ${groupperms}."
echo ""

# Set a (default) ACL for the group directory.
read -p "(Default) ACL setting for group: " -i "rwX" -e groupdiracl
setfacl -R -m g:${groupname}:${groupdiracl} ${groupdir}
setfacl -R -d -m g:${groupname}:${groupdiracl} ${groupdir}
echo_green "(Default) ACL on ${groupdir} has been set to g:${groupname}:${groupdiracl}"
echo ""

# Set quotas for the group on all file systems.
read -p "Group quota on /home: " -i "-b 4M -B 4M -i 2048 -I 2048" -e groupquotahome
lfs setquota -g ${groupname} ${groupquotahome} /home
echo_green "Quota on /home set to: ${groupquotahome}"
echo ""
read -p "Group quota on /data: " -i "-b 250G -B 250G -i 1000k -I 1100k" -e groupquotadata
lfs setquota -g ${groupname} ${groupquotadata} /data
echo_green "Quota on /data set to: ${groupquotadata}"
echo ""
read -p "Group quota on /scratch: " -i "-b 10T -B 20T -i 5000k -I 5500k" -e groupquotascratch
lfs setquota -g ${groupname} ${groupquotascratch} /scratch
echo_green "Quota on /scratch set to: ${groupquotascratch}"
echo ""

echo_green "Done!"

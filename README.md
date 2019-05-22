# cluster-utilities
A collection of utilities that don't need their own repositories.

## pgquota
Shows file and storage quota for all user groups a user is part of. Requires `lfs`.
Renamed from "Quota" because 'quota' is already being used as the name of some default software on Centos7.

## moduleDiff
shows difference in installed modules on different architectures on the cluster. Compare two directories like so: `./moduleDiff.py /apps/<architecture>/modules/all/ /apps/<architecture2>/modules/all/`. Using option `-s` enables 'shallow' mode wich does not compare versions of modules installed on both but only gives an overview of what general modules are missing from certain architectures.

## ebBackup
A script that shouldn't need to be run all that often if ever again. Therefore to use it properly, you have to edit the paths to repositories and possibly software (if those ever change) at the beginning of the file. To use, simply run the script once you have entered correct repository paths.

Behaviour is the following: This script will check for all .eb files in software, any of these that do not appear in either repository will be backed up to the cit-easybuild repository. If directories for software do not exist in the cit-easybuild repository, they will be created.

# cluster-utilities
A collection of utilities that don't need their own repositories.

## Quota
Shows file and storage quota for all user groups a user is part of. Requires `lfs`.

## moduleDiff
shows difference in installed modules on different architectures on the cluster. Compare two directories like so: `./moduleDiff.py /apps/<architecture>/modules/all/ /apps/<architecture2>/modules/all/`. Using option `-s` enables 'shallow' mode wich does not compare versions of modules installed on both but only gives an overview of what general modules are missing from certain architectures.

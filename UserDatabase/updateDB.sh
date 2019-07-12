#!/bin/bash

. ~/.bash_profile

module purge
module load Python/3.6.4-foss-2018a
source $HOME/.envs/UserDatabase/bin/activate
pwd
python DatabaseUpdate.py

#!/bin/bash

#SBATCH --job-name=test_job
#SBATCH --time=00:01:00
#SBATCH --tasks=7
#SBATCH --mem=1000
#SBATCH --partition=short

srun ./peregrine_test_mpi
echo  # print a blank line between script output and slurm 'cancel' statement in the job output file
sleep 10

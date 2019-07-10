#!/bin/bash

#SBATCH --job-name=test_job
#SBATCH --time=00:01:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1000
#SBATCH --partition=short

echo Peregrine test job starting...
echo [Sleeping for 5 seconds]
sleep 20
echo Peregrine test job complete.

#./peregrine_test_omp

#export OMP_NUM_THREADS=7

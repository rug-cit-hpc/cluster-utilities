#!/bin/bash

#SBATCH --job-name=test_job
#SBATCH --time=00:01:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1000
#SBATCH --partition=short

#export OMP_NUM_THREADS=7
./peregrine_test_omp
sleep 10

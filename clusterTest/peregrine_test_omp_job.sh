#!/bin/bash

#SBATCH --job-name=test_job
#SBATCH --time=00:01:00
#SBATCH --cpus-per-task=7
#SBATCH --mem=1000
#SBATCH --partition=short

./peregrine_test_omp

sleep 10

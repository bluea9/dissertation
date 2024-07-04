#!/bin/bash

# Grid Engine options
#$ -wd /exports/eddie/scratch/s2562233/dissertation/Docking_runs/2VXT_surf_10

# Set PE
#$ -pe sharedmem 10
#$ -l h_vmem=1G
#$ -l h_rt=00:20:00
#$ -o eddie-test-run.o
#$ -e eddie-test-run.e

# Setup the environment modules command
source /etc/profile.d/modules.sh

# Load modules if required
module load anaconda

conda activate haddock2.5

cd /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/
# Change Haddock configuration file
python install.py config.eddie
source haddock_configure.sh

which python
conda list

# Testing haddock command
# python3 /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock/run_haddock.py -h

# Run docking
cd /exports/eddie/scratch/s2562233/dissertation/Docking_runs/2VXT_surf_10/run1
python /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock/run_haddock.py

#!/bin/bash

# Grid Engine options
#$ -cwd
#$ -V

# Set PE
#$ -l h_vmem=1G
#$ -l h_rt=00:03:00
#
# Setup the environment modules command
source /etc/profile.d/modules.sh

# Load modules if required
module load anaconda

# Installing Haddock
cd /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/
python3 install.py config.eddie
source haddock_configure.sh

cd /exports/eddie/scratch/s2562233/dissertation/test-eddie

# Testing haddock command
# haddock2.5 --help #should give the same output
python3 /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock/run_haddock.py -h

conda deactivate

#$ -o eddie-testing.o
#$ -e eddie-testing.e
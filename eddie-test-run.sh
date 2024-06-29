#!/bin/bash

# Grid Engine options
#$ -wd /exports/eddie/scratch/s2562233/dissertation/dock_run/2VXT_surf_10m_unamb
#$ -V

# Set PE
#$ -pe sharedmem 10
#$ -l h_vmem=1G
#$ -l h_rt=00:20:00
#$ -o eddie-test-run.o
#$ -e eddie-test-run.e
#
# Setup the environment modules command
source /etc/profile.d/modules.sh

# Load modules if required
module load anaconda

conda activate haddock2.5
conda install mako #probably not necessary

cd /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/
python3 install.py config.eddie
source haddock_configure.sh

which python3
conda list

# Testing haddock command
# haddock2.5 --help #should give the same output
# python3 /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock/run_haddock.py -h

# Run docking
cd /exports/eddie/scratch/s2562233/dissertation/dock_run/2VXT_surf_10m_unamb/run1
python3 /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock/run_haddock.py

conda list
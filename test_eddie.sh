#!/bin/sh
# Grid Engine options (lines prefixed with #$)
#$ -N test_100m_32c              
#$ -wd /exports/eddie/scratch/s2562233/dissertation/temp/run1                  
#$ -l h_rt=00:30:00 
#$ -l h_vmem=1G
#$ -pe mpi 32
#  These options are:
#  job name: -N
#  use the current working directory: -cwd or defined path -wd
#  runtime limit of 5 minutes: -l h_rt
#  memory limit of 1 Gbyte: -l h_vmem
# Initialise the environment modules
. /etc/profile.d/modules.sh

# Load conda and activate environment
module load conda
conda activate haddock2.5

# Install Haddock
python3 /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/install.py /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/config.eddie
source /exports/eddie/scratch/s2562233/dissertation/haddock2.5-2024-03/haddock_configure.sh

haddock2.5 > &haddock_test-eddie.out
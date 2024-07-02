#!/usr/bin/python3.12
import os, shutil

# Path to file with antibody-antigen complexes PDB IDs
file = '~/reduced_set/complex_list_short.txt'
file = os.path.expanduser(file)

# Path to directory with file restraints from Haddock paper
path_restraints = '~/reduced_set/'
path_restraints = os.path.expanduser(path_restraints)

# Path to directory with HADDOCK-ready files
path_ready = '~/HADDOCK/BM5-clean/HADDOCK-ready'
path_ready = os.path.expanduser(path_ready)

# Path to directory to store files for HADDOCK replication study
parent_dir = '~/others/testing_dirs'
parent_dir = os.path.expanduser(parent_dir)

complex_list = []
try:
    with open(file, 'r') as txtfile:
        lines=txtfile.readlines()
        complex_list = [line.strip() for line in lines]
except:
    print(f"The file '{file}' does not exist.")
    exit()

try:
    os.chdir(parent_dir)
except:
    print(f"The directory '{parent_dir}' does not exist.")
    exit()

for id in complex_list:
    ready_dir = os.path.join(path_ready, id)
    complex_dir = os.path.join(parent_dir, id+'_all')
    try:
        os.chdir(complex_dir)
        ab = ready_dir + '/' + id + '_r_u.pdb'
        ab_cp = id + '_r_u.pdb'
        ag = ready_dir + '/' + id + '_l_u.pdb'
        ag_cp = id + '_l_u.pdb'
        restraints_file = path_restraints + id + '-restr.txt' 
        restraints_cp = id + '-restr.txt'
        shutil.copy(ab, ab_cp)
        shutil.copy(ag, ag_cp)
        shutil.copy(restraints_file, restraints_cp)
    except:
        print(f"The directories for each complex do not exist.")
        exit()

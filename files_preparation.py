#!/usr/bin/python3.12
import os, shutil

# Path to file with antibody-antigen complexes PDB IDs
file = '~/reduced_set/complex_list.txt'
file = os.path.expanduser(file)

# Path to directory with file restraints from Haddock paper
path_restraints = '~/reduced_set/'
path_restraints = os.path.expanduser(path_restraints)

# Path to directory with HADDOCK-ready files
path_ready = '~/HADDOCK/BM5-clean/HADDOCK-ready'
path_ready = os.path.expanduser(path_ready)

# Path to directory to store files for HADDOCK replication study
run_rep = '~/Replication'
run_rep = os.path.expanduser(run_rep)

complex_list = []
try:
    with open(file, 'r') as txtfile:
        lines=txtfile.readlines()
        complex_list = [line.strip() for line in lines]
except:
    print(f"The file '{file}' does not exist.")
    exit()

try:
    os.makedirs(run_rep)
except:
    print(f"The directory '{run_rep}' already exists.")
    exit()

for id in complex_list:
    ready_dir = os.path.join(path_ready, id)
    print('ready dir:'+ready_dir)
    complex_dir = os.path.join(run_rep, id)
    print('complex dir:'+complex_dir)
    os.mkdir(complex_dir)
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

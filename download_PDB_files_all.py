#!/usr/bin/python3.12
import csv, os, Bio
from Bio.PDB import PDBList
# Requires environment with Biopython

# Extract PBD IDs from structures in Benchmark5.5 and download structures

# Path to CSV file with antibody-antigen complexes PDB IDs
csv_file = '~/DATASET/B55_update.csv'
csv_file = os.path.expanduser(csv_file)

# Columns to extract
complex_id = 'Complex'
antibody_id = 'PDB_ID_1'
antigen_id = 'PDB_ID_2'

# Directory to save the output files (directories PDB_complex, PDB_ab and PDB_ag)
files_dir = '~/DATASET'
files_dir = os.path.expanduser(files_dir)

complex_dir = os.path.join(files_dir, 'PDB_complex')
ab_dir = os.path.join(files_dir, 'PDB_ab')
ag_dir = os.path.join(files_dir, 'PDB_ag')

try:
    os.makedirs(complex_dir)
except:
    print(f"The directory '{complex_dir}' already exists.")
    exit()

complex_list = []
ab_list = []
ag_list = []

try:
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            complex = row[complex_id]
            complex_list.append(complex[0:4])
            ab_id = row[antibody_id]
            ab_list.append(ab_id[0:4])
            ag_id = row[antigen_id]
            ag_list.append(ag_id[0:4])
except:
    print(f"The file '{csv_file}' does not exist.")
    exit()

# Downloaded files end with .ent, change to .pdb and only name with PDB ID
pdbl = PDBList()
for id in complex_list:
    long_name = pdbl.retrieve_pdb_file(id, file_format='pdb', pdir=complex_dir)
    pdb_name = os.path.join(complex_dir, f'{id}.pdb')
    try:
        os.rename(long_name, pdb_name)
    except:
        print(f'PDB ID {id} not found.')

for id in ab_list:
    long_name = pdbl.retrieve_pdb_file(id, file_format='pdb', pdir=ab_dir)
    pdb_name = os.path.join(ab_dir, f'{id}.pdb')
    try:
        os.rename(long_name, pdb_name)
    except:
        print(f'PDB ID {id} not found.')

for id in ag_list:
    long_name = pdbl.retrieve_pdb_file(id, file_format='pdb', pdir=ag_dir)
    pdb_name = os.path.join(ag_dir, f'{id}.pdb')
    try:
        os.rename(long_name, pdb_name)
    except:
        print(f'PDB ID {id} not found.')
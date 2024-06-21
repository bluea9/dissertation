#!/usr/bin/python3.12
import csv, os

# Extract PBD IDs from structures in Benchmark5.5

# Path to CSV file with antibody-antigen complexes PDB IDs
csv_file = '~/DATASET/B55_update.csv'
csv_file = os.path.expanduser(csv_file)

# Columns to extract
complex_id = 'Complex'
antibody_id = 'PDB_ID_1'
antigen_id = 'PDB_ID_2'

# Create directory to save the output files
id_dir = '~/DATASET/list_ids'
id_dir = os.path.expanduser(id_dir)

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

try: 
    os.makedirs(id_dir)
except:
    print("The directory specified already exists.")
    exit()

os.chdir(id_dir)
with open('PDB_ID_complex.txt', 'w') as file:
    for id in complex_list:
        file.write(f"{id}\n")

with open('PDB_ID_antibodies.txt', 'w') as file:
    for id in ab_list:
        file.write(f"{id}\n")

with open('PDB_ID_antigens.txt', 'w') as file:
    for id in ag_list:
        file.write(f"{id}\n")

with open('PDB_ID.txt', 'w') as file:
    for bound, ab, ag in zip(complex_list, ab_list, ag_list):
        file.write(f"{bound}\t{ab}\t{ag}\n")
#!/usr/bin/python3.12
import csv, os

# Variables to modify for new files
# Path to CSV file with antibody aa sequences
csv_file = '~/Sequences/antibodies_info.csv'

# Columns to extract
seq_id = 'sequence_id'
seq_aa = 'sequence_alignment_aa'

# Directory to save the output files, the directory fasta_seqs will be created here
seqs_dir = '~/Sequences'

# Expand paths
csv_file = os.path.expanduser(csv_file)
seqs_dir = os.path.expanduser(seqs_dir)

# Dictionary to store the ab sequences
seqs_dict = {}

try:
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            key = row[seq_id]
            value = row[seq_aa]
            value = value.replace(".","")
            seqs_dict[key] = value
except:
    print(f"The file '{csv_file}' does not exist.")
    exit()

# Create FASTA file for each antibody
seqs_dir = os.path.join(seqs_dir, "fasta_seqs")
try:
    os.makedirs(seqs_dir)
except: 
    print("The directory fasta_seqs already exists.")
    exit()

os.chdir(seqs_dir)
ab_counter = 1
temp_list = []
for key, value in seqs_dict.items():
    temp_list.append((key, value))
    if len(temp_list) == 2:
        ab_file = os.path.join(seqs_dir, f'HM{ab_counter}.fasta')
        with open(ab_file, 'w') as file:
            for id, aa in temp_list:
                file.write(f'>{id}\n{aa}\n')
        temp_list.clear()
        ab_counter += 1

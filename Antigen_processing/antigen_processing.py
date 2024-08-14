"""
Downloads structures in PDB format from the RCSB website and formats them as
antigens for docking with Haddock.

Usage:
    python antigen_processing.py <csv file with antigens PDB ID list> \ 
    <absolute/path/to/output/directory>

This script requieres the pdb-tools repository.
"""
import argparse, os, csv, subprocess

# Tools
pdbtools = os.path.expanduser('~/software/pdb-tools/pdbtools')

parser = argparse.ArgumentParser()
parser.add_argument('antigen_list', type=str, help='csv file with antigens PDB ID list')
parser.add_argument('output_dir', type=str, help='Absolute path to directory to save PDB files')

args = parser.parse_args()
antigen_file = os.path.expanduser(args.antigen_list)
output_dir = os.path.expanduser(args.output_dir)

file_list = [antigen_file]
dir_list = [pdbtools, output_dir]

# FILE AND DIRECTORY VERIFICATION
def verify_file(file_list):
    for file in file_list:
        if os.path.isfile(file) and os.access(file, os.X_OK):
            pass
        else:
            print(f"File {file} does not exist or reading permission is not granted.")
            exit()

def verify_dir(dir_list):
    for dir in dir_list:
        if os.path.isdir(dir) and os.access(dir, os.R_OK | os.W_OK | os.X_OK):
            pass
        else:
            print("Directory does not exist or not all permissions are granted.")
            exit()

verify_file(file_list)
verify_dir(dir_list)

# Function to get the values on a column from a csv file
def get_column_values(file, col_index):
    values = []
    with open(file, newline='') as csvfile:
        content = csv.reader(csvfile)
        for row in content:
            values.append(row[col_index])
    return values

def try_subprocess(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as error:
        print(f"An error occurred: {error.stderr.decode()}")
    except Exception as error:
        print(f"Unexpected error: {str(error)}")


# Get list of antigen PDB IDs
antigen_list = get_column_values(antigen_file,0)
print(antigen_list)

os.chdir(output_dir)

for antigen in antigen_list:
    print(antigen)
# Get PDB antigen files
    fetch = 'python ' + pdbtools + '/pdb_fetch.py '
# Rename chain
    chain = pdbtools + '/pdb_chain.py -B'
# Renumber residues
    renum = pdbtools + '/pdb_reres.py' 
# Keep ATOM lines only
    atom = " grep '^ATOM' | "
# Add TER and END
    tidy = pdbtools + '/pdb_tidy.py'
    file_name = antigen.upper() + '-ag-HADDOCK.pdb'
    try: 
        command = fetch + antigen + ' | ' + chain + ' | ' + renum + ' | ' + atom + tidy + ' > ' + file_name
        subprocess.run(command, shell=True)
    except:
        print(f'Antigen {antigen} could not be processed.')

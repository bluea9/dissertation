import argparse, os, subprocess

# Tools
immunopdb = os.path.expanduser('~/software/ANARCI/Example_scripts_and_sequences/ImmunoPDB.py')
haddockformat = os.path.expanduser('~/software/HADDOCK-antibody-antigen/ab_haddock_format.py')
pdbtools = os.path.expanduser('~/software/pdb-tools/pdbtools')
haddocktools = os.path.expanduser('~/software/haddock-tools')

parser = argparse.ArgumentParser()
parser.add_argument('complex_file', type=str, help='Antibody-Antigen complex in PDB format.')
parser.add_argument('antigen_chain', type=str, help='Chain with the antigen in the complex.')

args = parser.parse_args()
complex_file = args.complex_file
antigen_chain = args.antigen_chain

antigen_chain = antigen_chain.upper()
if len(antigen_chain) == 1 and antigen_chain.isalpha():
    pass
else:
    print('Antigen chain must be entered as one letter.')
    exit()

file_list = [complex_file]
dir_list = [pdbtools, haddocktools]

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

def try_subprocess(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as error:
        print(f"An error occurred: {error.stderr.decode()}")
    except Exception as error:
        print(f"Unexpected error: {str(error)}")

def delete_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print(f'{file} does not exist.')
    except PermissionError:
        print(f'Permission denied.')
    except Exception as error:
        print(f'An error occurred while trying to delete {file}: {error}')

# Renumber antibody structures according to Clothia system
complex = os.path.splitext(complex_file)[0]
fv_file = complex + '-ch.pdb'
command = ['python', immunopdb, '-i', complex_file, '-o', fv_file, '--scheme', 'c', '--fvonly', '--rename', '--splitscfv']
try_subprocess(command)

# Change antibody format to only have chain A 
fv_haddock_file = complex + '-HADDOCK.pdb'
command2 = 'python ' + haddockformat + ' ' + fv_file + ' ' + fv_haddock_file + ' A'
subprocess.run(command2, shell=True)

# Split antibody-antigen complex in different chains
tool = pdbtools + '/pdb_splitchain.py'
command3 = 'python ' + tool + ' ' + args.complex_file
subprocess.run(command3, shell=True)

# Replace antigen chain name for chain B to match predicted models
tool = pdbtools + '/pdb_rplchain.py'
chains = ' -' + antigen_chain + ':B '
antigen_file = complex + '_' + antigen_chain + '.pdb '
new_file = complex + '_ligand.pdb'
command4 = 'python ' + tool + chains + antigen_file + ' > ' + new_file
subprocess.run(command4, shell=True)

# Merge antibody fv region and antigen in one file. 
tool = pdbtools + '/pdb_merge.py '
merge = complex + '-merged.pdb'
command5 = 'python ' + tool + fv_haddock_file + ' ' + new_file + ' > ' + merge
subprocess.run(command5, shell=True)

# Run pdb_sort and keep only rows with ATOM
tool = pdbtools + '/pdb_sort.py '
sorted = complex + '-sorted.pdb'
command6 = 'python ' + tool + merge + ' > ' + sorted
subprocess.run(command6, shell=True)
with open(sorted, 'r') as file:
    content = file.readlines()
atom_lines = [line for line in content if line.startswith('ATOM')]
with open(sorted, 'w') as file:
    file.writelines(atom_lines)

# Run pdb_tidy to add TER END
tool = pdbtools + '/pdb_tidy.py '
target = complex.upper() + '-target.pdb'
command7 = 'python ' + tool + sorted + ' > ' + target
subprocess.run(command7, shell=True)

# Clean up directory
delete_file(complex+'-ch.pdb')
delete_file(fv_haddock_file)
delete_file(merge)
delete_file(sorted)
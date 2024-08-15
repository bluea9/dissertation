import argparse, os, subprocess, re

# Script to generate target file with Fv + antigen given complex PDB ID and antigen chain(s). 
# Note1: Results stored in working directory.
# Note2: Requires conda environment antibody_anarci_env (haddock_antibody environment + Biopython 1.84.dev0)

# Tools
immunopdb = os.path.expanduser('~/software/ANARCI/Example_scripts_and_sequences/ImmunoPDB.py')
haddockformat = os.path.expanduser('~/software/HADDOCK-antibody-antigen/ab_haddock_format.py')
pdbtools = os.path.expanduser('~/software/pdb-tools/pdbtools')
haddocktools = os.path.expanduser('~/software/haddock-tools')

def comma_sep_caps(chains):
    if not re.match(r'^([A-Z]{1},)*[A-Z]{1}$', chains.upper()):
        raise argparse.ArgumentTypeError(f"Invalid format: {chains}. Expected comma-separated letters.")
    return chains.upper()

def verify_pdb(input):
    pdbtools = os.path.expanduser('~/software/pdb-tools/pdbtools')
    if len(input) != 4:
        raise argparse.ArgumentTypeError(f"Invalid PDB ID: '{input}'. The argument must be 4 characters long.")
    else:
        try:
            # Fetch PDB file
            tool = pdbtools + '/pdb_fetch.py '
            pdb_file = input.upper() + '.pdb'
            command = 'python ' + tool + input + ' > ' + pdb_file
            subprocess.run(command, shell=True)
            return input
        except:
            print(f"The file from PDB ID {input} could not be retrieved.")
            exit()

parser = argparse.ArgumentParser()
parser.add_argument('pdb_id', type=verify_pdb, help='Antibody-Antigen pdb_id in PDB format, either file or PDB ID.')
parser.add_argument('antigen_chain', type=comma_sep_caps, help='Chain or comma separated chains with the antigen in the pdb_id.')

args = parser.parse_args()
pdb_id = args.pdb_id
antigen_chain = args.antigen_chain

pdb_id = pdb_id.upper()
antigen_chain = antigen_chain.upper()

dir_list = [pdbtools, haddocktools]

# DIRECTORY VERIFICATION
def verify_dir(dir_list):
    for dir in dir_list:
        if os.path.isdir(dir) and os.access(dir, os.R_OK | os.W_OK | os.X_OK):
            pass
        else:
            print("Directory does not exist or not all permissions are granted.")
            exit()

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

work_dir = os.getcwd()
pdb_file = os.path.join(work_dir, pdb_id + '.pdb') 
# Renumber antibody structures according to Clothia system
fv_file = pdb_id + '-ch.pdb'
command = ['python', immunopdb, '-i', pdb_file, '-o', fv_file, '--scheme', 'c', '--fvonly', '--rename', '--splitscfv']
try_subprocess(command)

# Change antibody format to only have chain A 
fv_haddock_file = pdb_id + '-HADDOCK.pdb'
command2 = 'python ' + haddockformat + ' ' + fv_file + ' ' + fv_haddock_file + ' A'
subprocess.run(command2, shell=True)

# Select antigen chains from pdb_id file, rename to chain B and renumber residues
tool = pdbtools + '/pdb_selchain.py'
chains = ' -' + antigen_chain
rename = pdbtools + '/pdb_chain.py -B '
renumber = pdbtools + '/pdb_reres.py '
new_file = pdb_id + '_ligand.pdb'
command4 = 'python ' + tool + chains + ' ' + pdb_file + ' | ' + rename + ' | ' + renumber + ' > ' + new_file
subprocess.run(command4, shell=True)

# Merge antibody fv region and antigen in one file. 
tool = pdbtools + '/pdb_merge.py '
merge = pdb_id + '-merged.pdb'
command5 = 'python ' + tool + fv_haddock_file + ' ' + new_file + ' > ' + merge
subprocess.run(command5, shell=True)

# Run pdb_sort and keep only rows with ATOM
tool = pdbtools + '/pdb_sort.py '
sorted = pdb_id + '-sorted.pdb'
command6 = 'python ' + tool + merge + ' > ' + sorted
subprocess.run(command6, shell=True)
with open(sorted, 'r') as file:
    content = file.readlines()
atom_lines = [line for line in content if line.startswith('ATOM')]
with open(sorted, 'w') as file:
    file.writelines(atom_lines)

# Run pdb_tidy to add TER END
tool = pdbtools + '/pdb_tidy.py '
target = pdb_id + '-target.pdb'
command7 = 'python ' + tool + sorted + ' > ' + target
subprocess.run(command7, shell=True)

# Clean up directory
delete_file(pdb_id+'-ch.pdb')
delete_file(fv_haddock_file)
delete_file(merge)
delete_file(sorted)
    


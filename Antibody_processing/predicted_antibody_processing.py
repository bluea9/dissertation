import argparse, os, subprocess

# Tools
immunopdb = os.path.expanduser('~/software/ANARCI/Example_scripts_and_sequences/ImmunoPDB.py')
haddockformat = os.path.expanduser('~/software/HADDOCK-antibody-antigen/ab_haddock_format.py')
pdbtools = os.path.expanduser('~/software/pdb-tools/pdbtools')
haddocktools = os.path.expanduser('~/software/haddock-tools')

parser = argparse.ArgumentParser()
parser.add_argument('antibody_prediction', type=str, help='PDB file with the predicted antibody structure')
parser.add_argument('output_dir', type=str, help='Absolute path to directory to save epitope residues for docking')

args = parser.parse_args()
antibody_prediction = os.path.expanduser(args.antibody_prediction)
output_dir = os.path.expanduser(args.output_dir)

file_list = [antibody_prediction]
dir_list = [output_dir]

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

def remove_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print(f"The file {file} does not exist.")
    except PermissionError:
        print(f"Permission denied: Unable to delete {file}.")
    except Exception as error:
        print(f"An error occurred: {error}")

structure = os.path.splitext(os.path.basename(antibody_prediction))[0]

os.chdir(output_dir)
# Renumber antibody structures according to Clothia system
fv_file = structure + '-ch.pdb'
command = ['python', immunopdb, '-i', antibody_prediction, '-o', fv_file, '--scheme', 'c', '--fvonly', '--rename', '--splitscfv']
try_subprocess(command)

# Change antibody format to only have chain A and extract active residues
fv_haddock_file = structure + '-preHADDOCK.pdb'
command = 'python ' + haddockformat + ' ' + fv_file + ' ' + fv_haddock_file + ' A > antibody-active.txt'
subprocess.run(command, shell=True)
# Add TER and END
tidy = pdbtools + '/pdb_tidy.py '
file_name = structure + '-HADDOCK.pdb'
try: 
    command = tidy + fv_haddock_file + ' > ' + file_name
    subprocess.run(command, shell=True)
except:
    print(f'Antibody {structure} could not be processed.')

with open('antibody-active.txt', 'r') as file:
        residues = file.read()
residues = residues.replace(',',' ')
with open('antibody-active.list', 'w') as file:
    file.write(residues+'\n')
# Create tbl file with active residues using haddock-tools script 
command_unambig = haddocktools + '/restrain_bodies.py ' + file_name + ' > antibody-unambig.tbl'
subprocess.run(command_unambig, shell=True)
remove_file(fv_file)
remove_file(fv_haddock_file)
remove_file('antibody-active.txt')
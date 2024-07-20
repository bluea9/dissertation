import filepaths
import re, os, csv, subprocess, shutil

fv_dir = os.path.expanduser('/home/s2562233/Testing_antigens/Fv_files')
id_file = os.path.expanduser(filepaths.id_file)
parent_dir = os.path.expanduser('/home/s2562233/Docking_hvl')
new_dir = os.path.expanduser('/home/s2562233/Testing_antigens/For_ti')
runparam = os.path.expanduser(filepaths.run_param_file)
haddock_tools = os.path.expanduser(filepaths.haddock_tools_dir)

# FILE VERIFICATION
dir_list = [parent_dir, fv_dir, new_dir, haddock_tools]
file_list = [id_file, runparam]

def verify_file(file_list):
    for file in file_list:
        if os.path.isfile(file):
            continue
        else:
            print(f"The file '{file}' is not valid.")
            exit()

def verify_dir(dir_list):
    for dir in dir_list:
        if os.path.isdir(dir):
            continue
        else:
            print(f"The directory '{dir}' is not valid.")
            exit()

complex_list = []
with open(id_file, 'r') as txtfile:
    lines=txtfile.readlines()
    for line in lines:
        line_stripped = line.strip()
        complex_list.append(line_stripped)
        if ' ' in line_stripped:
            print('The file with IDs is not valid.')
            exit()

parameters_list = ['_pred_1m']

# FUNCIONS

# Function to create directory tree for each PDB complex ID
def create_dirtree(parent_dir, id, parameters_list):
    complex_dir = os.path.join(parent_dir, id + '_all')
    for leaf in parameters_list:
        leaf_dir = os.path.join(complex_dir, id + leaf)
        os.makedirs(leaf_dir, exist_ok=True)

# Function to copy files
def copy_file(original, copy):
    try:
        shutil.copy(original, copy)
    except FileNotFoundError:
        print(f"The file {original} was not found.")
        exit()
    except PermissionError:
        print(f"Permission denied. Unable to copy to destination: {copy}")
        exit()
    except Exception as error:
        print(f"An error occurred: {error}")
        exit()

# END OF FUNCTIONS

# Create directory tree
for id in complex_list:
    for id2 in complex_list:
        if id != id2:
            leaf_dir = os.path.join(new_dir, id + '_' + id2 + '_pred_1m')
            os.makedirs(leaf_dir, exist_ok=True)
            os.chdir(leaf_dir)
            #prev_dir = os.path.join(parent_dir, id + '_all')
            ab = os.path.join(fv_dir, id + '_fv_tidy.pdb')
            ab_cp = id + '_fv_tidy.pdb'
            copy_file(ab, ab_cp)
            ag = os.path.join(parent_dir, id2 + '_all', id2 + '_l_u.pdb')
            ag_cp = id2 + '_l_u.pdb'
            copy_file(ag, ag_cp)
            pred_list = os.path.join(parent_dir, id2 + '_all', 'prediction-active.list')
            copy_file(pred_list, 'prediction-active.list')
            ab_list = os.path.join(parent_dir, id + '_all', 'antibody-active.list')
            copy_file(ab_list, 'antibody-active.list')
            ab_unambig = os.path.join(parent_dir, id + '_all', 'antibody-unambig.tbl')
            copy_file(ab_unambig, 'antibody-unambig.tbl')
            command_pred = haddock_tools + '/active-passive-to-ambig.py antibody-active.list prediction-active.list > fv-pred-ambig.tbl'
            subprocess.run(command_pred, shell=True)
            
            # Modify run.param file and copy to each directory plus the ambig.tbl file
            with open(runparam, 'r') as file:
                param_file = file.read()
            param_cp = param_file
            param_cp = re.sub(r'PDB_FILE1=\S+', 'PDB_FILE1=' + id + '_fv_tidy.pdb', param_cp)
            param_cp = re.sub(r'PDB_FILE2=\S+', 'PDB_FILE2=' + id2 + '_l_u.pdb', param_cp)
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=fv-pred-ambig.tbl', param_cp)
            with open('run.param', 'w') as file:
                file.write(param_cp)
        else:
            pass
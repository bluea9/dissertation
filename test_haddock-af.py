import filepaths2
import re, os, csv, subprocess, shutil

# List with PDB complex, antibodies and antigens IDs
id_file = os.path.expanduser(filepaths2.id_file)

# Directory to store each of the docking runs
parent_dir = os.path.expanduser(filepaths2.parent_dir)

# Directory with AlphaFold structure predictions 
af_dir = os.path.expanduser(filepaths2.af_dir)
# Directory with HADDOCK-ready files
hready_dir = os.path.expanduser(filepaths2.haddock_ready_dir)
# Directory with file restraints from Haddock paper
restraints_dir = os.path.expanduser(filepaths2.restraints_dir)
# Directory with epitope predictions generated using Discotope3
discotope_dir = os.path.expanduser(filepaths2.discotope_dir)

# Tools
immunopdb = os.path.expanduser(filepaths2.immunopdb)
haddockformat = os.path.expanduser(filepaths2.haddockformat)
pdbtools = os.path.expanduser(filepaths2.pdbtools)
haddocktools = os.path.expanduser(filepaths2.haddock_tools_dir)

# run.param basefile
runparam = os.path.expanduser(filepaths2.run_param_file)

parameters_list = filepaths2.parameters_list

file_list = [id_file]
dir_list = [af_dir, parent_dir]

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

# Function to create directory tree for each PDB complex ID
def create_dirtree(parent_dir, id, parameters_list):
    complex_dir = os.path.join(parent_dir, id + '_all')
    for leaf in parameters_list:
        leaf_dir = os.path.join(complex_dir, id + leaf)
        os.makedirs(leaf_dir, exist_ok=True)

# Function to extract residues from antigen and antibody binding
def get_epitope(restraints):
    epitope = re.search(r'Epitope4.5\s+([\d,]+)', restraints)
    try:
        epitope = epitope.group(1).replace(',',' ')
        return epitope
    except:
        print('The epitope residues are not in the required format.')

# Function to extract residues from epitope prediction using Discotope3
def get_prediction(content):
    residues = []
    try:
        for row in content:
            if row['epitope'].strip().lower() == 'true':
                residues.append(row['res_id'])
        residues_str = str(residues).replace('[','').replace(']','').replace(',','').replace("'","")
        return residues_str
    except:
        print('The predicted epitope residues are not in the required format.')

def try_subprocess(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as error:
        print(f"An error occurred: {error.stderr.decode()}")
    except Exception as error:
        print(f"Unexpected error: {str(error)}")

# Obtain lists of PDB IDs from file
complex_list = []
ab_list = []
ag_list = []
with open(id_file, 'r') as file:
    content = csv.DictReader(file)
    for row in content:
        complex_list.append(row['COMPLEX'])
        ab_list.append(row['ANTIBODY'])
        ag_list.append(row['ANTIGEN'])

for id1, id2 in zip(complex_list, ab_list):
    top_structure = os.path.join(af_dir, id2.lower() + '_fv', 'ranked_0.pdb')
    os.makedirs(os.path.join(parent_dir, id1 + '_all'))
    cp_structure = os.path.join(parent_dir, id1 + '_all', id2 + '-fv-r0.pdb')
    copy_file(top_structure, cp_structure)

# Renumber antibody structures according to Clothia system
for id, id2 in zip(ab_list, complex_list):
    complex_dir = os.path.join(parent_dir, id2 + '_all')
    os.chdir(complex_dir)
    structure = id + '-fv-r0.pdb'
    new_file = id + '-fv-r0-ch.pdb'
    #command = 'python ' + immunopdb + ' -i ' + structure + ' -o ' + new_file + ' --scheme c --fvonly --rename --splitscfv'
    #subprocess.run(command, shell=True)
    command = ['python', immunopdb, '-i', structure, '-o', new_file, '--scheme', 'c', '--fvonly', '--rename', '--splitscfv']
    try_subprocess(command)

# Format the antibody according to HADDOCK requirements and extract the HV loop residues
for id, id2 in zip(ab_list, complex_list):
    complex_dir = os.path.join(parent_dir, id2 + '_all')
    os.chdir(complex_dir)
    command = 'python ' + haddockformat + ' ' + id + '-fv-r0-ch.pdb ' + id + '-fv-r0-HADDOCK.pdb A > antibody-active.txt'
    subprocess.run(command, shell=True)
    command2 = pdbtools + '/pdb_tidy.py ' + id + '-fv-r0-HADDOCK.pdb > ' + id + '-fv-r0-tidy.pdb'
    subprocess.run(command2, shell=True)
    with open('antibody-active.txt', 'r') as file:
        residues = file.read()
    residues = residues.replace(',',' ')
    with open('antibody-active.list', 'w') as file:
        file.write(residues+'\n')
    # Create tbl file with active residues using haddock-tools script 
    command_unambig = haddocktools + '/restrain_bodies.py ' + id + '-fv-r0-tidy.pdb > antibody-unambig.tbl'
    subprocess.run(command_unambig, shell=True)


# Create directory tree
for id in complex_list:
    create_dirtree(parent_dir, id, parameters_list)

# Copy antigen PDB file and restraints for docking
for id in complex_list:
    ready_dir = os.path.join(hready_dir, id)
    complex_dir = os.path.join(parent_dir, id+'_all')
    try:
        os.chdir(complex_dir)
        ag = os.path.join(ready_dir, id + '_l_u.pdb')
        ag_cp = id + '_l_u.pdb'
        restraints_file = os.path.join(restraints_dir, id + '-restr.txt')
        restraints_cp = id + '-restr.txt'
        copy_file(ag, ag_cp)
        copy_file(restraints_file, restraints_cp)
    except:
        print(f"The directories for each complex do not exist.")
        exit()

# Create files with restraints for docking with Haddock2.5
for id in complex_list:
    complex_dir = os.path.join(parent_dir, id+'_all')
    os.chdir(complex_dir)
    # Restraints from Haddock-ready repository
    filename = id + '-restr.txt'
    with open(filename, 'r') as file:
        restraints = file.read()
    epitope_residues = get_epitope(restraints)
    with open('epitope-active.list', 'w') as file:
        file.write(epitope_residues+'\n\n')

    # Predicted epitopes using Dicotope3 server
    filename2 = os.path.join(discotope_dir, id + '_l_u_B_discotope3.csv')
    with open(filename2, 'r') as file:
        content = csv.DictReader(file)
        predicted_epi_residues = get_prediction(content)
    with open('prediction-active.list', 'w') as file:
        file.write(predicted_epi_residues+'\n\n')

    # Create tbl files from restraints files using haddock-tools scripts 
    command_epi = haddocktools + '/active-passive-to-ambig.py antibody-active.list epitope-active.list > complex-epi-ambig.tbl'
    subprocess.run(command_epi, shell=True)
    command_pred = haddocktools + '/active-passive-to-ambig.py antibody-active.list prediction-active.list > complex-pred-ambig.tbl'
    subprocess.run(command_pred, shell=True)

# Copy files to directories for docking
for id, ab in zip(complex_list, ab_list):
    complex_dir = os.path.join(parent_dir, id+'_all')
    os.chdir(complex_dir)
    pdb1 = ab + '-fv-r0-tidy.pdb'
    pdb2 = id + '_l_u.pdb'
    for leaf in parameters_list:
        pdb1_cp = os.path.join(complex_dir, id + leaf, pdb1)
        copy_file(pdb1, pdb1_cp)
        pdb2_cp = os.path.join(complex_dir, id + leaf, pdb2)
        copy_file(pdb2, pdb2_cp)
        ab_unambig = 'antibody-unambig.tbl'
        ab_unambig_cp = os.path.join(complex_dir, id + leaf, ab_unambig)
        copy_file(ab_unambig, ab_unambig_cp)

        # Modify run.param file and copy to each directory plus the ambig.tbl file
        with open(runparam, 'r') as file:
            param_file = file.read()
        param_cp = param_file
        param_cp = re.sub(r'PDB_FILE1=\S+', 'PDB_FILE1=' + pdb1, param_cp)
        param_cp = re.sub(r'PDB_FILE2=\S+', 'PDB_FILE2=' + pdb2, param_cp)
        
        if re.search(r'epi', leaf):
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=complex-epi-ambig.tbl', param_cp)
            ambig_file = os.path.join(complex_dir, 'complex-epi-ambig.tbl')
            ambig_file_cp = os.path.join(complex_dir, id + leaf, 'complex-epi-ambig.tbl')
        elif re.search(r'pred', leaf):
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=complex-pred-ambig.tbl', param_cp)
            ambig_file = os.path.join(complex_dir, 'complex-pred-ambig.tbl')
            ambig_file_cp = os.path.join(complex_dir, id + leaf, 'complex-pred-ambig.tbl')

        copy_file(ambig_file, ambig_file_cp)
        param_filepath = os.path.join(complex_dir, id + leaf, 'run.param')
        with open(param_filepath, 'w') as file:
            file.write(param_cp)


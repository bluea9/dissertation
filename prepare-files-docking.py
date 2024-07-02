import filepaths
import re, os, subprocess, shutil

parameters_list = ['_epi_1m', '_epi_5m', '_surf_1m', '_surf_5m', '_pred_1m', '_pred_5m']

# Path to file with antibody-antigen complexes PDB IDs
id_file = os.path.expanduser(filepaths.id_file)

# Path to directory with file restraints from Haddock paper
restraints_dir = os.path.expanduser(filepaths.restraints_dir)

# Path to directory with HADDOCK-ready files
hready_dir = os.path.expanduser(filepaths.haddock_ready_dir)

# Directory for HADDOCK replication study files
parent_dir = os.path.expanduser(filepaths.parent_dir)

# haddok-tools directory
haddock_tools = os.path.expanduser(filepaths.haddock_tools_dir)

# run.param basefile
runparam = os.path.expanduser(filepaths.run_param_file)

try:
    os.chdir(parent_dir)
except:
    print(f"The directory '{parent_dir}' does not exists.")
    exit()

complex_list = []
try:
    with open(id_file, 'r') as txtfile:
        lines=txtfile.readlines()
        complex_list = [line.strip() for line in lines]
except:
    print(f"The file '{id_file}' does not exist.")
    exit()

if os.path.isdir(haddock_tools):
    pass
else:
    print(f"The directory '{haddock_tools}' does not exists.")
    exit()

try:
    with open(runparam, 'r') as file:
        param_file = file.read()
except:
    print(f"The file '{runparam}' does not exist.")
    exit()

# Function to create directory tree for each PDB complex ID
def create_dirtree(parent_dir, id, parameters_list):
    complex_dir = os.path.join(parent_dir, id+'_all')
    for leaf in parameters_list:
        leaf_dir = os.path.join(complex_dir, id + leaf)
        os.makedirs(leaf_dir, exist_ok=True)

# Functions to extract residues from antigen and antibody binding
def get_epitope(restraints):
    epitope = re.search(r'Epitope4.5\s+([\d,]+)', restraints)
    try:
        epitope = epitope.group(1).replace(',',' ')
        return epitope
    except:
        print('The epitope residues are not in the file.')

def get_surface(restraints):
    surface = re.search(r'Antigen-Surf\s+([\d,]+)', restraints)
    try:
        surface = surface.group(1).replace(',',' ')
        return surface
    except:
        print('The antigen surface residues are not in the file.')

def get_paratope(restraints):
    paratope = re.search(r'Paratope\s+([\d,]+)', restraints)
    hv = re.search(r'HV-loops\s+([\d,]+)', restraints)
    try:
        paratope = paratope.group(1)
        hv = hv.group(1)
        paratope_list = [int(res) for res in paratope.split(',')]
        hv_list = [int(res) for res in hv.split(',')]
        antibody_list = paratope_list + hv_list
        antibody_list = sorted(list(set(antibody_list)))
        antibody_str = str(antibody_list).replace('[','').replace(']','').replace(',','')
        return antibody_str
    except:
        print('The paratope residues are not in the file.')


for id in complex_list:
    create_dirtree(parent_dir, id, parameters_list)

for id in complex_list:
    ready_dir = os.path.join(hready_dir, id)
    complex_dir = os.path.join(parent_dir, id+'_all')
    try:
        os.chdir(complex_dir)
        ab = ready_dir + '/' + id + '_r_u.pdb'
        ab_cp = id + '_r_u.pdb'
        ag = ready_dir + '/' + id + '_l_u.pdb'
        ag_cp = id + '_l_u.pdb'
        restraints_file = restraints_dir + id + '-restr.txt' 
        restraints_cp = id + '-restr.txt'
        shutil.copy(ab, ab_cp)
        shutil.copy(ag, ag_cp)
        shutil.copy(restraints_file, restraints_cp)
    except:
        print(f"The directories for each complex do not exist.")
        exit()

# Create files with restraints for docking with Haddock2.5
for id in complex_list:
    complex_dir = os.path.join(parent_dir, id+'_all')
    os.chdir(complex_dir)
    filename = id + '-restr.txt'
    with open(filename, 'r') as file:
        restraints = file.read()
    epitope_residues = get_epitope(restraints)
    surface_residues = get_surface(restraints)
    antibody_residues = get_paratope(restraints)

    with open('epitope-active.list', 'w') as file:
        file.write(epitope_residues+'\n\n')

    with open('surface-passive.list', 'w') as file:
        file.write('\n'+surface_residues+'\n')

    with open('antibody-active.list', 'w') as file:
        file.write(antibody_residues+'\n\n')
    
    # Create tbl files from restraints files using haddock-tools scripts 
    command = 'python3 ' + haddock_tools + '/restrain_bodies.py ' + id + '_r_u.pdb > antibody-unambig.tbl'
    subprocess.run(command, shell=True)
    command_surf = haddock_tools + '/active-passive-to-ambig.py antibody-active.list surface-passive.list > complex-surf-ambig.tbl'
    subprocess.run(command_surf, shell=True)
    command_epi = haddock_tools + '/active-passive-to-ambig.py antibody-active.list epitope-active.list > complex-epi-ambig.tbl'
    subprocess.run(command_epi, shell=True)

# Copy files to directories for docking
for id in complex_list:
    complex_dir = os.path.join(parent_dir, id+'_all')
    os.chdir(complex_dir)
    pdb1 = id + '_r_u.pdb'
    pdb2 = id + '_l_u.pdb'
    for leaf in parameters_list:
        pdb1_cp = os.path.join(complex_dir, id + leaf, pdb1)
        shutil.copyfile(pdb1, pdb1_cp)
        pdb2_cp = os.path.join(complex_dir, id + leaf, pdb2)
        shutil.copyfile(pdb2, pdb2_cp)
        ab_unambig = 'antibody-unambig.tbl'
        ab_unambig_cp = os.path.join(complex_dir, id + leaf, ab_unambig)
        shutil.copyfile(ab_unambig, ab_unambig_cp)

        # Modify run.param file and copy to each directory plus the ambig.tbl file
        param_cp = param_file
        param_cp = re.sub(r'PDB_FILE1=\S+', 'PDB_FILE1=' + pdb1, param_cp)
        param_cp = re.sub(r'PDB_FILE2=\S+', 'PDB_FILE2=' + pdb2, param_cp)
        
        if re.search(r'epi', leaf):
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=complex-epi-ambig.tbl', param_cp)
            ambig_file = os.path.join(complex_dir, 'complex-epi-ambig.tbl')
            ambig_file_cp = os.path.join(complex_dir, id + leaf, 'complex-epi-ambig.tbl')
        elif re.search(r'surf', leaf):
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=complex-surf-ambig.tbl', param_cp)
            ambig_file = os.path.join(complex_dir, 'complex-surf-ambig.tbl')
            ambig_file_cp = os.path.join(complex_dir, id + leaf, 'complex-surf-ambig.tbl')
        elif re.search(r'pred', leaf):
            param_cp = re.sub(r'^AMBIG_TBL=\S+', 'AMBIG_TBL=complex-pred-ambig.tbl', param_cp)
         #   ambig_file = os.path.join(complex_dir, 'complex-pred-ambig.tbl')
         #   ambig_file_cp = os.path.join(complex_dir, id + leaf, 'complex-pred-ambig.tbl')

        try:
            shutil.copyfile(ambig_file, ambig_file_cp)
        except:
            pass
        param_filepath = os.path.join(complex_dir, id + leaf, 'run.param')
        with open(param_filepath, 'w') as file:
            file.write(param_cp)
        
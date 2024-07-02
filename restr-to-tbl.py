import filepaths
import re, os, subprocess

# Directory for HADDOCK replication study files and list with PDB complex IDs
parent_dir = os.path.expanduser(filepaths.parent_dir)
id_file = os.path.expanduser(filepaths.id_file)
haddock_tools = os.path.expanduser(filepaths.haddock_tools_dir)

# verify paths and files
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
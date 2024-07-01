import re

def get_epitope(restraints_file):
    with open(restraints_file, 'r') as file:
        restraints = file.read()
    epitope = re.search(r'Epitope4.5\s+([\d,]+)', restraints)
    try:
        epitope = epitope.group(1)
        epitope = epitope.replace(',',' ')
        return epitope
    except:
        print('The epitope residues are not in the file.')

def get_surface(restraints_file):
    with open(restraints_file, 'r') as file:
        restraints = file.read()
    surface = re.search(r'Antigen-Surf\s+([\d,]+)', restraints)
    try:
        surface = surface.group(1)
        surface = surface.replace(',',' ')
        return surface
    except:
        print('The antigen surface residues are not in the file.')

def get_paratope(restraints_file):
    with open(restraints_file, 'r') as file:
        restraints = file.read()
    paratope = re.search(r'Paratope\s+([\d,]+)', restraints)
    hv = re.search(r'HV-loops\s+([\d,]+)', restraints)
    try:
        paratopef = paratope.group(1)
        hv = hv.group(1)
        paratope_list = [int(res) for res in paratopef.split(',')]
        hv_list = [int(res) for res in hv.split(',')]
        antibody_list = paratope_list + hv_list
        antibody_list = sorted(list(set(antibody_list)))
        antibody_str = str(antibody_list).replace('[','').replace(']','').replace(',','')
        return antibody_str
    except:
        print('The paratope residues are not in the file.')

# Providing filepath
filename = '2VXT-restr.txt'

epitope_residues = get_epitope(filename)
surface_residues = get_surface(filename)
antibody_residues = get_paratope(filename)
print("Residues epitope:", epitope_residues)
print("Residues surface antigen:", surface_residues)
print("Residues CDR and paratope:", antibody_residues)
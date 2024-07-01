import re

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

# Providing filepath
filename = '2VXT-restr.txt'
with open(filename, 'r') as file:
        restraints = file.read()

epitope_residues = get_epitope(restraints)
surface_residues = get_surface(restraints)
antibody_residues = get_paratope(restraints)
print("Residues epitope:", epitope_residues)
print("Residues surface antigen:", surface_residues)
print("Residues CDR and paratope:", antibody_residues)
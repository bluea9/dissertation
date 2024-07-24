import argparse, os
from Bio import PDB

parser = argparse.ArgumentParser()
parser.add_argument('complex', type=str, help='PDB file with the antibody(Fv region)-antigen complex structure')
parser.add_argument('output_dir', type=str, help='Absolute path to directory to save antibody and antigen active residues')

args = parser.parse_args()
complex_file = os.path.expanduser(args.complex)
output_dir = os.path.expanduser(args.output_dir)

parser = PDB.PDBParser(QUIET=True)
complex = parser.get_structure('complex', complex_file)
model = complex[0]
antibody = model['A']
antigen = model['B']

# Distance cutoff for interface residues in Ångströms
distance_cutoff = 4.5

# NeighborSearch object
atoms = list(antibody.get_atoms()) + list(antigen.get_atoms())
nsearch = PDB.NeighborSearch(atoms)

interface = set()
for atom in antibody.get_atoms():
    # Find all atoms in the antigen within the cutoff distance from each atom in the antibody
    neighbors = nsearch.search(atom.coord, distance_cutoff, level='R')
    for residue in neighbors:
        if residue.get_parent() == antigen:
            interface.add((atom.get_parent(), residue))

antibody_active = []
antigen_active = []
for res_ab, res_ag in interface:
    antibody_active.append(res_ab.get_id()[1])
    antigen_active.append(res_ag.get_id()[1])

ab_res_list = sorted(list(set(antibody_active)))
ag_res_list = sorted(list(set(antigen_active)))
ab_res = str(ab_res_list)
ab_res = ab_res.replace('[','').replace(']','').replace(',','')
ag_res = str(ag_res_list)
ag_res = ag_res.replace('[','').replace(']','').replace(',','')

os.chdir(output_dir)
with open('ab-interface-res.txt', 'w') as file:
    file.write(ab_res + '\n\n')

with open('ag-interface-res.txt', 'w') as file:
    file.write(ag_res + '\n\n')

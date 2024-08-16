from pyrosetta import *
from pyrosetta.toolbox import *
init()
import os, re
import pandas as pd

ia = pyrosetta.rosetta.protocols.analysis.InterfaceAnalyzerMover()

ab_list = ['HM1', 'HM2', 'HM3', 'HM4', 'HM5', 'HM6', 'HM7', 'HM8', 'HM9', 'HM10', 'HM11']
ag_list = ['1GK4', '1MIF', '4PCW', '3B97', '3GHG_A', '3GHG_B', '3GHG_C', '7E8D', '7E8D_A', '7E8D_B', '7E8D_D']
parent_dir = '/home/MSC/Docking_RA'


def get_haddock_scores(rank_file):
    '''
    Retrieve the file names and Haddock scores from a file.list after water refinement
    '''
    filenames = []
    haddock_scores = []
    try:
        with open(rank_file, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if index >= 100:
                    break
                # Use a regular expression to extract the filename and Haddock score
                structure = re.search(r'PREVIT:(\S+)"\s+{\s(\S+)\s}', line)
                if structure:
                    filename = structure.group(1)
                    score = float(structure.group(2))
                    filenames.append(filename)
                    haddock_scores.append(float(score))
            return filenames, haddock_scores
    except:
        print(f'An error occurred when parsing {rank_file}.')
        exit()

df_names = pd.DataFrame()
df_scores = pd.DataFrame()
col_names = ['Complex', 'Interface_dG', 'Interface_delta_SASA', 'Complex_energy', 'Separated_interface_energy', 'Complexed_SASA', 'Crossterm_interface_energy']
df_energy = pd.DataFrame(columns=col_names)
for ab in ab_list:
    for ag in ag_list:
        leaf_dir = os.path.join(parent_dir, ab + '_all', ab + '_' + ag)
        rank_file = os.path.join(leaf_dir, 'run1/structures/it1/water/file.list')
        if os.path.exists(rank_file):
            filenames, haddock_scores = get_haddock_scores(rank_file)
            structures_dir = os.path.join(leaf_dir, 'run1/structures/it1/water')
            for top_n in range(0, 100):
                scores = []
                pdb_file = os.path.join(leaf_dir, 'run1/structures/it1/water', filenames[top_n])
                complex_name = os.path.basename(pdb_file)
                complex_name = ab + '_' + ag + '_' + str(top_n)
                print(f'Processing {complex_name} structure...')
                pose = pose_from_pdb(pdb_file)
                ia.apply(pose)
                scores = [complex_name, ia.get_interface_dG(), ia.get_interface_delta_sasa(), ia.get_complex_energy(), ia.get_separated_interface_energy(), ia.get_complexed_sasa(), ia.get_crossterm_interface_energy()]
                df_energy.loc[len(df_energy)] = scores
        else:
            continue
        col_name = ab + '_' + ag
        df_names[col_name] = filenames
        df_scores[col_name] = haddock_scores

df_energy.to_csv('/home/MSC/Results/Top100/top_energy_scores_ra.csv', index=False)
df_names.to_csv('/home/MSC/Results/Top100/top_file_names_ra.csv', index=False)
df_scores.to_csv('/home/MSC/Results/Top100/top_scores_ra.csv', index=False)
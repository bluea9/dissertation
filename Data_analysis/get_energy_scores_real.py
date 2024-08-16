from pyrosetta import *
from pyrosetta.toolbox import *
init()
import os, re
import pandas as pd

ia = pyrosetta.rosetta.protocols.analysis.InterfaceAnalyzerMover()

complex_list = ['2VXT','3EO1','3G6D','3HI6','3MXW']
parent_dir = '/home/MSC/Docking_scenarios'

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

count = 0
df_names = pd.DataFrame()
df_scores = pd.DataFrame()
col_names = ['Complex', 'Interface_dG', 'Interface_delta_SASA', 'Complex_energy', 'Separated_interface_energy', 'Complexed_SASA', 'Crossterm_interface_energy']
df_energy = pd.DataFrame(columns=col_names)
for id in complex_list:
    count += 1
    leaf_dir = os.path.join(parent_dir, id + '_real')
    rank_file = os.path.join(leaf_dir, 'run1/structures/it1/water/file.list')
    filenames, haddock_scores = get_haddock_scores(rank_file)
    structures_dir = os.path.join(leaf_dir, 'run1/structures/it1/water')
    for top_n in range(0, 100):
        scores = []
        pdb_file = os.path.join(leaf_dir, 'run1/structures/it1/water', filenames[top_n])
        complex_name = id + '_' + str(top_n)
        print(f'Processing {complex_name} structure...')
        pose = pose_from_pdb(pdb_file)
        ia.apply(pose)
        scores = [complex_name, ia.get_interface_dG(), ia.get_interface_delta_sasa(), ia.get_complex_energy(), ia.get_separated_interface_energy(), ia.get_complexed_sasa(), ia.get_crossterm_interface_energy()]
        df_energy.loc[len(df_energy)] = scores
    col_name = id
    df_names[col_name] = filenames
    df_scores[col_name] = haddock_scores

df_energy.to_csv('/home/MSC/Results/Top100/top_energy_scores_real.csv', index=False)
df_names.to_csv('/home/MSC/Results/Top100/top_file_names_real.csv', index=False)
df_scores.to_csv('/home/MSC/Results/Top100/top_scores_real.csv', index=False)


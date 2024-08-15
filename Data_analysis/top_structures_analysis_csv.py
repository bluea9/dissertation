import argparse, os, re, subprocess
import pandas as pd

"""
Script that takes the Top 100 predicted docked structures using Haddock and evaluates them against 
a target file using DockQ. 
Note1: Results stored in working directory.
Note2: Requires conda environment dockq_env
"""

# Tools
dock = '~/software/DockQ/src/DockQ/DockQ.py'
dock = os.path.expanduser(dock)

parser = argparse.ArgumentParser()
parser.add_argument('docking_directory', type=str, help='Directory with docking results after running Haddok2.5 with water refinement.')
parser.add_argument('target_file', type=str, help='File with true antibody(Fv region)-antigen complex to evaluate predicted complexes.')

args = parser.parse_args()
docking_dir = os.path.expanduser(args.docking_directory)
target = os.path.expanduser(args.target_file)

file_list = [dock, target]
dir_list = [docking_dir]

# FILE AND DIRECTORY VERIFICATION
def verify_file(file_list):
    for file in file_list:
        if os.path.isfile(file):
            pass
        else:
            print(f"File {file} does not exist.")
            exit()

def verify_dir(dir_list):
    for dir in dir_list:
        if os.path.isdir(dir) and os.access(dir, os.R_OK | os.W_OK | os.X_OK):
            pass
        else:
            print("Directory does not exist or not all permissions are granted.")
            exit()

# FUNCTION TO CREATE DIRECTORY
def make_dir(path):
    path = os.path.expanduser(path)
    try:
        os.makedirs(path)
    except FileExistsError:
        print(f"Directory '{path}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create {path}.")
    except Exception as error:
        print(f"An error occurred: {error}")

verify_file(file_list)
verify_dir(dir_list)

# Get current directory to store results
work_dir = os.getcwd()
os.chdir(work_dir)
# Get file with ranking of predicted structures
rank_file = os.path.join(docking_dir, 'run1/structures/it1/water/file.list' )
complex = os.path.basename(os.path.normpath(docking_dir))

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
                haddock_scores.append(score)
except:
    print(f'An error occurred when parsing {rank_file}.')

# Lists to store metric scores
dockq = []
irms = []
lrms = []
fnat = []
fnonnat = []
clashes = []
f1 = []
dockq_f1 = []
quality = []

for file in filenames:
    structure_file = os.path.join(docking_dir, 'run1/structures/it1/water', file)
    command = 'DockQ ' + structure_file + ' ' + target + ' --short --allowed_mismatches 10'
    # Run DockQ to generate metrics for each predicted structure  (from previous line --allowed_mismatches 10)
    scores_dq = subprocess.run(command, shell=True, capture_output=True, text=True)
    scores_dq = scores_dq.stdout
    # Store each metric
    dockq_search = re.search(r'DockQ\s([0,1]\S+)\s', scores_dq)
    dockq.append(float(dockq_search.group(1)))
    
    irms_search = re.search(r'irms\s(\S+)\s', scores_dq)
    irms.append(float(irms_search.group(1)))
    
    lrms_search = re.search(r'Lrms\s(\S+)\s', scores_dq)
    lrms.append(float(lrms_search.group(1)))
    
    fnat_search = re.search(r'fnat\s(\S+)\s', scores_dq)
    fnat.append(float(fnat_search.group(1)))

    fnonnat_search = re.search(r'fnonnat\s(\S+)\s', scores_dq)
    fnonnat.append(float(fnonnat_search.group(1)))
    
    clashes_search = re.search(r'clashes\s(\S+)\s', scores_dq)
    clashes.append(float(clashes_search.group(1)))

    f1_search = re.search(r'F1\s(\S+)\s', scores_dq)
    f1.append(f1_search.group(1))
    
    dockq_f1_search = re.search(r'DockQ_F1\s(\S+)\s', scores_dq)
    dockq_f1.append(float(dockq_f1_search.group(1)))

    # Assign quality category depending on DockQ score
    value = float(dockq_search.group(1))
    if value <  0.23:
        quality.append('Incorrect')
    elif value >= 0.23 and value < 0.49:
        quality.append('Acceptable')
    elif value >= 0.49 and value < 0.80:
        quality.append('Medium')
    elif value >= 0.80:
        quality.append('High')
        
lists_scores = [filenames, haddock_scores, dockq, irms, lrms, fnat, fnonnat, clashes, f1, dockq_f1, quality]
# Convert lists with scores to series
for list in lists_scores:
    list = pd.Series(list) 

# Create DataFrame from the Series
df = pd.DataFrame({'Structure_file' : filenames, 'Haddock_score' : haddock_scores, 'DockQ' : dockq, 'Quality' : quality, 'iRMS' : irms, 'lRMS' : lrms, 'Fnat' : fnat, 'Fnonnat' : fnonnat, 'Clashes' : clashes, 'F1' : f1, 'DockQ_F1' : dockq_f1})

df.to_csv(complex+'_metrics.csv', index=False)
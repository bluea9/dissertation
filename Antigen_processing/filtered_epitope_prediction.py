import argparse, os, csv, subprocess
from operator import itemgetter

parser = argparse.ArgumentParser()
parser.add_argument('antigen_list', type=str, help='csv file with antigens PDB ID list')
parser.add_argument('predictions_dir', type=str, help='Absolute path to directory with Discotope3 epitope predictions')
parser.add_argument('output_dir', type=str, help='Absolute path to directory to save epitope residues for docking')

args = parser.parse_args()
antigen_file = os.path.expanduser(args.antigen_list)
predictions_dir = os.path.expanduser(args.predictions_dir)
output_dir = os.path.expanduser(args.output_dir)

file_list = [antigen_file]
dir_list = [predictions_dir, output_dir]

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

# Function to get the values on a column from a csv file
def get_column_values(file, col_index):
    values = []
    with open(file, newline='') as csvfile:
        content = csv.reader(csvfile)
        for row in content:
            values.append(row[col_index])
    return values

# Get list of antigen PDB IDs
antigen_list = get_column_values(antigen_file,0)
antigen_list = [antigen.upper() for antigen in antigen_list]

def get_prediction(content):
    residues = []
    try:
        for row in content:
            if row['epitope'].strip().lower() == 'true':
                residues.append(row['res_id'])
        residues_str = str(residues).replace('[','').replace(']','').replace(',','').replace("'","")
        if len(residues) < 15 or len(residues) > 25:
            print('Top 20 residues will be taken')
            residues = []
            for row1 in content:
                row1['calibrated_score'] = float(row1['calibrated_score'])
            sorted_content = sorted(content, key=itemgetter('calibrated_score'), reverse=True)
            top_20 = sorted_content[:20]
            print(top_20)
            for row2 in top_20:
                print('top20 row')
                print(row2)
                residues.append(int(row2['res_id']))
            residues = sorted(residues)
            residues_str = str(residues).replace('[','').replace(']','').replace(',','').replace("'","")
        return residues_str
    except:
        print('The predicted epitope residues are not in the file.')

os.chdir(predictions_dir)
for id in antigen_list:
    filename = id + '-ag_B_discotope3.csv'
    try: 
        with open(filename, 'r') as file:
            content = csv.DictReader(file)
            predicted_epi_residues = get_prediction(content)
            prediction_file = os.path.join(output_dir, id + '_pred-active.list')
    except:
        print(f'An error occurred when trying to parse the file {filename}')
    with open(prediction_file, 'w') as newfile:
        newfile.write(predicted_epi_residues+'\n\n')
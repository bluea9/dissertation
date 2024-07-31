import filepaths
import csv, os

# Directory with epitopes predicted using Discotope3 and list with PDB complex IDs
disco_dir = os.path.expanduser(filepaths.discotope_dir)
id_file = os.path.expanduser(filepaths.id_file)

# Verify paths and files
try:
    os.chdir(disco_dir)
    results_dir = os.path.join(disco_dir, 'Prediction_lists')
    os.makedirs(results_dir, exist_ok=True)
except FileNotFoundError:
    print(f"The directory '{disco_dir}' does not exist.")
    exit()
except Exception as error:
    print(f"An error occurred: {error}")
    exit()

complex_list = []
try:
    with open(id_file, 'r') as txtfile:
        lines=txtfile.readlines()
        complex_list = [line.strip() for line in lines]
except FileNotFoundError:
    print(f"The file '{id_file}' does not exist.")
    exit()
except Exception as error:
    print(f"An error occurred: {error}")
    exit()

def get_prediction(content):
    residues = []
    try:
        for row in content:
            if row['epitope'].strip().lower() == 'true':
                residues.append(row['res_id'])
        residues_str = str(residues).replace('[','').replace(']','').replace(',','').replace("'","")
        return residues_str
    except:
        print('The predicted epitope residues are not in the file.')

for id in complex_list:
    filename = id + '_l_u_B_discotope3.csv'
    with open(filename, 'r') as file:
        content = csv.DictReader(file)
        predicted_epi_residues = get_prediction(content)
        prediction_file = os.path.join(results_dir, id + '_pred-active.list')
    with open(prediction_file, 'w') as newfile:
        newfile.write(predicted_epi_residues+'\n\n')
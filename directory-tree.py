import argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('parentdir', help='Parent directory')
parser.add_argument('idfile', help='File with antibody-antigen complex PDB IDs')
args = parser.parse_args()
parent_dir = args.parentdir
id_file = args.idfile
parent_dir = os.path.expanduser(parent_dir)
id_file = os.path.expanduser(id_file)

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

def create_dirtree(parent_dir, id):
    complex_dir = os.path.join(parent_dir, id+'_all')
    os.makedirs(complex_dir+'/surface/'+id+'_surf_1m')
    os.makedirs(complex_dir+'/surface/'+id+'_surf_5m')
    os.makedirs(complex_dir+'/epitope/'+id+'_epi_1m')
    os.makedirs(complex_dir+'/epitope/'+id+'_epi_5m')
    os.makedirs(complex_dir+'/prediction/'+id+'_pred_1m')
    os.makedirs(complex_dir+'/prediction/'+id+'_pred_5m')

for id in complex_list:
    create_dirtree(parent_dir, id)
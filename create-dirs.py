import os

# Path to parent directory
parent_dir = '~/Reduced_rep'
parent_dir = os.path.expanduser(parent_dir)

# Path to file with antibody-antigen complexes PDB IDs
#file = '~/reduced_set/complex_list.txt'
file = '~/reduced_set/complex_list_short.txt'
file = os.path.expanduser(file)

complex_list = []
try:
    with open(file, 'r') as txtfile:
        lines=txtfile.readlines()
        complex_list = [line.strip() for line in lines]
except:
    print(f"The file '{file}' does not exist.")
    exit()

try:
    os.chdir(parent_dir)
except:
    print(f"The directory '{parent_dir}' does not exists.")
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
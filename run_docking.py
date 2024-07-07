import argparse, os, subprocess, re

# Path to run_haddock.py script from Haddock installation
haddock = '~/HADDOCK/haddock2.5-2024-03/haddock/run_haddock.py'
haddock = os.path.expanduser(haddock)
if os.path.isfile(haddock):
    pass
else:
    print(f"The file '{haddock}' is not valid.")
    exit()

parser = argparse.ArgumentParser()
parser.add_argument('docking_directory', type=str, help='Directory with files ready for docking with Haddock2.5')
parser.add_argument('exclude', type=str, choices=['y', 'n'], help='Randomly exclude a fraction of the ambiguous restraints (AIRs)')
parser.add_argument('-m', '-models', type=int, nargs=3, default=[1000, 400, 400], help='Number of structures to dock: Structures for rigid body docking, structures for refinemen, structures to be analysed')
parser.add_argument('-w', '-waterdock', type=int, help='Number of structures for the solvated docking refinement')

args = parser.parse_args()
docking_dir = args.docking_directory
exclude = args.exclude
models = args.m
water = args.w

docking_dir = os.path.expanduser(docking_dir)
if os.path.isdir(docking_dir):
    pass
else:
    print(f"The directory '{docking_dir}' is not valid.")
    exit()

# Function to ensure that the number of refined and analyzed structures is smaller than the total number of models
def verify_number_models(models, water):
    if any(num <= 0 for num in models):
        print("The number of models must be a positive integer.")
        exit()
    elif models[1] > models[0]:
        print("The number of refined structures must be smaller than the number of structures for rigid body docking.")
        exit()
    elif models[2] > models[1]:
        print("The number of analyzed models must be equal or smaller than the number of refined structures.")
        exit()
    elif water is not None:
        if water > models[0]:
            print("The number of water refined structures must be smaller than the number of structures for rigid body docking.")
            exit()
    return

verify_number_models(models, water)

# START DOCKING

# FIRST STEP -> Create run1 directory
os.chdir(docking_dir)
command = 'python ' + haddock
subprocess.run(command, shell=True)

# SECOND STEP -> cd into run1 and modify run.cns file according to experiment using argparse arguments
os.chdir(docking_dir + '/run1')

with open('run.cns', 'r') as file:
    cns_file = file.read()
if exclude == 'n':
    cns_file = re.sub('noecv=true', 'noecv=false', cns_file)
if water is not None:
    cns_file = re.sub('waterdock=false', 'waterdock=true', cns_file)
    cns_file = re.sub('waterrefine=200', 'waterrefine=' + str(water), cns_file)
cns_file = re.sub('structures_0=1000', 'structures_0=' + str(models[0]), cns_file)
cns_file = re.sub('structures_1=200', 'structures_1=' + str(models[1]), cns_file)
cns_file = re.sub('anastruc_1=200', 'anastruc_1=' + str(models[2]), cns_file)

with open('run.cns', 'w') as file:
    file.write(cns_file)

# THIRD STEP -> Run docking and redirect the output showing the progression to a file
command = 'python ' + haddock + ' > ../haddock.out'
subprocess.run(command, shell=True)

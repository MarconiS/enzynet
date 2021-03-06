'Generate datasets'

# Authors: Afshine Amidi <lastname@mit.edu>
#          Shervine Amidi <firstname@stanford.edu>

# MIT License

import numpy as np
import pandas as pa

import os

from tqdm import tqdm
from enzynet import read_dict, dict_to_csv, PDB_backbone


# Date of retrieval of raw datasets from rcsb.org: 07-03-2017

# Parameters
n_classes = 6

##------------------------- Data preprocessing -------------------------------##
# Computations
for i in range(1, n_classes+1):
    # Initialization
    errors = [] # List of indexes with error
    enzymes = pa.read_table('raw/' + str(i) + '.txt', header = None) # Load PDB IDs
    list_enzymes = enzymes.loc[:,0].tolist()

    # Look for errors
    for k, enzyme in enumerate(tqdm(list_enzymes)):
        try:
            # Load local enzyme
            local_enzyme = PDB_backbone(enzyme)
            local_enzyme.get_coords()

            # Look for problem
            if len(local_enzyme.backbone_atoms) == 0: # Empty enzyme
                errors += [k]

        except: # File does not exist, i.e. deprecated enzyme
            errors += [k]

    # Drop errors and save
    enzymes = enzymes.drop(enzymes.index[errors])
    enzymes.to_csv(str(i) + '.txt', header = None, index = None)

##-------------- Dictionary with all PDBs in dataset_all.csv -----------------##
# Initialization
labels = {}

# Computations
for i in range(1, n_classes+1):
    # Load PDB IDs for each class
    enzymes = pa.read_table(str(i) + '.txt', header = None)
    enzymes = enzymes[0].tolist()

    # Add entries to dict
    for entry in enzymes:
        if entry in labels: # PDB_id already in dict
            labels[entry] = labels[entry] + [i]
        else: # PDB_id not yet in dict
            labels[entry] = [i]

# # Save results
# dict_to_csv(labels, '../dataset_all.csv') # DONE 18-03-2017

##--------- Dictionary with single-label PDBs in dataset_single.csv ----------##
# Initialization
labels_temp = read_dict('../dataset_all.csv')
labels = {}

# Computations
for entry in labels_temp:
    if len(labels_temp[entry]) == 3: # Single-label ('[i]')
        labels[entry] = int(labels_temp[entry][1]) # Convert list to scalar

# # Save results
# dict_to_csv(labels, '../dataset_single.csv') # DONE 18-03-2017

##---------- Dictionary with multi-label PDBs in dataset_multi.csv -----------##
# Initialization
labels_temp = read_dict('../dataset_all.csv')
labels = {}

# Computations
for entry in labels_temp:
    if len(labels_temp[entry]) > 3: # Multi-label
        labels[entry] = labels_temp[entry]

# # Save results
# dict_to_csv(labels, '../dataset_multi.csv') # DONE 18-03-2017

##----- Dict of ligands pointing to associated PDB in ligands_to_pdb.csv -----##
# Initialization
pdb_all = read_dict('../dataset_all.csv')
pdb_all = list(pdb_all.keys())
ligands = {}

# Computations
for enzyme in tqdm(pdb_all):
    # Load local enzyme
    local_enzyme = PDB_backbone(enzyme)

    # Get ligands
    local_enzyme.get_ligands()

    # Update dict
    for local_ligand in local_enzyme.ligands:
        if local_ligand in ligands: # Already in dict
            ligands[local_ligand] += [enzyme]
        else: # New entry
            ligands[local_ligand] = [enzyme]

# # Save results
# dict_to_csv(ligands, '../ligands_to_pdb.csv')

##---- Dict of PDBs pointing to associated ligands in pdb_to_ligands.csv -----##
# Initialization
pdb_all = read_dict('../dataset_all.csv')
pdb_all = list(pdb_all.keys())
pdb = {}

# Computations
for enzyme in tqdm(pdb_all):
    # Load local enzyme
    local_enzyme = PDB_backbone(enzyme)

    # Get ligands
    local_enzyme.get_ligands()

    # Add entry to dict
    pdb[enzyme] = local_enzyme.ligands

# # Save results
# dict_to_csv(pdb, '../pdb_to_ligands.csv')

##---------- Split single-label dataset in train/validation/test -------------##
# Initialization
labels_temp = read_dict('../dataset_single.csv')
pdb_ids = list(labels_temp)
partition = {}

# Parameters
x = 0.8 # Split all 80:20 in train/test and train 80:20 in train/validation

# Random shuffling
indexes = np.arange(len(pdb_ids))
np.random.shuffle(indexes)

# Train
train_ids = [pdb_ids[i] for i in indexes[0:int(x*x*len(pdb_ids))]]
partition['train'] = train_ids

# Validation
val_ids = [pdb_ids[i] for i in indexes[int(x*x*len(pdb_ids)):int(x*len(pdb_ids))]]
partition['validation'] = val_ids

# Test
test_ids = [pdb_ids[i] for i in indexes[int(x*len(pdb_ids)):]]
partition['test'] = test_ids

# # Save results
# dict_to_csv(partition, '../partition_single.csv') # DONE 18-03-2017

##------ Create reduced single-label train/validation/test sets --------------##
# Initialization
partition = read_dict('../partition_single.csv')
partition_red = {}

# Parameters
factor_reduction = 0.1

# Train
exec("partition['train'] = " + partition['train'])
indexes = np.arange(len(partition['train']))
np.random.shuffle(indexes)
train_ids = [partition['train'][i] for i in indexes[0:int(factor_reduction*len(indexes))]]
partition_red['train'] = train_ids

# Validation
exec("partition['validation'] = " + partition['validation'])
indexes = np.arange(len(partition['validation']))
np.random.shuffle(indexes)
val_ids = [partition['validation'][i] for i in indexes[0:int(factor_reduction*len(indexes))]]
partition_red['validation'] = val_ids

# Test
exec("partition['test'] = " + partition['test'])
indexes = np.arange(len(partition['test']))
np.random.shuffle(indexes)
test_ids = [partition['test'][i] for i in indexes[0:int(factor_reduction*len(indexes))]]
partition_red['test'] = test_ids

# # Save results
# dict_to_csv(partition_red, '../partition_single_red.csv') # DONE 18-03-2017

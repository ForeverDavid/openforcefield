#!/bin/env python
import os
import glob


# Cross-check energies of molecules from AlkEthOH set using SMIRNOFF xml file
# versus energies from AMBER .prmtop and .crd files (parm@frosst params)

#datapath = './AlkEthOH_tripos/AlkEthOH_chain_filt1'
# datapath = './AlkEthOH_tripos/AlkEthOH_rings_filt1'
datapath = './AlkEthOH_tripos/AlkEthOH_test_filt1'

# Check if we have this data file; if not we have to extract the archive.
if not os.path.isdir(datapath):
    print("Extracting archived molecule files.")
    # Extract the AlkEthOH dataset shipped with the toolkit in data/molecules/ in the working directory.
    from openforcefield.tests.utils import get_data_filename
    tarfile_path = os.path.join(get_data_filename('molecules'), 'AlkEthOH_tripos.tar.gz')
    import tarfile
    with tarfile.open(tarfile_path, 'r:gz') as tar:
        tar.extractall()

#Obtain list of molecules
mol_filepaths = glob.glob(datapath+'/*tripos.mol2')
mol_filepaths = [fnm for fnm in mol_filepaths if not 'c1302' in fnm]  # Skip water.

print('Found {} files to test'.format(len(mol_filepaths)))

# Load forcefield
from openforcefield.typing.engines.smirnoff import ForceField
forcefield = ForceField('forcefield/Frosst_AlkEthOH_parmAtFrosst.offxml')

from openforcefield.topology import Molecule
for mol_filepath in mol_filepaths:
    # Load molecule.
    molecule = Molecule.from_file(mol_filepath)

    molname = os.path.basename(mol_filepath).replace('_tripos.mol2','')
    print("Comparing {} ({}/{})...".format(molname, mol_filepaths.index(mol_filepath), len(mol_filepaths)))

    prmtop_filepath = os.path.join(datapath, molname+'.top')
    inpcrd_filepath = os.path.join(datapath, molname+'.crd')

    # Compare energies
    from openforcefield.tests.utils import compare_amber_smirnoff
    from openforcefield.tests.utils import FailedParameterComparisonError, FailedEnergyComparisonError
    try:
        results = compare_amber_smirnoff(prmtop_filepath, inpcrd_filepath, forcefield, molecule)
    except FailedParameterComparisonError as e:
        print(e)
    except FailedEnergyComparisonError as e:
        print(e)

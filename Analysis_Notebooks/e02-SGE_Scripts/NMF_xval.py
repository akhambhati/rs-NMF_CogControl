#!/bin/zsh

#
# Make sure that output files arrive in the working directory
#$ -cwd
#
# Join the outputs together
#$ -j y
#
# Reserve 10 GB of memory
#$ -l h_vmem=10.5G,s_vmem=10.0G
#
#Specify which nodes to use
#$ -q all.q,basic.q
#

source activate echobase
ipython -c "

######
from __future__ import division

import os
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import sys
import glob
import numpy as np

sge_task_id = int(os.environ['SGE_TASK_ID'])-1

sys.path.append('$1')
import Echobase
Subgraph = Echobase.Network.Partitioning.Subgraph

path_InpData = '$2'
path_ExpData = '$3'
path_Output = '{}/NMF_CrossValidation.Param.{}.npz'.format(path_ExpData, sge_task_id)

# Check if the output already exists (can be commented if overwrite is needed)
if os.path.exists(path_Output):
    raise Exception('Output {} already exists'.format(path_Output))

# Load the configuration matrix and parameter list
cfg_data = np.load('{}/Population.Configuration_Matrix.npz'.format(path_InpData))
cfg_matr = cfg_data['cfg_matr']
param_list = np.load('{}/NMF_CrossValidation.Param_List.npz'.format(path_ExpData))['param_list']

# Grab the task ID of the current job (and the associated parameter dictionary)
param_dict = param_list[sge_task_id]
param_dict['train_ix'] = map(int, param_dict['train_ix'])
param_dict['test_ix'] = map(int, param_dict['test_ix'])

qmeas_dict = Subgraph.optimize_nmf.run_xval_paramset(cfg_matr, param_dict)

np.savez(path_Output, qmeas_dict=qmeas_dict)
######

"

# Copyright 2017 Diamond Light Source
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

'''
Created on 16 Jan 2012

@author: ssg37927
'''

import numpy as np

def calculate_phase_error(info, b_array):
    Energy = 3.0                    # Ideally needs to be tunable. Is a machine parameter. Would need a new Machine Class
    Const  = (0.03 / Energy) * 1e-2 # Appears to be defining 10^5eV... (Includes random 1e4 B factor)
    c      = 2.9911124e8            # The speed of light. For now.
    Mass   = 0.511e-3
    Gamma  = Energy / Mass

    nperiods = info['periods']
    step     = info['sstep']
    n_stp    = int(info['period_length'] / step)
    n_s_stp  = int(round((info['smax'] - info['smin']) / step))
    nskip    = 8

    trap_b_array = np.roll(b_array, 1, 0)
    trap_b_array[...,0,:] = 0.0
    trap_b_array = (trap_b_array + b_array) * (step / 2)

    trajectories        = np.zeros([*b_array.shape[:3], 4])
    trajectories[...,2] = -np.cumsum(np.multiply(Const, trap_b_array[...,1]), axis=2)
    trajectories[...,3] =  np.cumsum(np.multiply(Const, trap_b_array[...,0]), axis=2)

    trap_traj = np.roll(trajectories, 4, 0)
    trap_traj[:,:,0,:] = 0.0
    trap_traj = (trap_traj + trajectories) * (step / 2)

    trajectories[...,0] = np.cumsum(trap_traj[...,2], axis=2)
    trajectories[...,1] = np.cumsum(trap_traj[...,3], axis=2)

    i = ((b_array.shape[0] + 1) // 2) - 1
    j = ((b_array.shape[1] + 1) // 2) - 1

    w      = np.zeros([n_s_stp, 2])
    w[:,0] = np.square(trajectories[i,j,:,2])
    w[:,1] = np.square(trajectories[i,j,:,3])

    trap_w = np.roll(w, 1, 0)
    trap_w[0,:] = 0.0
    trap_w = (trap_w + w) * 1e-3 * (step / 2)

    # TODO unwind the order of operations going on here...
    ph  = np.cumsum(trap_w[:,0] + trap_w[:,1]) / (2.0 * c)
    ph2 = (step * 1e-3 / (2.0 * c * Gamma ** 2)) * np.arange(n_s_stp) + ph
    v1  = (n_stp // 4) * np.arange(4 * nperiods - 2 * nskip) + n_s_stp // 2 - nperiods * n_stp // 2 + (nskip - 1) * n_stp // 4
    v2  = ph2[(v1[0]):(v1[-1] + (n_stp // 4)):(n_stp // 4)]

    A = np.vstack([v1, np.ones(len(v1))]).T
    m, intercept = np.linalg.lstsq(A, v2, rcond=None)[0]

    Omega0 = 2 * np.pi / (m * n_stp)
    phfit  = intercept + m * v1
    ph     = v2 - phfit
    pherr  = np.sum(ph ** 2) * Omega0 ** 2
    pherr  = np.sqrt(pherr / (4 * nperiods + 1 - 2 * nskip)) * 360.0 / (2.0 * np.pi)
    return pherr, trajectories


# TODO marked for deprecation, never called
def straightness(trajectories, nperiods):

    points_per_period = (trajectories.shape[0] / nperiods) / 3

    # Magic number not documented (to do with how data is interleaved into trajectories tensor?)
    nskip  = 2 # Value of 8 in other functions...
    skip   = (trajectories.shape[0] / 3) + (nskip * points_per_period)

    xmean  = np.mean(trajectories[skip:-skip,0])
    dxmean = trajectories[skip:-skip,0] - xmean
    zabs   = np.abs(trajectories[skip:-skip,1])

    strx   = np.max(dxmean)
    strz   = np.max(zabs)
    return strx, strz

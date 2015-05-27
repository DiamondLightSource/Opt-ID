'''
Created on 16 Jan 2012

@author: ssg37927
'''

import numpy as np
from scipy import signal
import logging


def generate_B_array(xmin, xmax, xstep, zmin, zmax, zstep, smin, smax, sstep, magdims, V1):
    '''
    magdims = np.array([41.,16.,5.25])
    mingap = 5.0
    '''
    return generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, smin, smax, sstep, 0.0, magdims, V1)



def generate_integral_array(xmin, xmax, xstep, xoff, zmin, zmax, zstep, zoff, smin, smax, sstep, soff, magdims, mingap):
    
    # Fist generate the b_array at the right point
    BClean = generate_B_array_with_offsets(xmin, xmax, xstep, xoff, zmin, zmax, zstep, zoff, smin, smax, sstep, soff, magdims, mingap)
    
    B = BClean*1e4*sstep
    
    # get the appropriate parts of the b array
    bx = B[:,0,:,:,0]
    bz = B[:,0,:,:,1]
    bs = B[:,0,:,:,2]
    
    fintx = bx.sum(1)
    fintz = bz.sum(1)
    fints = bs.sum(1)
    
    scale_factor = -np.arange(smin, smax, sstep)
    
    sintx = np.array(bx)
    sintx[:,:,1] = bx[:,:,1]*scale_factor
    sintx[:,:,0] = bx[:,:,0]*scale_factor
    sintx[:,:,2] = bx[:,:,2]*scale_factor
    
    sintx =  sintx.sum(1)
    
    sintz = np.array(bz)
    sintz[:,:,1] = bz[:,:,1]*scale_factor
    sintz[:,:,0] = bz[:,:,0]*scale_factor
    sintz[:,:,2] = bz[:,:,2]*scale_factor
    
    sintz =  sintz.sum(1)
    
    sints = np.array(bs)
    sints[:,:,1] = bs[:,:,1]*scale_factor
    sints[:,:,0] = bs[:,:,0]*scale_factor
    sints[:,:,2] = bs[:,:,2]*scale_factor
    
    sints =  sints.sum(1)
    
    mid = (BClean.shape[0]-1)/2
    
    # should only pass back the middle point 
#    return (BClean[mid:mid+1,:,:,:,:], fintx, fintz, fints, sintx, sintz, sints)
    #Passing back full array
    return (BClean, fintx, fintz, fints, sintx, sintz, sints)

def calculate_magnetic_components(mag_x, mag_z, mag_s, B_array):
    mult = B_array*np.array([mag_x,mag_z,mag_s])
#    mult = B_array*np.array([mag_z,mag_x,mag_s])
    return mult.sum((len(mult.shape)-1))


def calculate_integral_component(mag_x, mag_z, mag_s, fintx, fintz, sintx, sintz):
    mags = np.array([mag_x,mag_z,mag_s])
    
    firstix = (fintx*mags).sum(1)
    firstiz = (fintz*mags).sum(1)
    
    secondix = (sintx*mags).sum(1)
    secondiz = (sintz*mags).sum(1)
    
    return(firstix,firstiz,secondix,secondiz)
    

def calculate_phase_error(info, b_array):
    Energy = 3.0  #ideally needs to be tunable. Is a machine parameter. Would need a new Machine Class
    Const = (0.03/Energy)*1e-2  # appears to be defining 10^5eV...(Includes random 1e4 B factor)
    c=2.9911124e8 #The speed of light. For now.
    Mass =0.511e-3
    Gamma=Energy/Mass
    
    #quick hack for central trajectory only
#    i=b_array.shape[0]
#    i=(i+1)/2-1
#    b_array=b_array[i,:,:]
    
    
    nperiods=info['periods']
    step=info['sstep']
    n_stp = (info['period_length']/step)
    n_s_stp = (info['smax']-info['smin'])/step
    
    nskip=8
    
#    ph=np.zeros(n_s_stp)
    ph2=np.zeros(n_s_stp)
    
#    v1=np.zeros((4*nperiods-2*nskip))
#    v2=np.zeros((4*nperiods-2*nskip))
    v2a=np.zeros((4*nperiods-2*nskip))
    
    logging.debug("Barray shape %s"%(str(b_array.shape)))
    
    trap_b_array = np.roll(b_array, 1, 0)
    logging.debug("trap_b_array shape %s"%(str(trap_b_array.shape)))
    trap_b_array[:,:,0,:]=0.0
    trap_b_array = (trap_b_array+b_array)*step/2
    
    trajectories = np.zeros([b_array.shape[0],b_array.shape[1],b_array.shape[2],4]) 
    
    trajectories[:,:,:,2]=-np.cumsum(np.multiply(Const,trap_b_array[:,:,:,1]), axis=2)
    trajectories[:,:,:,3]=np.cumsum(np.multiply(Const,trap_b_array[:,:,:,0]), axis=2)
    
    trap_traj = np.roll(trajectories, 4, 0)
    trap_traj[:,:,0,:]=0.0
    trap_traj=(trap_traj+trajectories)*step/2
    
    trajectories[:,:,:,0]=np.cumsum(trap_traj[:,:,:,2], axis=2)
    trajectories[:,:,:,1]=np.cumsum(trap_traj[:,:,:,3], axis=2)
    
    #wx=np.cumsum(np.square(trajectories[:,2])*1e-3)
    #wz=np.cumsum(np.square(trajectories[:,3])*1e-3)

    i=b_array.shape[0]
    i=(i+1)/2-1
    j=b_array.shape[1]
    j=(j+1)/2-1
    
    b_array=b_array[i,j,:,:]
    
    
    
    w=np.zeros([n_s_stp,2])
    
    w[:,0]=np.square(trajectories[i,j,:,2])
    w[:,1]=np.square(trajectories[i,j,:,3])
    
    trap_w = np.roll(w,1,0)
    trap_w[0,:] = 0.0
    trap_w= (trap_w+w)*1e-3*step/2
    
    ph=np.cumsum(trap_w[:,0]+trap_w[:,1])/(2.0*c)
    ph2=(step*1e-3/(2.0*c*Gamma**2))*np.arange(n_s_stp)+ph
    
    
    v1=(n_stp/4)*np.arange(4*nperiods-2*nskip)+n_s_stp/2-nperiods*n_stp/2+(nskip-1)*n_stp/4
    v2=ph2[v1[0]:v1[-1]+n_stp/4:n_stp/4]
            
            
    #'linear fit'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]
    Omega0=2*np.pi/(m*n_stp)
    
    v2=ph[v1[0]:v1[-1]+n_stp/4:n_stp/4]
    
        
    #'fit function'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]

    phfit=intercept+m*v1
    
    
    ph=v2-phfit
    pherr=np.sum(ph**2)*Omega0**2
    
    pherr=np.sqrt(pherr/(4*nperiods+1-2*nskip))*360.0/(2.0*np.pi)
    return (pherr, trajectories)

def calculate_phase_error2(info, b_array):
    Energy = 3.0  #ideally needs to be tunable. Is a machine parameter. Would need a new Machine Class
    Const = (0.03/Energy)*1e-2  # appears to be defining 10^5eV...(Includes random 1e4 B factor)
    c=2.9911124e8 #The speed of light. For now.
    Mass =0.511e-3
    Gamma=Energy/Mass
    
    #quick hack for central trajectory only
    i=b_array.shape[0]
    i=(i+1)/2-1
    b_array=b_array[i,:,:]
    
    
    nperiods=info['periods']
    step=info['sstep']
    n_stp = (info['period_length']/step)
    n_s_stp = (info['smax']-info['smin'])/step
    
    nskip=8
    
    ph=np.zeros(n_s_stp)
    ph2=np.zeros(n_s_stp)
    
    v1=np.zeros((4*nperiods-2*nskip))
    v2=np.zeros((4*nperiods-2*nskip))
    v2a=np.zeros((4*nperiods-2*nskip))
    
    
    
    trap_b_array = np.roll(b_array, 1, 0)
    trap_b_array[0,:]=0.0
    trap_b_array = (trap_b_array+b_array)*step/2
    
    trajectories = np.zeros([n_s_stp,4]) 
    
    trajectories[:,2]=-np.cumsum(np.multiply(Const,trap_b_array[:,1]))
    trajectories[:,3]=np.cumsum(np.multiply(Const,trap_b_array[:,0]))
    
    trap_traj = np.roll(trajectories, 1, 0)
    trap_traj[0,:]=0.0
    trap_traj=(trap_traj+trajectories)*step/2
    
    trajectories[:,0]=np.cumsum(trap_traj[:,2])
    trajectories[:,1]=np.cumsum(trap_traj[:,3])
    
    #wx=np.cumsum(np.square(trajectories[:,2])*1e-3)
    #wz=np.cumsum(np.square(trajectories[:,3])*1e-3)
    
    w=np.zeros([n_s_stp,2])
    
    w[:,0]=np.square(trajectories[:,2])
    w[:,1]=np.square(trajectories[:,3])
    
    trap_w = np.roll(w,1,0)
    trap_w[0,:] = 0.0
    trap_w= (trap_w+w)*1e-3*step/2
    
    ph=np.cumsum(trap_w[:,0]+trap_w[:,1])/(2.0*c)
    ph2=(step*1e-3/(2.0*c*Gamma**2))*np.arange(n_s_stp)+ph
    
    
    v1=(n_stp/4)*np.arange(4*nperiods-2*nskip)+n_s_stp/2-nperiods*n_stp/2+(nskip-1)*n_stp/4
    v2=ph2[v1[0]:v1[-1]+n_stp/4:n_stp/4]
            
            
    #'linear fit'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]
    Omega0=2*np.pi/(m*n_stp)
    
    v2=ph[v1[0]:v1[-1]+n_stp/4:n_stp/4]
    
        
    #'fit function'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]

    phfit=intercept+m*v1
    
    
    ph=v2-phfit
    pherr=np.sum(ph**2)*Omega0**2
    
    pherr=np.sqrt(pherr/(4*nperiods+1-2*nskip))*360.0/(2.0*np.pi)
    return (pherr, trajectories)
    
def calculate_phase_error3(info, b_array):
    Energy = 3.0  #ideally needs to be tunable. Is a machine parameter. Would need a new Machine Class
    Const = (0.03/Energy)*1e-2  # appears to be defining 10^5eV...(Includes random 1e4 B factor)
    c=2.9911124e8 #The speed of light. For now.
    Mass =0.511e-3
    Gamma=Energy/Mass
    
    #quick hack for central trajectory only
    i=b_array.shape[0]
    i=(i+1)/2-1
    b_array=b_array[i,:,:]
    
    
    nperiods=info['periods']
    step=info['sstep']
    n_stp = (info['period_length']/step)
    n_s_stp = (info['smax']-info['smin'])/step
    
    nskip=8
    
    trap_b_array = np.roll(b_array, 1, 0)
    trap_b_array[0,:]=0.0
    trap_b_array = (trap_b_array+b_array)*step/2
    
    trajectories = np.zeros([n_s_stp,4]) 
    
    trajectories[:,2]=-np.cumsum(np.multiply(Const,trap_b_array[:,1]))
    trajectories[:,3]=np.cumsum(np.multiply(Const,trap_b_array[:,0]))
    
    trap_traj = np.roll(trajectories, 1, 0)
    trap_traj[0,:]=0.0
    trap_traj=(trap_traj+trajectories)*step/2
    
    trajectories[:,0]=np.cumsum(trap_traj[:,2])
    trajectories[:,1]=np.cumsum(trap_traj[:,3])
    
    #wx=np.cumsum(np.square(trajectories[:,2])*1e-3)
    #wz=np.cumsum(np.square(trajectories[:,3])*1e-3)
    
    detrended_trajectories=signal.detrend(trajectories[:,:],axis=0)
    a=np.gradient(detrended_trajectories[:,0])
    b=np.gradient(detrended_trajectories[:,1])
    w=np.vstack((a,b))
    w=np.square(np.transpose(w))
    
    trap_w = np.roll(w,1,0)
    trap_w[0,:] = 0.0
    trap_w= (trap_w+w)*1e-3*1/2
    
    ph=np.cumsum(trap_w[:,0]+trap_w[:,1])/(2.0*c)

    ph2=(1*1e-3/(2.0*c*Gamma**2))*np.arange(n_s_stp)+ph
    
    
    v1=(n_stp/2)*np.arange(2*nperiods-1*nskip)+n_s_stp/2-nperiods*n_stp/2+(nskip-1)*n_stp/4
    v2=ph2[v1[0]:v1[-1]+n_stp/2:n_stp/2]
            
            
    #'linear fit'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]
    Omega0=2*np.pi/(m*n_stp)
    
    v2=ph[v1[0]:v1[-1]+n_stp/2:n_stp/2]
    
        
    #'fit function'
    A=np.vstack([v1,np.ones(len(v1))]).T
    
    m,intercept=np.linalg.lstsq(A, v2)[0]

    phfit=intercept+m*v1
    
    
    ph=v2-phfit
    pherr=np.sum(ph**2)*Omega0**2
    pherrnew=ph*Omega0*360.0/(2.0*np.pi)
    
    pherr=np.sqrt(pherr/(4*nperiods+1-2*nskip))*360.0/(2.0*np.pi)
    
    

    return (pherr, trajectories, pherrnew)

def straightness(trajectories, nperiods):
    points_per_period = (trajectories.shape[0]/nperiods)/3
    nskip = 2
    skip = (trajectories.shape[0]/3)+(nskip*points_per_period)
    xmean=np.mean(trajectories[skip:-skip,0])
    dxmean=trajectories[skip:-skip,0]-xmean
    zabs=np.abs(trajectories[skip:-skip,1])
    strx=np.max(dxmean)
    strz=np.max(zabs)
    
    return (strx, strz)

'Area for testing new B-Field calculation functions'
def fortPMB_NEW(testpoint,m,i,magdims, V1):
    '''This function Calculates the B-field in a single orientation according to the calling function
    It's pretty much a carbon-copy of the FORTRAN code
    
    '''

    B=0.0
    
    V2=V1+magdims
    
    r1=testpoint.copy()
    r2=testpoint.copy()
    
    for p in range(3):
        r1[p]=r1[p]-V1[p]
        r2[p]=r2[p]-V2[p]
    
#    r1=testpoint-V1
#    r2=testpoint-V2
        
    for j in range(3):
        I1=0.
        I2=0.
        if j==i:
            B=B
        else:
            k=3-i-j
            r1i=r1[i]
            r1j=r1[j]
            r2i=r2[i]
            r2j=r2[j]
            if ((r1[k].all() > 0) and (r2[k].all() > 0 )) :
                r1k=r1[k]
                r2k=r2[k]
            else :
                r1k=-r2[k]
                r2k=-r1[k]
            
            a1=np.sqrt(r2i*r2i+r2j*r2j+r2k*r2k)
            a2=np.sqrt(r1i*r1i+r1j*r1j+r2k*r2k)
            a3=np.sqrt(r1i*r1i+r2j*r2j+r1k*r1k)
            a4=np.sqrt(r2i*r2i+r1j*r1j+r1k*r1k)
            a5=np.sqrt(r1i*r1i+r2j*r2j+r2k*r2k)
            a6=np.sqrt(r2i*r2i+r1j*r1j+r2k*r2k)
            a7=np.sqrt(r2i*r2i+r2j*r2j+r1k*r1k)
            a8=np.sqrt(r1i*r1i+r1j*r1j+r1k*r1k)
            

            b2=r1i*r2k/(r1j*a2)
            b4=r2i*r1k/(r1j*a4)
            b6=r2i*r2k/(r1j*a6)
            b8=r1i*r1k/(r1j*a8)
    
            b1=r2i*r2k/(r2j*a1)
            b3=r1i*r1k/(r2j*a3)
            b5=r1i*r2k/(r2j*a5)
            b7=r2i*r1k/(r2j*a7)
    
            I1=(np.arctan(b1)+np.arctan(b2)+np.arctan(b3)+np.arctan(b4)-np.arctan(b5)-np.arctan(b6)-np.arctan(b7)-np.arctan(b8))
                

            

            c1=a1+r2k
            c2=a2+r2k
            c3=a3+r1k
            c4=a4+r1k
            c5=a5+r2k
            c6=a6+r2k
            c7=a7+r1k
            c8=a8+r1k

    
            I2=(np.log(c1*c2*c3*c4/(c5*c6*c7*c8)))

    
            B=B-(m[i]*I1/(4*np.pi))
            B=B-(m[j]*I2/(4*np.pi))

    return B
#TODO might be able to remove s_offset altogether
#TODO not sure about mingap either 

def wrapCalcB(testpoint, magdims,  V1):
    '''This function takes the arguments 'testpoint' and 's_offset'
    'testpoint' requires an array of floats of length 3 describing the [x,z,s] co-ordinates of the point under consideration
    's_offset' requires a float that describes the s-direction offset of the magnet block
    
    This function calls the main field calculating function, and outputs a 3x3 matrix of the form
    [[Bx(x), Bz(x), Bs(x)]
     [Bx(z), Bz(z), Bs(z)]
     [Bx(s), Bz(s), Bs(s)]].
     
     To calculate the real field component of any block need to get real data sum contributions such that
     Bx=Bx(x)*Mx + Bx(z)*Mz + Bx(s)*Ms'''
    B=np.zeros((testpoint.shape+(3,3))[1:])
    for i in range(3):
        m=np.zeros(3)
        m[i]=1
        for j in range(i,3):
            B[:,:,:,i,j]= fortPMB_NEW(testpoint,m,j, magdims, V1)
            if i!=j:
                B[:,:,:,j,i]=B[:,:,:,i,j]
    return B

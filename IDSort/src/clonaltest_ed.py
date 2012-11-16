'''
Created on 16 Nov 2011

@author: ssg37927
'''

import scisoftpy as dnp
import setmag as sm
import id_bcell as idb
import traj_shim_bcell as bcell
import clonal as cl
import magnet_tools as mt
import h5py
import os
reload(sm)
reload(idb)
reload(cl)
reload(mt)
reload(bcell)


mag = sm.AllMagnets()
mag.add_magnet_set(sm.MagnetStore.horizontal, "C:\Documents and Settings\gdy32713\workspace\IDSort/data/I23H.sim")
mag.add_magnet_set(sm.MagnetStore.horizontal_end, "C:\Documents and Settings\gdy32713\workspace\IDSort\data/I23HEA.sim")
mag.add_magnet_set(sm.MagnetStore.vertical, "C:\Documents and Settings\gdy32713\workspace\IDSort\data/I23V.sim")
mag.add_magnet_set(sm.MagnetStore.vertical_end, "C:\Documents and Settings\gdy32713\workspace\IDSort\data/I23VE.sim")

presort = "S:\Technical\IDs\History files\I23 - U27\Physics\Measurement\C001\C001_order.sim"
bfields = "S:\Technical\IDs\History files\I23 - U27\Physics\Measurement\C001\C001.inp"
ppm = sm.PPM(mag, periods=74, symetry=sm.BeamAssembly.antisymetric, magdims=[41.,16.,6.75], offset=0.325, presort = presort, bfields = bfields)
ppm.report()

'''For testing of flips'''

#ppmbc = idb.PPM_BCell(ppm)

#h5filea = h5py.File("C:/IDData/init22.h5",'a')
#ppmbc.write_bcell_to_h5(h5filea, 0, 0)
#h5filea.close()

flips = 5
swaps = 2

ppmbc = bcell.traj_shim_BCell(ppm)

cs = cl.ClonalSelection(ppmbc,"C:/IDData/i23_0042.h5", population_size=10, dup=2, c=1.0)

cs.initialise()

cs.run_epocs(10)
cs.pop[10][0].report()
#def plot_data(clonal):
#    stats = cl.get_clonal_stats(clonal)
#    dnp.plot.line([dnp.array(stats[0]),dnp.array(stats[1]),dnp.array(stats[2])])
#
#plot_data(cs)

#def plot_update(itterations):
#    for i in range(itterations):
#        cs.run_epocs(2)
#        dnp.plot.line([dnp.array(cs.average_fitness),dnp.array(cs.best),dnp.array(cs.worst)])

#ppm.calculate_phase_error()


t1 = ppm.top_beam.calculate_b_contribution(10)
t2 = ppm.top_beam.calculate_b_contribution(11)
t3 = ppm.top_beam.calculate_b_contribution(12)
t4 = ppm.top_beam.calculate_b_contribution(13)

#one
dnp.plot.line([t1[0,0,500:1300,0]], name="Bx")
dnp.plot.line([t1[0,0,500:1300,1]], name="Bz")
dnp.plot.line([t1[0,0,500:1300,2]], name="Bs")

#top cycle
dnp.plot.line([t1[0,0,800:2000,0],t2[0,0,600:1800,0],t3[0,0,400:1600,0],t4[0,0,200:1400,0]], name="Bx")
dnp.plot.line([t1[0,0,800:2000,1],t2[0,0,600:1800,1],t3[0,0,400:1600,1],t4[0,0,200:1400,1]], name="Bz")
dnp.plot.line([t1[0,0,800:2000,2],t2[0,0,600:1800,2],t3[0,0,400:1600,2],t4[0,0,200:1400,2]], name="Bs")

b1 = ppm.bottom_beam.calculate_b_contribution(10)
b2 = ppm.bottom_beam.calculate_b_contribution(11)
b3 = ppm.bottom_beam.calculate_b_contribution(12)
b4 = ppm.bottom_beam.calculate_b_contribution(13)

# bottom cycle
dnp.plot.line([b1[0,0,800:1600,0],b2[0,0,600:1400,0],b3[0,0,400:1200,0],b4[0,0,200:1000,0]], name="Bx")
dnp.plot.line([b1[0,0,800:1600,1],b2[0,0,600:1400,1],b3[0,0,400:1200,1],b4[0,0,200:1000,1]], name="Bz")
dnp.plot.line([b1[0,0,800:1600,2],b2[0,0,600:1400,2],b3[0,0,400:1200,2],b4[0,0,200:1000,2]], name="Bs")


# both cycles
dnp.plot.line([t1[0,0,800:1600,0],t2[0,0,600:1400,0],t3[0,0,400:1200,0],t4[0,0,200:1000,0],b1[0,0,800:1600,0],b2[0,0,600:1400,0],b3[0,0,400:1200,0],b4[0,0,200:1000,0]], name="Bx")
dnp.plot.line([t1[0,0,800:1600,1],t2[0,0,600:1400,1],t3[0,0,400:1200,1],t4[0,0,200:1000,1],b1[0,0,800:1600,1],b2[0,0,600:1400,1],b3[0,0,400:1200,1],b4[0,0,200:1000,1]], name="Bz")
dnp.plot.line([t1[0,0,800:1600,2],t2[0,0,600:1400,2],t3[0,0,400:1200,2],t4[0,0,200:1000,2],b1[0,0,800:1600,2],b2[0,0,600:1400,2],b3[0,0,400:1200,2],b4[0,0,200:1000,2]], name="Bs")

top = ppm.top_beam.build_b_arrays()
bottom = ppm.bottom_beam.build_b_arrays()

# top id
dnp.plot.line([top[0,0,:,0]], name="Bx")
dnp.plot.line([top[0,0,:,1]], name="Bz")
dnp.plot.line([top[0,0,:,2]], name="Bs")

#bottom id
dnp.plot.line([bottom[0,0,:,0]], name="Bx")
dnp.plot.line([bottom[0,0,:,1]], name="Bz")
dnp.plot.line([bottom[0,0,:,2]], name="Bs")


# both
dnp.plot.line([top[0,0,:,0],bottom[0,0,:,0]], name="Bx")
dnp.plot.line([top[0,0,:,1],bottom[0,0,:,1]], name="Bz")
dnp.plot.line([top[0,0,:,2],bottom[0,0,:,2]], name="Bs")

# sum
ppm_b = ppm.build_b_array()
dnp.plot.line([ppm_b[0,0,:,0]], name="Bx")
dnp.plot.line([ppm_b[0,0,:,1]], name="Bz")
dnp.plot.line([ppm_b[0,0,:,2]], name="Bs")

#raise Exception("Buggerit")

def plot_b(ppm_list):
    x = []
    y = []
    z = []
    for ppm in ppm_list:
        ppm_b = ppm.build_b_array()
        x.append(ppm_b[0,0,:,0])
        y.append(ppm_b[0,0,:,1])
        z.append(ppm_b[0,0,:,2])
    dnp.plot.line(x, name="Bx")
    dnp.plot.line(y, name="Bz")
    dnp.plot.line(z, name="Bs")

# general time plot
#from time import sleep
#for i in range(110):
#    tmp = []
#    for j in range(10):
#        tmp.append(cs.pop[i+j][0].ppm)
#    plot_b(tmp)
#    print(i)
#    sleep(0.2)


# cProfile.run('execfile("C:\\Users\\ssg37927\\Desktop\\IDSort\\IDSort\\src\\clonaltest.py")')
# cProfile.run('execfile("C:\\Documents and Settings\\gdy32713\\workspace\\IDSort\\src\\clonaltest_ed.py")','stats')

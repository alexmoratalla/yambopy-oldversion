#
# Author: Alejandro Molina-Sanchez
#
# Example of YamboQPDB Class 
#
from qepy import *
from yambopy import *
import matplotlib.pyplot as plt


# Define path in reduced coordinates using Class Path

'''
path = Path([ [[0.0,0.0,0.0],'$\Gamma$'],
           [[0.0,0.5,0.5],'$X$'],
           [[0.0,0.0,0.0],'$\Gamma$'],
           [[0.5,0.0,0.0],'$L$']], [20,20,20])

'''
path = Path([[ [0.  ,0.  ,0.  ],'$\Gamma$'],
             [ [0.5 ,0.5 ,0.  ],'$X$'     ],
             [ [0.5 ,0.5 ,0.5 ],'$L$'     ],
             [ [0.75,0.75,0.25],'$M$'     ]], [10,10,10] ) 

# Read Lattice information from SAVE
lat  = YamboSaveDB.from_db_file(folder='gw_calc/SAVE',filename='ns.db1')
# Read QP database
y    = YamboQPDB.from_db(filename='ndb.QP',folder='gw_calc/yambo')


# 1. Find scissor operator for valence and conduction bands
fig = plt.figure(figsize=(6,4))
ax  = fig.add_axes( [ 0.20, 0.20, 0.70, 0.70 ])
ax.set_xlabel('$E_{KS}$')
ax.set_ylabel('$E_{GW}$')

y.plot_scissor_ax(ax,4)

plt.show()

# 2. Plot of KS and QP eigenvalues NOT interpolated along the path
ks_bs_0, qp_bs_0 = y.get_bs_path(lat,path)

fig = plt.figure(figsize=(4,5))
ax = fig.add_axes( [ 0.20, 0.20, 0.70, 0.70 ])

ks_bs_0.plot_ax(ax,legend=True,color_bands='r',label='KS')
qp_bs_0.plot_ax(ax,legend=True,color_bands='b',label='QP-GW')

plt.show()

# 3. Interpolation of KS and QP eigenvalues

ks_bs, qp_bs = y.interpolate(lat,path,what='QP+KS',lpratio=20)

fig = plt.figure(figsize=(4,5))
ax = fig.add_axes( [ 0.20, 0.20, 0.70, 0.70 ])

ks_bs.plot_ax(ax,legend=True,color_bands='r',label='KS')
qp_bs.plot_ax(ax,legend=True,color_bands='b',label='QP-GW')

plt.show()

# 4. Comparison of not-interpolaed and  interpolated eigenvalues

fig = plt.figure(figsize=(4,5))
ax = fig.add_axes( [ 0.20, 0.20, 0.70, 0.70 ])

ks_bs_0.plot_ax(ax,legend=True,color_bands='r',label='KS')
qp_bs_0.plot_ax(ax,legend=True,color_bands='b',label='QP-GW')
ks_bs.plot_ax(ax,legend=True,color_bands='g',label='KS')
qp_bs.plot_ax(ax,legend=True,color_bands='k',label='QP-GW')

plt.show()

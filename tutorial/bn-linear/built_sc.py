#
# Authors: A. Molina-Sanchez & H. P. C. Miranda
# Create a supercell with atoms displaced by phonons modes 
#
from __future__ import print_function, division
from qepy    import *
from yambopy import *
import argparse
from numpy import zeros, array, dot
from cmath import exp, pi

I = complex(0,1)
N_unitcell = 2
N_phonon   = 5
natoms     = 2
amplitude  = 0.02

# Extract numbers from the string
def flo_str(x):
  y=[]
  for t in x.split():
    try:
      y.append(float(t))
    except ValueError:
      pass
  return y

def reading_modes(folder,name,atoms,kpoints):
    """
    Function to read the eigenvalues and eigenvectors from Quantum Expresso
    """
    nphons = atoms*3
    data_phon = open('%s/%s' % (folder,name),'r').readlines()
    eig = zeros([kpoints,nphons])
    vec = zeros([kpoints,nphons,atoms,3],dtype=complex)
    for k in xrange(kpoints):
        #iterate over kpoints
        k_idx = 2 + k*((atoms+1)*nphons + 5)
        for n in xrange(nphons):
            #read eigenvalues
            eig_idx = k_idx+2+n*(atoms+1)
            eig[k][n] = flo_str(data_phon[eig_idx])[1]
            for i in xrange(atoms):
                #read eigenvectors
                z = flo_str(data_phon[eig_idx+1+i])
                vec[k][n][i] = array( [complex(z[0],z[1]),complex(z[2],z[3]),complex(z[4],z[5])], dtype=complex )
    return eig, vec

def get_inputfile():
    """ Define a Quantum espresso input file for boron nitride
    """ 
    qe = PwIn()
    qe.atoms = [['N',[0.0,0.0,0.0]],
                ['B',[0.5,0.0,0.0]]]
    qe.atypes = {'B': [10.811, "B.pbe-mt_fhi.UPF"],
                 'N': [14.0067,"N.pbe-mt_fhi.UPF"]}

    qe.control['prefix'] = "'bn'"
    qe.control['wf_collect'] = '.true.'
    qe.system['ecutwfc'] = 5
    qe.system['occupations'] = "'fixed'"
    qe.system['nat'] = 2
    qe.system['ntyp'] = 2
    qe.system['ibrav'] = 0
    qe.cell_units = 'bohr'
    qe.cell_parameters = [[4.926,0.0,0.0],
                          [0.0,20, 0.0],
                          [0.0,0.0,20 ]]
    qe.kpoints = [12, 1, 1]
    qe.electrons['conv_thr'] = 1e-8
    return qe

def get_supercell(n_replicas,phonon_mode,n_atoms,displacement):
#  n_replicas:   Number of unit-cell
#  phonon_mode:  select the phonon mode to displace the atoms of the supercell
#  n_atoms:      Atomas in the unit cell
#  displacement: Length of the displacement
  print()
  print('Supercell %d'    % n_replicas) 
  print('Phonon mode  %d' % phonon_mode)

  qpoint = [1/float(n_replicas), 0, 0]

  # read dynamical matrix and generate force constant file
  q2r = DynmatIn()
  q2r['fildyn'] = '\'bn.dyn\''
  q2r['flfrc']  = '\'bn.fc\''
  q2r.write('phonon/q2r.in')
  os.system('cd phonon; /Users/alejandro.molina/Software/espresso-5.1/bin/q2r.x < q2r.in > q2r.out')

  # calculate phonon mode
  matdyn = DynmatIn()
  matdyn['flfrc'] = '\'bn.fc\''
  matdyn['flfrq'] = '\'bn.freq\'' 
  matdyn.qpoints  = [ qpoint ]
  matdyn.write('phonon/matdyn.in')
  os.system('cd phonon; /Users/alejandro.molina/Software/espresso-5.1/bin/matdyn.x < matdyn.in > mat.out')


  freq, modes = reading_modes('phonon','matdyn.modes',2,1)
  freq, modes = freq[0], modes[0]

  pc = get_inputfile()
  sc = get_inputfile()

  # Cell parameter Super-cell
  apc =            pc.cell_parameters[0][0]
  asc = n_replicas*pc.cell_parameters[0][0]
  sc.cell_parameters = [[asc,0.0,0.0],
                        [0.0,20, 0.0],
                        [0.0,0.0,20 ]]
# Positions of the atoms
  sc_positions = [] 
  for ic in range(n_replicas):
    for ia in range(natoms):
      pos  = (array(pc.atoms[ia][1]) + array([ ic,0,0]))/n_replicas
      disp = amplitude * modes[phonon_mode,ia] * exp(I*2*pi*dot(qpoint,pos))
      sc_positions.append( [ str(pc.atoms[ia][0]), disp.real+pos ] )

  sc.atoms = sc_positions
  sc.system['nat'] = n_replicas*natoms 
  return sc

n_replicas   = 10
phonon_mode  = 5
n_atoms      = 2
displacement = 0.01


tag       = 'NR%dPM%dNA%dD%f' % (n_replicas,phonon_mode,n_atoms,displacement)
supercell = get_supercell(n_replicas,phonon_mode,n_atoms,displacement)

'''
# Generation of the NSCF data files and QE calculation of the SC
os.system( 'mkdir -p %s' % tag )
supercell.control['prefix'] = '"bn_sc"'
supercell.write('%s/sc.scf' % tag)
os.system('cd %s; pw.x < sc.scf | tee scf.out' %tag)
supercell.control['calculation'] = '"nscf"'
supercell.system['nbnd']         = 10*n_replicas
supercell.write('%s/sc.nscf' % tag)
os.system('cd %s; pw.x < sc.nscf | tee nscf.out' %tag)

# Bethe-Salpeter Calculation of the Supercell
os.system('cd %s/bn_sc.save ; p2y -O ../bse'  % tag)
os.system('cd %s/bse ; yambo'  % tag)
'''

# Input file for the BSE calculation
y = YamboIn('yambo -b -o b -k sex -y d -V all -q',folder='%s/bse'%tag)
y.write('%s/bse/yambo_run.in'%tag)
y['FFTGvecs'] = [30,'Ry']
y['NGsBlkXs'] = [1,'Ry']
y['BndsRnXs'] = [1,30]
y['BSEBands'] = [3,6]
y['BEnSteps'] = 500
y['BEnRange'] = [[0.0,6.0],'eV']
y.arguments.append('WRbsWF')
print(str(y))

#print( str(supercell) )

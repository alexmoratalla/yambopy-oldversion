#
# Author: Henrique Pereira Coutada Miranda
# Run a Silicon groundstate calculation using Quantum Espresso
#
from __future__ import print_function, division
from qepy import *
import argparse

kpoints = [30,1,1]
qpoints = [6,1,1]

# create the input files
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
    qe.system['ecutwfc'] = 20
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

#relax
def relax():
    if not os.path.isdir('relax'):
        os.mkdir('relax')
    qe = get_inputfile()
    qe.control['calculation'] = "'vc-relax'"
    qe.ions['ion_dynamics']  = "'bfgs'"
    qe.cell['cell_dynamics']  = "'bfgs'"
    qe.cell['cell_dofree']  = "'x'"
    qe.write('relax/bn.scf')

#scf
def scf(folder='scf'):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    qe = get_inputfile()
    qe.control['calculation'] = "'scf'"
    qe.write('%s/bn.scf'%folder)
 
#nscf
def nscf(kpoints,folder='nscf'):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    qe = get_inputfile()
    qe.control['calculation'] = "'nscf'"
    qe.electrons['diago_full_acc'] = ".true."
    qe.electrons['conv_thr'] = 1e-10
    qe.system['nbnd'] = 20
    qe.system['force_symmorphic'] = ".true."
    qe.kpoints = kpoints
    qe.write('%s/bn.nscf'%folder)

def phonon(kpoints,qpoints,folder='phonon'):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    ph = PhIn()
    ph['nq1'],ph['nq2'],ph['nq3'] = qpoints
    ph['tr2_ph'] = 1e-10
    ph['prefix'] = "'bn'"
    ph['epsil'] = ".false."
    ph['trans'] = ".true."
    ph['fildyn'] = "'bn.dyn'"
    ph['fildrho'] = "'bn.drho'"
    ph['ldisp'] = ".true."
    ph.write('%s/bn.ph'%folder)

    md = DynmatIn()
    md['asr'] = "'simple'"
    md['fildyn'] = "'bn.dyn1'"
    md['filout'] = "'bn.modes'"
    md.write('%s/bn.dynmat'%folder)

def update_positions(pathin,pathout):
    """ update the positions of the atoms in the scf file using the output of the relaxation loop
    """
    e = PwXML('bn',path=pathin)
    pos = e.get_scaled_positions()

    q = PwIn('%s/bn.scf'%pathin)
    print("old celldm(1)", q.cell_parameters[0][0])
    q.cell_parameters[0][0] = e.cell[0][0]
    q.cell_units = 'bohr'
    print("new celldm(1)", q.cell_parameters[0][0])
    q.atoms = zip([a[0] for a in q.atoms],pos)
    q.write('%s/bn.scf'%pathout)

if __name__ == "__main__":

    #parse options
    parser = argparse.ArgumentParser(description='Test the yambopy script.')
    parser.add_argument('-r' ,'--relax',       action="store_true", help='Don\'t run structural relaxation')
    parser.add_argument('-s' ,'--scf',         action="store_true", help='Don\'t run self-consistent calculation')
    parser.add_argument('-n' ,'--nscf',        action="store_true", help='Don\'t run non-self consistent calculation')
    parser.add_argument('-n2','--nscf_double', action="store_true", help='Don\'t run non-self consistent calculation for the double grid')
    parser.add_argument('-p' ,'--phonon',      action="store_true", help='Don\'t run phonon calculation')
    parser.add_argument('-t' ,'--nthreads',    action="store_true", help='Number of threads', default=2 )
    args = parser.parse_args()

    # create input files and folders
    relax()
    scf()
    nscf(kpoints)
    phonon(kpoints,qpoints)

    if args.relax:
        print("running relax:")
        os.system("cd relax; mpirun -np %d pw.x -inp bn.scf > relax.log"%args.nthreads)  #relax
        update_positions('relax','scf') 
        print("done!")

    if args.scf:
        print("running scf:")
        os.system("cd scf; mpirun -np %d pw.x -inp bn.scf > scf.log"%args.nthreads)  #scf
        print("done!")
   
    if args.nscf: 
        print("running nscf:")
        os.system("cp -r scf/bn.save nscf/") #nscf
        os.system("cd nscf; mpirun -np %d pw.x -inp bn.nscf > nscf.log"%args.nthreads) #nscf
        print("done!")

    if args.phonon:
        print("running phonon:")
        os.system("cp -r scf/bn.save phonon/")
        os.system("cd phonon; ph.x -inp bn.ph > phonon.log") #phonon
        os.system("cd phonon; dynmat.x -inp bn.dynmat > dynmat.log") #matdyn
        print("done!")

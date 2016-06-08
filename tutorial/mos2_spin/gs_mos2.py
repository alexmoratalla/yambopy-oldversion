#
# Author: Henrique Pereira Coutada Miranda
# Run a MoS2 groundstate calculation using Quantum Espresso
#
from __future__ import print_function, division
from qepy import *
import argparse

#parse options
parser = argparse.ArgumentParser(description='Test the yambopy script.')
parser.add_argument('-s' ,'--scf')
parser.add_argument('-n' ,'--nscf')
args = parser.parse_args()

#
# Create the input files
#
def get_inputfile():
    """ Define a Quantum espresso input file for MoS2
    """
    qe = PwIn()
    a = 5.838
    c = 20
    qe.atoms = [['Mo',[2/3,1/3,0.5]],
                [ 'S',[1/3,2/3, 2.92781466/c+0.5]],
                [ 'S',[1/3,2/3,-2.92781466/c+0.5]]]
    qe.atypes = {'Mo': [95.940, "Mo_RL_withPS_PZ.UPF"],
                 'S':  [32.065, "S.pz-hgh.UPF"       ]}

    qe.control['prefix'] = "'mos2'"
    qe.control['wf_collect'] = '.true.'
    qe.system['celldm(1)'] = a
    qe.system['celldm(3)'] = c/qe.system['celldm(1)']
    qe.system['ecutwfc'] = 20
    qe.system['occupations'] = "'fixed'"
    qe.system['nat'] = 3
    qe.system['ntyp'] = 2
    qe.system['ibrav'] = 4
    qe.system['lspinorb'] = '.true.'
    qe.system['noncolin'] = '.true.'
    qe.kpoints = [6, 6, 1]
    qe.electrons['conv_thr'] = 1e-8
    return qe

#scf
def scf():
    if not os.path.isdir('scf'):
        os.mkdir('scf')
    qe = get_inputfile()
    qe.control['calculation'] = "'scf'"
    qe.write('scf/mos2.scf')

#nscf
def nscf(kpoints,folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    qe = get_inputfile()
    qe.control['calculation'] = "'nscf'"
    qe.electrons['diago_full_acc'] = ".true."
    qe.electrons['conv_thr'] = 1e-8
    qe.system['nbnd'] = 40
    qe.system['force_symmorphic'] = ".true."
    qe.kpoints = kpoints
    qe.write('%s/mos2.nscf'%folder)

# create input files and folders
scf()
nscf([3,3,3], 'nscf')

if args.scf:
  print("running scf:")
  os.system("cd scf; pw.x -inp mos2.scf > scf.log")  #scf
  print("done!")
if args.nscf:
  print("running nscf:")
  os.system("cp -r scf/mos2.save nscf/") #nscf
  os.system("cd nscf; pw.x -inp mos2.nscf > nscf.log") #nscf
  print("done!")

# Copyright (C) 2015 Henrique Pereira Coutada Miranda, Alejandro Molina Sanchez
# All rights reserved.
#
# This file is part of yambopy
#
#
import os
import re
from math import sqrt

meVtocm = 8.06573

class DynmatIn():
    """ A class to generate an manipulate quantum espresso input files for matdyn.x
    """
    def __init__(self):
        self.variable = dict()
        self.qpoints     = [] 

    def write(self,filename):
        f = open(filename,'w')
        f.write(str(self))
        f.close()

    def __str__(self):
        s = '&input'
        s += self.stringify_group('',self.variable) #print variable
        if len(self.qpoints) > 0:
          s+=("%d\n"%len(self.qpoints))
          for q in self.qpoints:
            s+=("%12.8lf %12.8lf %12.8lf")%tuple(q[:3])+"\n"
        return s

    def __setitem__(self,key,value):
        self.variable[key] = value

    def __getitem__(self,key):
        return self.variable[key]

    def stringify_group(self, keyword, group):
        if group != {}:
            string='\n'
            for keyword in group:
                string += "%20s = %s\n" % (keyword, group[keyword])
            string += "/\n"
            return string
        else:
            return ''

"""
Convert a string in a float 
"""

def float_from_string(x):
  y=[]
  for t in x.split():
    try:
      y.append(float(t))
    except ValueError:
      pass
  return y

"""
Function to read the file matdyn.modes of quantum espresso and generate and array of phonon frequencies
It depends on how the file is written by QE. Be aware of possible changes in the output
"""
def reading_modes(name,natom,q):
  nphon = natom*3
  with open (name,'r') as myfile:
    data_phon = myfile.readlines()
  eig = []
  vec = []
  for j in xrange(q):
    frec    = []
    v_frec  = []
    for i in xrange(nphon):
      k=4 + j*(nphon*(natom+1)+5) + i*(natom+1)
      y = flo_str(data_phon[k])
      v_mode = []
      for ii in xrange(1,natom+1):
        z      = float_from_string(data_phon[k+ii])
        v_atom = array([complex(z[0],z[1]),complex(z[2],z[3]),complex(z[4],z[5])])
        v_mode.append(v_atom)
      v_frec.append(array(v_mode))
      frec.append(y[1])
    eig.append(frec)
    vec.append(array(v_frec))
  return eig, vec, nphon

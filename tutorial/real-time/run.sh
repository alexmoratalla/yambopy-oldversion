
#commands
cp -r scf/bn.save nscf/
cd nscf; mpirun -np 2 pw.x -nk 2 -inp bn.nscf > nscf.log
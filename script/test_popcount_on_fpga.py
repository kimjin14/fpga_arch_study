#!/usr/bin/python
"""
Take a verilog circuit and check if it can 
be embedded in given architecture.

@author: Jin Hee
"""

from pylab import *
import generate_architecture as genarch
import convert_cnf_for_fpga as cnfgen
import parse_output as parseout
import expand_to_SAT as expandSAT
import sys
sys.path.insert(0,'python')
import os
import subprocess as sub

#########################
# INPUT CIRCUIT 
#########################
if (len(sys.argv) < 2):
  CIRCUIT = "popcount2"
else:
  CIRCUIT = sys.argv[1] 

VSRC_PATH = "verilog/"
TFILE_PATH = "script/temp/"
OUTPUT_CNF_NAME = "circuits/circuit_on_xilinx.qdimacs"
OUTPUT_SAT_CNF_NAME = "circuits/expanded_SAT.dimacs"

if not os.path.isfile(VSRC_PATH + CIRCUIT + ".v"):
  print "Verilog file does not exist."
  sys.exit(0)

#########################
# TOOL PATHS
#########################
# - ODIN (Verilog to BLIF)
# - blif2cnf (BLIF to CNF)
# - convert_cnf_for_fpga (CNF ready for combining)
# - combine_cnf_with_fpga (combine)
# - run_qbf_solver (compute)
# - organize output
ODIN_PATH = "script/odin_II.exe"
BLIF2CNF_PATH = "script/blif2cnf.pl" 
QBF_PATH = "../rareqs/rareqs"
SAT_PATH = "../minisat-2.2/simp/minisat"

#########################
# Generate Architecture 
#########################
clause_list, config_te, fa, int_te, curr_var, in_list, out_list, int_list, config_list = \
  genarch.print_xilinx()
in_var = in_list[0]
out_var = out_list[0]

#########################
# Run ODIN   
#########################
if not os.path.isfile(ODIN_PATH):
  print "Path to ODIN is wrong."
  sys.exit(0)

p = sub.call([ODIN_PATH, \
  "-V" + VSRC_PATH  + CIRCUIT + ".v", \
  "-o" + TFILE_PATH + CIRCUIT + ".blif.pre"])

#########################
# Run blif2cnf
#########################
# BLIF cannot have certain characters
with open(TFILE_PATH + CIRCUIT + ".blif.pre") as fblifpre:
  with open(TFILE_PATH + CIRCUIT + ".blif", "w+") as fblif:
    for line in fblifpre:
      newline = line.replace("^", "_")
      fblif.write(newline.replace("~", "_"))

if not os.path.isfile(BLIF2CNF_PATH):
  print "Path to BLIF2CNF is wrong."
  sys.exit(0)

p = sub.call([BLIF2CNF_PATH, \
  "-m " + TFILE_PATH + CIRCUIT + ".fname", \
  TFILE_PATH + CIRCUIT + ".blif"])
os.rename(CIRCUIT + ".cnf", TFILE_PATH + CIRCUIT + ".cnf")

#########################
# Run convert cnf 
#########################
print "CONVERTING BLIF CNF TO CNF\n"
added_clause_list, added_int_te, added_int_list = \
  cnfgen.convert_cnf(in_var, out_var, curr_var, TFILE_PATH + CIRCUIT)
clause_list.extend(added_clause_list)
int_te = int_te + added_int_te
int_list.extend(added_int_list)
   
RUNSAT = 0
if RUNSAT == 1:
  #########################
  # Expand to SAT 
  #########################
  print "EXPAND TO SAT\n"
  expandSAT.convert_to_SAT(in_list, int_list, clause_list, OUTPUT_SAT_CNF_NAME)

  #########################
  # Run SAT Solver 
  #########################
  #print "SAT SOLVER\n"
  #p = sub.call([SAT_PATH, OUTPUT_SAT_CNF_NAME, "output_sat.log"])

  #########################
  # Parse Solver Output
  #########################
  #print "PARSE OUTPUT\n"
  #parseout.parse_minisat_output(config_list, TFILE_PATH + "output_256.log")
  
else :
  #########################
  # Combine 
  #########################
  with open (OUTPUT_CNF_NAME, "w+") as ocnf: 
    ocnf.write("p " + str(int_list[len(int_list)-1]) + " " + str(len(clause_list)) + "\n")
    ocnf.write(config_te + " 0\n")
    ocnf.write(fa + " 0\n")
    ocnf.write(int_te + " 0\n")
    for clause in clause_list:
      ocnf.write(clause + "\n")
  
  #########################
  # Run QBF Solver
  #########################
  f = open("output.log", "w")
  p = sub.call([QBF_PATH, OUTPUT_CNF_NAME], stdout=f)
  print "\n*QBF Solver: " + QBF_PATH + " " + OUTPUT_CNF_NAME
  
  #########################
  # Parse Solver Output
  #########################
  parseout.parse_rareqs_output(config_list, "output.log")

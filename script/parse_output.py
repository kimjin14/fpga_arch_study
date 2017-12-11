#!/usr/bin/python
"""
Parse output to show LUT and MUX configurations chosen by the QBF solver.

@author: Jin Hee  
"""

from pylab import *
import sys
sys.path.insert(0, 'python')
import os

def parse_minisat_output(config_list, sat_assignment_file):
  
  ####################################################
  # For each literal, organize the QBF solver output.
  ####################################################
  #LUT5 = 169
  #LUT6 = 433
  #INPUT_MUX = 49  
  #N_INPUT_MUX = 24
  #INPUT_MUX_SIZE = 5
  #OUTPUT_MUX = 445
  #N_OUTPUT_MUX = 8
  #OUTPUT_MUX_SIZE = 3 
  
  sat_assignment_dict = {}
  
  for config_type in config_list:
    print config_type
    print config_list[config_type]
    print "\n"

  with open(sat_assignment_file) as fsat:
    parse = 0
    for line in fsat:
      if "UNSAT" in line:
        print "UNSAT"
        exit(0)
      if parse == 1:  
        sat_assignment = line.split()
        for i in sat_assignment:
          literal = int(i)
          if (literal < 0):
            sat_assignment_dict[abs(literal)] = 0
          else:
            sat_assignment_dict[abs(literal)] = 1
      if "SAT" in line:
        parse = 1
        print "SAT"

  for config_type in config_list:
    print config_type
    if config_type == "lut":
      print "TEST\n"
      for config_per_lut in config_list[config_type]:
        for config_per_lut_per_output in config_per_lut:
          for lit in config_per_lut_per_output:
            print str(sat_assignment_dict[lit]),
          print "\n"
        print "\n"
    elif config_type == "ixbar":
      for i in range(28):
        temp = 0
        bit = 0
        for j in range(5):
          bit = sat_assignment_dict[config_list[config_type][i*5 + j]]
          temp = (bit << j) | temp;
        print temp,
      print "\n"
          
 #       for i in range(N_INPUT_MUX):
 # temp = 0
 # bit = 0
 # for j in range(INPUT_MUX_SIZE):
 #   bit = sat_assignment_dict[INPUT_MUX + i*INPUT_MUX_SIZE + j]
 #   temp = (bit << j) | temp;
 # print temp+1, 
#print "\n"
#  print "\n"
        
    else:
      for lit in config_list[config_type]:
        if lit in sat_assignment_dict:
          print str(sat_assignment_dict[lit]),
    print "\n"

  sys.exit(0)
def parse_rareqs_output (config_list, sat_assignment_file):
  
  ####################################################
  # For each literal, organize the QBF solver output.
  ####################################################
  #LUT5 = 169
  #LUT6 = 433
  #INPUT_MUX = 49  
  #N_INPUT_MUX = 24
  #INPUT_MUX_SIZE = 5
  #OUTPUT_MUX = 445
  #N_OUTPUT_MUX = 8
  #OUTPUT_MUX_SIZE = 3 
  
  sat_assignment_dict = {}
  
  for config_type in config_list:
    print config_type
    print config_list[config_type]
    print "\n"

  with open(sat_assignment_file) as fsat:
    for line in fsat:
      if "s cnf 0" in line:
        print "UNSAT"
        exit(0)
      if "V " in line:
        sat_assignment = line.split()
        sat_assignment.pop(0)
        for i in sat_assignment:
          literal = int(i)
          if (literal < 0):
            sat_assignment_dict[abs(literal)] = 0
          else:
            sat_assignment_dict[abs(literal)] = 1

  for config_type in config_list:
    print config_type
    if config_type == "lut":
      for config_per_lut in config_list[config_type]:
        for config_per_lut_per_output in config_per_lut:
          for lit in config_per_lut_per_output:
            print str(sat_assignment_dict[lit]),
          print "\n"
        print "\n"
    else:
      for lit in config_list[config_type]:
        print str(sat_assignment_dict[lit]),
    print "\n"

  sys.exit(0)

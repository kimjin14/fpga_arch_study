#!/usr/bin/python
"""
Convert given QBF problem with the "configuration" and "input" info to SAT instances
Configuration stays the same.
Input gets replaced with either 0 or 1
Intermediate values are assigned new variables

@author: Jin Hee  
"""

from pylab import *
import sys
sys.path.insert(0, 'python')
import os

### Get bit value given the position in a number ###
def get_bit(n, idx):
  return ((n&(1<<int(idx)))!=0);

### Get current combination and decide whether it is redundant ###
def check_redundancy(comb):
  return 1;

def convert_to_SAT (in_list, int_list, clause_list, output_file_name):

  intsize = len(int_list)
  intmap = {}
  for i in range(len(int_list)):
    intmap[int_list[i]] = i + int_list[len(int_list)-1] + 1 
  probsize = 1024 

  with open (output_file_name, "w+") as ocnf:
    # For each combination of input, rewrite the clause
    new_clause_list = []
    for comb in range(1<<len(in_list)):
      
      # Check comb and if it's redundant, skip it
      if comb == probsize: 
        break
      print "COMB " + str(comb) + " at " + str(intmap[533]+intsize*(comb-1)) + " set of vars."
      # For each clause, 
      #   if you find an intermediate signal, replace it with the next big val
      #   if you find an input, replace it with the correct constant
      #     if input is - and it should be 0, the clause should be removed
      #     if input is + and it should be 0, the literal should be removed
      #     if input is - and it should be 1, the literal should be removed
      #     if input is + and it should be 1, the clause should be removed
      for c in clause_list:
        #new_clause_list.append(c)
        #continue
        c = " " + c
        write_flag = 1
        for j in int_list:
          if comb == 0:
            c = c.replace(" " + str(j) + " ", " " + str(j) + " ")
            c = c.replace(" -" + str(j) + " ", " -" + str(j) + " ")
          else:
            c = c.replace(" " + str(j) + " ", " " + str(intmap[j]+intsize*(comb-1)) + " ")
            c = c.replace(" -" + str(j) + " ", " -" + str(intmap[j]+intsize*(comb-1)) + " ")
        for i in in_list:
          polarity = get_bit(comb, i-1)
          if not polarity: # 0
            if c.find(" -" + str(i) + " ") > -1:
              write_flag = 0
          else: # 1
            if c.find(" " + str(i) + " ") > -1:
              write_flag = 0
          c = c.replace(" " + str(i) + " ", " ")
          c = c.replace(" -" + str(i) + " ", " ")

        if write_flag == 1:
          new_clause_list.append(c)

    ocnf.write("p cnf " + str(int_list[len(int_list)-1] + intsize*(probsize-1)) +  " " + \
      str(len(new_clause_list)) + "\n")
    for c in new_clause_list:
      ocnf.write(c + "\n") 


#!/usr/bin/python
"""
Converts BLIF from ODINII for QBF solver.

@author: Jin Hee  
"""

from pylab import *
from itertools import *

import sys
sys.path.insert(0, 'python')
import os


class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences
def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1

def unique_permutations(elements,n):
  eset = set(elements)
  list_unique = [unique_element(i,elements.count(i)) for i in eset]
  u = len(elements)
  return perm_unique_helper(list_unique,[0]*u,u-1)

def convert_cnf_and_expand(in_var, out_var, curr_var, circuit):
  blif_file = circuit + ".blif"
  name_map_file = circuit + ".fname"
  cnf_file = circuit + ".cnf" 
 
  # FULL XILINX SLICE
  input_flag = 0
  output_flag = 0
  multiline_flag = 0
 
  var_map = {}
  int_te = ""
  int_list = []
  var_map_input = []

  # Parse from .blif file for the names of the input/output signals 
  # input_names and output_names contain list of names assigned
  #   from Verilog
  with open(blif_file) as fblif:
    for line in fblif:
      split_line = line.split()
      if 'inputs' in line:
        input_flag = 1
        input_names = split_line
      if 'outputs' in line:
        output_flag = 1 
        output_names = line.split()  
      if multiline_flag == 1:
        multiline_flag = 0
        if input_flag == 1:
          input_names.extend(split_line)
        if output_flag == 1:
          output_names.extend(split_line)
      if len(split_line) > 2:
        if split_line[len(split_line)-1] == "\\":
          multiline_flag = 1        
          split_line.pop(len(split_line)-1)
  
  input_names.pop(0)    
  output_names.pop(0)    
  
  # All of the names are mapped to literals by a different tool
  # Literals must match architecture
  with open (name_map_file) as fname:
    for line in fname:
      (name,key) = line.split()
      if name in input_names:
        var_map[int(key)] = in_var
        var_map_input.append(int(key))
        in_var = in_var + 1
      elif name in output_names:
        var_map[int(key)] = out_var
        out_var = out_var + 1
      else:
        var_map[int(key)] = curr_var
        int_te = int_te + str(curr_var) + " "
        int_list.append(curr_var)
        curr_var = curr_var + 1 
 
  # Remap all clauses with the correct literals
  old_clause_list = []
  perm_count = 0
  with open(cnf_file) as fcnf:
    for clause in fcnf:
      old_clause_list.append(clause)


  clause_list = [[] for i in range(len(old_clause_list))]

  # Consider all permutations of assigning circuit variables (cv) to architecture variable (av)

  # Boolean Function Symmetry
  # For now, you need to specify previously what the symmetries are
  # A = 1 2
  # B = 3 4
  # c = 5 6
  # D = 7 8 9 10 ... 28
  
  a = [1,2]
  b = [3,4]
  c = [5,6]
  d = [7,8]
  e = [9,10]
  f = [11,12]
  g = [13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]

  h = [a,b,c,d,e,f]
  i = [g]
 
  count = 0 

  print count

  sys.exit(0)

  #for cv in permutations([1,2,3,4,5,6,7,8,9,10,11,12,\
  #  13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28], 28):
  for cv in unique_permutations(['a','a','b','b','c','c','d','d','e','e','f',\
    'f','g','g','g','g','g','g','g','g','g','g','g','g','g','g','g'], 28):
  #for cv in combinations(['a','a','b','b','c','c','d','d','e','e','f',\
  #  'f','g','g','g','g','g','g','g','g','g','g','g','g','g','g','g'], 28):

    print cv
    
    ai = 0
    bi = 0
    ci = 0
    di = 0
    ei = 0
    fi = 0
    gi = 0
   
    av = 28*[0]
    for i in range(len(cv)):
      if cv[i] == 'a':
        av[i] = a[ai]
        ai = ai + 1 
      if cv[i] == 'b':
        av[i] = b[bi]
        bi = bi + 1 
      if cv[i] == 'c':
        av[i] = c[ci]
        ci = ci + 1 
      if cv[i] == 'd':
        av[i] = d[di]
        di = di + 1 
      if cv[i] == 'e':
        av[i] = e[ei]
        ei = ei + 1 
      if cv[i] == 'f':
        av[i] = f[fi]
        fi = fi + 1 
      if cv[i] == 'g':
        av[i] = g[gi]
        gi = gi + 1 
    # First Order Architecture Symmetry
    # This assumes LUT config can change given same input variables
    if av[0] > av[1] or av[1] > av[2] or av[2] > av[3] or av[3] > av[4]:
      continue
    if av[7] > av[8] or av[8] > av[9] or av[9] > av[10] or av[10] > av[11]:
      continue
    if av[14] > av[15] or av[15] > av[16] or av[16] > av[17] or av[17] > av[18]:
      continue
    if av[21] > av[22] or av[22] > av[23] or av[23] > av[24] or av[24] > av[25]:
      continue
    
    #print av
    #if (perm_count > 40):
    #  break

   # i = 0
   # for key in var_map_input:
   #   var_map[key] = av[i]
   #   i = i + 1
   #   
   # for iclause in range(len(old_clause_list)):
   #   if "p" in old_clause_list[iclause] or "c" in old_clause_list[iclause]:
   #     continue
   #   literals = old_clause_list[iclause].split()
   #   new_clause = ""
   #   for i in literals:
   #     n = int(i)
   #     if (n == 0):
   #       new_clause = new_clause + "0"
   #     elif (n < 0):
   #       new_clause = new_clause + "-" + str(var_map[abs(n)]) + " "
   #     else:
   #       new_clause = new_clause + str(var_map[abs(n)]) + " "
   #   clause_list[iclause].append(new_clause)
    perm_count = perm_count + 1

  print perm_count
  #print clause_list

  print "Printing Var Map\n"
  print var_map
  return clause_list, int_te, int_list; 

###################################################################
# Read from the .cnf file line by line
# Change the variable starting # to the appropriate one
#
# 1. Find the input and output names from the blif file
# 2. Match the name to the variable name from the fname file
# With more time, look at the .blif, name mapping, and report .cnf I/O variable #
###################################################################

def convert_cnf(in_var, out_var, curr_var, circuit):
  blif_file = circuit + ".blif"
  name_map_file = circuit + ".fname"
  cnf_file = circuit + ".cnf" 
 
  # FULL XILINX SLICE
  input_flag = 0
  output_flag = 0
  multiline_flag = 0
 
  var_map = {}
  int_te = ""
  int_list = []
  var_map_input = []
  clause_list = []

  # Parse from .blif file for the names of the input/output signals 
  # input_names and output_names contain list of names assigned
  #   from Verilog
  with open(blif_file) as fblif:
    for line in fblif:
      split_line = line.split()
      if 'inputs' in line:
        input_flag = 1
        input_names = split_line
      if 'outputs' in line:
        output_flag = 1 
        output_names = line.split()  
      if multiline_flag == 1:
        multiline_flag = 0
        if input_flag == 1:
          input_names.extend(split_line)
        if output_flag == 1:
          output_names.extend(split_line)
      if len(split_line) > 2:
        if split_line[len(split_line)-1] == "\\":
          multiline_flag = 1        
          split_line.pop(len(split_line)-1)
  
  input_names.pop(0)    
  output_names.pop(0)    
  
  # All of the names are mapped to literals by a different tool
  # Literals must match architecture
  with open (name_map_file) as fname:
    for line in fname:
      (name,key) = line.split()
      if name in input_names:
        var_map[int(key)] = in_var
        in_var = in_var + 1
      elif name in output_names:
        var_map[int(key)] = out_var
        out_var = out_var + 1
      else:
        var_map[int(key)] = curr_var
        int_te = int_te + str(curr_var) + " "
        int_list.append(curr_var)
        curr_var = curr_var + 1 
 
  # Remap all clauses with the correct literals
  old_clause_list = []
  perm_count = 0
  with open(cnf_file) as fcnf:
    for clause in fcnf:
      old_clause_list.append(clause)

  for iclause in range(len(old_clause_list)):
    if "p" in old_clause_list[iclause] or "c" in old_clause_list[iclause]:
      continue
    literals = old_clause_list[iclause].split()
    new_clause = ""
    for i in literals:
      n = int(i)
      if (n == 0):
        new_clause = new_clause + "0"
      elif (n < 0):
        new_clause = new_clause + "-" + str(var_map[abs(n)]) + " "
      else:
        new_clause = new_clause + str(var_map[abs(n)]) + " "
    clause_list.append(new_clause)

  print "Printing Var Map\n"
  print var_map
  return clause_list, int_te, int_list; 

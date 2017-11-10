#!/usr/bin/python
"""
Generates CNF for miniSAT of MUX/LUT given the input numbers.
Use it by changing the input range and output range.

@author: Jin Hee  
"""

from collections import namedtuple
from pylab import *
import sys
sys.path.insert(0, 'python')
import os
import math

## Get bit value given the position in a number
def get_bit(n, idx):
  return ((n&(1<<int(idx)))!=0);

def print_xor2(i1,i2,o):

  clause_list = []

  clause_list.append(str(-i1) + " " + str(-i2) + " " + str(-o) + " 0")
  clause_list.append(str(i1) + " " + str(i2) + " " +  str(-o) + " 0")
  clause_list.append(str(-i1) + " " +  str(i2) + " " +  str(o) + " 0")
  clause_list.append(str(i1) + " " +  str(-i2) + " " +  str(o) + " 0")

  return clause_list;

def print_mux2_constant(i, s, o):

  clause_list = []
  
  clause_list.append(str(s) + " " + "-" + str(i) + " " + str(o) + " 0")
  clause_list.append(str(s) + " " + str(i) + " " + "-" + str(o) + " 0")
  clause_list.append("-" + str(s) + " " + str(o) + " 0")

  return clause_list;

###################################################################
# For printing LUT or MUX 
#   must give list of input/select signals
###################################################################
def print_mux_list(n_input, n_select, i, s, o):

  clause_list = []

  lut_input_list = i
  lut_select_list = s 
  lut_o = o
  
  for i in range(1<<n_select):
    if (i < n_input):
      for repeat in range(2):
        clause = ""
        for b in range(n_select):
          if (get_bit(i,b) == 0):
            clause = clause + str(lut_select_list[b]) + " "
          else:
            clause = clause + "-" + str(lut_select_list[b]) + " "
        if (repeat == 0):
          clause = clause + "-" + str(lut_input_list[i]) + " "
          clause = clause + str(lut_o) + " 0"
        else:
          clause = clause + str(lut_input_list[i]) + " "
          clause = clause + "-" + str(lut_o) + " 0"
        clause_list.append(clause)
    else:
      clause = ""
      for b in range(n_select):
        if (get_bit(i,b) == 0):
          clause = clause + str(lut_select_list[b]) + " "
        else:
          clause = clause + "-" + str(lut_select_list[b]) + " "
      clause = clause + " 0"  
      clause_list.append(clause)

  return clause_list; 

###################################################################
# For creating Xilinx Slice 
###################################################################
ConfigStruct = namedtuple("ConfigStruct", "field1 field2 field3 field4 field5 field6")
def print_xilinx():

  # Keep track of all variables (total length should equal currvar at the end)
  #   external refers to variables attached to circuit (before xbar)
  #   internal refers to variables attached to architecture (after xbar)
  num_of_xlut = 4
  einput_size = 28
  input_sel_size = int(math.ceil(math.log(einput_size,2)))
  input_size = einput_size/num_of_xlut
  lut_size = 5
  lut_output_size = 2
  config_size = 1<<lut_size
  output_size = 8
  output_sel_size = int(math.ceil(math.log(output_size,2)))
  
  input_external = []
  input_internal = [[] for x in xrange(num_of_xlut)]

  output_external = [] 
  output_lut = [[] for x in xrange(num_of_xlut)]
  output_6lut = []
  output_8lut = []
  output_cout = []
  output_sum = []
  output_mux = []

  config_list = {}
  config_list["uinput"] = [[[] for x in xrange(lut_output_size)] for x in xrange(num_of_xlut)]
  config_list["lut"] = [[[] for x in xrange(lut_output_size)] for x in xrange(num_of_xlut)]
  config_list["lut6"] = []
  config_list["ixbar"] = []
  config_list["adder"] = []
  config_list["omux"] = []
  config_list["oxbar"] = []
  config_list["cin"] = []

  intermediate_list = []
  cin = []
  
  clause_list = []

  currvar = 1 
  
  # INPUT CROSSBAR
  # - input exteral, input xbar select, input internal
  for i in range (einput_size):
    input_external.append(currvar + i)

  for a in range (num_of_xlut):
    for i in range (input_size):
      input_internal[a].append(currvar + einput_size + input_size*a + i)
      intermediate_list.append(currvar + einput_size + input_size*a + i)
    for i in range (input_size):
      select_temp = []
      for j in range (input_sel_size):
        select_temp.append(currvar + einput_size*2 + input_size*input_sel_size*a + \
          input_sel_size*i + j)
      if i < 6:
        clause_list.extend(print_mux_list(einput_size - i%5 + 1, input_sel_size, 
          [currvar + einput_size*(2 + input_sel_size) + input_size*a + i] + input_external, \
          select_temp, input_internal[a][i]))
      else:
        clause_list.extend(print_mux_list(einput_size + 1, input_sel_size, \
          [currvar + einput_size*(2 + input_sel_size) + input_size*a + i] + input_external, \
          select_temp, input_internal[a][i]))
      config_list["ixbar"].extend(select_temp)
      config_list["uinput"].append(currvar + einput_size*(2 + input_sel_size) + input_size*a + i)
  
  currvar = currvar + einput_size*3 + input_sel_size*einput_size

#      input_internal[a].append(currvar + input_size*a + i)
#  currvar = currvar + einput_size

  # FOUR 5-to-1 LUT
  # - input internal, lut config, lut output
  for a in range (num_of_xlut):
    for i in range (lut_output_size):
      output_lut[a].append(currvar + lut_output_size*a + i)
      intermediate_list.append(currvar + lut_output_size*a + i)
  
  for a in range (num_of_xlut):
    for o in range (lut_output_size):
      select_temp = []
      for i in range (config_size):
        select_temp.append(currvar + num_of_xlut*lut_output_size + \
          (lut_output_size*config_size)*a + config_size*o + i)
      clause_list.extend(print_mux_list(config_size, lut_size, select_temp, \
        input_internal[a], output_lut[a][o]))
      config_list["lut"][a][o].extend(select_temp)
   
  currvar = currvar + num_of_xlut*lut_output_size + num_of_xlut*lut_output_size*config_size 

  # 6-to-1 LUT
  # - input internal/constant, mux config, intermediate wire
  for a in range (num_of_xlut):
    clause_list.extend(print_mux2_constant(input_internal[a][5], currvar + a, \
      currvar + num_of_xlut + a))
    clause_list.extend(print_mux_list(2, 1, output_lut[a], [currvar + num_of_xlut + a], \
      currvar + num_of_xlut*2 + a))
    config_list["lut6"].append(currvar + a)
    intermediate_list.append(currvar + num_of_xlut + a)
    intermediate_list.append(currvar + num_of_xlut*2 + a)
    output_6lut.append(currvar + num_of_xlut*2 + a)

  currvar = currvar + 3*num_of_xlut

  # ADDER (2 2-to-1 MUX and an XOR)
  for a in range (num_of_xlut):
    clause_list.extend(print_mux_list(2, 1, [input_internal[a][6], output_lut[a][0]], \
      [currvar + a], currvar + num_of_xlut + a))
    if a == 0:
      clause_list.extend(print_mux_list(2, 1, [currvar + num_of_xlut + a, currvar + num_of_xlut*4], \
        [output_6lut[a]], currvar + num_of_xlut*2 + a))
      clause_list.extend(print_xor2(currvar + num_of_xlut*4, output_6lut[a], \
        currvar + num_of_xlut*3 + a))
    else:
      clause_list.extend(print_mux_list(2, 1, [currvar + num_of_xlut + a, output_cout[a-1]], \
        [output_6lut[a]], currvar + num_of_xlut*2 + a))
      clause_list.extend(print_xor2(output_cout[a-1], output_6lut[a], currvar + num_of_xlut*3 + a))
    output_cout.append(currvar + num_of_xlut*2 + a)
    output_sum.append(currvar + num_of_xlut*3 + a)
    intermediate_list.append(currvar + num_of_xlut + a)
    intermediate_list.append(currvar + num_of_xlut*2 + a)
    intermediate_list.append(currvar + num_of_xlut*3 + a)
    config_list["adder"].append(currvar + a)
  config_list["cin"].append(currvar + 4*num_of_xlut)

  cin = currvar + 4*num_of_xlut
  currvar = currvar + 4*num_of_xlut + 1

  # 8-to-1 MUX 
  clause_list.extend(print_mux_list(2, 1, [output_6lut[0], output_6lut[1]], \
    [input_internal[0][6]], currvar))
  clause_list.extend(print_mux_list(2, 1, [output_6lut[2], output_6lut[3]], \
    [input_internal[2][6]], currvar + 1))
  clause_list.extend(print_mux_list(2, 1, [currvar, currvar + 1], \
    [input_internal[1][6]], currvar + 2))
  output_8lut.extend([currvar, currvar + 1, currvar + 2])
  intermediate_list.extend([currvar, currvar + 1, currvar + 2])
  
  currvar = currvar + 3

  # MUXED OUTPUT
  for a in range (num_of_xlut):
    select_temp = []
    for i in range (3):
      select_temp.append(currvar + a*3 + i)
    if a != 3:
      clause_list.extend(print_mux_list(5, 3, \
        [output_lut[a][0], output_6lut[a], output_cout[a], output_sum[a], output_8lut[a]],
        select_temp, currvar + num_of_xlut*3 + a))
    else:
      clause_list.extend(print_mux_list(4, 3, \
        [output_lut[a][0], output_6lut[a], output_cout[a], output_sum[a]],
        select_temp, currvar + num_of_xlut*3 + a))
    config_list["omux"].extend(select_temp)
    output_mux.append(currvar + num_of_xlut*3 + a)
    intermediate_list.append(currvar + num_of_xlut*3 + a)

  currvar = currvar + num_of_xlut*4
  
  # OUTPUT CROSSBAR
  # - output from previous step and 6 lut output
  for a in range (output_size):
    select_temp = []
    for i in range (output_sel_size):
      select_temp.append(currvar + a*output_sel_size + i)
    clause_list.extend(print_mux_list(output_size, output_sel_size, output_6lut + output_mux, \
      select_temp, currvar + output_size*output_sel_size + a))
    output_external.append(currvar + output_size*output_sel_size + a)
    intermediate_list.append(currvar + output_size*output_sel_size + a)
    config_list["oxbar"].extend(select_temp)
  
  currvar = currvar + output_size*output_sel_size + output_size

  config_te = "e " 
  for a in range(num_of_xlut):
    for i in range(lut_output_size):
      for j in range(len(config_list["lut"][a][i])):
        config_te = config_te + str(config_list["lut"][a][i][j]) + " "
  for i in range(len(config_list["lut6"])):
    config_te = config_te + str(config_list["lut6"][i]) + " "
  for i in range(len(config_list["ixbar"])):
    config_te = config_te + str(config_list["ixbar"][i]) + " "
  for i in range(len(config_list["adder"])):
    config_te = config_te + str(config_list["adder"][i]) + " "
  for i in range(len(config_list["omux"])):
    config_te = config_te + str(config_list["omux"][i]) + " "
  for i in range(len(config_list["oxbar"])):
    config_te = config_te + str(config_list["oxbar"][i]) + " "
 
  fa ="a "
  for i in range(len(input_external)):
  #for i in range(16):
    fa = fa + str(input_external[i]) + " "

  int_te = "e "
  #for i in range(12):
  #  int_te = int_te + str(input_external[i+16]) + " "
  for a in range(num_of_xlut):
    for i in range(len(input_internal[a])):
      int_te = int_te + str(input_internal[a][i]) + " "
  for i in range(len(intermediate_list)):
    int_te = int_te + str(intermediate_list[i]) + " "
  #for a in range(num_of_xlut):
  #  for i in range(len(output_lut[a])):
  #    int_te = int_te + str(output_lut[a][i]) + " "
  #for i in range(len(output_6lut)):
  #  int_te = int_te + str(output_6lut[i]) + " "
  #for i in range(len(output_cout)):
  #  int_te = int_te + str(output_cout[i]) + " "
  #for i in range(len(output_sum)):
  #  int_te = int_te + str(output_sum[i]) + " "
  #for i in range(len(output_8lut)):
  #  int_te = int_te + str(output_8lut[i]) + " "
  #for i in range(len(output_mux)):
  #  int_te = int_te + str(output_mux[i]) + " "
  #for i in range(len(output_external)):
  #  int_te = int_te + str(output_external[i]) + " "

  return clause_list, config_te, fa, int_te, currvar, input_external, output_external, intermediate_list, config_list; 

###################################################################
# Main program
###################################################################
def main():

  # print xilinx architecture
  print_xilinx()
  

if __name__ == "__main__":
  main()


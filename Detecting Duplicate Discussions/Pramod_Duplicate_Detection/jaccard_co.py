#!/usr/bin/python
from __future__ import division
import codecs
import json
import nltk
import re
import os
import subprocess

with open("discussions.thorn") as thorn_file:
         disc_list=[]
         disc_str = ""
         j_co_mat = []
         i = 0
         l=0
         j_co = 0
         while 1:
               char = thorn_file.read(1)
               disc_str += char
               if (char == "þ"):
                  disc_str=disc_str.replace(char,"")
                  disc_str = re.sub('[^a-zA-Z0-9\.]','',disc_str)
                  disc_list.append(disc_str)
                  disc_str = ""
               if not char: break
                
         for i in range(len(disc_list)-1):
             j=i
             while(j<len(disc_list)-1):
                  str_1 = disc_list[i]
                  str_2 = disc_list[j+1]
                  cnt_inter = 0
                  cnt_union = 0
                  if (str_1 == str_2):
                     j_co = 1
                     j_co_mat.append([i+1,j+2,j_co])
                     j = j+1
                  else:
                       output = subprocess.run("""bash -c 'diff -u <(echo '%s'| fold -w1) <(echo '%s' | fold -w1)'""" %(str_1,str_2) ,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
                       diff_str = output.stdout;
                       for dif in diff_str.splitlines():
                           if re.match('^\s.$',dif) is not None:
                              cnt_inter = cnt_inter+1
                           if re.match('^\s.$',dif) or re.match('^[+-].$',dif) is not None:
                              cnt_union = cnt_union+1

                       j_co=(cnt_inter)/(cnt_union)
                       j_co_mat.append([i+1,j+2,j_co])
                       j=j+1
         j_co_mat=sorted(j_co_mat,key=lambda listed :listed[2],reverse=True)
         for k in range(len(j_co_mat)):
             print(j_co_mat[k])

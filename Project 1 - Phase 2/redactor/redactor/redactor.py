#!/usr/bin/python
import sys
import subprocess
import re
import glob
import nltk
import PyPDF2
import os
import datefinder
from collections import defaultdict
from nltk.tag import StanfordNERTagger
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from itertools import chain
from nltk.corpus import wordnet
from nltk import sent_tokenize
from nltk import word_tokenize
from bs4 import BeautifulSoup
from nltk.chunk.util import (ChunkScore, accuracy, tagstr2tree, conllstr2tree,
                             conlltags2tree, tree2conlltags, tree2conllstr, tree2conlltags,
                             ieerstr2tree)
from nltk.chunk.regexp import RegexpChunkParser, RegexpParser
from nltk import ne_chunk
from nltk import pos_tag
from astropy.table import Table, Column


stat_data = []

def redact_dates(content,file_name):
    dates_list = []
    matches = datefinder.find_dates(content, source = True)
    for match in matches:
        dates_list.append(match[1])
    for n in dates_list:
        content = content.replace(n,'*'*len(n))
        stat_data.append([n,len(n),file_name,"dates"])
    #print(content)
    return content

def redact_address(content,file_name):
    addresses_re =  re.compile("[0-9]{1,4} .+,? .+,? [A-Z]{2,15} [0-9]{5}", re.IGNORECASE)
    addresses = addresses_re.findall(content)
    for n in addresses:
        content = content.replace(n,'*'*len(n))
        stat_data.append([n,len(n),file_name,"address"])
    #print(content)
    return content

def redact_phones(content,file_name):
    phones_re = re.compile("\(?\d{3}\)?\d{7}|\+?\d?-?\d{3}-\d{3}-\d{4}|\+?\d{2}?-?\d{3}-?\d{3}-?\d{2}-?\d{2}|\+?\d{2}?-?\d{3}\s\d{7}|\+?\d\s?\(?\d{3}\)?\s\d{2}\s\d{2}\s\d{3}|\+?\d\s?\(?\d{3}\)?\s\d{2}-?\d{2}\s\d{3}|\+?\d{2}?\.?\d{3}\.?\d{3}\.?\d{4}|\+?\d?\/\d{3}\/\d{3}\/\d{4}|\+?\d{2}?\d{10}", re.IGNORECASE)
    phones = phones_re.findall(content)
    for n in phones:
        content = content.replace(n,'*'*len(n))
        stat_data.append([n,len(n),file_name,"phones"])
    #print(content)
    return content


def redact_concept(content,concept):
    cont_sent = nltk.sent_tokenize(content)
    syn_word = wordnet.synsets(concept)
    syn_concept = set(chain.from_iterable([word.lemma_names() for word in syn_word]))
    for sent in cont_sent:
        if any(item in sent.lower() for item in syn_concept):
           content = content.replace(sent,'*'*len(sent))
    return content

def redact_gender(content,file_name):
    gender_list = ['him','her','himself','herself','male','female','his','she','Actor','Actress','Author','Authoress','Bachelor','Spinster','Boy','Girl','Boy Scout','Girl Guide','Brave','Squaw','Bridegroom','Bride','Brother','Sister','Conductor','Conductress','Count','Countess','Czar','Czarina','Dad','Mom','Daddy','Mummy','Duke','Duchess','Emperor','Empress','Father','Mother','Father-in-law','Mother-in-law','Fiance','Fiancee','Gentleman','Lady','Gaint','Gaintess','God','Goddess','Governor','Matron','Grandfather','Grandmother','Headmaster','Headmistress','Heir','Heiress','Hero','Heroine','Host','Hostess','Hunter','Huntress','Husband','Wife','King','Queen','Lad','Lass','Landlord','Landlady','Lord','Lady','Man','Woman','Manager','Manageress','Manservant','Maidservant','Master','Mistress','Mayor','Mayoress','Milkman','Milkmaid','Millionaire','Millionairess','Monitor','Monitrice','Monk','Nun','Murderer','Murderess','Negro','Negress','Nephew','Niece','Papa','Mama','Poet','Poetess','Postman','Postwoman','Postmaster','Postmistress','Priest','Priestess','Prince','Princess','Prophet','Prophetess','Proprietor','Proprietress','Protector','Protectress','Shepherd','Shepherdess','Sir','Madam','Son','Daughter','Son-in-law','Daughter-in-law','Step-father','Step-mother','Step-son','Step-mother','Steward','Stewardess','Sultan','Sultana','Tailor','Tailoress','Uncle','Aunt','Waiter','Waitress','Washerman','Washerwoman','Widower','Widow','Wizard','Witch']
    #print(content.find("he"))
    for word in content.split():
        word = re.sub('[,\.]','',word)
        for g in gender_list:
            if word.lower() == g.lower() and re.match('^'+re.escape(word.lower())+'$',g.lower()) is not None:
               #gender_list = ([word,len(word),file_name])
               content = content.replace(word, '*'*len(word))
               stat_data.append([word,len(word),file_name,"genders"])
    he_re =  re.compile(r"\bhe\b", re.IGNORECASE|re.VERBOSE|re.MULTILINE)
    he_found = he_re.findall(content)
    for he in he_found:
        stat_data.append([he,len(he),file_name,"genders"])
    new_content = re.sub(r"\bhe\b","**",content)
    new_1_content = re.sub(r"\bHe\b","**",new_content)
    new_2_content = re.sub(r"\bHE\b","**",new_1_content)
    return new_2_content

def redact_name_loc(content,n_o_l,file_name):
    name_list=[]
    loc_list=[]
    """for sent in sent_tokenize(content):
        for chunk in ne_chunk(pos_tag(word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
               print(chunk.label(), ' '.join(c[0] for c in chunk.leaves()))
            #if hasattr(chunk, 'label') and chunk.label() == 'LOCATION' or chunk.label() == 'GPE':
             #  print(chunk.label(), ' '.join(c[0] for c in chunk.leaves()))"""
    st = StanfordNERTagger('stanford-ner-2016-10-31/classifiers/english.all.3class.distsim.crf.ser.gz','stanford-ner-2016-10-31/stanford-ner.jar',encoding='utf-8') 
    tokenized_cont = word_tokenize(content)
    cont_chunks = st.tag(tokenized_cont)
    for chunk in cont_chunks:
        if (chunk[1] == 'PERSON'):
           name_list.append(chunk[0])
        if (chunk[1] == 'LOCATION'):
           loc_list.append(chunk[0])

    if (n_o_l == "--names"):
        for n in name_list:
           content = content.replace(n,'*'*len(n))
           stat_data.append([n,len(n),file_name,"names"])
    if (n_o_l == "--places"):
        for n in loc_list:
           content = content.replace(n,'*'*len(n))
           stat_data.append([n,len(n),file_name,"places"])
    return content

def dict_form(content,word_list):
    dict_index = {}
    #dict_index = defaultdict(list)
    for word in set(word_list):
        for m in re.finditer(word,content):
            dict_index[m.group()]=[m.start(),m.end()]
    return(dict_index)

def search_tag(argv,tag):
    for s_tag in argv:
        if s_tag == tag:
           return 1
    return 0



if __name__ == "__main__":
  html_files=[]
  xml_files=[]
  text_files=[]
  argv_list = sys.argv
  indices = [i for i, x in enumerate(argv_list) if x == "--input"]
  for indice in indices:
      if argv_list[indice+1] == '*.html':
         html_files = glob.glob(argv_list[indice+1],recursive = True)
      match = re.search('txt', argv_list[indice+1])
      if match:
         text_files = glob.glob(argv_list[indice+1],recursive = True)
      #if argv_list[indice+1] == '*.xml':
         #xml_files = glob.glob(argv_list[indice+1],recursive = True)
  conc=''
  out_loc=''
  stat_status=''
  if search_tag(argv_list,"--output") == 1:
     for i in range(len(argv_list)):
         if argv_list[i] == "--output":
            out_loc = argv_list[i+1]
            subprocess.Popen("""mkdir %s""" %(out_loc) ,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if search_tag(argv_list,"--stats") == 1:
     for i in range(len(argv_list)):
         if argv_list[i] == "--stats":
            stat_status = argv_list[i+1]

  if len(html_files) == 0:
     print("There are no html files available")
  else: 
       for file_name in html_files:
           html_file_ptr = open(file_name,'r')
           html_file_cont = html_file_ptr.read()
           raw = BeautifulSoup(html_file_cont,'lxml')
           filedata = raw.text
           if search_tag(argv_list,"--concept") == 1:
              for i in range(len(argv_list)):
                  if argv_list[i] == "--concept":
                     conc = argv_list[i+1]
              filedata = redact_concept(filedata,conc)
           if search_tag(argv_list,"--genders") == 1:
              filedata = redact_gender(filedata,file_name)
           if search_tag(argv_list,"--dates") == 1:
              filedata = redact_dates(filedata,file_name)
           if search_tag(argv_list,"--phones") == 1:
              filedata = redact_phones(filedata,file_name)
           if search_tag(argv_list,"--addresses") == 1:
              filedata = redact_address(filedata,file_name)
           if search_tag(argv_list,"--names") == 1:
              filedata = redact_name_loc(filedata,"--names",file_name)
           if search_tag(argv_list,"--places") == 1:
              filedata = redact_name_loc(filedata,"--places",file_name)
           if search_tag(argv_list,"--output") == 1:
              temp_txt = "temp_redact.txt"
              with open(temp_txt,"w") as red_w:
                   red_w.write(filedata)
                   red_w.close()
              split_file_name = file_name.split('/')
              abs_file_name = split_file_name[len(split_file_name)-1]
              pdf_file_name = re.sub(r"\bhtml\b","",abs_file_name) + "pdf"
              pdf_file_name = out_loc + pdf_file_name
              #print(pdf_file_name)
              cmd = "cupsfilter "+temp_txt+" > "+pdf_file_name
              subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable = '/bin/bash', shell = True)
           #print(filedata)

  if len(text_files) == 0:
     print("There are no text files available in otherfiles directory")
  else:
       for file_name in text_files:
           txt_file_ptr = open(file_name,'r')
           filedata = txt_file_ptr.read()
           if search_tag(argv_list,"--concept") == 1:
              for i in range(len(argv_list)):
                  if argv_list[i] == "--concept":
                     conc = argv_list[i+1]
              filedata = redact_concept(filedata,conc)
           if search_tag(argv_list,"--genders") == 1:
              filedata = redact_gender(filedata,file_name)
           if search_tag(argv_list,"--dates") == 1:
              filedata = redact_dates(filedata,file_name)
           if search_tag(argv_list,"--phones") == 1:
              filedata = redact_phones(filedata,file_name)
           if search_tag(argv_list,"--addresses") == 1:
              filedata = redact_address(filedata,file_name)
           if search_tag(argv_list,"--names") == 1:
              filedata = redact_name_loc(filedata,"--names",file_name)
           if search_tag(argv_list,"--places") == 1:
              filedata = redact_name_loc(filedata,"--places",file_name)
           if search_tag(argv_list,"--output") == 1:
              temp_txt = "temp_redact.txt"
              with open(temp_txt,"w") as red_w:
                   red_w.write(filedata)
                   red_w.close()
              split_file_name = file_name.split('/')
              abs_file_name = split_file_name[len(split_file_name)-1]
              pdf_file_name = re.sub(r"\btxt\b","",abs_file_name) + "pdf"
              pdf_file_name = out_loc + pdf_file_name
              #print(pdf_file_name)
              cmd = "cupsfilter "+temp_txt+" > "+pdf_file_name
              subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable = '/bin/bash', shell = True)
  if search_tag(argv_list,"--stats") == 1:
     t = Table(rows=stat_data, names=('Redacted Term', 'Length', 'File', 'Type'))
     if(stat_status == "stdout"):
       #print("Redacted Term,Length,File,Type")
       #print("============= ====== ==== ====")
       #for row in t:
        #   print (row.as_void())
       print(t)
     if(stat_status == "stderr"):
       #from __future__ import print_function
       print(t, file=sys.stderr)
     else:
          stat_f = open(stat_status,"w")
          for row in t:
              stat_f.write(str(row.as_void()))
              stat_f.write("\n")
          stat_f.close()


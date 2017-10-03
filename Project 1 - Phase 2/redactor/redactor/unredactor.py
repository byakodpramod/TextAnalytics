#!/usr/bin/python 
# -*- coding: utf-8 -*-
import glob 
import io 
import os 
import pdb 
import sys
import nltk 
import re
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk import sent_tokenize 
from nltk import word_tokenize 
from nltk import pos_tag 
from nltk import ne_chunk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from nltk.tag import StanfordNERTagger
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier

stops = set(stopwords.words("english"))
name_dict_list = []
red_dict = []
total_name_list = []

def get_entity(text):
   name_list = []
   name_l_list = []
   name_r_list = []
   for sent in sent_tokenize(text):
       words = word_tokenize(sent)
       chunk = ne_chunk(pos_tag(words))
       for i in range(len(chunk)):
           #print(chunk[i])
           if hasattr(chunk[i], 'label') and chunk[i].label() == 'PERSON':
              name = (' '.join(c[0] for c in chunk[i].leaves()))
              name_list.append(name)
              if i-1 == 0:
                 name_l_list.append('')
              else:
                 if (hasattr(chunk[i-1], 'label') and chunk[i-1].label() == 'PERSON') or (hasattr(chunk[i-1], 'label') and chunk[i-1].label() == 'ORGANIZATION') or (hasattr(chunk[i-1], 'label') and chunk[i-1].label() == 'GPE'):
                    temp_left = (' '.join(c[0] for c in chunk[i-1].leaves()))
                    name_l_list.append(temp_left)
                 else:
                    name_l_list.append(chunk[i-1][0])
              if i+1 == len(chunk):
                 name_r_list.append('')
              else:
                 if (hasattr(chunk[i+1], 'label') and chunk[i+1].label() == 'PERSON') or (hasattr(chunk[i+1], 'label') and chunk[i+1].label() == 'ORGANIZATION') or (hasattr(chunk[i+1], 'label') and chunk[i+1].label() == 'GPE'):
                    temp_right = (' '.join(c[0] for c in chunk[i+1].leaves()))
                    name_r_list.append(temp_right)
                 else:
                    name_r_list.append(chunk[i+1][0])
   return(name_list,name_l_list,name_r_list)

def create_features(glob_text,red_name_list):
    for thefile in glob.glob(glob_text):
        with io.open(thefile, 'r', encoding='utf-8') as fyl:
             text = fyl.read()
             name_list,name_l_list,name_r_list=get_entity(text)
             for name,left,right in zip(name_list,name_l_list,name_r_list):
                 total_name_list.append(name)
                 temp_dict = {}
                 temp_dict["name"] = name
                 temp_dict["name_length"] = len(name)
                 space_count = re.findall(' ',name)
                 temp_dict["spaces"] = len(space_count)
                 temp_dict["left_w"] = left
                 temp_dict["right_w"] = right
                 name_dict_list.append(temp_dict)
    predict(red_name_list)


def predict(red_name_list):    
    vectorizer = DictVectorizer()
    train_data_features = vectorizer.fit_transform(name_dict_list).toarray()
    test_data_features = vectorizer.transform(red_dict).toarray()
    z = train_data_features
    x = test_data_features
    neigh = KNeighborsClassifier(n_neighbors=1)
    neigh.fit(z, total_name_list)
    pre = neigh.kneighbors(x, n_neighbors= 5,return_distance=False)
    
    for i,j in zip(range(len(pre)),range(len(red_name_list))):
        print("Top 5 predicted names for the redacted term "+red_name_list[j]+" are:")
        print("                                            "+'-'*len(red_name_list[j])+"     ")
        for j in range(len(pre[i])):
            print(total_name_list[pre[i][j]])
        print("\n")
    #for x,y in zip(red_name_list,predicted):
     #   print("input:::"+x,"predicted:::"+y)
    #print(z)


if __name__ == '__main__':
  if len(sys.argv) is 3:
     red_name_list = []
     red_name_r_list = []
     red_name_l_list = []
     if (sys.argv[1]):
        red_file = open(sys.argv[1],"r")
        red_data = red_file.read()
        #print(red_data)
        for sent in sent_tokenize(red_data):
            words = word_tokenize(sent)
            for i in range(len(words)):
                if i-1 is not 0 and (words[i-1] == '*'*len(words[i-1])):
                   red_name_l_list.append(words[i-1])
                   if i+1 == len(words):
                      red_name_r_list.append('')
                   else:
                      red_name_r_list.append(words[i+1])
                   continue
                if words[i] == '*'*len(words[i]):
                   if i+1 is not 0 and (words[i+1] == '*'*len(words[i+1])):
                      #print(words[i]+' '+words[i+1])
                      red_name_list.append(words[i]+' '+words[i+1])
                   else:
                      red_name_list.append(words[i])
                      if i-1 == 0:
                         red_name_l_list.append('')
                      else:
                         red_name_l_list.append(words[i-1])
                      if i+1 == len(words):
                         red_name_r_list.append('')
                      else:
                         red_name_r_list.append(words[i+1])
        for name,left,right in zip(red_name_list,red_name_l_list,red_name_r_list):
            temp_dict = {}
            temp_dict["name"] = name
            temp_dict["name_length"] = len(name)
            space_count = re.findall(' ',name)
            temp_dict["spaces"] = len(space_count)
            temp_dict["left_w"] = left
            temp_dict["right_w"] = right
            #print(temp_dict)
            red_dict.append(temp_dict)
        if (sys.argv[2]):
           create_features(sys.argv[2],red_name_list)
        else:
           print("Please enter the training data folder as second command line argument")
     else:
        print("Please enter name of the redacted file as first command line argument")
  else:
     print("Please enter the proper command line argument")

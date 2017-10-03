import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
from pylab import *
from scipy import *
from sklearn.cluster import KMeans
from scipy import sparse
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.neighbors import KNeighborsClassifier
from astropy.table import Table, Column

def predict_cuisines(json,arg_list):
    ingred_dict = {}
    all_ingredients = []
    all_ids = []
    for i in range(len(json)):
        cuisine_id = json[i]['id']
        ingreds = json[i]['ingredients']
        if cuisine_id not in ingred_dict.keys():
            all_ids.append(cuisine_id) 
            ingred_dict[cuisine_id] = ingreds
        else: 
            temp_list = ingred_dict[cuisine_id]
            temp_list.extend(ingreds)
            ingred_dict[cuisine_id] = temp_list
        all_ingredients.extend(ingreds)
        
    all_ingredients = list(set(all_ingredients))
    num_ingred = len(all_ingredients)
    num_ids = len(all_ids)
    train_matrix = np.zeros((num_ids,num_ingred))
    test_matrix = np.zeros((1,num_ingred))
    i = 0
    for ids in all_ids:
        ingreds = ingred_dict[ids]
        for ingredient in ingreds:
            j = all_ingredients.index(ingredient) 
            train_matrix[i,j] += 1
        i += 1
    train_matrix = sparse.csr_matrix(train_matrix)
    for test_ingred in arg_list:
        if test_ingred in all_ingredients:
           j = all_ingredients.index(test_ingred)
           test_matrix[0,j] += 1
    test_matrix = sparse.csr_matrix(test_matrix)
    transformer = TfidfTransformer()
    train_tfidf = transformer.fit_transform(train_matrix)
    test_tfidf = transformer.fit_transform(test_matrix)
    train_tfidf = train_tfidf.toarray()
    test_tfidf = test_tfidf.toarray()
    neigh = KNeighborsClassifier(n_neighbors=1)
    neigh.fit(train_tfidf,all_ids)
    top_ele = 5
    table_list = []
    if len(all_ids) >= top_ele:
       pre = neigh.kneighbors(test_tfidf, n_neighbors= 5,return_distance=False)
       for i in range(len(pre)):
           print("Best matching meals available for given Ingredients are:")
           for j in range(len(pre[i])):
               pre_id = all_ids[pre[i][j]]
               for k in range(len(json)):
                   pre_cuisine_id = json[k]['id']
                   if pre_cuisine_id == pre_id:
                      pre_cuisine_type = json[k]['cuisine']
                      pred_cuisine_ingred = json[k]['ingredients']
               table_list.append([pre_id,pre_cuisine_type,pred_cuisine_ingred])
       t = Table(rows=table_list, names=('Cuisine ID', 'Cuisine Type', "Cuisine Ingredients"))
       print(t)
    else:
       print("Training set of data is very less to predict the cuisines")

def main():
    with open('yummly.json') as data_file:    
         data = json.load(data_file)
    arg_list = sys.argv
    arg_list.pop(0)
    if len(arg_list) is 0:
       print("Kindly give the ingredients as command line arguments")
    else:
       predict_cuisines(data,arg_list)

main()

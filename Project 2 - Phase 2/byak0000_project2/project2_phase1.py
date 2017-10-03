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
get_ipython().magic(u'matplotlib inline')


      
def create_kmeans_labels(json):
    ingred_dict = {}
    all_cuisines = []
    all_ingredients = []
    for i in range(len(json)):
        cuisine = json[i]['cuisine']
        ingreds = json[i]['ingredients']
        if cuisine not in ingred_dict.keys():
            all_cuisines.append(cuisine) 
            ingred_dict[cuisine] = ingreds
        else: 
            temp_list = ingred_dict[cuisine]
            temp_list.extend(ingreds)
            ingred_dict[cuisine] = temp_list
        all_ingredients.extend(ingreds)
    all_ingredients = list(set(all_ingredients)) 
    num_ingred = len(all_ingredients)
    num_cuisines = len(all_cuisines)                
    matrix = np.zeros((num_cuisines,num_ingred))
    i = 0
    for cuisine in all_cuisines: 
        ingreds = ingred_dict[cuisine]
        for ingredient in ingreds:
            j = all_ingredients.index(ingredient) 
            matrix[i,j] += 1
        i += 1
    matrix = sparse.csr_matrix(matrix)
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(matrix) 
    tfidf=tfidf.toarray()
    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(tfidf)
    pca_dataframe = pd.DataFrame(pca_data)
    pca_dataframe.columns = ['Cuisines', 'Ingredients']  
    kmeans = KMeans(init='k-means++', n_clusters= 7, n_init=20)
    kmeans.fit(pca_data)
    return kmeans.predict(pca_data),pca_data,all_cuisines
    


def main():
    with open('yummly.json') as data_file:    
         data = json.load(data_file)
    labels, pca_data, all_cuisines = create_kmeans_labels(data)
    rdata = pca_data
    i=0
    figureRatios = (15,20)
    x = []
    y = []
    color = []
    area = []
    colors = ['#009600','#2980b9', '#ff6300','#2c3e50', '#660033', '#8b8378', '#fff8dc', '#ffe4e1', '#2f4f4f', '#6495ed', '#66cdaa'] 
    plt.figure(4, figsize=figureRatios)
    for data in rdata:
        x.append(data[0]) 
        y.append(data[1])  
        color.append(colors[labels[i]]) 
        area.append(15000)
        text(data[0], data[1], all_cuisines[i], size=10.6,horizontalalignment='center', fontweight = 'bold', color='w')
        i += 1

    plt.scatter(x, y, c=color, s=area, linewidths=2, edgecolor='w', alpha=0.80) 
    plt.axes().set_aspect(0.8, 'box')
    plt.xlabel('Cuisines')
    plt.ylabel('Ingredients')
    plt.axis('on') 
    plt.show()
main() 

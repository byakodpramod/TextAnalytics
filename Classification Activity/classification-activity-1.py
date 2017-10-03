import nltk
import sklearn
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import sklearn.metrics
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import precision_recall_fscore_support

actual_labels = np.array(['spam', 'ham', 'spam', 'spam', 'spam','ham', 'ham', 'spam', 'ham', 'spam','spam', 'ham', 'ham', 'ham', 'spam','ham', 'ham', 'spam', 'spam', 'ham'])
predicted_labels = np.array(['spam', 'spam', 'spam', 'ham', 'spam','spam', 'ham', 'ham', 'spam', 'spam','ham', 'ham', 'spam', 'ham', 'ham','ham', 'spam', 'ham', 'spam', 'spam'])
print("PRECISION   RECALL    F1")
print("=========================")
print(precision_recall_fscore_support(actual_labels, predicted_labels,average=None))
print("ACCURACY")
print("========")
print(accuracy_score(actual_labels,predicted_labels))

def word_grams(word_bag, n):
    n_bag = []
    temp_bag = ngrams(word_bag, n)    
    for ngram in temp_bag:  
        n_bag.append(' '.join(str(i) for i in ngram))
    return n_bag

def bag_words():
    sent1 = "a set of a set of words that is complete in itself"
    sent2 = "The punishment assigned to a defendant found guilty by a court"
    sent3 = "declare the punishment decided for an offender"
    sent_list = [sent1,sent2,sent3]
    #find_tfidf(sent_list)
    word_bag = []
    for sent in sent_list:
        word_split = sent.split(' ')
        word_bag.extend(word_split)
    bag=word_grams(word_bag, 3)
    return bag

bag=bag_words()
print("Bag with 3 grams")
print("================")
print(bag)
vectorizer_tfidf = TfidfVectorizer(min_df = 1,ngram_range=(3,3))
features_tfidf = vectorizer_tfidf.fit_transform(bag)
print("tfidf values below")
print("===================")
print (features_tfidf.todense())

clf=MultinomialNB(alpha=.01)
vectorizer =TfidfVectorizer(min_df=1,ngram_range=(1,2))
X_train=vectorizer.fit_transform(bag)
y_train=[0,0,1,1,1,2]
clf.fit(X_train, y_train)

print (clf.predict(vectorizer.transform(['i'])))

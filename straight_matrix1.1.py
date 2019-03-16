#инициализации
import numpy as np
from scipy.spatial.distance import pdist, squareform
import numpy
import random
import pandas as pd
#матан
df = pd.read_csv('sabaton.csv',error_bad_lines=False)
dfdr = df.drop(['coutnry'], axis=1)
ids = df["_id"];
dfdr = dfdr.drop(['_id'], axis=1)
data = dfdr.as_matrix()
data_dist = pdist(data, 'euclidean')
dist_matrix = squareform(data_dist)
dist_matrix[0].size
ids = df["_id"];
ids = ids.tolist()
#пожилой преобразователь
m_ids =[]
for i in range(0, len(ids)):
    v = ids[i].split('(')[1]
    v = v.split(')')[0]
    v = v.split('"')[1]
    m_ids.append(v)
#рандомный бот
def random_bot():
    cart = []
    
    for i in range(1,6,1):
        p = numpy.random.randint(1,23997);
        cart.append(m_ids[p])
    return cart
random_bot()
#матричный бот
def matrix_bot(_id):
    cart = []
    j = m_ids.index(_id)
    dists = dist_matrix[j]
    dists_sorted = np.sort(dists)[::1]
    for i in range(1,6):
        k = dists_sorted[i+1]
        n = (dists==k).argmax()
        cart.append(m_ids[n])
    return cart
matrix_bot("5c825dd82dcf3568a17d27b2")
#метрика
def metrix(_idc, _id):
    cart = []
    cart_final = {}
    j = m_ids.index(_idc)
    dists = dist_matrix[j].tolist()
    dists_sorted = np.sort(dists)[::1]
    for i in range(1,101):
        k = dists_sorted[i]
        n = dists.index(k)
        cart.append(n);
    for i in _id:
        zid = m_ids.index(i)
        
        if zid in cart:
            if cart.index(zid) < np.random.randint(0,100):
                cart_final[i] = True
            else: 
                cart_final[i] = False
        else: 
            cart_final[i] = False
    return cart_final
metrix("5c825dd82dcf3568a17d27b1", matrix_bot("5c825dd82dcf3568a17d27b1"))
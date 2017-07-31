import os

# cassandra driver
from cassandra.cluster import Cluster
from cassandra.cluster import SimpleStatement, ConsistencyLevel

import io
from PIL import Image
import numpy as np

from keras.applications.xception import Xception
from keras.applications.xception import preprocess_input

def load_images(path, target_height=299, target_width=299):
    try:
        img = Image.open(path)
        
        width, height = img.size
        if width != target_width or height != target_height:
            img = img.resize((target_height, target_width), Image.ANTIALIAS)
        
        return np.array(img)
    except:
        return None

def predict_image(x, model):
    x = x.astype('float32')
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    features = model.predict(x)
    features = features.flatten()
    return features

# init
datadir = './preview'

# connect to cassandra
cluster = Cluster(['cassandra'])
session = cluster.connect()

#create keyspace
cql_stmt = """
    CREATE KEYSPACE IF NOT EXISTS images 
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1' } 
"""
result = session.execute(cql_stmt)

# create table
cql_stmt = """
    CREATE TABLE IF NOT EXISTS images.embeddings (
      filename   text,
      vector     list<double>,
      PRIMARY KEY (filename)
    );
"""

result = session.execute(cql_stmt)

# prepared statement for getting the name of the top venue in a given cluster
cql_insert = session.prepare("INSERT INTO images.embeddings (filename, vector) values (?, ?)")

# prepared statement for getting the name of the top venue in a given cluster
cql_query = session.prepare("SELECT count(1) from images.embeddings where filename=?")

model = Xception(include_top=False)

for filename in os.listdir(datadir):
        fullname = os.path.join(datadir,filename)
        im =load_images(fullname, 50, 50)
        
        #predict and insert to cassandra
        if im is not None:
            done= False
            while(not done):
                try:
                    vec = predict_image(im, model)
                    res = session.execute(cql_insert.bind((filename,vec.tolist())))
                    print(filename, im.size, vec.shape)
                    done=True
                except:
                    done=False
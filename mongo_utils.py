# import relevant libraries
import pandas as pd
from pymongo import MongoClient

def query_to_dataframe(query, collection):
    '''
    custom function to create a dataframe of query results
    from the weather_data
    '''
    entries = []
    for entry in collection.find(query):
        entries.append(entry)
      
    if len(entries)==0: # no hits for the query
        print("No hits for the specified query")
        return None
    else:
        return pd.DataFrame(entries).drop(columns=["_id"])

def config_collection(server):
    '''
    The pointer can then be used to add new documents to the collection, or
    to query objects from the collection.
   
    parameters:
    server: a dictionary containing a mongodb server configuration information
    
    return: a pointer to the specifed mongodb collection 
    '''
    client = MongoClient(host=server["host"], port=server["port"])
    db = client[server["database"]]
    collection = db[server["collection"]]

    return collection

def make_lineObj(line, data):
    ''' 
    create a dictionary object containing entries from a specified row
    of a dataframe.
    parameters:
    line - the row index of interest
    return:
    obj - a dictionary object containing the specified row entries
    '''
   
    obj = {}
    
    for column in data.columns:
        obj[column] = data[column].iloc[line]
        
    return obj


def storeObj(obj, collection):
    '''
    Store a dictionary object as a document in a specifed collection
    within a mongodb database
    parameters:
    obj - a dictionary object to be stored as a mongodb document
    collection - a pointer to a mongodb collection where the document 
                 will be sotred. The collection pointer can be obtained
                 from the fucntion config_collection(server)
    '''
    collection.insert_one(obj)
    
def store_data(data, collection):
    '''
    Stores all the rows in a pandas data frame as documents within a specified 
    collection on a mogodb database
    '''
    for row in range(0, len(data)):
        obj = make_lineObj(row, data)
        storeObj(obj, collection)

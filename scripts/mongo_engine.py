import pymongo
import gridfs
import pandas as pd
import geopandas as gpd
from bson import json_util, ObjectId
import json
from settings import DATABASE_URI

class MongoEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name, uri=DATABASE_URI):
        self.client = pymongo.MongoClient(uri, maxPoolSize=None)
        self.db = self.client[db_name]

    def insert_geodataframe(self, gdf : gpd.GeoDataFrame, collection_name : str , geojson_state : str, geojson_name : str):
        """
        Insert a GeoDataFrame into a specified collection and store its features in the "features" collection.

        :param gdf: GeoDataFrame to be inserted.
        :param collection_name: Name of the collection to insert the GeoJSON document into.
        :param geojson_name: Name of the GeoJSON document to be created.
        :param geojson_state: State the GeoJSON document belongs to.
        """
        
        collection = self.db[collection_name]
        
        # Insert GeoJSON document
        geojson_document = {
            'state': geojson_state,
            'name': geojson_name,
            'geojson': json.loads(gdf.to_json())
        }
        collection.insert_one(geojson_document)
    
    def update_ensemble(self, ensemble_data : dict):
        """
        Update the features of a GeoJSON document in the "states" collection based on the provided GeoDataFrame.

        :param ensemble_name: Name of ensemble being updated
        :param ensemble_data: Document containing new ensemble data
        """ 
        collection = self.db['states']
        ensemble_name = ensemble_data['name']
        update = { '$set' : { k:v for k,v in ensemble_data.items()}}
        query = { 'name': ensemble_name }
        collection.update_one(query, update, upsert=True)
    
            
    def drop_collection(self, collection_name : str):
        """
        Drop a collection form the db.
        """
        if collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)

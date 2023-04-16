import pymongo
import pandas as pd
import geopandas as gpd
from bson import json_util, ObjectId
import json

class MongoEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name, uri='mongodb://localhost:27017/'):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

    def insert_geodataframe(self, gdf, collection_name, geojson_name):
        """
        Insert a GeoDataFrame into a specified collection and store its features in the "features" collection.

        :param gdf: GeoDataFrame to be inserted.
        :param collection_name: Name of the collection to insert the GeoJSON document into.
        :param geojson_name: Name of the GeoJSON document to be created.
        """
        
        collection = self.db[collection_name]
        features_collection = self.db['features']
        
        # Insert GeoJSON document
        geojson_document = {
            'name': geojson_name,
            'type': 'FeatureCollection',
            'features': []
        }
        result = collection.insert_one(geojson_document)
        geojson_id = result.inserted_id

        # Insert features
        records = json.loads(gdf.to_json())
        
        #"anonymous" function
        def a(feature):
            feature['plan'] = geojson_id
            return feature
        
        # add FeatureCollection id to populate later
        
        # write features in bulk out of order for speed
        result = features_collection.insert_many(map(a, records['features']), ordered=False)
        # add ids to featureCollection
        collection.update_one({'_id': geojson_id}, {'$set': {'features': result.inserted_ids}})


    def read_geodataframe(self, collection_name, geojson_name):
        """
        Read a GeoJSON document from a collection and its features from the "features" collection into a GeoDataFrame.

        :param collection_name: Name of the collection containing the GeoJSON document.
        :param geojson_name: Name of the GeoJSON document to read.
        :return: A GeoDataFrame containing the data from the specified GeoJSON document or None if the document is not found.
        """
        collection = self.db[collection_name]
        features_collection = self.db['features']

        geojson_document = collection.find_one({'name': geojson_name})
        if geojson_document is None:
            return None

        feature_ids = list(map(lambda fid: ObjectId(fid), geojson_document['features']))
        results = features_collection.find({ '_id': { '$in': feature_ids } }, projection={'_id': False})
        features = json_util.loads(json_util.dumps(results))

        gjson = {'type': 'FeatureCollection', 'features': features}
        return gpd.GeoDataFrame.from_features(gjson)
    
    # EXPERIMENTAL DOES NOT WORK
    def update_geodataframe(self, gdf, collection_name, geojson_name):
        """
        Update the features of a GeoJSON document in the "features" collection based on the provided GeoDataFrame.

        :param gdf: GeoDataFrame containing updated data.
        :param collection_name: Name of the collection containing the GeoJSON document.
        :param geojson_name: Name of the GeoJSON document to update.
        :param query: Dictionary specifying the query to select features to update. Defaults to an empty dictionary ({}).
        """
        
        collection = self.db[collection_name]
        features_collection = self.db['features']
        geojson_document = collection.find_one({'name': geojson_name})
        
        if geojson_document is None:
            return
        
        geojson_id = geojson_document['_id']

        for _, row in gdf.iterrows():
            row_dict = row.to_json(default_handler=str)
            row_query = { 'properties': { 'GEOID20': row_dict['properties']['GEOID20'] } }
            feature = features_collection.find_one(row_query)

            if feature is not None:
                update = {'$set': row_dict}
                features_collection.update_one({'_id': feature['_id']}, update)


    def delete_geojson(self, collection_name, geojson_name):
        collection = self.db[collection_name]
        features_collection = self.db['features']

        geojson_document = collection.find_one({'name': geojson_name})
        if geojson_document is not None:
            feature_ids = geojson_document['features']
            for fid in feature_ids:
                features_collection.delete_one({'_id': ObjectId(fid)})
            collection.delete_one({'_id': geojson_document['_id']})
            
    def drop_collection(self, collection_name):
        if collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)

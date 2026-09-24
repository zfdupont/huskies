import pymongo
import gridfs
import geopandas as gpd
import json
from settings import DATABASE_URI

class MongoEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_name, uri=DATABASE_URI):
        # __new__ hands back the cached instance, but __init__ still runs on every
        # construction. Guard it so the client connects once; later calls (e.g.
        # fill_database builds this 4x) reuse the same connection instead of
        # reconnecting and rebinding the db.
        if getattr(self, "_initialized", False):
            return
        self.client = pymongo.MongoClient(uri, maxPoolSize=None)
        self.db = self.client[db_name]
        self._initialized = True

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
    
    def update_ensemble(self, contract : dict):
        """Upsert a contract document into the 'states' collection, keyed by meta.state."""
        collection = self.db['states']
        state = contract['meta']['state']
        collection.update_one({'meta.state': state}, {'$set': contract}, upsert=True)
    
            
    def drop_collection(self, collection_name : str):
        """
        Drop a collection form the db.
        """
        if collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)

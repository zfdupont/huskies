# Example usage
from shapely.geometry import Point
import geopandas as gpd

import sys, os
from pathlib import Path
print()
sys.path.append(str(Path(__file__).parent.parent))

import settings
from MongoEngine import MongoEngine
# Create a sample GeoDataFrame


def test_geojson_ops():
    print("reading from file...")
    gdf = gpd.read_file("/Users/zfdupont/huskies-server/scripts/mergedGAEnacted.geojson")
    print(gdf)
    # Initialize MongoEngine and connect to a database
    engine = MongoEngine('geo_test', uri=settings.DATABASE_URI)

    print("inserting to db...")
    # Insert GeoDataFrame into a collection
    engine.insert_geodataframe(gdf, 'geo_test_collection', 'geojson_1')

    # print("updating from db")
    # # Update GeoDataFrame in a collection
    # gdf['district_id'] = gdf['district_id'] * 10
    # engine.update_geodataframe(gdf, 'geo_test_collection', 'geojson_1')

    # print("deleting records...")
    # # Delete records in a collection using a query
    # engine.delete_geodataframe('geo_test_collection', query={'id': 20})

    # Drop the collection
    # engine.drop_collection('geo_test_collection')

def test_ensemble_ops():
    ensemble_data = {
        'name': 'WA',
        'test_arg1': 1,
        'test_arg2' : ['3'],
        'plans': [ '123123', '1231' ]
    }
    
    engine = MongoEngine('test_db', uri=settings.DATABASE_URI)
    
    engine.update_ensemble(ensemble_data)
    
    ensemble_data = {
        'name': 'WA',
        'test_arg1': 2,
        'test_arg2' : ['3'],
        'plans': [ '123123', '1231', '1982739' ]
    } 
    
    engine.update_ensemble(ensemble_data)
    
test_geojson_ops()

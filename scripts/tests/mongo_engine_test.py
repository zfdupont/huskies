# Example usage
from shapely.geometry import Point
import geopandas as gpd

import sys, os
sys.path.append("/Users/zfdupont/huskies-server/scripts")

import settings
from MongoEngine import MongoEngine
# Create a sample GeoDataFrame


print("reading from file...")
gdf = gpd.read_file("/Users/zfdupont/huskies-server/scripts/mergedGA.geojson")
print(gdf)
# Initialize MongoEngine and connect to a database
engine = MongoEngine('geo_test_db', uri=settings.DATABASE_URI)

print("inserting to db...")
# Insert GeoDataFrame into a collection
engine.insert_geodataframe(gdf, 'geo_test_collection', 'geojson_1')


print("reading from db...")
# Read GeoDataFrame from a collection
gdf_from_db = engine.read_geodataframe('geo_test_collection', 'geojson_1')
print(gdf_from_db)
assert len(gdf) == len(gdf)

# print("updating from db")
# # Update GeoDataFrame in a collection
# gdf['district_id'] = gdf['district_id'] * 10
# engine.update_geodataframe(gdf, 'geo_test_collection', 'geojson_1')

# print("deleting records...")
# # Delete records in a collection using a query
# engine.delete_geodataframe('geo_test_collection', query={'id': 20})

# Drop the collection
engine.drop_collection('geo_test_collection')

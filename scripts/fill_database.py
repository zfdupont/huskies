from settings import HUSKIES_HOME, DATABASE_URI
import geopandas as gpd
from mongo_engine import MongoEngine
import json
import argparse

def fill_ensemble_data(state, engine):
    ensemble_data_path = f'{HUSKIES_HOME}/generated/{state}/ensemble_data.json'
    with open(ensemble_data_path, 'r') as f:
        ensemble_data = json.load(f)
    engine.update_ensemble(ensemble_data)
    
def fill_plans(state, engine):
    geojsons_path = f'{HUSKIES_HOME}/generated/{state}/interesting/'
    interesting_criteria = {"enacted", "democrat_favored", "republican_favored",
                            "fair_seat_vote", "fair_geo_pop_var", "high_geo_pop_var"}
    for criteria in interesting_criteria:
        interesting_plan = gpd.read_file(f'{geojsons_path}{criteria}_plan.geojson')
        engine.insert_geodataframe(interesting_plan, 'plans', state, criteria)

def fill_database(state, db_collection):
    engine = MongoEngine(db_collection, uri=DATABASE_URI)
    fill_ensemble_data(state, engine)
    fill_plans(state, engine)

def fill_database_all(db_collection):
    fill_database("GA", db_collection)
    fill_database("NY", db_collection)
    fill_database("IL", db_collection)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', help='collection to write to (defaults to dev)',
                        default="dev")
    args = parser.parse_args()
    fill_database_all(args.collection)
from settings import HUSKIES_HOME, DATABASE_URI
import geopandas as gpd
from mongo_engine import MongoEngine
import json
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
def fill_database(state):
    engine = MongoEngine('dev', uri=DATABASE_URI)
    fill_ensemble_data(state, engine)
    fill_plans(state, engine)
def fill_database_all():
    fill_database("GA")
    fill_database("NY")
    fill_database("IL")
if __name__ == '__main__':
    fill_database_all()
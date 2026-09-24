from settings import HUSKIES_HOME, DATABASE_URI
import geopandas as gpd
import topojson as tp
from mongo_engine import MongoEngine
import json

# Districts are stored/served at full precinct-vertex resolution (~160k vertices
# per state), which makes /api/plan payloads multi-MB and slow to fetch/render.
# Topology-preserving simplification shrinks them ~10-15x with no visible change
# at map zoom and no gaps between adjacent districts. ~0.0005 deg is ~55m.
SIMPLIFY_TOLERANCE = 0.0005

def simplify_for_display(gdf):
    crs = gdf.crs
    simplified = tp.Topology(gdf, prequantize=False, toposimplify=SIMPLIFY_TOLERANCE).to_gdf()
    return simplified.set_crs(crs, allow_override=True)

def fill_ensemble_data(state, engine):
    contract_path = f'{HUSKIES_HOME}/generated/{state}/contract_{state}.json'
    with open(contract_path, 'r') as f:
        contract = json.load(f)
    engine.update_ensemble(contract)
def fill_plans(state, engine):
    geojsons_path = f'{HUSKIES_HOME}/generated/{state}/interesting/'
    interesting_criteria = {"enacted", "democrat_favored", "republican_favored",
                            "fair_seat_vote", "fair_geo_pop_var", "high_geo_pop_var"}
    for criteria in interesting_criteria:
        interesting_plan = gpd.read_file(f'{geojsons_path}{criteria}_plan.geojson')
        interesting_plan = simplify_for_display(interesting_plan)
        engine.insert_geodataframe(interesting_plan, 'plans', state, criteria)
def fill_database(state):
    engine = MongoEngine('huskies', uri=DATABASE_URI)
    fill_ensemble_data(state, engine)
    fill_plans(state, engine)
def fill_database_all():
    MongoEngine('huskies', uri=DATABASE_URI).drop_collection('plans')
    MongoEngine('huskies', uri=DATABASE_URI).drop_collection('states')
    fill_database("GA")
    fill_database("NY")
    fill_database("IL")
if __name__ == '__main__':
    fill_database_all()

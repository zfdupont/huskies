from settings import HUSKIES_HOME, DATABASE_URI
import geopandas as gpd
import pandas as pd
from gerrychain import Graph, GeographicPartition
from ensemble_analysis import map_incumbents
from plan_analysis import calculate_differences
from mongo_engine import MongoEngine
def setup_district_data(state, election_results, plan_21):
    district_data = {district:{"incumbent":None, "democrat_candidate": "Democrat Candidate",
                               "republican_candidate": "Republican Candidate", "democrat_votes":0,
                               "republican_votes":0, "winner":"D"} 
                     for district in plan_21.parts}
    for i in range(len(election_results)):
        district = election_results["district"][i] - 1
        if election_results["incumbent"][i] == True:
            district_data[district]["incumbent"] = election_results["name"][i]
        if election_results["party"][i] == "R":
            district_data[district]["republican_candidate"] = election_results["name"][i]
            district_data[district]["republican_votes"] = int(election_results["votes"][i])
        else:
            district_data[district]["democrat_candidate"] = election_results["name"][i]
            district_data[district]["democrat_votes"] = int(election_results["votes"][i])
    for district in district_data:
        if district_data[district]["democrat_votes"] > district_data[district]["republican_votes"]:
            district_data[district]["winner_party"] = "D"
        else:
            district_data[district]["winner_party"] = "R"
    return district_data
def merge_into_districts(path, state):
    precincts = gpd.read_file(path)
    precincts.set_geometry("geometry")
    if state == "NY":
        precincts = precincts.drop(7041)
    district_plan = precincts.dissolve(by="district_id_21",
                       aggfunc={key: 'sum' for key in filter(lambda x: x in 
                                              ["pop_total", "vap_total", "vap_white", "vap_black", 
                                               "vap_native", "vap_asian", "vap_hwn", "vap_other", 
                                               "vap_mixed", "vap_hisp", "republican", "democrat"], 
                                               list(precincts.columns))})
    return district_plan
def addon_properties(new_districts, changes):
    new_properties = set()
    for change in changes:
        new_properties.add(change + "_common")
        new_properties.add(change + "_added")
        new_properties.add(change + "_lost")
        new_properties.add(change + "_variation")
    for property in new_properties:
        new_districts[property] = None
    new_districts = new_districts.reset_index(drop=True)
    return new_districts, new_properties
def fill_properties(new_districts, election_properties, district_data, new_properties, incumbent_mappings):
    for district in district_data:
        for property in election_properties:
            new_districts.loc[district, property] = district_data[district][property]
    for mapping in incumbent_mappings:
        for property in new_properties:
            new_districts.loc[incumbent_mappings[mapping]['id_new'], property] = incumbent_mappings[mapping][property]
    return new_districts
def analyze_enacted(state):
    graph_21 = Graph.from_json(f'{HUSKIES_HOME}/generated/{state}/preprocess/graph{state}.json')
    plan_21 = GeographicPartition(graph_21, "district_id_21")
    graph_20 = Graph.from_json(f'{HUSKIES_HOME}/generated/{state}/preprocess/graph{state}20.json')
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    election_results = pd.read_csv(f'{HUSKIES_HOME}/data/{state}/election_results_{state}.csv')
    district_data = setup_district_data(state, election_results, plan_21)
    incumbents = pd.read_csv(f'{HUSKIES_HOME}/data/{state}/incumbents_{state}.csv')
    incumbent_mappings = map_incumbents(plan_20, plan_21, incumbents)
    changes = {"vap_total", "area", "vap_black", "vap_white", "vap_hisp","democrat", "republican"}
    calculate_differences(plan_20, plan_21, incumbent_mappings, changes)
    enacted_plan = merge_into_districts(f'{HUSKIES_HOME}/generated/{state}/preprocess/merged{state}P.geojson',
                                         state)
    enacted_plan, new_properties = addon_properties(enacted_plan, changes)
    election_properties = {"incumbent", "democrat_candidate", "republican_candidate",
                      "democrat_votes","republican_votes", "winner"}
    enacted_plan = fill_properties(enacted_plan, election_properties, district_data, new_properties, incumbent_mappings)
    engine = MongoEngine('huskies', uri=DATABASE_URI)
    engine.insert_geodataframe(enacted_plan, 'plans', state, "enacted")
    #enacted_plan.to_file(f'{HUSKIES_HOME}/generated/{state}/interesting/enacted_plan.geojson', driver='GeoJSON')
def analyze_enacted_all():
    analyze_enacted("GA")
    analyze_enacted("NY")
    analyze_enacted("IL")
if __name__ == '__main__':
    analyze_enacted_all()
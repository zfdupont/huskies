import pickle
from gerrychain import(GeographicPartition, Graph)
import pandas as pd
from collections import defaultdict
import json
import numpy as np
from plan_analysis import analyze_plan
def get_ensemble(state):
    graph = Graph.from_json('./generated/'+ state +'/preprocess/graph'+ state +'.json')
    assignments = []
    for i in range(4):
        some_assignments = pickle.load(open('./generated/' + state + '/assignments/assign_' + state + '_' + str(i) + '.p', 'rb')) #load a pickled list of assignments
        assignments += some_assignments
    ensemble = []
    for a in assignments:
        ensemble.append(GeographicPartition(graph, a))
    return ensemble
def setup_box_w_data(num_incumbents):
    properties = ["geo_variations","pop_variations","VAPBLACK_proportions", "DEMOCRAT_proportions", "REPUBLICAN_proportions"]
    box_w_data = {}
    for property in properties:
        box_w_data[property] = [[] for x in range(num_incumbents)]
    return box_w_data
def map_incumbents(plan_20, plan_new, incumbents):
    incumbent_mappings = {}
    for i in range(len(incumbents)):
        mapping = dict()
        mapping["IncumbentParty"] = incumbents["Party"][i]
        for node in plan_20.graph.nodes:
            if str(plan_20.graph.nodes[node]["GEOID20"]) == str(incumbents["GEOID20"][i]):
                mapping["id_20"] = plan_20.assignment[node]
                break
        for node in plan_new.graph.nodes:
            if str(plan_new.graph.nodes[node]["GEOID20"]) == str(incumbents["GEOID20"][i]):
                mapping["id_new"] = plan_new.assignment[node]
                break
        incumbent_mappings[incumbents["Name"][i]] = mapping
    return incumbent_mappings
def calculate_split(plan, incumbent_mappings):
    precincts = plan.graph.nodes
    dem_winners = 0
    rep_winners = 0
    already_seen = [False for x in range(len(plan.parts))]
    for incumbent in incumbent_mappings:
        mapping = incumbent_mappings[incumbent]
        district = mapping["id_new"]
        if already_seen[district] == True:
            continue
        dem_votes = sum([precincts[precinct]["DEMOCRAT"] for precinct in plan.parts[district]])
        rep_votes = sum([precincts[precinct]["REPUBLICAN"] for precinct in plan.parts[district]])
        party = incumbent_mappings[incumbent]["IncumbentParty"]
        if dem_votes > rep_votes and party == "D":
            dem_winners += 1
            already_seen[district] = True
        elif rep_votes > dem_votes and party == "R":
            rep_winners += 1
            already_seen[district] = True
    return str(dem_winners) + "/" + str(rep_winners), rep_winners + dem_winners
def calc_summary_data(plan_20, plan_new, incumbent_mappings, incumbent_summary_data, box_w_data):
    variations_needed = ["VAPTOTAL", "ALAND20"]
    box_w_lists = {"geo_variations":[], "pop_variations":[],"VAPBLACK_proportions":[], "DEMOCRAT_proportions":[], "REPUBLICAN_proportions":[]}
    for incumbent in incumbent_mappings:
        id_20 = incumbent_mappings[incumbent]["id_20"]
        id_new = incumbent_mappings[incumbent]["id_new"]
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        union = plan_20.parts[id_20].union(plan_new.parts[id_new])
        for variation in variations_needed:
            sum_inter = sum([plan_20.graph.nodes[x][variation] for x in intersection])
            sum_union = sum([plan_20.graph.nodes[x][variation] for x in union])
            variance = 100 * (1 - sum_inter / (sum_union))
            if variation == "VAPTOTAL":
                property = "pop_variations"
            else:
                property = "geo_variations"
            incumbent_summary_data[incumbent][property].append(variance)
            box_w_lists[property].append(variance)
        demographics_needed = ["VAPBLACK", "DEMOCRAT", "REPUBLICAN"]
        for demographic in demographics_needed:
            demographic_sum = sum([plan_new.graph.nodes[x][demographic] for x in plan_new.parts[id_new]])
            if demographic == "DEMOCRAT" or demographic == "REPUBLICAN":
                pop_sum = sum([plan_new.graph.nodes[x]["DEMOCRAT"] + plan_new.graph.nodes[x]["REPUBLICAN"] for x in plan_new.parts[id_new]])
            else:
                pop_sum = sum([plan_new.graph.nodes[x]["VAPTOTAL"] for x in plan_new.parts[id_new]])
            proportion = demographic_sum / pop_sum
            incumbent_summary_data[incumbent][demographic + "_proportions"].append(proportion)
            box_w_lists[demographic + "_proportions"].append(proportion)
        update_box_w(box_w_lists, box_w_data)
def update_box_w(box_w_lists, box_w_data):
    for property in box_w_lists:
        sorted_list = sorted(box_w_lists[property])
        for i in range(len(sorted_list)):
            box_w_data[property][i].append(sorted_list[i])
def find_quartiles(box_w_data):
    for property in box_w_data:
        for i in range(len(box_w_data[property])):
            curr_list = box_w_data[property][i]
            box_w_data[property][i] = list(np.percentile(curr_list,[0,25,50,75,100]))
def find_averages(incumbent_summary_data):
    total_geo_var = 0
    total_pop_var = 0
    total_vars = 0
    for incumbent in incumbent_summary_data:
        total_geo_var += sum(incumbent_summary_data[incumbent]["geo_variations"])
        total_pop_var += sum(incumbent_summary_data[incumbent]["pop_variations"])
        total_vars += len(incumbent_summary_data[incumbent]["geo_variations"])
    return total_geo_var / total_vars, total_pop_var / total_vars
def analyze_ensemble(state):
    ensemble = get_ensemble(state)
    incumbents = pd.read_csv('./data/'+ state +'/incumbents_'+ state +'.csv')
    graph_20 = Graph.from_json('./generated/'+ state +'/preprocess/graph'+ state +'20.json')
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    winner_split = defaultdict(int)
    total_winners = 0
    incumbent_summary_data = {name:{"geo_variations":[],"pop_variations":[], "VAPBLACK_proportions":[], "DEMOCRAT_proportions":[], "REPUBLICAN_proportions":[]} for name in incumbents["Name"]}
    box_w_data = setup_box_w_data(len(incumbents))
    for plan in ensemble:
        incumbent_mappings = map_incumbents(plan_20,plan,incumbents)
        split, winners = calculate_split(plan, incumbent_mappings)
        winner_split[split] += 1
        total_winners += winners
        calc_summary_data(plan_20, plan, incumbent_mappings, incumbent_summary_data, box_w_data)
    find_quartiles(box_w_data)
    average_geo_var, average_pop_var = find_averages(incumbent_summary_data)
    ensemble_summary = {"num_plans": len(ensemble), "num_incumbents": len(incumbents), "avg_incumbent_winners": total_winners / len(ensemble), "avg_geo_var":average_geo_var, "avg_pop_var":average_pop_var}
    state_data = {"ensemble_summary": ensemble_summary, "winner_split": winner_split, "box_w_data": box_w_data, "incumbent_data": incumbent_summary_data}
    return state_data
def analyze_all():
    state_data_GA = analyze_ensemble("GA")
    state_data_NY = analyze_ensemble("NY")
    state_data_IL = analyze_ensemble("IL")
    ensemble_data = {"GA":state_data_GA, "NY":state_data_NY, "IL":state_data_IL}
    with open('./generated/ensemble_data.json', "w") as outfile:
        json.dump(ensemble_data, outfile)
def plan_test(state):
    incumbents = pd.read_csv('./data/'+ state +'/incumbents_'+ state +'.csv')
    graph_20 = Graph.from_json('./generated/'+ state +'/preprocess/graph'+ state +'20.json')
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    graph_new = Graph.from_json('./generated/'+ state +'/preprocess/graph'+ state +'.json')
    plan_new = GeographicPartition(graph_new, assignment="district_id_21")
    incumbent_mappings = map_incumbents(plan_20,plan_new,incumbents)
    analyze_plan(plan_20,plan_new,incumbent_mappings,"GA","current")
if __name__ == '__main__':
    analyze_all()
    #plan_test("GA")
import pickle
from gerrychain import(GeographicPartition, Graph)
import pandas as pd
from collections import defaultdict
import json
import numpy as np
import multiprocessing
from plan_analysis import analyze_plan
from interesting_plan import find_interesting_plans
def get_ensemble(state):
    graph = Graph.from_json('./generated/'+ state +'/preprocess/graph'+ state +'.json')
    assignments = []
    for i in range(multiprocessing.cpu_count()):
        some_assignments = pickle.load(open('./generated/' + state + '/assignments/assign_' + state + '_' + str(i) + '.p', 'rb')) #load a pickled list of assignments
        assignments += some_assignments
    ensemble = []
    for a in assignments:
        ensemble.append(GeographicPartition(graph, a))
    return ensemble
def setup_box_w_data(num_incumbents):
    properties = ["geo_variations","pop_variations","vap_white_proportions","vap_black_proportions", "vap_hisp_proportions","democrat_proportions", "republican_proportions"]
    box_w_data = {}
    for property in properties:
        box_w_data[property] = [[] for x in range(num_incumbents)]
    return box_w_data
def map_incumbents(plan_20, plan_new, incumbents):
    incumbent_mappings = {}
    already_mapped_districts = set()
    for i in range(len(incumbents)):
        mapping = dict()
        mapping["incumbent_party"] = incumbents["party"][i]
        for node in plan_20.graph.nodes:
            if str(plan_20.graph.nodes[node]["geoid20"]) == str(incumbents["geoid20"][i]):
                if plan_20.assignment[node] in already_mapped_districts:
                    continue
                mapping["id_20"] = plan_20.assignment[node]
                already_mapped_districts.add(plan_20.assignment[node])
                break
        for node in plan_new.graph.nodes:
            if str(plan_new.graph.nodes[node]["geoid20"]) == str(incumbents["geoid20"][i]):
                mapping["id_new"] = plan_new.assignment[node]
                break
        incumbent_mappings[incumbents["name"][i]] = mapping
    return incumbent_mappings
def calculate_split(plan, incumbent_mappings):
    precincts = plan.graph.nodes
    dem_winners = 0
    rep_winners = 0
    for incumbent in incumbent_mappings:
        mapping = incumbent_mappings[incumbent]
        district = mapping["id_new"]
        dem_votes = sum([precincts[precinct]["democrat"] for precinct in plan.parts[district]])
        rep_votes = sum([precincts[precinct]["republican"] for precinct in plan.parts[district]])
        party = incumbent_mappings[incumbent]["incumbent_party"]
        if dem_votes > rep_votes and party == "D":
            dem_winners += 1
        elif rep_votes > dem_votes and party == "R":
            rep_winners += 1
    return str(dem_winners) + "/" + str(rep_winners), rep_winners + dem_winners
def calc_summary_data(plan_20, plan_new, incumbent_mappings, incumbent_summary_data, box_w_data):
    variations_needed = ["vap_total", "area"]
    box_w_lists = {property:[] for property in box_w_data}
    for incumbent in incumbent_mappings:
        id_20 = incumbent_mappings[incumbent]["id_20"]
        id_new = incumbent_mappings[incumbent]["id_new"]
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        for property in variations_needed:
            common = sum([plan_20.graph.nodes[x][property] for x in intersection])
            total = sum([plan_20.graph.nodes[x][property] for x in plan_new.parts[id_new]])
            added = total - common
            variation = added / total
            if property == "vap_total":
                summary_property = "pop_variations"
            else:
                summary_property = "geo_variations"
            incumbent_summary_data[incumbent][summary_property].append(variation)
            box_w_lists[summary_property].append(variation)
        demographics_needed = ["vap_black", "vap_white", "vap_hisp", "democrat", "republican"]
        for demographic in demographics_needed:
            demographic_sum = sum([plan_new.graph.nodes[x][demographic] for x in plan_new.parts[id_new]])
            if demographic == "democrat" or demographic == "republican":
                pop_sum = sum([plan_new.graph.nodes[x]["democrat"] + plan_new.graph.nodes[x]["republican"] for x in plan_new.parts[id_new]])
            else:
                pop_sum = sum([plan_new.graph.nodes[x]["vap_total"] for x in plan_new.parts[id_new]])
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
    incumbent_summary_data = {name:{"geo_variations":[],"pop_variations":[], "vap_black_proportions":[], "vap_white_proportions":[], "vap_hisp_proportions":[], "democrat_proportions":[], "republican_proportions":[]} for name in incumbents["name"]}
    box_w_data = setup_box_w_data(len(incumbents))
    least_fair_score = 1
    least_favored_score = -100
    lowest_var_score = 0
    interesting_criteria = {"fairest_seat_vote":least_fair_score,"most_democrat_favored":least_favored_score, "most_republican_favored":least_favored_score, "highest_geo_pop_var":lowest_var_score, "fairest_geo_pop_var":least_fair_score}
    interesting_plans = {"fair_seat_vote":None, "democrat_favored":None, "republican_favored":None, "high_geo_pop_var":None, "fair_geo_pop_var":None}
    for plan in ensemble:
        incumbent_mappings = map_incumbents(plan_20,plan,incumbents)
        split, winners = calculate_split(plan, incumbent_mappings)
        winner_split[split] += 1
        total_winners += winners
        calc_summary_data(plan_20, plan, incumbent_mappings, incumbent_summary_data, box_w_data)
        find_interesting_plans(plan_20, plan, incumbent_mappings, interesting_criteria, interesting_plans)
    for criteria in interesting_plans:
        incumbent_mappings = map_incumbents(plan_20, interesting_plans[criteria], incumbents)
        analyze_plan(plan_20, interesting_plans[criteria], incumbent_mappings, state, criteria)
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
    analyze_plan(plan_20,plan_new,incumbent_mappings,state,"current")
if __name__ == '__main__':
    analyze_all()
    #plan_test("GA")
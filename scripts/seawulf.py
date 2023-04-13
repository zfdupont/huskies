from gerrychain import(GeographicPartition, Graph, MarkovChain,
                        updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from gerrychain.updaters import Tally
from functools import partial
from collections import defaultdict
import json
import pandas as pd
import geopandas as gpd
import multiprocessing
import pickle
def create_partitions(n):
    graph = Graph.from_json('./graphGA.json')
    elections = [Election("PRE20", {"Democratic": "2020VBIDEN", "Republican": "2020VTRUMP"})]
    #also track total population, total VAP, and black VAP
    my_updaters = {"population": updaters.Tally("POPTOT", alias="population")}
    election_updaters = {election.name: election for election in elections}
    my_updaters.update(election_updaters)
    #use district_id from preprocessing for initial partition
    initial_partition = GeographicPartition(graph, assignment="district_id_21", updaters=my_updaters)
    #ideal population is the total population divided by number of districts
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
    proposal = partial(recom,
                    pop_col="POPTOT",
                    pop_target=ideal_population,
                    epsilon=0.05,
                    node_repeats=2
                    )
    #compactness constraint
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(initial_partition["cut_edges"])
    )
    #keep the populations within 2% of the ideal population
    pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.05)
    plans = []
    for i in range(4):
        chain = MarkovChain(
            proposal=proposal,
            constraints=[
                pop_constraint,
                compactness_bound
            ],
            accept=accept.always_accept,
            initial_state=initial_partition,
            total_steps=5
        )
        for plan in chain:
            pass
        plans.append(chain.state)
    assignments = []
    for i in range(len(plans)):
        assignments.append(plans[i].assignment)
    pickle.dump(assignments, open('assignments_' + str(n) + '.p', 'wb'))
def calculate_split(ensemble):
    split = defaultdict(int)
    for plan in ensemble:
        precincts = plan.graph.nodes
        dem_winners = 0
        rep_winners = 0
        for district in plan.parts:
            dem_votes = sum([precincts[precinct]["2020VBIDEN"] for precinct in plan.parts[district]])
            rep_votes = sum([precincts[precinct]["2020VTRUMP"] for precinct in plan.parts[district]])
            if dem_votes > rep_votes:
                dem_winners += 1
            else:
                rep_winners += 1
        split[str(dem_winners) + "/" + str(rep_winners)] += 1
    with open("ensemble_split.json", "w") as outfile:
        json.dump(split, outfile)

def map_incumbents(plan_new, incumbents):
    graph_20 = Graph.from_json('./graphGA20.json')
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    incumbent_mappings = []
    for i in range(len(incumbents)):
        mapping = dict()
        mapping["name"] = incumbents["Name"][i]
        mapping["party"] = incumbents["Party"][i]
        for node in plan_20.graph.nodes:
            if plan_20.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_20"] = plan_20.assignment[node]
        for node in plan_new.graph.nodes:
            if plan_new.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_new"] = plan_new.assignment[node]
        incumbent_mappings.append(mapping)
    return incumbent_mappings
def compare_plan_to_2020(plan_20, plan_new, incumbent_mappings):
    changes = ["VAPTOTAL", "ALAND20", "VAPBLACK", "2020VBIDEN", "2020VTRUMP"]
    for i in range(len(incumbent_mappings)):
        id_20 = incumbent_mappings[i]["id_20"]
        id_new = incumbent_mappings[i]["id_new"]
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        for change in changes:
            common = sum([plan_20.graph.nodes[x][change] for x in intersection])
            incumbent_mappings[i][change + "_common"] = int(common)
            tot_plan_20 = sum([plan_20.graph.nodes[x][change] for x in plan_20.parts[id_20]])
            tot_plan_new = sum([plan_new.graph.nodes[x][change] for x in plan_new.parts[id_new]])
            added = tot_plan_new - common
            incumbent_mappings[i][change + "_added"] = int(added)
            lost = tot_plan_20 - common
            incumbent_mappings[i][change + "_lost"] = int(lost)
    gdf = gpd.read_file("./mergedGAP.geojson")
    gdf = gdf.drop(columns='district_id_21')
    new_districts = [0 for x in range(len(gdf))]
    for i in range(len(plan_new)):
        for j in plan_new.parts[i]:
            new_districts[j] = i
    gdf["new_districts"] = new_districts
    gdf.set_geometry("geometry")
    gdf_new = gdf.dissolve(by="new_districts",aggfunc={key: 'sum' for key in filter(lambda x: x in "POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  2020VTRUMP  2020VBIDEN".split(), list(gdf.columns))})
    new_cols = ["id_20"]
    for change in changes:
        new_cols.append(change + "_common")
        new_cols.append(change + "_added")
        new_cols.append(change + "_lost")
    for col in new_cols:
        gdf_new[col] = None
    for mapping in incumbent_mappings:
        for col in new_cols:
            gdf_new[col][mapping['id_new']] = mapping[col]
    gdf_new.to_file('generated_district.geojson', driver='GeoJSON')
def combine_plans(plans_lists):
    combined_plans = []
    for plans_list in plans_lists:
        combined_plans += plans_list
    return combined_plans
if __name__ == '__main__':
    num_cores = 4
    args = [i for i in range(num_cores)]
    processes = []
    for arg in args:
        p = multiprocessing.Process(target=create_partitions, args=[arg])
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    #ensemble = combine_plans(plans_lists)
    #calculate_split(ensemble)
    #graph_20 = Graph.from_json('./graphGA20.json')
    #plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    #incumbents = pd.read_csv('./data/GA/incumbents_GA.csv')
    #plan_new = ensemble[-1]
    #incumbent_mappings = map_incumbents(plan_new, incumbents)
    #compare_plan_to_2020(plan_20, plan_new, incumbent_mappings)
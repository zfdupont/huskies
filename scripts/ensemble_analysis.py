import pickle
from gerrychain import(GeographicPartition, Graph, MarkovChain,
                        updaters, constraints, accept, Election)
import pandas as pd
from collections import defaultdict
import json
import numpy as np
#get the ensemble of district plans
def get_ensemble():
    graph = Graph.from_json('./graphGA.json') #get the graph
    assignments = [] #list of assignments to fill
    for i in range(4):
        some_assignments = pickle.load(open('assignments_' + str(i) + '.p', 'rb')) #load a pickled list of assignments
        assignments += some_assignments #append the list to assignments
    ensemble = [] #create the ensemble list
    for a in assignments:
        #get a district plan by combining the graph with an assignment and add it to the ensemble
        ensemble.append(GeographicPartition(graph, a))
    return ensemble
#setup the dictionary for box-and-whisker data
def setup_b_w_data(num_incumbents):
    #properties to gather data for
    properties = ["geo_variations","pop_variations","VAPBLACK_percentages"]
    b_w_data = {}
    #create a list of empty lists for each property equal to the number of incumbents
    for property in properties:
        b_w_data[property] = [[] for x in range(num_incumbents)]
    return b_w_data
#create a mapping of incumbents to each district plan
def map_incumbents(plan_20, plan_new, incumbents):
    incumbent_mappings = {} #dictionary of mappings
    for i in range(len(incumbents)):
        mapping = dict() #dictionary containing one mapping
        mapping["party"] = incumbents["Party"][i] #add the incumbent party to the mapping
        #add the 2020 district plan number to the mapping by finding the assignment of the node with the same GEOID20 as the incumbent
        for node in plan_20.graph.nodes:
            if plan_20.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_20"] = plan_20.assignment[node]
        #add the new district plan number to the mapping by finding the assignment of the node with the same GEOID20 as the incumbent
        for node in plan_new.graph.nodes:
            if plan_new.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_new"] = plan_new.assignment[node]
        incumbent_mappings[incumbents["Name"][i]] = mapping
    return incumbent_mappings
#find the party split of incumbent winners in a district plan
def calculate_split(plan, incumbent_mappings):
    precincts = plan.graph.nodes
    dem_winners = 0
    rep_winners = 0
    #use already_seen list to avoid giving a party multiple wins if two incumbents of one party map to one district and win
    already_seen = [False for x in range(len(plan.parts))]
    for incumbent in incumbent_mappings:
        mapping = incumbent_mappings[incumbent]
        district = mapping["id_new"]
        #if the incumbent winner of the district is already determined, move on to next incumbent
        if already_seen[district] == True:
            continue
        #sum votes for each party
        dem_votes = sum([precincts[precinct]["2020VBIDEN"] for precinct in plan.parts[district]])
        rep_votes = sum([precincts[precinct]["2020VTRUMP"] for precinct in plan.parts[district]])
        #find party of incumbent
        party = incumbent_mappings[incumbent]["party"]
        #increment winners of incumbent's party if incumbent won
        if dem_votes > rep_votes and party == "D":
            dem_winners += 1
            already_seen[district] = True
        elif rep_votes > dem_votes and party == "R":
            rep_winners += 1
            already_seen[district] = True
    #returns the party split of incumbent winners and the total amount of incumbent winners
    return str(dem_winners) + "/" + str(rep_winners), rep_winners + dem_winners
def calc_summary_data(plan_20, plan_new, incumbent_mappings, incumbent_summary_data, b_w_data):
    #variation properties needed
    variations_needed = ["VAPTOTAL", "ALAND20"]
    #lists of data to store into b_w_data
    b_w_lists = {"geo_variations":[], "pop_variations":[],"VAPBLACK_percentages":[]}
    for incumbent in incumbent_mappings:
        id_20 = incumbent_mappings[incumbent]["id_20"]
        id_new = incumbent_mappings[incumbent]["id_new"]
        #find the precincts in the intersection of the 2020 and new plan's districts
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        for variation in variations_needed:
            #calculate the variance
            common = sum([plan_20.graph.nodes[x][variation] for x in intersection])
            tot_plan_20 = sum([plan_20.graph.nodes[x][variation] for x in plan_20.parts[id_20]])
            tot_plan_new = sum([plan_new.graph.nodes[x][variation] for x in plan_new.parts[id_new]])
            added = tot_plan_new - common
            lost = tot_plan_20 - common
            variance = 100 * (1 - common / (common + added  + lost))
            #determine the property to update
            if variation == "VAPTOTAL":
                property = "pop_variations"
            else:
                property = "geo_variations"
            #update the incumbent summary data
            incumbent_summary_data[incumbent][property].append(variance)
            #update b_w_lists
            b_w_lists[property].append(variance)
        demographics_needed = ["VAPBLACK"]
        for demographic in demographics_needed:
            #calculate the percentage of the population that is of that demographic
            demographic_sum = sum([plan_new.graph.nodes[x][demographic] for x in plan_new.parts[id_new]])
            pop_sum = sum([plan_new.graph.nodes[x]["VAPTOTAL"] for x in plan_new.parts[id_new]])
            percentage = 100 * demographic_sum / pop_sum
            #update incumbent summary data
            incumbent_summary_data[incumbent][demographic + "_percentages"].append(percentage)
            #update b_w_lists
            b_w_lists[demographic + "_percentages"].append(percentage)
        #use b_w_lists to update b_w_data
        update_b_w(b_w_lists, b_w_data)
#update b_w_data by sorting b_w_lists and placing items from each list into the corresponding list in b_w_data
def update_b_w(b_w_lists, b_w_data):
    for property in b_w_lists:
        sorted_list = sorted(b_w_lists[property])
        for i in range(len(sorted_list)):
            b_w_data[property][i].append(sorted_list[i])
#convert the lists in b_w_data into quartiles for box_and_whisker data
def find_quartiles(b_w_data):
    for property in b_w_data:
        for i in range(len(b_w_data[property])):
            curr_list = b_w_data[property][i]
            b_w_data[property][i] = list(np.percentile(curr_list,[0,25,50,75,100]))
#find the average amount geographic and population variation in the summary data
def find_averages(incumbent_summary_data):
    total_geo_var = 0
    total_pop_var = 0
    total_vars = 0
    for incumbent in incumbent_summary_data:
        total_geo_var += sum(incumbent_summary_data[incumbent]["geo_variations"])
        total_pop_var += sum(incumbent_summary_data[incumbent]["pop_variations"])
        total_vars += len(incumbent_summary_data[incumbent]["geo_variations"])
    return total_geo_var / total_vars, total_pop_var / total_vars
if __name__ == '__main__':
    ensemble = get_ensemble() #get the ensemble
    incumbents = pd.read_csv('./data/GA/incumbents_GA.csv') #read csv file of incumbents mapped to home precincts
    graph_20 = Graph.from_json('./graphGA20.json') #get the 2020 district plan graph
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20") #convert the graph to a partition using the 2020 district id
    winner_split = defaultdict(int) #create a dictionary to store the winner split data
    total_winners = 0
    incumbent_summary_data = {name:{"geo_variations":[],"pop_variations":[], "VAPBLACK_percentages":[]} for name in incumbents["Name"]}
    b_w_data = setup_b_w_data(len(incumbents))
    #loop through the plans of the ensemble
    for plan in ensemble:
        incumbent_mappings = map_incumbents(plan_20,plan,incumbents) #find the mapping of incumbents to districts in each plan
        split, winners = calculate_split(plan, incumbent_mappings)
        winner_split[split] += 1 #find the split of winners in the plan and update winner_split
        total_winners += winners
        calc_summary_data(plan_20, plan, incumbent_mappings, incumbent_summary_data, b_w_data)
    find_quartiles(b_w_data)
    average_geo_var, average_pop_var = find_averages(incumbent_summary_data)
    ensemble_summary = {"num_plans": len(ensemble), "num_incumbents": len(incumbents), "avg_incumbent_winners": total_winners / len(ensemble), "avg_geo_var":average_geo_var, "avg_pop_var":average_pop_var}
    ensemble_data = {"ensemble_summary": ensemble_summary, "winner_split": winner_split, "b_w_data": b_w_data, "incumbent_data": incumbent_summary_data}
    with open("ensemble_data.json", "w") as outfile:
        json.dump(ensemble_data, outfile)
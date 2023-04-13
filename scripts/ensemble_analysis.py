import pickle
from gerrychain import(GeographicPartition, Graph, MarkovChain,
                        updaters, constraints, accept, Election)
import pandas as pd
from collections import defaultdict
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
#create a mapping of incumbents to each district plan
def map_incumbents(plan_20, plan_new, incumbents):
    incumbent_mappings = [] #list of mappings
    for i in range(len(incumbents)):
        mapping = dict() #dictionary containing one mapping
        mapping["name"] = incumbents["Name"][i] #add the incumbent name to the mapping
        mapping["party"] = incumbents["Party"][i] #add the incumbent party to the mapping
        #add the 2020 district plan number to the mapping by finding the assignment of the node with the same GEOID20 as the incumbent
        for node in plan_20.graph.nodes:
            if plan_20.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_20"] = plan_20.assignment[node]
        #add the new district plan number to the mapping by finding the assignment of the node with the same GEOID20 as the incumbent
        for node in plan_new.graph.nodes:
            if plan_new.graph.nodes[node]["GEOID20"] == incumbents["GEOID20"][i]:
                mapping["id_new"] = plan_new.assignment[node]
        incumbent_mappings.append(mapping)
    return incumbent_mappings
#find the party split of incumbent winners in a district plan
#still in progress
def calculate_split(plan):
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
    return str(dem_winners) + "/" + str(rep_winners)
if __name__ == '__main__':
    ensemble = get_ensemble() #get the ensemble
    incumbents = pd.read_csv('./data/GA/incumbents_GA.csv') #read csv file of incumbents mapped to home precincts
    graph_20 = Graph.from_json('./graphGA20.json') #get the 2020 district plan graph
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20") #convert the graph to a partition using the 2020 district id
    winner_split = defaultdict(int) #create a dictionary to store the winner split data
    #loop through the plans of the ensemble
    for plan in ensemble:
        incumbent_mappings = map_incumbents(plan_20,plan,incumbents) #find the mapping of incumbents to districts in each plan
        winner_split[calculate_split(plan)] += 1 #find the split of winners in the plan and update winner_split
    print(winner_split)
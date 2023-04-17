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
def create_partitions(n, state):
    graph = Graph.from_json('./generated/' + state + '/preprocess/graph' + state + '.json')
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
    #creates some district plans and appends them to plans
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
    #creates a list of plan assignments
    assignments = []
    #append each plan's assignment to assignments
    #note that all the plans have the same graph, so graph does not need to be saved
    for i in range(len(plans)):
        assignments.append(plans[i].assignment)
    #pickle the assignments into a file for later ensemble analysis
    pickle.dump(assignments, open('./generated/'+ state + '/assignments/assign_' + state + '_' + str(n) + '.p', 'wb'))
def generate_plans(state):
    num_cores = 4 #set to number of cores in system
    args = [[i,state] for i in range(num_cores)] #numbering for each process
    processes = [] #list of processes
    for arg in args:
        p = multiprocessing.Process(target=create_partitions, args=arg) #create a parallel process
        processes.append(p) #add the process to the list
        p.start() #run the process
    for p in processes:
        p.join() #end the process
def generate_all_plans():
    generate_plans("GA")
    generate_plans("NY")
    generate_plans("IL")
if __name__ == '__main__':
    generate_all_plans()
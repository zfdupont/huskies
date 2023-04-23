from gerrychain import(GeographicPartition, Graph, MarkovChain, updaters, constraints, accept)
from gerrychain.proposals import recom
from functools import partial
import multiprocessing
import pickle
import math
import random
from settings import HUSKIES_HOME
def create_partitions(n, state, num_plans, recom_steps):
    random.seed(n)
    graph = Graph.from_json(f'{HUSKIES_HOME}/generated/' + state + '/preprocess/graph' + state + '.json')
    pop_updater = {"population": updaters.Tally("pop_total", alias="population")}
    initial_partition = GeographicPartition(graph, assignment="district_id_21", updaters=pop_updater)
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
    proposal = partial(recom,
                    pop_col="pop_total",
                    pop_target=ideal_population,
                    epsilon=0.05,
                    node_repeats=2
                    )
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(initial_partition["cut_edges"])
    )
    pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.05)
    plans = []
    for i in range(num_plans):
        chain = MarkovChain(
            proposal=proposal,
            constraints=[
                pop_constraint,
                compactness_bound
            ],
            accept=accept.always_accept,
            initial_state=initial_partition,
            total_steps=recom_steps
        )
        for plan in chain:
            pass
        plans.append(chain.state)
    assignments = []
    for i in range(len(plans)):
        assignments.append(plans[i].assignment)
    pickle.dump(assignments, open(f'{HUSKIES_HOME}/generated/'+ state + '/assignments/assign_' + state + '_' + str(n) + '.p', 'wb'))
def generate_plans(state, num_cores, total_plans, recom_steps):
    num_plans = math.ceil(total_plans / num_cores)
    args = [[i,state, num_plans, recom_steps] for i in range(num_cores)]
    processes = set()
    for arg in args:
        p = multiprocessing.Process(target=create_partitions, args=arg)
        processes.add(p)
        p.start()
    for p in processes:
        p.join()
def generate_all_plans():
    num_cores = multiprocessing.cpu_count()
    total_plans = 8
    recom_steps = 20
    generate_plans("GA", num_cores, total_plans, recom_steps)
    generate_plans("NY", num_cores, total_plans, recom_steps)
    generate_plans("IL", num_cores, total_plans, recom_steps)
if __name__ == '__main__':
    generate_all_plans()
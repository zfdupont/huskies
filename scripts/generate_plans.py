from gerrychain import(GeographicPartition, Graph, MarkovChain, updaters, constraints, accept)
from gerrychain.proposals import recom
from functools import partial
import multiprocessing
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
import pickle
import math
import random
from uuid import uuid4
from time import time
from settings import HUSKIES_HOME, TOTAL_PLANS, RECOM_STEPS


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_partitions(id, state, num_plans, recom_steps):
    random.seed(id)
    graph = Graph.from_json(f'{HUSKIES_HOME}/generated/{state}/preprocess/graph{state}.json')
    pop_updater = {"population": updaters.Tally("pop_total", alias="population")}
    initial_partition = GeographicPartition(graph, assignment="district_id_21", updaters=pop_updater)
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
    POP_PERCENT_ALLOWED = 0.05
    NODE_REPEATS = 2
    proposal = partial(recom,
                    pop_col="pop_total",
                    pop_target=ideal_population,
                    epsilon=POP_PERCENT_ALLOWED,
                    node_repeats=NODE_REPEATS
                    )
    CUT_EDGES_MULTIPLIER = 2
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        CUT_EDGES_MULTIPLIER*len(initial_partition["cut_edges"])
    )
    pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, POP_PERCENT_ALLOWED)
    plans = []
    for _ in range(num_plans):
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
        for plan in chain: pass
        plans.append(chain.state)
    assignments = [p.assignment for p in plans]
    pickle.dump(assignments, 
                open(f'{HUSKIES_HOME}/generated/{state}/assignments/{state}_{id}.p', 'wb'))
    return state
def generate_plans(state, num_cores, total_plans, recom_steps):
    num_plans_per_core = math.ceil(total_plans / num_cores)
    
    args = [[str(uuid4()),state, num_plans_per_core, recom_steps] for i in range(num_cores)]
    processes = set()
    for arg in args:
        p = multiprocessing.Process(target=create_partitions, args=arg)
        processes.add(p)
        p.start()
    for p in processes:
        p.join()
def generate_all_plans():
    num_cores = multiprocessing.cpu_count()
    num_plans_per_core = math.ceil(TOTAL_PLANS / num_cores)
    
    # generate_plans("GA", num_cores, TOTAL_PLANS, RECOM_STEPS)
    # generate_plans("NY", num_cores, TOTAL_PLANS, RECOM_STEPS)
    # generate_plans("IL", num_cores, TOTAL_PLANS, RECOM_STEPS)
    
    # Creates 5 times as many workers as available CPUs
    with ThreadPoolExecutor() as exec:
        try: 
            futures = [
                exec.submit(create_partitions, args=[str(uuid4().hex), "GA", num_plans_per_core, RECOM_STEPS]),
                exec.submit(create_partitions, args=[str(uuid4().hex), "NY", num_plans_per_core, RECOM_STEPS]), 
                exec.submit(create_partitions, args=[str(uuid4().hex), "IL", num_plans_per_core, RECOM_STEPS])
            ]
            for future in as_completed(futures):
                logger.info(f"{num_plans_per_core} for {future.result()} completed!")
        except BrokenProcessPool as ex:
            logger.error(f"{ex} -- Limited System Resources")
if __name__ == '__main__':
    print("generating plans...")
    generate_all_plans()
    print("generation complete!")
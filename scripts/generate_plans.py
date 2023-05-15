from gerrychain import(GeographicPartition, Graph, MarkovChain, updaters, constraints, accept)
from gerrychain.proposals import recom
from functools import partial
import multiprocessing
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
import pickle
import math
import random
from uuid import uuid4
import os
from settings import HUSKIES_HOME, TOTAL_PLANS, RECOM_STEPS, NODE_COUNT


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_partitions(id, state, num_plans, recom_steps):
    def create_plans() -> GeographicPartition:
        nonlocal proposal, pop_constraint, compactness_bound, initial_partition
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
        return chain.state
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
    assignments = []
    with ProcessPoolExecutor as exec:
        try:
            futures = [
                exec.submit(create_plans) for _ in range(num_plans)
            ]
            for future in as_completed(futures):
                assignments.append(future.result().assignment)
        except Exception as e:
            logger.error("Error while creating plans for %s:", state, exc_info=1)
            exit(-1)
    pickle.dump(assignments, 
                open(f'{HUSKIES_HOME}/generated/{state}/assignments/{state}_{id}.p', 'wb'))
    logger.info("%s created in process %s", num_plans, os.getpid())

def generate_all_plans():
    num_cores = multiprocessing.cpu_count()
    logger.info("num cores available: %s", num_cores)
    with ProcessPoolExecutor(max_workers=3) as exec:
        try: 
            futures = [
                exec.submit(create_partitions, str(uuid4().hex), "GA", TOTAL_PLANS, RECOM_STEPS),
                exec.submit(create_partitions, str(uuid4().hex), "NY", TOTAL_PLANS, RECOM_STEPS),
                exec.submit(create_partitions, str(uuid4().hex), "IL", TOTAL_PLANS, RECOM_STEPS),
            ]
        except BrokenProcessPool as ex:
            logger.error(f"{ex} -- Limited System Resources")
            exit(-1)
if __name__ == '__main__':
    print("generating plans...")
    generate_all_plans()
    print("generation complete!")
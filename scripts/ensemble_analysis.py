import pickle
from gerrychain import(GeographicPartition, Graph, MarkovChain,
                        updaters, constraints, accept, Election)
import pandas as pd
def map_incumbents(plan_20, plan_new, incumbents):
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
if __name__ == '__main__':
    graph = Graph.from_json('./graphGA.json')
    assignments = []
    for i in range(4):
        some_assignments = pickle.load(open('assignments_' + str(i) + '.p', 'rb'))
        assignments += some_assignments
    print(assignments)
    ensemble = []
    for a in assignments:
        ensemble.append(GeographicPartition(graph, a))
    incumbents = pd.read_csv('./data/GA/incumbents_GA.csv')
    graph_20 = Graph.from_json('./graphGA20.json')
    plan_20 = GeographicPartition(graph_20, assignment="district_id_20")
    for plan in ensemble:
        incumbent_mappings = map_incumbents(plan_20,plan,incumbents)
        print("mapping")
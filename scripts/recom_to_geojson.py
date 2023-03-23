import pandas
import geopandas as gpd
from rtree import index
import matplotlib.pyplot as plt
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.proposals import recom
from gerrychain.updaters import Tally
from functools import partial
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import shapely
#read the geojson file, change crs for feet distances
print("reading")
gdf = gpd.read_file('./mergedIL.geojson')
gdf = gdf.to_crs("epsg:2248")
#r tree setup
print("finding adjacencies")
idx = index.Index()
for i, geometry in enumerate(gdf.geometry):
    #store the left, right, up, down boundaries of each geometry alongside index
    idx.insert(i, geometry.bounds)
#neighbors (edges) list
neighbors = {}
for i, polygon in enumerate(gdf.geometry):
    # Get the bounds of the polygon
    bounds = polygon.bounds
    
    # Find the intersecting bounds in the index
    intersecting = list(idx.intersection(bounds))
    
    # Get the neighbors by checking for intersection with other polygons
    neighbors[i] = []
    for j in intersecting:
        if i != j:
            other_polygon = gdf.iloc[j].geometry
            if polygon.intersection(other_polygon).length >= 200:
                neighbors[i].append(j)
#create gerrychain grain using neighbors as edges
print("creating graph")
graph = Graph(neighbors)
#add in the geodataframe data
graph.add_data(gdf)
#set the graph geometry attribute
graph.geometry = gdf.geometry
#election to keep track of
print("running MGGG Recom")
elections = [Election("PRE20", {"Democratic": "2020VBIDEN", "Republican": "2020VTRUMP"})]
#also track total population, total VAP, and black VAP
my_updaters = {"population": updaters.Tally("POPTOT", alias="population"),"black_vap": updaters.Tally("VAPBLACK", alias="black_vap"),"total_vap": updaters.Tally("VAPTOTAL", alias="total_vap")}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)
#use district_id from preprocessing for initial partition
initial_partition = GeographicPartition(graph, assignment="district_id", updaters=my_updaters)
#ideal population is the total population divided by number of districts
ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
proposal = partial(recom,
                   pop_col="POPTOT",
                   pop_target=ideal_population,
                   epsilon=0.02,
                   node_repeats=2
                  )
#compactness constraint
compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]),
    2*len(initial_partition["cut_edges"])
)
#keep the populations within 2% of the ideal population
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.02)
#run the chain
chain = MarkovChain(
    proposal=proposal,
    constraints=[
        pop_constraint,
        compactness_bound
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=100
)
for state in chain:
    pass

final_plan = chain.state

new_districts = [0 for x in range(len(gdf))]
for i in range(len(final_plan)):
  for j in final_plan.parts[i]:
    new_districts[j] = i
gdf["new_districts"] = new_districts
gdf.set_geometry("geometry")
gdf_new = gdf.dissolve(by='new_districts')
gdf_new.to_file("district_plan.geojson", driver="GeoJSON")
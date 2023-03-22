#pip install numpy pandas shapely fiona pyproj packaging geopandas maup rtree gerrychain
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
#read the geojson file, change crs for feet distances
print("reading")
gdf = gpd.read_file('./mergedGA.geojson')
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
            inter = polygon.intersection(other_polygon.buffer(200))
            if inter.geom_type == "Polygon" and inter.length / 2 >= 200:
                neighbors[i].append(j)
            elif inter.length >= 200:
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
    total_steps=200
)
#print election result data
print("printing election results")
total_d = 0
total_r = 0
counter = 0
highest_d = 0
highest_r = 0
for partition in chain:
  dems = partition["PRE20"].percents("Democratic")
  winner_d = 0
  for x in dems:
    if x > 0.5:
      winner_d += 1
  winner_r = len(partition) - winner_d
  total_d += winner_d
  total_r += winner_r
  counter += 1
  highest_d = max(highest_d, winner_d)
  highest_r = max(highest_r, winner_r)
print("Average:")
print("Democrats:", total_d / counter, "Republicans:", total_r / counter)
print("Best Result for Democrats:")
print("Democrats:", highest_d, "Republicans:", len(partition) - highest_d)
print("Best Result for Republicans:")
print("Democrats:", len(partition) - highest_r, "Republicans:", highest_r)
print("plotting")
#navigate to plan #25
counter = 25
for plan in chain:
  counter -= 1
  if counter == 0:
    new_plan = plan
    break
#plot the plan
fig, ax = plt.subplots(figsize=(8, 8))
new_plan.plot(ax=ax,cmap="tab20")
plt.axis('off')
plt.show()
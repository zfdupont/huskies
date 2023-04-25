import geopandas as gpd
from rtree import index
from gerrychain import Graph
from networkx import connected_components
from settings import HUSKIES_HOME
def get_precincts(path):
    precincts = gpd.read_file(path)
    FEET_CRS = "epsg:2248"
    precincts = precincts.to_crs(FEET_CRS)
    return precincts
def find_neighbors(precincts):
    idx = index.Index()
    for i, geometry in enumerate(precincts.geometry):
        idx.insert(i, geometry.bounds)
    neighbors = {}
    for i, polygon in enumerate(precincts.geometry):
        bounds = polygon.bounds
        intersecting = list(idx.intersection(bounds))
        neighbors[i] = set()
        for j in intersecting:
            if i != j:
                other_polygon = precincts.iloc[j].geometry
                NEIGHBOR_DISTANCE_MAX = 200
                if polygon.distance(other_polygon) < NEIGHBOR_DISTANCE_MAX:
                    neighbors[i].add(j)
    return neighbors
def make_graph(neighbors, path, precincts):
    graph = Graph(neighbors)
    graph.add_data(precincts)
    graph.geometry = precincts.geometry
    components = list(connected_components(graph))
    biggest_component_size = max(len(c) for c in components)
    islands = [c for c in components if len(c) != biggest_component_size]
    for component in islands:
        for node in component:
            graph.remove_node(node)
    graph.to_json(path, include_geometries_as_geojson=True)
def neighbors(state):
    statePath = f'{HUSKIES_HOME}/generated/{state}/preprocess/'
    precincts = get_precincts(f'{statePath}merged{state}P.geojson')
    neighbors = find_neighbors(precincts)
    make_graph(neighbors, f'{statePath}graph{state}.json', precincts)
    precincts_20 = get_precincts(f'{statePath}merged{state}P20.geojson')
    neighbors = find_neighbors(precincts_20)
    make_graph(neighbors, f'{statePath}graph{state}20.json', precincts_20)
def neighbors_all():
    neighbors('NY')
    neighbors('GA')
    neighbors('IL')
if __name__ == '__main__':
    neighbors_all()
import geopandas as gpd
from rtree import index
from gerrychain import Graph
def get_precincts(path):
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs("epsg:2248")
    return gdf
def find_neighbors(gdf):
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
                if polygon.distance(other_polygon) < 200:
                    neighbors[i].append(j)
    return neighbors
def make_graph(neighbors, path, gdf):
    graph = Graph(neighbors)
    graph.add_data(gdf)
    graph.geometry = gdf.geometry
    graph.to_json(path, include_geometries_as_geojson=True)
def neighbors_NY():
    gdf = get_precincts('./mergedNYP.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphNY.json', gdf)
    gdf = get_precincts('./mergedNYP20.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphNY20.json', gdf)
def neighbors_GA():
    gdf = get_precincts('./mergedGAP.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphGA.json', gdf)
    gdf = get_precincts('./mergedGAP20.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphGA20.json', gdf)
def neighbors_IL():
    gdf = get_precincts('./mergedILP.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphIL.json', gdf)
    gdf = get_precincts('./mergedILP20.geojson')
    neighbors = find_neighbors(gdf)
    make_graph(neighbors, './graphIL20.json', gdf)
def neighbors_all():
    neighbors_NY()
    neighbors_GA()
    neighbors_IL()
if __name__ == '__main__':
    neighbors_all()
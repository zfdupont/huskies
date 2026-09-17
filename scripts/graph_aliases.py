# Adapter for the on-disk (Oct 2023) precinct graphs, which store raw uppercase
# Census/election column names. The current analysis scripts (ensemble_analysis,
# enacted_analysis, plan_analysis, interesting_plan) read the lowercase naming
# produced by merge_data.py. To analyze the preserved ensemble without rebuilding
# the graphs (which would invalidate the existing assignments), inject lowercase
# aliases onto the graph nodes immediately after loading.
#
# Only fields actually read off the graph are mapped. GeoJSON reads (merged*P.geojson)
# already use the lowercase names and are untouched.
GRAPH_FIELD_ALIASES = {
    "democrat": "2020VBIDEN",
    "republican": "2020VTRUMP",
    "geoid20": "GEOID20",
    "area": "ALAND20",
    "pop_total": "POPTOT",
    "vap_total": "VAPTOTAL",
    "vap_white": "VAPWHITE",
    "vap_black": "VAPBLACK",
    "vap_hisp": "VAPHISP",
}


def add_lowercase_aliases(graph):
    """Copy uppercase node attributes to their lowercase analysis names, in place."""
    for node_id in graph.nodes:
        node = graph.nodes[node_id]
        for lower, upper in GRAPH_FIELD_ALIASES.items():
            if lower not in node and upper in node:
                node[lower] = node[upper]
    return graph


def normalize_zero_indexed(graph, field):
    """Shift a district-id field so it starts at 0, in place.

    The on-disk graphs are inconsistent: GA/IL number district_id_21 from 0,
    but NY numbers from 1. enacted_analysis assumes 0-based (its -1 election
    correction and the 0-based GeoJSON dissolve both rely on it), so normalize
    the field to a 0-based contiguous range. No-op when already 0-based.
    """
    values = [graph.nodes[n][field] for n in graph.nodes
              if graph.nodes[n].get(field) is not None]
    if not values:
        return graph
    offset = min(values)
    if offset != 0:
        for n in graph.nodes:
            if graph.nodes[n].get(field) is not None:
                graph.nodes[n][field] -= offset
    return graph

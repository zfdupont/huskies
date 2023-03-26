import sys
import geopandas as gpd
from collections import defaultdict
import json
def compare_plans(dataPath, plan1, plan2):
    gdf = gpd.read_file(dataPath) #read the precincts geojson file, must contain plan1 and plan2 as attributes for each precinct
    districts1 = defaultdict(set) #contains a dictionary mapping districts to the set of districts to precincts for plan 1
    districts2 = defaultdict(set) #prev but for plan 2
    for x in range(0, len(gdf[plan1])):
        districts1[gdf[plan1][x]].add(x)
    for x in range(0, len(gdf[plan2])):
        districts2[gdf[plan2][x]].add(x)
    distr_comp = defaultdict(dict) #contains all comparison data
    for x in districts1:
        #get intersections and attempt to map districts to each other
        intersections = dict()
        for y in districts2:
            inter = districts1[x].intersection(districts2[y])
            if len(inter) > 0:
                intersections[y] = inter
        pops = dict()
        for a in intersections:
            pops[a] = sum([gdf["POPTOT"][x] for x in intersections[a]])
        best_pop = 0
        best_id = 0
        for a in pops:
            if pops[a] > best_pop:
                best_id = a
                best_pop = pops[a]
        distr_comp[int(best_id)]["2020_id"] = int(x)
        #find demographic differences and similarities between districtp lans
        changes = ["VAPTOTAL", "ALAND20", "VAPBLACK"]
        for change in changes:
            common = sum([gdf[change][x] for x in intersections[best_id]])
            distr_comp[int(best_id)][change + "_common"] = int(common)
            tot_plan_1 = sum([gdf[change][x] for x in districts1[x]])
            #distr_comp[int(best_id)][change + "_tot_plan_1"] = int(tot_plan_1)
            tot_plan_2 = sum([gdf[change][x] for x in districts2[best_id]])
            #distr_comp[int(best_id)][change + "_tot_plan_2"] = int(tot_plan_2)
            added = tot_plan_2 - common
            distr_comp[int(best_id)][change + "_added"] = int(added)
            lost = tot_plan_1 - common
            distr_comp[int(best_id)][change + "_lost"] = int(lost)
            #variance = (added + lost) / (added + lost + common) * 100
            #distr_comp[int(best_id)][change + "_variance"] = float(variance)
    gdf = gdf.drop(columns=plan1)
    gdf = gdf.dissolve(by=plan2,
                       aggfunc={
                           key: 'sum' for key in filter(lambda x: x in "POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  2020VTRUMP  2020VBIDEN".split(), list(gdf.columns))
                       })
    for prop in distr_comp[0]:    
        l = [0 for x in range(len(distr_comp))]
        for i in distr_comp:
            l[i] = distr_comp[i][prop]
        gdf[prop] = l
    gdf.to_file('district_compared.geojson', driver='GeoJSON')
if __name__ == '__main__':
    dataPath = sys.argv[1]
    plan1 = sys.argv[2]
    plan2 = sys.argv[3]
    compare_plans(dataPath, plan1, plan2)
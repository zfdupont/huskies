import geopandas as gpd
from settings import HUSKIES_HOME, DATABASE_URI
def analyze_plan(plan_20, plan_new, incumbent_mappings, state, reason):
    changes = ["vap_total", "area", "vap_black", "vap_white", "vap_hisp","democrat", "republican"]
    for incumbent in incumbent_mappings:
        id_20 = incumbent_mappings[incumbent]["id_20"]
        id_new = incumbent_mappings[incumbent]["id_new"]
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        for change in changes:
            common = sum([plan_20.graph.nodes[x][change] for x in intersection])
            incumbent_mappings[incumbent][change + "_common"] = int(common)
            tot_plan_20 = sum([plan_20.graph.nodes[x][change] for x in plan_20.parts[id_20]])
            tot_plan_new = sum([plan_new.graph.nodes[x][change] for x in plan_new.parts[id_new]])
            added = tot_plan_new - common
            incumbent_mappings[incumbent][change + "_added"] = int(added)
            lost = tot_plan_20 - common
            incumbent_mappings[incumbent][change + "_lost"] = int(lost)
            variation = added / (common + added)
            incumbent_mappings[incumbent][change + "_variation"] = variation
    gdf = gpd.read_file(f'{HUSKIES_HOME}/generated/'+ state +'/preprocess/merged'+ state +'P.geojson')
    gdf = gdf.drop(columns='district_id_21')
    new_districts = [0 for x in range(len(gdf))]
    for i in plan_new.parts:
        for j in plan_new.parts[i]:
            new_districts[j] = i
    gdf["district_id"] = new_districts
    gdf.set_geometry("geometry")
    if state == "NY":
        gdf = gdf.drop(7041)
    gdf_new = gdf.dissolve(by="district_id",aggfunc={key: 'sum' for key in filter(lambda x: x in "pop_total  vap_total  vap_white  vap_black  vap_native  vap_asian  vap_hwn  vap_other  vap_mixed  vap_hisp  republican  democrat".split(), list(gdf.columns))})
    new_cols = ["incumbent_party"]
    for change in changes:
        new_cols.append(change + "_common")
        new_cols.append(change + "_added")
        new_cols.append(change + "_lost")
        new_cols.append(change + "_variation")
    gdf_new["incumbent"] = None
    gdf_new["winner_party"] = None
    gdf_new["safe_seat"] = False
    for col in new_cols:
        gdf_new[col] = None
    for i in range(len(gdf_new)):
        dem_votes = gdf["democrat"][i]
        rep_votes = gdf["republican"][i]
        dem_proportion = dem_votes / (dem_votes + rep_votes)
        rep_proportion = rep_votes / (dem_votes + rep_votes)
        if dem_proportion > 0.5:
            gdf_new["winner_party"][i] = "D"
            if dem_proportion > 0.55:
                gdf_new["safe_seat"][i] = True
        else:
            gdf_new["winner_party"][i] = "R"
            if rep_proportion > 0.55:
                gdf_new["safe_seat"][i] = True
    for mapping in incumbent_mappings:
        gdf_new["incumbent"][incumbent_mappings[mapping]['id_new']] = mapping
        for col in new_cols:
            gdf_new[col][incumbent_mappings[mapping]['id_new']] = incumbent_mappings[mapping][col]
    return gdf_new
    #gdf_new.to_file(f'{HUSKIES_HOME}/generated/'+ state +'/interesting/'+ reason +'_plan.geojson', driver='GeoJSON')
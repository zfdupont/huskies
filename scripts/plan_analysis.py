import geopandas as gpd
def analyze_plan(plan_20, plan_new, incumbent_mappings, state, reason):
    changes = ["VAPTOTAL", "ALAND20", "VAPBLACK", "VAPWHITE", "VAPHISP","DEMOCRAT", "REPUBLICAN"]
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
    gdf = gpd.read_file('./generated/'+ state +'/preprocess/merged'+ state +'P.geojson')
    gdf = gdf.drop(columns='district_id_21')
    new_districts = [0 for x in range(len(gdf))]
    for i in range(len(plan_new)):
        for j in plan_new.parts[i]:
            new_districts[j] = i
    gdf["district_id"] = new_districts
    gdf.set_geometry("geometry")
    gdf_new = gdf.dissolve(by="district_id",aggfunc={key: 'sum' for key in filter(lambda x: x in "POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  REPUBLICAN  DEMOCRAT".split(), list(gdf.columns))})
    new_cols = ["IncumbentParty"]
    for change in changes:
        new_cols.append(change + "_common")
        new_cols.append(change + "_added")
        new_cols.append(change + "_lost")
    gdf_new["Incumbent"] = None
    for col in new_cols:
        gdf_new[col] = None
    for mapping in incumbent_mappings:
        gdf_new["Incumbent"][incumbent_mappings[mapping]['id_new']] = mapping
        for col in new_cols:
            gdf_new[col][incumbent_mappings[mapping]['id_new']] = incumbent_mappings[mapping][col]
    gdf_new.to_file('./generated/'+ state +'/interesting/'+ reason +'/generated_district.geojson', driver='GeoJSON')
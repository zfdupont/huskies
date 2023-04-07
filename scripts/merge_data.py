import pandas as pd
import geopandas as gpd
import maup
import asyncio
import numpy as np
from pathlib import Path
def get_bounds(path, columns):
    gdf = gpd.read_file(path)
    gdf = gdf[columns]
    return gdf
def get_data(path, columns):
    df = pd.read_csv(path,low_memory=False)
    df = df[columns]
    return df
def merge_data(gdf, column, data):
    for x in data:
        gdf = x.merge(gdf,on=column,how='left')
    return gdf
def assign_plan(precincts, path, label):
    districts = gpd.read_file(path)
    if districts.crs != precincts.crs:
        districts = districts.to_crs(precincts.crs)
    assignments = maup.assign(precincts, districts)
    precincts[label] = assignments
    return precincts
def aggregate(gdf, by, agg_list):
    gdf = gdf.dissolve(by=by,aggfunc={key: 'sum' for key in filter(lambda x: x in agg_list, list(gdf.columns))})
    return gdf
def merge_NY(src_path, agg):
    gdf = get_bounds(f"{src_path}/data/NY/ny_vtd_2020_bound.shp", ['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{src_path}/data/NY/ny_2020_2020_vtd.csv", ['GEOID20','R_2020_pres','D_2020_pres'])
    d_data = get_data(f"{src_path}/data/NY/ny_pl2020_vtd.csv", ['GEOID20','TOTAL_ADJ','TOTAL_VAP_ADJ','WHITE_VAP_ADJ','BLACK_VAP_ADJ','AMIND_VAP_ADJ','ASIAN_VAP_ADJ','HWN_VAP_ADJ','OTHER_VAP_ADJ','MULTI_VAP_ADJ','HISP_VAP_ADJ'])
    gdf['GEOID20']=gdf['GEOID20'].astype(np.int64)
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'R_2020_pres': '2020VTRUMP', 'D_2020_pres': '2020VBIDEN','TOTAL_ADJ':'POPTOT', 'TOTAL_VAP_ADJ':'VAPTOTAL', 'WHITE_VAP_ADJ':'VAPWHITE', 'BLACK_VAP_ADJ':'VAPBLACK','AMIND_VAP_ADJ':'VAPINAMORAK','ASIAN_VAP_ADJ':'VAPASIAN','HWN_VAP_ADJ':'VAPISLAND','OTHER_VAP_ADJ':'VAPOTHER','MULTI_VAP_ADJ':'VAPMIXED','HISP_VAP_ADJ':'VAPHISP'})
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf = gdf.drop(7041, axis=0)
    gdf = gdf.reset_index(drop=True)
    gdf = assign_plan(gdf, f'{src_path}/data/NY/CON22_June_03_2022.shp', 'district_id_21')
    gdf.to_file('mergedNYP.geojson', driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf, 'district_id_21', "POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  2020VTRUMP  2020VBIDEN".split())
        gdf.to_file('mergedNYD.geojson', driver='GeoJSON')
def merge_GA(src_path, agg):
    gdf = get_bounds(f'{src_path}/data/GA/ga_vtd_2020_bound.shp',['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{src_path}/data/GA/ga_2020_2020_vtd.csv",['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{src_path}/data/GA/ga_pl2020_vtd.csv",['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005','P0030006','P0030007','P0030008','P0030009','P0040002'])
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'G20PRERTRU': '2020VTRUMP', 'G20PREDBID': '2020VBIDEN', 'P0010001':'POPTOT','P0030001':'VAPTOTAL', 'P0030003':'VAPWHITE', 'P0030004':'VAPBLACK','P0030005':'VAPINAMORAK','P0030006':'VAPASIAN','P0030007':'VAPISLAND','P0030008':'VAPOTHER','P0030009':'VAPMIXED','P0040002':'VAPHISP'})
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf = assign_plan(gdf,f'{src_path}/data/GA/ga_cong_2011_to_2021.shp','district_id_21')
    gdf.to_file('mergedGAP.geojson', driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf,'district_id_21',"POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  2020VTRUMP  2020VBIDEN".split())
        gdf.to_file('mergedGAD.geojson', driver='GeoJSON')
def merge_IL(src_path, agg):
    gdf = get_bounds(f'{src_path}/data/IL/il_vtd_2020_bound.shp',['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{src_path}/data/IL/il_2020_2020_vtd.csv",['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{src_path}/data/IL/il_pl2020_vtd.csv",['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005','P0030006','P0030007','P0030008','P0030009','P0040002'])
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'G20PRERTRU': '2020VTRUMP', 'G20PREDBID': '2020VBIDEN', 'P0010001':'POPTOT','P0030001':'VAPTOTAL', 'P0030003':'VAPWHITE', 'P0030004':'VAPBLACK','P0030005':'VAPINAMORAK','P0030006':'VAPASIAN','P0030007':'VAPISLAND','P0030008':'VAPOTHER','P0030009':'VAPMIXED','P0040002':'VAPHISP'})
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf = assign_plan(gdf,f'{src_path}/data/IL/il_cong_2011_to_2021.shp','district_id_21')
    gdf.to_file("mergedILP.geojson", driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf,'district_id_21',"POPTOT  VAPTOTAL  VAPWHITE  VAPBLACK  VAPINAMORAK  VAPASIAN  VAPISLAND  VAPOTHER  VAPMIXED  VAPHISP  2020VTRUMP  2020VBIDEN".split())
        gdf.to_file('mergedILD.geojson', driver='GeoJSON')
def merge_all(agg):
    src_path = str(Path(__file__).parent)
    merge_NY(src_path, agg)
    merge_GA(src_path, agg)
    merge_IL(src_path, agg)
if __name__ == '__main__':
    merge_all(True)

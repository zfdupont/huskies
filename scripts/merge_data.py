import pandas as pd
import geopandas as gpd
import maup
import numpy as np
from settings import HUSKIES_HOME
def get_bounds(path, columns):
    bounds = gpd.read_file(path)
    bounds = bounds[columns]
    return bounds
def get_data(path, columns):
    data = pd.read_csv(path,low_memory=False)
    data = data[columns]
    return data
def merge_data(precincts, column, data):
    for x in data:
        precincts = x.merge(precincts,on=column,how='left')
    return precincts
def assign_plan(precincts, path, label):
    districts = gpd.read_file(path)
    if path == f'{HUSKIES_HOME}/data/NY/CON22_June_03_2022.shp':
        districts = districts.dissolve(by="DISTRICT")
        districts = districts.reset_index(drop=True)
    if districts.crs != precincts.crs:
        districts = districts.to_crs(precincts.crs)
    assignments = maup.assign(precincts, districts)
    precincts[label] = assignments
    return precincts
def merge_NY():
    bounds = get_bounds(f"{HUSKIES_HOME}/data/NY/ny_vtd_2020_bound.shp", 
                     ['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/NY/ny_2020_2020_vtd.csv", 
                      ['GEOID20','R_2020_pres','D_2020_pres'])
    d_data = get_data(f"{HUSKIES_HOME}/data/NY/ny_pl2020_vtd.csv", 
                      ['GEOID20','TOTAL_ADJ','TOTAL_VAP_ADJ','WHITE_VAP_ADJ',
                       'BLACK_VAP_ADJ','AMIND_VAP_ADJ','ASIAN_VAP_ADJ','HWN_VAP_ADJ',
                       'OTHER_VAP_ADJ','MULTI_VAP_ADJ','HISP_VAP_ADJ'])
    bounds['GEOID20']=bounds['GEOID20'].astype(np.int64)
    precincts = merge_data(bounds, "GEOID20", [e_data, d_data])
    precincts = precincts.rename(columns={'ALAND20':'area','R_2020_pres': 'republican', 
                              'D_2020_pres': 'democrat','TOTAL_ADJ':'pop_total', 
                              'TOTAL_VAP_ADJ':'vap_total', 'WHITE_VAP_ADJ':'vap_white', 
                              'BLACK_VAP_ADJ':'vap_black','AMIND_VAP_ADJ':'vap_native',
                              'ASIAN_VAP_ADJ':'vap_asian','HWN_VAP_ADJ':'vap_hwn',
                              'OTHER_VAP_ADJ':'vap_other','MULTI_VAP_ADJ':'vap_mixed',
                              'HISP_VAP_ADJ':'vap_hisp'})
    precincts.columns = precincts.columns.str.lower()
    precincts = gpd.GeoDataFrame(precincts, geometry='geometry')
    precincts_20 = assign_plan(precincts,f'{HUSKIES_HOME}/data/NY/ny_cong_2012_to_2021.shp','district_id_20')
    precincts_20.to_file(f'{HUSKIES_HOME}/generated/NY/preprocess/mergedNYP20.geojson', driver='GeoJSON')
    precincts_enacted = assign_plan(precincts, f'{HUSKIES_HOME}/data/NY/CON22_June_03_2022.shp', 'district_id_21')
    precincts_enacted.to_file(f'{HUSKIES_HOME}/generated/NY/preprocess/mergedNYP.geojson', driver='GeoJSON')
def merge_GA():
    bounds = get_bounds(f'{HUSKIES_HOME}/data/GA/ga_vtd_2020_bound.shp',
                     ['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/GA/ga_2020_2020_vtd.csv",
                      ['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{HUSKIES_HOME}/data/GA/ga_pl2020_vtd.csv",
                      ['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005',
                       'P0030006','P0030007','P0030008','P0030009','P0040002'])
    precincts = merge_data(bounds, "GEOID20", [e_data, d_data])
    precincts = precincts.rename(columns={'ALAND20':'area','G20PRERTRU': 'republican', 'G20PREDBID': 'democrat', 
                              'P0010001':'pop_total','P0030001':'vap_total', 'P0030003':'vap_white', 
                              'P0030004':'vap_black','P0030005':'vap_native','P0030006':'vap_asian',
                              'P0030007':'vap_hwn','P0030008':'vap_other','P0030009':'vap_mixed',
                              'P0040002':'vap_hisp'})
    precincts.columns = precincts.columns.str.lower()
    precincts = gpd.GeoDataFrame(precincts, geometry='geometry')
    precincts_20 = assign_plan(precincts,f'{HUSKIES_HOME}/data/GA/ga_cong_2011_to_2021.shp','district_id_20')
    precincts_20.to_file(f'{HUSKIES_HOME}/generated/GA/preprocess/mergedGAP20.geojson', driver='GeoJSON')
    precincts_enacted = assign_plan(precincts,f'{HUSKIES_HOME}/data/GA/GAD.geojson','district_id_21')
    precincts_enacted.to_file(f'{HUSKIES_HOME}/generated/GA/preprocess/mergedGAP.geojson', driver='GeoJSON')
def merge_IL():
    bounds = get_bounds(f'{HUSKIES_HOME}/data/IL/il_vtd_2020_bound.shp',
                     ['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/IL/il_2020_2020_vtd.csv",
                      ['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{HUSKIES_HOME}/data/IL/il_pl2020_vtd.csv",
                      ['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005',
                       'P0030006','P0030007','P0030008','P0030009','P0040002'])
    precincts = merge_data(bounds, "GEOID20", [e_data, d_data])
    precincts = precincts.rename(columns={'ALAND20':'area','G20PRERTRU': 'republican', 'G20PREDBID': 'democrat', 
                              'P0010001':'pop_total','P0030001':'vap_total', 'P0030003':'vap_white', 
                              'P0030004':'vap_black','P0030005':'vap_native','P0030006':'vap_asian',
                              'P0030007':'vap_hwn','P0030008':'vap_other','P0030009':'vap_mixed',
                              'P0040002':'vap_hisp'})
    precincts.columns = precincts.columns.str.lower()
    precincts = gpd.GeoDataFrame(precincts, geometry='geometry')
    precincts_20 = assign_plan(precincts,f'{HUSKIES_HOME}/data/IL/il_cong_2011_to_2021.shp','district_id_20')
    precincts_20.to_file(f'{HUSKIES_HOME}/generated/IL/preprocess/mergedILP20.geojson', driver='GeoJSON')
    precincts_enacted = assign_plan(precincts,f'{HUSKIES_HOME}/data/IL/ILD.geojson','district_id_21')
    precincts_enacted.to_file(f"{HUSKIES_HOME}/generated/IL/preprocess/mergedILP.geojson", driver='GeoJSON')
def merge_all():
    merge_NY()
    merge_GA()
    merge_IL()
if __name__ == '__main__':
    merge_all()
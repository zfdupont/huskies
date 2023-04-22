import pandas as pd
import geopandas as gpd
import maup
import numpy as np
from MongoEngine import MongoEngine
from settings import HUSKIES_HOME, DATABASE_URI

engine = MongoEngine("dev", uri=DATABASE_URI)

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
    if path == f'{HUSKIES_HOME}/data/NY/CON22_June_03_2022.shp':
        districts = districts.dissolve(by="DISTRICT")
    if districts.crs != precincts.crs:
        districts = districts.to_crs(precincts.crs)
    assignments = maup.assign(precincts, districts)
    precincts[label] = assignments
    return precincts
def aggregate(gdf : gpd.GeoDataFrame, by, agg_list):
    gdf = gdf.dissolve(by=by,aggfunc={key: 'sum' for key in filter(lambda x: x in agg_list, list(gdf.columns))})
    return gdf
def merge_NY(agg):
    gdf = get_bounds(f"{HUSKIES_HOME}/data/NY/ny_vtd_2020_bound.shp", ['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/NY/ny_2020_2020_vtd.csv", ['GEOID20','R_2020_pres','D_2020_pres'])
    d_data = get_data(f"{HUSKIES_HOME}/data/NY/ny_pl2020_vtd.csv", ['GEOID20','TOTAL_ADJ','TOTAL_VAP_ADJ','WHITE_VAP_ADJ','BLACK_VAP_ADJ','AMIND_VAP_ADJ','ASIAN_VAP_ADJ','HWN_VAP_ADJ','OTHER_VAP_ADJ','MULTI_VAP_ADJ','HISP_VAP_ADJ'])
    gdf['GEOID20']=gdf['GEOID20'].astype(np.int64)
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'ALAND20':'area','R_2020_pres': 'republican', 'D_2020_pres': 'democrat','TOTAL_ADJ':'pop_total', 'TOTAL_VAP_ADJ':'vap_total', 'WHITE_VAP_ADJ':'vap_white', 'BLACK_VAP_ADJ':'vap_black','AMIND_VAP_ADJ':'vap_native','ASIAN_VAP_ADJ':'vap_asian','HWN_VAP_ADJ':'vap_hwn','OTHER_VAP_ADJ':'vap_other','MULTI_VAP_ADJ':'vap_mixed','HISP_VAP_ADJ':'vap_hisp'})
    gdf.columns = gdf.columns.str.lower()
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf20 = assign_plan(gdf,f'{HUSKIES_HOME}/data/NY/ny_cong_2012_to_2021.shp','district_id_20')
    gdf20.to_file(f'{HUSKIES_HOME}/generated/NY/preprocess/mergedNYP20.geojson', driver='GeoJSON')
    gdf = assign_plan(gdf, f'{HUSKIES_HOME}/data/NY/CON22_June_03_2022.shp', 'district_id_21')
    gdf.to_file(f'{HUSKIES_HOME}/generated/NY/preprocess/mergedNYP.geojson', driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf, 'district_id_21', "pop_total  vap_total  vap_white  vap_black  vap_native  vap_asian  vap_hwn  vap_other  vap_mixed  vap_hisp  democrat  republican".split())
        engine.insert_geodataframe(gdf, 'plans', geojson_state='NY', geojson_name='Enacted')
        # gdf.to_file(f'{HUSKIES_HOME}/genereated/NY/preprocess/mergedNYD.geojson', driver='GeoJSON')
def merge_GA(agg):
    gdf = get_bounds(f'{HUSKIES_HOME}/data/GA/ga_vtd_2020_bound.shp',['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/GA/ga_2020_2020_vtd.csv",['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{HUSKIES_HOME}/data/GA/ga_pl2020_vtd.csv",['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005','P0030006','P0030007','P0030008','P0030009','P0040002'])
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'ALAND20':'area','G20PRERTRU': 'republican', 'G20PREDBID': 'democrat', 'P0010001':'pop_total','P0030001':'vap_total', 'P0030003':'vap_white', 'P0030004':'vap_black','P0030005':'vap_native','P0030006':'vap_asian','P0030007':'vap_hwn','P0030008':'vap_other','P0030009':'vap_mixed','P0040002':'vap_hisp'})
    gdf.columns = gdf.columns.str.lower()
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf20 = assign_plan(gdf,f'{HUSKIES_HOME}/data/GA/ga_cong_2011_to_2021.shp','district_id_20')
    gdf20.to_file(f'{HUSKIES_HOME}/generated/GA/preprocess/mergedGAP20.geojson', driver='GeoJSON')
    gdf = assign_plan(gdf,f'{HUSKIES_HOME}/data/GA/GAD.geojson','district_id_21')
    gdf.to_file(f'{HUSKIES_HOME}/generated/GA/preprocess/mergedGAP.geojson', driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf,'district_id_21',"pop_total  vap_total  vap_white  vap_black  vap_native  vap_asian  vap_hwn  vap_other  vap_mixed  vap_hisp  democrat  republican".split())
        engine.insert_geodataframe(gdf, 'plans', geojson_state='GA', geojson_name='Enacted')
        # gdf.to_file(f'{HUSKIES_HOME}/generated/GA/preprocess/mergedGAD.geojson', driver='GeoJSON')
def merge_IL(agg):
    gdf = get_bounds(f'{HUSKIES_HOME}/data/IL/il_vtd_2020_bound.shp',['NAME20','GEOID20','ALAND20','geometry'])
    e_data = get_data(f"{HUSKIES_HOME}/data/IL/il_2020_2020_vtd.csv",['GEOID20','G20PRERTRU','G20PREDBID'])
    d_data = get_data(f"{HUSKIES_HOME}/data/IL/il_pl2020_vtd.csv",['GEOID20','P0010001','P0030001','P0030003','P0030004','P0030005','P0030006','P0030007','P0030008','P0030009','P0040002'])
    gdf = merge_data(gdf, "GEOID20", [e_data, d_data])
    gdf = gdf.rename(columns={'ALAND20':'area','G20PRERTRU': 'republican', 'G20PREDBID': 'democrat', 'P0010001':'pop_total','P0030001':'vap_total', 'P0030003':'vap_white', 'P0030004':'vap_black','P0030005':'vap_native','P0030006':'vap_asian','P0030007':'vap_hwn','P0030008':'vap_other','P0030009':'vap_mixed','P0040002':'vap_hisp'})
    gdf.columns = gdf.columns.str.lower()
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    gdf20 = assign_plan(gdf,f'{HUSKIES_HOME}/data/IL/il_cong_2011_to_2021.shp','district_id_20')
    gdf20.to_file(f'{HUSKIES_HOME}/generated/IL/preprocess/mergedILP20.geojson', driver='GeoJSON')
    gdf = assign_plan(gdf,f'{HUSKIES_HOME}/data/IL/ILD.geojson','district_id_21')
    gdf.to_file(f"{HUSKIES_HOME}/generated/IL/preprocess/mergedILP.geojson", driver='GeoJSON')
    if agg:
        gdf = aggregate(gdf,'district_id_21',"pop_total  vap_total  vap_white  vap_black  vap_native  vap_asian  vap_hwn  vap_other  vap_mixed  vap_hisp  democrat  republican".split())
        engine.insert_geodataframe(gdf, 'plans', geojson_state='IL', geojson_name='Enacted')
        # gdf.to_file(f'{HUSKIES_HOME}/generated/IL/preprocess/mergedILD.geojson', driver='GeoJSON')

def merge_all(agg):
    merge_NY(agg)
    merge_GA(agg)
    merge_IL(agg)
if __name__ == '__main__':
    merge_all(True)
import mergeDataGA
import mergeDataIL
import mergeDataNY
import geopandas
import asyncio
import requests
import json



SERVER_URL = 'http://localhost:8080'

async def sendGDF(gdf : geopandas.GeoDataFrame, name : str, state : str):
    API_URL=f'{SERVER_URL}/api/plan'
    r = requests.post(API_URL, json={
        'name': name,
        'state': state,
        'plan': gdf.to_json(drop_id=True)
    })
    return r

async def main():
    print("getting json...")
    data_frames = await asyncio.gather(
        mergeDataGA.merge("/data/GA/ga_cong_2011_to_2021.shp", districts=True, write=False),
        mergeDataIL.merge("/data/IL/il_cong_2011_to_2021.shp", districts=True, write=False),
        mergeDataNY.merge("/data/NY/ny_cong_2012_to_2021.shp", districts=True, write=False),
        mergeDataGA.merge(districts=True, write=False),
        mergeDataIL.merge(districts=True, write=False),
        mergeDataNY.merge(districts=True, write=False)
    )
    print(data_frames)
    STATE_IDS = ['GA', 'IL', 'NY']
    L = await asyncio.gather(
        *[sendGDF(df, ('Enacted' if i > 2 else '2020'), STATE_IDS[i%3]) for i,df in enumerate(data_frames)]   
    )
    print("done!")
    print(L)

if __name__ == '__main__':
    asyncio.run(main())
from fastapi import FastAPI, HTTPException, Query
import copernicusmarine as cm
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

#Example url: http://localhost:8000/ocean-data/?dataset_id=cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m&min_lon=35.381&max_lon=35.381&min_lat=34.121&max_lat=34.121&variables=uo,vo&start_date=2022-09-16&end_date=2023-12-31 -> could also add fields min_depth and max_depth

load_dotenv()

COPERNICUS_USERNAME = os.getenv("COPERNICUS_USERNAME")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD")

app = FastAPI()

login = cm.login(COPERNICUS_USERNAME, COPERNICUS_PASSWORD)
if(login):
    print("Login Successful")
else:
    print("Login Failed")

def fetch_data(
        dataset_id: str,
        min_lon: float,
        max_lon: float,
        min_lat: float,
        max_lat: float,
        min_depth: float,
        max_depth: float,
        variables: list,
        start_date: str,
        end_date: str
):
    try:
        df = cm.read_dataframe(
            dataset_id=dataset_id,
            minimum_longitude=min_lon,
            maximum_longitude=max_lon,
            minimum_latitude=min_lat,
            maximum_latitude=max_lat,
            minimum_depth=min_depth,
            maximum_depth=max_depth,
            variables=variables,
            start_datetime=start_date,
            end_datetime=end_date
        )
        df.replace([np.inf, -np.inf], np.nan, inplace=True)  
        print(df)
        df = df.map(lambda x: None if pd.isna(x) else x)
        return df.reset_index().to_dict(orient="records")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ocean-data/")
def get_ocean_data(
    dataset_id: str = Query(..., description="The dataset ID to fetch data from."),
    min_lon: float = Query(..., description="The minimum longitude of the bounding box."),
    max_lon: float = Query(..., description="The maximum longitude of the bounding box."),
    min_lat: float = Query(..., description="The minimum latitude of the bounding box."),
    max_lat: float = Query(..., description="The maximum latitude of the bounding box."),
    min_depth: float = Query(0, description="The minimum depth of the data."),
    max_depth: float = Query(1, description="The maximum depth of the data."),
    variables: str = Query("CHL", description="The variables to fetch. Comma separated."),
    start_date: str = Query("2024-3-12", description="The start date of the data."),
    end_date: str = Query("2025-3-12", description="The end date of the data.")
):
    variable_list = variables.split(",")
    return fetch_data(dataset_id, min_lon, max_lon, min_lat, max_lat,min_depth, max_depth, variable_list, start_date, end_date)
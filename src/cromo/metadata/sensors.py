import pandas as pd
import sys
import json
import geojson
import requests
from requests.api import request

def getMeanWindSpeedFromGustsFile(inputs, geojson_file, start_date, end_date):
    df = None
    for input in inputs:
        idf = pd.read_csv(input,skiprows=8, header=None)
        if df is None:
            df = idf
        else:
            df = pd.concat([df, idf])
    min_df = df.min()
    mean_df = df.mean()
    max_df = df.max()
    val = {'min_wind_10': float(min_df[2]), # convert from km/h to m/s, which is what we have in the model catalog
            'mean_wind_10': float(mean_df[2]),
            'max_wind_10': float(max_df[2]),
            'min_wind_dir': float(min_df[3]),
            'mean_wind_dir': float(mean_df[3]),
            'max_wind_dir': float(max_df[3])}

    des = {'wind_10': 'Wind speed at 10m',
            'wind_dir': 'Wind direction at 10m'}

    units = {'wind_10': 'm/s',
            'wind_dir':'deg'}

    res = {'description':des,
            'values': val,
            'units': units}
    return res

def getWindComplexityFromGustsFile(inputs, geojson_file, start_date, end_date):
    input = inputs[0]
    df = pd.read_csv(input,skiprows=8, header=None)
    df_diff=df.iloc[:,2:].diff()
    c1=(df_diff.iloc[:,0].abs()>2.5).any()
    c2=(df_diff.iloc[:,1].abs()>45).any()
    if c1 == True and c2 == True:
        c=1
    else:
        c=0
    val = {'wind_speed_change': float(c1), # convert from km/h to m/s, which is what we have in the model catalog
            'wind_direction_change': float(c2),
            'wind_complexity': float(c)}

    des = {'wind_speed_change': 'If True, changes in wind speed greater than 2.5mps were observed',
            'wind_direction_change': 'If True, changes in wind direction greater than 45deg were observed',
            'wind_complexity':'If True, changes in wind speed greater than 2.5mps and wind direction greater than 45deg were observed'}

    res = {'description':des,
            'values': val}
    return res

def bbox(coord_list):
     box = []
     for i in (0,1):
         res = sorted(coord_list, key=lambda x:x[i])
         box.append((res[0][i],res[-1][i]))
     ret = f"{box[0][0]},{box[1][0]},{box[0][1]},{box[1][1]}"
     return ret

def getMeanSlopeFromAPI(inputs, feature, start_date, end_date):
    boundingBox = bbox(list(geojson.utils.coords(feature)))
    url = f"https://sdge.sdsc.edu/pylaski/app/fastfuels/elevation?bbox={boundingBox}"
    val = requests.get(url).json()
    #val = {"mean_elevation": 787.8670450428692, "mean_slope": 20.09848326408428, "units": {"mean_elevation": "m", "mean_slope": "%"}}
    units = val["units"]
    del val["units"]
    return {
        "values": val,
        "units": units
    }

SENSORS = {
    "mean_wind_10": {
        "GustsFile": getMeanWindSpeedFromGustsFile
    },
    "wind_complexity": {
        "GustsFile": getWindComplexityFromGustsFile
    },
    "mean_slope": {
        "DEMFile": getMeanSlopeFromAPI
    }
}


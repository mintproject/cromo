import pandas as pd
import sys
import json
import geojson
import requests
from requests.api import request

def getMeanWindSpeedFromGustsFile(inputs, geojson_file, start_date, end_date):
    input = inputs[0]
    df = pd.read_csv(input,skiprows=8, header=None)
    min_df = df.min()
    mean_df = df.mean()
    max_df = df.max()
    
    #val = {'min_wind_10': float(min_df[2]), # convert from km/h to m/s, which is what we have in the model catalog
    #        'mean_wind_10': float(mean_df[2]),
    #        'max_wind_10': float(max_df[2]),
    #        'min_wind_dir': float(min_df[3]),
    #        'mean_wind_dir': float(mean_df[3]),
    #        'max_wind_dir': float(max_df[3])}

    val = {'mean_wind_10': float(mean_df[2])}
    labels = {'mean_wind_10': 'Mean Wind Speed at 10m'}
    des = {'mean_wind_10': 'Mean Wind Speed at 10m'}
    units = {'mean_wind_10': 'm/s'}

    #'mean_wind_dir':'deg'

    res = {'description':des,
            'labels': labels,
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

    #val = {'wind_speed_change': float(c1), # convert from km/h to m/s, which is what we have in the model catalog
    #        'wind_direction_change': float(c2),
    #        'wind_complexity': float(c)}

    val = {'wind_complexity': float(c)}
    labels = {'wind_complexity': 'Wind Complexity'}
    units = {'wind_complexity': ""}

    #des = {'wind_speed_change': 'If equal to 1, changes in wind speed greater than 2.5mps were observed',
    #        'wind_direction_change': 'If equal to 1, changes in wind direction greater than 45deg were observed',
    #        'wind_complexity':'If equal to 1, then changes in wind speed greater than 2.5mps and wind direction greater than 45deg were observed'}
    
    des = {'wind_complexity':'If equal to 1, then changes in wind speed greater than 2.5mps and wind direction greater than 45deg were observed'}

    res = {'description':des,
            'labels': labels,
            'values': val,
            'units': units}
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

    labels = {'mean_slope': 'Mean Terrain Slope', 'mean_elevation': 'Mean Terrain Elevation'}
    units = {"mean_elevation": "m", "mean_slope": "%"}
    if "units" not in val:
        val = {"mean_elevation": 787.8670450428692, "mean_slope": 20.09848326408428, "units": units}

    units = val["units"]
    del val["units"]
    return {
        "values": val,
        "labels": labels,
        "description": labels,
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


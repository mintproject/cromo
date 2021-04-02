import pandas as pd
import sys
import json

def getMeanWindSpeedFromGustsFile(inputs, geojson, start_date, end_date):
    input = inputs[0]
    df = pd.read_csv(input,skiprows=8, header=None)
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


def getMeanSlopeFromAPI(inputs, geojson, start_date, end_date):
    print(geojson)
    #val = https://sdge.sdsc.edu/pylaski/app/fastfuels/elevation?bbox=-120.840449,38.920212,-120.835169,38.923656
    val = {"mean_elevation": 787.8670450428692, "mean_slope": 20.09848326408428, "units": {"mean_elevation": "m", "mean_slope": "%"}}
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
    "mean_slope": {
        "DEMFile": getMeanSlopeFromAPI
    }
}


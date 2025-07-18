# Imports
import streamlit as st
import requests
import datetime
import numpy as np
import pandas as pd
from sources_boreholes_Tilsig import depths_tilsig

##################################################
### Data loading from Tilsig and MET functions ###
##################################################

# Load data once per day
@st.cache_data(ttl=86400, show_spinner='Fetching data')
def load_data_Tilsig(source_string):

    ######################
    ### Authentication ###
    ######################

    # Define the Tilsig API endpoint and credentials
    endpoint = 'https://api.where2o.com/v1/authentication/authenticate'
    username = 'maaikew@unis.no'
    password = 'ToppTur1!2@3#4$'

    # Define the data and headers for the token request
    data = {
        'username': username,
        'password': password,
    }

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # Send the token request
    r = requests.post(endpoint, json=data, headers=headers)

    # Check if request succeeded and retrieve token
    if r.status_code == 200:
        token_data = r.json()
        access_token = token_data['token']
    else:
        print('Error! Returned status code %s' % r.status_code)

    ######################
    ### Data retrieval ###
    ######################

    # Loop over years because data request is limited to 1 year
    source_sn = source_string[:4]

    start_date = source_string[len(source_string)-11:-1]
    start_year = int(start_date[:4])
    end_year = datetime.datetime.now().year + 1

    years = [start_date]
    for i in range (end_year-start_year):
        years.append(str(start_year+1+i)+'-01-01')

    # Define headers for data retrieval
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer '+access_token,
    }

    for i in range(len(years)-1):
        endpoint = "https://api.where2o.com/v1/measurement/raw"
        parameters = {
            'stationId': '',
            'deviceId': '',
            'sensorId': source_sn,
            'from': years[i] + 'T00:00:00.000Z',
            'to': years[i+1] + 'T00:00:00.000Z',
        }

        # Issue an HTTP GET request
        response = requests.get(endpoint, parameters, headers=headers)
        data_part = response.json()

        if i == 0:
            data = data_part
        else:
            data = data + data_part

    return data


def Tilsig_data_to_dataframe(data, row_idx):
    # Load into to DataFrame
    df = pd.DataFrame(data)

    # Parse timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'],format='ISO8601')

    # Sort by time and sequence
    df = df.sort_values(['timestamp', 'sequence'])

    # Add depth column corresponding to sequence
    depths = depths_tilsig[row_idx]
    sequences = np.sort(df['sequence'].unique()).tolist()
    depth_map = dict(zip(sequences, depths))
    df['depth'] = df['sequence'].map(depth_map)
    df['depthUnit'] = 'cm'

    # Drop unwanted columns
    df = df.drop(columns=['unitId', 'typeId', 'category', 'sequence'], errors='ignore').reset_index()

    # Reorder and rename columns
    desired_order = [
        'timestamp', 'depth', 'depthUnit', 'type',
        'value', 'unit', 'stationId', 'deviceId', 'sensorId'
    ]
    df = df[desired_order]
    df = df.rename(columns={'timestamp':'referenceTime', 'type': 'measurementType'})

    # Replace faulty values with NaN
    df.loc[df['value'] > 30, 'value'] = np.nan
    df.loc[df['value'] < -30, 'value'] = np.nan

    return df


# Load data once per day
@st.cache_data(ttl=86400, show_spinner="Fetching data")
def load_data_MET(source_string):
    # Load data from MET source
    source_sn = source_string[:7]
    
    # Date tomorrow
    date_tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    # Define reference time for each source
    if source_string != "SN99875: JANSSONHAUGEN (1998-05-09)":
        reference_times = [source_string[len(source_string)-11:-1] + "/" + date_tomorrow]
    else:
        reference_times = [
        source_string[len(source_string)-11:-1] + "/" + '2008-01-01',
        '2008-01-01' + "/" + '2018-01-01',
        '2018-01-01' + "/" + date_tomorrow
        ]

    # Make an account on frost.met.no and paste client_id here 
    client_id = 'd3c88b9a-0578-4021-b984-67e8f31cc1bd'

    data_allTimes=0
    for j in range(len(reference_times)):    
 
        # Define endpoint and parameters            
        endpoint = 'https://frost.met.no/observations/v0.jsonld'
        parameters = {
            'sources': source_sn,
            'elements': 'soil_temperature',
            'referencetime': reference_times[j],
        }

        # Issue an HTTP GET request
        r = requests.get(endpoint, parameters, auth=(client_id,''))
    
        # Extract JSON data
        json_data = r.json()
   
        # Check if the request worked, print out any errors
        if r.status_code == 200:
            data = json_data['data']

            # Paste data from different reference times together (limit on observations per request)
            if j == 0:
                data_allTimes = data
            else:
                data_allTimes = data_allTimes + data

    data_allTimes = data_allTimes

    return data_allTimes


def MET_data_to_dataframe(data):
    # Load data into Dataframe
    flattened_data = []
    for entry in data:
        for obs in entry['observations']:
            record = {
                'referenceTime': entry['referenceTime'],
                'depth': obs['level']['value'],
                'depthUnit': obs['level']['unit'],
                'measurementType': obs['elementId'],
                'value': obs['value'],
                'unit': obs.get('unit'),
                'sourceId': entry['sourceId'],
            }
            flattened_data.append(record)

    df = pd.DataFrame(flattened_data)

    #########################
    ### Small adjustments ###
    #########################

    # Convert referenceTime to datetime
    df['referenceTime'] = pd.to_datetime(df['referenceTime'],format='ISO8601')

    # Sort and reset index
    df = df.sort_values(by=['referenceTime', 'depth'])
    df = df.reset_index(drop=True)

    # Replace meaurement type naming
    df['measurementType'] = df['measurementType'].replace('soil_temperature', 'Temperature')

    # Replace faulty values with NaN
    df.loc[df['value'] > 30, 'value'] = np.nan
    df.loc[df['value'] < -30, 'value'] = np.nan

    return df


def data_processing_for_plotting(df):
    # Process data for plotting purposes
    
    #########################################
    ### Full depth profiles per timestamp ###
    #########################################
    
    depths = np.sort(df['depth'].unique()).tolist()

    # Create a MultiIndex of all timestamp-depth combinations
    full_index = pd.MultiIndex.from_product(
        [df['referenceTime'].unique(), depths],
        names=['referenceTime', 'depth']
    )

    # Set index and reindex to include all combinations
    df.set_index(['referenceTime', 'depth'], inplace=True)
    df = df.reindex(full_index).reset_index()

    # Fill metadata columns except 'value' and 'sequence'
    meta_cols = [col for col in df.columns if col not in ['value', 'depth', 'referenceTime']]
    for col in meta_cols:
        df[col] = df.groupby('referenceTime')[col].ffill().bfill()
    
    ##############################################################
    ### Detect missing timestamps and insert full NaN profiles ###
    ##############################################################
    
    # Find timestamps and intervals
    timestamps = df['referenceTime'].drop_duplicates().sort_values().reset_index(drop=True)
    intervals = timestamps.diff()

    # Find missing timestamps based on previous interval and use safety margin
    # Create missing timestamps and insert NaN profiles
    new_rows = []
    for i in range(1, len(timestamps)-1):
        previous_timestamp = timestamps[i-1]
        
        if intervals[i] < intervals[i-1] + datetime.timedelta(minutes = 1) and intervals[i] > intervals[i-1] - datetime.timedelta(minutes = 1):
            expected_interval = intervals[i]   
        else:
            expected_interval = intervals[i-1]

        if intervals[i] > expected_interval * 1.1 and expected_interval > datetime.timedelta(minutes = 1):
            new_timestamp = previous_timestamp + expected_interval

            if 'sourceId' in df.columns:
                for j in range(len(depths)):
                    new_rows.append({
                        'referenceTime': new_timestamp,
                        'depth': depths[j],
                        'depthUnit': df['depthUnit'][0],
                        'measurementType': df['measurementType'][0],
                        'value': np.nan,
                        'unit': df['unit'][0],
                        'sourceId': df['sourceId'][0],
                    })
            
            elif 'stationId' in df.columns or 'deviceId' in df.columns or 'sensorId' in df.columns:
                for j in range(len(depths)):
                    new_rows.append({
                        'referenceTime': new_timestamp,
                        'depth': depths[j],
                        'depthUnit': df['depthUnit'][0],
                        'measurementType': df['measurementType'][0],
                        'value': np.nan,
                        'unit': df['unit'][0],
                        'stationId': df['stationId'][0],
                        'deviceId': df['deviceId'][0],
                        'sensorId': df['sensorId'][0],
                    })

    # Create DataFrame with new rows and merge
    df_insert = pd.DataFrame(new_rows)
    df = pd.concat([df, df_insert]).sort_values(['referenceTime', 'depth']).reset_index(drop=True)

    return df
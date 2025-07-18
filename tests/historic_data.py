# Imports
import streamlit as st
import os
from io import BytesIO
import requests
import pandas as pd
import numpy as np
import json
import datetime

# Load data
#@st.cache_data(ttl=86400) # [s] Cache data for 1 day
@st.cache_data(show_spinner="Fetching MET data")
def load_data(sources, first_observations, date_to):

    sources_sn = [sn[:7] for sn in sources]
    
    for i in range(len(sources_sn)):
        
        # Define reference time for each source
        reference_times = [first_observations[i] + "/" + date_to]
        #if sources[i] != "SN99875: JANSSONHAUGEN":
        #    reference_times = [first_observations[i] + "/" + date_to]
        #else:
        #    reference_times = [
        #    first_observations[sources.index("SN99875: JANSSONHAUGEN")] + "/" + '2008-01-01',
        #    '2008-01-01' + "/" + '2018-01-01',
        #    '2018-01-01' + "/" + date_to
        #    ]

        for j in range(len(reference_times)):    
            
            # Define endpoint and parameters            
            endpoint = 'https://frost.met.no/observations/v0.jsonld'
            parameters = {
                'sources': sources_sn[i],
                'elements': 'soil_temperature',
                'referencetime': reference_times[j],
            }

            # Make an account on frost.met.no and paste client_id here 
            client_id = 'd3c88b9a-0578-4021-b984-67e8f31cc1bd'

            # Issue an HTTP GET request
            r = requests.get(endpoint, parameters, auth=(client_id,''))
    
            # Extract JSON data
            json_data = r.json()
    
            # Check if the request worked, print out any errors
            if r.status_code == 200:
                data = json_data['data']
                print('Data retrieved from frost.met.no!')

                # Paste data from different reference times together
                if j == 0:
                    data_allTimes_oneSource = data
                else:
                    data_allTimes_oneSource = data_allTimes_oneSource + data
            else:
                print('Error! Returned status code %s' % r.status_code)
                print('Message: %s' % json_data['error']['message'])
                print('Reason: %s' % json_data['error']['reason'])
        
        # Paste data from different reference times and sources together
        if i == 0:
            data_allTimes_allSources = data_allTimes_oneSource
        else:
            data_allTimes_allSources = data_allTimes_allSources + data_allTimes_oneSource
        
    return data_allTimes_allSources

# Borehole station numbers, names, and first observations
sources = [
    "SN99843: PLATÅBERGET III", 
    "SN99855: LONGYEARDALEN - VALLEY BOTTOM",
    "SN99857: LONGYEARDALEN - CENTRAL",
    "SN99862: BREINOSA - BLOCKFIELD PLATEAU",
    "SN99867: GRUVEFJELLET - BLOCKFIELD PLATEAU",
    "SN99868: ENDALEN",
    "SN99869: ADVENTDALEN - LOESS TERRACE",
    "SN99872: ADVENTDALEN - UPPER SNOWDRIFT",
    "SN99874: JANSSONHAUGEN - VEST",
    "SN99875: JANSSONHAUGEN",
    "SN99877: ADVENTDALEN - ICE-WEDGE",
    "SN99879: ADVENTDALEN - INNERHYTTA PINGO"
]

#first_observations = [
#    "2018-02-03",
#    "2019-09-16",
#    "2023-09-16",
#    "2022-03-25",
#    "2022-03-26",
#    "2021-11-14",
#    "2019-08-24",
#    "2019-09-03",
#    "2019-09-28",
#    "1998-05-09",
#    "2019-08-26",
#    "2020-08-24"
#    ]

first_observations = [
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01",
    "2025-01-01"
    ]

# Tomorrow's date
#date_tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# First upcoming Monday date
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

d = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
next_monday = next_weekday(d, 0).strftime('%Y-%m-%d') # 0=Monday, 1=Tuesday, 2=Wednesday, etc.

# Call function to retrieve all soil_temperature data from all sources
data_allTimes_allSources = load_data(sources, first_observations, next_monday)

# Make some plots
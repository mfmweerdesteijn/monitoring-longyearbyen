# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium

from sources_weather_stations_MET import *
from sources_weather_stations_Tilsig import *
from load_weather_stations_data_Tilsig_and_MET import *
from plot_weather_stations_data import *

# Functions: put in other script
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False, na_rep='NaN').encode('utf-8-sig')

# Set page configuration
st.set_page_config(page_title='Weather stations',layout='wide')
st.title('Weather stations')
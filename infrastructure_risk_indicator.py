# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

### IMPLEMENT DUAL MAP OPTION

# Set page configuration
st.set_page_config(page_title='Infrastructure risk indicator',layout='wide')
st.title('Infrastructure risk indicator')

col1, col2 = st.columns(2)
with col1:
    # Create map centered near Longyearbyen
    m1 = folium.Map(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)#, width=300, height=100)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Basiskart_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='Basisdata_NP_Basiskart_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Basemap',
    overlay=False,
    control=True,
    show=True,
).add_to(m1)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Satellitt_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='Basisdata_NP_Satellitt_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Satellite',
    overlay=False,
    control=True,
    show=False,
).add_to(m1)

folium.LayerControl().add_to(m1)

# call to render Folium map in Streamlit
st_data1 = st_folium(m1, use_container_width=True, height=700) #width=1100

with col2:
    # Create map centered near Longyearbyen
    m2 = folium.Map(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)#, width=300, height=100)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Basiskart_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='Basisdata_NP_Basiskart_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Basemap',
    overlay=False,
    control=True,
    show=True,
).add_to(m2)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Satellitt_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='Basisdata_NP_Satellitt_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Satellite',
    overlay=False,
    control=True,
    show=False,
).add_to(m2)

folium.LayerControl().add_to(m2)

# call to render Folium map in Streamlit
st_data2 = st_folium(m2, use_container_width=True, height=700) #width=1100
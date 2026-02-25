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

m = folium.plugins.DualMap(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)

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
).add_to(m.m1).add_to(m.m2)

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
).add_to(m.m1)

folium.LayerControl().add_to(m.m1)

st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip']) #width=1100
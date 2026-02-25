# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# Set page configuration
st.set_page_config(page_title='Depth to bedrock',layout='wide')
st.title('Depth to bedrock')

# Create map centered near Longyearbyen
m = folium.Map(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)#, width=300, height=100)

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
).add_to(m)

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
).add_to(m)

folium.LayerControl().add_to(m)

# Add markers, polylines, and polygons

# Add a Polygon (Filled Shape)
polygon_coords = [
    [78.2206516787612, 15.63335948841357],
    [78.22070424390284, 15.657220418201998],
    [78.21704165250685, 15.655675465913536],
    [78.2206516787612, 15.63335948841357]
]
folium.Polygon(
    locations=polygon_coords,
    color=None,
    fill=True,
    fill_color= "#829d4c",
    fill_opacity=0.7,
    tooltip='0 - 5 m'
).add_to(m)

# Add a Point (Marker)
folium.CircleMarker(
    location=[78.2206516787612, 15.63335948841357],
    radius=3,
    color='black',
    fill=True,
    fill_color='black',
    fill_opacity=1
).add_to(m)

folium.Marker(
    location=[78.2183096579359, 15.646119038680919],
    icon=folium.DivIcon(html=f"""<div style='font-size: 20px; font-weight: regular; color: black'>&#43;</div>""")
).add_to(m)

folium.Marker(
    location=[78.21965605893124, 15.635458832204813],
    icon=folium.DivIcon(html=f"""<div style='font-size: 20px; font-weight: regular; color: black'>&#215;</div>""")
).add_to(m)

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
<div class='legend-scale'>
  <ul class='legend-labels'>
    <b>Observed depth to bedrock</b>
    <li>&ensp;&#9679;&ensp;&thinsp;Depth to bedrock from boreholes</li>
    <li>&ensp;&#43;&ensp;&thinsp;Shallow (<5 m) boreholes not reaching bedrock</li>
    <li>&ensp;&#215;&ensp;&thinsp;Deep (>5 m) boreholes reaching bedrock</li>
    <b>Interpolated depth to bedrock (m)</b>
  </ul>
  <ul class='legend-labels legend-grid'>
    <li><span style='background: #829d4c; opacity: 0.7;'></span>0 - 5</li>
    <li><span style='background: #a4c16d; opacity: 0.7;'></span>5 - 10</li>
    <li><span style='background: #cde6a4; opacity: 0.7;'></span>10 - 20</li>
    <li><span style='background: #eaf4b5; opacity: 0.7;'></span>20 - 30</li>
    <li><span style='background: #f6ecae; opacity: 0.7;'></span>30 - 40</li>
    <li><span style='background: #ecd097; opacity: 0.7;'></span>40 - 50</li>
    <li><span style='background: #d3ac6b; opacity: 0.7;'></span>50 - 60</li>
    <li><span style='background: #b98c4b; opacity: 0.7;'></span>60 - 70</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 22px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 20px; margin-right: 4.5px;}
  .legend-grid {display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(4, auto); grid-auto-flow: column; column-gap: 15px;}
</style>
{% endmacro %}
"""

# Add the legend to the map
macro = MacroElement()
macro._template = Template(legend_template)
m.get_root().add_child(macro)

# call to render Folium map in Streamlit
st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip']) #width=1100
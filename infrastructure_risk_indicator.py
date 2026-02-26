# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# Set page configuration
st.set_page_config(page_title='Infrastructure risk indicator',layout='wide')
st.title('Infrastructure risk indicator')

# Create two columns
col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    st.header("Cultural heritage")
    #st.write("This is the text for the first column.")

# Add content to the second column
with col2:
    st.header("Modern buildings")
    #st.write("This is the text for the second column.")

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
).add_to(m)

#folium.raster_layers.WmsTileLayer(
#    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Satellitt_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
#    layers='Basisdata_NP_Satellitt_Svalbard_WMTS_3857',
#    fmt='image/png',
#    transparent=False,
#    version='1.0.0',
#    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
#    name='Satellite',
#    overlay=False,
#    control=True,
#    show=False,
#).add_to(m)

#folium.LayerControl().add_to(m.m1)
#folium.LayerControl().add_to(m.m2)

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
    tooltip='landform 1'
).add_to(m.m1)

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
<div class='legend-scale'>
  <ul class='legend-labels legend-grid'>
    <li><span style='background: #829d4c; opacity: 0.7;'></span>landform 1</li>
    <li><span style='background: #a4c16d; opacity: 0.7;'></span>landform 2</li>
    <li><span style='background: #cde6a4; opacity: 0.7;'></span>landform 3</li>
    <li><span style='background: #eaf4b5; opacity: 0.7;'></span>landform 4</li>
    <li><span style='background: #f6ecae; opacity: 0.7;'></span>landform 5</li>
    <li><span style='background: #ecd097; opacity: 0.7;'></span>landform 6</li>
    <li><span style='background: #d3ac6b; opacity: 0.7;'></span>landform 7</li>
    <li><span style='background: #b98c4b; opacity: 0.7;'></span>landform 8</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 22px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 20px; margin-right: 4.5px;}
  .legend-grid {display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(2, auto); grid-auto-flow: column; column-gap: 15px;}
</style>
{% endmacro %}
"""

# Add the legend to the map
macro = MacroElement()
macro._template = Template(legend_template)
m.m1.get_root().add_child(macro)

st_data = st_folium(m, use_container_width=True, height=700)
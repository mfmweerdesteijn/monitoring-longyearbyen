# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
from folium import Element

# Set page configuration
st.set_page_config(page_title='Infrastructure risk indicator',layout='wide')
st.title('Infrastructure risk indicator')

# Create two columns
col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    st.header("Modern buildings")

# Add content to the second column
with col2:
    st.header("Cultural heritage")

# Create map centered near Longyearbyen
m = folium.plugins.DualMap(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)

# Basemap layers for different zoom levels
basemap = folium.FeatureGroup(name="Basemap", overlay=False)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Basiskart_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='NP_Basiskart_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Basemap low zoom',
    min_zoom=0,
    max_zoom=12,
    #overlay=True,
    show=True,
).add_to(basemap)

folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/FKB_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
    layers='FKB_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Basemap high zoom',
    min_zoom=13,
    max_zoom=17,
    #overlay=True,
    show=True,
).add_to(basemap)

basemap.add_to(m)

# Orthographic map as overlay
folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Ortofoto_Svalbard_WMTS_25833/MapServer/tile/{z}/{y}/{x}',
    layers='NP_Ortofoto_Svalbard_WMTS_3857',
    fmt='image/png',
    transparent=False,
    version='1.0.0',
    attr=u'<a href=https://toposvalbard.npolar.no/> TopoSvalbard</a> © 2015 <a href=https://www.npolar.no/en/>Norwegian Polar Insitute</a>',
    name='Orthophoto',
    min_zoom=0,
    max_zoom=17,
    overlay=True,
    control=True,
    show=False,
).add_to(m)

# Add layer control: this method ensures that there is no jumping of zoom levels when switching between basemap and ortographic map
folium.LayerControl().add_to(m.m1)
folium.LayerControl().add_to(m.m2)

js = """
<script>
var basemapLayers = [];
var orthoLayer;

// collect layers
map.eachLayer(function(layer){
    if(layer.options && layer.options.name === "Orthophoto"){
        orthoLayer = layer;
    }
    if(layer.options && layer.options.name === "Basemap low zoom"){
        basemapLayers.push(layer);
    }
    if(layer.options && layer.options.name === "Basemap high zoom"){
        basemapLayers.push(layer);
    }
});

// custom control behavior
map.on('overlayadd', function(e){
    if(e.name === "Orthophoto"){
        basemapLayers.forEach(l => map.removeLayer(l));
    }
    if(e.name === "Basemap Low" || e.name === "Basemap high zoom"){
        map.removeLayer(orthoLayer);
    }
});
</script>
"""

m.get_root().html.add_child(Element(js))

# Add data on map through polygons

# Add a polygon
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
    fill_color= "#67b0ff",
    fill_opacity=0.7,
    tooltip='0 Undefined'
).add_to(m.m1)

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
<div class='legend-scale'>
  <ul class='legend-labels legend-grid'>
    <b>Modern Buildings (MB) and Cultural<br>Heritage (CH) risk estimate</b>
    <li><span style='background: #67b0ff; opacity: 0.7;'></span>0 Undefined</li>
    <li><span style='background: #ffeb8c; opacity: 0.7;'></span>1-3 Low</li>
    <li><span style='background: #fa875f; opacity: 0.7;'></span>4-6 Low-medium</li>
    <li><span style='background: #b6367a; opacity: 0.7;'></span>7-9 Medium-high</li>
    <li><span style='background: #51137b; opacity: 0.7;'></span>10-12 High</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 22px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 20px; margin-right: 4.5px;}
</style>
{% endmacro %}
"""

# Add the legend to the map
macro = MacroElement()
macro._template = Template(legend_template)
m.m1.get_root().add_child(macro)

# call to render Folium map in Streamlit
st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip'])
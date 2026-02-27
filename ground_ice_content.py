# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
from folium import Element

# Set page configuration
st.set_page_config(page_title='Ground ice content',layout='wide')
st.title('Ground ice content')

# Create map centered near Longyearbyen
m = folium.Map(location=[78.213578, 15.699462], zoom_start=10, tiles=None, control_scale=True)

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
    overlay=True,
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
    overlay=True,
    show=True,
).add_to(basemap)

basemap.add_to(m)

# Orthographic map as overlay
folium.raster_layers.WmsTileLayer(
    url='https://geodata.npolar.no/arcgis/rest/services/Basisdata/NP_Ortofoto_Svalbard_WMTS_3857/MapServer/tile/{z}/{y}/{x}',
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
folium.LayerControl().add_to(m)

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

# Add data on map through polygons and markers

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
    fill_color= "#8aaae5", # "#919191", "#d5dfe8", "#a4d1ee", "#8aaae5", "#6d78ae",
    fill_opacity=0.7,
    tooltip='>20%'
).add_to(m)

# Add a marker
folium.CircleMarker(
    location=[78.2206516787612, 15.63335948841357],
    radius=3,
    color='black',
    fill=True,
    fill_color='black',
    fill_opacity=1
).add_to(m)

folium.Marker(
    [78.2206516787612, 15.63335948841357],
    icon=folium.DivIcon(
    icon_anchor=(0,0),
    html=f'<div style="font-size: 12pt; color: black; font-weight: normal;">{"16%"}</div>')
).add_to(m)

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
<div class='legend-scale'>
  <ul class='legend-labels'>
    <b>Excess Ice Content (EIC) in top 1 m permafrost</b>
    <li>&ensp;&#9679;&ensp;&thinsp;Average EIC at boreholes (%)</li>
    <li><span style='background: #6d78ae; opacity: 0.7;'></span>High (>20%)</li>
    <li><span style='background: #8aaae5; opacity: 0.7;'></span>Medium (10-20%)</li>
    <li><span style='background: #a4d1ee; opacity: 0.7;'></span>Low (5-10%)</li>
    <li><span style='background: #d5dfe8; opacity: 0.7;'></span>Negligible (<5%)</li>
    <li><span style='background: #919191; opacity: 0.7;'></span>No data</li>
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
m.get_root().add_child(macro)

# call to render Folium map in Streamlit
st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip'])
# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
from folium import Element
import geopandas as gpd
import random
import json

# Set page configuration
st.set_page_config(page_title='Geomorphology',layout='wide')
st.title('Geomorphology')

# Create map centered near Longyearbyen
m = folium.Map(location=[78.213578, 15.599462], zoom_start=11, tiles=None, control_scale=True)#, width=300, height=100)

# Basemap layers for different zoom levels
basemap = folium.FeatureGroup(name='Basemap', overlay=False)

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
    if(layer.options && layer.options.name === 'Orthophoto'){
        orthoLayer = layer;
    }
    if(layer.options && layer.options.name === 'Basemap low zoom'){
        basemapLayers.push(layer);
    }
    if(layer.options && layer.options.name === 'Basemap high zoom'){
        basemapLayers.push(layer);
    }
});

// custom control behavior
map.on('overlayadd', function(e){
    if(e.name === 'Orthophoto'){
        basemapLayers.forEach(l => map.removeLayer(l));
    }
    if(e.name === 'Basemap Low' || e.name === 'Basemap high zoom'){
        map.removeLayer(orthoLayer);
    }
});
</script>
"""

m.get_root().html.add_child(Element(js))

# Add data on map through polygons and markers
# Read file
gdf = gpd.read_file('LyBQuatMap10k_Rubensdotter_2022_EPSG32633.geojson')

# Reproject to WGS84 (lon/lat/h)
gdf = gdf.to_crs('EPSG:4326')

# Ignore h coordinate and empty columns
gdf['geometry'] = gdf['geometry'].force_2d()
gdf = gdf.drop(columns=['DATO','OPPHAV','NOTAT'])

# Necessary now that I don't have acces to .lyr file
landforms_unique = gdf['JORDART'].unique()

random.seed(39)
def random_hex_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
colors = [random_hex_color() for _ in range(len(landforms_unique))]
landforms_colors = dict(zip(landforms_unique, colors))

gdf['color'] = gdf['JORDART'].map(landforms_colors)

# Add polygons to map
for row in gdf.itertuples():
    geom = row.geometry
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]

    for poly in polys:
        coords = [[lat, lon] for lon, lat in poly.exterior.coords]
        folium.Polygon(
            locations=coords,
            color=None,
            fill=True,
            fill_color=row.color,
            fill_opacity=0.7,
            tooltip=row.JORDART
        ).add_to(m)

## Extract coordinates
#all_polygons = []
#
#for geom in gdf.geometry:
#    for poly in (geom.geoms if geom.geom_type == 'MultiPolygon' else [geom]):
#        all_polygons.append([
#            [lat, lon]
#            for lon, lat in poly.exterior.coords
#        ])
#
## Add polygons to map
#for i in range(len(all_polygons)):
#    folium.Polygon(
#        locations=all_polygons[i],
#        color=None,
#        fill=True,
#        fill_color= landforms_colors[gdf.iloc[i]['JORDART']],# "#829d4c",
#        fill_opacity=0.7,
#        tooltip=gdf.iloc[i]['JORDART']
#    ).add_to(m)

# Create the legend template as an HTML element
legend_items = ""

for jordart, color in sorted(landforms_colors.items()):
    legend_items += f"""
    <li><span style='background:{color}; opacity:0.7;'></span>{jordart}</li>
    """

legend_template = f"""
{{% macro html(this, kwargs) %}}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
<div class='legend-scale'>
  <ul class='legend-labels legend-grid'>
    {legend_items}
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {{margin: 0; padding: 0; color: #0f0f0f;}}
  .maplegend .legend-scale ul li {{list-style: none; line-height: 22px; margin-bottom: 1.5px;}}
  .maplegend ul.legend-labels li span {{float: left; height: 16px; width: 20px; margin-right: 4.5px;}}
  .legend-grid {{display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(8, auto); grid-auto-flow: column; column-gap: 15px;}}
</style>
{{% endmacro %}}
"""

# Add the legend to the map
macro = MacroElement()
macro._template = Template(legend_template)
m.get_root().add_child(macro)

# call to render Folium map in Streamlit
st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip'])
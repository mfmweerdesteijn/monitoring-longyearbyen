# Imports
import streamlit as st
import folium.raster_layers
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
from folium import Element
import geopandas as gpd
from folium.plugins import StripePattern

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

landforms_descriptions_en = {
    11: 'Till',
    12: 'Till, thin cover',
    15: 'Marginal morain',
    20: 'Glaciofluvial deposit',
    21: 'Glaciofluvial deposit, active channel',
    41: 'Marine deposit',
    42: 'Marine beach deposit',
    50: 'Fluvial deposit',
    71: 'Weathering material',
    72: 'Weathering material, thin cover',
    81: 'Mixed avalanche deposits',
    82: 'Mixed avalanche deposits, thin cover',
    88: 'Rock glacier',
    120: 'Anthropogenic fill mass',
    121: 'Mining dump',
    122: 'Anthropogenically disturbed sediment',
    130: 'Bedrock',
    207: 'Tidal deposit',
    301: 'Debris-flow deposit',
    302: 'Debris-flow deposit, thin cover',
    307: 'Rock-fall deposit',
    308: 'Rock-fall deposit, thin cover',
    309: 'Snow-avalanche deposit',
    310: 'Snow-avalanche deposit, thin cover',
    311: 'Rock-avalnache deposit',
    313: 'Snow-avalanche and debris-flow deposit',
    314: 'Snow-avalanche and debris-flow deposit, thin cover',
    316: 'Rock-fall and debris-flow deposit',
    317: 'Snow-avalnache and rock-fall deposit',
    320: 'Solifluction material with high organic content',
    321: 'Stone-rich solifluction metrial',
    4050: 'Mixed flivial and marine deposit',
}

landforms_colors = {
    11: '#b4fc9d',
    12: '#d6fcb4',
    15: '#63fc82',
    20: '#fcca63',
    21: '#fbe5aa',
    41: '#89d6fc',
    42: '#89bffc',
    50: '#fcf19d',
    71: '#e9d0f0',
    72: '#f2d9f9', #striped
    81: '#fc9d9d',
    82: '#fc9d9d', #striped
    88: '#c4bf86',
    120: '#cbcbcb',
    121: '#dddddd',
    122: '#dbdbdb',
    130: '#fcf3f3',
    207: '#a0deca',
    301: '#fc9191',
    302: '#fc9191', #striped
    307: '#fcbfbf',
    308: '#fcbfbf', #striped
    309: '#fca8a8',
    310: '#fca8a8', #striped
    311: '#fcdddd',
    313: '#d7879e',
    314: '#d7879e', #striped
    316: '#e9b1c1', #striped
    317: '#e9cad3',
    320: '#f0d197',
    321: '#e6d4ab',
    4050: '#63edc8',
}

striped_codes = {72, 82, 302, 308, 310, 314, 316}

#pattern_dict = {}
#
#for code in striped_codes:
#    base_color = landforms_colors.get(code, "#ffffff")
#
#    pattern = StripePattern(
#        color='#ffffff',#base_color,
#        width=4,
#        spacing=6,
#        angle=45,
#    )
#
#    pattern_dict[code] = pattern

gdf['color'] = gdf['JORDART'].map(landforms_colors)
gdf['description'] = gdf['JORDART'].map(landforms_descriptions_en)

# Add polygons to map
for row in gdf.itertuples():
    geom = row.geometry
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]

    for poly in polys:
        exterior = [[lat, lon] for lon, lat in poly.exterior.coords]
        holes = [
            [[lat, lon] for lon, lat in interior.coords]
            for interior in poly.interiors
        ]

        if row.JORDART in striped_codes:
            folium.Polygon(
                locations=[exterior] + holes,
                color=None,
                fill=True,
                fill_color='#000000',#row.color,
#                fill_pattern=pattern_dict[row.JORDART],
                fill_pattern = StripePattern(
                    color='#ffffff',#base_color,
                    width=20,
                    spacing=20,
                    angle=45,
                    ),
                fill_opacity=0.8,
                tooltip=row.JORDART
            ).add_to(m)
        else:
            folium.Polygon(
                locations=[exterior] + holes,
                color=None,
                fill=True,
                fill_color=row.color,
                fill_opacity=0.8,
                tooltip=row.JORDART
            ).add_to(m)

# Create the legend template as an HTML element
legend_list = []

striped_codes = {72, 82, 302, 308, 310, 314, 316}

for jordart in sorted(gdf["JORDART"].unique()):
    color = landforms_colors.get(jordart, "#000000")
    description = landforms_descriptions_en.get(jordart, "Unknown")

    if jordart in striped_codes:
        background_style = (
            f"background: repeating-linear-gradient("
            f"45deg, {color}, {color} 5px, white 5px, white 10px);"
        )
    else:
        background_style = f"background:{color};"

    legend_list.append(
        f"<li><span style='{background_style}'></span>"
        f"{jordart} {description}</li>"
    )

legend_items = "".join(legend_list)

#legend_template = f"""
#{{% macro html(this, kwargs) %}}
#<div id='maplegend' class='maplegend' 
#    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.8);
#     border-radius: 6px; padding: 10px; left: 10px; bottom: 70px;'>     
#<div class='legend-scale'>
#  <ul class='legend-labels legend-grid'>
#    {legend_items}
#  </ul>
#</div>
#</div> 
#<style type='text/css'>
#  .maplegend .legend-scale ul {{margin: 0; padding: 0; color: #0f0f0f;}}
#  .maplegend .legend-scale ul li {{list-style: none; line-height: 22px; margin-bottom: 1.5px;}}
#  .maplegend ul.legend-labels li span {{float: left; height: 16px; width: 20px; margin-right: 4.5px;}}
#  .legend-grid {{display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(8, auto); grid-auto-flow: column; column-gap: 15px;}}
#</style>
#{{% endmacro %}}
#"""

# Add the legend to the map
#macro = MacroElement()
#macro._template = Template(legend_template)
#m.get_root().add_child(macro)

# call to render Folium map in Streamlit
legend_html = f"""
<div class='maplegend'>
  <ul class='legend-labels'>
    {legend_items}
  </ul>
</div>

<style>
.maplegend {{
  background-color: rgba(255,255,255,0.95);
  border-radius: 8px;
  padding: 15px;
  font-size: 14px;
}}
.maplegend ul {{
  margin: 0;
  padding: 0;
}}
.maplegend li {{
  list-style: none;
  margin-bottom: 6px;
}}
.maplegend li span {{
  display: inline-block;
  height: 16px;
  width: 20px;
  margin-right: 8px;
  vertical-align: middle;
}}
</style>
"""

col1, col2 = st.columns([3,1])

with col1:
    st_data = st_folium(m, use_container_width=True, height=700, returned_objects=['last_object_clicked_tooltip'])

with col2:
    st.markdown(legend_html, unsafe_allow_html=True)
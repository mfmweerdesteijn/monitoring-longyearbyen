# Imports
import folium.raster_layers
import streamlit as st
import folium
from streamlit_folium import st_folium

from sources_boreholes_MET import *
from sources_boreholes_Tilsig import *
from load_boreholes_data_Tilsig_and_MET import *
from plot_boreholes_data import *

# Functions: put in other script
@st.cache_data
def convert_df(df):
   return df.to_csv(index=False, na_rep='NaN').encode('utf-8-sig')

# Set page configuration
st.set_page_config(page_title='Ground temperature data visualization',layout='wide')
st.title('Ground temperature data visualization')

# Create map centered near Longyearbyen
m = folium.Map(location=[78.213578, 15.699462], zoom_start=10, tiles=None)#, width=300, height=100)

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

# Create markers with popup texts and icons
#icon_ws = folium.Icon(color='blue',icon='cloud')

for i in range(len(marker_met_html)):
    icon_bh = folium.Icon(color='orange',icon='temperature-half', prefix='fa')
    #iframe = folium.IFrame(marker_html[i], width=200, height=110)
    #popup = folium.Popup(iframe)
    html = folium.Html(marker_met_html[i], script=True)
    popup = folium.Popup(html, max_width=500)
    folium.Marker(
        location=marker_met_coordinates[i], popup=popup, tooltip=marker_met_tooltip[i], icon=icon_bh
    ).add_to(m)

for i in range(len(marker_tilsig_html)):
    icon_bh2 = folium.Icon(color='red',icon='temperature-half', prefix='fa')
    #iframe = folium.IFrame(marker_html[i], width=200, height=110)
    #popup = folium.Popup(iframe)
    html = folium.Html(marker_tilsig_html[i], script=True)
    popup = folium.Popup(html, max_width=500)
    folium.Marker(
        location=marker_tilsig_coordinates[i], popup=popup, tooltip=marker_tilsig_tooltip[i], icon=icon_bh2
    ).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, use_container_width=True, height=450, returned_objects=['last_object_clicked_tooltip']) #width=1100

# Visualize data?
if st_data['last_object_clicked_tooltip'] != None:
    st.markdown(f"You selected **{st_data['last_object_clicked_tooltip']}**")
    #if st.button(f"Visualizate data of **{st_data['last_object_clicked_tooltip']}**?",type='primary'):
        
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        button_h = st.button('Show historic (long-term) data', use_container_width=True)
    with col2:
        button_r = st.button('Show recent (short-term) data', use_container_width=True)
    with col4:
        if st_data['last_object_clicked_tooltip'] in marker_met_tooltip:
            # Load data from source
            row_idx = [idx for idx, s in enumerate(marker_met_html) if st_data['last_object_clicked_tooltip'] in s][0]
            source_str = sources_met[row_idx]
            data = load_data_MET(source_str)

            # Load into Dataframe and convert to CSV
            data_df_pre = MET_data_to_dataframe(data)
            data_df = data_processing_for_plotting(data_df_pre)

        elif st_data['last_object_clicked_tooltip'] in marker_tilsig_tooltip:
            # Load data from source
            row_idx = [idx for idx, s in enumerate(marker_tilsig_html) if st_data['last_object_clicked_tooltip'] in s][0]
            source_str = sources_tilsig[row_idx]
            data = load_data_Tilsig(source_str)

            # Load into Dataframe and convert to CSV
            data_df_pre = Tilsig_data_to_dataframe(data, row_idx)
            data_df = data_processing_for_plotting(data_df_pre)

        csv = convert_df(data_df)

        st.download_button(
            'Press to download data (CSV)',
            csv,
            'file.csv', # Give other name
            'text/csv',
            key='download-csv'
        )

    if button_h == True and st_data['last_object_clicked_tooltip'] in marker_met_tooltip:
        # Create plots in columns
        col1_1, col1_2 = st.columns(2)
        fig1 = plot_1(data_df)
        fig2 = plot_2(data_df)
        fig3 = plot_3(data_df)
        fig4 = plot_4(data_df)
        fig5, fig6 = plot_5_6(data_df)
        fig7, fig8 = plot_7_8(data_df)
        
        with col1_1:
            st.pyplot(fig1)

            st.pyplot(fig3)

            st.pyplot(fig5)

            st.pyplot(fig7)

        with col1_2:
            st.pyplot(fig2)

            st.pyplot(fig4)

            st.pyplot(fig6)

            st.pyplot(fig8)

    elif button_r == True and st_data['last_object_clicked_tooltip'] in marker_met_tooltip:          
        # Create plots in columns
        col2_1, col2_2 = st.columns(2)

        with col2_1:
            'Plots'

        with col2_2:
            'More plots'

    elif button_h == True and st_data['last_object_clicked_tooltip'] in marker_tilsig_tooltip:       
        # Create plots in columns
        col2_1, col2_2 = st.columns(2)
        fig1 = plot_1(data_df)
        fig2 = plot_2(data_df)
        fig3 = plot_3(data_df)
        fig4 = plot_4(data_df)
        fig5, fig6 = plot_5_6(data_df)
        fig7, fig8 = plot_7_8(data_df)

        with col2_1:
            st.pyplot(fig1)

            st.pyplot(fig3)

            st.pyplot(fig5)

            st.pyplot(fig7)

        with col2_2:
            st.pyplot(fig2)

            st.pyplot(fig4)

            st.pyplot(fig6)

            st.pyplot(fig8)

    elif button_r == True and st_data['last_object_clicked_tooltip'] in marker_tilsig_tooltip:  
        # Create plots in columns
        col2_1, col2_2 = st.columns(2)

        with col2_1:
            'Plots'

        with col2_2:
            'More plots'
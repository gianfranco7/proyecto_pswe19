import streamlit as st
import plotly.express as px
import geopandas as gpd
from pathlib import Path
from .logic import load_geo_json, get_incidence_df_with_geo_data

def render_heatmap_form():
    parent_folder = Path(__file__).resolve().parent
    map_dir = parent_folder.joinpath("geography", "Cantones_de_Costa_Rica.geojson")

    df = get_incidence_df_with_geo_data(map_dir)

    # with st.container(border=True):
    #     fig = px.choropleth_map(df, geojson=df.geometry, 
    #                             color="Total", locations="Canton",  
    #                             map_style="carto_positron", zoom=9)   

    #     st.plotly_chart(fig)

    st.dataframe(df)

    return False

# exporta ambos componentes visuales
HEATMAP = {
    "Heatmap":(
        render_heatmap_form,
        None
    )
}



import streamlit as st
import pandas as pd
import inference_utils as iu
import os

# GLobal Vars
__app_dir__ = os.path.dirname(os.path.abspath(__file__))
__active_df__ = iu.load_csv_as_dataframe(os.path.join(__app_dir__, "datasets\\incidencia.csv"))

# Configuración de la página
st.set_page_config(
    page_title="Estadisticas Criminales",
    page_icon="🔍",
    layout="wide"
)

st.write("# Estadisticas Criminales")

# Sidebar con información
with st.sidebar:
    st.header("Información")
    st.markdown("""
    Esta Applicacion permite visualizar y en alguna forma
                interactuar con las estadisticas criminales del OIJ de Costa Rica.
    """)

st.dataframe(__active_df__)


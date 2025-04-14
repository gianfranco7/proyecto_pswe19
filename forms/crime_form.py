import streamlit as st
from .geo import PROVINCES

def render_crime_form():
    st.write("Es peligroso el Canton donde Vive?")
    
    with st.container(border=True):
        col1, col2 = st.columns([1,1])


        with col1:
            province = st.selectbox(
                label="Seleccione una Provincia",
                options=PROVINCES.keys(), 
                key=1
            )
        with col2:
            selected_canton = st.selectbox(
                label="Seleccione un Canton",
                options=PROVINCES[province],
                key=2
            )

    return selected_canton



CRIME_FORM = {
    "Peligrosidad":(
        render_crime_form,
        "Formulario de prueba"
    )
}

import streamlit as st
from .geo import PROVINCES

# render del componente para input de usuario
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


# respuesta para el componente de render_query_form
def render_crime_form_response(canton:str):
    st.write(f"Esta es una respuesta para {canton}")

# exporta ambos componentes visuales
CRIME_FORM = {
    "Peligrosidad":(
        render_crime_form,
        render_crime_form_response
    )
}

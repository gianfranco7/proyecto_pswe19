import os
import streamlit as st
from .nlp_crime_form_logic import *
from .inference.inference import InferenceEngine

default_dataset_path = os.path.join(current_dir, "datasets", "Estadisticas.csv")
titulo = "Estadísticas Criminales apoyadas por IA"

def render_nlp_crime_form():
    if 'loaded_file' not in st.session_state:
        st.session_state.loaded_file = None
    if 'IE' not in st.session_state:
        st.session_state.IE = None

    # Configuración de la página
    # st.set_page_config(
    #     page_title=titulo,
    #     layout="wide"
    # )

    st.title(titulo)
    st.markdown("""
        Este form permite realizar una prueba de concepto de lo que sería realizar consultas al motor de inferencia por medio de 
        procesamiento de lenguaje natural (NLP). Para fines de este prototipo solamente se analisa un cantón de Costa Rica con base 
        en su nivel de incidencia ciminal calculado a partir de la base de datos de crimenes facilitada por el Organinismo de 
        Investigación Judicial (OIJ).
        
        Puede descargar dicha base de datos en formato .CSV por medio de la opción 'Exportar' siguiendo el siguiente enlace: 
        [Estadísticas Policiales OIJ](https://sitiooij.poder-judicial.go.cr/index.php/apertura/transparencia/estadisticas-policiales)
    """)

    col1, col2 = st.columns(2, border=True)

    with col1:
        # Opciones de configuración
        st.header("Configuración:")
        needs_reset = False

        if st.button("Cargar el archivo 'Default'"):
            needs_reset = st.session_state.loaded_file != default_dataset_path
            st.session_state.loaded_file = default_dataset_path
        
        uploaded_file = st.file_uploader("O bien, seleccione otro archivo .CSV:", type="csv")

        if uploaded_file is not None:
            needs_reset = st.session_state.loaded_file != uploaded_file
            st.session_state.loaded_file = uploaded_file

        if st.session_state.loaded_file is not None:
            # Display del contenido del .csv seleccionado
            st.subheader("Contenido:")
            if needs_reset:
                st.session_state.main_dataframe = load_main_dataframe(st.session_state.loaded_file)
            if st.session_state.main_dataframe is None:
                st.error("Error: Hubo un problema al cargar el archivo .CSV, por favor inténtelo de nuevo.")
            else:
                st.write(st.session_state.main_dataframe)

                # Cálculo y display de incidencias
                st.subheader("Incidencias:")
                st.write("Generado dinamicamente con base en el archivo .CSV seleccionado.")
                if needs_reset:
                    st.session_state.incidences_dataframe = create_incidence_dataframe(st.session_state.main_dataframe)
                if st.session_state.incidences_dataframe is None:
                    st.error("Error: El archivo seleccionado no tiene el formato correcto, por favor intente con otro archivo.")
                else:
                    st.write(st.session_state.incidences_dataframe)

                    # Generación de base de conocimientos
                    st.subheader("Base de conocimientos:")
                    st.write("Incluye contenido estático y contenido generado dinamicamente con base en el archivo .CSV seleccionado.")
                    if needs_reset:
                        st.session_state.kb_dataframe = create_kb_dataframe(st.session_state.incidences_dataframe)
                    if st.session_state.kb_dataframe is None:
                        st.error("Error: Hubo un problema al generar la base de conocimientos, por favor inténtelo de nuevo.")
                    else:
                        st.write(st.session_state.kb_dataframe)

                        if needs_reset:
                            # Carga de reglas al motor de inferencia
                            st.session_state.IE = InferenceEngine()
                            st.session_state.IE.knowledgeBase(st.session_state.kb_dataframe[kb_dataframe_col_name])

                            # Cargar el modelo de lenguaje natural y los datos
                            st.session_state.nlp_comps = load_nlp_model(st.session_state.incidences_dataframe)

    with col2:
        st.header("Aplicación:")

        if st.session_state.IE is None:
            st.write("Debe seleccionar un archivo .CSV antes de iniciar.")
        else:
            query = st.text_area(
                "Consulta:",
                placeholder="Ejemplo: ¿es Barva un lugar peligroso?",
                height=150
            )

            # Procesamiento
            if st.button("Enviar", type="primary"):
                if query.strip():
                    with st.spinner("Procesando texto..."):
                        res = conceptual_nlp_query_processing(st.session_state.nlp_comps, query, st.session_state.IE)
                        if res["matches"] == 0:
                            st.warning("No se detectaron entidades en el texto")
                        else:
                            st.subheader("Respuesta:")
                            st.write(res["reply"])

                            st.subheader("Resultados del Análisis:")
                            for frame in res["frames"]:
                                st.write(frame)
                else:
                    st.warning("Por favor ingrese un texto para analizar")

            st.subheader("Más ejemplos:")
            st.code("¿qué tan peligroso es montes de oca?")
            st.code("¿la ciudad de belen es peligrosa?")
            st.code("¿cuál es el nivel de peligro en dota?")

render_nlp_crime_form()

NLP_CRIME_FORM = {
    "Peligrosidad_NLP":(
        render_nlp_crime_form,
        None
    )
}
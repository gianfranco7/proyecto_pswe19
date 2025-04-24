import streamlit as st
from src import DEMO_FORMS


def main():
    st.title("Estadisticas Criminales")

    with st.sidebar:
        st.header("Consultas")
        form_options = ("Peligrosidad", "Natural Language Processing")
        selected_form = st.selectbox(
            label="Escoja una opcion:",
            options=form_options,
        )

        query, resp = DEMO_FORMS[selected_form]
     
# Renderiza y obtiene la query_data del componente (form) si existe   
    query_data = query()

# Si form genera query_data entonces renderiza el componente de respuesta
    if(query_data):
       resp(query_data)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Estadisticas Criminales", page_icon=":chart_with_upwards_trend:", layout="wide"
    )
    main()


import os
import pandas as pd
import streamlit as st
import inference_utils as iu
from forms import DEMO_FORMS

from datasets import incidence

def main():
    st.title("Estadisticas Criminales")

    with st.sidebar:
        st.header("Consultas")
        form_options = ("Peligrosidad", "Crimenes")
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

    st.dataframe(incidence)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Estadisticas Criminales", page_icon=":chart_with_upwards_trend:"
    )
    main()
    # with st.sidebar:
    #     st.markdown("---")
    #     st.markdown(
    #         '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://twitter.com/andfanilo">@andfanilo</a></h6>',
    #         unsafe_allow_html=True,
    #     )
    #     st.markdown(
    #         '<div style="margin-top: 0.75em;"><a href="https://www.buymeacoffee.com/andfanilo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a></div>',
    #         unsafe_allow_html=True,
    #     )
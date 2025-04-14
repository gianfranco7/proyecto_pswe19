

import streamlit as st
import pandas as pd
import inference_utils as iu
import os
from inference_init import is_dangerous_place

from forms import DEMO_FORMS

def main():
    st.title("Estadisticas Criminales")

    with st.sidebar:
        st.header("Consultas")
        form_options = ("Peligrosidad", "Crimenes")
        selected_form = st.selectbox(
            label="Escoja una opcion:",
            options=form_options,
        )

        form, comment = DEMO_FORMS[selected_form]
     
   
    canton = form()
    response = is_dangerous_place(canton)

    if(response):
        st.write("Es peligroso")
    else:
        st.write("No es Peligroso")


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
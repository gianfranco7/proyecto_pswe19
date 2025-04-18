import streamlit as st
from streamlit_echarts import st_echarts
from .data import PROVINCES, INCIDENCE_COLOR, SIMPLE_PIE_OPTIONS
from .logic import *

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
    stats = get_canton_incidence_statistics(canton)
    st_dic = stats.to_dict(orient='records')[0]  # Obtiene cada row del df como un diccionario (toma solo el row 0)

    province = st_dic.get('Provincia', '')
    inc = st_dic.get('Incidencia', 'No determinada')
    total = st_dic.get('Total', 0)
    perc_prov =  st_dic.get('Perc Provincia', 0.00)
    color = INCIDENCE_COLOR.get(inc, 'white')

    with st.container(border=True):
        markd = f'''El canton de :blue[{canton}] tiene una peligrosidad catalogada como :{color}[{inc}].  
        Esto se debe a que el canton registra :{color}[{total}] delitos, lo que representa :{color}[{round(perc_prov, 2)}%] del total registrado
        para la provincia de {province.title()}.
        '''
        st.markdown(markd)

    prov_stats = get_province_incidence_statistics(province)
    top_5 = prov_stats.sort_values(by="Total", ascending=False).head(5)
    data_list = top_5[['Total', 'Canton']].rename(columns={'Total': 'value', 'Canton': 'name'}).to_dict(orient='records')
    SIMPLE_PIE_OPTIONS["series"][0]["data"] = data_list
    with st.container(border=True):
         SIMPLE_PIE_OPTIONS['title']= {"text": "Top 5 Cantones Peligrosos", "subtext": province, "left": "center"}
         st_echarts(options=SIMPLE_PIE_OPTIONS, height="600px")




# exporta ambos componentes visuales
CRIME_FORM = {
    "Peligrosidad":(
        render_crime_form,
        render_crime_form_response
    )
}

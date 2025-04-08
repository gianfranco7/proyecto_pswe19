import streamlit as st
import spacy
from spacy.tokens import Span, Doc
from spacy.language import Language
from spacy.matcher import Matcher
import re
import pandas as pd
import os

# Ruta del archivo
current_dir = os.getcwd()
filename = "Estadisticas.csv"
dataset_path = os.path.join(current_dir, filename)

# Cargar CSV y extraer provincias y cantones únicos
def cargar_datos(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv, on_bad_lines='skip', encoding='utf-8')
        
        # Extraer provincias y cantones únicos (ajustar nombres de columnas si es necesario)
        provincias = set(df['Provincia'].str.upper().dropna().unique())
        cantones = set(df['Canton'].str.upper().dropna().unique())
        
        return df, provincias, cantones
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return None, set(), set()

df, provincias_db, cantones_db = cargar_datos(dataset_path)
if df is None:
    st.error("Error al cargar la base de datos. Verifique el archivo Estadisticas.csv")
    st.stop()


# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Crímenes",
    page_icon="🔍",
    layout="wide"
)

# Cargar el modelo en español (con cache para mejor performance)
@st.cache_resource
def load_nlp_model():
    nlp = spacy.load("es_core_news_sm")
    
    # Definir listas de provincias, cantones, procesos, sexo y horas
    # provincias = {"ALAJUELA", "SAN JOSÉ", "CARTAGO", "HEREDIA", "GUANACASTE", "PUNTARENAS", "LIMÓN"}
    # cantones = {"SAN CARLOS", "GRECIA", "ATENAS", "POÁS", "OROTINA", "ALAJUELA"}  
    provincias = provincias_db
    cantones = cantones_db
    procesos = {"SUMA", "RESTA", "CONTEO"} 
    sexo = {"MUJER", "HOMBRE"}
    genero_relacionado = {"NIÑA": "MUJER", "NIÑO": "HOMBRE", "ABUELA": "MUJER", "ABUELO": "HOMBRE"}

    # Mapeo de palabras clave a horas específicas
    mapeo_horas = {
        "madrugada": "04:00",
        "mañana": "09:00",
        "tarde": "16:00",
        "noche": "21:00"
    }

    # Crear el Matcher para detectar entidades
    matcher = Matcher(nlp.vocab)

    # Agregar patrones de provincia y canton al matcher
    for nombre in provincias.union(cantones):
        pattern = [{"LOWER": token.lower()} for token in nombre.split()]
        matcher.add("PROVINCIA_CANTON", [pattern])

    # Agregar patrones de procesos
    for nombre in procesos:
        pattern = [{"LOWER": token.lower()} for token in nombre.split()]
        matcher.add("PROCESO", [pattern])

    # Agregar patrones de sexo
    for nombre in sexo.union(genero_relacionado):
        pattern = [{"LOWER": token.lower()} for token in nombre.split()]
        matcher.add("SEXO", [pattern])

    # Agregar patrón para detectar horas (formato de 24 horas)
    pattern_hora = [{"TEXT": {"regex": r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b"}}]
    matcher.add("HORA", [pattern_hora])

    # Agregar patrón para las palabras que representan las horas del día
    pattern_palabra_hora = [{"LOWER": {"in": list(mapeo_horas.keys())}}]
    matcher.add("PALABRA_HORA", [pattern_palabra_hora])

    @Language.component("detectar_entidades_personalizadas")
    def detectar_entidades_personalizadas(doc):
        matches = matcher(doc)
        nuevas_entidades = []
        ya_detectado_provincias = set()

        for match_id, start, end in matches:
            text = doc[start:end].text

            if text in provincias:
                if text not in ya_detectado_provincias:
                    nuevas_entidades.append(Span(doc, start, end, label="PROVINCIA"))
                    ya_detectado_provincias.add(text)
                else:
                    nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
            elif text in cantones:
                nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
            elif text in procesos:
                nuevas_entidades.append(Span(doc, start, end, label="PROCESO"))
            elif text in sexo:
                nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
            elif text.lower() in genero_relacionado:
                nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
            elif re.match(r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b", text):
                nuevas_entidades.append(Span(doc, start, end, label="HORA"))
            elif text.lower() in mapeo_horas:
                nuevas_entidades.append(Span(doc, start, end, label="HORA"))
            else:
                nuevas_entidades.append(doc[start:end])

        doc.set_ents(nuevas_entidades)
        return doc

    if "detectar_entidades_personalizadas" not in nlp.pipe_names:
        nlp.add_pipe("detectar_entidades_personalizadas", after="ner")
    
    return nlp, provincias, cantones, procesos, sexo, genero_relacionado, mapeo_horas

# Cargar el modelo y los datos
nlp, provincias, cantones, procesos, sexo, genero_relacionado, mapeo_horas = load_nlp_model()

# Requisitos para cada proceso
requisitos_procesos = {
    "SUMA": ["PROVINCIA", "CANTON"],
    "RESTA": ["PROVINCIA", "CANTON", "HORA"],
    "CONTEO": ["PROVINCIA", "CANTON", "SEXO"]
}

# Interfaz de usuario
st.title("🔍 Calculadora de Crímenes a Nivel País")
st.markdown("---")

# Sidebar con información
with st.sidebar:
    st.header("Información")
    st.markdown("""
    Esta aplicación permite analizar información sobre crímenes utilizando:
    - **Procesos**: SUMA, RESTA, CONTEO
    - **Entidades**: Provincias, Cantones, Sexo, Horas
    """)
    
    st.header("Requisitos por Proceso")
    for proceso, reqs in requisitos_procesos.items():
        st.markdown(f"**{proceso}**: {', '.join(reqs)}")

# Selección de proceso
proceso_seleccionado = st.radio(
    "Seleccione el proceso a realizar:",
    sorted(procesos),
    horizontal=True,
    index=0
)

# Entrada de texto
texto = st.text_area(
    "Ingrese el texto con la información requerida:",
    placeholder="Ejemplo: 'En ALAJUELA, cantón SAN CARLOS, a las 15:00...'",
    height=150
)

# Procesamiento
if st.button("Analizar Texto", type="primary"):
    if texto.strip():
        with st.spinner("Procesando texto..."):
            # Obtener entidades
            doc = nlp(texto)
            entidades = {}
            for ent in doc.ents:
                if ent.label_ not in entidades:
                    entidades[ent.label_] = []
                entidades[ent.label_].append(ent.text)
            
            # Mostrar resultados
            st.subheader("Resultados del Análisis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Entidades detectadas:**")
                if entidades:
                    for tipo, valores in entidades.items():
                        st.markdown(f"- **{tipo}**: {', '.join(valores)}")
                else:
                    st.warning("No se detectaron entidades en el texto")
            
            with col2:
                st.markdown("**Validación de requisitos:**")
                faltantes = [req for req in requisitos_procesos[proceso_seleccionado] 
                           if req not in entidades]
                
                if faltantes:
                    st.error(f"Faltan los siguientes datos para {proceso_seleccionado}:")
                    for req in faltantes:
                        st.markdown(f"- {req}")
                else:
                    st.success("✅ Todos los requisitos están completos")
                    st.balloons()
                    
                    # Aquí iría la lógica específica del proceso
                    # st.markdown(f"**Proceso {proceso_seleccionado} completado con éxito**")
                    
                      # Lógica específica para cada proceso
                    if proceso_seleccionado == "RESTA":
                        # Cargar datos (aquí deberías cargar tu DataFrame real)
                    
                        
                        # provincia = entidades["PROVINCIA"][0]
                        # canton = entidades["CANTON"][0]
                        # hora = entidades["HORA"][0]
                        
                        # Ejecutar el análisis RESTA
                        # responder_probabilidad_delito_violento(
                        #     df=df,
                        #     provincia=provincia,
                        #     canton=canton,
                        #     hora_input=hora,
                        #     st_component=st
                        # )
                        st.markdown(f"**Proceso {proceso_seleccionado} completado con éxito**")
                    
                    elif proceso_seleccionado == "SUMA":
                        # Lógica para SUMA
                        # pass
                        st.markdown(f"**Proceso {proceso_seleccionado} completado con éxito**")
                    
                    elif proceso_seleccionado == "CONTEO":
                        # Lógica para CONTEO
                        # pass
                        st.markdown(f"**Proceso {proceso_seleccionado} completado con éxito**")
    else:
        st.warning("Por favor ingrese un texto para analizar")

# Información adicional
st.markdown("---")
expander = st.expander("ℹ️ Acerca de esta aplicación")
expander.markdown("""
Esta aplicación utiliza:
- **spaCy**: Para el procesamiento de lenguaje natural
- **Streamlit**: Para la interfaz web
- **Modelo es_core_news_sm**: Para el reconocimiento de entidades en español

Ejemplos de texto que puedes usar:
- *"En ALAJUELA, cantón SAN CARLOS, a las 15:00 hubo un incidente"*
- *"Reporte de HEREDIA, cantón BARVA, involucrando a una MUJER"*
- *"En PUNTARENAS, cantón MONTES DE ORO, durante la tarde"*
""")
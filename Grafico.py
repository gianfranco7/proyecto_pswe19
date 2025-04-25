import streamlit as st
import spacy
from spacy.tokens import Span, Doc
from spacy.language import Language
from spacy.matcher import Matcher
import re
import pandas as pd
import os
import numpy as np
from datetime import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Ruta del archivo
current_dir = os.getcwd()
filename = "Estadisticas.csv"
dataset_path = os.path.join(current_dir, "datasets", filename)

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

# ===========================
# Función principal del caso 1
# ===========================
# Función vectorizada para verificar si la hora está dentro del rango
def hora_en_rango_vectorizada(df, hora_input):
    rango_horas = df['Hora'].str.split(' - ', expand=True)
    rango_horas = rango_horas.apply(lambda x: pd.to_datetime(x, format='%H:%M:%S').dt.time)
    return (rango_horas[0] <= hora_input) & (rango_horas[1] >= hora_input)

def responder_probabilidad_delito_violento(df, provincia, canton, hora_input):
    # Paso 1: Filtrar delitos violentos
    df_filtrado = df[
        (df['Provincia'] == provincia) &
        (df['Canton'] == canton) &
        (df['Delito'].str.contains("VIOLENCIA|LESIONES|HOMICIDIO", case=False, na=False)) &
        hora_en_rango_vectorizada(df, hora_input)
    ]

    if df_filtrado.empty:
        # print("No hay datos de delitos violentos para los criterios dados.")
        pMensaje = "No hay datos de delitos violentos para los criterios dados."
        return pMensaje

    # Paso 2: Calcular frecuencia relativa
    total_delitos_canton = df[
        (df['Provincia'] == provincia) &
        (df['Canton'] == canton)
    ]
    frecuencia = len(df_filtrado) / len(total_delitos_canton) if len(total_delitos_canton) > 0 else 0

    # Paso 3: Variables difusas
    hora = ctrl.Antecedent(np.arange(0, 24, 1), 'hora')
    zona_riesgo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'zona_riesgo')
    nivel_alerta = ctrl.Consequent(np.arange(0, 101, 1), 'nivel_alerta')

    # Hora difusa
    hora['madrugada'] = fuzz.trapmf(hora.universe, [0, 0, 4, 6])
    hora['mañana'] = fuzz.trapmf(hora.universe, [5, 7, 10, 12])
    hora['tarde'] = fuzz.trapmf(hora.universe, [12, 14, 17, 18])
    hora['noche'] = fuzz.trapmf(hora.universe, [18, 20, 23, 23])

    # Zona de riesgo
    zona_riesgo['baja'] = fuzz.trimf(zona_riesgo.universe, [0, 0, 0.3])
    zona_riesgo['media'] = fuzz.trimf(zona_riesgo.universe, [0.2, 0.5, 0.7])
    zona_riesgo['alta'] = fuzz.trimf(zona_riesgo.universe, [0.6, 1, 1])

    # Nivel de alerta
    nivel_alerta['bajo'] = fuzz.trimf(nivel_alerta.universe, [0, 0, 40])
    nivel_alerta['medio'] = fuzz.trimf(nivel_alerta.universe, [30, 50, 70])
    nivel_alerta['alto'] = fuzz.trimf(nivel_alerta.universe, [60, 100, 100])

    # Reglas
    reglas = [
        ctrl.Rule(hora['noche'] & zona_riesgo['alta'], nivel_alerta['alto']),
        ctrl.Rule(hora['madrugada'] & zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(hora['mañana'] & zona_riesgo['baja'], nivel_alerta['bajo']),
        ctrl.Rule(hora['tarde'] & zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(zona_riesgo['alta'], nivel_alerta['alto']),
        ctrl.Rule(zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(zona_riesgo['baja'], nivel_alerta['bajo']),
    ]

    sistema_ctrl = ctrl.ControlSystem(reglas)
    sistema_sim = ctrl.ControlSystemSimulation(sistema_ctrl)

    # Entradas
    sistema_sim.input['hora'] = hora_input.hour
    sistema_sim.input['zona_riesgo'] = frecuencia

    try:
        sistema_sim.compute()
        resultado = sistema_sim.output['nivel_alerta']
        pMensaje = f"\n🛑 Nivel de alerta por delito violento en {provincia}, {canton} a las {hora_input} es : {resultado:.2f}%"
        # print(f"\n🛑 Nivel de alerta por delito violento en {provincia}, {canton} a las {hora_input}: {resultado:.2f}%")
        return pMensaje
    except Exception as e:
        pMensaje = f"Error en el sistema difuso: {e}"
        # print(f"Error en el sistema difuso: {e}")
        return pMensaje


# ===========================
# Función principal del caso 2
# ===========================
def evaluar_vulnerabilidad(df, edad_input, sexo_input, provincia, canton):
    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]
    if df_zona.empty:
        print("No hay datos para la zona.")
        return None

    sexo_str = 'HOMBRE' if sexo_input == 0 else 'MUJER'
    delitos_totales = len(df)
    total_zona = len(df_zona)
    proporcion_zona = total_zona / delitos_totales if delitos_totales > 0 else 0
    proporcion_sexo = df_zona['Sexo'].value_counts(normalize=True).get(sexo_str, 0)

    # Variables difusas
    edad = ctrl.Antecedent(np.arange(0, 101, 1), 'edad')
    riesgo_sexo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'riesgo_sexo')
    zona_riesgo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'zona_riesgo')
    nivel = ctrl.Consequent(np.arange(0, 101, 1), 'nivel')

    # Edad
    edad['joven'] = fuzz.trimf(edad.universe, [0, 15, 30])
    edad['adulto'] = fuzz.trimf(edad.universe, [25, 40, 60])
    edad['adulto_mayor'] = fuzz.trimf(edad.universe, [55, 75, 100])

    # Riesgo sexo
    riesgo_sexo['bajo'] = fuzz.trimf(riesgo_sexo.universe, [0, 0, 0.3])
    riesgo_sexo['medio'] = fuzz.trimf(riesgo_sexo.universe, [0.2, 0.5, 0.7])
    riesgo_sexo['alto'] = fuzz.trimf(riesgo_sexo.universe, [0.6, 1, 1])

    # Zona
    zona_riesgo['baja'] = fuzz.trimf(zona_riesgo.universe, [0, 0, 0.3])
    zona_riesgo['media'] = fuzz.trimf(zona_riesgo.universe, [0.2, 0.5, 0.7])
    zona_riesgo['alta'] = fuzz.trimf(zona_riesgo.universe, [0.6, 1, 1])

    # Vulnerabilidad (salida)
    nivel['muy_baja'] = fuzz.trimf(nivel.universe, [0, 0, 20])
    nivel['baja'] = fuzz.trimf(nivel.universe, [10, 25, 40])
    nivel['media'] = fuzz.trimf(nivel.universe, [30, 50, 70])
    nivel['alta'] = fuzz.trimf(nivel.universe, [60, 75, 90])
    nivel['muy_alta'] = fuzz.trimf(nivel.universe, [80, 100, 100])

    # Reglas
    reglas = [
        ctrl.Rule(edad['joven'] & riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta']),
        ctrl.Rule(edad['joven'] & riesgo_sexo['medio'] & zona_riesgo['alta'], nivel['alta']),
        ctrl.Rule(edad['adulto'] & riesgo_sexo['medio'] & zona_riesgo['media'], nivel['media']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['alto'] & zona_riesgo['media'], nivel['alta']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta']),
        ctrl.Rule(edad['joven'] | edad['adulto'] | edad['adulto_mayor'], nivel['media']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['medio'] & zona_riesgo['baja'], nivel['baja']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['bajo'] & zona_riesgo['baja'], nivel['muy_baja']),
        ctrl.Rule(riesgo_sexo['bajo'] & zona_riesgo['baja'], nivel['muy_baja']),
        ctrl.Rule(riesgo_sexo['medio'] & zona_riesgo['media'], nivel['media']),
        ctrl.Rule(riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta'])

        # ctrl.Rule(True, nivel['media'])  # 🛟 Regla de respaldo
    ]

    sistema_ctrl = ctrl.ControlSystem(reglas)
    sim = ctrl.ControlSystemSimulation(sistema_ctrl)

    # Entradas
    sim.input['edad'] = edad_input
    sim.input['riesgo_sexo'] = proporcion_sexo
    sim.input['zona_riesgo'] = proporcion_zona

    try:
        sim.compute()

        if 'nivel' in sim.output:
            resultado = sim.output['nivel']
            pMensaje = f"📌 Nivel de vulnerabilidad para {sexo_str}, {edad_input} años en {provincia}, {canton}: {resultado:.2f}%"
            # print(f"📌 Nivel de vulnerabilidad para {sexo_str}, {edad_input} años en {provincia}, {canton}: {resultado:.2f}%")
            return pMensaje
        else:
            print("❌ No se pudo determinar el nivel de vulnerabilidad.")
            # print("❌ No se pudo determinar el nivel de vulnerabilidad.")
            pMensaje ="❌ No se pudo determinar el nivel de vulnerabilidad."
            return pMensaje

    except Exception as e:
        # print(f"❌ Error al calcular vulnerabilidad: {e}")
        pMensaje = f"❌ Error al calcular vulnerabilidad: {e}"
        return pMensaje


# ===========================
# Función principal del caso 3
# ===========================

# Categorizar hora como franja difusa
def obtener_franja_horaria(hora_obj):
    h = hora_obj.hour
    if 0 <= h < 6:
        return 'madrugada'
    elif 6 <= h < 12:
        return 'mañana'
    elif 12 <= h < 18:
        return 'tarde'
    else:
        return 'noche'

def categorizar_hora(hora_str, ref_hora):
    try:
        h_inicio, h_fin = hora_str.split(" - ")
        h_inicio = pd.to_datetime(h_inicio).hour
        h_fin = pd.to_datetime(h_fin).hour
        h = ref_hora.hour
        if h_inicio <= h <= h_fin:
            return obtener_franja_horaria(ref_hora)
    except:
        return None
        
# Función para detectar tendencia
def tendencia_delictiva(df, provincia, canton, hora_input):
    franja = obtener_franja_horaria(hora_input)

    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)].copy()
    if df_zona.empty:
        return "No hay datos en esa zona."

    df_zona['Franja'] = df_zona['Hora'].apply(lambda h: categorizar_hora(h, hora_input))
    df_franja = df_zona[df_zona['Franja'] == franja]
    if df_franja.empty:
        return "No hay registros para esa franja horaria."

    # 🔧 Convertir Fecha a datetime
    df_franja['Fecha'] = pd.to_datetime(df_franja['Fecha'], errors='coerce')

    # Agrupar por mes
    df_franja['Mes'] = df_franja['Fecha'].dt.to_period('M')
    conteos_mensuales = df_franja.groupby('Mes').size().sort_index()

    if len(conteos_mensuales) < 3:
        return "No hay suficientes datos mensuales para analizar tendencia."

    # Calcular la pendiente (crecimiento)
    x = np.arange(len(conteos_mensuales))
    y = conteos_mensuales.values
    pendiente, _ = np.polyfit(x, y, 1)

    # Crear sistema difuso
    pendiente_input = ctrl.Antecedent(np.arange(-10, 11, 1), 'pendiente')
    alerta = ctrl.Consequent(np.arange(0, 101, 1), 'alerta')

    pendiente_input['estable'] = fuzz.trimf(pendiente_input.universe, [-1, 0, 1])
    pendiente_input['creciente'] = fuzz.trimf(pendiente_input.universe, [0, 3, 6])
    pendiente_input['acelerado'] = fuzz.trimf(pendiente_input.universe, [5, 10, 10])

    alerta['baja'] = fuzz.trimf(alerta.universe, [0, 0, 40])
    alerta['media'] = fuzz.trimf(alerta.universe, [30, 50, 70])
    alerta['alta'] = fuzz.trimf(alerta.universe, [60, 100, 100])

    reglas = [
        ctrl.Rule(pendiente_input['estable'], alerta['baja']),
        ctrl.Rule(pendiente_input['creciente'], alerta['media']),
        ctrl.Rule(pendiente_input['acelerado'], alerta['alta'])
    ]

    sistema = ctrl.ControlSystem(reglas)
    sim = ctrl.ControlSystemSimulation(sistema)

    sim.input['pendiente'] = pendiente
    sim.compute()

    resultado = sim.output['alerta']

    pMensaje = f"  \n📍 Zona: {provincia}, {canton}  \n🕓 Franja horaria: {franja} (hora: {hora_input})  \n📈 Pendiente mensual de delitos: {pendiente:.2f}  \n ⚠️ Nivel de alerta por tendencia creciente: {resultado:.2f}%"

    # Graficar tendencia
    conteos_mensuales.plot(title="Tendencia mensual de delitos en franja horaria")
    plt.ylabel("Número de delitos")
    plt.xlabel("Mes")
    plt.grid(True)
    plt.tight_layout()
       # Mostrar en Streamlit
    st.pyplot(plt.gcf())  # gcf = get current figure

    plt.clf()  # Limpia la figura actual para evitar que se acumulen si se vuelve a llamar la función


    return pMensaje

# ===========================
# Función principal del caso 4
# ===========================

# Función para extraer delitos probables según hora y zona
def delito_probable_por_hora_y_zona(df, provincia, canton, hora_input):
    # Paso 1: Filtrar por zona
    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]
    if df_zona.empty:
        # print("No hay datos para esa zona.")
        pMensaje = "No hay datos para esa zona."
        return pMensaje

    # Paso 2: Categorizar hora en bandas
    hora_num = hora_input.hour
    if 0 <= hora_num < 6:
        franja = 'madrugada'
    elif 6 <= hora_num < 12:
        franja = 'mañana'
    elif 12 <= hora_num < 18:
        franja = 'tarde'
    else:
        franja = 'noche'

    # Paso 3: Crear columna auxiliar para franja horaria
    def categorizar_hora(hora_str):
        try:
            h_inicio, h_fin = hora_str.split(" - ")
            h_inicio = pd.to_datetime(h_inicio).hour
            h_fin = pd.to_datetime(h_fin).hour
            if 0 <= hora_num < 6 and h_inicio < 6:
                return 'madrugada'
            elif 6 <= hora_num < 12 and 6 <= h_inicio < 12:
                return 'mañana'
            elif 12 <= hora_num < 18 and 12 <= h_inicio < 18:
                return 'tarde'
            elif 18 <= hora_num < 24 and 18 <= h_inicio <= 23:
                return 'noche'
        except:
            return 'otro'

    df_zona['Franja'] = df_zona['Hora'].apply(categorizar_hora)
    df_franja = df_zona[df_zona['Franja'] == franja]

    if df_franja.empty:
        pMensaje = f"No hay registros para {franja} en {provincia}, {canton}."
        return pMensaje

    # Paso 4: Calcular frecuencia relativa de delitos
    frecuencias = df_franja['Delito'].value_counts(normalize=True)
    pMensaje = f"📊 Delitos más probables en {provincia}, {canton} durante la {franja}:"

    for delito, freq in frecuencias.items():
        nivel = (
            "Alta" if freq > 0.5 else
            "Media" if freq > 0.2 else
            "Baja"
        )
        pMensaje += f"  \n• {delito} → {nivel} probabilidad ({freq:.2%})"

    # Extra: mostrar el más probable
    delito_top = frecuencias.idxmax()
    pMensaje += f"  \n  \n🔎 Delito más probable: {delito_top} ({frecuencias.max():.2%})"
    return pMensaje



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
    provincias = provincias_db
    cantones = cantones_db
    procesos = {"Delito_Mas_probable", "Probabilidad_Delito", "Tendencia_Delictiva","Vulnerabilidad"} 
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

     # Agregar patrón para detectar edad (número seguido de la palabra "edad")
    pattern_edad = [
        {"LIKE_NUM": True},
        {"LOWER": "años"}
    ]
    matcher.add("EDAD", [pattern_edad])

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
            elif match_id == nlp.vocab.strings["EDAD"]:
                # Extraer solo el número como edad
                edad_numero = doc[start].text  # El primer token es el número
                span = Span(doc, start, start+1, label="EDAD")  # Solo el número
                nuevas_entidades.append(span)
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
    "Delito_Mas_probable": ["PROVINCIA", "CANTON","HORA"],
    "Probabilidad_Delito": ["PROVINCIA", "CANTON", "HORA"],
    "Tendencia_Delictiva": ["PROVINCIA", "CANTON", "HORA"],
    "Vulnerabilidad": ["PROVINCIA", "CANTON","EDAD","SEXO"]  
}

# Interfaz de usuario
st.title("🔍 Calculadora de Crímenes a Nivel País")
st.markdown("---")

# Sidebar con información
with st.sidebar:
    st.header("Información")
    st.markdown("""
    Esta aplicación permite analizar información sobre crímenes utilizando:
    - **Procesos**: Delito_Mas_probable, Probabilidad_delito, Tendencia_Delictiva, Vulnerabilidad
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
            doc = nlp(texto.upper())
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
                    if proceso_seleccionado == "Probabilidad_Delito":

                        provincia = entidades["PROVINCIA"][0]
                        canton = entidades["CANTON"][0]
                        hora_str = entidades["HORA"][0]  # Ejemplo: "15:00"
                        hora_partes = hora_str.split(":")
                        hora_obj = time(hour=int(hora_partes[0]), minute=int(hora_partes[1]))  # Crea un objeto time

                        
                        # Ejecutar
                        resultado = responder_probabilidad_delito_violento(
                            df=df,
                            provincia=provincia,
                            canton=canton,
                            hora_input=hora_obj
                        )
                        st.markdown(f"**Resultado:** {resultado}")
                    
                    elif proceso_seleccionado == "Delito_Mas_probable":
                        # Lógica para 
                        provincia = entidades["PROVINCIA"][0]
                        canton = entidades["CANTON"][0]
                        hora_str = entidades["HORA"][0]  # Ejemplo: "15:00"
                        hora_partes = hora_str.split(":")
                        hora_obj = time(hour=int(hora_partes[0]), minute=int(hora_partes[1]))  # Crea un objeto time

                        
                        # Ejecutar el análisis Probabilidad_Delito
                        resultado = delito_probable_por_hora_y_zona(
                            df=df,
                            provincia=provincia,
                            canton=canton,
                            hora_input=hora_obj
                        )

                        st.markdown(f"**Resultado:** {resultado}")
                    
                    elif proceso_seleccionado == "Tendencia_Delictiva":

                        provincia = entidades["PROVINCIA"][0]
                        canton = entidades["CANTON"][0]
                        hora_str = entidades["HORA"][0]  # Ejemplo: "15:00"
                        hora_partes = hora_str.split(":")
                        hora_obj = time(hour=int(hora_partes[0]), minute=int(hora_partes[1]))  # Crea un objeto time

                        
                        # Ejecutar 
                        resultado = tendencia_delictiva(
                            df=df,
                            provincia=provincia,
                            canton=canton,
                            hora_input=hora_obj
                        )

                        st.markdown(f"**Resultado:** {resultado}")
                    
                    elif proceso_seleccionado == "Vulnerabilidad":
                        provincia = entidades["PROVINCIA"][0]
                        canton = entidades["CANTON"][0]
                        edad = int(entidades["EDAD"][0])
                        sexo = entidades["SEXO"][0]
                        sexo = 0 if sexo == "HOMBRE" else 1 if sexo == "MUJER" else -1

                        # Ejecutar 
                        resultado = evaluar_vulnerabilidad(
                            df= df,
                            edad_input= edad,
                            sexo_input= sexo,
                            provincia= provincia,
                            canton= canton
                        )
                        st.markdown(f"**Resultado:** {resultado}")
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


import os
import pandas as pd
from datetime import datetime, time
import numpy as np
import spacy
from spacy.matcher import Matcher
import pytholog as pl
from .inference import InferenceEngine
import io

current_dir = os.getcwd()
geo_path = os.path.join(current_dir, "src", "inference", "kb_files", "geo.txt")
kb_dataframe_col_name = "Knowledge Base"

# Corrige los headers del archivo .csv en caso de ser necesario
def fix_csv_headers(uploaded_file):
    try:
        first_line = uploaded_file.readline().decode("utf-8")

        cols = first_line.split(",")
        if cols[3] != "Hora":
            cols.insert(3, "Hora")
            first_line = ",".join(cols)

        new_file = first_line + uploaded_file.read().decode("utf-8")
        return io.StringIO(new_file)

    except:
        return uploaded_file

def load_main_dataframe(file):
    file = fix_csv_headers(file)
    df = pd.read_csv(file, on_bad_lines='skip', encoding='utf-8')
    df = df.map(lambda x: fix_unicode(x) if isinstance(x, str) else x)
    return df
    
def fix_unicode(str: str):
    str = str.replace("&#193;", "Á")
    str = str.replace("&#201;", "É")
    str = str.replace("&#205;", "Í")
    str = str.replace("&#209;", "Ñ")
    str = str.replace("&#211;", "Ó")
    str = str.replace("&#218;", "Ú")
    str = str.replace("&#220;", "Ü")
    return str

def create_incidence_dataframe(df: pd.DataFrame):
    try:
        # Drop de la columna Distrito ya que no aporta datos
        if 'Distrito' in df.columns:
            df.drop('Distrito', axis=1, inplace=True)

        # Convertir tipo de dato de la columna Fecha a Datetime
        df['Fecha'] = pd.to_datetime(df['Fecha'])

        # Convertir solo las columnas de tipo 'object' a 'str'
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)

        # Remover los rows donde se desconoce el lugar del Delito
        df = df[df['Provincia'] != "DESCONOCIDO"]
        # Rellenar los datos de Cantón con el valor de la provincia cuando Cantón = DESCONOCIDO
        df['Canton'] =  df['Canton'].where(df['Canton'] != 'DESCONOCIDO', df['Provincia'])
        # La única excepción es Guanacaste cuyo Cantón Central no es Guanacaste sino Liberia
        df['Canton'] = df['Canton'].where(df['Canton'] != 'GUANACASTE', 'LIBERIA')

        # Esta función toma los valores de la hora y los clasifica
        # en Madrugada, Mañana, Tarde o Noche de acuerdo al rango horario
        def hour_fuzzier(hour_range):
            time_string = hour_range.split("-")[1].strip()

            dawn_start = time(00, 00, 00)
            dawn_end = time(5, 59, 59)
            morn_start = time(6, 00, 00)
            morn_end = time(11, 59, 59)
            aftn_start = time(12, 00, 00)
            aftn_end = time(17, 59, 59)
            nigt_start = time(18, 00, 00)
            nigt_end = time(23, 59, 59)
            
            #print(time_string)   
            time_object = datetime.strptime(time_string, "%H:%M:%S").time()
            if dawn_start <= time_object <= dawn_end:
                return "Madrugada"
            elif morn_start <= time_object <= morn_end:
                return "Mañana"
            elif aftn_start <= time_object <= aftn_end:
                return "Tarde"
            else:
                return "Noche"

        #Insertar la columna fuzzy para la hora del delito en el dataframe    
        fuzzy_time_col = df['Hora'].apply(lambda x: hour_fuzzier(x))
        df.insert(4, "Hora Fuzzy", fuzzy_time_col)

        # Drop de la columna Distrito ya que no aporta datos
        if 'Hora' in df.columns:
            df.drop('Hora', axis=1, inplace=True)

        #print("\r\nCLEAN ESTADISTICAS.CSV")
        #print(df.head())

        # Intentaremos hacer una Fuzzy sobre la incidencia de un delito dado
        # La incidencia del delito seria la cantidad de delitos de este tipo dividido entre la cantidad total de delitos
        # posteriormente con todas las incidencias se pueden clasificar 

        #Tabla de incidencia 
        incidence = df.groupby(['Provincia', 'Canton', 'Hora Fuzzy']).size().reset_index(name="Incidencia")

        #Pivotea los valores de Incidencia como columnas y los tamaños del conjunto como valores
        piv_df = incidence.pivot_table(index=['Provincia', 'Canton'], columns='Hora Fuzzy', values='Incidencia', fill_value=0).reset_index()

        #Formatea la tabla resultante
        piv_df.columns.name = None # Remover el nombre de las columnas
        piv_df = piv_df.rename_axis(None, axis=1)

        #Convertir los valores de float a enteros
        f_cols = ['Madrugada', 'Mañana', 'Tarde', 'Noche']
        piv_df[f_cols] = piv_df[f_cols].map(np.int64)

        piv_df['Total'] = piv_df['Madrugada'] + piv_df['Mañana'] + piv_df['Tarde'] + piv_df['Noche']

        tdf = piv_df.groupby('Provincia').sum().reset_index()
        tdf.drop('Canton', axis=1, inplace=True)
        prov_totals = tdf[['Provincia', 'Total']].sort_values(by='Total')

        def province_percentile(x):
            province = x['Provincia']
            c_total = x['Total']
            total = prov_totals.loc[prov_totals['Provincia'] == province, 'Total'].values[0]  # Extracts the first matching value
            return (c_total/total)* 100


        piv_df['Perc Provincia'] = piv_df.apply(province_percentile, axis=1)

        total_incidents = piv_df['Total'].sum()

        piv_df['Perc Pais'] = piv_df.apply(lambda x: 0 if x['Total'] == 0 else ((x['Total']/total_incidents) * 100) , axis=1)

        # Debido a la distribucion de los datos se usaran los Quartiles para determinar las categorias de incidencia de Delitos 

        q1 = piv_df['Total'].quantile(0.15)
        q2 = piv_df['Total'].quantile(0.38)
        q3 = piv_df['Total'].quantile(0.62)
        q4 = piv_df['Total'].quantile(0.85)

        def place_ranker(incidents):
            if incidents <= q1:
                return 'Muy Baja'
            elif q1 < incidents < q2:
                return 'Baja'
            elif q2 <= incidents < q3:
                return 'Moderada'
            elif q3 <= incidents < q4:
                return 'Alta'
            else:
                return 'Muy Alta'

        piv_df['Incidencia'] = piv_df['Total'].apply(place_ranker)

        #print("\r\nINCIDENCIAS.CSV")
        #print(piv_df.head())
        return piv_df
    
    except:
        return None
    
def add_row(df: pd.DataFrame, col_name: str, value: str):
    return pd.concat([df, pd.DataFrame({col_name: [value]})], ignore_index=True)

def format_str_for_rule(str):
    return str.lower().replace(" ", "_")

def df_column_to_facts(df: pd.DataFrame, column: str, fact_name: str):
    unique_values = df[column].unique()
    unique_values = np.vectorize(lambda x: f"{format_str_for_rule(fact_name)}({format_str_for_rule(x)})")(unique_values)
    return unique_values

def format_rule(rule: str):
    return f"{rule.rstrip(".")}"

def create_kb_dataframe(incidences: pd.DataFrame):
    # Carga reglas del archivo geo.txt
    with open(geo_path, "r") as file:
        geo_data = file.readlines()

    kb = pd.DataFrame([item.strip() for item in geo_data], columns=[kb_dataframe_col_name])
    kb = kb.dropna(how="all")
    kb = kb[kb.apply(lambda row: row.astype(str).str.strip().any(), axis=1)]
    
    # Genera reglas de incidencias con base en las incidencias calculadas
    incidence_levels = df_column_to_facts(incidences, "Incidencia", "incidence_level")
    for val in incidence_levels:
        kb = add_row(kb, kb_dataframe_col_name, val)

    # Genera reglas de incidencias por cantón con base en las incidencias calculadas
    for i in range(incidences.shape[0]):
        canton = format_str_for_rule(f"{incidences.Canton[i]}")
        if incidences.Canton[i] == incidences.Provincia[i]:
            canton += "_cc"
        incidence_level = format_str_for_rule(f"{incidences.Incidencia[i]}")
        kb = add_row(kb, kb_dataframe_col_name, f"canton_incidence_level({canton}, {incidence_level})")
    
    # Agrega reglas adicionales
    kb = add_row(kb, kb_dataframe_col_name, "dangerous_incidence_level(alta)")
    kb = add_row(kb, kb_dataframe_col_name, "dangerous_incidence_level(muy_alta)")
    kb = add_row(kb, kb_dataframe_col_name, "is_dangerous(C) :- canton_incidence_level(C, L), dangerous_incidence_level(L)")

    kb = kb.map(lambda x: format_rule(x) if isinstance(x, str) else x)
    return kb

def load_nlp_model(df: pd.DataFrame):
    nlp = spacy.load("es_core_news_sm")
    
    # Definir listas de provincias, cantones, procesos, sexo y horas
    provincias = set(df['Provincia'].str.lower().dropna().unique())
    cantones = set(df['Canton'].str.lower().dropna().unique())
    key_words = {"PELIGRO", "PELIGROSO", "PELIGROSA"}

    # Crear el Matcher para detectar entidades
    matcher = Matcher(nlp.vocab)

    def create_patterns_from_set(set, name):
        for item in set:
            pattern = [{"LOWER": token.lower()} for token in item.split()]
            matcher.add(name, [pattern])

    create_patterns_from_set(provincias, "PROVINCIA")
    create_patterns_from_set(cantones, "CANTON")
    create_patterns_from_set(key_words, "KEY_WORD")
    
    return {"nlp": nlp, "matcher": matcher, "provincias": provincias}

def __query_kb__(expr: str, engine: InferenceEngine):
    expr = format_rule(expr)
    query_result = engine.knowledgeBase.query(pl.Expr(expr))
    try:
        return {"query": pl.Expr(expr), "reply": query_result[0]["R"]}
    except:
        return {"query": pl.Expr(expr), "reply": query_result[0]}
    
def conceptual_nlp_query_processing(nlp_comps, query: str, engine: InferenceEngine):
    # Obtener entidades
    doc = nlp_comps["nlp"](query)
    matches = nlp_comps["matcher"](doc)

    response = {
        "matches": 0,
        "reply": None,
        "frames": []
    }
    
    # Calcular resultados
    if matches:

        res = {
            "entidades": {
                "name": "Entidades Detectadas",
                "headers": [],
                "cells": []
            },
            "queries": {
                "name": "Consultas Generadas",
                "headers": [],
                "cells": []
            },
            "results": {
                "name": "Respuestas Obtenidas",
                "headers": [],
                "cells": []
            }
        }

        for match_id, start, end in matches:
            match_name = nlp_comps["nlp"].vocab.strings[match_id]
            match_text = doc[start:end].text
            res["entidades"]["headers"].append(match_name)
            res["entidades"]["cells"].append(match_text)

        if "KEY_WORD" in res["entidades"]["headers"] and "CANTON" in res["entidades"]["headers"]:
            canton = res["entidades"]["cells"][res["entidades"]["headers"].index("CANTON")]
            if canton.lower() in nlp_comps["provincias"]:
                canton += "_cc"
            accion = "is_dangerous" # unico escenario por el momento, haría falta evaluarlo si se agregan mas
            res["queries"]["cells"].append(f"canton({format_str_for_rule(canton)})")
            res["queries"]["cells"].append(f"belongs_to({format_str_for_rule(canton)}, R)")
            res["queries"]["cells"].append(f"canton_incidence_level({format_str_for_rule(canton)}, R)")
            res["queries"]["cells"].append(f"{accion}({format_str_for_rule(canton)})")

        for query in res["queries"]["cells"]:
            res["results"]["cells"].append(__query_kb__(query, engine)["reply"])

        if len(res["results"]["cells"]) > 0:
            res_canton = canton.replace("_cc", "").title()
            is_cc = canton.lower() == "liberia" or canton.endswith("_cc")
            res_provincia = res["results"]["cells"][1].title().replace("_", " ")
            res_incidence = res["results"]["cells"][2].lower().replace("_", " ")
            res_dangerous = "seguro" if res["results"]["cells"][3] == "No" else "peligroso"

            response["reply"] = f"""
                {res_canton}, el cantón{" central" if is_cc else ""} de la provincia de {res_provincia}, 
                cuenta con incidencia de criminalidad {res_incidence} y por lo tanto se considera un lugar 
                {res_dangerous}.
            """
        
        response["frames"].append(pd.DataFrame(res["entidades"]["cells"], index=res["entidades"]["headers"], columns=[res["entidades"]["name"]]))
        response["frames"].append(pd.DataFrame(res["queries"]["cells"], columns=[res["queries"]["name"]]))
        response["frames"].append(pd.DataFrame(res["results"]["cells"], columns=[res["results"]["name"]]))
        response["matches"] = len(matches)

    return response
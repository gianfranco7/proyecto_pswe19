import os
import csv
import pytholog as pl
import pandas as pd
import inference_utils as iu
from inference import InferenceEngine 

# Usa la clase InferenceEngine como privada
__script_directory__ = os.path.dirname(os.path.abspath(__file__))

__geo_kb__ = "kb_files\geo.txt"
__crime_kb__ = "kb_files\crime.txt"

__incidencias_path__ = "datasets\incidencia.csv"

__ie__ = InferenceEngine()

__ie__.knowledgeBase.from_file(os.path.join(__script_directory__, __geo_kb__))
__ie__.knowledgeBase.from_file(os.path.join(__script_directory__, __crime_kb__))

__incidencia_df__ = iu.load_csv_as_dataframe(os.path.join(__script_directory__, __incidencias_path__))

#iu.df_column_to_facts(__incidencia_df__, "Incidencia", "incidence_level", __ie__)

def __asociate_canton_to_incidence_level__():
    #agregar el hecho para cada canton
    for i in range(__incidencia_df__.shape[0]):
        canton = (f"{__incidencia_df__.Canton[i]}").lower().replace(" ", "_")
        incidence_level = (f"{__incidencia_df__.Incidencia[i]}").lower().replace(" ", "_")
        __ie__.knowledgeBase([f"canton_incidence_level({canton}, {incidence_level})"])
        #print(f"canton_incidence_level({canton}, {incidence_level})")
    
    #agregar la regla para determinar peligrosidad de un canton
    #__ie__.knowledgeBase([f"is_dangerous(C, Truth) :- canton(C), canton_incidence_level(C, L) Truth is L == 'muy_alta' or L == 'alta'"])
    __ie__.knowledgeBase([f"is_dangerous(C) :- canton_incidence_level(C, L), dangerous_incidence_level(L)"])

__asociate_canton_to_incidence_level__()

#__ie__.print_kb_db()
#print(__ie__.knowledgeBase.query(pl.Expr("is_dangerous(escazu, R)")))

def __query_kb__(expr: str):
    query_result = __ie__.knowledgeBase.query(pl.Expr(expr))
    try:
        print(f"Q: {pl.Expr(expr)}. A: {query_result[0]["R"]}")
    except:
        print(f"Q: {pl.Expr(expr)}. A: {query_result[0]}")

                                                            #incidencia     esperado    antes   ahora
#__query_kb__("is_dangerous(montes_de_oca)")                 #muy alta       yes         yes     yes
#__query_kb__("is_dangerous(escazu)")                        #alta           yes         yes     yes
#__query_kb__("is_dangerous(belen)")                         #moderada       no          yes     no
#__query_kb__("is_dangerous(flores)")                        #baja           no          yes     no
#__query_kb__("is_dangerous(dota)")                          #muy baja       no          yes     no

#__query_kb__("canton_incidence_level(montes_de_oca, R)")    #ejemplo de un query que recupera información

def is_dangerous_place(place: str):
    p = place.lower().strip().replace(" ", "_")
    query_result = __ie__.query(f"is_dangerous({p})")
    return query_result[0] == "Yes"



print(is_dangerous_place("escazu"))
import os
import csv
import pytholog as pl
import pandas as pd
import inference_utils as iu
from inference import InferenceEngine 

# Usa la clase InferenceEngine como privada
__script_directory__ = os.path.dirname(os.path.abspath(__file__))

__geo_kb__ = "kb_files\geo.txt"

__incidencias_path__ = "datasets\incidencia.csv"

__ie__ = InferenceEngine()

__ie__.knowledgeBase.from_file(os.path.join(__script_directory__, __geo_kb__))

__incidencia_df__ = iu.load_csv_as_dataframe(os.path.join(__script_directory__, __incidencias_path__))

iu.df_column_to_facts(__incidencia_df__, "Incidencia", "incidence_level", __ie__)


def __asociate_canton_to_incidence_level__():
    #agregar el hecho para cada canton
    for i in range(__incidencia_df__.shape[0]):
        canton = (f"{__incidencia_df__.Canton[i]}").lower().replace(" ", "_")
        incidence_level = (f"{__incidencia_df__.Incidencia[i]}").lower().replace(" ", "_")
        __ie__.knowledgeBase([f"canton_incidence_level({canton}, {incidence_level})"])
    
    #agregar la regla para determinar peligrosidad de un canton
    __ie__.knowledgeBase([f"is_dangerous(C, Truth) :- canton(C), canton_incidence_level(C, L) Truth is L == 'muy_alto' or L == 'alto'"])


__asociate_canton_to_incidence_level__()

#__ie__.print_kb_db()
print(__ie__.knowledgeBase.query(pl.Expr("is_dangerous(escazu, R)")))

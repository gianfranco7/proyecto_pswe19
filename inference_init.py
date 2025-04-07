import os
import csv
import pytholog as pl
import pandas as pd
from inference import InferenceEngine 


# Usa la clase InferenceEngine como privada
__ie__ = InferenceEngine()

__script_directory__ = os.path.dirname(os.path.abspath(__file__))

__geo_kb__ = "kb_files\geo.txt"

__incidencias_path__ = "datasets\incidencia.csv"

# Creo que no sera necesaria esta funcion
# def load_kb_from_file(engine: InferenceEngine, path_to_file: str) -> InferenceEngine:
#     try:
#         engine.knowledgeBase.from_file(path_to_file)
#     except ValueError as e:
#         print(f"Error! load_csv: {e}")

def load_csv_as_dataframe(path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except ValueError as e:
        print(f"Error! load_csv: {e}")


__incidencia_df__ = load_csv_as_dataframe(os.path.join(__script_directory__, __incidencias_path__))


def df_column_to_facts(df: pd.DataFrame, column: str, fact_name: str, engine: InferenceEngine):
    try:
        unique_values = df[column].unique()
        fact_name = fact_name.lower().replace(" ", "_")
        for val in unique_values:
            val = val.lower().replace(" ", "_")
            engine.knowledgeBase([f"{fact_name}({val})"])
    except ValueError as e:
        print(f"Error! load_csv: {e}")



df_column_to_facts(__incidencia_df__, "Incidencia", "incidence_level", __ie__)

__ie__.knowledgeBase.from_file(os.path.join(__script_directory__, __geo_kb__))

    

#__ie__.print_kb_db()
#print(__ie__.knowledgeBase.query(pl.Expr("is_canton_of(escazu, san_jose)")))
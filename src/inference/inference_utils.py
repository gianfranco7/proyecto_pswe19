#inference_utils module

import pandas as pd
from .inference import InferenceEngine



def df_column_to_facts(df: pd.DataFrame, column: str, fact_name: str, engine: InferenceEngine):
    try:
        unique_values = df[column].unique()
        fact_name = fact_name.lower().replace(" ", "_")
        for val in unique_values:
            val = val.lower().replace(" ", "_")
            engine.knowledgeBase([f"{fact_name}({val})"])
            #print(f"{fact_name}({val})")
    except ValueError as e:
        print(f"Error! load_csv: {e}")



def load_csv_as_dataframe(path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except ValueError as e:
        print(f"Error! load_csv: {e}")



import datasets
import json
import pandas as pd
import geopandas as gpd
from pathlib import Path

# Limpia el nombre de un Canton y lo retorna en Mayuscula
def place_to_uppercase(canton:str):
    trans = str.maketrans("áéíóú", "aeiou")
    c = canton.translate(trans).upper()
    return c

def load_geo_json(filtpath):
    with open(filtpath, "r", encoding="utf-8") as f:    
        file = json.load(f)
    return file

#retorna el row del canton del dataset incidencia
def get_canton_incidence_statistics(canton: str):
    df = datasets.incidence
    c = place_to_uppercase(canton)
    column = df.loc[df['Canton'] == c]    
    return column.reset_index()

# retorna los rows para la procvincia dada del dataset incidencia
def get_province_incidence_statistics(province:str):
    df = datasets.incidence
    p = place_to_uppercase(province)
    province = (df[df["Canton"] ==  p]["Provincia"]).values[0]
    df = df[df["Provincia"] == province]
    return df

def get_incidence_df_with_geo_data(geojson_path: Path):    
    gdf = gpd.read_file(geojson_path)
    gdf.rename(columns={"NOM_PROV": "Provincia", "NOM_CANT_1":"Canton"}, inplace=True)
    gdf = gdf[["Canton", "geometry"]]

    df = datasets.incidence
    merged = pd.merge(df, gdf, on="Canton", how="left")
    #df["geometry"] = df.apply(lambda row: geo_dic.get(row['Canton'], 'None'), axis=1)
    return merged

import datasets

# Limpia el nombre de un Canton y lo retorna en Mayuscula
def place_to_uppercase(canton:str):
    trans = str.maketrans("áéíóú", "aeiou")
    c = canton.translate(trans).upper()
    return c

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


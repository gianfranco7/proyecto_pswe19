import datasets

# Limpia el nombre de un Canton y lo retorna en Mayuscula
def place_to_uppercase(canton:str):
    trans = str.maketrans("áéíóú", "aeiou")
    c = canton.translate(trans).upper()
    return c

def get_canton_incidence_statistics(canton: str):
    df = datasets.incidence
    c = place_to_uppercase(canton)
    column = df.loc[df['Canton'] == c]    
    return column.reset_index()

def get_province_incidence_statistics(province:str):
    df = datasets.incidence
    p = place_to_uppercase(province)
    province = (df[df["Canton"] ==  p]["Provincia"]).values[0]
    df = df[df["Provincia"] == province]
    return df


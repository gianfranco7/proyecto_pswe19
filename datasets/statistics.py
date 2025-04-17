import os
import pandas as pd

# ruta del script actual
BASE_DIR = os.path.dirname(__file__)

# cargar datos de los csv fomo Dataframes
incidence =  None
estadisticas = None
crime_types_by_zone = None
crime_type_by_victim_gender = None


incidence_path = os.path.join(BASE_DIR, "incidencia.csv")
estadisticas_path = os.path.join(BASE_DIR, "Estadisticas.csv")
crime_types_by_zone_path = os.path.join(BASE_DIR, "crime_types_by_zone.csv")
crime_type_by_victim_gender_path = os.path.join(BASE_DIR, "crime_type_by_victim_gender.csv")


if(os.path.exists(incidence_path)):
    incidence = pd.read_csv(incidence_path)

if(os.path.exists(estadisticas_path)):
    estadisticas = pd.read_csv(os.path.join(estadisticas_path))

if(os.path.exists(crime_types_by_zone_path)):
    crime_types_by_zone = pd.read_csv(os.path.join(crime_types_by_zone_path))

if(os.path.exists(crime_type_by_victim_gender_path)):
    crime_type_by_victim_gender = pd.read_csv(os.path.join(crime_type_by_victim_gender_path))


def load_csv(filename):
    file_path = os.path.join(BASE_DIR, filename)
    
    if os.path.exists(file_path):  # Verificar si el archivo existe
        return pd.read_csv(file_path)
    else:
        print(f"⚠️ Advertencia: El archivo '{filename}' no existe.")
        return None  # Retornar None si el archivo no está disponible

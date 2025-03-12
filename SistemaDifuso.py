import pandas as pd
import skfuzzy as fuzz
import numpy as np
import os
from skfuzzy import control as ctrl
from datetime import time
import matplotlib.pyplot as plt

# Obtener la ruta del archivo CSV
current_dir = os.getcwd()
filename = "Estadisticas.csv"
dataset_path = os.path.join(current_dir, filename)

# Cargar datos del CSV con manejo de errores
def cargar_datos(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv, on_bad_lines='skip', encoding='utf-8')
        return df
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return None

# Cargar los datos y validar
df = cargar_datos(dataset_path)
if df is None:
    exit()

# Filtrar filas donde el sexo no sea "HOMBRE" o "MUJER"
df = df[df['Sexo'].isin(['HOMBRE', 'MUJER'])]

# Parámetros de entrada
provincia_input = "SAN JOSE"
# canton_input = "SAN JOSE"
canton_input = "SANTA ANA"

hora_input = time(19, 0)  # Hora de entrada (19:00)
sexo_input = 0  # 0 = Hombre, 1 = Mujer

# Verificar que la hora esté en el rango válido
if not (0 <= hora_input.hour < 24):
    print(f"La hora '{hora_input.hour}' está fuera del rango válido (0-23).")
    exit()

# Verificar que el sexo sea válido
if sexo_input not in [0, 1]:
    print(f"El valor de sexo '{sexo_input}' no es válido. Debe ser 0 (hombre) o 1 (mujer).")
    exit()

# Función vectorizada para verificar si la hora está dentro de un rango
def hora_en_rango_vectorizada(df, hora_input):
    rango_horas = df['Hora'].str.split(' - ', expand=True)
    rango_horas = rango_horas.apply(lambda x: pd.to_datetime(x, format='%H:%M:%S').dt.time)
    return (rango_horas[0] <= hora_input) & (rango_horas[1] >= hora_input)

# Filtrar datos por criterios
df_filtrado = df[
    (df['Provincia'] == provincia_input) &
    (df['Canton'] == canton_input) &
    (df['Sexo'] == ('HOMBRE' if sexo_input == 0 else 'MUJER')) &
    hora_en_rango_vectorizada(df, hora_input)
]

# Verificar si el DataFrame filtrado está vacío
if df_filtrado.empty:
    print(f"No hay datos para la provincia '{provincia_input}', cantón '{canton_input}', sexo '{'HOMBRE' if sexo_input == 0 else 'MUJER'}' y hora '{hora_input}'.")
    exit()

# Obtener valores únicos de delitos
delitos_unicos = df_filtrado['Delito'].unique()

# Verificar si hay delitos registrados
if len(delitos_unicos) == 0:
    print("No hay delitos registrados para los parámetros de entrada.")
    exit()

# Crear variables difusas
hora = ctrl.Antecedent(np.arange(0, 24, 1), 'hora')
sexo = ctrl.Antecedent([0, 1], 'sexo')
delito_prob = ctrl.Consequent(np.arange(0, 101, 1), 'delito_prob')

# Definir funciones de membresía para hora
hora['dia'] = fuzz.trapmf(hora.universe, [6, 9, 18, 21])
hora['noche'] = np.fmax(fuzz.trapmf(hora.universe, [0, 0, 6, 9]), fuzz.trapmf(hora.universe, [18, 21, 23, 23]))

# Definir funciones de membresía para sexo
sexo['hombre'] = fuzz.trimf(sexo.universe, [0, 0, 1])
sexo['mujer'] = fuzz.trimf(sexo.universe, [0, 1, 1])

# Función para asignar probabilidades de delito
delito_prob['baja'] = fuzz.trimf(delito_prob.universe, [0, 0, 40])  # Ajustado
delito_prob['media'] = fuzz.trimf(delito_prob.universe, [30, 50, 70])  # Ajustado
delito_prob['alta'] = fuzz.trimf(delito_prob.universe, [60, 100, 100])  # Ajustado

# Calcular frecuencia relativa de delitos
frecuencia_delitos = df_filtrado['Delito'].value_counts(normalize=True)

def determinar_probabilidad(delito_condicion):
    if delito_condicion in frecuencia_delitos:
        if frecuencia_delitos[delito_condicion] > 0.5:
            return delito_prob['alta']
        elif frecuencia_delitos[delito_condicion] > 0.2:
            return delito_prob['media']
    return delito_prob['baja']

# Crear reglas difusas dinámicamente
todas_las_reglas = []
for d in delitos_unicos:
    probabilidad = determinar_probabilidad(d)
    regla = ctrl.Rule(
        hora['noche'] & sexo['hombre' if sexo_input == 0 else 'mujer'], probabilidad
    )
    todas_las_reglas.append(regla)

# Verificar si se crearon reglas difusas
if len(todas_las_reglas) == 0:
    print("No se pudieron crear reglas difusas. Verifica los datos de entrada.")
    exit()

# Crear sistema difuso
delito_ctrl = ctrl.ControlSystem(todas_las_reglas)
delito_sim = ctrl.ControlSystemSimulation(delito_ctrl)

# Asignar valores y computar resultado
delito_sim.input['hora'] = hora_input.hour
delito_sim.input['sexo'] = sexo_input

try:
    delito_sim.compute()
    probabilidad_predicha = delito_sim.output['delito_prob']
    print(f"Probabilidad de ser víctima de un delito en {provincia_input}, {canton_input} a las {hora_input}: {probabilidad_predicha:.2f}%")
except KeyError:
    print("No se pudo calcular la probabilidad. Verifica los datos de entrada y las reglas difusas.")

# Verificaciones adicionales
print("\n--- Verificaciones adicionales ---")

# Verificar datos filtrados
print("\nDatos filtrados:")
print(df_filtrado)

# Verificar delitos únicos
print("\nDelitos únicos en los datos filtrados:")
print(delitos_unicos)

# Verificar frecuencias de delitos
print("\nFrecuencia relativa de los delitos:")
print(frecuencia_delitos)

# Verificar reglas difusas
print("\nReglas difusas creadas:")
for i, regla in enumerate(todas_las_reglas):
    print(f"Regla {i + 1}: {regla}")

# Verificar valores de entrada
print(f"\nHora de entrada: {hora_input.hour}")
print(f"Sexo de entrada: {'Hombre' if sexo_input == 0 else 'Mujer'}")

print("\nValores de salida del sistema difuso:")
for key, value in delito_sim.output.items():
    print(f"{key}: {value}")

# Graficar funciones de membresía
print("\nGraficando funciones de membresía...")
hora.view()
plt.title("Función de membresía para 'hora'")
plt.show()

sexo.view()
plt.title("Función de membresía para 'sexo'")
plt.show()

delito_prob.view()
plt.title("Función de membresía para 'delito_prob'")
plt.show()
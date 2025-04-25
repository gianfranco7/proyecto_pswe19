import pandas as pd
import numpy as np
import os
from datetime import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Ruta del archivo
current_dir = os.getcwd()
filename = "Estadisticas.csv"
dataset_path = os.path.join(current_dir, filename)

# Cargar CSV
def cargar_datos(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv, on_bad_lines='skip', encoding='utf-8')
        return df
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        return None

df = cargar_datos(dataset_path)
if df is None:
    exit()


# ===========================
# Función principal del caso 2
# ===========================
def evaluar_vulnerabilidad(df, edad_input, sexo_input, provincia, canton):
    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]
    if df_zona.empty:
        print("No hay datos para la zona.")
        return None

    sexo_str = 'HOMBRE' if sexo_input == 0 else 'MUJER'
    delitos_totales = len(df)
    total_zona = len(df_zona)
    proporcion_zona = total_zona / delitos_totales if delitos_totales > 0 else 0
    proporcion_sexo = df_zona['Sexo'].value_counts(normalize=True).get(sexo_str, 0)

    # Variables difusas
    edad = ctrl.Antecedent(np.arange(0, 101, 1), 'edad')
    riesgo_sexo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'riesgo_sexo')
    zona_riesgo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'zona_riesgo')
    nivel = ctrl.Consequent(np.arange(0, 101, 1), 'nivel')

    # Edad
    edad['joven'] = fuzz.trimf(edad.universe, [0, 15, 30])
    edad['adulto'] = fuzz.trimf(edad.universe, [25, 40, 60])
    edad['adulto_mayor'] = fuzz.trimf(edad.universe, [55, 75, 100])

    # Riesgo sexo
    riesgo_sexo['bajo'] = fuzz.trimf(riesgo_sexo.universe, [0, 0, 0.3])
    riesgo_sexo['medio'] = fuzz.trimf(riesgo_sexo.universe, [0.2, 0.5, 0.7])
    riesgo_sexo['alto'] = fuzz.trimf(riesgo_sexo.universe, [0.6, 1, 1])

    # Zona
    zona_riesgo['baja'] = fuzz.trimf(zona_riesgo.universe, [0, 0, 0.3])
    zona_riesgo['media'] = fuzz.trimf(zona_riesgo.universe, [0.2, 0.5, 0.7])
    zona_riesgo['alta'] = fuzz.trimf(zona_riesgo.universe, [0.6, 1, 1])

    # Vulnerabilidad (salida)
    nivel['muy_baja'] = fuzz.trimf(nivel.universe, [0, 0, 20])
    nivel['baja'] = fuzz.trimf(nivel.universe, [10, 25, 40])
    nivel['media'] = fuzz.trimf(nivel.universe, [30, 50, 70])
    nivel['alta'] = fuzz.trimf(nivel.universe, [60, 75, 90])
    nivel['muy_alta'] = fuzz.trimf(nivel.universe, [80, 100, 100])

    # Reglas
    reglas = [
        ctrl.Rule(edad['joven'] & riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta']),
        ctrl.Rule(edad['joven'] & riesgo_sexo['medio'] & zona_riesgo['alta'], nivel['alta']),
        ctrl.Rule(edad['adulto'] & riesgo_sexo['medio'] & zona_riesgo['media'], nivel['media']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['alto'] & zona_riesgo['media'], nivel['alta']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta']),
        ctrl.Rule(edad['joven'] | edad['adulto'] | edad['adulto_mayor'], nivel['media']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['medio'] & zona_riesgo['baja'], nivel['baja']),
        ctrl.Rule(edad['adulto_mayor'] & riesgo_sexo['bajo'] & zona_riesgo['baja'], nivel['muy_baja']),
        ctrl.Rule(riesgo_sexo['bajo'] & zona_riesgo['baja'], nivel['muy_baja']),
        ctrl.Rule(riesgo_sexo['medio'] & zona_riesgo['media'], nivel['media']),
        ctrl.Rule(riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta'])

        # ctrl.Rule(True, nivel['media'])  # 🛟 Regla de respaldo
    ]

    sistema_ctrl = ctrl.ControlSystem(reglas)
    sim = ctrl.ControlSystemSimulation(sistema_ctrl)

    # Entradas
    sim.input['edad'] = edad_input
    sim.input['riesgo_sexo'] = proporcion_sexo
    sim.input['zona_riesgo'] = proporcion_zona

    try:
        sim.compute()

        if 'nivel' in sim.output:
            resultado = sim.output['nivel']
            print(f"📌 Nivel de vulnerabilidad para {sexo_str}, {edad_input} años en {provincia}, {canton}: {resultado:.2f}%")
            return resultado
        else:
            print("❌ No se pudo determinar el nivel de vulnerabilidad.")
            return None

    except Exception as e:
        print(f"❌ Error al calcular vulnerabilidad: {e}")
        return None

# ===========================
# EJEMPLO DE USO
# ===========================
provincia_input = "SAN JOSE"
canton_input = "SANTA ANA"
edad_input = 65
sexo_input = 1  # 0 = Hombre, 1 = Mujer

print(f"Caso 2")
evaluar_vulnerabilidad(df, edad_input, sexo_input, provincia_input, canton_input)
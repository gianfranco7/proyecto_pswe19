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

# Función vectorizada para verificar si la hora está dentro del rango
def hora_en_rango_vectorizada(df, hora_input):
    rango_horas = df['Hora'].str.split(' - ', expand=True)
    rango_horas = rango_horas.apply(lambda x: pd.to_datetime(x, format='%H:%M:%S').dt.time)
    return (rango_horas[0] <= hora_input) & (rango_horas[1] >= hora_input)

# ===========================
# Función principal del caso 1
# ===========================
def responder_probabilidad_delito_violento(df, provincia, canton, hora_input):
    # Paso 1: Filtrar delitos violentos
    df_filtrado = df[
        (df['Provincia'] == provincia) &
        (df['Canton'] == canton) &
        (df['Delito'].str.contains("VIOLENCIA|LESIONES|HOMICIDIO", case=False, na=False)) &
        hora_en_rango_vectorizada(df, hora_input)
    ]

    if df_filtrado.empty:
        print("No hay datos de delitos violentos para los criterios dados.")
        return None

    # Paso 2: Calcular frecuencia relativa
    total_delitos_canton = df[
        (df['Provincia'] == provincia) &
        (df['Canton'] == canton)
    ]
    frecuencia = len(df_filtrado) / len(total_delitos_canton) if len(total_delitos_canton) > 0 else 0

    # Paso 3: Variables difusas
    hora = ctrl.Antecedent(np.arange(0, 24, 1), 'hora')
    zona_riesgo = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'zona_riesgo')
    nivel_alerta = ctrl.Consequent(np.arange(0, 101, 1), 'nivel_alerta')

    # Hora difusa
    hora['madrugada'] = fuzz.trapmf(hora.universe, [0, 0, 4, 6])
    hora['mañana'] = fuzz.trapmf(hora.universe, [5, 7, 10, 12])
    hora['tarde'] = fuzz.trapmf(hora.universe, [12, 14, 17, 18])
    hora['noche'] = fuzz.trapmf(hora.universe, [18, 20, 23, 23])

    # Zona de riesgo
    zona_riesgo['baja'] = fuzz.trimf(zona_riesgo.universe, [0, 0, 0.3])
    zona_riesgo['media'] = fuzz.trimf(zona_riesgo.universe, [0.2, 0.5, 0.7])
    zona_riesgo['alta'] = fuzz.trimf(zona_riesgo.universe, [0.6, 1, 1])

    # Nivel de alerta
    nivel_alerta['bajo'] = fuzz.trimf(nivel_alerta.universe, [0, 0, 40])
    nivel_alerta['medio'] = fuzz.trimf(nivel_alerta.universe, [30, 50, 70])
    nivel_alerta['alto'] = fuzz.trimf(nivel_alerta.universe, [60, 100, 100])

    # Reglas
    reglas = [
        ctrl.Rule(hora['noche'] & zona_riesgo['alta'], nivel_alerta['alto']),
        ctrl.Rule(hora['madrugada'] & zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(hora['mañana'] & zona_riesgo['baja'], nivel_alerta['bajo']),
        ctrl.Rule(hora['tarde'] & zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(zona_riesgo['alta'], nivel_alerta['alto']),
        ctrl.Rule(zona_riesgo['media'], nivel_alerta['medio']),
        ctrl.Rule(zona_riesgo['baja'], nivel_alerta['bajo']),
    ]

    sistema_ctrl = ctrl.ControlSystem(reglas)
    sistema_sim = ctrl.ControlSystemSimulation(sistema_ctrl)

    # Entradas
    sistema_sim.input['hora'] = hora_input.hour
    sistema_sim.input['zona_riesgo'] = frecuencia

    try:
        sistema_sim.compute()
        resultado = sistema_sim.output['nivel_alerta']
        print(f"\n🛑 Nivel de alerta por delito violento en {provincia}, {canton} a las {hora_input}: {resultado:.2f}%")
        return resultado
    except Exception as e:
        print(f"Error en el sistema difuso: {e}")
        return None

# ===========================
# EJEMPLO DE USO
# ===========================
provincia_input = "SAN JOSE"
canton_input = "SANTA ANA"
hora_input = time(19, 0)  # 7:00 PM

responder_probabilidad_delito_violento(df, provincia_input, canton_input, hora_input)

# ===========================
# (Opcional) Visualizar funciones de membresía
# ===========================
# hora.view()
# zona_riesgo.view()
# nivel_alerta.view()
# plt.show()


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
        ctrl.Rule(riesgo_sexo['bajo'] & zona_riesgo['baja'], nivel['muy_baja']),
        ctrl.Rule(riesgo_sexo['medio'] & zona_riesgo['media'], nivel['media']),
        ctrl.Rule(riesgo_sexo['alto'] & zona_riesgo['alta'], nivel['muy_alta']),
    ]

    sistema_ctrl = ctrl.ControlSystem(reglas)
    sim = ctrl.ControlSystemSimulation(sistema_ctrl)

    # Entradas
    sim.input['edad'] = edad_input
    sim.input['riesgo_sexo'] = proporcion_sexo
    sim.input['zona_riesgo'] = proporcion_zona

    try:
        sim.compute()
        resultado = sim.output['nivel']
        print(f"📌 Nivel de vulnerabilidad para {sexo_str}, {edad_input} años en {provincia}, {canton}: {resultado:.2f}%")
        return resultado
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

evaluar_vulnerabilidad(df, edad_input, sexo_input, provincia_input, canton_input)


# ===========================
# Función principal del caso 3
# ===========================

# Función para extraer delitos probables según hora y zona
def delito_probable_por_hora_y_zona(df, provincia, canton, hora_input):
    # Paso 1: Filtrar por zona
    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]
    if df_zona.empty:
        print("No hay datos para esa zona.")
        return

    # Paso 2: Categorizar hora en bandas
    hora_num = hora_input.hour
    if 0 <= hora_num < 6:
        franja = 'madrugada'
    elif 6 <= hora_num < 12:
        franja = 'mañana'
    elif 12 <= hora_num < 18:
        franja = 'tarde'
    else:
        franja = 'noche'

    # Paso 3: Crear columna auxiliar para franja horaria
    def categorizar_hora(hora_str):
        try:
            h_inicio, h_fin = hora_str.split(" - ")
            h_inicio = pd.to_datetime(h_inicio).hour
            h_fin = pd.to_datetime(h_fin).hour
            if 0 <= hora_num < 6 and h_inicio < 6:
                return 'madrugada'
            elif 6 <= hora_num < 12 and 6 <= h_inicio < 12:
                return 'mañana'
            elif 12 <= hora_num < 18 and 12 <= h_inicio < 18:
                return 'tarde'
            elif 18 <= hora_num < 24 and 18 <= h_inicio <= 23:
                return 'noche'
        except:
            return 'otro'

    df_zona['Franja'] = df_zona['Hora'].apply(categorizar_hora)
    df_franja = df_zona[df_zona['Franja'] == franja]

    if df_franja.empty:
        print(f"No hay registros para {franja} en {provincia}, {canton}.")
        return

    # Paso 4: Calcular frecuencia relativa de delitos
    frecuencias = df_franja['Delito'].value_counts(normalize=True)
    print(f"📊 Delitos más probables en {provincia}, {canton} durante la {franja}:")

    for delito, freq in frecuencias.items():
        nivel = (
            "Alta" if freq > 0.5 else
            "Media" if freq > 0.2 else
            "Baja"
        )
        print(f"• {delito} → {nivel} probabilidad ({freq:.2%})")

    # Extra: mostrar el más probable
    delito_top = frecuencias.idxmax()
    print(f"\n🔎 Delito más probable: {delito_top} ({frecuencias.max():.2%})")

# --------------------------
# Ejemplo de uso
# --------------------------
provincia_input = "SAN JOSE"
canton_input = "SANTA ANA"
hora_input = time(19, 0)

delito_probable_por_hora_y_zona(df, provincia_input, canton_input, hora_input)

# ===========================
# Función principal del caso 4
# ===========================


# Convertir fecha a datetime
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
df = df.dropna(subset=['Fecha'])

# Categorizar hora como franja difusa
def obtener_franja_horaria(hora_obj):
    h = hora_obj.hour
    if 0 <= h < 6:
        return 'madrugada'
    elif 6 <= h < 12:
        return 'mañana'
    elif 12 <= h < 18:
        return 'tarde'
    else:
        return 'noche'

def categorizar_hora(hora_str, ref_hora):
    try:
        h_inicio, h_fin = hora_str.split(" - ")
        h_inicio = pd.to_datetime(h_inicio).hour
        h_fin = pd.to_datetime(h_fin).hour
        h = ref_hora.hour
        if h_inicio <= h <= h_fin:
            return obtener_franja_horaria(ref_hora)
    except:
        return None
        
# Función para detectar tendencia
def tendencia_delictiva(df, provincia, canton, hora_input):
    franja = obtener_franja_horaria(hora_input)

    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)].copy()
    if df_zona.empty:
        print("No hay datos en esa zona.")
        return

    df_zona['Franja'] = df_zona['Hora'].apply(lambda h: categorizar_hora(h, hora_input))
    df_franja = df_zona[df_zona['Franja'] == franja]
    if df_franja.empty:
        print("No hay registros para esa franja horaria.")
        return

    # Agrupar por mes
    df_franja['Mes'] = df_franja['Fecha'].dt.to_period('M')
    conteos_mensuales = df_franja.groupby('Mes').size().sort_index()

    if len(conteos_mensuales) < 3:
        print("No hay suficientes datos mensuales para analizar tendencia.")
        return

    # Calcular la pendiente (crecimiento)
    x = np.arange(len(conteos_mensuales))
    y = conteos_mensuales.values
    pendiente, _ = np.polyfit(x, y, 1)

    # Crear sistema difuso
    pendiente_input = ctrl.Antecedent(np.arange(-10, 11, 1), 'pendiente')
    alerta = ctrl.Consequent(np.arange(0, 101, 1), 'alerta')

    pendiente_input['estable'] = fuzz.trimf(pendiente_input.universe, [-1, 0, 1])
    pendiente_input['creciente'] = fuzz.trimf(pendiente_input.universe, [0, 3, 6])
    pendiente_input['acelerado'] = fuzz.trimf(pendiente_input.universe, [5, 10, 10])

    alerta['baja'] = fuzz.trimf(alerta.universe, [0, 0, 40])
    alerta['media'] = fuzz.trimf(alerta.universe, [30, 50, 70])
    alerta['alta'] = fuzz.trimf(alerta.universe, [60, 100, 100])

    reglas = [
        ctrl.Rule(pendiente_input['estable'], alerta['baja']),
        ctrl.Rule(pendiente_input['creciente'], alerta['media']),
        ctrl.Rule(pendiente_input['acelerado'], alerta['alta'])
    ]

    sistema = ctrl.ControlSystem(reglas)
    sim = ctrl.ControlSystemSimulation(sistema)

    sim.input['pendiente'] = pendiente
    sim.compute()

    resultado = sim.output['alerta']

    # Resultados
    print(f"\n📍 Zona: {provincia}, {canton}")
    print(f"🕓 Franja horaria: {franja} (hora: {hora_input})")
    print(f"📈 Pendiente mensual de delitos: {pendiente:.2f}")
    print(f"⚠️ Nivel de alerta por tendencia creciente: {resultado:.2f}%")

    # Graficar tendencia
    conteos_mensuales.plot(title="Tendencia mensual de delitos en franja horaria")
    plt.ylabel("Número de delitos")
    plt.xlabel("Mes")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --------------------------
# Ejemplo de uso
# --------------------------
provincia_input = "SAN JOSE"
canton_input = "SANTA ANA"
hora_input = time(20, 0)

tendencia_delictiva(df, provincia_input, canton_input, hora_input)

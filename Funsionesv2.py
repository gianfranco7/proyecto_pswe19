import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz

# ========================
# FUNCIONES DE APOYO
# ========================

def obtener_franja_horaria(hora):
    if pd.isnull(hora):
        return None
    hora = hora.hour
    if 0 <= hora < 6:
        return 'madrugada'
    elif 6 <= hora < 12:
        return 'mañana'
    elif 12 <= hora < 18:
        return 'tarde'
    else:
        return 'noche'

def clasificar_nivel_peligro(promedio):
    if promedio < 0.4:
        return "Bajo"
    elif promedio < 0.7:
        return "Medio"
    else:
        return "Alto"

# ========================
# CASO 1 – Conteo por tipo de delito
# ========================

def contar_delitos_por_tipo(df, provincia, canton):
    df_filtrado = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]
    conteo = df_filtrado['Tipo'].value_counts()
    print(f"\n--- CASO 1: Conteo de delitos en {provincia}, {canton} ---\n")
    print(conteo)

# ========================
# CASO 2 – Nivel de peligro usando lógica difusa
# ========================

def calcular_nivel_peligro(df, provincia, canton):
    df_filtrado = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)]

    if df_filtrado.empty:
        print("No hay datos para esta zona.")
        return

    # Variables difusas de entrada
    delitos = np.arange(0, 101, 1)
    gravedad = np.arange(0, 11, 1)

    # Variables difusas de salida
    peligro = np.arange(0, 1.1, 0.1)

    # Funciones de membresía
    delito_bajo = fuzz.trimf(delitos, [0, 0, 30])
    delito_medio = fuzz.trimf(delitos, [20, 50, 80])
    delito_alto = fuzz.trimf(delitos, [60, 100, 100])

    gravedad_leve = fuzz.trimf(gravedad, [0, 0, 3])
    gravedad_moderada = fuzz.trimf(gravedad, [2, 5, 8])
    gravedad_grave = fuzz.trimf(gravedad, [6, 10, 10])

    peligro_bajo = fuzz.trimf(peligro, [0, 0, 0.5])
    peligro_medio = fuzz.trimf(peligro, [0.3, 0.5, 0.7])
    peligro_alto = fuzz.trimf(peligro, [0.5, 1, 1])

    # Evaluar datos
    total_delitos = len(df_filtrado)
    gravedad_prom = df_filtrado['Gravedad'].mean() if 'Gravedad' in df_filtrado else 5  # Asume 5 si no hay columna

    delitos_level = fuzz.interp_membership(delitos, delito_bajo, total_delitos), \
                    fuzz.interp_membership(delitos, delito_medio, total_delitos), \
                    fuzz.interp_membership(delitos, delito_alto, total_delitos)

    gravedad_level = fuzz.interp_membership(gravedad, gravedad_leve, gravedad_prom), \
                     fuzz.interp_membership(gravedad, gravedad_moderada, gravedad_prom), \
                     fuzz.interp_membership(gravedad, gravedad_grave, gravedad_prom)

    # Inferencia difusa
    regla1 = np.fmin(delitos_level[2], gravedad_level[2])  # Alto y Grave → Peligro Alto
    regla2 = np.fmin(delitos_level[1], gravedad_level[1])  # Medio y Moderada → Medio
    regla3 = np.fmin(delitos_level[0], gravedad_level[0])  # Bajo y Leve → Bajo

    peligro0 = np.fmin(regla1, peligro_alto)
    peligro1 = np.fmin(regla2, peligro_medio)
    peligro2 = np.fmin(regla3, peligro_bajo)

    # Combinar y defuzzificar
    agregado = np.fmax(peligro0, np.fmax(peligro1, peligro2))
    resultado = fuzz.defuzz(peligro, agregado, 'centroid')

    print(f"\n--- CASO 2: Nivel de peligro en {provincia}, {canton} ---")
    print(f"Número de delitos: {total_delitos}")
    print(f"Gravedad promedio: {gravedad_prom:.2f}")
    print(f"Nivel de peligro (difuso): {resultado:.2f} → {clasificar_nivel_peligro(resultado)}")

# ========================
# CASO 3 – Visualización de delitos por hora
# ========================

def graficar_delitos_por_hora(df, provincia, canton):
    df_filtrado = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)].copy()

    if df_filtrado.empty:
        print("No hay datos para la zona seleccionada.")
        return

    df_filtrado['Hora'] = pd.to_datetime(df_filtrado['Hora'], format='%H:%M:%S', errors='coerce')
    df_filtrado['Hora_num'] = df_filtrado['Hora'].dt.hour

    conteo_horas = df_filtrado['Hora_num'].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    conteo_horas.plot(kind='bar', color='orange', edgecolor='black')
    plt.title(f'Distribución de delitos por hora en {provincia}, {canton}')
    plt.xlabel('Hora del día')
    plt.ylabel('Número de delitos')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

# ========================
# CASO 4 – Delitos por franja horaria
# ========================

def visualizar_delitos_por_franja(df, provincia, canton):
    df_zona = df[(df['Provincia'] == provincia) & (df['Canton'] == canton)].copy()

    if df_zona.empty:
        print("No hay datos para la zona seleccionada.")
        return

    df_zona['Hora'] = pd.to_datetime(df_zona['Hora'], format='%H:%M:%S', errors='coerce')
    df_zona['Franja'] = df_zona['Hora'].apply(lambda h: obtener_franja_horaria(h) if pd.notna(h) else None)
    franja_counts = df_zona['Franja'].value_counts().reindex(['madrugada', 'mañana', 'tarde', 'noche'], fill_value=0)

    plt.figure(figsize=(8, 5))
    franja_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f'Distribución de delitos por franja horaria en {provincia}, {canton}')
    plt.xlabel('Franja Horaria')
    plt.ylabel('Número de delitos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

# ========================
# MAIN
# ========================

if __name__ == "__main__":
    # Cargar tus datos
    try:
        df = pd.read_csv('Estadisticas.csv')  # Reemplaza con la ruta correcta
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        df = None

    if df is not None:
        provincia_input = "SAN JOSE"
        canton_input = "SANTA ANA"
        # provincia_input = input("Ingrese la provincia: ")
        # canton_input = input("Ingrese el cantón: ")

        print("\n=== CASO 1 ===")
        contar_delitos_por_tipo(df, provincia_input, canton_input)

        print("\n=== CASO 2 ===")
        calcular_nivel_peligro(df, provincia_input, canton_input)

        print("\n=== CASO 3 ===")
        graficar_delitos_por_hora(df, provincia_input, canton_input)

        print("\n=== CASO 4 ===")
        visualizar_delitos_por_franja(df, provincia_input, canton_input)

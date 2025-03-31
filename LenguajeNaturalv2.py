import spacy
from spacy.tokens import Span
from spacy.language import Language
from spacy.matcher import Matcher
import re

# Cargar el modelo en español
nlp = spacy.load("es_core_news_sm")

# Definir listas de provincias, cantones, procesos, sexo y horas
provincias = {"Alajuela", "San José", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"}
cantones = {"San Carlos", "Grecia", "Atenas", "Poás", "Orotina", "Alajuela"}
procesos = {"Suma", "Resta", "Conteo"}
sexo = {"Mujer", "Hombre"}
genero_relacionado = {"niña": "Mujer", "niño": "Hombre", "abuela": "Mujer", "abuelo": "Hombre"}

# Mapeo de palabras clave a horas específicas
mapeo_horas = {
    "madrugada": "04:00",
    "mañana": "09:00",
    "tarde": "16:00",
    "noche": "21:00"
}

# Requisitos para cada proceso
requisitos_procesos = {
    "Suma": ["PROVINCIA", "CANTON"],
    "Resta": ["PROVINCIA", "CANTON", "HORA"],
    "Conteo": ["PROVINCIA", "CANTON", "SEXO"]
}

# Crear el Matcher para detectar entidades
matcher = Matcher(nlp.vocab)

# Agregar patrones de provincia y canton al matcher
for nombre in provincias.union(cantones):
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("PROVINCIA_CANTON", [pattern])

# Agregar patrones de procesos
for nombre in procesos:
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("PROCESO", [pattern])

# Agregar patrones de sexo
for nombre in sexo.union(genero_relacionado):
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("SEXO", [pattern])

# Agregar patrón para detectar horas (formato de 24 horas)
pattern_hora = [{"TEXT": {"regex": r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b"}}]
matcher.add("HORA", [pattern_hora])

# Agregar patrón para las palabras que representan las horas del día
pattern_palabra_hora = [{"LOWER": {"in": list(mapeo_horas.keys())}}]
matcher.add("PALABRA_HORA", [pattern_palabra_hora])

@Language.component("detectar_entidades_personalizadas")
def detectar_entidades_personalizadas(doc):
    matches = matcher(doc)
    nuevas_entidades = []
    ya_detectado_provincias = set()

    # Asignar entidades con lógica para distinguir entre PROVINCIA, CANTON, PROCESO, SEXO, HORA
    for match_id, start, end in matches:
        text = doc[start:end].text

        # Asignar provincia o canton
        if text in provincias:
            if text not in ya_detectado_provincias:
                nuevas_entidades.append(Span(doc, start, end, label="PROVINCIA"))
                ya_detectado_provincias.add(text)
            else:
                nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
        elif text in cantones:
            nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
        
        # Asignar procesos
        elif text in procesos:
            nuevas_entidades.append(Span(doc, start, end, label="PROCESO"))
        
        # Asignar sexo
        elif text in sexo:
            nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
        elif text.lower() in genero_relacionado:
            nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
        
        # Asignar hora en formato 24 horas
        elif re.match(r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b", text):
            nuevas_entidades.append(Span(doc, start, end, label="HORA"))
        
        # Asignar las palabras clave de hora
        elif text.lower() in mapeo_horas:
            nuevas_entidades.append(Span(doc, start, end, label="HORA"))
        
        else:
            nuevas_entidades.append(doc[start:end])

    doc.set_ents(nuevas_entidades)
    return doc

# Asegurar que no se agregue dos veces el componente
if "detectar_entidades_personalizadas" not in nlp.pipe_names:
    nlp.add_pipe("detectar_entidades_personalizadas", after="ner")

def mostrar_menu():
    print("\n" + "="*50)
    print("Esta es una aplicación para el cálculo de crímenes a nivel país.")
    print("Estas son las opciones disponibles:")
    for i, proceso in enumerate(procesos, 1):
        print(f"{i}. {proceso}")
    print(f"{len(procesos)+1}. Salir")
    print("="*50)

def obtener_entidades(texto):
    doc = nlp(texto)
    entidades = {}
    for ent in doc.ents:
        if ent.label_ not in entidades:
            entidades[ent.label_] = []
        entidades[ent.label_].append(ent.text)
    return entidades

def verificar_requisitos(proceso, entidades):
    requisitos = requisitos_procesos.get(proceso, [])
    faltantes = [req for req in requisitos if req not in entidades]
    
    if faltantes:
        print(f"\nFaltan los siguientes datos para el proceso {proceso}:")
        for req in faltantes:
            print(f"- {req}")
        return False
    return True

def procesar_opcion(opcion):
    proceso = list(procesos)[opcion-1]
    print(f"\nHas seleccionado el proceso: {proceso}")
    print(f"Por favor, ingresa la información requerida (Provincia, Cantón, etc.)")
    
    while True:
        texto = input("Ingresa tu texto (o 'menu' para volver al menú): ").strip()
        
        if texto.lower() == 'menu':
            return False
        
        entidades = obtener_entidades(texto)
        print("\nEntidades detectadas:")
        for tipo, valores in entidades.items():
            print(f"{tipo}: {', '.join(valores)}")
        
        if verificar_requisitos(proceso, entidades):
            print("\n¡Todos los requisitos cumplidos! Procesando...")
            # Aquí iría la lógica específica del proceso
            print(f"Proceso {proceso} completado con éxito.")
            return True
        else:
            respuesta = input("\n¿Deseas intentarlo nuevamente? (s/n): ").lower()
            if respuesta != 's':
                return False

def main():
    while True:
        mostrar_menu()
        try:
            opcion = int(input("\nSelecciona una opción: "))
            
            if 1 <= opcion <= len(procesos):
                if not procesar_opcion(opcion):
                    continue
            elif opcion == len(procesos)+1:
                print("\n¡Gracias por usar la aplicación! Hasta luego.")
                break
            else:
                print("\nOpción no válida. Por favor, intenta nuevamente.")
        except ValueError:
            print("\nPor favor, ingresa un número válido.")

if __name__ == "__main__":
    main()
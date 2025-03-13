import spacy
from spacy.tokens import Span
from spacy.language import Language
from spacy.matcher import Matcher
import re

# Cargar el modelo en español
nlp = spacy.load("es_core_news_sm")

# Definir listas de provincias, cantones, procesos, sexo y horas
provincias = {"Alajuela", "San José", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"}
cantones = {"San Carlos", "Grecia", "Atenas", "Poás", "Orotina", "Alajuela"}  # Alajuela también es cantón por lo cual la repetimos en caso que el usuario vuelva a repetirlo
procesos = {"Suma", "Resta", "Conteo"} # Actualmente colocamos estos nombre ya que serian un ejemplo de guia para los futuros proceso que el sistema ahora como lo puede ser el total insidentes etc
sexo = {"Mujer", "Hombre"}
genero_relacionado = {"niña": "Mujer", "niño": "Hombre", "abuela": "Mujer", "abuelo": "Hombre"}

# Mapeo de palabras clave a horas específicas
mapeo_horas = {
    "madrugada": "04:00",
    "mañana": "09:00",
    "tarde": "16:00",
    "noche": "21:00"
}

# Crear el Matcher para detectar entidades
matcher = Matcher(nlp.vocab)

# Agregar patrones de provincia y canton al matcher
for nombre in provincias.union(cantones):  # Unir ambas listas correctamente usando union()
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("PROVINCIA_CANTON", [pattern])

# Agregar patrones de procesos
for nombre in procesos:
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("PROCESO", [pattern])

# Agregar patrones de sexo
for nombre in sexo.union(genero_relacionado):  # Unir listas de sexo y género relacionado
    pattern = [{"LOWER": token.lower()} for token in nombre.split()]
    matcher.add("SEXO", [pattern])

# Agregar patrón para detectar horas (formato de 24 horas) el formato que puede colocar el usuario podria ser asi ejemplo: 08:00
pattern_hora = [{"TEXT": {"regex": r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b"}}]
matcher.add("HORA", [pattern_hora])

# Agregar patrón para las palabras que representan las horas del día
pattern_palabra_hora = [{"LOWER": {"in": list(mapeo_horas.keys())}}]  # Las palabras mapeadas: Madrugada, Mañana, Tarde, Noche
matcher.add("PALABRA_HORA", [pattern_palabra_hora])

# Esta es una de las fases mas importante para separar las palabras a que entidades le recorresponde, con ello en un futuro ser utilizado para 
@Language.component("detectar_entidades_personalizadas")
def detectar_entidades_personalizadas(doc):
    matches = matcher(doc)
    nuevas_entidades = []
    ya_detectado_provincias = set()  # Usamos un conjunto para llevar un registro de las provincias detectadas

    print(f"\nTexto procesado: {doc.text}")  # Ver el texto de entrada
    print("Matches encontrados:", [(doc[start:end].text, start, end) for _, start, end in matches])

    # Asignar entidades con lógica para distinguir entre PROVINCIA, CANTON, PROCESO, SEXO, HORA
    for match_id, start, end in matches:
        text = doc[start:end].text

        # Asignar provincia o canton
        if text in provincias:
            if text not in ya_detectado_provincias:  # Si no se ha detectado previamente como provincia
                print(f"Modificando entidad: {text} -> PROVINCIA")
                nuevas_entidades.append(Span(doc, start, end, label="PROVINCIA"))
                ya_detectado_provincias.add(text)  # Marcar como detectada
            else:
                print(f"Modificando entidad: {text} -> CANTON")
                nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
        elif text in cantones:
            print(f"Modificando entidad: {text} -> CANTON")
            nuevas_entidades.append(Span(doc, start, end, label="CANTON"))
        
        # Asignar procesos
        elif text in procesos:
            print(f"Modificando entidad: {text} -> PROCESO")
            nuevas_entidades.append(Span(doc, start, end, label="PROCESO"))
        
        # Asignar sexo
        elif text in sexo:
            print(f"Modificando entidad: {text} -> SEXO")
            nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
        elif text.lower() in genero_relacionado:
            print(f"Modificando entidad: {text} -> {genero_relacionado[text.lower()]}")
            nuevas_entidades.append(Span(doc, start, end, label="SEXO"))
        
        # Asignar hora en formato 24 horas
        elif re.match(r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b", text):
            print(f"Modificando entidad: {text} -> HORA")
            nuevas_entidades.append(Span(doc, start, end, label="HORA"))
        
        # Asignar las palabras clave de hora (Madrugada, Mañana, Tarde, Noche)
        elif text.lower() in mapeo_horas:
            hora_equivalente = mapeo_horas[text.lower()]
            print(f"Modificando entidad: {text} -> HORA ({hora_equivalente})")
            # Crear un Span para la hora sin modificar el texto
            nuevas_entidades.append(Span(doc, start, end, label="HORA"))
        
        else:
            nuevas_entidades.append(doc[start:end])  # Mantener las demás entidades

    # Aplicar las nuevas entidades al doc de manera controlada
    doc.set_ents(nuevas_entidades)
    return doc

# Asegurar que no se agregue dos veces el componente
if "detectar_entidades_personalizadas" not in nlp.pipe_names:
    nlp.add_pipe("detectar_entidades_personalizadas", after="ner")

# Texto de prueba
texto = "La niña fue a la tienda a las 14:00 y su abuelo le dijo que su proceso de Resta estaba listo. Ella va a dormir a la madrugada."

# Procesar el texto
doc = nlp(texto)

# Mostrar entidades reconocidas
print("\nEntidades reconocidas:")
for ent in doc.ents:
    print(f"Texto: {ent.text}, Etiqueta: {ent.label_}")

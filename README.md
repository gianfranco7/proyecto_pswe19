# proyecto_pswe19
Repositorio para el proyecto del curso Sistemas Basados en el Conocimiento PSWE-19 - UCENFOTEC - 2025 Primer Cuatrimestre




Python 3.12 o mayor no cuenta con el modulo imp utilizado en PyKE

[instalar python 3.11 (kernel)](https://www.youtube.com/watch?v=IHSxLOCEiNE&t=1s) 
py -3.11 -m pip install scitools-pyke

# Guía de Usuario  

En este proyecto, seguimos un desarrollo por fases para garantizar una implementación eficiente.  

## 1. Limpieza de Datos  
La primera fase se centró en la limpieza de los datos proporcionados por el OIJ, los cuales contenían información errónea o irrelevante. Para ello, aplicamos un análisis exploratorio de datos (**EDA**), cuyos resultados puedes consultar en el archivo [`EDA.ipynb`](EDA.ipynb).  

## 2. Determinación de Incidencias  
Tras la limpieza, procesamos los datos para determinar las incidencias de manera más estructurada. Este proceso optimiza la información para su uso futuro en la definición de reglas difusas. Los resultados se encuentran en [`incidencia.csv`](incidencia.csv).  

## 3. Procesamiento de Lenguaje Natural  
Luego, trabajamos en la comprensión del lenguaje natural para que pueda ser utilizado dentro del proyecto. Este desarrollo se encuentra en [`LenguajeNatural.py`](LenguajeNatural.py).  

> **Nota:** Este archivo incluye datos precargados para facilitar las pruebas.  

## 4. Implementación del Motor de Inferencia  
Actualmente, el motor de inferencia se basa en un archivo CSV por razones de practicidad, aunque posteriormente se integrará con la base de datos. Durante esta fase, exploramos la creación de reglas para comprender mejor el funcionamiento de la biblioteca de sistemas difusos.  

Toda la implementación se documenta en [`SistemaDifuso.py`](SistemaDifuso.py), donde se detalla su funcionamiento paso a paso.  

## Ejecución de Archivos  
Para ejecutar los archivos `.py`, se recomienda utilizar un entorno como **Visual Studio Code**. Abre la terminal y usa el siguiente comando:  

```bash
python nombre_del_archivo.py

# proyecto_pswe19
Repositorio para el proyecto del curso Sistemas Basados en el Conocimiento PSWE-19 - UCENFOTEC - 2025 Primer Cuatrimestre




Python 3.8.10 o superior 


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


# Guía para la Instalación de Visual Studio Code y Librerias de Python

## 1. Instalación de Visual Studio Code

### Paso 1: Descargar Visual Studio Code
1. Dirígete a la página oficial de Visual Studio Code: [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Haz clic en el botón de descarga correspondiente a tu sistema operativo (Windows, macOS o Linux).

### Paso 2: Instalación
1. Una vez descargado el instalador, ejecútalo.
2. Sigue las instrucciones de instalación en pantalla (asegúrate de seleccionar la opción para agregar Visual Studio Code al PATH).
3. Después de la instalación, abre Visual Studio Code.

## 2. Instalación de Python

### Paso 1: Descargar Python
1. Visita la página oficial de Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Descarga la versión más reciente compatible con tu sistema operativo.

### Paso 2: Instalación de Python
1. Ejecuta el instalador de Python.
2. **Importante:** Asegúrate de marcar la casilla que dice **"Add Python to PATH"** durante la instalación.
3. Sigue las instrucciones para completar la instalación.

### Paso 3: Verificar instalación de Python
1. Abre la terminal o el símbolo del sistema (cmd).
2. Escribe el siguiente comando para verificar la instalación de Python:

```bash
   python --version
```

Deberías ver algo similar a Python 3.x.x.

### Paso 4: Instalación de pip (Administrador de paquetes)
Si **pip** no está instalado, puedes seguir los siguientes pasos:

Verificar si pip está instalado: Abre la terminal y ejecuta el siguiente comando:

```bash
pip --version
```

Si ves un error o el comando no es reconocido, significa que pip no está instalado.

**Instalar pip**: Si no tienes pip, puedes instalarlo descargando el script **get-pip.py**. Sigue estos pasos:

Abre la terminal y descarga el archivo get-pip.py utilizando curl o wget:

Si tienes curl instalado:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```

Si tienes wget instalado:

```bash
wget https://bootstrap.pypa.io/get-pip.py
```
Instalar pip: Una vez que hayas descargado get-pip.py, ejecuta el siguiente comando para instalar pip:

```bash
python get-pip.py
```
Verificar la instalación de pip: Después de instalar pip, puedes verificar que está correctamente instalado ejecutando:

```bash
pip --version
```
Esto debería mostrar la versión de pip instalada.

### Paso 5. Instalación de Bibliotecas en Python
#### Paso 1: Crear un Entorno Virtual (opcional pero recomendado)
1. Abre Visual Studio Code y abre la terminal integrada (usa Ctrl + ).

2. Navega a la carpeta donde deseas trabajar en tu proyecto.

3. Crea un entorno virtual con el siguiente comando:

```bash
python -m venv venv
```
Activa el entorno virtual:

En Windows:

```bash
.\venv\Scripts\activate
```

En macOS/Linux:

```bash
source venv/bin/activate
```

Deberías ver el nombre de tu entorno virtual precediendo la línea de comandos (por ejemplo, (venv)).

### Paso 6: Instalar las Bibliotecas Necesarias
Con el entorno virtual activado, puedes proceder a instalar las bibliotecas necesarias. Ejecuta los siguientes comandos en la terminal para instalar las dependencias:

```bash
pip install spacy pandas scikit-fuzzy numpy matplotlib scipy
```

### Paso 7: Descargar el Modelo de spaCy
Si necesitas usar un modelo de lenguaje de spaCy, como uno para el idioma español, puedes descargarlo con el siguiente comando:

```bash
python -m spacy download es_core_news_sm
```
Este comando descargará e instalará el modelo de lenguaje en español. Si necesitas otro idioma, puedes buscar el modelo adecuado en la documentación de spaCy.

### Paso 8 Configuración de Visual Studio Code para Python
#### Paso 1: Instalar la Extensión de Python en Visual Studio Code
1. Abre Visual Studio Code.
2. Ve a la sección de Extensiones (puedes abrirla con Ctrl + Shift + X).
3. Busca "Python" e instala la extensión oficial de Microsoft llamada Python.
#### Paso 2: Seleccionar el Intérprete de Python
1. En la parte inferior izquierda de Visual Studio Code, haz clic en el nombre del intérprete de Python.
2. Selecciona el intérprete del entorno virtual que creaste anteriormente (debería estar listado como **.\venv\Scripts\python.exe** en Windows o **./venv/bin/python** en macOS/Linux).
#### Paso 3: Verificación
1. Abre un archivo Python o crea uno nuevo.
2. Escribe un código de prueba como este para asegurarte de que las bibliotecas están funcionando correctamente:
```bash
import spacy
import pandas as pd
import skfuzzy as fuzz
import numpy as np
import matplotlib.pyplot as plt

print("¡Bibliotecas instaladas correctamente!")
```

### Ejecución de Archivos  
Para ejecutar los archivos `.py`, se recomienda utilizar un entorno como **Visual Studio Code**. Abre la terminal y usa el siguiente comando:  

```bash
python nombre_del_archivo.py
```
### Archivos .ipynb

Para abrir y ejecutar los notebooks de Jupyter, asegúrate de tener Jupyter Notebook o JupyterLab instalados. Si no los tienes, instálalos con:

```bash
pip install notebook jupyterlab
```

Una vez instalado, para abrir el notebook, usa uno de los siguientes comandos en la terminal:

```bash
jupyter notebook nombre_del_archivo.ipynb
```
o
```bash
jupyter lab nombre_del_archivo.ipynb
```

Esto abrirá la interfaz web de Jupyter, donde podrás visualizar y ejecutar cada celda del notebook.

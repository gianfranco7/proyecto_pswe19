
from .crime_form import CRIME_FORM
import datasets 

DEMO_FORMS = {
    **CRIME_FORM
}

DATASETS = {
    "Incidencia": datasets.incidence,
    "Tipos por Zona": datasets.crime_types_by_zone,
    "Tipos por Genero": datasets.crime_type_by_victim_gender,
    "Estadisticas": datasets.estadisticas
}
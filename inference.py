

import os
import csv
import pytholog as pl
import pandas as pd


script_directory = os.path.dirname(os.path.abspath(__file__))

filename = "kb_files/geo.txt"

dataset_path = os.path.join(script_directory, filename)

ex = pl.KnowledgeBase("geo")

ex.from_file(dataset_path)

print(ex.query(pl.Expr("is_canton_of(X, san_jose)")))


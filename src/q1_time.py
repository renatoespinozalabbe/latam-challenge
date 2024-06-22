from typing import List, Tuple
from datetime import datetime
import os
import pandas as pd


def q1_time(file_path: str) -> List[Tuple[datetime.date, str]]:

    # Ruta a archivo de credenciales JSON de Google Cloud
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../credentials/project-latam-challenge-749ce1a96052.json"

    # Leer el archivo CSV en un DataFrame
    df = pd.read_json(file_path,lines=True)

    pass
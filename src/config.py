# config.py
# Configuración de la base de datos y parámetros generales

import urllib.parse

class Config:
    # URI de conexión: mysql+mysqlconnector://usuario:contraseña@host/base_de_datos
    db_user = 'root'  # Usuario de la base de datos
    db_password = urllib.parse.quote_plus('23052006Cc!')  # Contraseña codificada de la base de datos 
    db_host = 'localhost'  # Host de la base de datos
    db_name = 'api_flask'  # Nombre de la base de datos
    
    # Configuración de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'lxQqHFl6Kku0KlgKAK1M0u7AY0Cz5KhGi3dWb1ErFfHZVO6KZDJ5sIyfP3tdAA1y97Wvq86qQ8at1NYN5jG7RQ'  # Llave segura. Usado luego para firmar JWT

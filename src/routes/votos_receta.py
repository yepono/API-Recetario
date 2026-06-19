# routes/votos_receta.py
# Contiene todas las rutas (endpoints) para manejar votos_receta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import VotoReceta                          # Modelo de la tabla votos_receta
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para votos_receta
votos_receta_bp = Blueprint('votos_bp', __name__)

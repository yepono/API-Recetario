# routes/comentarios.py
# Contiene todas las rutas (endpoints) para manejar comentarios
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import Usuario,Ingrediente,Imagen_Receta,Unidad,Ingrediente_Receta,Comentario,Receta
from models import VotoReceta                      # Modelo de la tabla comentario
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para comentarios
comentarios_bp = Blueprint('comentarios_bp', __name__)


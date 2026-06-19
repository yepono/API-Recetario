# routes/unidades.py
# Contiene todas las rutas (endpoints) para manejar unidades
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import Unidad                           # Modelo de la tabla unidades
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para recetas
unidades_bp = Blueprint('unidades_bp', __name__)

# ...existing code...

@unidades_bp.route('/', methods=['GET'])
@token_requerido
def ver_unidades(usuario_actual):
    try:
        unidades = Unidad.query.filter_by(activo=True).all()
        resultado = [u.to_dict() for u in unidades]
        return jsonify({"unidades": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener las unidades"}), 400

@unidades_bp.route('/', methods=['POST'])
@token_requerido
def agregar_unidad(usuario_actual):
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return jsonify({"mensaje": "El nombre es requerido"}), 400

        # Validar que no exista ya la unidad
        existente = Unidad.query.filter_by(nombre=nombre).first()
        if existente:
            return jsonify({"mensaje": "La unidad ya existe."}), 400

        nueva = Unidad(nombre=nombre, activo=True)
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Unidad agregada correctamente", "unidad": nueva.to_dict()}), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al agregar la unidad"}), 400
    

    try:
        from models import Unidad
        data = request.get_json()
        nuevo_nombre = data.get('nombre', '').strip()

        # Validar nombre: solo letras y guion medio, sin espacios, números ni caracteres especiales
        import re
        if not re.match(r'^[A-Za-z\-]+$', nuevo_nombre):
            return jsonify({"mensaje": "El nombre solo puede contener letras y guion medio (-), sin espacios, números ni caracteres especiales."}), 400

        # Buscar la relación ingrediente_receta
        from models import Ingrediente_Receta
        relacion = Ingrediente_Receta.query.get(id_relacion)
        if not relacion:
            return jsonify({"mensaje": "Relación ingrediente-receta no encontrada"}), 404

        # Buscar si la unidad ya existe
        unidad = Unidad.query.filter_by(nombre=nuevo_nombre).first()
        if not unidad:
            # Si no existe, la crea
            unidad = Unidad(nombre=nuevo_nombre, activo=True)
            db.session.add(unidad)
            db.session.commit()  # Guardar para obtener el id

        # Cambiar el unidad_id en la relación
        relacion.unidad_id = unidad.id
        db.session.commit()
        return jsonify({"mensaje": "Unidad de la receta modificada correctamente", "unidad_id": unidad.id, "nombre": unidad.nombre})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la unidad de la receta"}), 400
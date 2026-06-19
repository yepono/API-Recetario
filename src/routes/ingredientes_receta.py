# routes/ingredientes_receta.py
# Contiene todas las rutas (endpoints) para manejar ingredientes_receta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import Ingrediente_Receta                           # Modelo de la tabla ingredientes_receta
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para ingredientes_receta
ingredientes_receta_bp = Blueprint('ingredientes_receta_bp', __name__)

@ingredientes_receta_bp.route('/', methods=['GET'])
@token_requerido
def ver_ingredientes(usuario_actual):
    try:
        ingredientes = db.session.query(Ingrediente_Receta.ingrediente_id).distinct().all()
        # Si tienes el modelo Ingrediente importado, puedes mostrar el nombre:
        from models import Ingrediente
        lista = []
        for ing_id_tuple in ingredientes:
            ing = Ingrediente.query.get(ing_id_tuple[0])
            if ing:
                lista.append({"id": ing.id, "nombre": ing.nombre})
        return jsonify({"ingredientes": lista})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener la lista de ingredientes"}), 400
    
@ingredientes_receta_bp.route('/', methods=['POST'])
@token_requerido
def agregar_ingrediente(usuario_actual):
    try:
        from models import Ingrediente
        data = request.get_json()
        nombre = data.get('nombre', '').strip()

        # Validar nombre: solo letras y guion medio, sin espacios, sin números ni caracteres especiales
        import re
        if not re.match(r'^[A-Za-z\-]+$', nombre):
            return jsonify({"mensaje": "El nombre solo puede contener letras y guion medio (-), sin espacios, números ni caracteres especiales."}), 400

        # Verificar si ya existe
        existente = Ingrediente.query.filter_by(nombre=nombre).first()
        if existente:
            return jsonify({"mensaje": "El ingrediente ya existe."}), 400

        nuevo = Ingrediente(nombre=nombre)
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Ingrediente agregado correctamente", "ingrediente": {"id": nuevo.id, "nombre": nuevo.nombre}}), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al agregar el ingrediente"}), 400
    

@ingredientes_receta_bp.route('/recetas-por-ingrediente/<int:id_ingrediente>', methods=['GET'])
@token_requerido
def recetas_por_ingrediente(usuario_actual, id_ingrediente):
    try:
        from models import Receta
        # Buscar todas las relaciones donde el ingrediente_id coincida
        relaciones = Ingrediente_Receta.query.filter_by(ingrediente_id=id_ingrediente).all()
        receta_ids = [rel.receta_id for rel in relaciones]
        # Obtener las recetas activas con esos IDs
        recetas = Receta.query.filter(Receta.id.in_(receta_ids), Receta.activo == True).all()
        resultado = [r.to_dict() for r in recetas]
        return jsonify({"recetas": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas para el ingrediente"}), 400
    

@ingredientes_receta_bp.route('/recetas-por-ingrediente', methods=['GET'])
@token_requerido
def recetas_por_nombre_ingrediente(usuario_actual):
    try:
        from models import Ingrediente, Receta
        nombre = request.args.get('nombre', '').strip()
        if not nombre:
            return jsonify({"mensaje": "Debes proporcionar el nombre del ingrediente"}), 400

        ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
        if not ingrediente:
            return jsonify({"mensaje": "Ingrediente no encontrado"}), 404

        relaciones = Ingrediente_Receta.query.filter_by(ingrediente_id=ingrediente.id).all()
        receta_ids = [rel.receta_id for rel in relaciones]
        recetas = Receta.query.filter(Receta.id.in_(receta_ids), Receta.activo == True).all()
        resultado = [r.to_dict() for r in recetas]
        return jsonify({"recetas": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas para el ingrediente"}), 400
    

@ingredientes_receta_bp.route('/<int:id_relacion>/modificar-ingrediente', methods=['PUT'])
@token_requerido
def modificar_ingrediente_de_receta(usuario_actual, id_relacion):
    try:
        from models import Ingrediente
        data = request.get_json()
        nuevo_nombre = data.get('nombre', '').strip()

        # Validar nombre: solo letras y guion medio, sin espacios, números ni caracteres especiales
        import re
        if not re.match(r'^[A-Za-z\-]+$', nuevo_nombre):
            return jsonify({"mensaje": "El nombre solo puede contener letras y guion medio (-), sin espacios, números ni caracteres especiales."}), 400

        relacion = Ingrediente_Receta.query.get(id_relacion)
        if not relacion:
            return jsonify({"mensaje": "Relación ingrediente-receta no encontrada"}), 404

        # Buscar si el ingrediente ya existe
        ingrediente = Ingrediente.query.filter_by(nombre=nuevo_nombre).first()
        if not ingrediente:
            # Si no existe, lo crea
            ingrediente = Ingrediente(nombre=nuevo_nombre)
            db.session.add(ingrediente)
            db.session.commit()  # Guardar para obtener el id

        # Cambiar el ingrediente_id en la relación
        relacion.ingrediente_id = ingrediente.id
        db.session.commit()
        return jsonify({"mensaje": "Ingrediente de la receta modificado correctamente", "ingrediente_id": ingrediente.id, "nombre": ingrediente.nombre})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar el ingrediente de la receta"}), 400
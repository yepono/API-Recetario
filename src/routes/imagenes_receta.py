# routes/imagenes_receta.py
# Contiene todas las rutas (endpoints) para manejar imagenes_receta
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import Usuario,Ingrediente,Imagen_Receta,Unidad,Ingrediente_Receta,Comentario,Receta
from models import VotoReceta                          # Modelo de la tabla imagenes_receta
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para imagenes_receta
imagenes_receta_bp = Blueprint('imagenes_receta_bp', __name__)

@imagenes_receta_bp.route('/<int:id_receta>/agregar-imagenes', methods=['POST'])
@token_requerido
def agregar_varias_imagenes_a_receta(usuario_actual, id_receta):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        # Solo permitir agregar imágenes si la receta pertenece al usuario actual o es admin
        if not (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False)):
            return jsonify({"mensaje": "No tienes permisos para agregar imágenes a esta receta"}), 403

        data = request.get_json()
        imagenes = data.get('imagenes', [])
        if not imagenes or not isinstance(imagenes, list):
            return jsonify({"mensaje": "Debes enviar una lista de imágenes en el campo 'imagenes'."}), 400

        nuevas_imagenes = []
        for img in imagenes:
            if not img:
                continue
            # img puede ser un dict con campos 'datos' y 'descripcion' (opcional)
            if isinstance(img, dict):
                datos_base64 = img.get('datos')
                descripcion = img.get('descripcion', None)
            else:
                datos_base64 = img
                descripcion = None
            if not datos_base64:
                continue
            imagen_bytes = base64.b64decode(datos_base64)
            nueva_imagen = Imagen_Receta(
                receta_id=id_receta,
                datos=imagen_bytes,
                descripcion=descripcion,
                activo=True
            )
            db.session.add(nueva_imagen)
            nuevas_imagenes.append(nueva_imagen)

        db.session.commit()
        ids = [img.id for img in nuevas_imagenes]
        return jsonify({"mensaje": "Imágenes agregadas correctamente", "imagenes_id": ids}), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al agregar las imágenes a la receta"}), 400

@imagenes_receta_bp.route('/<int:id_imagen>', methods=['DELETE'])
@token_requerido
def borrar_imagen(usuario_actual, id_imagen):
    try:
        imagen = Imagen_Receta.query.get(id_imagen)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada"}), 404

        # Solo permitir borrar si la imagen pertenece a una receta del usuario actual o es admin
        receta = Receta.query.get(imagen.receta_id)
        if not (receta and (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False))):
            return jsonify({"mensaje": "No tienes permisos para borrar esta imagen"}), 403

        imagen.activo = False  # Baja lógica
        db.session.commit()
        return jsonify({"mensaje": "Imagen borrada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al borrar la imagen"}), 400   


@imagenes_receta_bp.route('/<int:id_imagen>', methods=['PUT'])
@token_requerido
def modificar_imagen_receta(usuario_actual, id_imagen):
    try:
        imagen = Imagen_Receta.query.get(id_imagen)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada"}), 404

        receta = Receta.query.get(imagen.receta_id)
        # Solo permitir modificar si la imagen pertenece a una receta del usuario actual o es admin
        if not (receta and (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False))):
            return jsonify({"mensaje": "No tienes permisos para modificar esta imagen"}), 403

        data = request.get_json()
        if 'datos' not in data or not data['datos']:
            return jsonify({"mensaje": "El campo 'datos' (imagen en base64) es requerido."}), 400

        imagen.datos = base64.b64decode(data['datos'])
        # Permitir actualizar la descripción si se envía
        if 'descripcion' in data:
            imagen.descripcion = data['descripcion']
        db.session.commit()
        return jsonify({"mensaje": "Imagen modificada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la imagen"}), 400
    

@imagenes_receta_bp.route('/<int:id_receta>/baja-imagenes', methods=['DELETE'])
@token_requerido
def baja_logica_imagenes_receta(usuario_actual, id_receta):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        # Solo permitir si la receta pertenece al usuario actual o es admin
        if not (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False)):
            return jsonify({"mensaje": "No tienes permisos para dar de baja las imágenes de esta receta"}), 403

        imagenes = Imagen_Receta.query.filter_by(receta_id=id_receta, activo=True).all()
        if not imagenes:
            return jsonify({"mensaje": "No hay imágenes activas para esta receta"}), 404

        for imagen in imagenes:
            imagen.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Todas las imágenes de la receta fueron dadas de baja correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja las imágenes de la receta"}), 400
    

@imagenes_receta_bp.route('/<int:id_receta>/modificar-imagenes', methods=['PUT'])
@token_requerido
def modificar_todas_imagenes_receta(usuario_actual, id_receta):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        # Solo permitir si la receta pertenece al usuario actual o es admin
        if not (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False)):
            return jsonify({"mensaje": "No tienes permisos para modificar las imágenes de esta receta"}), 403

        data = request.get_json()
        imagenes_nuevas = data.get('imagenes', [])
        if not imagenes_nuevas or not isinstance(imagenes_nuevas, list):
            return jsonify({"mensaje": "Debes enviar una lista de imágenes en el campo 'imagenes'."}), 400

        # Dar de baja lógica todas las imágenes actuales activas de la receta
        imagenes_actuales = Imagen_Receta.query.filter_by(receta_id=id_receta, activo=True).all()
        for imagen in imagenes_actuales:
            imagen.activo = False

        # Agregar las nuevas imágenes
        nuevas_imagenes = []
        for img in imagenes_nuevas:
            if not img:
                continue
            # img puede ser un dict con campos 'datos' y 'descripcion' (opcional)
            if isinstance(img, dict):
                datos_base64 = img.get('datos')
                descripcion = img.get('descripcion', None)
            else:
                datos_base64 = img
                descripcion = None
            if not datos_base64:
                continue
            imagen_bytes = base64.b64decode(datos_base64)
            nueva_imagen = Imagen_Receta(
                receta_id=id_receta,
                datos=imagen_bytes,
                descripcion=descripcion,
                activo=True
            )
            db.session.add(nueva_imagen)
            nuevas_imagenes.append(nueva_imagen)

        db.session.commit()
        ids = [img.id for img in nuevas_imagenes]
        return jsonify({"mensaje": "Imágenes de la receta modificadas correctamente", "imagenes_id": ids}), 200
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar las imágenes de la receta"}), 400
    

@imagenes_receta_bp.route('/mis-imagenes', methods=['GET'])
@token_requerido
def ver_imagenes_usuario_actual(usuario_actual):
    try:
        # Obtener todas las recetas del usuario actual
        recetas = Receta.query.filter_by(usuario_id=usuario_actual.id).all()
        receta_ids = [r.id for r in recetas]
        # Obtener todas las imágenes activas de esas recetas
        imagenes = Imagen_Receta.query.filter(
            Imagen_Receta.receta_id.in_(receta_ids),
            Imagen_Receta.activo == True
        ).all()
        resultado = []
        for img in imagenes:
            resultado.append({
                "id": img.id,
                "receta_id": img.receta_id,
                # "datos": base64.b64encode(img.datos).decode('utf-8')  # Descomenta si quieres devolver la imagen en base64
                "descripcion": img.descripcion
            })
        return jsonify({"imagenes": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener las imágenes del usuario"}), 400
    
@imagenes_receta_bp.route('/<int:id_receta>/imagenes', methods=['GET'])
@token_requerido
def ver_imagenes_de_receta(usuario_actual, id_receta):
    try:
        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        # Solo permitir ver si la receta pertenece al usuario actual o es admin
        if not (receta.usuario_id == usuario_actual.id or getattr(usuario_actual, 'admin', False)):
            return jsonify({"mensaje": "No tienes permisos para ver las imágenes de esta receta"}), 403

        imagenes = Imagen_Receta.query.filter_by(receta_id=id_receta, activo=True).all()
        resultado = []
        for img in imagenes:
            resultado.append({
                "id": img.id,
                "receta_id": img.receta_id,
                # "datos": base64.b64encode(img.datos).decode('utf-8'),  # Descomenta si quieres devolver la imagen en base64
                "descripcion": img.descripcion
            })
        return jsonify({"imagenes": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener las imágenes de la receta"}), 400
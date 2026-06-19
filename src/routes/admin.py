import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importaciones necesarias
from flask import Blueprint, request, jsonify          # Herramientas de Flask
from database import db                                # Conexión a la base de datos
from config import Config
from models import  Usuario,Ingrediente,Imagen_Receta,Unidad,Ingrediente_Receta,Comentario,Receta
from models import VotoReceta                          # Modelo de usuario
import jwt                                             # Librería para manejar tokens JWT
import datetime                                        # Para manejar fechas de expiración
from werkzeug.security import generate_password_hash, check_password_hash  # Para encriptar y verificar contraseñas

from routes.auth import token_requerido
# Creamos un Blueprint llamado 'auth_bp' para agrupar las rutas de autenticación
admin_bp = Blueprint('admin_bp', __name__)



@admin_bp.route('/usuarios-eliminados', methods=['GET'])
@token_requerido
def ver_usuarios_eliminados(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        usuarios = Usuario.query.filter_by(activo=False).all()
        resultado = [u.to_dict() for u in usuarios]
        return jsonify({"usuarios_eliminados": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener usuarios eliminados"}), 400
    
@admin_bp.route('/recetas-eliminadas', methods=['GET'])
@token_requerido
def ver_recetas_eliminadas(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        recetas = Receta.query.filter_by(activo=False).all()
        resultado = [r.to_dict() for r in recetas]
        return jsonify({"recetas_eliminadas": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas eliminadas"}), 400

@admin_bp.route('/imagenes-eliminadas', methods=['GET'])
@token_requerido
def ver_imagenes_eliminadas(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        imagenes = Imagen_Receta.query.filter_by(activo=False).all()
        resultado = [i.to_dict() for i in imagenes]
        return jsonify({"imagenes_eliminadas": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener imágenes eliminadas"}), 400
    
@admin_bp.route('/ingredientes-eliminados', methods=['GET'])
@token_requerido
def ver_ingredientes_eliminados(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        ingredientes = Ingrediente.query.filter_by(activo=False).all()
        resultado = [i.to_dict() for i in ingredientes]
        return jsonify({"ingredientes_eliminados": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener ingredientes eliminados"}), 400

@admin_bp.route('/unidades-eliminadas', methods=['GET'])
@token_requerido
def ver_unidades_eliminadas(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        unidades = Unidad.query.filter_by(activo=False).all()
        resultado = [u.to_dict() for u in unidades]
        return jsonify({"unidades_eliminadas": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener unidades eliminadas"}), 400

@admin_bp.route('/comentarios-eliminados', methods=['GET'])
@token_requerido
def ver_comentarios_eliminados(usuario_actual):
    try:
        # Verifica si el usuario actual tiene el atributo admin=True
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        comentarios = Comentario.query.filter_by(activo=False).all()
        resultado = [c.to_dict() for c in comentarios]
        return jsonify({"comentarios_eliminados": resultado})
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener comentarios eliminados"}), 400

@admin_bp.route('/usuarios/<int:id_usuario>/activar', methods=['PUT'])
@token_requerido
def activar_usuario(usuario_actual, id_usuario):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        usuario.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Usuario activado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar el usuario"}), 400

@admin_bp.route('/recetas/<int:id_receta>/activar', methods=['PUT'])
@token_requerido
def activar_receta(usuario_actual, id_receta):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        receta.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Receta activada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar la receta"}), 400

@admin_bp.route('/imagenes/<int:id_imagen>/activar', methods=['PUT'])
@token_requerido
def activar_imagen(usuario_actual, id_imagen):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        imagen = Imagen_Receta.query.get(id_imagen)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada"}), 404

        imagen.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Imagen activada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar la imagen"}), 400

@admin_bp.route('/ingredientes/<int:id_ingrediente>/activar', methods=['PUT'])
@token_requerido
def activar_ingrediente(usuario_actual, id_ingrediente):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        ingrediente = Ingrediente.query.get(id_ingrediente)
        if not ingrediente:
            return jsonify({"mensaje": "Ingrediente no encontrado"}), 404

        ingrediente.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Ingrediente activado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar el ingrediente"}), 400

@admin_bp.route('/unidades/<int:id_unidad>/activar', methods=['PUT'])
@token_requerido
def activar_unidad(usuario_actual, id_unidad):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        unidad = Unidad.query.get(id_unidad)
        if not unidad:
            return jsonify({"mensaje": "Unidad no encontrada"}), 404

        unidad.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Unidad activada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar la unidad"}), 400

@admin_bp.route('/comentarios/<int:id_comentario>/activar', methods=['PUT'])
@token_requerido
def activar_comentario(usuario_actual, id_comentario):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        comentario = Comentario.query.get(id_comentario)
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado"}), 404

        comentario.activo = True
        db.session.commit()
        return jsonify({"mensaje": "Comentario activado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al activar el comentario"}), 400

@admin_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
@token_requerido
def baja_logica_usuario(usuario_actual, id_usuario):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        # Baja lógica del usuario
        usuario.activo = False

        # Baja lógica de recetas del usuario
        for receta in getattr(usuario, 'recetas', []):
            receta.activo = False
            # Baja lógica de imágenes de la receta
            for imagen in getattr(receta, 'imagenes', []):
                imagen.activo = False
            # Baja lógica de comentarios de la receta
            for comentario in getattr(receta, 'comentarios', []):
                comentario.activo = False
            # Baja lógica de votos de la receta
            for voto in getattr(receta, 'votos', []):
                voto.activo = False

        # Baja lógica de comentarios del usuario
        for comentario in getattr(usuario, 'comentarios', []):
            comentario.activo = False

        # Baja lógica de imágenes subidas por el usuario (si aplica)
        for imagen in getattr(usuario, 'imagenes', []):
            imagen.activo = False

        # Baja lógica de votos del usuario
        for voto in getattr(usuario, 'votos', []):
            voto.activo = False

        # Baja lógica de likes del usuario (si tienes una relación de likes)
        if hasattr(usuario, 'likes'):
            for like in usuario.likes:
                like.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Usuario y todos sus elementos asociados dados de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente al usuario"}), 400

@admin_bp.route('/recetas/<int:id_receta>', methods=['DELETE'])
@token_requerido
def baja_logica_receta(usuario_actual, id_receta):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        # Baja lógica de la receta
        receta.activo = False

        # Baja lógica de imágenes asociadas
        for imagen in getattr(receta, 'imagenes', []):
            imagen.activo = False

        # Baja lógica de comentarios asociados
        for comentario in getattr(receta, 'comentarios', []):
            comentario.activo = False

        # Baja lógica de votos asociados
        for voto in getattr(receta, 'votos', []):
            voto.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Receta y sus elementos asociados dados de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente la receta"}), 400
    
@admin_bp.route('/imagenes/<int:id_imagen>', methods=['DELETE'])
@token_requerido
def baja_logica_imagen(usuario_actual, id_imagen):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        imagen = Imagen_Receta.query.get(id_imagen)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada"}), 404

        imagen.activo = False  # Baja lógica de la imagen

        db.session.commit()
        return jsonify({"mensaje": "Imagen dada de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente la imagen"}), 400
    
@admin_bp.route('/ingredientes/<int:id_ingrediente>', methods=['DELETE'])
@token_requerido
def baja_logica_ingrediente(usuario_actual, id_ingrediente):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        ingrediente = Ingrediente.query.get(id_ingrediente)
        if not ingrediente:
            return jsonify({"mensaje": "Ingrediente no encontrado"}), 404

        ingrediente.activo = False  # Baja lógica del ingrediente

        db.session.commit()
        return jsonify({"mensaje": "Ingrediente dado de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente el ingrediente"}), 400

@admin_bp.route('/unidades/<int:id_unidad>', methods=['DELETE'])
@token_requerido
def baja_logica_unidad(usuario_actual, id_unidad):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        unidad = Unidad.query.get(id_unidad)
        if not unidad:
            return jsonify({"mensaje": "Unidad no encontrada"}), 404

        unidad.activo = False  # Baja lógica de la unidad

        db.session.commit()
        return jsonify({"mensaje": "Unidad dada de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente la unidad"}), 400

@admin_bp.route('/comentarios/<int:id_comentario>', methods=['DELETE'])
@token_requerido
def baja_logica_comentario(usuario_actual, id_comentario):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        comentario = Comentario.query.get(id_comentario)
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado"}), 404

        comentario.activo = False  # Baja lógica del comentario

        db.session.commit()
        return jsonify({"mensaje": "Comentario dado de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente el comentario"}), 400


@admin_bp.route('/comentarios/<int:id_comentario>', methods=['DELETE'])
@token_requerido
def baja_logica_comentario(usuario_actual, id_comentario):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        comentario = Comentario.query.get(id_comentario)
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado"}), 404

        comentario.activo = False  # Baja lógica del comentario

        db.session.commit()
        return jsonify({"mensaje": "Comentario dado de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja lógicamente el comentario"}), 400
    
@admin_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@token_requerido
def modificar_usuario_admin(usuario_actual, id_usuario):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        data = request.get_json()
        # Actualiza solo los campos enviados
        for campo in ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'nickname']:
            if campo in data:
                setattr(usuario, campo, data[campo])

        if 'password' in data and data['password']:
            usuario.password = generate_password_hash(data['password'])

        if 'imagen' in data and data['imagen']:
            usuario.imagen = base64.b64decode(data['imagen'])

        db.session.commit()
        return jsonify({"mensaje": "Usuario modificado correctamente", "usuario": usuario.to_dict()})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar el usuario"}), 400

@admin_bp.route('/recetas/<int:id_receta>', methods=['PUT'])
@token_requerido
def modificar_receta_admin(usuario_actual, id_receta):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        receta = Receta.query.get(id_receta)
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada"}), 404

        data = request.get_json()
        for campo in ['titulo', 'descripcion']:
            if campo in data:
                setattr(receta, campo, data[campo])

        db.session.commit()
        return jsonify({"mensaje": "Receta modificada correctamente", "receta": receta.to_dict()})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la receta"}), 400

@admin_bp.route('/imagenes/<int:id_imagen>', methods=['PUT'])
@token_requerido
def modificar_imagen_admin(usuario_actual, id_imagen):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        imagen = Imagen_Receta.query.get(id_imagen)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada"}), 404

        data = request.get_json()
        if 'datos' in data:
            imagen.datos = base64.b64decode(data['datos'])

        db.session.commit()
        return jsonify({"mensaje": "Imagen modificada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la imagen"}), 400

@admin_bp.route('/ingredientes/<int:id_ingrediente>', methods=['PUT'])
@token_requerido
def modificar_ingrediente_admin(usuario_actual, id_ingrediente):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        ingrediente = Ingrediente.query.get(id_ingrediente)
        if not ingrediente:
            return jsonify({"mensaje": "Ingrediente no encontrado"}), 404

        data = request.get_json()
        if 'nombre' in data:
            ingrediente.nombre = data['nombre']

        db.session.commit()
        return jsonify({"mensaje": "Ingrediente modificado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar el ingrediente"}), 400

@admin_bp.route('/unidades/<int:id_unidad>', methods=['PUT'])
@token_requerido
def modificar_unidad_admin(usuario_actual, id_unidad):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        unidad = Unidad.query.get(id_unidad)
        if not unidad:
            return jsonify({"mensaje": "Unidad no encontrada"}), 404

        data = request.get_json()
        if 'nombre' in data:
            unidad.nombre = data['nombre']

        db.session.commit()
        return jsonify({"mensaje": "Unidad modificada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la unidad"}), 400

@admin_bp.route('/comentarios/<int:id_comentario>', methods=['PUT'])
@token_requerido
def modificar_comentario_admin(usuario_actual, id_comentario):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        comentario = Comentario.query.get(id_comentario)
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado"}), 404

        data = request.get_json()
        if 'comentario' in data:
            comentario.comentario = data['comentario']

        db.session.commit()
        return jsonify({"mensaje": "Comentario modificado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar el comentario"}), 400

@admin_bp.route('/valoraciones/<int:id_valoracion>', methods=['PUT'])
@token_requerido
def modificar_valoracion_admin(usuario_actual, id_valoracion):
    try:
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        valoracion = VotoReceta.query.get(id_valoracion)
        if not valoracion:
            return jsonify({"mensaje": "Valoración no encontrada"}), 404

        data = request.get_json()
        if 'valor' in data:
            valoracion.valor = data['valor']

        db.session.commit()
        return jsonify({"mensaje": "Valoración modificada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al modificar la valoración"}), 400

@admin_bp.route('/usuarios', methods=['POST'])
@token_requerido
def agregar_usuario_admin(usuario_actual):
    try:
        # Solo admin puede realizar esta acción
        if not getattr(usuario_actual, 'admin', False):
            return jsonify({"mensaje": "No tienes permisos de administrador"}), 403

        data = request.get_json()
        campos_obligatorios = ['nombre', 'apellido', 'email', 'password', 'nickname']
        for campo in campos_obligatorios:
            if campo not in data or not data[campo]:
                return jsonify({"mensaje": f"El campo '{campo}' es obligatorio."}), 400

        import re
        # Validar nombre y nickname: solo letras y guion medio, sin espacios ni caracteres especiales
        if not re.match(r'^[A-Za-z\-]+$', data['nombre']):
            return jsonify({"mensaje": "El nombre solo puede contener letras y guion medio (-), sin espacios ni caracteres especiales."}), 400
        if not re.match(r'^[A-Za-z\-]+$', data['nickname']):
            return jsonify({"mensaje": "El nickname solo puede contener letras y guion medio (-), sin espacios ni caracteres especiales."}), 400

        # Verificar si el email o nickname ya existen
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({"mensaje": "El email ya está registrado."}), 400
        if Usuario.query.filter_by(nickname=data['nickname']).first():
            return jsonify({"mensaje": "El nickname ya está registrado."}), 400

        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            nickname=data['nickname'],
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            admin=bool(data.get('admin', False)),
            activo=True
        )

        # Si se envía imagen en base64
        if 'imagen' in data and data['imagen']:
            import base64
            nuevo_usuario.imagen = base64.b64decode(data['imagen'])

        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario agregado correctamente", "usuario": nuevo_usuario.to_dict()}), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al agregar el usuario"}), 400


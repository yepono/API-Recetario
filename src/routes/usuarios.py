# routes/usuarios.py
# Contiene todas las rutas (endpoints) para manejar usuarios
#¡Esto le dice a Python que incluya la raíz del proyecto en la búsqueda!
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import  Usuario,Ingrediente,Imagen_Receta,Unidad,Ingrediente_Receta,Comentario
from models import VotoReceta                         # Modelo de la tabla Usuario
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT
from werkzeug.security import generate_password_hash, check_password_hash  # Para encriptar y verificar contraseñas

# Definir el Blueprint para usuarios
usuarios_bp = Blueprint('usuarios_bp', __name__)

#----------------------------------
# Ruta: GET/usuarios/
# Descripcion: Obtener todos los usuarios
# Protegida con token JWT
#------------------------------------------
@usuarios_bp.route('/', methods=['GET'])
@token_requerido # Esta ruta solo puede ser accedida mediante un token valido
def obtener_usuarios(usuario_actual):
    try: 
        print("Petición hecha por:", usuario_actual.email) # para ver quien realiza la peticion
        usuarios = Usuario.query.all() # Consulta todos los usuarios de la bd
        return jsonify([usuario.to_dict() for usuario in usuarios]) # Convierte cada alumno en dict y lo regresa como JSON
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": 'Error'})


# -----------------------------
# Ruta: POST /alumnos/
# Descripción: Crear un nuevo alumno (sin requerir token en este ejemplo)
# -----------------------------
@usuarios_bp.route('/', methods=['POST'])
@token_requerido
def agregar_usuario():
    try:
        data = request.get_json()                     # Recibimos los datos en formato JSON
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        email = data.get('email')
        password = data.get('password')

        # Campos no opcionales
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        nickname = data.get('nickname')

        campos = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "telefono": telefono,
            "nickname": nickname
        }
        for campo, valor in campos.items():
            if valor and (" " in valor or "_" in valor):
                return jsonify({"error": f"El campo '{campo}' no puede contener espacios ni _"}), 400

        # Decodifica la imagen en base64 si viene incluida en los datos
        imagen_bytes = None
        if 'imagen' in data and data['imagen']:
            imagen_bytes = base64.b64decode(data['imagen'])
        
        # 🔒 Encriptamos la contraseña antes de guardarla
        password_segura = generate_password_hash(data['password'])

        # Crea el objeto alumno con los datos recibidos
        nuevo = Usuario(
            nombre=data['nombre'],
            apellido= data['apellido'],
            email=data['email'],
            password=password_segura,
            telefono=data['telefono'],
            direccion=data['direccion'],
            nickname=data['nickname'],
            imagen=imagen_bytes,  # Guarda la imagen como bytes (binary)
        )
        db.session.add(nuevo)     # Agrega el alumno a la sesión
        db.session.commit()       # Guarda los cambios en la base de datos

        return jsonify(nuevo.to_dict()), 201  # Retorna el nuevo alumno en formato JSON

    except Exception as ex:
        return jsonify({'mensaje': 'Error al registrar usuario'}), 400

# -----------------------------
# Ruta: PUT /alumnos/<id>
# Descripción: Actualizar un alumno existente por su ID
# -----------------------------
@usuarios_bp.route('/mi-usuario', methods=['PUT'])
@token_requerido  # Esta ruta solo puede ser accedida con un token válido
def actualiza_usuario_actual(usuario_actual):
    try: 
        print("Petición hecha por:", usuario_actual.email)
        data = request.get_json()
        
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        email = data.get('email')
        password = data.get('password')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        nickname = data.get('nickname')

        # Solo letras y números, sin espacios, guiones bajos ni caracteres especiales
        import re
        patron = r'^[A-Za-z0-9]+$'
        for campo in ['nombre', 'nickname']:
            valor = data.get(campo, '')
            if valor and not re.match(patron, valor):
                return jsonify({"error": f"El campo '{campo}' solo puede contener letras y números, sin espacios, guiones bajos ni caracteres especiales."}), 400

        usuario_actual.nombre = nombre
        usuario_actual.email = email
        usuario_actual.apellido = apellido
        usuario_actual.telefono = telefono
        usuario_actual.direccion = direccion
        usuario_actual.nickname = nickname

        # Si se proporciona una nueva contraseña, actualízala
        if password:
            usuario_actual.password = generate_password_hash(password)

        # Si viene una imagen nueva, actualiza también
        if 'imagen' in data and data['imagen']:
            usuario_actual.imagen = base64.b64decode(data['imagen'])

        db.session.commit()
        return jsonify(usuario_actual.to_dict())

    except Exception as ex:
        db.session.rollback()
        return jsonify({'mensaje': 'Error al actualizar usuario'})
    try: 
        print("Petición hecha por:", usuario_actual.email)
        data = request.get_json()
        usuario = Usuario.query.get_or_404(id)  # Busca al alumno por ID o lanza error 404 si no existe
        if usuario.id != usuario_actual.id:
            return jsonify({'mensaje': 'No tienes permiso para actualizar este usuario.'}), 403# Recibimos los datos en formato JSON
        
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        email = data.get('email')
        password = data.get('password')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        nickname = data.get('nickname')

        campos = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "telefono": telefono,
            "nickname": nickname
        }
        for campo, valor in campos.items():
            if valor and (" " in valor or "_" in valor):
                return jsonify({"error": f"El campo '{campo}' no puede contener espacios ni _"}), 400

        usuario.nombre = data['nombre']        # Actualiza nombre
        usuario.email = data['email']        # Actualiza correo
        usuario.apellido = data['apellido']        # Actualiza apellido
        usuario.telefono = data['telefono']        # Actualiza telefono
        usuario.direccion = data['direccion']        # Actualiza direccion
        usuario.nickname = data['nickname']        # Actualiza nickname
        # Si se proporciona una nueva contraseña, actualízala
        if 'password' in data and data['password']:
            usuario.password = generate_password_hash(data['password'])  # Encriptamos la nueva contraseña

        # Si viene una imagen nueva, actualiza también
        if 'imagen' in data and data['imagen']:
            usuario.imagen = base64.b64decode(data['imagen'])

        db.session.commit()   # Guarda los cambios en la base de datos
        return jsonify(usuario.to_dict())  # Devuelve el alumno actualizado

    except Exception as ex:
        return jsonify({'mensaje': 'Error al actualizar usuario'})

# -----------------------------
# Ruta: DELETE /alumnos/<id>
# Descripción: Eliminar un alumno por su ID
# -----------------------------
@usuarios_bp.route('/mi-usuario', methods=['DELETE'])
@token_requerido
def eliminar_usuario_actual(usuario_actual):
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'mensaje': 'Debes proporcionar email y contraseña'}), 400

        if usuario_actual.email != email:
            return jsonify({'mensaje': 'El email no coincide con el usuario autenticado'}), 400

        from werkzeug.security import check_password_hash
        if not check_password_hash(usuario_actual.password, password):
            return jsonify({'mensaje': 'Contraseña incorrecta'}), 400

        # Baja lógica de recetas e imágenes
        for receta in usuario_actual.recetas:
            receta.activo = False
            for imagen in getattr(receta, 'imagenes', []):
                imagen.activo = False

        # Baja lógica de comentarios
        for comentario in usuario_actual.comentarios:
            comentario.activo = False

        # Baja lógica de valoraciones (votos)
        for voto in usuario_actual.votos:
            voto.activo = False

        # Baja lógica de likes a comentarios (si existe la relación)
        if hasattr(usuario_actual, 'likes_comentarios'):
            for like in usuario_actual.likes_comentarios:
                like.activo = False

        # Finalmente, baja lógica del usuario
        usuario_actual.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Usuario y sus publicaciones dados de baja lógicamente."})

    except Exception as ex:
        db.session.rollback()
        return jsonify({"mensaje": 'Error al eliminar usuario.'})
# routes/auth.py
#¡Esto le dice a Python que incluya la raíz del proyecto en la búsqueda!
import sys
import os
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importaciones necesarias
from flask import Blueprint, request, jsonify          # Herramientas de Flask
from database import db                                # Conexión a la base de datos
from config import Config
from models import Usuario                             # Modelo de usuario
import jwt                                             # Librería para manejar tokens JWT
import datetime                                        # Para manejar fechas de expiración
from werkzeug.security import generate_password_hash, check_password_hash  # Para encriptar y verificar contraseñas

# Creamos un Blueprint llamado 'auth_bp' para agrupar las rutas de autenticación
auth_bp = Blueprint('auth_bp', __name__)

# Clave secreta para firmar y verificar los tokens (puede venir desde config.py)
SECRET_KEY = Config.SECRET_KEY

# ----------------------------
# Ruta: POST /auth/register
# Descripción: Permite registrar un nuevo usuario
# ----------------------------
@auth_bp.route('/register', methods=['POST'])
def register():

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

    # Asegurarnos que la imagen se pueda guardar en base 64
    imagen_base64 = data.get('imagen')
    imagen_binaria = None

    if imagen_base64:
        try:
            imagen_binaria = base64.b64decode(imagen_base64)
        except Exception as e:
            return jsonify({"error": "Imagen no válida"}), 400

    # Verificamos si ya existe un usuario con ese correo
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "Usuario ya registrado"}), 400

    # 🔒 Encriptamos la contraseña antes de guardarla
    password_segura = generate_password_hash(password)

    # Creamos el nuevo usuario
    nuevo = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password=password_segura,  # Guardamos la contraseña encriptada
        telefono = telefono,
        direccion = direccion,
        nickname = nickname,
        imagen = imagen_binaria
    )
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201

# ----------------------------
# Ruta: POST /auth/login
# Descripción: Permite a un usuario iniciar sesión y obtener un token JWT
# ----------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verificamos que el correo y la contraseña no estén vacíos
    usuario = Usuario.query.filter_by(email=email).first()

    # ⚠️ Verifica si existe y si la contraseña es correcta
    if not usuario or not check_password_hash(usuario.password, password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Creamos el token JWT con el ID del usuario y una expiración de 1 hora
    token = jwt.encode({
        'user_id': usuario.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})   # Enviamos el token al cliente

# ----------------------------
# Decorador: @token_requerido
# Descripción: Verifica que el usuario tenga un token válido antes de acceder a una ruta
# ----------------------------
from functools import wraps   # Sirve para mantener el nombre y docstring de la función decorada

def token_requerido(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        # Verificamos si el token viene en los encabezados HTTP
        if 'Authorization' in request.headers:
            # Esperamos un encabezado así: Authorization: Bearer <token>
            token = request.headers['Authorization'].split(" ")[1]

        # Si no viene el token, rechazamos la solicitud
        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            # Decodificamos el token y extraemos el ID del usuario
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            usuario_actual = Usuario.query.get(data['user_id'])  # Obtenemos el usuario desde la BD

        except:
            # Si el token está mal formado o expiró, rechazamos la solicitud
            return jsonify({"error": "Token inválido o expirado"}), 401

        # Si todo salió bien, continuamos ejecutando la función original
        return f(usuario_actual, *args, **kwargs)

    return decorator

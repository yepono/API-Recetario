import base64  # Librería para codificar y decodificar imágenes en base64
from datetime import datetime # Para manejar fechas y horas
from database import db # Importa la instancia global de SQLAlchemy

# Definición del modelo Usuario
class Usuario(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(10), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    nickname = db.Column(db.String(30), nullable=True)
    imagen = db.Column(db.LargeBinary, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())
    activo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)  # Campo para indicar si es administrador
    # metodos
    def to_dict(self):

         # Convierte la imagen binaria a base64 si existe, de lo contrario devuelve None
        imagen_base64 = base64.b64encode(self.imagen).decode('utf-8') if self.imagen else None

        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'nickname': self.nickname,
            'imagen': imagen_base64,
            'fecha_creacion': self.fecha_creacion
        }
    def __repr__(self):
        return f"<Usuario {self.nombre} {self.apellido}>"


# Definición del modelo Receta
class Receta(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
    activo = db.Column(db.Boolean, default=True)

    # LLave foranea
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id')) 

    # Relaciones
    usuario = db.relationship('Usuario', backref='recetas', lazy=True)  # Relación con la tabla Usuario

    # metodos
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion,
            'fecha_modificacion': self.fecha_modificacion
        }
    def __repr__(self):
        return f"<Receta {self.titulo} {self.descripcion}>"


# Definición del modelo Unidades
class Unidad(db.Model): # db.Model le dice a SQLAlchemy "esto es una tabla"
    
    id = db.Column(db.Integer, primary_key=True)  # Clave primaria autoincremental
    nombre = db.Column(db.String(50), nullable=False) # Nombre de la unidad

    # metodos
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
        }
    def __repr__(self):
        return f"<Unidad {self.nombre}>"

    
# Definición del modelo Ingrediente_Receta
# Definición del modelo Ingrediente
class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    # Relación con Ingrediente_Receta
    recetas = db.relationship('Ingrediente_Receta', backref='ingrediente', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }

    def __repr__(self):
        return f"<Ingrediente {self.nombre}>"

# Definición del modelo Ingrediente_Receta (tabla intermedia)
class Ingrediente_Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Numeric(10, 2), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Llaves foráneas
    id_ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable=False)
    id_unidad = db.Column(db.Integer, db.ForeignKey('unidad.id'), nullable=False)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'), nullable=False)

    # Relaciones
    unidad = db.relationship('Unidad', backref='ingredientes_receta', lazy=True)
    receta = db.relationship('Receta', backref='ingredientes_receta', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'ingrediente': self.ingrediente.nombre if self.ingrediente else None,
            'cantidad': self.cantidad,
            'unidad': self.unidad.nombre if self.unidad else None,
            'id_receta': self.id_receta
        }

    def __repr__(self):
        return f"<Ingrediente_Receta {self.ingrediente.nombre} {self.cantidad} {self.unidad.nombre}>"
# Definición del modelo Imagen_Receta
class Imagen_Receta(db.Model): # db.Model le dice a SQLAlchemy "esto es una tabla"
    activo = db.Column(db.Boolean, default=True)
    id = db.Column(db.Integer, primary_key=True)  # Clave primaria autoincremental
    descripcion = db.Column(db.Text)  # Descripcion de la imagen
    imagen = db.Column(db.LargeBinary, nullable=False) # Imagen de la receta 
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())  # Fecha de creación
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())  # Fecha de creación
    
    # Llave foranea
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))  # Clave foranea, relacion con receta
    # Relacion
    receta = db.relationship('Receta', backref='imagenes_receta', lazy=True)  # Relación con la tabla Receta

    # metodos
    def to_dict(self):
        
        # Convierte la imagen binaria a base64 si existe, de lo contrario devuelve None
        imagen_base64 = base64.b64encode(self.imagen).decode('utf-8') if self.imagen else None

        return {
            'id': self.id,
            'receta_id': self.id_receta,
            'descripcion': self.descripcion,
            'imagen': imagen_base64,
            'fecha_creacion': self.fecha_creacion,
            'fecha_modificacion': self.fecha_modificacion
    }

    def __repr__(self):
        return f"<Imagen_Receta {self.descripcion}>"


# Definición del modelo Comentario
class Comentario(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
    activo = db.Column(db.Boolean, default=True)
    
    # Relacion recursiva
    id_comentario_padre = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=True)

    # Llaves foraneas
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    likes = db.relationship('LikeComentario', backref='comentario_liked', lazy='dynamic')
    # Relaciones (permite acceder de manera mas sencilla a usuario y receta sin necesidad de hacer el query a la bd)
    receta = db.relationship('Receta', backref='comentarios', lazy=True)  # Relación con la tabla Receta
    usuario = db.relationship('Usuario', backref='comentarios', lazy=True)  # Relación con la tabla Usuario
    comentario_padre = db.relationship('Comentario', remote_side=[id], backref=db.backref('comentarios_hijos', lazy='dynamic'), lazy='joined')
    # models.py
    
    """remote_side=[id] para especificar que la relación recursiva está usando la misma tabla y columna (id).
       lazy='joined' se usa para que la relación se cargue en la misma consulta SQL cuando se obtenga un comentario, haciendo la consulta más eficiente."""
    
    # metodos
    def to_dict(self):
        return {
            'id': self.id,
            'comentario': self.comentario,
            'likes': self.likes,
            'fecha_creacion': self.fecha_creacion,
            'fecha_modificacion': self.fecha_modificacion,
            'id_receta': self.id_receta,
            'id_usuario': self.id_usuario
        }
    def __repr__(self):
        return f"<Comentario {self.id} {self.comentario}>"

class LikeComentario(db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_comentario = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='likes_comentario', lazy=True)
    comentario = db.relationship('Comentario', backref='likes_rel', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('id_usuario', 'id_comentario', name='uq_usuario_comentario_like'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'id_comentario': self.id_comentario,
            'fecha_creacion': self.fecha_creacion,
            'activo': self.activo
        }

    def __repr__(self):
        return f"<LikeComentario usuario={self.id_usuario} comentario={self.id_comentario}>"

# Definición del modelo Voto_Receta
class VotoReceta(db.Model):
    activo = db.Column(db.Boolean, default=True)
    
    id = db.Column(db.Integer, primary_key=True)  # Llave primaria
    puntuacion = db.Column(db.Integer, nullable=False)  # Puntuación (entre 1 y 5)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=db.func.now())  # Fecha de creación
    
    #Llaves foraneas
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))  # Llave foránea hacia la tabla Receta
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))  # Llave foránea hacia la tabla Usuario
    
    # Definir la restricción UNIQUE para receta_id y usuario_id
    __table_args__ = (db.UniqueConstraint('id_receta', 'id_usuario', name='uq_receta_usuario'),
                      db.CheckConstraint('puntuacion >= 1 AND puntuacion <= 5', name='check_puntuacion_1_5'),)
    
    # Relaciones (permite acceder de manera mas sencilla a usuario y receta sin necesidad de hacer el query a la bd)
    receta = db.relationship('Receta', backref='votos', lazy=True)  # Relación con la tabla Receta
    usuario = db.relationship('Usuario', backref='votos', lazy=True)  # Relación con la tabla Usuario

    # Métodos
    def to_dict(self):
        return {
            'id': self.id,
            'receta_id': self.id_receta,
            'usuario_id': self.id_usuario,
            'puntuacion': self.puntuacion,
            'fecha_creacion': self.fecha_creacion
        }

    def __repr__(self):
        return f"<VotoReceta receta_id={self.receta_id} usuario_id={self.usuario_id} puntuacion={self.puntuacion}>"


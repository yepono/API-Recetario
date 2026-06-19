# routes/recetas.py
# Contiene todas las rutas (endpoints) para manejar recetas
import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import  Usuario,Ingrediente,Imagen_Receta,Unidad,Ingrediente_Receta,Comentario,LikeComentario
from models import VotoReceta
import base64                                       # Para convertir imágenes entre base64 y bytes
from flask import Blueprint, request, jsonify       # Herramientas de Flask
from models import Receta                           # Modelo de la tabla Receta
from database import db                             # Instancia de la base de datos
from routes.auth import token_requerido             # Decorador para proteger rutas con JWT

# Definir el Blueprint para recetas
recetas_bp = Blueprint('recetas_bp', __name__)

def fix_base64_padding(b64_string):
    return b64_string + '=' * (-len(b64_string) % 4)
@recetas_bp.route('/', methods=['GET'])
@token_requerido
def todas_las_recetas(usuario_actual):
    try:
        print("Petición hecha por:", usuario_actual.email)
        recetas = Receta.query.filter_by(activo=True).all()
        resultado = []
        for receta in recetas:
           
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
            # Imágenes en base64
            imagenes = []
            if hasattr(receta, 'imagenes'):
                for img in receta.imagenes:
                    imagenes.append(base64.b64encode(img.datos).decode('utf-8'))

            # Calcular media de valoraciones
            valoraciones = [v.puntuacion for v in getattr(receta, 'votos', []) if hasattr(v, 'puntuacion')]
            if valoraciones:
                media_valoraciones = round(sum(valoraciones) / len(valoraciones), 2)
            else:
                media_valoraciones = None

            resultado.append({
                "usuario": receta.usuario.nombre,
                "nickname": receta.usuario.nickname,
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes,
                "media_valoraciones": media_valoraciones
            })
        return jsonify(resultado)
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener todas las recetas"})   

@recetas_bp.route('/', methods=['POST'])
@token_requerido
def agregar_receta(usuario_actual):
    try:
        data = request.get_json()
       
        patron = r'^[A-Za-z\-]+$'
        if not re.match(patron, data['titulo']):
            return jsonify({'mensaje': 'El nombre de la receta solo puede contener letras y el guion - (sin espacios, números ni caracteres especiales)'}), 400

        for ing in data.get('ingredientes', []):
            if not re.match(patron, ing.get('nombre', '')):
                return jsonify({'mensaje': f"El nombre del ingrediente '{ing.get('nombre')}' solo puede contener letras y el guion - (sin espacios, números ni caracteres especiales)"}), 400

        
        nuevo = Receta(
            titulo=data['titulo'],
            descripcion=data['descripcion'],
            id_usuario=usuario_actual.id
        )
        db.session.add(nuevo)
        db.session.flush()  

        imagenes = data.get('imagenes', [])
        for img_dict in imagenes:
            descripcion = img_dict.get('descripcion', '')
            img_base64 = img_dict.get('imagen', '')
            if not img_base64:
                continue
            img_bin = base64.b64decode(fix_base64_padding(img_base64))
            nueva_imagen = Imagen_Receta(
                imagen=img_bin,
                descripcion=descripcion,
                id_receta=nuevo.id
            )
            db.session.add(nueva_imagen)
        
        ingredientes = data.get('ingredientes', [])
        for ing in ingredientes:
            nombre = ing.get('nombre')
            cantidad = ing.get('cantidad')
            unidad_nombre = ing.get('unidad')

      
            ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
            if not ingrediente:
                ingrediente = Ingrediente(nombre=nombre)
                db.session.add(ingrediente)
                db.session.flush()

         
            unidad = Unidad.query.filter_by(nombre=unidad_nombre).first()
            if not unidad:
                unidad = Unidad(nombre=unidad_nombre)
                db.session.add(unidad)
                db.session.flush()

            
            ing_receta = Ingrediente_Receta(
                id_receta=nuevo.id,
                id_ingrediente=ingrediente.id,
                cantidad=cantidad,
                id_unidad=unidad.id
            )
            db.session.add(ing_receta)

        db.session.commit()
        return jsonify(nuevo.to_dict()), 201

    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({'mensaje': 'Error al registrar receta'}), 400
    
@recetas_bp.route('/<int:id>', methods=['PUT'])
@token_requerido
def actualiza_receta(usuario_actual, id):
    try:
        print("Petición hecha por:", usuario_actual.email)
        receta = Receta.query.filter_by(activo=True).get_or_404(id)
        if receta.id_usuario != usuario_actual.id:
            return jsonify({'mensaje': 'No tienes permiso para actualizar esta receta.'}), 403

        data = request.get_json()
        patron = r'^[A-Za-z0-9\-]+$'

       
        if not re.match(patron, data['titulo']):
            return jsonify({'mensaje': 'El nombre de la receta solo puede contener letras, números y el guion - (sin espacios)'}), 400

        for ing in data.get('ingredientes', []):
            if not re.match(patron, ing.get('nombre', '')):
                return jsonify({'mensaje': f"El nombre del ingrediente '{ing.get('nombre')}' solo puede contener letras, números y el guion - (sin espacios)"}), 400

        receta.titulo = data['titulo']
        receta.descripcion = data['descripcion']

       
        Ingrediente_Receta.query.filter_by(id_receta=receta.id).delete()

        for ing in data.get('ingredientes', []):
            nombre = ing.get('nombre')
            cantidad = ing.get('cantidad')
            unidad_nombre = ing.get('unidad')

           
            ingrediente = Ingrediente.query.filter_by(nombre=nombre).first()
            if not ingrediente:
                ingrediente = Ingrediente(nombre=nombre)
                db.session.add(ingrediente)
                db.session.flush()

          
            unidad = Unidad.query.filter_by(nombre=unidad_nombre).first()
            if not unidad:
                unidad = Unidad(nombre=unidad_nombre)
                db.session.add(unidad)
                db.session.flush()

         
            ing_receta = Ingrediente_Receta(
                id_receta=receta.id,
                id_ingrediente=ingrediente.id,
                cantidad=cantidad,
                id_unidad=unidad.id
            )
            db.session.add(ing_receta)

       
        for img in receta.imagenes_receta:
            img.activo = False

       
        imagenes = data.get('imagenes', [])
        for img_dict in imagenes:
            descripcion = img_dict.get('descripcion', '')
            img_base64 = img_dict.get('imagen', '')
            if not img_base64:
                continue
            img_bin = base64.b64decode(fix_base64_padding(img_base64))
            nueva_imagen = Imagen_Receta(
                imagen=img_bin,
                descripcion=descripcion,
                id_receta=receta.id
            )
            db.session.add(nueva_imagen)

        db.session.commit()
        return jsonify(receta.to_dict())

    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({'mensaje': 'Error al actualizar receta'})

@recetas_bp.route('/<int:id>', methods=['DELETE'])
@token_requerido
def eliminar_receta(usuario_actual, id):
    try:
        print("Petición hecha por:", usuario_actual.email)
        receta = Receta.query.get_or_404(id)
        if receta.id_usuario != usuario_actual.id:
            return jsonify({'mensaje': 'No tienes permiso para eliminar esta receta.'}), 403

        receta.activo = False  

        for imagen in getattr(receta, 'imagenes', []):
            imagen.activo = False

        for comentario in getattr(receta, 'comentarios', []):
            comentario.activo = False

        
        for voto in getattr(receta, 'votos', []):
            voto.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Receta y sus elementos asociados dados de baja lógicamente."})

    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja la receta."})


@recetas_bp.route('/<string:nombre>/imagenes', methods=['GET'])
@token_requerido
def obtener_imagenes_por_receta(usuario_actual, nombre):
    try:
        receta = Receta.query.filter_by(titulo=nombre, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        imagenes = []
        
        for img in receta.imagenes_receta:
            if img.activo:
                imagenes.append({
                    "id": img.id,
                    "descripcion": img.descripcion,
                    "imagen": base64.b64encode(img.imagen).decode('utf-8')
                })

        return jsonify({
            "id": receta.id,
            "receta": receta.titulo,
            "descripcion": receta.descripcion,
            "imagenes": imagenes
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener imágenes de la receta"})
      
@recetas_bp.route('/<int:id>/imagenes', methods=['GET'])
@token_requerido
def obtener_imagenes_por_receta_id(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404
        imagenes = []
        
        for img in receta.imagenes_receta:
            if img.activo:
                imagenes.append({
                    "id": img.id,
                    "descripcion": img.descripcion,
                    "imagen": base64.b64encode(img.imagen).decode('utf-8')
                })

        return jsonify({
            "id": receta.id,
            "receta": receta.titulo,
            "descripcion": receta.descripcion,
            "imagenes": imagenes
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener imágenes de la receta"})


@recetas_bp.route('/<int:id>/imagenes', methods=['DELETE'])
@token_requerido
def eliminar_imagenes_receta(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

       
        if receta.id_usuario != usuario_actual.id:
            return jsonify({"mensaje": "No tienes permiso para eliminar las imágenes de esta receta."}), 403

        imagenes = receta.imagenes_receta  
        if not imagenes:
            return jsonify({"mensaje": "La receta no tiene imágenes para eliminar."}), 404

        for img in imagenes:
            img.activo = False  
            img.descripcion = False  

        db.session.commit()
        return jsonify({"mensaje": "Todas las imágenes de la receta han sido eliminadas correctamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar las imágenes de la receta"}), 400
@recetas_bp.route('/<int:id_receta>/imagen/<int:id_imagen>', methods=['DELETE'])
@token_requerido
def eliminar_imagen_receta(usuario_actual, id_receta, id_imagen):
    try:
        receta = Receta.query.filter_by(id=id_receta, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        
        if receta.id_usuario != usuario_actual.id:
            return jsonify({"mensaje": "No tienes permiso para eliminar imágenes de esta receta."}), 403

        imagen = next((img for img in receta.imagenes_receta if img.id == id_imagen), None)
        if not imagen:
            return jsonify({"mensaje": "Imagen no encontrada en la receta"}), 404

        imagen.activo = False  
        imagen.descripcion = False  

        db.session.commit()
        return jsonify({"mensaje": "Imagen eliminada correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar la imagen"}), 400
    

@recetas_bp.route('/usuario/<string:nombre>', methods=['GET'])
@token_requerido
def recetas_por_usuario(usuario_actual, nombre):
    try:
        usuario = Usuario.query.filter_by(nombre=nombre).first()
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        recetas = Receta.query.filter_by(id_usuario=usuario.id, activo=True).all()
        resultado = []
        for receta in recetas:
        
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })

            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })

        return jsonify({
            "usuario": usuario.nombre,
            "recetas": resultado
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas del usuario"})
    

@recetas_bp.route('/mis-recetas', methods=['GET'])
@token_requerido
def mis_recetas(usuario_actual):
    try:
        recetas = Receta.query.filter_by(activo=True, id_usuario=usuario_actual.id).all()
        resultado = []
        for receta in recetas:
            
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
      
            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })
        return jsonify({
            "usuario": usuario_actual.nombre,
            "recetas": resultado
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener tus recetas"})

@recetas_bp.route('/mis-recetas', methods=['DELETE'])
@token_requerido
def baja_logica_mis_recetas(usuario_actual):
    try:
        recetas = Receta.query.filter_by(id_usuario=usuario_actual.id, activo=True).all()
        if not recetas:
            return jsonify({"mensaje": "No tienes recetas activas para dar de baja."}), 404

        for receta in recetas:
            receta.activo = False
         
            for imagen in receta.imagenes_receta:
                imagen.activo = False
                imagen.descripcion = False  
            for comentario in getattr(receta, 'comentarios', []):
                comentario.activo = False
          
            for voto in getattr(receta, 'votos', []):
                voto.activo = False

        db.session.commit()
        return jsonify({"mensaje": "Todas tus recetas y sus elementos asociados han sido dadas de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja tus recetas"}), 400
    
@recetas_bp.route('/usuario-nickname/<string:nickname>', methods=['GET'])
@token_requerido
def recetas_por_nickname(usuario_actual, nickname):
    try:
        usuario = Usuario.query.filter_by(nickname=nickname).first()
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        if not getattr(usuario, "activo", True):
            return jsonify({"mensaje": "El usuario no está activo"}), 403

        recetas = Receta.query.filter_by(activo=True, id_usuario=usuario.id).all()
        resultado = []
        for receta in recetas:
            
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
       
            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })

        return jsonify({
            "usuario": usuario.nickname,
            "recetas": resultado
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas del usuario"})

@recetas_bp.route('/ingrediente/<string:nombre_ingrediente>', methods=['GET'])
@token_requerido
def recetas_por_ingrediente(usuario_actual, nombre_ingrediente):
    try:
        print("Petición hecha por:", usuario_actual.email)
        
        ingrediente = Ingrediente.query.filter_by(nombre=nombre_ingrediente).first()
        if not ingrediente:
            return jsonify({"mensaje": "Ingrediente no encontrado"}), 404

      
        relaciones = Ingrediente_Receta.query.filter_by(id_ingrediente=ingrediente.id).all()
        recetas_ids = set([rel.id_receta for rel in relaciones])

    
        recetas = Receta.query.filter(Receta.id.in_(recetas_ids), Receta.activo == True).all()
        resultado = []
        for receta in recetas:
            
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
            
            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "usuario": receta.usuario.nombre,
                "nickname": receta.usuario.nickname,
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })
        return jsonify(resultado)
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al buscar recetas por ingrediente"})

@recetas_bp.route('/<int:id>/comentario', methods=['POST'])
@token_requerido
def agregar_comentario(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        data = request.get_json()
        texto = data.get('comentario', '').strip()
        if not texto:
            return jsonify({"mensaje": "El comentario no puede estar vacío"}), 400

        nuevo_comentario = Comentario(
            comentario=texto,
            id_usuario=usuario_actual.id,
            id_receta=receta.id
        )
        db.session.add(nuevo_comentario)
        db.session.commit()

        comentario_dict = nuevo_comentario.to_dict()
        for key in list(comentario_dict.keys()):
            if str(type(comentario_dict[key])).endswith("AppenderQuery'>"):
                comentario_dict[key] = None  

        return jsonify({
            "mensaje": "Comentario agregado correctamente",
            "comentario": comentario_dict
        }), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al agregar comentario"}), 400
 
@recetas_bp.route('/<int:id>/voto', methods=['POST'])
@token_requerido
def votar_receta(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        data = request.get_json()
        puntuacion = data.get('voto')
        if puntuacion is None or not isinstance(puntuacion, int) or not (1 <= puntuacion <= 5):
            return jsonify({"mensaje": "La puntuación debe ser un número entero entre 1 y 5"}), 400

     
        voto = VotoReceta.query.filter_by(id_usuario=usuario_actual.id, id_receta=receta.id).first()
        if voto:
            return jsonify({"mensaje": "Ya has votado esta receta"}), 400  

        voto = VotoReceta(id_usuario=usuario_actual.id, id_receta=receta.id, puntuacion=puntuacion)
        db.session.add(voto)
        db.session.commit()
        return jsonify({
            "mensaje": "Voto registrado correctamente",
            "voto": voto.to_dict()
        }), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar el voto"}), 400

@recetas_bp.route('/<int:id>/voto', methods=['DELETE'])
@token_requerido
def eliminar_voto_receta(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        voto = VotoReceta.query.filter_by(id_usuario=usuario_actual.id, id_receta=receta.id).first()
        if not voto:
            return jsonify({"mensaje": "No has votado esta receta"}), 400

   
        voto.activo = False if hasattr(voto, "activo") else None
        db.session.commit()
        return jsonify({"mensaje": "Voto eliminado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar el voto"}), 400

@recetas_bp.route('/<int:id>', methods=['GET'])
@token_requerido
def obtener_receta_por_id(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

     
        ingredientes = []
        for ir in receta.ingredientes_receta:
            ingredientes.append({
                "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                "cantidad": float(ir.cantidad) if ir.cantidad else None,
                "unidad": ir.unidad.nombre if ir.unidad else None
            })

      
        imagenes = []
        for img in receta.imagenes_receta:
            if img.activo:
                imagenes.append({
                    "id": img.id,
                    "descripcion": img.descripcion,
                    "imagen": base64.b64encode(img.imagen).decode('utf-8')
                })

     
        comentarios = []
        for comentario in getattr(receta, 'comentarios', []):
            if getattr(comentario, "activo", True):
                comentarios.append(comentario.to_dict())

     
        valoraciones = []
        for voto in getattr(receta, 'votos', []):
            if getattr(voto, "activo", True):
                valoraciones.append(voto.to_dict())

        return jsonify({
            "id": receta.id,
            "titulo": receta.titulo,
            "descripcion": receta.descripcion,
            "usuario": receta.usuario.nombre,
            "nickname": receta.usuario.nickname,
            "ingredientes": ingredientes,
            "imagenes": imagenes,
            "comentarios": comentarios,
            "valoraciones": valoraciones
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener la receta"}), 400

@recetas_bp.route('/<int:id>/comentarios', methods=['GET'])
@token_requerido
def obtener_comentarios_por_receta(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        comentarios = [c for c in receta.comentarios if getattr(c, "activo", True)]

        comentarios_principales = [c for c in comentarios if getattr(c, "id_comentario_padre", None) is None]
        respuestas_dict = {}
        for c in comentarios:
            padre = getattr(c, "id_comentario_padre", None)
            if padre is not None:
                respuestas_dict.setdefault(padre, []).append(c)

        def anidar_respuestas(comentario):
            data = comentario.to_dict()
            
            if hasattr(comentario, "likes"):
                
                try:
                    data["likes"] = comentario.likes.filter_by(activo=True).count()
                except Exception:
                   
                    data["likes"] = sum(1 for like in comentario.likes if getattr(like, "activo", True))
            else:
                data["likes"] = 0
            hijos = respuestas_dict.get(comentario.id, [])
            if not isinstance(hijos, list):
                hijos = []
            data["respuestas"] = [anidar_respuestas(hijo) for hijo in hijos]
            return data

        comentarios_json = [anidar_respuestas(c) for c in comentarios_principales]

        return jsonify({
            "receta_id": receta.id,
            "receta_titulo": receta.titulo,
            "receta_descripcion": receta.descripcion,
            "comentarios": comentarios_json
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener los comentarios de la receta"}), 400




@recetas_bp.route('/<int:id>/valoraciones', methods=['GET'])
@token_requerido
def obtener_valoraciones_por_receta(usuario_actual, id):
    try:
        receta = Receta.query.filter_by(id=id, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        valoraciones = []
        for voto in receta.votos:
            valoraciones.append(voto.to_dict())

        return jsonify({
            "receta_id": receta.id,
            "receta_titulo": receta.titulo,
            "receta_descripcion": receta.descripcion,
            "valoraciones": valoraciones
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener las valoraciones de la receta"}), 400
    

@recetas_bp.route('/recientes', methods=['GET'])
@token_requerido
def recetas_recientes(usuario_actual):
    try:
        recetas = Receta.query.filter_by(activo=True).order_by(Receta.fecha_creacion.desc()).limit(10).all()
        resultado = []
        for receta in recetas:
         
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
          
            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "usuario": receta.usuario.nombre,
                "nickname": receta.usuario.nickname,
                "fecha_creacion": str(receta.fecha_creacion),
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })
        return jsonify(resultado)
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener recetas recientes"}), 400


@recetas_bp.route('/mejor-valoradas', methods=['GET'])
@token_requerido
def recetas_mejor_valoradas(usuario_actual):
    try:
        recetas = Receta.query.filter_by(activo=True).all()
        recetas_con_media = []

        for receta in recetas:
            valoraciones = [v.puntuacion for v in getattr(receta, 'votos', []) if hasattr(v, 'puntuacion')]
            if valoraciones:
                media = round(sum(valoraciones) / len(valoraciones), 2)
            else:
                media = 0
            recetas_con_media.append((receta, media))

       
        top_recetas = sorted(recetas_con_media, key=lambda x: x[1], reverse=True)[:10]

        resultado = []
        for receta, media_valoraciones in top_recetas:
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
            imagenes = []
            for img in receta.imagenes_receta:
                if img.activo:
                    imagenes.append({
                        "id": img.id,
                        "descripcion": img.descripcion,
                        "imagen": base64.b64encode(img.imagen).decode('utf-8')
                    })
            resultado.append({
                "usuario": receta.usuario.nombre,
                "nickname": receta.usuario.nickname,
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes,
                "media_valoraciones": media_valoraciones
            })
        return jsonify(resultado)
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener las recetas mejor valoradas"}), 400

@recetas_bp.route('/<int:id_receta>/comentario/<int:id_comentario_padre>', methods=['POST'])
@token_requerido
def responder_comentario(usuario_actual, id_receta, id_comentario_padre):
    try:
        receta = Receta.query.filter_by(id=id_receta, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

        comentario_padre = Comentario.query.filter_by(id=id_comentario_padre, id_receta=id_receta, activo=True).first()
        if not comentario_padre:
            return jsonify({"mensaje": "Comentario padre no encontrado o inactivo"}), 404

        data = request.get_json()
        texto = data.get('comentario', '').strip()
        if not texto:
            return jsonify({"mensaje": "El comentario no puede estar vacío"}), 400

        nuevo_comentario = Comentario(
            comentario=texto,
            id_usuario=usuario_actual.id,
            id_receta=receta.id,
            id_comentario_padre=id_comentario_padre
        )
        db.session.add(nuevo_comentario)
        db.session.commit()

        return jsonify({
            "mensaje": "Respuesta agregada correctamente",
            "comentario": nuevo_comentario.to_dict()
        }), 201
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al responder el comentario"}), 400
    
@recetas_bp.route('/<int:id_receta>/comentario/<int:id_comentario>', methods=['DELETE'])
@token_requerido
def baja_logica_comentario(usuario_actual, id_receta, id_comentario):
    try:
        comentario = Comentario.query.filter_by(id=id_comentario, id_receta=id_receta, activo=True).first()
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado o ya inactivo"}), 404

        
        if comentario.id_usuario != usuario_actual.id and not getattr(usuario_actual, 'es_admin', False):
            return jsonify({"mensaje": "No tienes permiso para eliminar este comentario"}), 403

        comentario.activo = False
        db.session.commit()
        return jsonify({"mensaje": "Comentario dado de baja lógicamente."})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al dar de baja el comentario"}), 400
    
@recetas_bp.route('/<int:id_receta>/comentario/<int:id_comentario>/like', methods=['POST'])
@token_requerido
def dar_like_comentario(usuario_actual, id_receta, id_comentario):
    try:
        
        receta = Receta.query.filter_by(id=id_receta, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

      
        comentario = Comentario.query.filter_by(id=id_comentario, id_receta=id_receta, activo=True).first()
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado o inactivo para esta receta"}), 404

        from models import LikeComentario
        like_existente = LikeComentario.query.filter_by(id_usuario=usuario_actual.id, id_comentario=id_comentario, activo=True).first()
        if like_existente:
            return jsonify({"mensaje": "Ya diste like a este comentario"}), 400

        nuevo_like = LikeComentario(id_usuario=usuario_actual.id, id_comentario=id_comentario, activo=True)
        db.session.add(nuevo_like)
        db.session.commit()

        return jsonify({"mensaje": "Like registrado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar el like"}), 400


@recetas_bp.route('/<int:id_receta>/comentario/<int:id_comentario>/like', methods=['DELETE'])
@token_requerido
def eliminar_like_comentario(usuario_actual, id_receta, id_comentario):
    try:
        
        receta = Receta.query.filter_by(id=id_receta, activo=True).first()
        if not receta:
            return jsonify({"mensaje": "Receta no encontrada o inactiva"}), 404

       
        comentario = Comentario.query.filter_by(id=id_comentario, id_receta=id_receta).first()
        if not comentario:
            return jsonify({"mensaje": "Comentario no encontrado para esta receta"}), 404

        from models import LikeComentario
        like = LikeComentario.query.filter_by(id_usuario=usuario_actual.id, id_comentario=id_comentario, activo=True).first()
        if not like:
            return jsonify({"mensaje": "No has dado like a este comentario"}), 400

        like.activo = False
        db.session.commit()
        return jsonify({"mensaje": "Like eliminado correctamente"})
    except Exception as ex:
        print(ex)
        db.session.rollback()
        return jsonify({"mensaje": "Error al eliminar el like"}), 400
    

@recetas_bp.route('/mis-recetas-votadas', methods=['GET'])
@token_requerido
def ver_mis_recetas_votadas(usuario_actual):
    try:
      
        votos = VotoReceta.query.filter_by(id_usuario=usuario_actual.id).all()
        recetas_ids = [voto.id_receta for voto in votos]
        recetas = Receta.query.filter(Receta.id.in_(recetas_ids), Receta.activo == True).all()
        resultado = []
        for receta in recetas:
            ingredientes = []
            for ir in receta.ingredientes_receta:
                ingredientes.append({
                    "nombre": ir.ingrediente.nombre if ir.ingrediente else None,
                    "cantidad": float(ir.cantidad) if ir.cantidad else None,
                    "unidad": ir.unidad.nombre if ir.unidad else None
                })
            imagenes = []
            if hasattr(receta, 'imagenes'):
                for img in receta.imagenes:
                    imagenes.append(base64.b64encode(img.datos).decode('utf-8'))
            resultado.append({
                "id": receta.id,
                "titulo": receta.titulo,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "imagenes": imagenes
            })
        return jsonify({
            "usuario": usuario_actual.nombre,
            "recetas_votadas": resultado
        })
    except Exception as ex:
        print(ex)
        return jsonify({"mensaje": "Error al obtener tus recetas votadas"}), 400
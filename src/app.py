from flask import Flask
from config import Config
from database import db
from routes.usuarios import usuarios_bp
from routes.recetas import recetas_bp
from routes.unidades import unidades_bp
from routes.ingredientes_receta import ingredientes_receta_bp
from routes.imagenes_receta import imagenes_receta_bp
from routes.comentarios import comentarios_bp
from routes.votos_receta import votos_receta_bp
from routes.auth import auth_bp

# Cambiar los codigos de los archivos y el codigo, revisar jwt, clase de usuario y token
# revisar routes.\src\app.py .\env\Scripts\activate

app = Flask(__name__)
app.config.from_object(Config)
#db.init_app(app)


try:
   
    db.init_app(app)
    # Registra los Blueprints (módulos de rutas)
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(recetas_bp, url_prefix='/recetas')
    app.register_blueprint(unidades_bp, url_prefix='/unidades')
    app.register_blueprint(ingredientes_receta_bp, url_prefix='/ingredientes-receta')
    app.register_blueprint(imagenes_receta_bp, url_prefix='/imagenes-receta')
    app.register_blueprint(comentarios_bp, url_prefix='comentarios')
    app.register_blueprint(votos_receta_bp, url_prefix='votos-receta')
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Si tienes rutas de autenticación


    # ✅ Crea las tablas en la base de datos si no existen
    @app.before_request
    def create_tables():
    # The following line will remove this handler, making it
    # only run on the first request
        app.before_request_funcs[None].remove(create_tables)
        db.create_all()

except Exception as e:
    # Mensaje amigable si la base de datos no existe o no hay conexión
    print("❌ Error al conectar con la base de datos:")
    print("💡 Asegúrate de que la base de datos 'api_flask' existe.")
    print("🔧 Puedes crearla con este comando en Workbench:")
    print("    CREATE DATABASE api_flask;")
    print(e)
    exit()

# Ejecuta el servidor local en modo debug
if __name__ == '__main__':
    app.run(debug=True)

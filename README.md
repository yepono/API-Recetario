# 🍳 API RESTful - Plataforma de Recetas (Flask)

> Una API robusta desarrollada con Flask para gestionar una plataforma interactiva de recetas de cocina. Permite la administración de usuarios, creación de recetas, manejo de ingredientes, subida de imágenes, comentarios, valoraciones y cuenta con autenticación segura.

---

## 🚀 Características Principales

* **Autenticación Segura:** Sistema de registro e inicio de sesión utilizando tokens JWT (JSON Web Tokens).
* **Gestión de Recetas:** Operaciones CRUD completas para recetas, incluyendo la vinculación con ingredientes específicos y unidades de medida.
* **Manejo de Imágenes:** Las imágenes de las recetas y los perfiles de usuario se codifican y almacenan de forma segura en formato `Base64` directamente en la base de datos (LargeBinary).
* **Interacción Social:** Los usuarios pueden dejar comentarios en las recetas, responder a otros comentarios y calificar las recetas (1 a 5 estrellas).
* **Panel de Administración:** Rutas protegidas exclusivas para administradores (`/admin`) que permiten la recuperación o eliminación permanente (baja lógica) de usuarios, recetas, imágenes y comentarios que infrinjan las normas.
* **Bajas Lógicas:** Los registros eliminados no se borran de la base de datos; simplemente cambian su estado a `activo = False` para mantener la integridad histórica de los datos.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **Framework:** Flask
* **Base de Datos:** MySQL
* **ORM:** Flask-SQLAlchemy
* **Seguridad:** PyJWT (Tokens), Werkzeug (Hashing de contraseñas)

---

## 📁 Estructura del Proyecto

[cite_start]El proyecto sigue una arquitectura modular utilizando `Blueprints` de Flask para separar las rutas lógicas del sistema[cite: 1, 2]:

```text
.
├── app.py                     # Punto de entrada principal y configuración del servidor
├── config.py                  # Variables de entorno y configuración de conexión a BD
├── database.py                # Instancia global de SQLAlchemy
├── models.py                  # Definición de las tablas (Modelos) de la base de datos
└── routes/                    # Controladores de las rutas de la API
    ├── admin.py
    ├── auth.py
    ├── comentarios.py
    ├── imagenes_receta.py
    ├── ingredientes_receta.py
    ├── recetas.py
    ├── unidades.py
    ├── usuarios.py
    └── votos_receta.py

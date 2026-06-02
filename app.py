import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Importamos nuestros propios módulos
from api.supabase_client import db
from api.routes import api_bp
from soap.billing_service import wsgi_soap_app

# Cargar variables del .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la app de Flask
db.init_app(app)

# Registrar las rutas REST (Le pone /api adelante a todo lo que está en routes.py)
app.register_blueprint(api_bp, url_prefix='/api')

# Integrar el servicio SOAP en la ruta /soap
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/soap': wsgi_soap_app
})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
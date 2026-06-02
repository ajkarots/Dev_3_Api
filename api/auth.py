import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify

# Inicializar Firebase
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({'error': 'Token de autenticación faltante'}), 401

        try:
            usuario_decodificado = auth.verify_id_token(token)
            request.user = usuario_decodificado 
        except Exception as e:
            return jsonify({'error': 'Token inválido o expirado', 'detalle': str(e)}), 401

        return f(*args, **kwargs)
    return decorated
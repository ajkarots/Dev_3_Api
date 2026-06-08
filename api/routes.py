from flask import Blueprint, request, jsonify
from api.supabase_client import db, Usuario, Producto, Compra, DetalleCompra
from api.auth import token_required

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def index():
    return jsonify({"mensaje": "API TechStore 360 funcionando correctamente"})

# --- RUTAS DE PRODUCTOS ---
@api_bp.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    return jsonify([{"id": p.id, "nombre": p.nombre, "precio": float(p.precio), "stock": p.stock} for p in productos]), 200

@api_bp.route('/productos', methods=['POST'])
@token_required
def crear_producto():
    datos = request.get_json()
    nuevo_producto = Producto(nombre=datos['nombre'], precio=datos['precio'], stock=datos.get('stock', 0), imagen=datos.get('imagen'))
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"mensaje": "Producto creado", "id": nuevo_producto.id}), 201

# --- RUTAS DE USUARIOS ---

@api_bp.route('/usuarios', methods=['GET'])
@token_required # Protegemos la ruta para que solo usuarios logueados (o admins) la vean
def obtener_todos_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.id,
            "firebase_uid": u.firebase_uid,
            "nombre": u.nombre,
            "correo": u.correo,
            "rol": u.rol,
            "fecha_registro": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else None
        })
    return jsonify(resultado), 200

@api_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@token_required
def eliminar_usuario():
    
    usuario = Usuario.query.get(id);
    
    if not usuario:
        return jsonify({"Error" : "Usuario no encontrado"}), 404
    
    db.session.delete(usuario)
    db.session.commit()
    
    return jsonify({
                    
                    "Mensaje" : "Usuario eliminado correctamente"
                    }), 200
    
@api_bp.route('/usuarios/<int:id>', methods= ['PUT'])    
@token_required
def editar_usuario(id):
    
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({"Error": "Usuario no encontrado"}), 404
    
    datos = request.get_json();
    
    if 'nombre' in datos:
        usuario.nombre = datos['nombre']
    
    if 'correo' in datos:
        usuario.correo = datos['correo']
        
    if 'rol' in datos:
        usuario.rol = datos['rol']

    db.session.commit()
    return jsonify({"mensaje": "Usuario actualizado", "id": usuario.id}), 200

@api_bp.route('/usuarios', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    usuario_existente = Usuario.query.filter_by(correo=datos['correo']).first()
    if usuario_existente:
        return jsonify({"mensaje": "El usuario ya existe", "id": usuario_existente.id}), 200

    nuevo_usuario = Usuario(firebase_uid=datos['firebase_uid'], correo=datos['correo'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado", "id": nuevo_usuario.id}), 201

# --- RUTAS DE COMPRAS ---
@api_bp.route('/compras', methods=['GET'])
@token_required
def obtener_todas_compras():
    compras = Compra.query.all()
    resultado = []
    for c in compras:
        # Buscamos los detalles de esta compra en particular
        detalles_db = DetalleCompra.query.filter_by(compra_id=c.id).all()
        detalles_formateados = []
        for d in detalles_db:
            detalles_formateados.append({
                "producto_id": d.producto_id,
                "cantidad": d.cantidad,
                "subtotal": float(d.subtotal)
            })

        resultado.append({
            "id": c.id,
            "usuario_id": c.usuario_id,
            "total": float(c.total),
            "estado": c.estado,
            "fecha": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
            "detalles": detalles_formateados
        })
    return jsonify(resultado), 200

@api_bp.route('/compras', methods=['POST'])
@token_required
def registrar_compra():
    datos = request.get_json()
    usuario_id = datos.get('usuario_id')
    detalles = datos.get('detalles') 

    if not usuario_id or not detalles:
        return jsonify({"error": "Faltan datos de la compra"}), 400

    try:
        nueva_compra = Compra(usuario_id=usuario_id, total=0, estado='COMPLETADA')
        db.session.add(nueva_compra)
        db.session.flush()

        total_compra = 0
        for item in detalles:
            producto = Producto.query.get(item['producto_id'])
            if not producto or producto.stock < item['cantidad']:
                raise Exception(f"Error con el producto ID {item['producto_id']}")
            
            subtotal = float(producto.precio) * item['cantidad']
            total_compra += subtotal
            producto.stock -= item['cantidad']

            db.session.add(DetalleCompra(compra_id=nueva_compra.id, producto_id=producto.id, cantidad=item['cantidad'], subtotal=subtotal))

        nueva_compra.total = total_compra
        db.session.commit()
        return jsonify({"mensaje": "Compra realizada", "compra_id": nueva_compra.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.BigInteger, primary_key=True)
    firebase_uid = db.Column(db.String, unique=True, nullable=False)
    nombre = db.Column(db.String)
    correo = db.Column(db.String, unique=True, nullable=False)
    rol = db.Column(db.String, default='cliente')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10,2))
    stock = db.Column(db.Integer)
    imagen = db.Column(db.Text)
    eliminado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey('usuarios.id'))
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.String, default='PENDIENTE')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class DetalleCompra(db.Model):
    __tablename__ = 'detalle_compras'
    id = db.Column(db.BigInteger, primary_key=True)
    compra_id = db.Column(db.BigInteger, db.ForeignKey('compras.id'))
    producto_id = db.Column(db.BigInteger, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer)
    subtotal = db.Column(db.Numeric(10, 2))
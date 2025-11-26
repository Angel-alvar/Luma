from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()


class TipoUsuario(db.Model):
    __tablename__ = 'tipos_usuario'
    id_tipo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    
    usuarios = db.relationship('Usuario', back_populates='tipo_usuario')


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(256), nullable=False)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipos_usuario.id_tipo'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    tipo_usuario = db.relationship('TipoUsuario', back_populates='usuarios')
    empleado = db.relationship('Empleado', back_populates='usuario', uselist=False)
    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False)

    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

    @property
    def is_admin(self):
        return self.tipo_usuario and self.tipo_usuario.nombre == 'admin'

    @property
    def is_empleado(self):
        return self.tipo_usuario and self.tipo_usuario.nombre == 'empleado'

    @property
    def is_cliente(self):
        return self.tipo_usuario and self.tipo_usuario.nombre == 'cliente'

class Empleado(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    puesto = db.Column(db.String(50), nullable=True)

    usuario = db.relationship('Usuario', back_populates='empleado')
    seguimientos = db.relationship('SeguimientoPedido', back_populates='empleado')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    usuario = db.relationship('Usuario', back_populates='cliente')
    pedidos = db.relationship('Pedido', back_populates='cliente')

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    detalles = db.relationship('DetallePedido', back_populates='producto')

class Insumo(db.Model):
    __tablename__ = 'insumos'
    id_insumo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(30), nullable=False)

    cliente = db.relationship('Cliente', back_populates='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido')
    seguimientos = db.relationship('SeguimientoPedido', back_populates='pedido')

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    pedido = db.relationship('Pedido', back_populates='detalles')
    producto = db.relationship('Producto', back_populates='detalles')

class SeguimientoPedido(db.Model):
    __tablename__ = 'seguimiento_pedido'
    id_seguimiento = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(30), nullable=False)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleados.id_empleado'))
    comentario = db.Column(db.Text, nullable=True)

    pedido = db.relationship('Pedido', back_populates='seguimientos')
    empleado = db.relationship('Empleado', back_populates='seguimientos')